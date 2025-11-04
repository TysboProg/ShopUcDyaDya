from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Enum,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import PromoStatus, UcAmount
from infra.db.models.base import BaseTable

class Promocode(BaseTable):
    __tablename__ = "promo_codes"

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    uc_amount: Mapped[UcAmount] = mapped_column(
        Enum(UcAmount),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[PromoStatus] = mapped_column(
        Enum(PromoStatus),
        default=PromoStatus.ACTIVE,
        nullable=False
    )

    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    used_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
