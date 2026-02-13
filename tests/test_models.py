
from oxplow.core.decorators import Postgres
from oxplow.core.models import Model


class TestPostgresModelDecorator:
    def test_postgres_model_decorator(self):
        @Postgres
        class User(Model):
            id: int
            name: str

        assert hasattr(User, "id")
        assert hasattr(User, "name")
