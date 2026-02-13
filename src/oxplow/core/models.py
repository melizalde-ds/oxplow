from typing import TypeVar, Generic


class Model:
    __table__: str
    __fields__: dict[str, Field[object]]
    __db__: object
    __engine_type__: object

    def __init_subclass__(cls) -> None:
        cls.__fields__ = {}
        for key, _value in cls.__annotations__.items():
            field_value = getattr(cls, key, None)
            if isinstance(field_value, Field):
                cls.__fields__[key] = field_value
            else:
                cls.__fields__[key] = Field()


T = TypeVar('T')


class Field(Generic[T]):
    def __init__(
        self,
        *,
        primary_key: bool = False,
        unique: bool = False,
        nullable: bool = False,
        default: object = None,
        max_length: int | None = None,
    ):
        self.primary_key = primary_key
        self.unique = unique
        self.nullable = nullable
        self.default = default
        self.max_length = max_length

    def __str__(self) -> str:
        primary_key_str = "primary_key=True" if self.primary_key else ""
        unique_str = "unique=True" if self.unique else ""
        nullable_str = "nullable=True" if self.nullable else ""
        default_str = f"default={self.default}" if self.default is not None else ""
        max_length_str = f"max_length={self.max_length}" if self.max_length is not None else ""
        return ", ".join(filter(None, [primary_key_str, unique_str, nullable_str, default_str, max_length_str]))

    def __repr__(self) -> str:
        return self.__str__()
