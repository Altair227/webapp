FROM python:3.14-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /usr/local/bin/uv

# venv lives outside the mounted project dir so it doesn't clash with host .venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /srv

FROM runtime AS deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# before the Python dependencies: changes in pyproject.toml or uv.lock must
# not download ffmpeg again
FROM runtime AS ffmpeg
# closer Debian mirror, e.g. http://ftp.de.debian.org/debian
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
RUN sed -i "s|http://deb.debian.org/debian$|${DEBIAN_MIRROR}|" \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# background video scan: ffmpeg makes posters of uploaded videos
FROM ffmpeg AS video-scan
COPY --from=deps /opt/venv /opt/venv
CMD ["python", "cli.py", "scan-videos", "--loop"]

# last stage: built when no target is given
FROM deps AS app
CMD ["python", "run.py"]
