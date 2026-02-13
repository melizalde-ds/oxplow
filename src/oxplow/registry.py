from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oxplow.core.models import Model
    from oxplow.db import Database

from oxplow.errors import ConfigurationError
from oxplow.types import DatabaseType


class Registry:
    def __init__(self):
        self._unbound: dict[DatabaseType, list[type[Model]]] = {}
        self._bound: dict[str, list[type[Model]]] = {}
        self._databases: dict[DatabaseType, dict[str, Database]] = {}

    def register_model(self, engine: DatabaseType, cls: type[Model]) -> None:
        self._unbound.setdefault(engine, []).append(cls)

    def register_database(self, db: Database) -> None:
        if db.engine not in self._databases:
            self._databases[db.engine] = {}
        if db.name in self._databases[db.engine]:
            raise ConfigurationError(
                engine=db.engine.name,
                reason=f"Database with name '{db.name}' is already registered",
            )
        self._databases.setdefault(db.engine, {})[db.name] = db
        waiting = self._unbound.pop(db.engine, [])
        for model_cls in waiting:
            model_cls.__db__ = db
            self._bound.setdefault(db.name, []).append(model_cls)

    def __str__(self) -> str:
        bound_display = {
            db_name: [cls.__name__ for cls in models]
            for db_name, models in self._bound.items()
        }
        unbound_display = {
            engine: [cls.__name__ for cls in models]
            for engine, models in self._unbound.items()
        }
        return (
            f"Registry(\n"
            f"  databases={self._databases},\n"
            f"  bound_models={bound_display},\n"
            f"  unbound_models={unbound_display}\n"
            f")"
        )

    def __repr__(self) -> str:
        return self.__str__()


registry = Registry()
