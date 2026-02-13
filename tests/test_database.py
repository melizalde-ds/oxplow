"""Unit and integration tests for oxplow.db."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from oxpg import InterfaceError

from oxplow.db import Database, DatabaseType, PostgresDatabase
from oxplow.errors import ConfigurationError

DSN = "postgresql://user:pass@localhost:5432/dbname"


class TestDatabaseABC:
    def test_cannot_instantiate_abstract_base(self):
        with pytest.raises(TypeError):
            Database(DatabaseType.POSTGRESQL)  # type: ignore


class TestPostgresDatabaseUnit:
    """Validate configuration logic with oxpg.connect mocked out."""

    @patch("oxplow.db.oxpg.connect")
    def test_init_with_dsn(self, mock_connect: MagicMock) -> None:
        mock_connect.return_value = MagicMock()

        db = PostgresDatabase(dsn=DSN)

        assert db.engine == DatabaseType.POSTGRESQL
        assert db.client is not None
        mock_connect.assert_called_once_with(DSN)

    @patch("oxplow.db.oxpg.connect")
    def test_init_with_individual_params(self, mock_connect: MagicMock) -> None:
        mock_connect.return_value = MagicMock()

        db = PostgresDatabase(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            db="dbname",
        )

        assert db.engine == DatabaseType.POSTGRESQL
        assert db.client is not None
        mock_connect.assert_called_once_with(
            host="localhost",
            user="user",
            password="pass",
            port=5432,
            db="dbname",
        )

    def test_raises_when_no_params_given(self) -> None:
        with pytest.raises(ConfigurationError):
            PostgresDatabase()

    def test_raises_when_partial_params_given(self) -> None:
        with pytest.raises(ConfigurationError):
            PostgresDatabase(host="localhost", port=5432, user="user")

    def test_raises_when_dsn_and_params_both_given(self) -> None:
        with pytest.raises(ConfigurationError):
            PostgresDatabase(
                dsn=DSN,
                host="localhost",
                port=5432,
                user="user",
                password="pass",
                db="dbname",
            )

    @patch("oxplow.db.oxpg.connect")
    def test_interface_error_wrapped_as_configuration_error(
        self, mock_connect: MagicMock
    ) -> None:
        mock_connect.side_effect = InterfaceError("boom")  # type: ignore[arg-type]

        with pytest.raises(ConfigurationError, match="Failed to create client"):
            PostgresDatabase(dsn=DSN)

    @patch("oxplow.db.oxpg.connect")
    def test_unexpected_error_wrapped_as_configuration_error(
        self, mock_connect: MagicMock
    ) -> None:
        mock_connect.side_effect = RuntimeError("oops")

        with pytest.raises(ConfigurationError, match="Unexpected error"):
            PostgresDatabase(dsn=DSN)


@pytest.mark.integration
class TestPostgresDatabaseIntegration:
    """Tests that hit a real Postgres instance via the conftest fixtures."""

    def test_connect_and_query(self, db_dsn: str) -> None:
        db = PostgresDatabase(dsn=db_dsn)
        rows: list[dict[str, int]] = db.client.query(  # type: ignore
            "SELECT count(*) AS cnt FROM users;"
        )
        assert rows[0]["cnt"] == 3

    def test_seed_users_present(self, db_dsn: str) -> None:
        db = PostgresDatabase(dsn=db_dsn)
        rows: list[dict[str, str]] = db.client.query(  # type: ignore[assignment]
            "SELECT username FROM users ORDER BY id;"
        )
        usernames = [r["username"] for r in rows]
        assert usernames == ["alice", "bob", "charlie"]

    def test_seed_posts_present(self, db_dsn: str) -> None:
        db = PostgresDatabase(dsn=db_dsn)
        rows: list[dict[str, bool]] = db.client.query(  # type: ignore
            "SELECT title, published FROM posts ORDER BY id;"
        )
        assert len(rows) == 3
        assert rows[0]["title"] == "First Post"
        assert rows[0]["published"] is True
        assert rows[1]["published"] is False

    def test_insert_and_read_back(self, db_dsn: str) -> None:
        db = PostgresDatabase(dsn=db_dsn)
        db.client.execute(
            "INSERT INTO users (username, email) VALUES ('dave', 'dave@example.com');"
        )
        rows = db.client.query(  # type: ignore
            "SELECT username FROM users WHERE username = 'dave';"
        )
        assert len(rows) == 1  # type: ignore
        assert rows[0]["username"] == "dave"

    def test_reset_between_tests_rollback(self, db_dsn: str) -> None:
        """Verify the conftest autouse fixture truncated + re-seeded.

        If the previous test's 'dave' insert leaked, this would find 4 users.
        """
        db = PostgresDatabase(dsn=db_dsn)
        rows = db.client.query(  # type: ignore
            "SELECT count(*) AS cnt FROM users;"
        )
        assert rows[0]["cnt"] == 3

    def test_cascade_delete(self, db_dsn: str) -> None:
        db = PostgresDatabase(dsn=db_dsn)
        db.client.execute("DELETE FROM users WHERE username = 'alice';")

        users = db.client.query(  # type: ignore
            "SELECT count(*) AS cnt FROM users;"
        )
        posts = db.client.query(  # type: ignore
            "SELECT count(*) AS cnt FROM posts;"
        )

        assert users[0]["cnt"] == 2
        assert posts[0]["cnt"] == 1
