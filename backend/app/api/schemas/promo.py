from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from uuid import UUID

from domain.enums import UcAmount, PromoStatus


class PromoShortResponse(BaseModel):
    id: UUID
    code: str
    uc_amount: UcAmount
    expires_at: datetime
    status: PromoStatus

    class Config:
        from_attributes = True
        json_encoders = {
            UcAmount: lambda v: v.value,
            PromoStatus: lambda v: v.value,
        }

class PromoResponse(BaseModel):
    id: UUID
    code: str
    uc_amount: UcAmount
    expires_at: datetime
    status: PromoStatus
    used_by: Optional[UUID] = None
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            UcAmount: lambda v: v.value,
            PromoStatus: lambda v: v.value,
        }

class PromoListResponse(BaseModel):
    items: List[PromoShortResponse]

class UsePromoResponse(BaseModel):
    message: str
    uc_amount: str

class MessageResponse(BaseModel):
    message: str
