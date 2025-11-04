from dataclasses import dataclass


@dataclass(eq=False)
class PromoCodeNotFoundException(Exception):
    code: str

    @property
    def message(self) -> str:
        return f"Промокод {self.code} не найден"


@dataclass(eq=False)
class PromoCodeAlreadyExistsException(Exception):
    code: str

    @property
    def message(self) -> str:
        return f"Промокод {self.code} уже существует"


@dataclass(eq=False)
class PromoCodeExpiredException(Exception):
    code: str

    @property
    def message(self) -> str:
        return f"Промокод {self.code} просрочен"


@dataclass(eq=False)
class PromoCodeAlreadyUsedException(Exception):
    code: str

    @property
    def message(self) -> str:
        return f"Промокод {self.code} уже использован"