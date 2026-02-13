from __future__ import annotations

import os
import pathlib
import re
import time
from typing import Protocol, cast

import pytest
from pytest import FixtureRequest

from oxplow import PostgresDatabase

SQL_DIR = pathlib.Path(__file__).parent / "sql"

DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5432/test_db"
TEST_DSN = os.getenv("TEST_DATABASE_DSN", DEFAULT_DSN)


class OxpgClientProto(Protocol):
    def execute(self, query: str, *args: object) -> object: ...
    def query(self, query: str, *args: object) -> list[dict[str, object]]: ...


def get_client(db: PostgresDatabase) -> OxpgClientProto:
    return cast(OxpgClientProto, db.client)


def _split_statements(sql: str) -> list[str]:
    """Split a SQL string on semicolons into individual statements.

    This is intentionally naive — it works for the simple DDL/DML in our
    test fixtures.  It does NOT handle semicolons inside strings, dollar-
    quoted blocks, or PL/pgSQL.
    """
    return [s.strip() for s in re.split(r";\s*", sql) if s.strip()]


def run_sql_file(client: OxpgClientProto, path: pathlib.Path) -> None:
    sql = path.read_text(encoding="utf-8").strip()
    for stmt in _split_statements(sql):
        client.execute(stmt)


def wait_for_db(dsn: str, timeout_s: float = 30.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None

    while time.time() < deadline:
        try:
            db = PostgresDatabase(dsn=dsn)
            get_client(db).execute("SELECT 1")
            return
        except Exception as e:
            last_err = e
            time.sleep(0.25)

    raise last_err or TimeoutError("Timed out waiting for database")


def integration_enabled(config: pytest.Config) -> bool:
    markexpr = getattr(config.option, "markexpr", "") or ""
    return "integration" in markexpr


@pytest.fixture(scope="session")
def db_dsn(pytestconfig: pytest.Config) -> str:
    if not integration_enabled(pytestconfig):
        pytest.skip("Database not needed (integration tests not selected).")

    wait_for_db(TEST_DSN)

    db = PostgresDatabase(dsn=TEST_DSN)
    client = get_client(db)

    client.execute("DROP SCHEMA public CASCADE")
    client.execute("CREATE SCHEMA public")
    run_sql_file(client, SQL_DIR / "001_schema.sql")
    run_sql_file(client, SQL_DIR / "002_seed.sql")

    return TEST_DSN


@pytest.fixture(autouse=True)
def reset_db_between_tests(request: FixtureRequest) -> None:
    """Re-seed the database between integration tests.

    Only activates for tests marked ``@pytest.mark.integration``.
    Unit tests skip this entirely — no dependency on ``db_dsn``.
    """
    if "integration" not in request.keywords:
        return

    dsn: str = request.getfixturevalue("db_dsn")

    db = PostgresDatabase(dsn=dsn)
    client = get_client(db)

    client.execute("TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE")
    run_sql_file(client, SQL_DIR / "002_seed.sql")
