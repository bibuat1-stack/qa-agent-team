---
name: api-automation-pytest
description: >-
  Guides building and maintaining a Python API automation framework with pytest,
  requests or httpx, allure-pytest, and pytest-html: directory layout, http_client
  singleton, assertions, logging, data-driven cases, reports, reruns, and CI/CD.
  Use for HTTP/HTTPS, REST, or microservice interface tests; Jenkins/GitLab CI;
  or when the user mentions API automation, 接口自动化, 接口测试, pytest 接口,
  Allure, or pytest-rerunfailures.
---

# API automation testing (Python / pytest)

## Purpose

Build an extensible, maintainable API test framework: case design, execution, reports, and troubleshooting. **Stack:** pytest + requests or httpx + allure-pytest + pytest-html. **Goals:** low coupling, reuse, easy maintenance, CI/CD ready.

## Directory layout (mandatory)

Generate and extend code **only** under this tree, rooted at the repository root (paths use `/`):

```
<repository root>/
├── config/
│   ├── settings.py
│   └── environment.py
├── common/
│   ├── http_client.py
│   ├── assertions.py
│   ├── logger.py
│   └── utils.py
├── pages/
│   ├── base_page.py
│   └── <page>_page.py
├── data/
│   ├── api_data/
│   └── test_cases/
├── tests/
│   ├── conftest.py
│   ├── api/
│   │   ├── module1/
│   │   │   ├── test_login.py
│   │   │   ├── test_user_info.py
│   │   │   └── test_order.py
│   │   └── module2/
│   └── ui/
│       ├── conftest.py
│       └── module1/
├── reports/
│   ├── allure-results/
│   └── html/
├── logs/
├── requirements.txt
└── run.py
```

## config/

### `config/settings.py`

- Multi-environment via **`ENVIRONMENT`** (no hardcoded base URL in tests).
- Read from **environment variables** for CI/CD; use `python-dotenv` + `load_dotenv()` where appropriate.
- Expose `BASE_URL` derived from a map keyed by `ENVIRONMENT` (e.g. dev/test/pre/prod), plus shared values: `TIMEOUT`, `RETRY_TIMES`, `LOG_LEVEL`, etc.

### `config/environment.py`

- Centralize **multi-env switching** (dev/test/pre/prod) and any env-specific overrides; keep URLs and secrets out of test files.

## common/

### `common/http_client.py`

- **Singleton** `HttpClient` / module-level `http_client` so sessions are not recreated per call.
- `requests.Session` with `HTTPAdapter` + `urllib3.util.retry.Retry`: `total=settings.RETRY_TIMES`, backoff, allowed methods **GET, POST, PUT, DELETE**.
- Default headers (e.g. `Content-Type: application/json`); `timeout=settings.TIMEOUT`.
- **`request`**, then **`get` / `post` / `put` / `delete`** delegating to `request`.
- Build full URL as `settings.BASE_URL` + path; log request (method, URL, kwargs) and response (status, truncated body) via `common.logger`; on failure log and re-raise.

### `common/assertions.py`

- Reusable helpers: status code; JSON field by dotted path; contains / not contains; lists; null/empty checks—avoid raw `assert` soup in tests.

### `common/logger.py`

- File + console; default level from settings; support debug verbosity.

### `common/utils.py`

- Timestamps, random data, crypto/helpers, file read/write as needed by cases.

## data/

- **`data/api_data/`:** request/response payloads (JSON/YAML).
- **`data/test_cases/`:** data-driven sources (CSV/Excel/YAML).

## tests/

- **`conftest.py`:** session/module fixtures (client, env, data loaders).
- Split by **business module** under `tests/api/<module>/` (API) and `tests/ui/<module>/` (UI).
- **Do not** call `requests.get/post/...` directly in tests; use **`http_client`** only.

## Case authoring rules

Each case should be traceable with: **id, name, preconditions, steps, expected outcome** (in docstring or comments as the project prefers).

- **Markers:** always use `@pytest.mark.*` — e.g. `smoke`, `regression`, and module tags like `@pytest.mark.module_name`.
- **Flow:** call `http_client` → then `assertions` helpers.
- **Config:** fix env/base URL in `config/settings.py` or `environment.py`, never hardcode env-specific values inside a single test file.

## Reports and logging

- Log requests, responses, assertion context, and exceptions under **`logs/`**; default **INFO**, configurable debug.
- **Allure:** `pytest --alluredir=reports/allure-results`; serve with `allure serve reports/allure-results` (or generate static HTML into `reports/allure-report`).
- **Failures:** default **2 reruns** via **pytest-rerunfailures** (`--reruns 2`).

## `requirements.txt`

Include at minimum: `pytest`, `requests` (or `httpx`), `allure-pytest`, `pytest-html`, `pytest-rerunfailures`, `python-dotenv`, and any YAML/Excel libs the project uses.

## `run.py`

Unified CLI entry (args for env, markers, report dirs, reruns).

## CI/CD (example)

```bash
pip install -r requirements.txt
pytest tests/ --alluredir=reports/allure-results --reruns 2
allure generate reports/allure-results -o reports/allure-report --clean
```

Adapt paths and Allure CLI availability for the runner image.

## Agent constraints

1. **Scaffold and changes** must follow the directory layout and module responsibilities above.
2. **New API cases:** extend **`http_client`** and **`assertions`** first; do not duplicate clients or ad-hoc assertion stacks in tests.
3. **Markers** on every new/updated test for filtering by type/module.
4. **Comments:** short notes for scenario intent and assertion logic where non-obvious.
5. **Configuration issues:** fix **`config/settings.py`** / **`environment.py`**; forbid per-case hardcoded environments or base URLs.

## Reference patterns

### Settings (shape)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
    BASE_URLS = {
        "dev": "http://dev-api.example.com",
        "test": "http://test-api.example.com",
        "pre": "http://pre-api.example.com",
        "prod": "https://api.example.com",
    }
    BASE_URL = BASE_URLS[ENVIRONMENT]
    TIMEOUT = 10
    RETRY_TIMES = 2
    LOG_LEVEL = "INFO"

settings = Settings()
```

### Test class (shape)

```python
import pytest
from common.http_client import http_client
from common.assertions import assert_status_code, assert_json_field

class TestLogin:
    """登录接口测试"""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "username, password, expected_code, expected_msg",
        [
            ("valid_user", "valid_pass", 200, "success"),
            ("invalid_user", "invalid_pass", 401, "用户名或密码错误"),
        ],
    )
    def test_login(self, username, password, expected_code, expected_msg):
        """测试登录接口不同场景"""
        payload = {"username": username, "password": password}
        response = http_client.post("/api/login", json=payload)

        assert_status_code(response, expected_code)
        if response.status_code == 200:
            assert_json_field(response, "code", 0)
            assert_json_field(response, "message", expected_msg)
        else:
            assert_json_field(response, "message", expected_msg)
```

Implement `assert_json_field` / `assert_json_contains` with dotted paths and clear failure messages as in the team’s `assertions` module.

## When answering users

Prefer concrete file paths relative to the repository root (`config/`, `common/`, `pages/`, `tests/api/`, `tests/ui/`), minimal diffs, and pytest commands that match their `run.py` and CI. If Allure CLI is missing locally, say how to install it or use CI artifacts instead.
