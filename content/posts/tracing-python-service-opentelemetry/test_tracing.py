"""Tests for the tracing helpers, the propagation demo, and the
semantic-convention claim. Run: ``python3 -m unittest discover -v``
from this folder, with opentelemetry-api/sdk 1.45.1 installed.
Tests that need requests instrumentation skip without it.
"""

import json
import os
import subprocess
import sys
import unittest

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.sampling import (
        ALWAYS_OFF,
        ALWAYS_ON,
        ParentBased,
        TraceIdRatioBased,
    )
    from opentelemetry.trace import SpanContext, SpanKind, StatusCode, TraceFlags

    from tracing import (
        build_provider,
        checkout,
        normalize_path,
        production_sampler,
        sanitize_url,
    )

    OTEL = True
except ImportError:  # pragma: no cover - environment without the SDK
    OTEL = False

try:
    import requests  # noqa: F401
    from opentelemetry.instrumentation.requests import (  # noqa: F401
        RequestsInstrumentor,
    )

    REQUESTS_INSTRUMENTATION = True
except ImportError:
    REQUESTS_INSTRUMENTATION = False


@unittest.skipUnless(OTEL, "opentelemetry-api/sdk not installed")
class TestSanitizing(unittest.TestCase):
    def test_sanitize_strips_query_and_fragment(self):
        self.assertEqual(
            sanitize_url("https://shop.example/orders?token=secret#top"),
            "https://shop.example/orders",
        )
        self.assertEqual(
            sanitize_url("http://127.0.0.1:8000/health"),
            "http://127.0.0.1:8000/health",
        )

    def test_normalize_path_generalizes_ids(self):
        self.assertEqual(
            normalize_path("/orders/12345/items"), "/orders/{id}/items"
        )
        self.assertEqual(
            normalize_path("/users/550e8400-e29b-41d4-a716-446655440000"),
            "/users/{id}",
        )
        self.assertEqual(
            normalize_path("/orders/recent"), "/orders/recent"
        )


@unittest.skipUnless(OTEL, "opentelemetry-api/sdk not installed")
class TestSpans(unittest.TestCase):
    def test_checkout_span_tree(self):
        provider, exporter = build_provider()
        tracer = trace.get_tracer("test", tracer_provider=provider)
        result = checkout(tracer, 3)
        self.assertEqual(result, {"reserved": 3})
        spans = {s.name: s for s in exporter.get_finished_spans()}
        parent, child = spans["checkout"], spans["reserve_inventory"]
        self.assertEqual(child.parent.span_id, parent.context.span_id)
        self.assertEqual(
            child.parent.trace_id, parent.context.trace_id
        )
        self.assertEqual(parent.attributes["order.item_count"], 3)
        self.assertEqual(parent.attributes["order.currency"], "USD")
        self.assertEqual(parent.kind, SpanKind.SERVER)
        self.assertEqual(child.kind, SpanKind.CLIENT)
        self.assertEqual(parent.status.status_code, StatusCode.UNSET)

    def test_checkout_failure_marks_span_error(self):
        provider, exporter = build_provider()
        tracer = trace.get_tracer("test", tracer_provider=provider)
        with self.assertRaises(RuntimeError):
            checkout(tracer, 1, inventory_ok=False)
        spans = {s.name: s for s in exporter.get_finished_spans()}
        parent = spans["checkout"]
        self.assertEqual(parent.status.status_code, StatusCode.ERROR)
        events = [e.name for e in parent.events]
        self.assertIn("exception", events)

    def test_ratio_sampler_zero_drops_one_keeps(self):
        for sampler, expected in ((TraceIdRatioBased(0.0), 0),
                                  (TraceIdRatioBased(1.0), 1)):
            provider, exporter = build_provider(sampler=sampler)
            tracer = trace.get_tracer("test", tracer_provider=provider)
            with tracer.start_as_current_span("work"):
                pass
            self.assertEqual(len(exporter.get_finished_spans()), expected)

    def test_parent_based_honours_sampled_parent(self):
        provider, exporter = build_provider(
            sampler=ParentBased(root=ALWAYS_OFF)
        )
        tracer = trace.get_tracer("test", tracer_provider=provider)
        sampled = SpanContext(
            trace_id=0x1234567890ABCDEF1234567890ABCDEF,
            span_id=0x1234567890ABCDEF,
            is_remote=True,
            trace_flags=TraceFlags(0x01),
        )
        ctx = trace.set_span_in_context(trace.NonRecordingSpan(sampled))
        with tracer.start_as_current_span("child", context=ctx):
            pass
        self.assertEqual(len(exporter.get_finished_spans()), 1)

    def test_production_sampler_is_parent_based_ratio(self):
        sampler = production_sampler()
        self.assertIsInstance(sampler, ParentBased)
        self.assertIsInstance(sampler._root, TraceIdRatioBased)
        self.assertEqual(sampler._root._rate, 0.1)

    def test_propagation_round_trip(self):
        import demo

        provider, exporter = build_provider()
        server = demo.make_server(provider)
        tracer = trace.get_tracer("test", tracer_provider=provider)
        from urllib.request import Request, urlopen
        from opentelemetry import propagate

        url = f"http://127.0.0.1:{server.server_port}/reserve"
        with tracer.start_as_current_span(
            "reserve_inventory", kind=SpanKind.CLIENT
        ):
            request = Request(url, data=b"{}", method="POST")
            propagate.inject(request.headers)
            with urlopen(request, timeout=5) as response:
                response.read()
        server.shutdown()
        server.server_close()
        spans = {s.name: s for s in exporter.get_finished_spans()}
        client, server_span = spans["reserve_inventory"], spans["POST /reserve"]
        self.assertEqual(
            client.context.trace_id, server_span.context.trace_id
        )
        self.assertEqual(
            server_span.parent.span_id, client.context.span_id
        )


@unittest.skipUnless(
    OTEL and REQUESTS_INSTRUMENTATION,
    "requests instrumentation not installed",
)
class TestSemconv(unittest.TestCase):
    def _probe(self, env_value):
        env = dict(os.environ)
        if env_value is None:
            env.pop("OTEL_SEMCONV_STABILITY_OPT_IN", None)
        else:
            env["OTEL_SEMCONV_STABILITY_OPT_IN"] = env_value
        out = subprocess.run(
            [sys.executable, "probe_semconv.py"],
            capture_output=True, text=True, timeout=60, env=env, check=True,
        )
        return json.loads(out.stdout.strip().splitlines()[-1])["attrs"]

    def test_default_emits_old_names(self):
        attrs = self._probe(None)
        self.assertIn("http.method", attrs)
        self.assertIn("http.status_code", attrs)
        self.assertIn("http.url", attrs)
        self.assertNotIn("http.request.method", attrs)
        # The default URL attribute carries the query string verbatim.
        self.assertIn("token=secret", attrs["http.url"])

    def test_http_opt_in_emits_stable_names(self):
        attrs = self._probe("http")
        self.assertIn("http.request.method", attrs)
        self.assertIn("http.response.status_code", attrs)
        self.assertIn("url.full", attrs)
        self.assertIn("server.address", attrs)
        self.assertNotIn("http.method", attrs)
        self.assertNotIn("http.url", attrs)


if __name__ == "__main__":
    unittest.main()
