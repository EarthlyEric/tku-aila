import logging
import redis
logger = logging.getLogger('tku-aila')

class Checker:
    def __init__(self, redis_url: str = None):
        self.redis_client = redis.Redis.from_url(redis_url)
        
    def redis_is_available(self) -> bool:
        try:
            self.redis_client.ping()
            logger.info("Redis ping successful.")
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False