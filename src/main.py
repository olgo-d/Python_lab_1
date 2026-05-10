from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.app.config import setup_logging
from src.app.core import InboxApp
from src.sources.api_source import create_api_source
from src.sources.generation import create_generated_source
from src.sources.json import create_json_source

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Создаёт CLI-парсер приложения."""
    parser = argparse.ArgumentParser(description="Демонстрация платформы обработки задач")
    parser.add_argument("--api", action="store_true", help="читать задачи из API-заглушки")
    parser.add_argument("--generated", type=int, default=0, help="сгенерировать N задач")
    parser.add_argument("--file", type=Path, help="прочитать задачи из JSONL-файла")
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
    for task in app.iter_tasks():
        print(task)


if __name__ == "__main__":
    main()
