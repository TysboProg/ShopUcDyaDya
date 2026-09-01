from sqlalchemy.orm import DeclarativeBase

from shopucdyadya.db.mixins.created_at import CreatedAtMixin
from shopucdyadya.db.mixins.uuid_id import UUIDIDMixin


class Base(DeclarativeBase):
    __abstract__ = True


class BaseMixin(Base, CreatedAtMixin, UUIDIDMixin):
    __abstract__ = True
