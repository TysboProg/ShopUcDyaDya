from taskiq_aio_pika import AioPikaBroker

from shopucdyadya.app.config import settings

broker = AioPikaBroker(url=settings.broker_url.encoded_string())
