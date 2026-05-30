import pytest
import asyncio

from src.async_executor.async_queue import AsyncioTaskQueue
from src.async_executor.executor import AsyncTaskExecutor
from src.handlers.handler import FileTaskHandler
from src.task_model.descriptors import TaskStatus
from src.task_model.task import Task


@pytest.mark.asyncio
async def test_handler_completes_task() -> None:
    task = Task(id="1", description="async task")
    handler = FileTaskHandler()

    await handler.handle(task)

    assert task.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_executor_processes_tasks() -> None:
    tasks = [
        Task(id="1", description="first"),
        Task(id="2", description="second"),
    ]

    queue = AsyncioTaskQueue(tasks)
    handler = FileTaskHandler()

    async with AsyncTaskExecutor(queue, handler) as executor:
        await executor.run()

    assert all(task.status == TaskStatus.COMPLETED for task in tasks)

class SlowCountingHandler:
    """Тестовый обработчик, проверяющий конкурентную работу воркеров."""

    name = "slow-counting-handler"

    def __init__(self) -> None:
        self.active_count = 0
        self.max_active_count = 0
        self._lock = asyncio.Lock()

    async def handle(self, task: Task) -> None:
        async with self._lock:
            self.active_count += 1
            self.max_active_count = max(
                self.max_active_count,
                self.active_count,
            )

        await asyncio.sleep(0.05)

        task.status = TaskStatus.COMPLETED

        async with self._lock:
            self.active_count -= 1


@pytest.mark.asyncio
async def test_executor_uses_two_workers_concurrently() -> None:
    tasks = [
        Task(id="1", description="first"),
        Task(id="2", description="second"),
        Task(id="3", description="third"),
        Task(id="4", description="fourth"),
    ]

    queue = AsyncioTaskQueue(tasks)
    handler = SlowCountingHandler()

    async with AsyncTaskExecutor(
        queue,
        handler,
        workers_count=2,
    ) as executor:
        await executor.run()

    assert all(task.status == TaskStatus.COMPLETED for task in tasks)
    assert handler.max_active_count == 2
