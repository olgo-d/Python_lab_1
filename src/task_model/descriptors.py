from enum import Enum
from datetime import datetime

from .error_tasks import (
    TaskDescriptionError,
    TaskPriorityError,
    TaskStatusError,
)

import logging
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Допустимые состояния задачи."""

    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"

class NotEmptyString:
    """Data descriptor для проверки непустой строки."""

    def __init__(self, storage_name: str) -> None:
        self.storage_name = storage_name

    def __get__(self, instance: object, owner: type | None = None) -> str | "NotEmptyString":
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            logger.warning(
                "Ошибка валидации строки для поля %s: value=%r",
                self.storage_name,
                value,
            )
            raise TaskDescriptionError("Описание задачи должно быть непустой строкой")

        object.__setattr__(instance, self.storage_name, value.strip())

        logger.debug(
            "Поле %s успешно установлено",
            self.storage_name,
        )


class Priority:
    """Data descriptor для проверки приоритета."""

    def __init__(self, storage_name: str) -> None:
        self.storage_name = storage_name

    def __get__(self, instance: object, owner: type | None = None) -> int | "Priority":
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: object) -> None:
        if type(value) is not int:
            logger.warning(
                "Ошибка валидации приоритета для поля %s: value=%r, type=%s",
                self.storage_name,
                value,
                type(value).__name__,
            )
            raise TaskPriorityError("Приоритет должен быть целым числом")

        if not 1 <= value <= 5:
            logger.warning(
                "Приоритет вне допустимого диапазона для поля %s: value=%s",
                self.storage_name,
                value,
            )

            raise TaskPriorityError("Приоритет должен быть в диапазоне от 1 до 5")

        object.__setattr__(instance, self.storage_name, value)

        logger.debug(
            "Поле %s успешно установлено: value=%s",
            self.storage_name,
            value,
        )


class CreatedAt:
    """Non-data descriptor: только чтение времени создания."""

    def __init__(self, storage_name: str) -> None:
        self.storage_name = storage_name

    def __get__(self, instance: object, owner: type | None = None) -> datetime | "CreatedAt":
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

class Status:
    """Data descriptor для проверки статуса задачи."""

    def __init__(self, storage_name: str) -> None:
        self.storage_name = storage_name

    def __get__(self, instance: object, owner: type | None = None) -> TaskStatus | "Status":
        if instance is None:
            return self

        return getattr(instance, self.storage_name)

    def __set__(self, instance: object, value: TaskStatus | str) -> None:
        if isinstance(value, TaskStatus):
            status = value
        elif isinstance(value, str):
            try:
                status = TaskStatus(value.lower())
            except ValueError as exc:
                logger.warning(
                    "Недопустимый статус для поля %s: value=%r",
                    self.storage_name,
                    value,
                )
                raise TaskStatusError(f"Недопустимый статус задачи: {value}") from exc
        else:
            logger.warning(
                "Некорректный тип статуса для поля %s: value=%r, type=%s",
                self.storage_name,
                value,
                type(value).__name__,
            )
            raise TaskStatusError("status должен быть TaskStatus или строкой")

        object.__setattr__(instance, self.storage_name, status)

        logger.debug(
            "Поле %s успешно установлено: status=%s",
            self.storage_name,
            status.value,
        )
