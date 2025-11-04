import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        server_default=str(uuid.uuid4()),
    )
