from collections.abc import Iterable
from dataclasses import dataclass

import pytest

from src.app.core import InboxApp
from src.sources.register_sources import REGISTRY, register_source
from src.task_model.task import Task


@dataclass
class GoodSource:
    name: str = "good"

    def get_tasks(self) -> Iterable[Task]:
        yield Task(id="1", description="from source")


@dataclass
class BrokenSource:
    name: str = "broken"

    def get_tasks(self) -> Iterable[Task]:
        raise RuntimeError("source failed")
        yield  # pragma: no cover


class NotSource:
    pass


def test_inbox_app_iterates_all_valid_sources_and_skips_broken_source() -> None:
    app = InboxApp([GoodSource(), BrokenSource(), GoodSource(name="second")])

    tasks = list(app.iter_tasks())

    assert [task.description for task in tasks] == ["from source", "from source"]


def test_inbox_app_rejects_object_without_protocol() -> None:
    app = InboxApp([NotSource()])  # type: ignore[list-item]

    with pytest.raises(TypeError, match="не соответствует TaskSource"):
        list(app.iter_tasks())


def test_empty_app_yields_no_tasks() -> None:
    assert list(InboxApp().iter_tasks()) == []


def test_register_source_saves_factory_and_rejects_duplicate_name() -> None:
    name = "unit-test-source"
    REGISTRY.pop(name, None)

    @register_source(name)
    def factory() -> GoodSource:
        return GoodSource()

    assert REGISTRY[name] is factory

    with pytest.raises(ValueError, match="уже зарегистрирован"):
        register_source(name)(factory)
