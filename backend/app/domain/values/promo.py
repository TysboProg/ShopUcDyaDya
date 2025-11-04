from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from domain.enums import UcAmount


@dataclass(frozen=True)
class PromoValue:
    code: str
    uc_amount: UcAmount | None

    def __post_init__(self):
        if not self.code.strip():
            raise ValueError("Промокод не может быть пустым")
        if not self.uc_amount:
            raise ValueError("Номинал UC не может быть пустым")


@dataclass(frozen=True)
class PromoCodeExpiration:
    expires_at: datetime

    @classmethod
    def create(cls, duration_days: int) -> 'PromoCodeExpiration':
        if duration_days <= 0:
            raise ValueError("Продолжительность дней должна быть положительной")

        return cls(
            expires_at=datetime.now(timezone.utc) + timedelta(days=duration_days)
        )

    @property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now(timezone.utc)


@dataclass(frozen=True)
class PromoCodeUsage:
    used_at: Optional[datetime] = None
    used_by: Optional[UUID] = None

    @staticmethod
    def mark_used(user_id: UUID) -> 'PromoCodeUsage':
        return PromoCodeUsage(
            used_at=datetime.now(timezone.utc),
            used_by=user_id
        )