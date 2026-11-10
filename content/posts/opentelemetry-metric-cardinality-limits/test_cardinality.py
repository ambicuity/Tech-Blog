"""Tests for OpenTelemetry Python SDK 1.45.2 cardinality enforcement.

Every test runs against the real SDK (opentelemetry-api/sdk 1.45.2,
Python 3.12) with an in-memory reader, except the Prometheus test, which
renders the exposition format through a fresh registry. Small limits stand
in for the 2000 default so the mechanism is visible in a handful of
measurements; the default-limit tests use the real 2000.
"""

import unittest

from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics._internal.aggregation import AggregationTemporality
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.metrics.view import View

from cardinality import (
    DEFAULT_LIMIT,
    INSTRUMENT_NAME,
    OVERFLOW_ATTRIBUTE,
    collect,
    filtered_total,
    is_overflow,
    make_provider,
    record_requests,
    total,
)


class TestDefaultLimit(unittest.TestCase):
    def test_overflow_starts_at_combination_2001(self):
        provider, reader = make_provider()
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        routes = [f"/item/{i}" for i in range(DEFAULT_LIMIT + 1)]
        record_requests(counter, routes, failures=["/item/0"])
        points = collect(reader)
        overflow = [p for p in points if is_overflow(p[0])]
        self.assertEqual(len(points), DEFAULT_LIMIT + 1)
        self.assertEqual(len(overflow), 1)
        self.assertEqual(overflow[0][0], {OVERFLOW_ATTRIBUTE: True})
        # The 2001st route and the failure folded together.
        self.assertEqual(overflow[0][1], 2)
        self.assertEqual(total(points), DEFAULT_LIMIT + 2)
        provider.shutdown()

    def test_no_overflow_at_exactly_the_limit(self):
        provider, reader = make_provider()
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        routes = [f"/item/{i}" for i in range(DEFAULT_LIMIT)]
        record_requests(counter, routes)
        points = collect(reader)
        self.assertEqual(len(points), DEFAULT_LIMIT)
        self.assertFalse(any(is_overflow(a) for a, _ in points))
        self.assertEqual(total(points), DEFAULT_LIMIT)
        provider.shutdown()

    def test_filtered_query_misses_overflowed_failures(self):
        provider, reader = make_provider(limit=3)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        record_requests(counter, ["/a", "/b", "/c"], failures=["/a"])
        points = collect(reader)
        # The failure is a fourth combination, so it folds into overflow.
        self.assertEqual(filtered_total(points, "success", "false"), 0)
        self.assertEqual(total(points), 4)
        provider.shutdown()


class TestViews(unittest.TestCase):
    def test_view_raises_the_limit(self):
        provider, reader = make_provider(limit=5000)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        routes = [f"/item/{i}" for i in range(DEFAULT_LIMIT + 1)]
        record_requests(counter, routes, failures=["/item/0"])
        points = collect(reader)
        # 2001 success=true combinations plus the one success=false
        # combination: no overflow, so every combination gets a point.
        self.assertEqual(len(points), DEFAULT_LIMIT + 2)
        self.assertFalse(any(is_overflow(a) for a, _ in points))
        self.assertEqual(total(points), DEFAULT_LIMIT + 2)
        provider.shutdown()

    def test_view_dropping_the_unbounded_attribute(self):
        provider, reader = make_provider(keep_attributes={"success"})
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        routes = [f"/item/{i}" for i in range(DEFAULT_LIMIT + 1)]
        record_requests(counter, routes, failures=["/item/0"])
        points = collect(reader)
        self.assertEqual(len(points), 2)
        self.assertEqual(filtered_total(points, "success", "true"),
                         DEFAULT_LIMIT + 1)
        self.assertEqual(filtered_total(points, "success", "false"), 1)
        self.assertEqual(total(points), DEFAULT_LIMIT + 2)
        provider.shutdown()

    def test_limit_is_enforced_after_attribute_filtering(self):
        # After the View drops http.route, only two combinations remain
        # (success true/false), so a limit of 1 still overflows.
        provider, reader = make_provider(
            limit=1, keep_attributes={"success"})
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        record_requests(counter, ["/a", "/b", "/c"], failures=["/a"])
        points = collect(reader)
        overflow = [p for p in points if is_overflow(p[0])]
        self.assertEqual(len(points), 2)
        self.assertEqual(len(overflow), 1)
        self.assertEqual(total(points), 4)
        provider.shutdown()


class TestReaderLimit(unittest.TestCase):
    def test_reader_level_limit(self):
        reader = InMemoryMetricReader(cardinality_limits={Counter: 3})
        provider = MeterProvider(metric_readers=[reader])
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        record_requests(counter, [f"/item/{i}" for i in range(5)])
        points = collect(reader)
        overflow = [p for p in points if is_overflow(p[0])]
        self.assertEqual(len(points), 4)
        self.assertEqual(len(overflow), 1)
        self.assertEqual(overflow[0][1], 2)
        self.assertEqual(total(points), 5)
        provider.shutdown()


class TestTemporality(unittest.TestCase):
    def _two_cycles(self, temporality):
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
        provider.shutdown()
        return cycle1, cycle2

    def test_cumulative_accumulates_combinations_across_cycles(self):
        cycle1, cycle2 = self._two_cycles(AggregationTemporality.CUMULATIVE)
        self.assertEqual(len(cycle1), 4)
        self.assertEqual(total(cycle1), 4)
        overflow = [p for p in cycle2 if is_overflow(p[0])]
        self.assertEqual(len(cycle2), 6)  # 5 regular + overflow
        self.assertEqual(len(overflow), 1)
        self.assertEqual(overflow[0][1], 3)  # tenants t5, t6, t7
        self.assertEqual(total(cycle2), 8)

    def test_delta_resets_each_cycle(self):
        cycle1, cycle2 = self._two_cycles(AggregationTemporality.DELTA)
        self.assertEqual(len(cycle1), 4)
        self.assertEqual(total(cycle1), 4)
        self.assertEqual(len(cycle2), 4)
        self.assertFalse(any(is_overflow(a) for a, _ in cycle2))
        self.assertEqual(total(cycle2), 4)


class TestOverflowSemantics(unittest.TestCase):
    def test_first_observed_combinations_keep_their_points(self):
        provider, reader = make_provider(limit=3)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        record_requests(counter, ["/a", "/b", "/c", "/d", "/e"])
        points = collect(reader)
        regular = sorted(a["http.route"] for a, _ in points
                         if not is_overflow(a))
        self.assertEqual(regular, ["/a", "/b", "/c"])
        overflow = [p for p in points if is_overflow(p[0])]
        self.assertEqual(overflow[0][1], 2)  # /d and /e folded together
        provider.shutdown()

    def test_overflow_value_accumulates(self):
        provider, reader = make_provider(limit=3)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        for route in ["/a", "/b", "/c", "/d", "/e"]:
            counter.add(2, {"http.route": route})
        points = collect(reader)
        overflow = [p for p in points if is_overflow(p[0])]
        self.assertEqual(overflow[0][1], 4)  # two folded routes x 2
        self.assertEqual(total(points), 10)
        provider.shutdown()

    def test_no_measurement_lost_or_double_counted(self):
        provider, reader = make_provider(limit=10)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        for i in range(12):
            counter.add(3, {"http.route": f"/item/{i}"})
        points = collect(reader)
        self.assertEqual(len(points), 11)  # 10 regular + overflow
        self.assertEqual(total(points), 36)  # 12 measurements x 3
        provider.shutdown()

    def test_histogram_overflows_too(self):
        from opentelemetry.sdk.metrics import Histogram

        reader = InMemoryMetricReader(cardinality_limits={Histogram: 5})
        provider = MeterProvider(metric_readers=[reader])
        meter = provider.get_meter("checkout")
        histogram = meter.create_histogram("http.server.request.duration")
        durations = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        for route, seconds in zip(
                [f"/item/{i}" for i in range(6)], durations):
            histogram.record(seconds, {"http.route": route})
        data = reader.get_metrics_data()
        points = []
        for rm in data.resource_metrics:
            for sm in rm.scope_metrics:
                for metric in sm.metrics:
                    points.extend(metric.data.data_points)
        overflow = [p for p in points
                    if dict(p.attributes).get(OVERFLOW_ATTRIBUTE) is True]
        self.assertEqual(len(points), 6)
        self.assertEqual(len(overflow), 1)
        self.assertEqual(overflow[0].count, 1)
        self.assertAlmostEqual(overflow[0].sum, 0.6)
        self.assertEqual(sum(p.count for p in points), 6)
        self.assertAlmostEqual(sum(p.sum for p in points), 2.1)
        provider.shutdown()

    def test_attribute_free_measurements_never_overflow(self):
        provider, reader = make_provider(limit=3)
        meter = provider.get_meter("checkout")
        counter = meter.create_counter(INSTRUMENT_NAME)
        for _ in range(100):
            counter.add(1)
        points = collect(reader)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0][0], {})
        self.assertEqual(points[0][1], 100)
        provider.shutdown()


class TestPrometheusExporter(unittest.TestCase):
    def test_overflow_series_carries_the_overflow_label(self):
        from demo import prometheus_overflow_lines

        lines = prometheus_overflow_lines()
        self.assertEqual(len(lines), 4)  # 3 regular + overflow
        overflow_lines = [ln for ln in lines
                          if 'otel_metric_overflow="true"' in ln]
        self.assertEqual(len(overflow_lines), 1)
        self.assertTrue(overflow_lines[0].endswith(" 2.0"))
        values = [float(ln.rsplit(" ", 1)[1]) for ln in lines]
        self.assertEqual(sum(values), 5.0)


if __name__ == "__main__":
    unittest.main()
