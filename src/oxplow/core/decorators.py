from oxplow.core.models import Model
from oxplow.registry import registry
from oxplow.types import DatabaseType


def Postgres(cls: type[Model]) -> type[Model]:
    cls.__engine_type__ = DatabaseType.POSTGRESQL
    registry.register_model(DatabaseType.POSTGRESQL, cls)
    return cls
