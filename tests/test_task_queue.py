from collections.abc import Iterable
from dataclasses import dataclass

import pytest

from src.task_model.descriptors import TaskStatus
from src.task_model.error_tasks import TaskPriorityError, TaskStatusError
from src.task_model.task import Task
from src.task_model.task_queue import TaskQueue


@dataclass
class TaskSourceExample:
    tasks: list[Task]
    name: str = "memory"

    def get_tasks(self) -> Iterable[Task]:
        yield from self.tasks


class InvalidSource:
    pass


def seed_tasks() -> list[Task]:
    return [
        Task(
            id="1",
            description="created",
            priority=1,
            status=TaskStatus.CREATED,
        ),
        Task(
            id="2",
            description="processing",
            priority=3,
            status=TaskStatus.PROCESSING,
        ),
        Task(
            id="3",
            description="completed",
            priority=5,
            status=TaskStatus.COMPLETED,
        ),
    ]


def test_queue_iterate_tasks_from_sources() -> None:
    source_1 = TaskSourceExample(seed_tasks()[:2])
    source_2 = TaskSourceExample(seed_tasks()[2:])

    queue = TaskQueue([source_1, source_2])

    assert [task.id for task in queue] == ["1", "2", "3"]


def test_queue_repeated_iteration() -> None:
    queue = TaskQueue([TaskSourceExample(seed_tasks())])

    first_pass = [task.id for task in queue]
    second_pass = [task.id for task in queue]

    assert first_pass == ["1", "2", "3"]
    assert second_pass == ["1", "2", "3"]


def test_filter_by_statuses() -> None:
    queue = TaskQueue([TaskSourceExample(seed_tasks())])

    result = queue.filter_by_statuses([TaskStatus.CREATED, "completed"])

    assert [task.id for task in result] == ["1", "3"]


def test_filter_by_statuses_invalid_status() -> None:
    queue = TaskQueue([TaskSourceExample(seed_tasks())])

    with pytest.raises(TaskStatusError):
        list(queue.filter_by_statuses(["unknown"]))


def test_filter_by_priority() -> None:
    queue = TaskQueue([TaskSourceExample(seed_tasks())])

    result = queue.filter_by_priority(min_priority=2, max_priority=4)

    assert [task.id for task in result] == ["2"]


def test_filter_by_priority_invalid_range() -> None:
    queue = TaskQueue([TaskSourceExample(seed_tasks())])

    with pytest.raises(TaskPriorityError):
        list(queue.filter_by_priority(min_priority=5, max_priority=1))


def test_queue_rejects_invalid_source() -> None:
    queue = TaskQueue([InvalidSource()])  # type: ignore[list-item]

    with pytest.raises(TypeError):
        list(queue)