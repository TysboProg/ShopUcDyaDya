# Uncle's Shop

Uncle's Shop is a Telegram-based PUBG Mobile UC top-up service. Customers will be able to browse available UC packages, place an order, pay for it, and receive their purchase through the Telegram bot.

The project is under development. The features below describe the intended customer experience at the final stage; availability may vary while development is in progress.

## Planned customer features

- Browse the available PUBG Mobile UC packages and their prices.
- Place and pay for an order using the supported payment methods.
- Receive the purchased UC through a redemption code delivered by the Telegram bot.
- View order progress and receive purchase notifications in Telegram.
- Contact customer support for help with orders and payments.
- Use the shop through a Telegram Mini App with Telegram account verification.

## Requirements

- Docker Desktop (Windows/macOS) or Docker Engine with the Docker Compose plugin (Linux).
- A Telegram bot and its bot token, created through [BotFather](https://t.me/BotFather).
- An ngrok account with an authtoken and a public HTTPS domain for Telegram Mini App access.

## Configure the environment

Create a private `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

On Linux or macOS:

```sh
cp .env.example .env
```

Edit `.env` and replace every example value with your own credentials. In particular:

- Set `POSTGRES_PASSWORD`, `RUNTIME_DB_PASSWORD`, and `MIGRATION_DB_PASSWORD` to separate strong passwords.
- Keep the usernames and database name in the two database URLs consistent with `RUNTIME_DB_USER`, `MIGRATION_DB_USER`, and `POSTGRES_DB`.
- URL-encode reserved characters in database passwords before placing them in `RUNTIME_DB_URL` and `MIGRATION_DB_URL`.
- Set `BOT_TOKEN` to the token from BotFather.
- Set `NGROK_AUTHTOKEN` to your ngrok agent token.
- Set `WEBAPP_URL` to the exact HTTPS domain configured in your ngrok account, for example `https://your-domain.ngrok-free.app`.
- Keep `CORS_ORIGINS` as `[]` when the web app is served through the same origin. If using a separate frontend, set it to a JSON list of its allowed origins, such as `["https://shop.example.com"]`.
- Set `PROXY_URL` only if the bot needs an outbound proxy; otherwise leave it empty.

Do not commit `.env` or put real credentials in `.env.example`.

## Build and start

From the project directory, run:

```sh
docker compose up --build -d
```

Compose starts PostgreSQL, prepares the database, and then starts the API, Telegram bot, background worker, scheduler, and ngrok tunnel. The first run may take a few minutes while images are built and the database is initialized.

Check service status and logs:

```sh
docker compose ps
docker compose logs -f
```

To stop the services while preserving database data:

```sh
docker compose down
```

To stop the services and permanently remove the Compose database volume and its data:

```sh
docker compose down --volumes
```

## Open the shop in Telegram

After the services start, open your bot in Telegram and send `/start`. Tap the shop button to open the Mini App. Telegram authentication data is required for protected shop endpoints; opening those endpoints directly in a regular browser is expected to fail authentication.

The ngrok domain in `WEBAPP_URL` must be the same public HTTPS domain configured for your ngrok account. The tunnel forwards requests to the local API service.

## Local development

The Docker Compose setup is the recommended way to run the full application because it also provides PostgreSQL and the public tunnel. To run Python tooling locally, install [uv](https://docs.astral.sh/uv/) and sync the project environment:

```sh
uv sync
```

Configure the required environment variables in `.env` before starting application commands. For a local API process, the database URL must use a host and port reachable from your machine rather than the Compose-only hostname `pg`.
