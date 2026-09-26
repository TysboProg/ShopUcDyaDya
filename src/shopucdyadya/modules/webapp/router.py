from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from shopucdyadya.modules.dependencies import rate_limit, require_telegram_user_id

PACKAGE_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(
    directory=PACKAGE_DIR / "templates",
)

router = APIRouter(tags=["WebApp"])


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ShopUcDyaDya",
        },
    )


@router.get(
    "/products/fragment",
    response_class=HTMLResponse,
    dependencies=[Depends(rate_limit), Depends(require_telegram_user_id)],
)
async def product_list(request: Request) -> HTMLResponse:
    products = [
        {
            "id": 1,
            "name": "Starter Pack",
            "uc_amount": 60,
        },
        {
            "id": 2,
            "name": "Big Pack",
            "uc_amount": 660,
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="_product_list.html",
        context={"products": products},
    )
