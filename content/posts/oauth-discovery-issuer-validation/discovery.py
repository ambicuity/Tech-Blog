"""OAuth 2.0 authorization-server discovery with mandatory issuer validation.

Implements the client side of RFC 8414 section 3 (metadata retrieval and
validation). The discovery order follows the MCP authorization spec
(2026-07-28): the client learns the authorization server's URL from the
protected resource's metadata (RFC 9728) first, then fetches and validates
the authorization server's own metadata document (RFC 8414).

The one rule this module never bends: the ``issuer`` value inside a metadata
document MUST be byte-identical to the issuer identifier the client
independently discovered (RFC 8414 section 3.3). If they differ, the document
MUST NOT be used. There is no fallback path that skips this check.

Tested on Python 3.12, standard library only.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Callable


class DiscoveryError(Exception):
    """Discovery failed closed. No credentials were sent anywhere."""


class IssuerMismatchError(DiscoveryError):
    """The metadata document's issuer did not match the discovered URL."""


WELL_KNOWN_SUFFIX = "/.well-known/oauth-authorization-server"
REQUIRED_FIELDS = ("issuer", "authorization_endpoint", "token_endpoint")


def well_known_url(issuer: str) -> str:
    """Build the RFC 8414 section 3.1 metadata URL for an issuer identifier.

    The well-known string is inserted *before* the path component, so
    ``https://example.com/tenant`` becomes
    ``https://example.com/.well-known/oauth-authorization-server/tenant``.
    """
    parts = urllib.parse.urlsplit(issuer)
    if parts.scheme != "https" or not parts.netloc:
        raise DiscoveryError(
            f"issuer must be an https URL with a host: {issuer!r}"
        )
    if parts.query or parts.fragment:
        raise DiscoveryError(
            f"issuer must have no query or fragment: {issuer!r}"
        )
    path = parts.path.rstrip("/")
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, WELL_KNOWN_SUFFIX + path, "", "")
    )


@dataclass(frozen=True)
class AuthorizationServer:
    """A metadata document that survived validation. Safe to use."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    raw: dict = field(repr=False, compare=False)


def _require_https(url: str, field_name: str) -> None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.netloc:
        raise DiscoveryError(
            f"{field_name} must be an absolute https URL: {url!r}"
        )


def validate_metadata(document: dict, expected_issuer: str) -> AuthorizationServer:
    """Apply RFC 8414 section 3.3 to a fetched metadata document.

    ``expected_issuer`` is the issuer identifier the client discovered
    independently (from protected-resource metadata, or a pinned value the
    operator configured). The comparison is exact: no case folding, no
    trailing-slash trimming, no default-port elision. Anything else, and the
    document is discarded.
    """
    if not isinstance(expected_issuer, str) or not expected_issuer:
        # Fail closed: a missing anchor must never mean "skip the check".
        raise DiscoveryError(
            "refusing to validate metadata with no expected issuer"
        )
    issuer = document.get("issuer")
    if not isinstance(issuer, str) or issuer != expected_issuer:
        raise IssuerMismatchError(
            f"metadata issuer {issuer!r} does not match "
            f"the discovered issuer {expected_issuer!r}"
        )
    for name in REQUIRED_FIELDS:
        if not isinstance(document.get(name), str) or not document[name]:
            raise DiscoveryError(f"metadata is missing required field {name!r}")
    _require_https(document["authorization_endpoint"], "authorization_endpoint")
    _require_https(document["token_endpoint"], "token_endpoint")
    return AuthorizationServer(
        issuer=issuer,
        authorization_endpoint=document["authorization_endpoint"],
        token_endpoint=document["token_endpoint"],
        raw=dict(document),
    )


def fetch_metadata(url: str) -> dict:
    """Fetch a metadata document over HTTPS and parse it as JSON."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise DiscoveryError(f"metadata must be fetched over https: {url!r}")
    request = urllib.request.Request(
        url, headers={"Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise DiscoveryError(
                f"metadata request failed with status {response.status}"
            )
        return json.loads(response.read().decode("utf-8"))


def discover(
    issuer: str,
    fetch: Callable[[str], dict] = fetch_metadata,
) -> AuthorizationServer:
    """Discover and validate an authorization server, end to end.

    ``issuer`` is the identifier the client learned from the protected
    resource (or pinned in configuration). The metadata is fetched from the
    well-known URL derived from it, then validated against it. Either step
    failing raises DiscoveryError and nothing is trusted.
    """
    url = well_known_url(issuer)
    document = fetch(url)
    return validate_metadata(document, issuer)


class CredentialStore:
    """Holds client secrets bound to a *validated* issuer.

    Secrets are registered only together with the AuthorizationServer object
    that validation produced, and are released only for that exact issuer.
    A credential labeled for one issuer is never sent to another's endpoints,
    which is what stops the metadata lie from turning into credential theft.
    """

    def __init__(self) -> None:
        self._secrets: dict[str, str] = {}

    def register(self, server: AuthorizationServer, client_secret: str) -> None:
        self._secrets[server.issuer] = client_secret

    def secret_for(self, server: AuthorizationServer) -> str:
        try:
            return self._secrets[server.issuer]
        except KeyError:
            raise KeyError(
                f"no credential registered for validated issuer {server.issuer!r}"
            ) from None
