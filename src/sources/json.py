import json
import uuid
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.task_model.task import Task
from src.task_model.error_tasks import TaskError
from src.sources.register_sources import register_source

logger = logging.getLogger(__name__)

def parse_json_line(line: str, path: str | Path, line_no: int) -> dict[str, Any]:
    """
    Преобразует одну строку JSONL-файла в словарь

    :param line: строка из JSONL-файла
    :param path: путь к файлу, из которого прочитана строка
    :param line_no: номер строки в файле
    :return: словарь с данными задачи
    """
    try:
        data = json.loads(line)
    except json.JSONDecodeError as error:
        logger.error(
            "Некорректный JSON в файле %s на строке %s: %s",
            path,
            line_no,
            error,
        )
        raise ValueError(f"Некорректный JSON в файле {path}:{line_no}: {error}") from error

    if not isinstance(data, dict):
        logger.error(
            "JSON-значение в файле %s на строке %s должно быть словарём, получено: %s",
            path,
            line_no,
            type(data).__name__,
        )
        raise ValueError(f"JSON-значение в файле {path}:{line_no} должно быть словарём")

    logger.info(
        "Строка %s из файла %s успешно преобразована в словарь",
        line_no,
        path,
    )

    return data

@dataclass(frozen=True)
class JsonlSource:
    """
    Источник задач, читающий данные из JSONL-файла
    :param path: путь к JSONL-файлу
    :param name: имя источника для логирования
    """
    path: Path
    name: str = "file-jsonl"

    def __post_init__(self) -> None:
        """Проверяет корректность параметров источника"""
        if not isinstance(self.path, Path):
            logger.error("Некорректный путь: %s", self.path)
            raise TypeError("path должен быть объектом pathlib.Path")


    def get_tasks(self) -> Iterable[Task]:
        """
        Читает JSONL-файл и последовательно возвращает задачи
        :return: итерируемый объект с валидными задачами
        """
        logger.info(
            "Источник %s начал чтение задач из файла: %s",
            self.name,
            self.path,
        )

        created_count = 0
        skipped_count = 0

        try:
            file = self.path.open("r", encoding="utf-8")
        except OSError as error:
            logger.error(
                "Источник %s не смог открыть файл %s",
                self.name,
                self.path,
            )
            raise ValueError(f"Не удалось открыть файл {self.path}") from error

        with file:
            for line_no, line in enumerate(file, start=1):
                stripped_line = line.strip()

                if not stripped_line:
                    logger.debug(
                        "Источник %s пропустил пустую строку в файле %s",
                        self.name,
                        self.path,
                    )
                    continue

                try:
                    task_data = parse_json_line(stripped_line, self.path, line_no)

                    if not task_data.get("id"):
                        generated_id = str(uuid.uuid4())
                        task_data["id"] = generated_id

                        logger.info(
                            "Для строки %s файла %s сгенерирован id: %s",
                            line_no,
                            self.path,
                            generated_id,
                        )

                    task = Task.from_dict(task_data)

                except (ValueError, TaskError) as exc:
                    skipped_count += 1
                    logger.warning(
                        "Источник %s пропустил строку %s файла %s: %s",
                        self.name,
                        line_no,
                        self.path,
                        exc,
                    )
                    continue

                created_count += 1

                logger.debug(
                    "Источник %s создал задачу из строки %s файла %s: id=%s",
                    self.name,
                    line_no,
                    self.path,
                    task.id,
                )

                yield task

        logger.info(
            "Источник %s завершил чтение файла %s. Создано: %s, пропущено: %s",
            self.name,
            self.path,
            created_count,
            skipped_count,
        )

@register_source("file-jsonl")  # type: ignore[arg-type]
def create_json_source(path: Path) -> JsonlSource:
    """
    Создаёт зарегистрированный источник задач из JSONL-файла
    :param path: путь к JSONL-файлу
    :return: объект JsonlSource
    """
    logger.debug(
        "Создание JsonlSource через фабрику: path=%s",
        path,
    )
    return JsonlSource(path=path)
