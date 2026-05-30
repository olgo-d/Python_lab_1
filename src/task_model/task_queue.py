from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import cast
import logging

from src.contracts.task_source import TaskSource
from src.task_model.descriptors import TaskStatus
from src.task_model.task import Task
from src.task_model.error_tasks import TaskStatusError, TaskPriorityError

logger = logging.getLogger(__name__)


class TaskQueue:
    """
    Очередь задач объединяющая несколько источников задач.

    Хранит только источники, сами задачи получает лениво
    во время итерации.
    """

    def __init__(self, sources: Iterable[TaskSource]) -> None:
        self._sources: list[TaskSource] = list(sources)

    def __iter__(self) -> Iterator[Task]:
        """
        Лениво возвращает задачи из всех источников.

        При каждом новом обходе создаётся новый итератор,
        поэтому очередь можно обходить повторно.
        """
        for source in self._sources:
            if not isinstance(source, TaskSource):
                logger.error(
                    "%s не соответствует контракту источника задач TaskSource",
                    type(source).__name__,
                )
                raise TypeError(
                    f"{type(source).__name__} не соответствует контракту источника задач TaskSource"
                )

            for task in source.get_tasks():
                yield task

    def filter_by_statuses(self, statuses: Iterable[TaskStatus | str]) -> Iterator[Task]:
        """
        Лениво возвращает задачи с указанными статусами.
        """
        normalized_statuses = self._normalize_statuses(statuses)

        for task in self:
            if task.status in normalized_statuses:
                yield task

    def filter_by_priority(
        self,
        min_priority: int | None = None,
        max_priority: int | None = None,
    ) -> Iterator[Task]:
        """
        Лениво возвращает задачи в заданном диапазоне приоритетов.
        """
        if min_priority is not None and max_priority is not None:
            if min_priority > max_priority:
                raise TaskPriorityError("min_priority не может быть больше max_priority")

        for task in self:
            priority = cast(int, task.priority)

            if min_priority is not None and priority < min_priority:
                continue

            if max_priority is not None and priority > max_priority:
                continue

            yield task

    @staticmethod
    def _normalize_statuses(statuses: Iterable[TaskStatus | str]) -> set[TaskStatus]:
        """
        Преобразует итерируемую коллекцию статусов таким образом,
        чтобы все её элементы были экземплярами класса TaskStatus.
        """
        normalized_statuses: set[TaskStatus] = set()

        for status in statuses:
            if isinstance(status, TaskStatus):
                normalized_statuses.add(status)
            elif isinstance(status, str):
                try:
                    normalized_statuses.add(TaskStatus(status.lower()))
                except ValueError as exc:
                    raise TaskStatusError(f"Недопустимый статус задачи {status}") from exc
            else:
                raise TaskStatusError("статус должен быть TaskStatus или строкой")

        return normalized_statuses
