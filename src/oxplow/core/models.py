from __future__ import annotations

import typing
from typing import Any, Generic, TypeVar

import pydantic
from pydantic import BaseModel

_MISSING: Any = object()

T = TypeVar("T")


class Field(Generic[T]):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: Any = _MISSING,
        max_length: int | None = None,
    ) -> None:
        self.primary_key = primary_key
        self.unique = unique
        self.nullable = nullable
        self.default = default
        self.max_length = max_length
        self.name: str = ""
        self.python_type: type = object

    @property
    def has_default(self) -> bool:
        return self.default is not _MISSING

    def __str__(self) -> str:
        parts = [
            "primary_key=True" if self.primary_key else "",
            "unique=True" if self.unique else "",
            "nullable=True" if self.nullable else "",
            f"default={self.default!r}" if self.has_default else "",
            f"max_length={self.max_length}" if self.max_length is not None else "",
        ]
        return ", ".join(filter(None, parts))

    def __repr__(self) -> str:
        return f"Field({self})"


class Model:
    __table__: str
    __fields__: dict[str, Field[Any]]
    __db__: object
    __engine_type__: object
    _pydantic_model: type[BaseModel]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        fields: dict[str, Field[Any]] = {}

        for key, annotation in cls.__annotations__.items():
            if key.startswith("_"):
                continue

            field_value = getattr(cls, key, None)
            if isinstance(field_value, Field):
                field: Field[Any] = typing.cast(Field[Any], field_value)
            else:
                field = Field()

            field.name = key

            origin = typing.get_origin(annotation)
            if origin is Field:
                args = typing.get_args(annotation)
                field.python_type = args[0] if args else object
            else:
                field.python_type = annotation

            fields[key] = field

        cls.__fields__ = fields

        if "__table__" not in cls.__dict__:
            cls.__table__ = cls.__name__.lower() + "s"

        cls._pydantic_model = cls._build_pydantic_schema()

    @classmethod
    def _build_pydantic_schema(cls) -> type[BaseModel]:
        field_defs: dict[str, Any] = {}
        for name, field in cls.__fields__.items():
            if field.has_default:
                field_defs[name] = (field.python_type, field.default)
            else:
                field_defs[name] = (field.python_type, ...)
        return pydantic.create_model(cls.__name__, **field_defs)

    def __init__(self, **kwargs: Any) -> None:
        for name, field in self.__class__.__fields__.items():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif field.has_default:
                setattr(self, name, field.default)

    def validate(self) -> None:
        self._pydantic_model(**self._to_dict())

    def to_pydantic(self) -> BaseModel:
        return self._pydantic_model(**self._to_dict())

    def _to_dict(self) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name in self.__fields__
            if hasattr(self, name)
        }

    def __repr__(self) -> str:
        field_strs = ", ".join(
            f"{name}={getattr(self, name, _MISSING)!r}"
            for name in self.__fields__
        )
        return f"{self.__class__.__name__}({field_strs})"

    def __str__(self) -> str:
        return self.__repr__()
