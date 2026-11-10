"""Measure OpenTelemetry Python SDK 1.45.2 metric cardinality enforcement.

A request counter records one measurement per request, with the attributes
``http.route`` and ``success``. The harness shows what the SDK's default
cardinality limit (2000 combinations per metric stream, new in 1.45.2) does
once a high-cardinality attribute pushes a stream past it: the extra
combinations fold into a single overflow data point, totals stay correct,
and any query that filters by an attribute undercounts.

Run the demo with ``python3 demo.py`` and the proofs with
``python3 -m unittest test_cardinality -v``. Requires
``opentelemetry-api`` and ``opentelemetry-sdk`` 1.45.2.
"""

from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics._internal.aggregation import AggregationTemporality
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.metrics.view import View

OVERFLOW_ATTRIBUTE = "otel.metric.overflow"
DEFAULT_LIMIT = 2000
INSTRUMENT_NAME = "http.server.request.count"


def make_provider(*, limit=None, keep_attributes=None, temporality=None):
    """Build a MeterProvider with an in-memory reader.

    limit: per-stream cardinality limit, applied through a View.
        None means the SDK default of 2000.
    keep_attributes: attribute keys to keep; every other attribute is
        dropped by a View before aggregation, so it cannot count toward
        the limit. None keeps all attributes.
    temporality: AggregationTemporality.CUMULATIVE (the default) or .DELTA.
    """
    views = []
    if limit is not None or keep_attributes is not None:
        views.append(
            View(
                instrument_name=INSTRUMENT_NAME,
                aggregation_cardinality_limit=limit,
                attribute_keys=keep_attributes,
            )
        )
    reader_kwargs = {}
    if temporality is not None:
        reader_kwargs["preferred_temporality"] = {Counter: temporality}
    reader = InMemoryMetricReader(**reader_kwargs)
    provider = MeterProvider(metric_readers=[reader], views=views)
    return provider, reader


def provider_with_limit(limit):
    """Build a MeterProvider whose request counter uses the given limit."""
    views = [View(
        instrument_name=INSTRUMENT_NAME,
        aggregation_cardinality_limit=limit,
    )]
    reader = InMemoryMetricReader()
    return MeterProvider(metric_readers=[reader], views=views), reader


def provider_with_reader_limit(limit):
    """Build a MeterProvider with a reader-level limit for counters.

    The reader limit is a mapping from instrument class to limit, not a
    plain number: passing {"default": limit} raises ValueError.
    """
    reader = InMemoryMetricReader(cardinality_limits={Counter: limit})
    return MeterProvider(metric_readers=[reader]), reader


def record_requests(counter, routes, failures=()):
    """Record one successful request per route, plus the failed ones.

    Each route is a distinct attribute combination, so ``len(routes)``
    is the stream's cardinality before the failures are counted.
    """
    for route in routes:
        counter.add(1, {"http.route": route, "success": "true"})
    for route in failures:
        counter.add(1, {"http.route": route, "success": "false"})


def collect(reader):
    """Return [(attributes dict, value)] for every data point collected."""
    points = []
    data = reader.get_metrics_data()
    for resource_metrics in data.resource_metrics:
        for scope_metrics in resource_metrics.scope_metrics:
            for metric in scope_metrics.metrics:
                for point in metric.data.data_points:
                    points.append((dict(point.attributes), point.value))
    return points


def is_overflow(attributes):
    """True when a data point is the overflow point."""
    return attributes.get(OVERFLOW_ATTRIBUTE) is True


def total(points):
    """The unfiltered total: every measurement, including overflowed ones."""
    return sum(value for _, value in points)


def filtered_total(points, key, value):
    """The total for one attribute value, as a filtered query would see it."""
    return sum(v for attrs, v in points if attrs.get(key) == value)
