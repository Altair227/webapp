import json
import os
import shutil
import signal
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Event
from typing import Any
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

from sqlalchemy import or_

from app.common.types import VideoType
from app.config import UPLOAD_DIR
from app.database import db_session
from app.models import SourceVideo
from app.utils.logger import get_logger
from app.utils.uploads import UPLOAD_PREFIX, local_file
from app.utils.video_types import (
    detect_type,
    extract_vimeo_id,
    extract_youtube_id,
)


BATCH_SIZE = 20
TIMEOUT = 5  # seconds
LOOP_PAUSE = 10  # seconds
MAX_RESPONSE = 1024 * 1024
MAX_POSTER = 500  # length of source_video.poster
# pause after the 1st, 2nd... failure; after the last one we give up
RETRY_MINUTES = (1, 5, 30, 120)
MAX_ATTEMPTS = len(RETRY_MINUTES) + 1
# types whose poster this scan can find; local files need ffmpeg, which only
# the video-scan image has: elsewhere they are left for that service
FETCHABLE = [VideoType.YOUTUBE, VideoType.VIMEO]
if shutil.which("ffmpeg") and shutil.which("ffprobe"):
    FETCHABLE.append(VideoType.LOCAL)

POSTER_DIR = "posters"  # in UPLOAD_DIR
PROBE_TIMEOUT = 15  # seconds
FRAME_TIMEOUT = 60  # seconds
# uploaded files are not trusted: no network, no playlists that could make
# ffmpeg read other files
INPUT_OPTIONS = (
    "-protocol_whitelist",
    "file",
    "-format_whitelist",
    "mov,mp4,matroska,webm,avi,ogg",
)

logger = get_logger("video_scan")


class ScanError(Exception):
    """The poster could not be found."""


@dataclass(frozen=True)
class VideoMeta:
    poster: str
    duration: int | None = None


def _youtube(url: str) -> VideoMeta:
    video_id = extract_youtube_id(url)
    if not video_id:
        raise ScanError("no YouTube id in the URL")
    return VideoMeta(f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg")


def _vimeo(url: str) -> VideoMeta:
    found = extract_vimeo_id(url)
    if not found:
        raise ScanError("no Vimeo id in the URL")
    # rebuilt from the id: the URL typed in the form is never requested
    target = "https://vimeo.com/" + "/".join(part for part in found if part)
    query = urlencode({"url": target, "width": 640})
    with urlopen(
        f"https://vimeo.com/api/oembed.json?{query}", timeout=TIMEOUT
    ) as response:
        data = json.loads(response.read(MAX_RESPONSE))
    if not isinstance(data, dict):
        raise ScanError("unexpected oEmbed response")
    poster = data.get("thumbnail_url")
    if not isinstance(poster, str) or len(poster) > MAX_POSTER:
        raise ScanError("no usable thumbnail_url in the oEmbed response")
    parts = urlsplit(poster)
    if parts.scheme != "https" or parts.hostname != "i.vimeocdn.com":
        raise ScanError("unexpected thumbnail host")
    duration = data.get("duration")
    if not isinstance(duration, int) or duration <= 0:
        duration = None
    return VideoMeta(poster, duration)


def _run(command: list[str], timeout: int) -> str:
    try:
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        raise ScanError(f"{command[0]}: timeout {timeout} s") from e
    if result.returncode != 0:
        error = result.stderr.strip()[-300:]
        raise ScanError(f"{command[0]}: {error or result.returncode}")
    return result.stdout


def _probe(file: Path) -> float | None:
    """Duration in seconds, None when the container does not tell it."""
    output = _run(
        [
            "ffprobe",
            "-v",
            "error",
            *INPUT_OPTIONS,
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            f"file:{file}",
        ],
        PROBE_TIMEOUT,
    )
    try:
        duration = float(json.loads(output)["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        return None
    return duration if 0 < duration < float("inf") else None


def _save_frame(file: Path, second: float, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    # renamed when ready, so a half-written picture is never served
    temp = target.with_name(f".{target.name}.tmp")
    try:
        _run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-ss",
                f"{second:.3f}",
                *INPUT_OPTIONS,
                "-i",
                f"file:{file}",
                "-map",
                "0:v:0",
                "-frames:v",
                "1",
                "-vf",
                "scale='min(640,iw)':-2",
                "-c:v",
                "mjpeg",
                "-pix_fmt",
                "yuvj420p",
                "-q:v",
                "3",
                "-f",
                "image2",
                "-update",
                "1",
                f"file:{temp}",
            ],
            FRAME_TIMEOUT,
        )
        if not temp.is_file() or not temp.stat().st_size:
            raise ScanError("ffmpeg: no frame")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


def _local(video_id: int, url: str) -> VideoMeta:
    file = local_file(url)
    if not file:
        raise ScanError("file not found in UPLOAD_DIR")
    duration = _probe(file)
    name = f"{video_id}.jpg"
    # the very first frame is often black
    second = min(duration * 0.1, 5) if duration else 0
    _save_frame(file, second, UPLOAD_DIR / POSTER_DIR / name)
    return VideoMeta(
        f"{UPLOAD_PREFIX}{POSTER_DIR}/{name}",
        max(1, round(duration)) if duration else None,
    )


def _fetch(video_id: int, video_type: VideoType, url: str) -> VideoMeta:
    if video_type == VideoType.LOCAL:
        return _local(video_id, url)
    if video_type == VideoType.YOUTUBE:
        return _youtube(url)
    return _vimeo(url)


def _save(video_id: int, values: dict[Any, Any]) -> None:
    # poster IS NULL: never overwrite a poster saved meanwhile
    db_session.query(SourceVideo).filter(
        SourceVideo.id == video_id, SourceVideo.poster.is_(None)
    ).update(values, synchronize_session=False)
    db_session.commit()


def _process(
    video_id: int, url: str, video_type: VideoType | None, attempts: int
) -> bool:
    """Update one video, False when its poster could not be found."""
    if video_type is None:
        video_type = detect_type(url)
        _save(video_id, {"type": video_type})
    if video_type not in FETCHABLE or attempts >= MAX_ATTEMPTS:
        return True
    try:
        meta = _fetch(video_id, video_type, url)
    except Exception as e:
        attempts += 1
        next_at = None
        if attempts < MAX_ATTEMPTS:
            pause = timedelta(minutes=RETRY_MINUTES[attempts - 1])
            next_at = datetime.now(UTC) + pause
        _save(video_id, {"attempts": attempts, "next_attempt_at": next_at})
        logger.warning(
            "Video %s (%s): attempt %s/%s failed: %s",
            video_id,
            video_type.name,
            attempts,
            MAX_ATTEMPTS,
            e,
        )
        return False
    values: dict[Any, Any] = {
        "poster": meta.poster,
        "attempts": 0,
        "next_attempt_at": None,
    }
    if meta.duration is not None:
        values["duration"] = meta.duration
    _save(video_id, values)
    logger.info("Video %s (%s): poster saved", video_id, video_type.name)
    return True


def _next_batch(
    after_id: int,
) -> list[tuple[int, str, VideoType | None, int]]:
    rows = (
        db_session.query(
            SourceVideo.id,
            SourceVideo.url,
            SourceVideo.type,
            SourceVideo.attempts,
        )
        .filter(
            SourceVideo.id > after_id,
            SourceVideo.is_deleted.is_(False),
            SourceVideo.poster.is_(None),
            or_(
                SourceVideo.type.is_(None),
                SourceVideo.type.in_(FETCHABLE)
                & (SourceVideo.attempts < MAX_ATTEMPTS)
                & or_(
                    SourceVideo.next_attempt_at.is_(None),
                    SourceVideo.next_attempt_at <= datetime.now(UTC),
                ),
            ),
        )
        .order_by(SourceVideo.id)
        .limit(BATCH_SIZE)
        .all()
    )
    # no open transaction while the network is busy
    db_session.remove()
    return [(row[0], row[1], row[2], row[3]) for row in rows]


def scan_videos(stop: Event | None = None) -> tuple[int, int]:
    """One pass over the videos without type or poster: (done, failed).

    When stop is set, the pass ends after the current video.
    """
    done = failed = last_id = 0
    try:
        while batch := _next_batch(last_id):
            for video_id, url, video_type, attempts in batch:
                if stop and stop.is_set():
                    return done, failed
                if _process(video_id, url, video_type, attempts):
                    done += 1
                else:
                    failed += 1
                last_id = video_id
    finally:
        db_session.remove()
    return done, failed


def scan_videos_loop() -> None:
    """Scan until SIGTERM or SIGINT."""
    stop = Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: stop.set())
    logger.info("Scan started, every %s s", LOOP_PAUSE)
    while not stop.is_set():
        try:
            scan_videos(stop)
        except Exception:
            # e.g. Postgres restarts or a migration is not applied yet
            logger.exception("Scan failed")
        stop.wait(LOOP_PAUSE)
    logger.info("Scan stopped")
