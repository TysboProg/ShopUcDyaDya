from fastapi import APIRouter

from shopucdyadya.api.orders import router as order_router
from shopucdyadya.api.packages import router as packages_router
from shopucdyadya.api.payments import router as payments_router
from shopucdyadya.api.supports import router as support_router
from shopucdyadya.api.users import router as users_router

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}


router.include_router(users_router)
router.include_router(payments_router)
router.include_router(order_router)
router.include_router(packages_router)
router.include_router(support_router)
