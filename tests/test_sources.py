import json
from pathlib import Path

import pytest

from src.sources.api_source import ApiClient, ApiSource, create_api_source, fake_api_response
from src.sources.generation import GeneratedSource, create_generated_source
from src.sources.json import JsonlSource, create_json_source, parse_json_line
from src.task_model.descriptors import TaskStatus


def test_fake_api_response_and_client_return_valid_items() -> None:
    client = ApiClient(request=fake_api_response)
    items = client.get_tasks()

    assert len(items) == 3
    assert items[0]["description"] == "Сделать лабораторную"


@pytest.mark.parametrize(
    ("raw_response", "expected_error_text"),
    [
        ("bad-json", "Bad API JSON"),
        (json.dumps({"id": "1"}), "Ответ API должен представлять собой list"),
        (json.dumps(["not-dict"]), "должен быть словарем"),
    ],
)
def test_api_client_rejects_invalid_response(raw_response: str, expected_error_text: str) -> None:
    client = ApiClient(request=lambda: raw_response)

    with pytest.raises(ValueError, match=expected_error_text):
        client.get_tasks()


def test_api_source_creates_tasks_generates_missing_id_and_skips_bad_items() -> None:
    payload = [
        {"id": "1", "description": "ok", "priority": 2},
        {"description": "without id"},
        {"id": "bad", "description": "bad", "priority": 99},
    ]
    source = ApiSource(client=ApiClient(request=lambda: json.dumps(payload)))

    tasks = list(source.get_tasks())

    assert len(tasks) == 2
    assert tasks[0].id == "1"
    assert tasks[1].id != ""
    assert tasks[1].description == "without id"


def test_create_api_source_factory() -> None:
    source = create_api_source()

    assert isinstance(source, ApiSource)
    assert source.name == "api-stub"


@pytest.mark.parametrize(
    ("count", "expected_error"),
    [
        (True, TypeError),
        (-1, ValueError),
    ],
)
def test_generated_source_validates_count(count: object, expected_error: type[Exception]) -> None:
    with pytest.raises(expected_error):
        GeneratedSource(count=count)  # type: ignore[arg-type]


def test_generated_source_yields_expected_tasks_and_priorities() -> None:
    tasks = list(GeneratedSource(count=6).get_tasks())

    assert len(tasks) == 6
    assert [task.priority for task in tasks] == [2, 3, 4, 5, 1, 2]
    assert all(task.status == TaskStatus.CREATED for task in tasks)
    assert tasks[0].description == "Generated task №1"


def test_create_generated_source_factory() -> None:
    source = create_generated_source(2)

    assert isinstance(source, GeneratedSource)
    assert source.count == 2


def test_parse_json_line_validates_json_and_object_type() -> None:
    assert parse_json_line('{"id": "1"}', "tasks.jsonl", 1) == {"id": "1"}

    with pytest.raises(ValueError, match="Некорректный JSON"):
        parse_json_line("bad", "tasks.jsonl", 2)

    with pytest.raises(ValueError, match="должно быть словарём"):
        parse_json_line("[1, 2]", "tasks.jsonl", 3)


def test_jsonl_source_rejects_non_path_argument() -> None:
    with pytest.raises(TypeError):
        JsonlSource(path="tasks.jsonl")  # type: ignore[arg-type]


def test_jsonl_source_reports_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.jsonl"

    with pytest.raises(ValueError, match="Не удалось открыть файл"):
        list(JsonlSource(path=missing_path).get_tasks())


def test_jsonl_source_reads_valid_lines_and_skips_invalid_lines(tmp_path: Path) -> None:
    path = tmp_path / "tasks.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"id": "1", "description": "first", "priority": 1, "status": "created"}',
                "",
                "bad-json",
                "[1, 2]",
                '{"id": "2", "description": "bad priority", "priority": 10}',
                '{"description": "generated id", "priority": 3, "status": "COMPLETED"}',
            ]
        ),
        encoding="utf-8",
    )

    tasks = list(JsonlSource(path=path).get_tasks())

    assert len(tasks) == 2
    assert tasks[0].id == "1"
    assert tasks[0].description == "first"
    assert tasks[1].id != ""
    assert tasks[1].status == TaskStatus.COMPLETED


def test_create_json_source_factory() -> None:
    path = Path("tasks.jsonl")
    source = create_json_source(path)

    assert isinstance(source, JsonlSource)
    assert source.path == path
