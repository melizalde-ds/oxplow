from abc import ABC, abstractmethod

import oxpg
from oxpg import Client as oxpgClient
from oxpg import InterfaceError

from oxplow.registry import registry

from .errors import ConfigurationError
from .types import DatabaseType


class Database(ABC):
    name: str
    engine: DatabaseType
    __db_engine__: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class PostgresDatabase(Database):
    engine = DatabaseType.POSTGRESQL
    client: oxpgClient

    def __init__(
        self,
        dsn: str | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        db: str | None = None,
        name: str = "postgres",
    ) -> None:
        super().__init__(name=name)
        if not dsn and not (host and user and password or (db or port)):
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Must provide either dsn or all connection parameters",
            )

        if dsn and (host or port or user or password or db):
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Cannot provide both dsn and individual connection parameters",
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
                    db=db if db is not None else "postgres",
                )
            registry.register_database(self)
        except InterfaceError as ie:
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Failed to create client with provided configuration",
                source=ie,
            ) from ie
        except Exception as e:
            raise ConfigurationError(
                engine="PostgreSQL",
                reason="Unexpected error during client initialization",
                source=e,
            ) from e

    def disconnect(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"PostgresDatabase(name={self.name})"

    def __str__(self) -> str:
        return f"PostgresDatabase(name={self.name})"
