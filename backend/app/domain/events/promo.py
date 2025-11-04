from dataclasses import dataclass

from .base import BaseEvent


@dataclass
class CreatedPromoCodeEvent(BaseEvent):
    code: str
    message: str = "Промокод успешно создан"


@dataclass
class DeletedPromoCodeEvent(BaseEvent):
    code: str
    message: str = "Промокод успешно удален"


@dataclass
class UsedPromoCodeEvent(BaseEvent):
    code: str
    user_id: str
    message: str = "Промокод успешно использован"
