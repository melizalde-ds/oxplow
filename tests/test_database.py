from unittest import TestCase
from oxplow.errors import ConfigurationError
from oxplow.db import Database, DatabaseType
from oxplow import PostgresDatabase


class TestDatabase(TestCase):
    def test_database_initialization(self):
        with self.assertRaises(TypeError):
            db = Database(DatabaseType.POSTGRESQL)  # type: ignore


class TestPostgresDatabase(TestCase):
    def test_postgres_initialization_with_dsn(self):
        dsn = "postgresql://user:pass@localhost:5432/dbname"
        db = PostgresDatabase(dsn=dsn)
        self.assertEqual(db.engine, DatabaseType.POSTGRESQL)
        self.assertIsNotNone(db.client)

    def test_postgres_initialization_with_attributes(self):
        db = PostgresDatabase(
            host="localhost",
            port=5432,
            user="user",
            password="pass",
            db="dbname"
        )
        self.assertEqual(db.engine, DatabaseType.POSTGRESQL)
        self.assertIsNotNone(db.client)

    def test_postgres_initialization_with_both_dsn_and_attributes(self):
        with self.assertRaises(ConfigurationError):
            db = PostgresDatabase(  # type: ignore
                dsn="postgresql://user:pass@localhost:5432/dbname",
                host="localhost",
                port=5432,
                user="user",
                password="pass",
                db="dbname"
            )
