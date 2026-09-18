from app.models import News
from app.database import db_session
from sqlalchemy import or_, func
from app.models.base import to_dict




class NewsService:
    @staticmethod
    def list(
        page: int = 1,
        size: int = 25,
        search: str = None,
    ) -> tuple[int, list[News]]:
        if size < 1:
            size = 1
        if page < 1:
            page = 1
        query = db_session.query(News).filter(
            News.is_deleted.is_(False),
            or_(
                News.published_at.is_(None),
                News.published_at <= func.now(),
            )
        )
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(News.title.ilike(like), News.description.ilike(like))
            )
            query=query.order_by(
                func.greatest(
                    func.coalesce(News.published_at, News.created_at),
                    News.created_at
                ).desc()
            )
        rows = query.offset((page - 1) * size).limit(size).all()
        return [to_dict(news) for news in rows]


    @staticmethod
    def get_by_id(_id: int) -> News | None:
        query = db_session.query(News).filter(
            News.id == _id,
            News.is_deleted.is_(False),
            or_(
                News.published_at.is_(None),
                News.published_at <= func.now(),
            )
        )
        return query.first()


