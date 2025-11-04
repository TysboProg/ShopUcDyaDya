from enum import Enum


class UcAmount(str, Enum):
    """Номиналы UC"""

    UC60 = "60UC"
    UC300 = "325UC"
    UC600 = "660UC"
    UC985 = "985UC"
    UC1800 = "1800UC"
    UC2460 = "2460UC"
    UC3850 = "3850UC"
    ALL = "ALL"


class PromoField(str, Enum):
    """Поля промокода для фильтрации"""

    CREATED_AT = "created_at"
    EXPIRES_AT = "expires_at"
    UC_AMOUNT = "uc_amount"
    STATUS = "status"


class PromoStatus(str, Enum):
    """Статусы промокода"""

    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
