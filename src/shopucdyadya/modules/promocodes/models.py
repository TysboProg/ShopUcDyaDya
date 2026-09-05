from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import Field

from shopucdyadya.infra.base_model import Base

from .schemas import PromoStatus, UcAmount

uc_amount_enum = ENUM(UcAmount, name="ucamount", create_type=False)
promo_status_enum = ENUM(PromoStatus, name="promostatus", create_type=False)


class Promocode(Base, table=True):
    __tablename__ = "promocodes"

    code: str = Field(sa_column=Column(String(50), unique=True, nullable=False))

    uc_amount: UcAmount = Field(sa_column=Column(uc_amount_enum, nullable=False))

    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

    status: PromoStatus = Field(
        default=PromoStatus.ACTIVE,
        sa_column=Column(promo_status_enum, nullable=False),
    )

    used_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    used_by: str | None = Field(default=None, sa_column=Column(String(100), nullable=True))
