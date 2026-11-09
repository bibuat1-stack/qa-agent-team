"""HTTP 客户端单例：共享会话、重试、超时、默认请求头，以及脱敏后的请求/响应日志。

用例只传相对路径，例如 http_client.get("/posts/1")，基础地址来自 settings.BASE_URL。
"""
from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from common.logger import logger
from common.utils import redact_headers, redact_text, response_text, to_log_text, truncate
from config.settings import settings


class HttpClient:
    _instance: HttpClient | None = None
    session: requests.Session

    def __new__(cls) -> HttpClient:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.session = cls._create_session()
            cls._instance = instance
        return cls._instance

    @staticmethod
    def _create_session() -> requests.Session:
        # 只重试连接失败和读超时；HTTP 错误状态码原样返回，交给断言判断。
        # urllib3 默认会对带 Retry-After 的 413/429/503 等待后重发（POST 也会），所以关掉。
        retry = Retry(
            total=settings.RETRY_TIMES,
            backoff_factor=0.5,
            allowed_methods=frozenset({"GET", "POST", "PUT", "DELETE"}),
            respect_retry_after_header=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        # Content-Type 由 requests 按 json= / data= / files= 自动设置，固定成 JSON 会破坏表单和文件上传。
        session.headers.update({"Accept": "application/json"})
        if settings.API_TOKEN:
            session.headers["Authorization"] = f"Bearer {settings.API_TOKEN}"
        return session

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        method = method.upper()
        url = self.build_url(path)
        kwargs.setdefault("timeout", settings.TIMEOUT)
        self._log_request(method, url, kwargs)
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            logger.error("请求异常 %s %s：%s", method, redact_text(url), redact_text(str(exc)))
            raise
        self._log_response(response)
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def set_token(self, token: str | None) -> None:
        """登录后切换令牌；传 None 去掉认证头。"""
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        else:
            self.session.headers.pop("Authorization", None)

    def close(self) -> None:
        self.session.close()

    @staticmethod
    def build_url(path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{settings.BASE_URL}/{path.lstrip('/')}"

    def _log_request(self, method: str, url: str, kwargs: dict[str, Any]) -> None:
        logger.info("--> %s %s", method, redact_text(url))
        logger.debug("    请求头：%s", redact_headers({**self.session.headers, **(kwargs.get("headers") or {})}))
        for key in ("params", "json", "data"):
            if kwargs.get(key) is not None:
                logger.info("    %s：%s", key, truncate(to_log_text(kwargs[key])))

    @staticmethod
    def _log_response(response: requests.Response) -> None:
        elapsed_ms = response.elapsed.total_seconds() * 1000
        logger.info("<-- %s %s（%.0f ms）", response.status_code, redact_text(response.url), elapsed_ms)
        logger.debug("    响应头：%s", redact_headers(response.headers))
        logger.info("    响应体：%s", truncate(response_text(response)))


http_client = HttpClient()
