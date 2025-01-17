from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class Engine(object):
    def __init__(self, database_url, database_name) -> None:
        self.database_driver = AsyncIOMotorClient(database_url)
        self.driver = self.database_driver[database_name]

    def get_database(self):
        return self.driver

    async def close(self):
        """Closes the database client connection."""
        self.database_driver.close()

    def __new__(cls, database_url, database_name: str):
        if not hasattr(cls, "instance"):
            cls.instance = super(Engine, cls).__new__(cls)
        return cls.instance


app_engine = Engine(database_url=settings.database_url, database_name=settings.app_database_name).get_database()
