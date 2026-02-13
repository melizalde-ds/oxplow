from unittest import TestCase

from oxplow.db import Database, DatabaseType


class TestDatabase(TestCase):
    def test_database_initialization(self):
        with self.assertRaises(TypeError):
            db = Database(DatabaseType.POSTGRESQL)  # type: ignore
