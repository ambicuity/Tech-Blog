"""Print one requests-instrumentation span as JSON.

The test suite runs this in a subprocess twice: once with no
OTEL_SEMCONV_STABILITY_OPT_IN (the default) and once with it set to
``http``. The attribute keys prove which convention set the
instrumentation actually emits; the article's claims about old versus
stable names come from this output, not from the docs alone.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


def main():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    RequestsInstrumentor().instrument()
    requests.get(
        f"http://127.0.0.1:{server.server_port}/orders/42?token=secret",
        timeout=5,
    )
    server.shutdown()
    for span in exporter.get_finished_spans():
        print(json.dumps({"name": span.name, "attrs": dict(span.attributes)}))


if __name__ == "__main__":
    main()
