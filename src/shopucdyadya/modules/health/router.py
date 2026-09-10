from enum import StrEnum
from typing import Protocol

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from shopucdyadya.modules.health.services import (
    BrokerHealthCheck,
    DatabaseHealthCheck,
    RedisHealthCheck,
)

router = APIRouter(prefix="/health", tags=["Health"])


class HealthStatus(StrEnum):
    OK = "ok"
    UNAVAILABLE = "unavailable"


class HealthResponse(BaseModel):
    status: HealthStatus


class HealthCheck(Protocol):
    async def is_available(self) -> bool: ...


async def _check_dependency(check: HealthCheck, response: Response) -> HealthResponse:
    if await check.is_available():
        return HealthResponse(status=HealthStatus.OK)

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status=HealthStatus.UNAVAILABLE)


@router.get("/database", response_model=HealthResponse)
@inject
async def check_database(
    response: Response,
    check: FromDishka[DatabaseHealthCheck],
) -> HealthResponse:
    return await _check_dependency(check, response)


@router.get("/redis", response_model=HealthResponse)
@inject
async def check_redis(
    response: Response,
    check: FromDishka[RedisHealthCheck],
) -> HealthResponse:
    return await _check_dependency(check, response)


@router.get("/broker", response_model=HealthResponse)
@inject
async def check_broker(
    response: Response,
    check: FromDishka[BrokerHealthCheck],
) -> HealthResponse:
    return await _check_dependency(check, response)
