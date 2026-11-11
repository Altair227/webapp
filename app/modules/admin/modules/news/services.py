from datetime import datetime
from typing import Any

from sqlalchemy import or_

from app.database import db_session
from app.models import News
from app.models.base import get_sortable_columns, to_dict
from app.utils.source_images import get_or_create_images


SORTABLE = get_sortable_columns(News)


class NewsService:
    @staticmethod
    def get_list(
        page: int = 1,
        size: int = 25,
        search: str | None = None,
        field: str | None = "id",
        direction: str | None = "desc",
    ) -> tuple[int, list[Any]]:
        if size < 1:
            size = 1
        if field not in SORTABLE:
            field = "id"
        if direction != "asc":
            direction = "desc"
        if page < 1:
            page = 1
        query = db_session.query(News)
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(News.title.ilike(like), News.description.ilike(like))
            )
        total = query.count()
        column = SORTABLE[field]
        query = query.order_by(
            column.desc() if direction == "desc" else column.asc()
        )
        rows = query.offset((page - 1) * size).limit(size).all()
        return (total + size - 1) // size, [to_dict(news) for news in rows]

    @staticmethod
    def create(
        title: str,
        description: str,
        content: str,
        published_at: datetime | None = None,
        image_url: str | None = None,
        images: list[str] | None = None,
    ) -> str | None:
        data = News(
            title=title,
            description=description,
            content=content,
            published_at=published_at,
            image_url=image_url,
        )
        db_session.add(data)
        try:
            data.images = get_or_create_images(images or [])
            db_session.commit()
            return None
        except Exception as e:
            db_session.rollback()
            return str(e)

    @staticmethod
    def get_by_id(_id: int) -> News | None:
        return db_session.get(News, _id)

    @staticmethod
    def update(
        _id: int,
        title: str,
        description: str,
        content: str,
        published_at: datetime | None = None,
        image_url: str | None = None,
        images: list[str] | None = None,
    ) -> str | None:
        data = NewsService.get_by_id(_id)
        if not data:
            return "News not found"
        data.title = title
        data.description = description
        data.content = content
        data.published_at = published_at
        data.image_url = image_url
        try:
            # replaces links in _r_news_source_image; SourceImage rows stay
            data.images = get_or_create_images(images or [])
            db_session.commit()
            return None
        except Exception as e:
            db_session.rollback()
            return str(e)

    @staticmethod
    def remove(_id: list[int]) -> None | str:
        db_session.query(News).filter(News.id.in_(_id)).update(
            {"is_deleted": True}, synchronize_session=False
        )
        try:
            db_session.commit()
            return None
        except Exception as e:
            return str(e)

    @staticmethod
    def resume(_id: list[int]) -> None | str:
        db_session.query(News).filter(News.id.in_(_id)).update(
            {"is_deleted": False}, synchronize_session=False
        )
        try:
            db_session.commit()
            return None
        except Exception as e:
            return str(e)
