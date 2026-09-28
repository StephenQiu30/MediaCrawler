"""HotKey's Bilibili child uses typed exits, never log text as a risk signal."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import config
from media_platform.bilibili.client import BilibiliClient
from media_platform.bilibili.exception import DataFetchError
from media_platform.bilibili.login import BilibiliLogin


@pytest.mark.asyncio
async def test_missing_login_stops_before_qr_interaction(monkeypatch):
    monkeypatch.setattr(config, "HOTKEY_SAFETY_MODE", True)
    login = BilibiliLogin(login_type="qrcode", browser_context=None, context_page=None)
    with pytest.raises(SystemExit) as failure:
        await login.begin()
    assert failure.value.code == 70


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "payload", "exit_code"),
    [
        (429, {"code": 0}, 71),
        (200, {"code": -101, "message": "arbitrary upstream text"}, 70),
    ],
)
async def test_numeric_upstream_risk_has_typed_exit(
    monkeypatch, status, payload, exit_code
):
    monkeypatch.setattr(config, "HOTKEY_SAFETY_MODE", True)
    response = SimpleNamespace(status_code=status, json=lambda: payload)
    client_context = AsyncMock()
    client_context.__aenter__.return_value.request.return_value = response
    monkeypatch.setattr(
        "media_platform.bilibili.client.make_async_client",
        lambda **_kwargs: client_context,
    )
    client = BilibiliClient(headers={}, playwright_page=None, cookie_dict={})
    monkeypatch.setattr(client, "_refresh_proxy_if_expired", AsyncMock())

    with pytest.raises(SystemExit) as failure:
        await client.request("GET", "https://api.bilibili.com/test")
    assert failure.value.code == exit_code


@pytest.mark.asyncio
async def test_unclassified_error_keeps_ordinary_failure(monkeypatch):
    monkeypatch.setattr(config, "HOTKEY_SAFETY_MODE", True)
    response = SimpleNamespace(status_code=200, json=lambda: {"code": -500, "message": "captcha"})
    client_context = AsyncMock()
    client_context.__aenter__.return_value.request.return_value = response
    monkeypatch.setattr(
        "media_platform.bilibili.client.make_async_client",
        lambda **_kwargs: client_context,
    )
    client = BilibiliClient(headers={}, playwright_page=None, cookie_dict={})
    monkeypatch.setattr(client, "_refresh_proxy_if_expired", AsyncMock())

    with pytest.raises(DataFetchError):
        await client.request("GET", "https://api.bilibili.com/test")
