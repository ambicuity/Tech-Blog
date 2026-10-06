"""Minimal MCP 2026-07-28 server: one tool, stateless Streamable HTTP.

Pinned versions: Python 3.12, mcp 2.3.0 (the official Python SDK).

Run it:
    uvicorn server:app --host 127.0.0.1 --port 8000

Call it with plain HTTP (no initialize handshake, no session):
    curl -s -X POST http://127.0.0.1:8000/mcp \
      -H 'Content-Type: application/json' \
      -H 'Accept: application/json, text/event-stream' \
      -H 'MCP-Protocol-Version: 2026-07-28' \
      -H 'Mcp-Method: tools/call' -H 'Mcp-Name: sha256' \
      -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
           "params":{"name":"sha256","arguments":{"text":"abc"},
           "_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28",
                    "io.modelcontextprotocol/clientCapabilities":{}}}}'

What this server guarantees:
  * every request is answered on its own, from a single POST;
  * no per-client state is kept between requests (stateless_http=True);
  * requests with a forged Origin header are rejected (DNS rebinding
    protection is ON here; the SDK ships it OFF by default).

What it does NOT do: authenticate callers. In production, put this behind
an authenticated gateway or wire the SDK's auth settings; the spec says
servers SHOULD authenticate all connections.
"""

import hashlib

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

PROTOCOL_VERSION = "2026-07-28"

server = MCPServer("stateless-demo")


@server.tool()
def sha256(text: str) -> str:
    """Return the hex SHA-256 digest of the input text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_app(*, dns_rebinding_protection: bool = True):
    """Build the ASGI app.

    Flip dns_rebinding_protection to False and the /mcp endpoint accepts
    requests from any Origin, which is exactly the DNS-rebinding hole the
    spec's Security section warns about. The SDK's default is False, kept
    for backwards compatibility: turn it on yourself.
    """
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=dns_rebinding_protection,
        # Hosts this deployment is served on. Requests with any other Host
        # header are rejected when protection is enabled. The ":*" wildcard
        # covers any port, which is what you want behind a local dev server;
        # in production, list the exact public host instead.
        allowed_hosts=["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*"],
        # Browser origins allowed to call this server. A page served from
        # anywhere else gets 403, which is what stops DNS rebinding.
        allowed_origins=["https://app.example.com"],
    )
    return server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,   # no session state between requests
        json_response=True,    # answer with one JSON object, not SSE
        transport_security=security,
    )


app = build_app()
