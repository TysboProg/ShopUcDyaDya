from infra.db.models.mixins.created_at import CreatedAtMixin
from infra.db.models.mixins.uuid_id import UUIDIDMixin
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True


class BaseMixin(Base, CreatedAtMixin, UUIDIDMixin):
    __abstract__ = True
