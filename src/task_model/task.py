from __future__ import annotations

from datetime import datetime
from typing import Any, Self
import logging

from .descriptors import (
    NotEmptyString,
    Priority,
    CreatedAt,
    TaskStatus,
    Status,
)
from .error_tasks import (
    TaskError,
    TaskIdError,
    TaskPriorityError,
    TaskStatusError,
)

logger = logging.getLogger(__name__)

class Task:
    """
    Модель задачи с валидацией состояния

    :param id: строковый идентификатор задачи
    :param description: описание задачи
    :param priority: приоритет от 1 до 5
    :param status: текущее состояние задачи
    """
    __slots__ = (
        "id",
        "_description",
        "_priority",
        "_status",
        "_created_at",
    )

    id: str
    _description: str
    _priority: int
    _status: TaskStatus
    _created_at: datetime

    description = NotEmptyString("_description")
    priority = Priority("_priority")
    status = Status("_status")
    created_at = CreatedAt("_created_at")

    def __init__(
        self,
        id: str,
        description: str,
        priority: int = 1,
        status: TaskStatus | str = TaskStatus.CREATED,
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            logger.error("Ошибка создания Task: некорректный id=%r", id)
            raise TaskIdError("id задачи должен быть непустой строкой")


        self.id = id.strip()
        self._created_at = datetime.now()
        self.status = status
        self.description = description
        self.priority = priority

        logger.info(
            "Task успешно создана: id=%s, priority=%s, status=%s",
            self.id,
            self.priority,
            self.status,
        )

    @property
    def is_ready(self) -> bool:
        """Готова ли задача к обработке."""
        return self.status == TaskStatus.CREATED

    @property
    def is_finished(self) -> bool:
        """Завершена ли задача."""
        return self.status == TaskStatus.COMPLETED

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """
        Создаёт задачу из словаря без изменения исходных данных
        :param data: словарь с ключами id, description, priority, status
        :return: валидный объект Task
        """
        logger.debug("Создание Task из словаря: %s", data)

        raw = dict(data)

        try:
            task_id = raw["id"]
            description = raw["description"]
        except KeyError as exc:
            logger.warning(
                "Ошибка создания Task из словаря: отсутствует поле %r. Данные: %s",
                exc.args[0],
                raw,
            )
            raise TaskError(f"Не хватает обязательного поля: {exc.args[0]}") from exc

        try:
            priority = int(raw.get("priority", 1))
        except (TypeError, ValueError) as error:
            logger.warning(
                "Ошибка создания Task из словаря: некорректный priority=%r. Данные: %s",
                raw.get("priority"),
                raw,
            )
            raise TaskPriorityError("priority должен быть числом") from error

        try:
            status = raw.get("status", TaskStatus.CREATED)
            if isinstance(status, str):
                status = TaskStatus(status.lower())
        except ValueError as error:
            logger.warning(
                "Ошибка создания Task из словаря: некорректный status=%r. Данные: %s",
                raw.get("status"),
                raw,
            )
            raise TaskStatusError(f"Недопустимый статус задачи: {raw.get('status')}") from error

        task = cls(
            id=task_id,
            description=description,
            priority=priority,
            status=status,
        )
        logger.info("Task из словаря успешно создана: id=%s", task.id)
        return task

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, "
            f"description={self.description!r}, "
            f"priority={self.priority!r}, "
            f"status={self.status!r})"
        )
