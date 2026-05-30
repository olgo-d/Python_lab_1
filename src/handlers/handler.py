from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import cast

from src.task_model.descriptors import TaskStatus
from src.task_model.task import Task

logger = logging.getLogger(__name__)


class FileTaskHandler:
    """Обработчик задач, записывающий обработанные задачи в файл."""

    name = "file-task-handler"

    def __init__(self, file_path: str = "processed_tasks.jsonl") -> None:
        self._file_path = Path(file_path)
        self._lock = asyncio.Lock()

    async def handle(self, task: Task) -> None:
        """Обрабатывает задачу и записывает результат в файл."""
        logger.info("Начата обработка задачи: %s", task.id)

        task.status = TaskStatus.PROCESSING

        # имитация обработки задачи
        await asyncio.sleep(0)

        task.status = TaskStatus.COMPLETED

        async with self._lock:
            await asyncio.to_thread(self._write_task_to_file, task)

        logger.info("Задача обработана и записана в файл: %s", task.id)

    def _write_task_to_file(self, task: Task) -> None:
        """
        Синхронная запись задачи в файл
        запускается через asyncio.to_thread, чтобы не блокировать event loop
        """
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        status = cast(TaskStatus, task.status)
        created_at = cast(datetime, task.created_at)

        task_data = {
            "id": task.id,
            "description": task.description,
            "priority": task.priority,
            "status": status.value,
            "created_at": created_at.isoformat(),
        }

        with self._file_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(task_data, ensure_ascii=False) + "\n")
