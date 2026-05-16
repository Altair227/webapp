from enum import IntEnum
from typing import Any
from sqlalchemy import CheckConstraint, SmallInteger
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class UserType(IntEnum):
    USER = 0
    ADMIN = 1


class AdminType(IntEnum):
    SUPER_ADMIN = 0
    ADMIN = 1
    MODERATOR = 2


class EntityType(IntEnum):
    USER = 1
    ADMIN = 2


class EmailTokenType(IntEnum):
    PASSWORD_RESET = 1


class SmallIntEnum(TypeDecorator[IntEnum]):
    """
    SQLAlchemy TypeDecorator для IntEnum -> SMALLINT маппинга.

    Хранит в БД как SMALLINT, работает в Python как IntEnum.
    """

    impl = SmallInteger
    cache_ok = True

    def __init__(
        self, enum_class: type[IntEnum], *args: Any, **kwargs: Any
    ) -> None:
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(
        self, value: IntEnum | None, _dialect: Dialect
    ) -> int | None:
        """Python Enum -> DB Integer"""
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        # Если передали int напрямую
        return int(value)

    def process_result_value(
        self, value: int | None, _dialect: Dialect
    ) -> IntEnum | None:
        """DB Integer -> Python Enum"""
        if value is None:
            return None
        return self.enum_class(value)

    @staticmethod
    def create_check_constraint(
        column_name: str, enum_class: type[IntEnum]
    ) -> CheckConstraint:
        """Создаёт CHECK constraint для валидации значений"""
        valid_values = [e.value for e in enum_class]
        values_str = ", ".join(map(str, valid_values))
        return CheckConstraint(
            f"{column_name} IN ({values_str})",
            name=f"ck_{column_name}_valid_values",
        )
