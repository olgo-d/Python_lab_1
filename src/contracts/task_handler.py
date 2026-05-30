from typing import Protocol, runtime_checkable

from src.task_model.task import Task


@runtime_checkable
class TaskHandler(Protocol):
    """Контракт асинхронного источника задач"""

    name: str

    async def handle(self, task: Task) -> None:
        """Асинхронно обрабатывает задачу"""
        ...
