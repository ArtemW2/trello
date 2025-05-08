from redis import Redis

from django.conf import settings

class RedisService:
    def __init__(self):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.db = settings.REDIS_DB
        self.connection = Redis(self.host, self.port, self.db)

    def set(self, key, value):
        self.connection.set(key, value)

    def get(self, key):
        return self.connection.get(key)
    
    def delete(self, key):
        self.connection.delete(key)
