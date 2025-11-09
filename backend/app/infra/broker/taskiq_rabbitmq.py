from settings.config import settings
from taskiq import TaskiqScheduler
from taskiq_aio_pika import AioPikaBroker

rabbitmq_broker = AioPikaBroker(url=settings.rabbit.url.encoded_string())

scheduler = TaskiqScheduler(broker=rabbitmq_broker, sources=[])
