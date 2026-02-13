from typing import Any


class OxplowError(Exception):
    """Base exception for all oxplow errors."""

    _template: str = ""

    def __init__(self, /, source: Exception | None = None, **kwargs: Any) -> None:
        self.source = source
        self.__dict__.update(kwargs)
        msg = self._template.format(**kwargs) if self._template else ""
        super().__init__(msg)

    def __str__(self) -> str:
        msg = super().__str__()
        if self.source:
            msg += f": {self.source}"
        return msg

    def __repr__(self) -> str:
        fields = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_") and k != "source"
        }
        parts = [f"{k}={v!r}" for k, v in fields.items()]
        if self.source:
            parts.append(f"source={self.source!r}")
        return f"{type(self).__name__}({', '.join(parts)})"


class ConnectionError(OxplowError):
    """Failed to establish a database connection."""

    _template = "failed to connect to {engine} at {target}"

    def __init__(
        self,
        *,
        engine: str,
        target: str,
        source: Exception | None = None,
    ) -> None:
        self.engine: str
        self.target: str
        super().__init__(source=source, engine=engine, target=target)
