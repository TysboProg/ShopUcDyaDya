# Архитектура ShopUcDyaDya

Документ описывает фактическое состояние проекта и целевое направление развития.
Дата аудита: 20 сентября 2026 года.

## 1. Краткий вывод

Проект сейчас находится на стадии технического каркаса, а не готового магазина.
Рабочие инфраструктурные части уже есть:

- FastAPI и Aiogram запускаются как отдельные процессы;
- PostgreSQL используется как основная БД, кэш, rate limiter и очередь;
- Dishka используется для dependency injection;
- PgQueuer используется для фоновых задач и расписаний;
- Alembic используется для миграций.

При этом заявленная предметная архитектура пока опережает код. В репозитории
реально реализован модуль `promocodes` и технический `health`; модулей users,
products, orders и payments пока нет. Следующий этап должен быть не расширением
случайных роутеров, а выделением вертикальных бизнес-срезов: модель, репозиторий,
сервис, HTTP-роутер, Telegram-handlers, задачи и миграции для одной функции.

## 2. Фактическая схема запуска

```text
Telegram
  ├─> aiogram-app
  └─> Telegram WebApp -> fastapi-app

fastapi-app ─┐
aiogram-app  ├─> PostgreSQL
pgq-worker   ┤      ├─ бизнес-таблицы
pgq-scheduler┘      ├─ psycache
                    ├─ rate_limits
                    └─ PgQueuer
```

Сервисы Compose:

- `pg` — PostgreSQL;
- `db-init` — установка схемы PgQueuer и применение Alembic-миграций;
- `fastapi-app` — HTTP-приложение;
- `aiogram-app` — Telegram-бот;
- `pgq-worker` — обработчик фоновых задач;
- `pgq-scheduler` — обработчик расписаний.

Compose ждёт завершения `db-init`, который сначала устанавливает PgQueuer
(если он ещё не установлен), а затем выполняет `alembic upgrade head`. После
этого запускаются worker/scheduler и приложения в соответствии с их
`depends_on`.

## 3. Что в текущем проекте сделано удачно

- Есть раздельные entrypoint-ы FastAPI и Aiogram.
- Общие зависимости вынесены в Dishka providers.
- Сессия SQLAlchemy ограничена request scope, engine — app scope.
- PgQueuer используется вместо отдельного брокера сообщений.
- `db-init` не должен удалять данные при каждом старте; PgQueuer пропускает
  повторную установку, а Alembic применяет только отсутствующие миграции.
- Кэш и rate limit имеют общий PostgreSQL-слой.
- В Docker используется отдельный непривилегированный `appuser`.
- Есть базовая проверка PostgreSQL через Testcontainers.

## 4. Основные слабые и скрытые места

### 4.1. Архитектура и код расходятся

В документе описаны users, products, orders и payments, но исходники содержат
только `modules/promocodes`, `modules/health` и общую модель. Из-за этого легко
создать ложное ощущение готовности системы.

Правило: завершённым считать только тот модуль, у которого есть:

1. доменные модели и ограничения;
2. миграция;
3. repository или query layer;
4. application service с транзакционными границами;
5. HTTP/Telegram adapter;
6. unit и integration tests;
7. health/metrics или понятная эксплуатационная диагностика.

### 4.2. Миграции опасны без дисциплины

Миграции должны быть единственным владельцем схемы приложения. Нельзя включать в
автосгенерированную миграцию удаление таблиц PgQueuer или psycache только потому,
что SQLAlchemy metadata о них не знает. Такие внешние таблицы не являются
основанием для `drop_table`.

Перед применением миграции нужно проверять:

```text
alembic upgrade head
alembic downgrade -1   # только в development/test
```

Миграции production должны быть forward-only: исправление уже применённой
миграции делается новой миграцией, а не переписыванием старой.

`db-init` выполняет `pgq install`, Alembic upgrade, инициализацию psycache и
выдачу прав runtime-роли последовательными отдельными шагами. API, бот, worker
и scheduler стартуют после успешного завершения job. Ошибка любого шага должна
завершать `db-init` с ненулевым кодом.

### 4.3. Глобальные singleton-ы усложняют тесты и lifecycle

Объекты `settings`, `broker`, `scheduler` и глобальный `Dispatcher` создаются при
импорте модулей. Это создаёт скрытое состояние между тестами, осложняет запуск
нескольких приложений в одном процессе и затрудняет graceful shutdown.

Целевое правило:

- конфигурация создаётся один раз на composition root;
- broker/scheduler передаются через Dishka;
- routers и handlers не импортируют глобальные подключения;
- lifecycle каждого ресурса закрывается тем контейнером, который его создал.

На переходном этапе глобальный `broker` допустим, но нельзя добавлять новые
глобальные клиенты и соединения.

### 4.4. Брокер может быть запущен слишком рано или дважды

`BrokerProvider` стартует broker при создании app-scoped зависимости, а
`PgQueuerTask.kiq()` также умеет запускать его лениво. Нужно выбрать одну модель:

- для API: broker стартует в lifespan и закрывается там;
- для worker: worker владеет одним отдельным connection;
- producer и consumer никогда не используют одно соединение.

Регистрация задач должна выполняться до `broker.start()`. Все задачи должны быть
импортированы в producer и worker одинаково, иначе producer может поставить имя
задачи, которое consumer не зарегистрировал.

### 4.5. Надёжность очереди пока не определена

Для каждой задачи нужно явно определить:

- идемпотентна ли она;
- максимальное число попыток;
- backoff;
- dead-letter/failed status;
- что делать после частичного внешнего эффекта;
- как коррелировать задачу с `order_id`.

Особенно опасны платежи и выдача UC: повторная доставка задачи не должна создать
двойную оплату или повторно выдать товар. Состояние заказа и операции выдачи
должны защищаться уникальными ключами и транзакциями.

### 4.6. Rate limit нельзя строить только на IP

Для Telegram WebApp и Telegram-бота IP не является устойчивой идентичностью.
Нужны отдельные стратегии:

- Telegram user id для бота;
- проверенный Telegram `initData.user.id` для WebApp;
- IP плюс route scope только как дополнительный слой;
- отдельные лимиты для login, promo-code, payment и webhook.

Health endpoints для внутреннего мониторинга обычно не ограничиваются тем же
лимитом, что публичные пользовательские endpoints.

### 4.7. Секреты и окружение

Пароли PostgreSQL, bot token и proxy не должны храниться в репозитории или быть
зашиты в `docker-compose.yml`. Они должны приходить через secrets/CI variables.
Токен бота, который когда-либо попал в Git, следует немедленно перевыпустить.

Нужно разделить настройки:

```text
config/base.py
config/development.py
config/test.py
config/production.py
```

И валидировать production-настройки при старте: secure HTTPS, allowed origins,
Telegram secret, payment credentials, database SSL и отсутствие dev proxy.

### 4.8. Захардкоженный proxy

`AiohttpSession(proxy="socks5://172.26.144.1:10808")` в коде делает образ
непереносимым и ломает production. Proxy должен быть `TELEGRAM_PROXY` в настройках
и быть optional. При пустом значении должна использоваться обычная сессия.

### 4.9. Ошибки скрываются или слишком широко перехватываются

`except Exception` в health checks допустим только с логированием причины и
correlation id. В business services нельзя превращать все ошибки в `False`.
Нужно разделить:

- ожидаемые domain errors;
- ошибки валидации;
- временные ошибки БД/сети;
- программные ошибки.

Не следует использовать `assert` для пользовательских или production-проверок:
Python может запускаться с оптимизацией, и assert исчезнет.

### 4.10. Кэш не должен быть обязательным для бизнес-операций

psycache и rate limiter — инфраструктурные оптимизации. Ошибка кэша не должна
ломать выдачу каталога или критичный платёжный flow без явно принятого решения.
Для кэша нужны TTL, cleanup task, namespace и стратегия деградации.

### 4.11. Тесты пока проверяют только подключение к БД

Текущие тесты не проверяют:

- Dishka injection в FastAPI/Aiogram;
- rate limit и коды 429;
- регистрацию и выполнение PgQueuer task;
- промокоды и конкурентное использование;
- payment webhook и повторную доставку;
- Telegram WebApp `initData`;
- graceful shutdown.

Минимальный набор нужно разделить на unit, integration и contract tests. В
integration tests должны запускаться PostgreSQL, миграции, psycache и PgQueuer.

## 5. Целевая структура каталогов

Рекомендуется перейти от технического группирования к вертикальным модулям:

```text
src/shopucdyadya/
├── app/                         # composition roots и lifecycle
│   ├── config.py
│   ├── api.py                   # create_api_app
│   ├── bot.py                   # create_bot / polling entrypoint
│   ├── lifespan.py
│   └── di/
│       ├── container.py
│       └── providers/
├── domain/                      # чистые правила, без FastAPI/aiogram/SQLAlchemy
│   ├── users/
│   ├── products/
│   ├── promocodes/
│   ├── orders/
│   └── payments/
├── application/                 # use cases и ports
│   ├── users/
│   ├── orders/
│   ├── payments/
│   └── common/
├── adapters/
│   ├── http/                    # FastAPI routers, schemas, dependencies
│   ├── telegram/                # Aiogram routers, handlers, keyboards, FSM
│   └── payments/                # SDK/webhook adapters
├── infrastructure/
│   ├── database/                # SQLAlchemy models, repositories, sessions
│   ├── cache/
│   ├── queue/                   # PgQueuer producer/consumer
│   └── clock.py
├── jobs/
│   ├── tasks.py
│   ├── worker.py
│   └── scheduler.py
└── migrations/
```

Для небольшого проекта допустима упрощённая форма внутри каждого bounded
context-а:

```text
modules/orders/
├── models.py
├── schemas.py
├── repositories.py
├── services.py
├── router.py
├── handlers.py
└── tasks.py
```

Главное правило — domain/application не должны импортировать FastAPI, Aiogram,
`Request`, `Message`, SQLAlchemy session или конкретного платёжного провайдера.
Зависимости направлены внутрь:

```text
adapters -> application -> domain
infrastructure ---------^ (через ports/interfaces)
```

## 6. Границы ответственности

### Domain

Содержит состояния заказа, правила цены, промокоды, роли, переходы статусов и
доменные исключения. Domain не знает о способе доставки ответа пользователю.

### Application

Содержит use cases:

- `CreateOrder`;
- `ApplyPromocode`;
- `StartPayment`;
- `HandlePaymentWebhook`;
- `CompleteOrder`;
- `NotifyUser`.

Use case открывает транзакционную границу, вызывает ports и возвращает DTO.

### Adapters

FastAPI и Aiogram только преобразуют входные данные, вызывают use case и
преобразуют результат в HTTP/Telegram response. Нельзя помещать в handlers SQL,
расчёт цен или переходы статусов.

### Infrastructure

Реализует ports: repositories, payment clients, Telegram notifier, cache и queue.
Здесь находятся retry, timeout, connection pool и технические логи.

## 7. Ключевые бизнес-инварианты

- Цена заказа фиксируется в момент создания/начала оплаты.
- Промокод нельзя применить дважды к несовместимым заказам.
- Webhook платежа идемпотентен по provider event id.
- Один заказ не может перейти из финального статуса обратно в активный.
- Выдача UC выполняется не более одного раза.
- Все денежные значения хранятся в минимальных единицах или Decimal, не float.
- Внешний Telegram user id имеет уникальный индекс.
- Публичные идентификаторы и внутренние primary keys не смешиваются без причины.

## 8. Рекомендуемый порядок развития

### Этап 1 — стабилизация платформы

1. Добавить `db-migrate` в Compose и healthcheck миграций.
2. Убрать секреты и proxy из исходников.
3. Зафиксировать версии runtime-зависимостей, а не только нижние границы.
4. Убрать опасные автосгенерированные drop-операции из миграций.
5. Добавить structured logging и request/update correlation id.
6. Написать smoke-тест старта API, бота, worker и scheduler.

### Этап 2 — пользователи и каталог

1. `users`: Telegram identity, роль, блокировка.
2. `products`: каталог, цена, валюта, active flag.
3. Получение каталога в WebApp и команда `/start` через application services.
4. Unit tests для ролей, цены и доступности товара.

### Этап 3 — заказ и промокод

1. Создание draft order в транзакции.
2. Конкурентно безопасное применение промокода.
3. State machine заказа вместо свободных присваиваний статуса.
4. Outbox event для уведомлений и фоновых задач.

### Этап 4 — оплата и выдача

1. Adapter конкретного payment provider.
2. Идемпотентный webhook.
3. `payment_events` с уникальным provider event id.
4. Очередь `deliver_order` с retry и защитой от повторной выдачи.
5. Аудит действий администратора.

### Этап 5 — production readiness

1. TLS и стабильный reverse proxy вместо Ngrok.
2. Метрики: latency, 5xx, queue lag, failed jobs, payment states.
3. Sentry/traceback aggregation с очисткой секретов.
4. Backup/restore drill для PostgreSQL.
5. Rollback plan для миграций и blue/green или rolling deployment.

## 9. Definition of Done для нового модуля

Новый business module считается готовым только если:

- сценарий описан в application service;
- есть database constraints и миграция;
- есть repository tests на PostgreSQL;
- есть API/Telegram adapter;
- есть authorization и rate limit;
- внешние вызовы имеют timeout и retry policy;
- фоновые задачи идемпотентны;
- есть structured logs и health signal;
- документация и пример запуска обновлены.

## 10. Архитектурное решение на ближайший этап

Не следует сейчас добавлять сложный event bus, микросервисы или отдельный Redis.
PostgreSQL и PgQueuer подходят для текущего масштаба. Основной приоритет —
границы модулей, безопасные миграции, идемпотентность платежей/очереди, тесты и
секреты. После появления устойчивой модели orders/payments можно выделять
отдельные adapters и outbox, не меняя доменные правила.
