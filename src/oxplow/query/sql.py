from __future__ import annotations

from typing import TYPE_CHECKING

from oxplow.db import PostgresDatabase

if TYPE_CHECKING:
    from oxplow.db import Database


class SQLStatement:
    @staticmethod
    def insert(table: str, data: dict[str, object]) -> tuple[str, list[object]]:
        keys = list(data.keys())
        values = list(data.values())
        columns = ", ".join(keys)
        placeholders = ", ".join(f"${i+1}" for i in range(len(keys)))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return (sql, values)

    @staticmethod
    def select(table: str,  data: dict[str, object]) -> tuple[str, list[object]]:
        ...

    @staticmethod
    def update():
        ...

    @staticmethod
    def delete():
        ...


class PostgresEngine:
    @staticmethod
    def insert(db: Database, table: str, data: dict[str, object]) -> list[dict[str, object]]:
        if not isinstance(db, PostgresDatabase):
            raise TypeError("Expected a PostgresDatabase instance")
        (sql, params) = SQLStatement.insert(table, data)
        print(f"Executing SQL: {sql} with data: {data}")
        result: list[dict[str, object]] = db.client.query(  # type: ignore
            sql, *params)
        return result

    @staticmethod
    def select(db: Database, table: str, where: dict[str, object]):
        pass

    @staticmethod
    def update(db: Database, table: str, data: dict[str, object], where: dict[str, object]):
        pass

    @staticmethod
    def delete(db: Database, table: str, where: dict[str, object]):
        pass
