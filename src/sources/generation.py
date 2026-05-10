from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
import logging
import uuid

from src.task_model.task import Task
from src.task_model.descriptors import TaskStatus
from src.sources.register_sources import register_source

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratedSource:
    """
    Источник задач, создающий задачи программно

    :param count: количество задач для генерации
    :param name: имя источника для логирования
    """
    count: int
    name: str = "generated"

    def __post_init__(self) -> None:
        """Проверяет корректность параметров источника после инициализации"""

        if type(self.count) is not int:
            logger.error("В источник %s подан нецелый параметр count: %s", self.name, self.count)
            raise TypeError("count должен быть целым числом")
        if self.count < 0:
            logger.error("В источник %s подан отрицательный параметр count: %s", self.name, self.count)
            raise ValueError("count не может быть отрицательным")

    def get_tasks(self) -> Iterable[Task]:
        """
        Последовательно генерирует задачи и возвращает их как поток объектов Task
        :return: итерируемый объект с валидными задачами
        """
        logger.info(
            "Источник %s начал генерацию %s задач", self.name, self.count
        )

        created_count = 0
        skipped_count = 0

        for index in range(1, self.count + 1):
            task_data: dict[str, Any] = {
                "id": str(uuid.uuid4()),
                "description": f"Generated task #{index}",
                "priority": (index % 5) + 1,
                "status": TaskStatus.CREATED,
            }

            try:
                task = Task.from_dict(task_data)
                created_count += 1
            except Exception as exc:
                skipped_count += 1
                logger.warning(
                    "Не удалось создать задачу %s: %s", index, exc
                )
                continue

            logger.debug(
                "Источник %s создал задачу: id=%s",
                self.name,
                task.id
            )
            yield task

        logger.info(
            "Источник %s завершил генерацию: создано=%s, пропущено=%s",
            self.name,
            created_count,
            skipped_count,
        )

@register_source("generated")  # type: ignore[arg-type]
def create_generated_source(count: int) -> GeneratedSource:
    """
    Создаёт зарегистрированный источник программно сгенерированных задач
    :param count: количество задач для генерации
    :return: объект GeneratedSource
    """
    logger.debug(
        "Создание GeneratedSource через фабрику: count=%s",
        count,
    )
    return GeneratedSource(count=count)
