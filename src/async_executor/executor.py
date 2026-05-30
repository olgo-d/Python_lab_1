from __future__ import annotations

import asyncio
import logging

from src.async_executor.async_queue import AsyncioTaskQueue
from src.contracts.task_handler import TaskHandler

logger = logging.getLogger(__name__)


class AsyncTaskExecutor:
    """Асинхронный исполнитель задач с несколькими воркерами"""

    def __init__(self, queue: AsyncioTaskQueue, handler: TaskHandler, workers_count: int = 2) -> None:
        if not isinstance(handler, TaskHandler):
            raise TypeError(
                f"{type(handler).__name__} не соответствует контракту TaskHandler"
            )

        if workers_count < 1:
            raise ValueError("Количество воркеров (workers_count) должно быть не меньше 1")

        self._queue = queue
        self._handler = handler
        self._is_running = False
        self._workers_count = workers_count

    async def __aenter__(self) -> "AsyncTaskExecutor":
        logger.info("Асинхронный исполнитель запущен")
        self._is_running = True
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        self._is_running = False

        if exc is not None:
            logger.error("Исполнитель завершился с ошибкой: %s", exc)

        logger.info("Асинхронный исполнитель остановлен")

    async def run(self) -> None:
        """Запускает обработку задач"""

        await self._queue.load(workers_count=self._workers_count)

        workers = [
            asyncio.create_task(self._worker(worker_id))
            for worker_id in range(1, self._workers_count + 1)
        ]

        await self._queue.join()
        await asyncio.gather(*workers)

    async def _worker(self, worker_id: int) -> None:
        """Рабочая корутина, забирающая задачи из очереди"""
        logger.info("Воркер %s запущен", worker_id)

        while True:
             task = await self._queue.get()

             if task is None:
                 self._queue.task_done()
                 logger.info("Воркер %s остановлен", worker_id)
                 break

             try:
                 logger.info(
                     "Воркер %s начал обработку задачи %s",
                     worker_id,
                     task.id,
                 )

                 await self._handler.handle(task)

                 logger.info(
                     "Воркер %s завершил обработку задачи %s",
                     worker_id,
                     task.id,
                 )

             except Exception as exc:
                 logger.exception(
                     "Воркер %s получил ошибку при обработке задачи %s: %s",
                     worker_id,
                     task.id,
                     exc,
                 )

             finally:
                 self._queue.task_done()
