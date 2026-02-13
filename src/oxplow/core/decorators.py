from oxplow.core.models import Model


def Postgres(cls: type[Model]) -> type[Model]:
    print(f"Decorating {cls.__name__} with Postgres")
    return cls
