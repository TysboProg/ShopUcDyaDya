# Альтернативная файловая архитектура backend

Цель этой архитектуры - уменьшить количество разрозненных папок и сделать проект понятнее по бизнес-смыслу. Сейчас структура в основном разделена по техническим слоям: `api`, `services`, `repositories`, `schemas`, `models`, `integrations`, `di`, `db`, `workers`. Такой подход быстро разрастается: чтобы понять одну фичу, например заказы, нужно прыгать между несколькими папками.

Более удобный вариант для этого проекта - группировать код по доменам: пользователи, заказы, пакеты UC, платежи, поддержка.

## Предлагаемая структура

```text
backend/
├── src/
│   └── shopucdyadya/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── app/
│       │   ├── __init__.py
│       │   ├── factory.py
│       │   ├── config.py
│       │   ├── openapi.py
│       │   └── di.py
│       │
│       ├── modules/
│       │   ├── __init__.py
│       │   │
│       │   ├── users/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── models.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── orders/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── models.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── packages/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── models.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── payments/
│       │   │   ├── __init__.py
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   └── gateway.py
│       │   │
│       │   └── support/
│       │       ├── __init__.py
│       │       ├── router.py
│       │       ├── service.py
│       │       ├── repository.py
│       │       ├── models.py
│       │       └── schemas.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── base_model.py
│       │   ├── mixins.py
│       │   ├── redis.py
│       │   └── broker.py
│       │
│       ├── jobs/
│       │   ├── __init__.py
│       │   ├── scheduler.py
│       │   └── tasks.py
│       │
│       └── migrations/
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── modules/
│   │   ├── users/
│   │   ├── orders/
│   │   ├── packages/
│   │   ├── payments/
│   │   └── support/
│   └── infrastructure/
│
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Что куда переносится

| Сейчас                               | Новое место                                          | Зачем                                                         |
|--------------------------------------|------------------------------------------------------|---------------------------------------------------------------|
| `core/config.py`                     | `app/config.py`                                      | Настройки приложения ближе к созданию приложения.             |
| `core/app.py`                        | `app/factory.py` или часть `app/config.py`           | Конфигурация FastAPI и middleware в одном месте.              |
| `core/openapi.py`                    | `app/openapi.py`                                     | OpenAPI - часть настройки приложения.                         |
| `di/container.py` и `di/providers/*` | `app/di.py`                                          | На старте проекта отдельная папка `di/providers` избыточна.   |
| `api/users.py`                       | `modules/users/router.py`                            | Роутер лежит рядом со всем кодом пользователей.               |
| `api/orders.py`                      | `modules/orders/router.py`                           | Роутер лежит рядом с сервисом, схемами и моделями заказов.    |
| `api/packages.py`                    | `modules/packages/router.py`                         | Все про пакеты UC в одном модуле.                             |
| `api/payments.py`                    | `modules/payments/router.py`                         | Все про оплату в одном модуле.                                |
| `api/supports.py`                    | `modules/support/router.py`                          | Поддержка как отдельный домен.                                |
| `models/*`                           | `modules/<domain>/models.py`                         | Модели хранятся рядом с доменом.                              |
| `schemas/*`                          | `modules/<domain>/schemas.py`                        | Pydantic-схемы хранятся рядом с API и сервисом.               |
| `repositories/*`                     | `modules/<domain>/repository.py`                     | Репозиторий не нужно искать в отдельной общей папке.          |
| `services/*`                         | `modules/<domain>/service.py`                        | Бизнес-логика лежит в домене.                                 |
| `integrations/*`                     | `modules/payments/gateway.py` или `infrastructure/*` | Интеграции держим там, где они используются.                  |
| `db/*`                               | `infrastructure/*`                                   | Общая техническая инфраструктура: БД, Redis, брокер.          |
| `db/migrations/*`                    | `migrations/*`                                       | Alembic обычно удобнее держать отдельной папкой у приложения. |
| `workers/*`                          | `jobs/*`                                             | Короткое и понятное имя для фоновых задач.                    |

## Главная идея

Каждый бизнес-модуль должен быть самодостаточным:

```text
modules/orders/
├── router.py       # HTTP endpoints: FastAPI routes
├── service.py      # бизнес-логика заказов
├── repository.py   # запросы к базе по заказам
├── models.py       # SQLAlchemy-модели заказов
└── schemas.py      # Pydantic-схемы request/response
```

Когда нужно изменить заказы, почти все нужные файлы лежат в `modules/orders`. Не нужно открывать `api`, `schemas`, `models`, `repositories` и `services` отдельно.

## Правила создания файлов

1. Новый бизнес-раздел создается в `modules/<name>`.
2. Если в модуле только один endpoint и нет бизнес-логики, можно начать только с `router.py`.
3. `service.py` создается, когда появляется логика сложнее простого вызова репозитория.
4. `repository.py` создается, когда модуль начинает читать или писать в базу.
5. `models.py` создается только если у модуля есть свои таблицы.
6. `schemas.py` создается, когда появляются Pydantic request/response модели.
7. Общие технические вещи кладутся в `infrastructure`, а не в бизнес-модули.
8. Общие бизнес-утилиты лучше не создавать заранее. Сначала держать код в конкретном модуле, выносить только при реальном повторении.

## Импорты

Пример для роутера заказов:

```python
from fastapi import APIRouter

from shopucdyadya.modules.orders.schemas import OrderCreate, OrderRead
from shopucdyadya.modules.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])
```

Пример общего роутера:

```python
from fastapi import APIRouter

from shopucdyadya.modules.orders.router import router as orders_router
from shopucdyadya.modules.packages.router import router as packages_router
from shopucdyadya.modules.payments.router import router as payments_router
from shopucdyadya.modules.support.router import router as support_router
from shopucdyadya.modules.users.router import router as users_router

router = APIRouter()

router.include_router(users_router)
router.include_router(packages_router)
router.include_router(orders_router)
router.include_router(payments_router)
router.include_router(support_router)
```

## Почему это лучше текущего варианта

- Меньше верхнеуровневых папок внутри `shopucdyadya`.
- Проще искать код конкретной фичи.
- Проще удалять или переписывать фичу целиком.
- Меньше пустых папок на ранней стадии проекта.
- Новым разработчикам легче понять, где лежит логика.
- Архитектура хорошо растет: если модуль станет большим, его можно дробить уже внутри `modules/<domain>`.

## Когда модуль станет слишком большим

Если, например, `orders` разрастется, его можно расширить так:

```text
modules/orders/
├── router.py
├── service.py
├── repository.py
├── models.py
├── schemas.py
├── statuses.py
├── exceptions.py
└── use_cases/
    ├── create_order.py
    ├── cancel_order.py
    └── complete_order.py
```

Но такую вложенность стоит добавлять только после появления реальной сложности. На старте проекта лучше держать модуль плоским.

## План мягкого перехода

1. Создать папки `app`, `modules`, `infrastructure`, `jobs`, `migrations`.
2. Перенести `core/*` в `app/*`.
3. Перенести роутеры из `api/*` в `modules/<domain>/router.py`.
4. Перенести пустые или будущие `services`, `repositories`, `schemas`, `models` внутрь доменных модулей.
5. Перенести `db/base.py` и mixins в `infrastructure`.
6. Перенести `workers/*` в `jobs/*`.
7. Обновить импорты.
8. Обновить `alembic.ini`, если путь миграций изменится.
9. Запустить `ruff`, `mypy` и `pytest`.

## Минимальный вариант, если не хочется большого переноса

Можно сделать более осторожный вариант:

```text
src/shopucdyadya/
├── main.py
├── app/
│   ├── config.py
│   ├── openapi.py
│   └── di.py
├── modules/
│   ├── users/
│   ├── orders/
│   ├── packages/
│   ├── payments/
│   └── support/
├── infrastructure/
│   ├── db/
│   ├── redis.py
│   └── broker.py
└── jobs/
```

Это уже убирает лишние верхнеуровневые папки, но не требует сразу идеально раскладывать весь код.

## Рекомендация

Для текущей стадии проекта я бы выбрал доменную структуру `modules/<domain>` и не создавал файлы заранее. Например, если у `users` пока есть только пустой роутер, достаточно:

```text
modules/users/
├── __init__.py
└── router.py
```

`service.py`, `repository.py`, `models.py` и `schemas.py` стоит добавлять только тогда, когда они действительно понадобятся.
