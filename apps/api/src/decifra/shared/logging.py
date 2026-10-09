"""One JSON line per relevant event, for whoever operates the deployed demo.

The question and the report text never go in. These records say what happened,
how long it took and whether a guardrail refused the answer: enough to follow
the operation without reading anyone's health data.
"""

import json
import logging
from time import perf_counter
from uuid import uuid4

logger = logging.getLogger("decifra.events")


def new_request_id() -> str:
    return uuid4().hex[:12]


def elapsed_ms(started: float) -> int:
    return int((perf_counter() - started) * 1000)


def log_event(event: str, **fields) -> None:
    logger.info(json.dumps({"event": event, **fields}, ensure_ascii=False, default=str))
