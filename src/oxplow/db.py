from abc import ABC, abstractmethod
from enum import Enum
from oxpg import Client as oxpgClient
from oxpg import InterfaceError
from .errors import ConfigurationError
import oxpg


class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


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

    def __init__(self, *, dsn: str | None = None, host: str | None = None, port: int | None = None,
                 user: str | None = None, password: str | None = None,
                 db: str | None = None):
        if not dsn and not (host and port and user and password and db):
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Must provide either dsn or all connection parameters"
            )
        if dsn and (host or port or user or password or db):
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Cannot provide both dsn and individual connection parameters"
            )
        try:
            if dsn:
                self.client = oxpg.connect(dsn)
            else:
                self.client = oxpg.connect(
                    host=host,
                    user=user,
                    password=password,
                    port=port if port is not None else 5432,
                    db=db if db is not None else "postgres"
                )
        except InterfaceError as ie:
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Failed to create client with provided configuration",
                source=ie
            ) from ie
        except Exception as e:
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Unexpected error during client initialization",
                source=e
            ) from e

    def disconnect(self):
        pass
