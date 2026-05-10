from typing import Callable

from src.contracts.task_source import TaskSource

SourceFactory = Callable[..., TaskSource]

REGISTRY: dict[str, SourceFactory] = {}

def register_source(source: str) -> Callable[[SourceFactory], SourceFactory]:
    """
    Регистрирует фабрику источника задач в общем реестре

    :param source: имя источника, по которому его можно будет найти
    :return: декоратор, сохраняющий фабрику в REGISTRY
    """
    def _decorator(factory: SourceFactory) -> SourceFactory:
        if source in REGISTRY:
            raise ValueError(f"Источник {source!r} уже зарегистрирован")
        REGISTRY[source] = factory
        return factory

    return _decorator
