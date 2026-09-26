import logging

from shopucdyadya.infra.broker import broker

logger = logging.getLogger(__name__)


@broker.task("health.audit")
async def audit_health(component: str, result: str) -> None:
    logger.info(
        "Health audit: component=%s result=%s",
        component,
        result,
    )
