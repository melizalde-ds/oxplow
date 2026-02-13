class Registry:
    registry: dict[str, object]

    def __init__(self):
        self._registry = {}
