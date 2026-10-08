---
title: "Validate the Issuer: Securing OAuth Discovery Metadata"
description: >-
  OAuth discovery hands your client the URLs where credentials go. RFC 8414's
  issuer check is the control that keeps that safe; a September 2026 flaw in
  the MCP Python SDK showed what happens when the check exists but does not
  run on every path. A deep dive with a tested Python client.
date: 2026-10-08 14:00:00 +0000
author: ritesh
categories: [Security, AI]
tags: [oauth, openid-connect, mcp, discovery, security, python]
kind: Deep Dive
draft: false
cover:
  image: cover.webp
  alt: "Two OAuth metadata documents side by side: a trusted one with a check mark, and a rogue one whose attacker-controlled token endpoint is crossed out."
---

On September 28, 2026, Cycode published research showing that the MCP Python SDK, versions 1.9.1 through 1.29.1 and 2.0.0 through 2.1.1, could be tricked by a malicious MCP server into handing over OAuth credentials: the client secret, the authorization code, and the PKCE verifier, the complete set needed to mint a valid access token. The login page the victim saw was genuine. There was no phishing, no fake certificate, nothing to notice. The SDK was fixed in 1.30.0 and 2.2.0.

The root cause was not a missing check. The check existed: validate the authorization server metadata's `issuer`. It simply did not run on every discovery path. When a server answered 404 to the modern discovery request, the SDK fell back to asking the server directly for its login configuration, and on that path the anchor the check needed was empty, so the check was skipped. The attacker then supplied metadata that named the victim's real identity provider as its issuer while pointing the token endpoint at the attacker's own infrastructure.

This article is about the one rule that stops this class of attack. It is short, it is old, and it is load-bearing: the `issuer` value inside an authorization server metadata document must be identical to the issuer identifier the client independently discovered, and if it is not, the document must not be used. That is RFC 8414, section 3.3. What follows is how discovery works, why that check is the control that matters, the three ways production code gets it wrong, and a small Python client that gets it right, with sixteen tests that replay the attack.

This deep dive targets Python 3.12 (standard library only), `mcp` 2.2.0 and 1.30.0 (the fixed releases; 2.3.0 is current as of writing), the MCP specification revision 2026-07-28, and RFC 8414.

> [!NOTE]
> **In short**
> - The `issuer` inside an authorization server metadata document must be byte-identical to the issuer identifier you discovered independently. If it differs, discard the document. That is RFC 8414 section 3.3, and it is the whole defense.
> - Never guard that check with "if we have the anchor". A missing anchor must fail closed, because the attacker controls whether the anchor exists.
> - Do not validate metadata against itself. Compare against the URL you discovered independently, never against the `issuer` value inside the same document.
> - Pin the expected issuer in configuration for machine-to-machine clients. On `mcp` 2.2.0 and later, pass `issuer=` to the machine-to-machine providers; it becomes required in 3.0.
> - After upgrading a client that may have touched an untrusted server, clear stored registrations, rotate the client secret, and revoke tokens. Upgrading alone does not rebind old credentials.

## How discovery is supposed to work

An OAuth client starts out knowing the resource server, the API it wants to call, but not the authorization server, the login provider that will issue its tokens. Discovery bridges that gap in two hops. First, the client fetches the resource server's protected resource metadata (RFC 9728), a small document at the server's well-known URL that names the authorization server. Second, the client fetches the authorization server's own metadata (RFC 8414) from the well-known URL derived from that name, which lists the endpoints: where to send the user to log in, where to exchange the code for a token, where to register the client.

Notice what that means: every URL the client will eventually send credentials to arrives in documents the resource server pointed at. Discovery is a mechanism for a server to tell your client where your secrets go. The only thing standing between that mechanism and credential theft is the client's willingness to check the answer against something the server did not supply.

That check is RFC 8414 section 3.3, and it fits in two sentences: the `issuer` value returned must be identical to the issuer identifier the well-known URL was built from, and if the two are not identical, the data in the response must not be used. The RFC's security considerations describe the exact attack it prevents: an attacker publishing a metadata document that carries the impersonated server's issuer identifier but its own endpoints and signing keys, which lets it impersonate that server "if accepted by the client". The authors saw this coming in 2018. The defense has been written down for eight years.

[MCP's 2026-07-28 revision](/posts/mcp-stateless-servers/) builds its authorization flow on exactly this stack: servers must implement protected resource metadata, clients must use it for authorization server discovery, and clients must support both RFC 8414 and OpenID Connect Discovery to read the result. It adds one more binding on top: before redirecting the user, the client must record the `issuer` from the validated metadata document and later compare the `iss` parameter in the authorization response against that recorded value, using simple string comparison with no normalization. The spec is explicit about why: the validation provides no protection if the expected issuer was obtained from an unvalidated source.

![Safe OAuth discovery: the client requests the protected resource, learns the authorization server from its metadata, fetches the authorization server metadata, checks the issuer, and only then trusts the token endpoint.](discovery-flow.svg "Discovery is safe only when the issuer check runs against an independently discovered URL."){: .figure}

## A client that cannot be lied to

The complete client is [discovery.py](discovery.py). It is built in four steps, and each step states what it guarantees and what it leaves to the next one.

**Step 1: build the well-known URL.** `well_known_url` takes an issuer identifier and inserts `/.well-known/oauth-authorization-server` before the path component, per RFC 8414 section 3.1. It guarantees the URL is `https`, has a host, and carries no query or fragment, because an issuer identifier with a query string is not an identifier, it is an attack surface. It does not guarantee anything about who answers at that URL. That is the next step's job.

```python
def well_known_url(issuer: str) -> str:
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
```

**Step 2: validate the document.** `validate_metadata` is the RFC 8414 section 3.3 check, plus the hygiene around it. The comparison is exact: no case folding, no trailing-slash trimming, no default-port elision, matching the RFC's own string-comparison rules and the MCP spec's no-normalization requirement for the `iss` parameter. The required fields must be present, and every endpoint that will receive credentials must be an absolute `https` URL. And the anchor rule: if the expected issuer is missing or empty, validation raises instead of being skipped. A missing anchor is not a reason to skip the check; it is a reason to stop.

```python
def validate_metadata(document: dict, expected_issuer: str) -> AuthorizationServer:
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
```

**Step 3: compose fetch and validate.** `discover` takes the issuer the client learned from the protected resource (or pinned in configuration), fetches the document from the well-known URL, and validates it against that same issuer. Either step failing raises, and nothing is trusted. The fetch function is a parameter, which is what makes the whole flow testable without a network.

**Step 4: bind credentials to the validated issuer.** `CredentialStore` registers secrets only alongside the `AuthorizationServer` object that validation produced, and releases them only for that exact issuer. There is deliberately no way to ask the store for "the secret for this raw document", because a raw document is exactly what the attacker controls. This is the code-level form of the fix the SDK shipped: credentials labeled with their login provider, so credentials labeled for one provider cannot be sent to another.

## Three ways to get this wrong in production

**Mistake 1: the conditional check.** The vulnerable code, as quoted in the disclosure, guarded validation like this:

```python
if self.context.auth_server_url is not None:
    validate_metadata_issuer(asm, self.context.auth_server_url)
```

On the fallback path the server had returned 404, so the anchor was `None`, and the check never ran. Cycode's own summary of the pattern is worth memorizing: a safety check that only runs when certain data is present, where the attacker controls whether that data is present. Skip the check, and the unchecked value does not just go unverified, it flows into the next safety check as trusted input and actively satisfies it.

The fix is to make the anchor unconditional. The SDK now derives the expected issuer on the fallback path from the server's own origin URL instead of leaving it empty, so there is always something to check against, and a mismatch raises `OAuthFlowError`. In `discovery.py` the equivalent is simpler: there is no code path that calls validation with a missing anchor, because a missing anchor raises. When you review OAuth client code, search for the validation call and then ask: is there any path to the token endpoint that does not pass through it? Fallbacks, retries, and "legacy" endpoints are where the answer is usually yes.

![The fallback hijack: the rogue server answers 404 on discovery, forcing the unchecked fallback path, then supplies metadata naming the real identity provider with its own token endpoint.](fallback-hijack.svg "The attacker never breaks the checks; the checks never run."){: .figure}

**Mistake 2: validating against the wrong anchor.** The SDK had a second control, credential binding: credentials carried a label naming the login provider they belonged to, and the client checked the label before using them. The problem was what the label was compared against: the `issuer` field from the login configuration, the same field the attacker controlled because the first check never ran. The attacker set `issuer` to the victim's real identity provider, and the binding check passed. As the disclosure puts it, the attacker did not break this safety check; they passed it with a lie.

The rule: the anchor must come from outside the document being validated. The discovered URL, a pinned configuration value, a trust store, any of these work, because the attacker does not control them. The document's own `issuer` field is the claim under test; comparing the claim to itself proves nothing. This is also why the comparison must be exact. Normalization is a second, quieter way to compare against the wrong thing: `https://auth.example.com/` and `https://auth.example.com` are different strings, and treating them as the same is a policy decision the RFC deliberately does not make for you.

![The issuer check decision: only a byte-identical issuer passes; every normalization trick fails.](issuer-check.svg "RFC 8414 section 3.3: identical, or the data must not be used."){: .figure}

**Mistake 3: unbound credentials and stale registrations.** The disclosure's fix notes contain a warning that is easy to skim past: upgrading the SDK does not finish the job. The machine-to-machine providers had no way to say which login provider their credentials belonged to, so they followed whichever provider the server named. The fixed versions accept an `issuer=` parameter for exactly this, warn when it is missing, and will require it in 3.0. And registrations stored by older versions carry no label at all, so they stay unbound until cleared.

The general lesson: credentials must be bound to their intended issuer from birth, in storage as well as in code. Anything persisted before the binding existed is unbound, and unbound credentials are attacker-steerable credentials. If a client may have connected to an untrusted server while vulnerable, the remediation is three steps in order: clear stored registrations so the client re-registers with the binding in place, rotate the client secret because it is long-lived and reusable, and revoke tokens at the provider. Rotating the token without rotating the secret leaves the attacker able to mint new ones.

## Proving it

The proofs are [test_discovery.py](test_discovery.py): sixteen tests, all passing on Python 3.12.3 against the standard library only, with deprecation warnings treated as errors. Every test replaces the network with canned documents, so the suite runs with no servers and nothing to attack.

The center of the suite is the attack replay, in three parts that mirror the disclosure's own experiments. First, the attack: a helper shaped like the vulnerable code takes the fallback path, where the anchor is `None` and the guard is skipped, and accepts the rogue document. The test then asserts the theft directly, that the document's `token_endpoint` points at the attacker while its `issuer` still names the real identity provider. Second, the fix: the same rogue document, validated against the server's own origin as the expected issuer, raises `IssuerMismatchError` before anything is trusted. Third, the control: when discovery succeeds and the check runs, the rogue document is rejected there too, proving the issuer check is the control that matters.

Around that core, the suite pins the exactness of the check: a trailing slash, a case change, an explicit default port, and a scheme downgrade are all rejected, as are a missing `issuer` field and non-`https` endpoints. Two tests pin the fail-closed behavior: validating with no expected issuer raises instead of skipping, and a document the attacker controls can never become an `AuthorizationServer` object, so the credential store has nothing to release the secret for.

```
$ python -m pytest test_discovery.py -q
................                                    [100%]
16 passed in 0.05s
```

## Operating it

An issuer check that nobody watches is a control you cannot prove. Four things to instrument around any OAuth client that does discovery.

**Count validation decisions.** Emit a counter for metadata fetch outcomes with the decision as a label: `validated`, `issuer_mismatch`, `fetch_failed`, `fallback_taken`. An `issuer_mismatch` in production is either an attack or a misconfigured identity provider, and both need a human. Alert on any nonzero count; this is not a metric where a small baseline is normal.

**Watch the fallback rate.** The attack works by forcing the fallback path, a server answering 404 on protected-resource-metadata discovery and the client asking the server directly instead. A spike in `fallback_taken` is the exact precondition of this attack class. The fixed SDK goes further: if protected resource metadata cannot be fetched because of a 5xx or 429, the flow now stops instead of falling back to legacy endpoints. Treat fallback as an exceptional event, log the server that triggered it, and make sure your dashboards can show it per server. If the fetch fails transiently, retry it with [backoff and jitter](/posts/retries-with-exponential-backoff-and-jitter/) rather than degrading to a path that skips validation.

**Log the decision, not the secrets.** On every discovery, log the expected issuer, the validation decision, and which path was taken. Never log the metadata document's endpoints alongside client secrets in a way that lets a log reader reconstruct where credentials went, and never log the secrets themselves. When an `issuer_mismatch` fires, the log line should let you answer: which server, which discovered URL, what the document claimed.

**Rotate on suspicion, rebind on upgrade.** Client secrets are long-lived by design; the disclosure notes that rotating the code or revoking the current token does not help if the secret itself is not rotated. Build rotation into the runbook: one command to rotate the secret at the provider, one to clear stored client registrations, one to verify the client re-registers with the issuer binding in place. After any SDK upgrade that changes credential binding, clear stored registrations once as a matter of routine, the way the fixed SDK's own advisory instructs.

## Trade-offs and alternatives

**Skip discovery entirely.** Discovery exists for clients that meet identity providers they have never seen: multi-tenant products, agent frameworks connecting to arbitrary servers. If your client talks to one identity provider that you chose, pin the issuer and the endpoints in configuration and do not discover anything. There is no safer metadata document than one the attacker never got to influence. The cost is operational: rotating endpoints means changing configuration, but for a first-party client that is a deploy, not a vulnerability.

**Signed metadata.** RFC 8414 lets an authorization server sign its metadata as a JWT, so the client validates a signature against a pinned key instead of comparing an issuer string. This is stronger against document tampering, but it moves the trust problem to key distribution: you still need an independent way to know whose key to pin, which is the same problem the issuer check solves more simply. Consider signed metadata when you already operate a key distribution story, not as a first defense.

**Bind the token, not just the discovery.** The issuer check protects the discovery step; it says nothing about what a stolen token is worth afterwards. Token binding mechanisms like DPoP tie the token to a client-held key, so a token lifted from one channel cannot be replayed from another, and the resource parameter (RFC 8707) plus the `iss` check in the authorization response narrow where a stolen code can be redeemed. The MCP spec mandates the resource parameter and the `iss` validation for exactly this reason. These are complements, not substitutes: use them together.

**The cost of exactness.** Byte-identical comparison means an identity provider that changes its issuer string, adds a trailing slash, or moves regions will break your client loudly. That is the intended behavior, and the correct response is a configuration change with a human looking at it, not a normalization rule that silently accepts both. Every normalization you add is a bet that no attacker will find the gap between the strings you consider equal; the RFC authors declined to make that bet for you.

## Checklist

1. Pin the expected issuer before discovery, from configuration or the protected resource's validated metadata, never from the document under test.
2. Compare the document's `issuer` to the expected value with exact string equality. No case folding, no trailing-slash trimming, no port elision.
3. Run the check on every discovery path, including fallbacks and legacy endpoints. A missing anchor fails closed.
4. Require `https` on the metadata URL and on every endpoint in the document.
5. Bind stored credentials to the validated issuer. Never release a secret for an unvalidated document.
6. After upgrading past a binding fix: clear stored registrations once, rotate client secrets, revoke tokens if exposure was possible.
7. Alert on any issuer mismatch in production, and watch the fallback-path rate per server.
8. For first-party clients with a known provider, skip discovery and pin the endpoints.

## References

- [MCP Python SDK OAuth flaw: account takeover via unvalidated discovery](https://cycode.com/blog/mcp-python-sdk-oauth-account-takeover/): Cycode research, published September 28, 2026: the fallback-path mechanism, affected versions, and the fix.
- [RFC 8414: OAuth 2.0 Authorization Server Metadata](https://www.rfc-editor.org/rfc/rfc8414.html): section 3.3 states the issuer validation rule; section 6.2 describes the impersonation attack it prevents.
- [MCP authorization specification, revision 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization): protected resource metadata discovery, client discovery requirements, and RFC 9207 `iss` validation.
- [mcp 2.2.0 release notes](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.2.0): issuer validation on every discovery path, `issuer=` pinning for machine-to-machine providers, and the new fallback behavior on 5xx/429.
