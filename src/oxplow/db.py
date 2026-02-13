from abc import ABC, abstractmethod
from enum import Enum
from oxpg import Client as oxpgClient
import oxpg


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


class DatabaseAttributes:
    host: str
    port: int
    username: str
    password: str
    database: str


class Database(ABC):
    engine: DatabaseType

    def __init__(self, engine: DatabaseType):
        self.engine = engine

    @abstractmethod
    def disconnect(self):
        pass


class PostgresDatabase(Database):
    engine = DatabaseType.POSTGRESQL
    client: oxpgClient

    def __init__(self, dsn: str | None = None, attributes: DatabaseAttributes | None = None):
        if not dsn and not attributes:
            raise ValueError("Either DSN or attributes must be provided.")
        if dsn and attributes:
            raise ValueError(
                "Only one of DSN or attributes should be provided.")
        super().__init__(self.engine)
        self.client = oxpg.connect(
            dsn=dsn, **vars(attributes) if attributes else {})

    def disconnect(self):
        pass


class MongoDatabase(Database):
    engine = DatabaseType.MONGODB

    def disconnect(self):
        pass
