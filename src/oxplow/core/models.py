from abc import ABC, abstractmethod


class Model(ABC):
    __db__: object
    __engine_type__: object

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
