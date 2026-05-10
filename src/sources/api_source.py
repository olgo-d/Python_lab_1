import json
import logging
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Callable

from src.task_model.task import Task
from src.sources.register_sources import register_source

logger = logging.getLogger(__name__)

def fake_api_response() -> str:
    """Имитирует ответ внешнего API в формате JSON"""

    logger.info("API-заглушка возвращает JSON-ответ")

    return json.dumps(
        [
            {"id": "1", "description": "Сделать лабораторную"},
            {"id": "2", "description": "Написать тесты"},
            {"description": "Задача без id"},
        ]
    )


@dataclass(frozen=True)
class ApiClient:
    """
    Клиент для получения данных из API

    :param request: функция, возвращающая JSON-строку
    """
    request: Callable[[], str]

    def get_tasks(self) -> list[dict[str, Any]]:
        """
        Получает и проверяет данные API

        :return: список словарей для создания задач
        """

        raw_data = self.request()

        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as error:
            logger.error("Bad API JSON: %s", error)
            raise ValueError(f"Bad API JSON: {error}") from error

        if not isinstance(data, list):
            logger.error("Ответ API должен представлять собой list")
            raise ValueError("Ответ API должен представлять собой list")

        validated_items: list[dict[str, Any]] = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                logger.error("API item #%s должен быть словарем", index)
                raise ValueError(f"API item #{index} должен быть словарем")
            validated_items.append(item)

        logger.info("JSON-данные API успешно обработаны: %s элементов", len(validated_items))
        return validated_items


@dataclass(frozen=True)
class ApiSource:
    """
    Источник задач, получающий данные из API-клиента.

    :param client: Клиент для получения данных из API
    :param name: название источника задач
    """

    client: ApiClient
    name: str = "api-stub"

    def get_tasks(self) -> Iterable[Task]:
        """
        Возвращает поток задач, созданных из данных API
        :return: итерируемый объект с валидными задачами
        """
        logger.info(
            "Источник %s начал получение задач из API",
            self.name,
        )

        created_count = 0
        skipped_count = 0
        tasks = self.client.get_tasks()

        for index, item in enumerate(tasks, start=1):
            try:
                task = self._create_task_from_item(item)
            except (TypeError, ValueError) as ex:
                skipped_count += 1
                logger.warning(
                    "Элемент API #%s пропущен: %s. Данные: %s",
                    index,
                    ex,
                    item,
                )
                continue

            created_count += 1
            yield task

        logger.info(
            "Источник %s завершил получение задач: создано=%s, пропущено=%s",
            self.name,
            created_count,
            skipped_count,
        )

    def _create_task_from_item(self, item: dict[str, Any]) -> Task:
        """
        Создаёт Task из одного элемента API-ответа
        :param item: словарь с данными одной задачи из API
        :return: валидный объект Task
        """

        task_data = dict(item)

        if not task_data.get("id"):
            generated_id = str(uuid.uuid4())
            task_data["id"] = generated_id
            logger.info(
                "Для API-элемента без id сгенерирован id: %s",
                generated_id,
            )

        task = Task.from_dict(task_data)

        logger.debug(
            "Задача из API-элемента успешно создана: id=%s",
            task.id,
        )

        return task


@register_source("api-stub")  # type: ignore[arg-type]
def create_api_source() -> ApiSource:
    """
    Создаёт зарегистрированный API-источник на основе API-заглушки.
    :return: объект ApiSource.
    """
    logger.debug("Создание ApiSource через фабрику")
    client = ApiClient(request=fake_api_response)
    return ApiSource(client=client)
