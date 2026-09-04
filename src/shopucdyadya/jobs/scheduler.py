from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from shopucdyadya.infra.broker import broker

scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])
