---
name: api-case-debugger
description: Debug API test cases and interface automation failures. Use when the user mentions 调试接口用例, 接口测试失败, 接口自动化报错, pytest 接口, Postman collection tests, API assertion failures, HTTP status mismatches, auth errors, request payload issues, or wants help locating why an API case fails.
---

# API Case Debugger

## Purpose

Help debug API test cases with evidence first. Cover both Postman collection tests and Python API automation frameworks using pytest, requests or httpx.

## Default Workflow

1. Identify the failing case, command, environment, endpoint, method, and expected result.
2. Reproduce the failure with the smallest reliable command:
   - Postman: use the Postman test workflow or Newman command if present.
   - pytest: run the specific test node, then broaden only if needed.
3. Collect evidence before changing code:
   - Request URL, method, headers, query params, body, files.
   - Response status, headers, body, timing, redirects.
   - Environment variables, base URL, selected Postman environment, pytest markers.
   - Auth token source, expiry, scopes, cookies, signature fields.
   - Test data source and upstream setup dependencies.
4. Classify the failure:
   - Environment/config: wrong base URL, missing env var, proxy, DNS, TLS, timeout.
   - Authentication: missing token, expired token, wrong scope, bad signature, cookie/session loss.
   - Request contract: wrong path, method, params, headers, content type, payload shape.
   - Data dependency: missing seed data, reused IDs, order-dependent case, dirty state.
   - Assertion issue: assertion expects old schema, checks brittle text, ignores nullable fields.
   - Service behavior: real API regression, 5xx, changed business rule, rate limit.
5. Make the smallest fix that matches the classification.
6. Re-run the failing case, then a nearby smoke/regression subset if the change touches shared helpers.

## Postman Debugging

When Postman is involved:

- Prefer plugin workflows for collection tests, docs, mocks, sync, security, and search.
- Check collection variables, environment variables, auth inheritance, pre-request scripts, and test scripts.
- Compare resolved values, not just template variables like `{{baseUrl}}`.
- For test script failures, separate API response failure from JavaScript assertion failure.
- For sync/codegen issues, inspect the source collection or OpenAPI spec before editing generated code.

## Pytest API Automation Debugging

When pytest is involved:

- Use targeted commands first:

```bash
pytest path/to/test_file.py::TestClass::test_case -vv -s
```

- If markers exist, use them for a focused subset:

```bash
pytest -m smoke -vv
```

- Prefer fixing shared helpers when the same problem appears across cases:
  - HTTP client/session wrapper.
  - Environment settings.
  - Auth fixture.
  - Data loader.
  - Assertion helper.

- Avoid hardcoding base URLs, tokens, cookies, or case-specific sleeps in tests.
- If retries hide the root cause, run once without reruns while debugging.

## Evidence To Report

When explaining a failure, include:

- Root cause: one sentence.
- Evidence: exact status/body/assertion/log clue that proves it.
- Fix: what changed or should change.
- Verification: command or Postman run used to confirm.
- Residual risk: only if relevant, such as missing backend logs or unstable shared test data.

## Safe Editing Rules

- Do not change unrelated cases while debugging one case.
- Do not loosen assertions just to make a test pass.
- Preserve meaningful contract checks: status code, business code, required fields, and important side effects.
- If the API behavior changed intentionally, update the expected result and note the contract reason.
- If credentials or secrets appear in logs, redact them in responses and do not commit them.

## User Interaction

If required context is missing, ask for the minimum needed:

- The failing command or Postman run.
- The failing test file or collection name.
- The error output.
- Target environment.
- Whether the API behavior or the test expectation is considered correct.

When the user asks in Chinese, answer in Chinese.
