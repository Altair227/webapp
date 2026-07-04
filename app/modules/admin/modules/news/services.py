from app.models import News
from app.database import db_session
from sqlalchemy import or_, desc
from app.models.base import get_sortable_columns, to_dict
from datetime import datetime


SORTABLE = get_sortable_columns(News)


class NewsService:
    @staticmethod
    def list(
        page: int = 1,
        size: int = 25,
        search: str = None,
        field: str = "id",
        direction: str = "desc",
    ) -> tuple[int, list[News]]:
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
        column = SORTABLE.get(field)
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
    ) -> str | None:
        data = News(
            title=title,
            description=description,
            content=content,
            published_at=published_at,
        )
        db_session.add(data)
        try:
            db_session.commit()
            return None
        except Exception as e:
            return str(e)
