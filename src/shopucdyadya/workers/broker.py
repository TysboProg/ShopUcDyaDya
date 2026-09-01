from taskiq_aio_pika import AioPikaBroker

from shopucdyadya.core.config import settings

broker = AioPikaBroker(url=settings.broker_url.encoded_string())
