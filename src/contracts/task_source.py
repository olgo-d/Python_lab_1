from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from src.task_model.task import Task

@runtime_checkable
class TaskSource(Protocol):
    """Контракт источника задач."""
    name: str

    def get_tasks(self) -> Iterable[Task]:
        """Возвращает поток задач."""
        ...
