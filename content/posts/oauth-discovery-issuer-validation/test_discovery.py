"""Proving tests for discovery.py.

Every test is hermetic: the network is replaced by canned metadata documents,
so the suite runs with no servers and no network access.

The attack replay mirrors the September 2026 disclosure in the MCP Python SDK
(Cycode research; fixed in mcp 2.2.0 / 1.30.0): a rogue server answers 404 on
protected-resource-metadata discovery, forcing the client onto a fallback path
where the issuer check is skipped, then hands the client metadata that names
the victim's real identity provider as its issuer while pointing the token
endpoint at the attacker.
"""

import pytest

from discovery import (
    AuthorizationServer,
    CredentialStore,
    DiscoveryError,
    IssuerMismatchError,
    discover,
    validate_metadata,
    well_known_url,
)

REAL_IDP = "https://accounts.real-idp.example"
ATTACKER = "https://evil.example"
ROGUE_SERVER = "https://rogue-mcp.example"

LEGIT_METADATA = {
    "issuer": REAL_IDP,
    "authorization_endpoint": REAL_IDP + "/authorize",
    "token_endpoint": REAL_IDP + "/token",
    "response_types_supported": ["code"],
}

# The attacker's document: claims the victim's real IdP as its issuer, but
# every endpoint that receives credentials points at the attacker.
ROGUE_METADATA = {
    "issuer": REAL_IDP,
    "authorization_endpoint": REAL_IDP + "/authorize",  # the real login page
    "token_endpoint": ATTACKER + "/token",  # ...but the code goes here
    "response_types_supported": ["code"],
}


def fake_fetch(documents):
    def fetch(url):
        try:
            return documents[url]
        except KeyError:
            raise DiscoveryError(f"no canned document for {url}")

    return fetch


def vulnerable_discover(server_origin, fetch):
    """The flawed shape from the disclosure: the issuer check is guarded by
    ``if auth_server_url is not None``. On the fallback path the server
    returned 404, so there is nothing to check against, and the check never
    runs. The returned document is used unchecked."""
    auth_server_url = None  # fallback path: discovery answered 404
    document = fetch(server_origin + "/.well-known/oauth-authorization-server")
    if auth_server_url is not None:
        validate_metadata(document, auth_server_url)
    return document


# --- the happy path --------------------------------------------------------


def test_legit_metadata_validates():
    server = validate_metadata(dict(LEGIT_METADATA), REAL_IDP)
    assert server.issuer == REAL_IDP
    assert server.token_endpoint == REAL_IDP + "/token"


def test_discover_end_to_end_with_pinned_issuer():
    url = well_known_url(REAL_IDP)
    server = discover(REAL_IDP, fetch=fake_fetch({url: dict(LEGIT_METADATA)}))
    assert isinstance(server, AuthorizationServer)


def test_well_known_url_inserts_before_path():
    assert (
        well_known_url("https://example.com/tenant")
        == "https://example.com/.well-known/oauth-authorization-server/tenant"
    )
    assert (
        well_known_url("https://example.com/")
        == "https://example.com/.well-known/oauth-authorization-server"
    )


def test_well_known_url_rejects_non_https_and_extras():
    for bad in (
        "http://example.com",
        "https://example.com?x=1",
        "https://example.com#frag",
        "not-a-url",
    ):
        with pytest.raises(DiscoveryError):
            well_known_url(bad)


# --- the attack replay -----------------------------------------------------


def test_vulnerable_pattern_sends_credentials_to_attacker():
    """On the fallback path the guard is skipped, the rogue document is
    accepted, and the client's credentials would go to the attacker's
    token endpoint. This is the theft, reproduced."""
    fetch = fake_fetch(
        {ROGUE_SERVER + "/.well-known/oauth-authorization-server": dict(ROGUE_METADATA)}
    )
    document = vulnerable_discover(ROGUE_SERVER, fetch)
    assert document["token_endpoint"] == ATTACKER + "/token"
    # The issuer *looks* right, which is why the theft is invisible.
    assert document["issuer"] == REAL_IDP


def test_fixed_client_rejects_rogue_metadata():
    """The fix: the expected issuer on the fallback path is the server's own
    origin, never 'no anchor'. The rogue document names the real IdP, so the
    exact-match check fails and nothing is trusted."""
    url = well_known_url(ROGUE_SERVER)
    fetch = fake_fetch({url: dict(ROGUE_METADATA)})
    with pytest.raises(IssuerMismatchError):
        discover(ROGUE_SERVER, fetch=fetch)


def test_control_path_rejects_rogue_metadata_too():
    """The disclosure's control experiment: when discovery succeeds, the
    check runs even in the vulnerable shape. The independently discovered
    URL is the rogue server's own origin, so the real-IdP issuer claim does
    not match, and the attack is blocked before any credential moves."""
    auth_server_url = ROGUE_SERVER  # discovery answered properly
    with pytest.raises(IssuerMismatchError):
        validate_metadata(dict(ROGUE_METADATA), auth_server_url)


# --- the check itself must be exact ----------------------------------------


@pytest.mark.parametrize(
    "claimed",
    [
        REAL_IDP + "/",  # trailing slash
        "https://ACCOUNTS.real-idp.example",  # case folding
        "https://accounts.real-idp.example:443",  # default port elision
        "http://accounts.real-idp.example",  # scheme downgrade
        REAL_IDP + "?",  # empty query
    ],
)
def test_issuer_must_match_exactly_no_normalization(claimed):
    document = dict(LEGIT_METADATA, issuer=claimed)
    with pytest.raises(IssuerMismatchError):
        validate_metadata(document, REAL_IDP)


def test_missing_issuer_field_rejected():
    document = {k: v for k, v in LEGIT_METADATA.items() if k != "issuer"}
    with pytest.raises(IssuerMismatchError):
        validate_metadata(document, REAL_IDP)


def test_no_expected_issuer_fails_closed_never_skips():
    """A missing anchor must raise, never silently skip the check."""
    with pytest.raises(DiscoveryError):
        validate_metadata(dict(LEGIT_METADATA), None)
    with pytest.raises(DiscoveryError):
        validate_metadata(dict(LEGIT_METADATA), "")


def test_non_https_endpoints_rejected():
    document = dict(LEGIT_METADATA, token_endpoint="http://accounts.real-idp.example/token")
    with pytest.raises(DiscoveryError):
        validate_metadata(document, REAL_IDP)


# --- credential binding ----------------------------------------------------


def test_credentials_bound_to_validated_issuer_only():
    store = CredentialStore()
    server = validate_metadata(dict(LEGIT_METADATA), REAL_IDP)
    store.register(server, "secret-123")
    assert store.secret_for(server) == "secret-123"

    # A document the attacker controls never becomes an AuthorizationServer,
    # so there is no validated object to release the secret for.
    other = validate_metadata(
        {
            "issuer": "https://other-idp.example",
            "authorization_endpoint": "https://other-idp.example/authorize",
            "token_endpoint": "https://other-idp.example/token",
        },
        "https://other-idp.example",
    )
    with pytest.raises(KeyError):
        store.secret_for(other)
