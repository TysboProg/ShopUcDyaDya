from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from infra.db.models.mixins import CreatedAtMixin, UUIDIDMixin


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

class BaseTable(Base, CreatedAtMixin, UUIDIDMixin):
    __abstract__ = True