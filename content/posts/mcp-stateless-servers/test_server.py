"""Tests for server.py: the MCP 2026-07-28 stateless contract, proved over HTTP.

Pinned versions: Python 3.12, mcp 2.3.0, httpx (ASGI transport, no network).

Each test posts raw JSON-RPC to /mcp and asserts the wire behavior the
article claims. Run:  pytest -W error::DeprecationWarning
"""

import hashlib
import json
from contextlib import asynccontextmanager

import httpx
import pytest

from server import PROTOCOL_VERSION, build_app

CLIENT_CAPS = "io.modelcontextprotocol/clientCapabilities"
PROTOCOL_KEY = "io.modelcontextprotocol/protocolVersion"


def envelope(version: str = PROTOCOL_VERSION) -> dict:
    return {"_meta": {PROTOCOL_KEY: version, CLIENT_CAPS: {}}}


@asynccontextmanager
async def lifespan_client(app, origin: str | None = None):
    """An httpx client speaking raw MCP-over-HTTP to a live ASGI app."""
    transport = httpx.ASGITransport(app=app)

    async def post(method, params=None, msg_id=1, version=PROTOCOL_VERSION,
                   extra_headers=None, notification=False):
        body = {"jsonrpc": "2.0", "method": method}
        if not notification:
            body["id"] = msg_id
        if params is not None:
            body["params"] = params
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": version,
            "Mcp-Method": method,
        }
        if origin:
            headers["Origin"] = origin
        headers.update(extra_headers or {})
        async with httpx.AsyncClient(transport=transport,
                                     base_url="http://127.0.0.1") as client:
            return await client.post("/mcp", content=json.dumps(body),
                                     headers=headers)

    async with app.router.lifespan_context(app):
        yield post


@pytest.mark.asyncio()
async def test_first_request_needs_no_initialize():
    """A modern client opens with tools/list. No handshake, no session."""
    async with lifespan_client(build_app()) as post:
        r = await post("tools/list", {"_meta": envelope()["_meta"]})
    assert r.status_code == 200
    names = [t["name"] for t in r.json()["result"]["tools"]]
    assert "sha256" in names


@pytest.mark.asyncio()
async def test_version_header_must_match_meta():
    """Header and _meta disagree -> 400. The request is rejected, not guessed."""
    params = {"_meta": {PROTOCOL_KEY: "2025-11-25", CLIENT_CAPS: {}}}
    async with lifespan_client(build_app()) as post:
        r = await post("tools/list", params, version=PROTOCOL_VERSION)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == -32020


@pytest.mark.asyncio()
async def test_legacy_initialize_is_rejected():
    """initialize is an unknown method on a modern-only server: 404 / -32601."""
    params = {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
              "clientInfo": {"name": "probe", "version": "0"},
              "_meta": envelope()["_meta"]}
    async with lifespan_client(build_app()) as post:
        r = await post("initialize", params)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == -32601


@pytest.mark.asyncio()
async def test_server_discover_lists_supported_versions():
    """server/discover is mandatory; it names what the server speaks."""
    async with lifespan_client(build_app()) as post:
        r = await post("server/discover", {"_meta": envelope()["_meta"]})
    assert r.status_code == 200
    assert PROTOCOL_VERSION in r.json()["result"]["supportedVersions"]


@pytest.mark.asyncio()
async def test_forged_origin_rejected_when_protection_on():
    """A page from evil.example driving this server gets 403, not a tool run."""
    async with lifespan_client(build_app(dns_rebinding_protection=True),
                               origin="https://evil.example") as post:
        r = await post("tools/list", {"_meta": envelope()["_meta"]})
    assert r.status_code == 403


@pytest.mark.asyncio()
async def test_forged_origin_accepted_when_protection_off():
    """Documents the SDK default: protection is OFF unless you enable it."""
    async with lifespan_client(build_app(dns_rebinding_protection=False),
                               origin="https://evil.example") as post:
        r = await post("tools/list", {"_meta": envelope()["_meta"]})
    assert r.status_code == 200


@pytest.mark.asyncio()
async def test_notification_acknowledged():
    """A notification (no id) is accepted with 202 and an empty body."""
    async with lifespan_client(build_app()) as post:
        r = await post("notifications/cancelled",
                       {"_meta": envelope()["_meta"]}, notification=True)
    assert r.status_code == 202
    assert r.text == ""


@pytest.mark.asyncio()
async def test_unknown_method_is_404():
    async with lifespan_client(build_app()) as post:
        r = await post("frobnicate", {"_meta": envelope()["_meta"]})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == -32601


@pytest.mark.asyncio()
async def test_tools_call_returns_digest():
    """The tool does what its description says, byte for byte."""
    params = {"name": "sha256", "arguments": {"text": "abc"},
              "_meta": envelope()["_meta"]}
    async with lifespan_client(build_app()) as post:
        r = await post("tools/call", params,
                       extra_headers={"Mcp-Name": "sha256"})
    assert r.status_code == 200
    text = r.json()["result"]["content"][0]["text"]
    assert text == hashlib.sha256(b"abc").hexdigest()


@pytest.mark.asyncio()
async def test_requests_carry_no_session_state():
    """Two identical requests with different ids both succeed independently."""
    async with lifespan_client(build_app()) as post:
        for msg_id in (41, 42):
            r = await post("tools/list", {"_meta": envelope()["_meta"]},
                           msg_id=msg_id)
            assert r.status_code == 200
            assert r.json()["id"] == msg_id
