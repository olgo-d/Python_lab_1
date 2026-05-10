class TaskError(ValueError):
    """Базовая ошибка, связанная с некорректным состоянием задачи."""


class TaskIdError(TaskError):
    """Ошибка идентификатора задачи."""


class TaskDescriptionError(TaskError):
    """Ошибка описания задачи."""


class TaskPriorityError(TaskError):
    """Ошибка приоритета задачи."""


class TaskStatusError(TaskError):
    """Ошибка статуса задачи."""
