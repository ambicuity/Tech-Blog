"""End-to-end propagation demo: one trace id across an HTTP boundary.

A stdlib HTTP server extracts the W3C traceparent header the client
injected, so its server span becomes a child of the client's span.
Run: ``python3 demo.py``. Prints the client span, the server span,
and whether they share a trace id.
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen

from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind

from tracing import build_provider


def make_server(provider):
    tracer = trace.get_tracer("demo.inventory", tracer_provider=provider)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            ctx = propagate.extract(self.headers)
            with tracer.start_as_current_span(
                "POST /reserve", kind=SpanKind.SERVER, context=ctx
            ) as span:
                span.set_attribute("http.request.method", "POST")
                span.set_attribute("url.path", "/reserve")
                span.set_attribute("http.response.status_code", 200)
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main():
    provider, exporter = build_provider()
    server = make_server(provider)
    tracer = trace.get_tracer("demo.checkout", tracer_provider=provider)
    url = f"http://127.0.0.1:{server.server_port}/reserve"
    with tracer.start_as_current_span("reserve_inventory", kind=SpanKind.CLIENT):
        request = Request(url, data=b"{}", method="POST")
        propagate.inject(request.headers)
        with urlopen(request, timeout=5) as response:
            response.read()
    server.shutdown()
    server.server_close()
    spans = {span.name: span for span in exporter.get_finished_spans()}
    client = spans["reserve_inventory"]
    server_span = spans["POST /reserve"]
    print(f"client trace id: {client.context.trace_id:032x}")
    print(f"server trace id: {server_span.context.trace_id:032x}")
    print(f"server parent:   {server_span.parent.span_id:016x}")
    print(f"client span id:  {client.context.span_id:016x}")
    print("same trace:", client.context.trace_id == server_span.context.trace_id)
    print(
        "server is child of client:",
        server_span.parent.span_id == client.context.span_id,
    )


if __name__ == "__main__":
    main()
