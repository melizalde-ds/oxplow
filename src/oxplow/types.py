from enum import Enum


class DatabaseType(Enum):
    POSTGRESQL = "Postgresql"
    MONGODB = "Mongodb"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.__str__()
