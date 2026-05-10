from collections.abc import Iterable, Sequence
import logging

from src.task_model.task import Task
from src.contracts.task_source import TaskSource

logger = logging.getLogger(__name__)

class InboxApp:
    """
    Прикладной слой для получения задач из нескольких источников
    :param sources: последовательность источников, реализующих TaskSource
    """
    def __init__(self, sources: Sequence[TaskSource] | None = None) -> None:
        self._sources = sources or []

    def iter_tasks(self) -> Iterable[Task]:
        """
        Возвращает задачи из всех источников
        :return: итерируемый объект с задачами
        """
        for source in self._sources:
            if not isinstance(source, TaskSource):
                logger.error("Источник %s не соответствует TaskSource", type(source).__name__)
                raise TypeError(
                    f"Источник {type(source).__name__} не соответствует TaskSource"
                )

            logger.info(
                "Получение задач из источника %s",
                getattr(source, "name",
                type(source).__name__),
            )

            try:
                yield from source.get_tasks()
            except Exception as exc:
                logger.warning(
                    "Источник %s пропущен из-за ошибки: %s",
                    type(source).__name__,
                    exc,
                )
                continue
