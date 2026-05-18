# Проект по питону (лабораторная работа 1 и 2)

## Требования

- Python **3.10+**.

Зависимости:

```bash
python -m pip install -r requirements.txt
```

## Структура проекта

```text
Python_lab
├── source
│   └── messages.jsonl
├── src
│   ├── app
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── core.py
│   ├── contracts
│   │   ├── __init__.py
│   │   └── task_source.py
│   ├── sources
│   │   ├── __init__.py
│   │   ├── api_source.py
│   │   ├── generation.py
│   │   ├── json.py
│   │   └── register_sources.py
│   ├── task_model
│   │   ├── __init__.py
│   │   ├── descriptors.py
│   │   ├── error_tasks.py
│   │   └── task.py
│   ├── __init__.py
│   └── main.py
├── tests
│   ├── __init__.py
│   ├── test_core_and_registry.py
│   ├── test_sources.py
│   └── test_task_model.py
├── .coveragerc
├── .gitignore
├── .pre-commit-config.yaml
├── app.log
├── README.md
└── requirements.txt
```
## Описание модулей

- **`source/`** - директория с исходными файлами данных (например, `messages.jsonl`).
- **`src/`** - основной исходный код проекта:
  - `app/config.py` - настройка логирования.
  - `app/core.py` - централизованный сбор задач из всех подключенных источников.
  - `contracts/task_source.py` - контракт источника задач.
  - `sources/` - реализации конкретных источников данных (API, генерация, JSON) и их регистрация.
  - `task_model/` - модели данных для задач, дескрипторы и логика работы с ошибками.
  - `main.py` - главная точка входа в приложение.
- **`tests/`** - модульные тесты для проверки ядра, моделей и источников (используется `pytest`).

### Системные файлы в корне проекта:
- `.coveragerc` — настройки и отчеты покрытия кода тестами.
- `app.log` — лог-файл работы приложения.
- `requirements.txt` — список зависимостей проекта.
---

### Лабораторная работа №1: источники задач и контракты

Кратко: сделана подсистема приёма задач из разных источников через единый поведенческий контракт.

Реализовано:

- контракт источника задач `TaskSource` через `typing.Protocol` и `@runtime_checkable`;
- единый метод контракта `get_tasks()`, который возвращает поток объектов `Task`;
- runtime-проверка источников через `isinstance(source, TaskSource)` в `InboxApp`;
- несколько независимых источников без общего базового класса:
  - `JsonlSource` — чтение задач из JSONL-файла;
  - `GeneratedSource` — программная генерация задач;
  - `ApiSource` — получение задач из API-заглушки;
- реестр фабрик источников `REGISTRY` и декоратор `register_source`, чтобы можно было добавлять новые источники без изменения ядра приложения;
- обработка ошибок источников: некорректные элементы пропускаются, ошибки логируются.

### Лабораторная работа №2: модель задачи, дескрипторы и `@property`

Кратко: реализована безопасная модель задачи `Task` с валидацией атрибутов и защитой некорректных состояний.

Реализовано:

- класс `Task` с полями:
  - `id` — идентификатор задачи;
  - `description` — описание;
  - `priority` — приоритет от 1 до 5;
  - `status` — статус задачи;
  - `created_at` — время создания;
- пользовательские дескрипторы для валидации:
  - `NotEmptyString` — проверяет непустое описание;
  - `Priority` — проверяет диапазон приоритета;
  - `Status` — проверяет допустимые статусы;
  - `CreatedAt` — non-data descriptor для чтения времени создания;
- перечисление `TaskStatus` со статусами `created`, `processing`, `completed`;
- вычисляемые свойства через `@property`:
  - `is_ready` — задача готова к обработке;
  - `is_finished` — задача завершена;
- специализированные исключения:
  - `TaskError`;
  - `TaskIdError`;
  - `TaskDescriptionError`;
  - `TaskPriorityError`;
  - `TaskStatusError`;
- метод `Task.from_dict()`, который создаёт задачу из словаря и не изменяет исходные данные;
- `__slots__` для ограничения внутреннего состояния объекта.

## Запуск приложения

Запуск с API-заглушкой:

```bash
python -m src.main --api
```

Запуск с генерацией задач:

```bash
python -m src.main --generated 5
```

Запуск с чтением из JSONL-файла:

```bash
python -m src.main --file source/messages.jsonl
```

Можно комбинировать источники:

```bash
python -m src.main --api --generated 3 --file source/messages.jsonl
```

## Формат JSONL-файла

Каждая строка файла — отдельный JSON-объект задачи:

```json
{"id": "1", "description": "Сделать лабораторную работу", "priority": 1, "status": "created"}
```

Обязательные поля:

- `id`;
- `description`.

Необязательные поля:

- `priority` — по умолчанию `1`;
- `status` — по умолчанию `created`.

Если у задачи из источника нет `id`, для неё генерируется UUID.

## Запуск тестов

```bash
python -m pytest
```

Проверка покрытия:

```bash
python -m coverage run -m pytest
python -m coverage report
```

На момент проверки проекта:

```text
34 passed
TOTAL coverage: 89%
```
