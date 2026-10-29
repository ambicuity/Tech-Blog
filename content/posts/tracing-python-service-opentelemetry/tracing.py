"""Tracing helpers for "Tracing a Python Service with OpenTelemetry".

Pinned versions: Python 3.12, opentelemetry-api 1.45.1,
opentelemetry-sdk 1.45.1. The requests instrumentation used by the
semconv probe is opentelemetry-instrumentation-requests 0.66b1.

Run the demo: ``python3 demo.py`` (stdlib only apart from the SDK).
Run the tests: ``python3 -m unittest discover -v`` from this folder.
"""

import re
from urllib.parse import urlparse

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.sdk.trace.sampling import (
    ParentBased,
    TraceIdRatioBased,
)
from opentelemetry.trace import SpanKind, Status, StatusCode

SERVICE_NAME = "checkout-service"

_ID_SEGMENT = re.compile(r"\A([0-9]+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\Z")


def sanitize_url(url):
    """Return the URL without query string or fragment.

    Instrumentations record the full URL by default, so a URL like
    ``https://shop.example/orders?token=secret`` lands in the trace
    backend verbatim. Strip it before the value ever becomes an
    attribute; the route template, not the query, is the grouping key.
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def normalize_path(path):
    """Replace id-like path segments with ``{id}``.

    ``/orders/12345/items`` and ``/orders/98765/items`` are the same
    operation. Recording the raw path creates one time series per
    order id; the route template keeps cardinality bounded.
    """
    parts = []
    for segment in path.split("/"):
        if _ID_SEGMENT.match(segment):
            parts.append("{id}")
        else:
            parts.append(segment)
    return "/".join(parts)


def build_provider(sampler=None):
    """Build a TracerProvider wired to an in-memory exporter.

    Production code uses BatchSpanProcessor and an OTLP exporter; the
    in-memory exporter exists so tests can read the finished spans.
    The sampler defaults to the SDK default (ParentBased AlwaysOn);
    pass an explicit sampler in production instead of relying on it.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider(sampler=sampler)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def production_sampler():
    """Sample 10 percent of root traces, honour a sampled parent.

    ParentBased means: if an upstream service already sampled this
    trace, keep sampling it end to end; otherwise apply the ratio.
    A ratio of 1.0 (the SDK default via parentbased_always_on) on a
    busy service exports every trace and pays for it in the backend.
    """
    return ParentBased(root=TraceIdRatioBased(0.1))


def checkout(tracer, item_count, inventory_ok=True):
    """One business operation, traced as one named span.

    The ``checkout`` span is the span an on-call engineer searches
    for. Library spans underneath it explain the latency; without
    this span the trace is a pile of HTTP calls with no owner.
    """
    with tracer.start_as_current_span("checkout", kind=SpanKind.SERVER) as span:
        span.set_attribute("order.item_count", item_count)
        span.set_attribute("order.currency", "USD")
        try:
            with tracer.start_as_current_span(
                "reserve_inventory", kind=SpanKind.CLIENT
            ) as child:
                child.set_attribute("server.address", "inventory.internal")
                if not inventory_ok:
                    raise RuntimeError("inventory service refused")
                child.add_event("inventory reserved")
        except RuntimeError as exc:
            # Status UNSET means "finished without error" to a backend.
            # A span that owns a failure must say so, and the exception
            # event carries the type and message for the alert query.
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            span.record_exception(exc)
            raise
        return {"reserved": item_count}
