from __future__ import annotations

import asyncio
import argparse
import logging
from pathlib import Path

from src.app.config import setup_logging
from src.app.core import InboxApp
from src.sources.api_source import create_api_source
from src.sources.generation import create_generated_source
from src.sources.json import create_json_source

from src.task_model.task_queue import TaskQueue
from src.async_executor.async_queue import AsyncioTaskQueue
from src.async_executor.executor import AsyncTaskExecutor
from src.handlers.handler import FileTaskHandler

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Создаёт CLI-парсер приложения."""
    parser = argparse.ArgumentParser(description="Демонстрация платформы обработки задач")
    parser.add_argument("--api", action="store_true", help="читать задачи из API-заглушки")
    parser.add_argument("--generated", type=int, default=0, help="сгенерировать N задач")
    parser.add_argument("--file", type=Path, help="прочитать задачи из JSONL-файла")
    parser.add_argument(
        "--async-run",
        action="store_true",
        help="обработать задачи асинхронным исполнителем",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="количество асинхронных воркеров",
    )
    return parser


def main() -> None:
    """Точка входа приложения."""
    setup_logging()
    args = build_parser().parse_args()

    sources = []
    if args.api:
        sources.append(create_api_source())
    if args.generated:
        sources.append(create_generated_source(args.generated))
    if args.file:
        sources.append(create_json_source(args.file))

    if not sources:
        logger.info("Источники не выбраны. Используйте --api, --generated N или --file PATH")
        build_parser().print_help()
        return

    app = InboxApp(sources)

    if args.async_run:
        task_queue = TaskQueue(sources)
        async_queue = AsyncioTaskQueue(task_queue)
        handler = FileTaskHandler()

        async def run_async() -> None:
            async with AsyncTaskExecutor(async_queue, handler, workers_count=args.workers) as executor:
                await executor.run()

        asyncio.run(run_async())
        return

    for task in app.iter_tasks():
        print(task)


if __name__ == "__main__":
    main()
