from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import AsyncIterator

from src.task_model.task import Task


class AsyncioTaskQueue:
    """Асинхронная очередь задач"""

    def __init__(self, tasks: Iterable[Task]) -> None:
        self._tasks = tasks
        self._queue: asyncio.Queue[Task | None] = asyncio.Queue()
        self._loaded = False

    async def load(self, workers_count: int = 2) -> None:
        """Загружает задачи в асинхронную очередь"""

        if self._loaded:
            return

        for task in self._tasks:
            await self._queue.put(task)

        for _ in range(workers_count):
            await self._queue.put(None)

        self._loaded = True

    async def get(self) -> Task | None:
        """Возвращает следующую задачу из очереди"""
        return await self._queue.get()

    def task_done(self) -> None:
        """Сообщает, что все задачи из очереди выполнены"""
        self._queue.task_done()

    async def join(self) -> None:
        """Ожидает завершения всех задач из очереди"""
        await self._queue.join()

    async def __aiter__(self) -> AsyncIterator[Task]:
        while True:
            task = await self.get()

            if task is None:
                self.task_done()
                break
            try:
                yield task
            finally:
                self.task_done()
