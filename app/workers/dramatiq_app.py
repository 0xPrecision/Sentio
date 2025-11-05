import dramatiq
from dramatiq.brokers.redis import RedisBroker
from app.config.settings import settings

broker = RedisBroker(url=settings.redis_url)
dramatiq.set_broker(broker)
