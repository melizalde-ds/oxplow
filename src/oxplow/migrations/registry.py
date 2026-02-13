from oxplow.db import Database, DatabaseType


class Registry:
    _registry: dict[DatabaseType, dict[str, Database]]

    def __init__(self):
        self._registry = {}

    def register(self, obj: Database) -> None:
        if obj.engine not in self._registry:
            self._registry[obj.engine] = {}
        self._registry[obj.engine][obj.name] = obj

    def get(self, name: str, engine: DatabaseType) -> Database:
        return self._registry[engine][name]

    def __repr__(self) -> str:
        engines_str = "\n".join(
            f"  {engine}: {list(dbs.keys())}" for engine, dbs in self._registry.items())
        return f"Registry\nEngines: {list(self._registry.keys())}\n{engines_str}"
