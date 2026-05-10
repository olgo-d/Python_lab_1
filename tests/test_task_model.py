from datetime import datetime

import pytest

from src.task_model.task import Task
from src.task_model.descriptors import TaskStatus
from src.task_model.error_tasks import (
    TaskDescriptionError,
    TaskError,
    TaskIdError,
    TaskPriorityError,
    TaskStatusError,
)


def test_task_created_with_trimmed_fields_and_defaults() -> None:
    task = Task(id="  task-1  ", description="  Сделать тесты  ")

    assert task.id == "task-1"
    assert task.description == "Сделать тесты"
    assert task.priority == 1
    assert task.status == TaskStatus.CREATED
    assert task.is_ready is True
    assert task.is_finished is False
    assert isinstance(task.created_at, datetime)
    assert "Task(id='task-1'" in repr(task)


def test_status_can_be_passed_as_string_case_insensitive() -> None:
    task = Task(id="task-2", description="done", status="COMPLETED")

    assert task.status == TaskStatus.COMPLETED
    assert task.is_ready is False
    assert task.is_finished is True


@pytest.mark.parametrize(
    ("kwargs", "expected_error"),
    [
        ({"id": " ", "description": "valid"}, TaskIdError),
        ({"id": "1", "description": ""}, TaskDescriptionError),
        ({"id": "1", "description": "valid", "priority": 0}, TaskPriorityError),
        ({"id": "1", "description": "valid", "priority": True}, TaskPriorityError),
        ({"id": "1", "description": "valid", "status": "unknown"}, TaskStatusError),
        ({"id": "1", "description": "valid", "status": 123}, TaskStatusError),
    ],
)
def test_invalid_task_fields_raise_domain_errors(kwargs: dict[str, object], expected_error: type[Exception]) -> None:
    with pytest.raises(expected_error):
        Task(**kwargs)  # type: ignore[arg-type]


def test_from_dict_creates_task_without_mutating_source_dict() -> None:
    data = {
        "id": "1",
        "description": "Из словаря",
        "priority": "4",
        "status": "processing",
    }

    task = Task.from_dict(data)

    assert task.id == "1"
    assert task.description == "Из словаря"
    assert task.priority == 4
    assert task.status == TaskStatus.PROCESSING
    assert data["priority"] == "4"


@pytest.mark.parametrize(
    ("data", "expected_error"),
    [
        ({"id": "1"}, TaskError),
        ({"id": "1", "description": "x", "priority": "bad"}, TaskPriorityError),
        ({"id": "1", "description": "x", "status": "bad"}, TaskStatusError),
        ({"id": None, "description": "x"}, TaskIdError),
        ({"id": "1", "description": None}, TaskDescriptionError),
    ],
)
def test_from_dict_reports_missing_and_invalid_fields(data: dict[str, object], expected_error: type[Exception]) -> None:
    with pytest.raises(expected_error):
        Task.from_dict(data)


def test_descriptor_access_from_class_returns_descriptor() -> None:
    assert Task.description is not None
    assert Task.priority is not None
    assert Task.status is not None
    assert Task.created_at is not None
