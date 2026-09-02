"""Utilities for the command line interface."""

import json
import logging
import sys
from collections.abc import Awaitable, Callable
from enum import Enum, StrEnum
from types import SimpleNamespace
from typing import Any

import asyncclick as click
import yaml
from aiohttp import ClientSession, TraceConfig
from aiohttp.tracing import TraceRequestEndParams
from asyncclick.core import Context
from pydantic import BaseModel, ValidationError
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexer import Lexer
from pygments.lexers import JsonLexer, YamlLexer

from ..api_layer.exceptions import OpenApiError
from ..api_layer.rest_api import PostEndpointResult

_LOGGER = logging.getLogger(__name__)


class Format(StrEnum):
    JSON = "json"
    YAML = "yaml"


class StrEnumChoice(click.Choice):
    """Choice that maps enum values (not names) from the command line to enum members."""

    def normalize_choice(self, choice: object, ctx: Context | None) -> str:
        if isinstance(choice, Enum):
            return str(choice.value)
        return super().normalize_choice(choice, ctx)


async def handle_request(
    ctx: Context,
    func: Callable[..., Awaitable],
    *args: Any,
) -> None:
    """Handle API requests and perform error handling."""
    try:
        result = await func(*args)
        if isinstance(result, BaseModel):
            ctx.obj["print"](result.model_dump(mode="json", by_alias=True))
        elif isinstance(result, PostEndpointResult):
            ctx.obj["print"](
                {
                    "url": result.url,
                    "status": result.status,
                    "headers": result.headers,
                }
            )
        elif result is None:
            ctx.obj["print"]({"status": "ok"})
        else:
            ctx.obj["print"](result)
    except (OpenApiError, ValidationError) as err:
        status_code = err.status_code if isinstance(err, OpenApiError) else None
        ctx.obj["print"](
            {
                "error": type(err).__name__,
                "message": str(err),
                "status_code": status_code,
            }
        )


def highlight_for_console(text: str, lexer: Lexer) -> str:
    if sys.stdout.isatty():
        return highlight(text, lexer, TerminalFormatter())
    return text


def print_json(data: Any) -> None:
    print(highlight_for_console(json.dumps(data, indent=4, ensure_ascii=False), JsonLexer()))


def print_yaml(data: Any) -> None:
    print(highlight_for_console(yaml.dump(data, allow_unicode=True), YamlLexer()))


async def trace_response(
    _session: ClientSession,
    _trace_config_ctx: SimpleNamespace,
    params: TraceRequestEndParams,
) -> None:
    """Log response details. Used in aiohttp.TraceConfig."""
    try:
        resp_text = await params.response.text()
    except UnicodeDecodeError:
        resp_text = "<non-UTF-8 response body>"
    _LOGGER.debug(
        "Trace: %s %s - response: %s (%s bytes) %s",
        params.method,
        str(params.url)[:60],
        params.response.status,
        params.response.content_length,
        resp_text[:5000],
    )


TRACE_CONFIG = TraceConfig()
TRACE_CONFIG.on_request_end.append(trace_response)
