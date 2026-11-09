"""日志：同时输出到控制台和 logs/test_YYYYMMDD.log，级别由 LOG_LEVEL 控制（排查问题时设为 DEBUG）。"""
from __future__ import annotations

import logging
from datetime import datetime

from config.settings import settings

_FORMAT = "%(asctime)s %(levelname)s [%(module)s] %(message)s"


def _build_logger(name: str = "qa") -> logging.Logger:
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(settings.LOG_LEVEL)
    log.propagate = False
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(_FORMAT)
    log_file = settings.LOG_DIR / f"test_{datetime.now():%Y%m%d}.log"
    for handler in (logging.StreamHandler(), logging.FileHandler(log_file, encoding="utf-8", delay=True)):
        handler.setFormatter(formatter)
        log.addHandler(handler)
    return log


logger = _build_logger()
