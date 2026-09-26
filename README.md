# Магазин дядюшки👀😎

Магазин дядюшки — это сайт для удобной и быстрой покупки UC для игры PUBG Mobile. С помощью этого бота пользователи могут легко пополнить свой игровой счет, выбрать нужное количество UC и получить их в кратчайшие сроки.

## Основные функции

- **Покупка UC**: Выбор нужного количества UC и оплата через удобные платежные системы.
- **Поддержка 24/7**: Круглосуточная поддержка пользователей для решения любых вопросов.
- **Автоматическая доставка**: UC приходит в виде промокода в специального тг бота для выдачи.
- **Простота использования**: Удобный интерфейс и пошаговые инструкции.

## Фоновые задачи

Очередь работает через PostgreSQL и `pgqueuer`; RabbitMQ для очереди не нужен.
Схема PgQueuer устанавливается, а Alembic-миграции применяются сервисом
`db-init`; worker запускается сервисом
`pgq-worker`.

```python
from shopucdyadya.infra.broker import broker


@broker.task("send_receipt")
async def send_receipt(order_id: int) -> None: ...


await send_receipt.kiq(order_id)
```

Аргументы задачи должны быть JSON-сериализуемыми. Для локального worker сначала
выполните `pgq install`, затем `make worker`.

## Production configuration and database roles

Never commit `.env` or `.env.docker`. `.env.docker` is no longer used by Compose
and is excluded from the Docker build context. If it has ever contained real
credentials, rotate them and remove the file from the repository history as well
as the current index.

Create a private `.env` with `Copy-Item .env.example .env` (PowerShell) or
`cp .env.example .env` (Linux/macOS), then replace every placeholder with a
different strong secret. Compose passes the migration URL only to `db-init` and
the runtime URL only to FastAPI, Aiogram, worker, and scheduler. The Postgres
bootstrap account is only for provisioning; application containers do not get
its password.

The first initialization of an empty Postgres volume runs
`docker/postgres/init/01-provision-roles.sh`. It creates two separate login
roles:

- `shopucdyadya_migrator` owns the application database and runs `pgq install`
  and `alembic upgrade head`;
- `shopucdyadya_runtime` is used by the running applications and receives
  CRUD access to tables/sequences plus execute access to public functions.

`db-init` grants the runtime role access to current objects and sets default
privileges for objects created by future migrations. For an existing database
volume, after setting the four role variables in `.env`, run the provisioning
script once as the Postgres bootstrap administrator:

```sh
docker compose exec -T pg sh /docker-entrypoint-initdb.d/01-provision-roles.sh
```

The roles can also be created manually with the database bootstrap/admin
connection (replace both password placeholders with separate strong values):

```sql
CREATE ROLE shopucdyadya_migrator LOGIN PASSWORD 'replace-with-migration-secret';
CREATE ROLE shopucdyadya_runtime LOGIN PASSWORD 'replace-with-runtime-secret';
ALTER DATABASE shopucdyadya OWNER TO shopucdyadya_migrator;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
ALTER SCHEMA public OWNER TO shopucdyadya_migrator;
GRANT CONNECT ON DATABASE shopucdyadya TO shopucdyadya_runtime;
GRANT USAGE ON SCHEMA public TO shopucdyadya_runtime;
```

The subsequent `db-init` run grants runtime CRUD, sequence, function and type
permissions on the objects PgQueuer, Alembic and psycache create, and sets
default privileges for later migrations.

Then set `RUNTIME_DB_URL` to a `postgresql+psycopg://shopucdyadya_runtime:...`
URL and `MIGRATION_DB_URL` to a distinct
`postgresql+psycopg://shopucdyadya_migrator:...` URL. URL-encode reserved
characters in passwords. Keep `POSTGRES_PASSWORD`, `RUNTIME_DB_PASSWORD`, and
`MIGRATION_DB_PASSWORD` different. In managed PostgreSQL, create the two roles
and assign database/schema ownership and grants through the provider's admin
connection before starting `db-init`.

Telegram WebApp requests send `X-Telegram-Init-Data`. The backend checks its
signature and age with the bot token before using the signed Telegram user ID
for rate limiting. Requests without Telegram data are keyed by client IP;
data endpoints should use `require_telegram_user_id` so an arbitrary client
cannot claim another user's ID. Configure `CORS_ORIGINS` as a JSON list of
specific origins. The WebApp is served by the same FastAPI origin, so CORS can
remain empty when no cross-origin frontend is used.

### Open the WebApp from Telegram through ngrok

Create an ngrok account, copy its agent authtoken, and reserve/claim a static
HTTPS ngrok domain in the dashboard. Put the token in `NGROK_AUTHTOKEN` and the
full domain, such as `https://your-name.ngrok-free.app`, in `WEBAPP_URL` in
`.env`. The `ngrok` Compose service forwards that URL to `fastapi-app:8000`, and
the bot includes the same URL in its `/start` WebApp button. Start the stack,
send `/start` to the bot, and tap **Открыть магазин**. Opening
`/products/fragment` directly in an ordinary browser has no signed Telegram
`initData` and is expected to return 401.

The configured ngrok URL must exactly match the static URL assigned to your
account. The tunnel command follows [ngrok's Docker agent guide](https://ngrok.com/download/docker).
---

**Магазин дядюшки** — ваш надежный помощник в мире PUBG Mobile! 🎮
