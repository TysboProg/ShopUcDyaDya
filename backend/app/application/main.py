from api.routers import main_router
from application.create_app import create_app

main_app = create_app(
    create_custom_static_urls=True,
)

main_app.include_router(main_router)
