"""Demo: what the OpenTelemetry Python 1.45.2 cardinality limit does.

Scenario 1 records 2001 routes against the default limit of 2000, with one
failure on an already-seen route. Scenario 2 drops the unbounded attribute
with a View. Scenario 3 shows the same tenant dimension under cumulative
and delta temporality across two collection cycles.
"""

from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics._internal.aggregation import AggregationTemporality
from opentelemetry.sdk.metrics.view import View

from cardinality import (
    DEFAULT_LIMIT,
    INSTRUMENT_NAME,
    collect,
    filtered_total,
    is_overflow,
    make_provider,
    record_requests,
    total,
)


def scenario_default_limit():
    provider, reader = make_provider()
    meter = provider.get_meter("checkout")
    counter = meter.create_counter(INSTRUMENT_NAME)
    routes = [f"/item/{i}" for i in range(DEFAULT_LIMIT + 1)]
    record_requests(counter, routes, failures=["/item/0"])
    points = collect(reader)
    overflow = [p for p in points if is_overflow(p[0])]
    print(f"Default limit ({DEFAULT_LIMIT}), {len(routes)} routes, "
          "1 failure on /item/0:")
    print(f"  data points: {len(points)} "
          f"({len(points) - len(overflow)} regular + {len(overflow)} overflow)")
    print(f"  overflow value: {overflow[0][1]} "
          "(the 2001st route plus the failure, folded together)")
    print(f"  total requests: {total(points)} (correct: 2002 recorded)")
    print(f"  success=false total: "
          f"{filtered_total(points, 'success', 'false')} "
          "(wrong: 1 failure was recorded, the query sees 0)")
    provider.shutdown()


def scenario_drop_attribute():
    provider, reader = make_provider(keep_attributes={"success"})
    meter = provider.get_meter("checkout")
    counter = meter.create_counter(INSTRUMENT_NAME)
    routes = [f"/item/{i}" for i in range(DEFAULT_LIMIT + 1)]
    record_requests(counter, routes, failures=["/item/0"])
    points = collect(reader)
    print("View keeps only success (drops http.route):")
    for attrs, value in points:
        print(f"  data point {attrs}: {value}")
    print(f"  total requests: {total(points)} (correct)")
    print(f"  success=false total: "
          f"{filtered_total(points, 'success', 'false')} (correct now)")
    provider.shutdown()


def scenario_temporality():
    for temporality in (AggregationTemporality.CUMULATIVE,
                        AggregationTemporality.DELTA):
        provider, reader = make_provider(
            limit=5, temporality=temporality)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        for i in range(4):
            counter.add(1, {"tenant": f"t{i}"})
        cycle1 = collect(reader)
        for i in range(4, 8):
            counter.add(1, {"tenant": f"t{i}"})
        cycle2 = collect(reader)
        overflow = [p for p in cycle2 if is_overflow(p[0])]
        print(f"{temporality.name}: cycle 1 has {len(cycle1)} points, "
              f"cycle 2 has {len(cycle2)} points, "
              f"overflow value {overflow[0][1] if overflow else 0}, "
              f"cycle 2 total {total(cycle2)}")
        provider.shutdown()


def prometheus_overflow_lines(limit=3, n_routes=5):
    """Render the Prometheus exposition for an overflowing counter.

    Returns the exposition lines for the request counter. Needs
    opentelemetry-exporter-prometheus 0.66b2 and prometheus_client.
    """
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from prometheus_client import CollectorRegistry, generate_latest

    registry = CollectorRegistry()
    reader = PrometheusMetricReader(registry=registry)
    provider = MeterProvider(
        metric_readers=[reader],
        views=[View(instrument_name=INSTRUMENT_NAME,
                    aggregation_cardinality_limit=limit)],
    )
    meter = provider.get_meter("checkout")
    counter = meter.create_counter(INSTRUMENT_NAME)
    record_requests(counter, [f"/item/{i}" for i in range(n_routes)])
    text = generate_latest(registry).decode()
    provider.shutdown()
    return [ln for ln in text.splitlines()
            if ln.startswith("http_server_request_count_total{")]


if __name__ == "__main__":
    scenario_default_limit()
    scenario_drop_attribute()
    scenario_temporality()
