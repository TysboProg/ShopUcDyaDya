from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


@lru_cache
def _load_description() -> str:
    DESCRIPTION_PATH = Path(__file__).parent / "openapi_description.md"
    return DESCRIPTION_PATH.read_text(encoding="utf-8")


class OpenAPIConfig(BaseModel):
    title: str = "Магазин дядюшки API"
    version: str = "0.0.1"
    summary: str = "API для покупки UC (PUBG Mobile)"
    description: str = Field(default_factory=_load_description)
    doc_url: str | None = "/docs"
    redoc_url: str | None = None
