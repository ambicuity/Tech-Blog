"""Tests for slo.py: every number the article prints is computed here.

Run:  python3 -m unittest test_slo -v
       python3 -m unittest test_slo -v -W error::DeprecationWarning
"""

import unittest

import yaml

from slo import (
    MINUTES_PER_DAY,
    WORKBOOK_RULES_999,
    AlertRule,
    EventLog,
    ForDurationAlert,
    build_flapping,
    build_low_traffic,
    build_stream,
    build_with_outage,
    budget_balance,
    budget_remaining_fraction,
    burn_rate,
    evaluate_rules,
    full_outage_budget_minutes,
    generate_prometheus_rules,
    policy_action,
)

TARGET = 0.999  # 99.9% SLO over 30 days
RPM = 10_000  # requests per minute in the checkout scenarios
DAYS_30 = 30 * MINUTES_PER_DAY


def incident_stream(
    clean_minutes: int = 120,
    spike_minutes: int = 60,
    spike_error_rate: float = 0.15,
    requests_per_minute: int = 1000,
) -> EventLog:
    """Clean traffic, then one error spike. Minutes before the spike are
    real clean minutes, so a 1-hour window at 5 minutes into the spike
    still contains 55 clean minutes, exactly as a Prometheus rate would."""
    log = EventLog()
    for minute in range(clean_minutes):
        log.append(minute, requests_per_minute, 0)
    bad = int(round(requests_per_minute * spike_error_rate))
    for minute in range(clean_minutes, clean_minutes + spike_minutes):
        log.append(minute, requests_per_minute, bad)
    return log


def clean_then_burn(
    clean_days: int, burn_days: int, rate: float, requests_per_minute: int = RPM
) -> EventLog:
    """Clean history first, so long windows are fully populated when the
    burn starts, exactly as a service that has been running for weeks."""
    log = EventLog()
    minute = 0
    for _ in range(clean_days * MINUTES_PER_DAY):
        log.append(minute, requests_per_minute, 0)
        minute += 1
    bad = int(round(requests_per_minute * rate))
    for _ in range(burn_days * MINUTES_PER_DAY):
        log.append(minute, requests_per_minute, bad)
        minute += 1
    return log


class TestBudgetArithmetic(unittest.TestCase):
    def test_full_outage_budget_minutes(self):
        self.assertAlmostEqual(full_outage_budget_minutes(0.99), 432.0)
        self.assertAlmostEqual(full_outage_budget_minutes(0.999), 43.2)
        self.assertAlmostEqual(full_outage_budget_minutes(0.9995), 21.6)
        self.assertAlmostEqual(full_outage_budget_minutes(0.9999), 4.32)

    def test_burn_rate_arithmetic(self):
        self.assertAlmostEqual(burn_rate(0.001, 0.999), 1.0)
        self.assertAlmostEqual(burn_rate(0.0144, 0.999), 14.4)
        self.assertAlmostEqual(burn_rate(0.0035, 0.999), 3.5)
        self.assertAlmostEqual(burn_rate(1.0, 0.999), 1000.0)

    def test_steady_half_burn_leaves_half_the_budget(self):
        # 0.05% errors against a 99.9% SLO is a 0.5 burn rate.
        log = build_stream(DAYS_30, RPM, 0.0005)
        self.assertAlmostEqual(
            budget_remaining_fraction(log, TARGET, now=DAYS_30), 0.5
        )

    def test_steady_burn_one_spends_exactly_the_budget(self):
        log = build_stream(DAYS_30, RPM, 0.001)
        self.assertAlmostEqual(
            budget_remaining_fraction(log, TARGET, now=DAYS_30), 0.0
        )

    def test_twenty_minute_outage_costs_46_percent_of_budget(self):
        # 20 minutes of total outage / 43.2 minutes of budget = 46.3%.
        log = build_with_outage(
            requests_per_minute=1000, outage_minutes=20
        )
        self.assertAlmostEqual(
            budget_remaining_fraction(log, TARGET, now=DAYS_30),
            1 - 20 / 43.2,
            places=4,
        )

    def test_cumulative_balance_falls_linearly_at_burn_one(self):
        log = build_stream(DAYS_30, RPM, 0.001)
        expected_total = RPM * DAYS_30
        self.assertAlmostEqual(
            budget_balance(log, TARGET, expected_total, now=DAYS_30 // 2), 0.5
        )
        self.assertAlmostEqual(
            budget_balance(log, TARGET, expected_total, now=DAYS_30), 0.0
        )

    def test_cumulative_balance_cliff_from_outage(self):
        log = build_with_outage(requests_per_minute=1000, outage_minutes=20)
        expected_total = 1000 * DAYS_30
        before = budget_balance(
            log, TARGET, expected_total, now=10 * MINUTES_PER_DAY
        )
        after = budget_balance(
            log, TARGET, expected_total, now=10 * MINUTES_PER_DAY + 20
        )
        self.assertAlmostEqual(before, 1.0)
        self.assertAlmostEqual(after, 1 - 20 / 43.2, places=4)

    def test_extreme_availability_99999_exhausts_in_26_seconds(self):
        # The workbook: a 100% outage for a 99.999% SLO exhausts the
        # budget in 26 seconds, faster than most alert pipelines.
        self.assertAlmostEqual(
            full_outage_budget_minutes(0.99999) * 60, 25.92, places=1
        )

    def test_90_percent_slo_page_rule_can_never_fire(self):
        # The workbook: at 90%, a 100% outage consumes only 1.4% of the
        # budget in an hour, below the 2% the fast page rule needs.
        self.assertAlmostEqual(60 / full_outage_budget_minutes(0.90), 0.0139, places=3)


class TestMultiwindowRules(unittest.TestCase):
    def test_workbook_table_short_windows_are_one_twelfth(self):
        for rule in WORKBOOK_RULES_999:
            self.assertEqual(rule.short_window_min * 12, rule.long_window_min)

    def test_workbook_table_values(self):
        fast, medium, slow = WORKBOOK_RULES_999
        self.assertEqual((fast.long_window_min, fast.burn, fast.severity), (60, 14.4, "page"))
        self.assertEqual((medium.long_window_min, medium.burn, medium.severity), (360, 6.0, "page"))
        self.assertEqual((slow.long_window_min, slow.burn, slow.severity), (4320, 1.0, "ticket"))

    def test_fast_burn_pages_at_minute_six_not_five(self):
        # 15% errors: the 1h window average crosses 1.44% after 6
        # minutes (6 * 15% / 60 = 1.5%), not after 5 (1.25%).
        # Budget spent by then: 900 / 43,200 = 2.08%, as designed.
        log = incident_stream()
        self.assertFalse(WORKBOOK_RULES_999[0].fires(log, TARGET, 120 + 5))
        self.assertTrue(WORKBOOK_RULES_999[0].fires(log, TARGET, 120 + 6))

    def test_page_stops_five_minutes_after_errors_stop(self):
        # The short window is what resets the alert. Without it the
        # 1h window alone would keep the page firing for ~55 minutes.
        log = incident_stream(clean_minutes=120, spike_minutes=10)
        spike_end = 130
        self.assertTrue(WORKBOOK_RULES_999[0].fires(log, TARGET, spike_end))
        self.assertFalse(WORKBOOK_RULES_999[0].fires(log, TARGET, spike_end + 6))
        # ...while the long window alone is still above threshold.
        self.assertGreater(
            log.window_error_rate(60, spike_end + 6), 0.0144
        )

    def test_slow_burn_tickets_but_never_pages(self):
        # 0.35% errors is a 3.5x burn: below both page thresholds (6x
        # and 14.4x), above the 1x ticket threshold. The ticket fires
        # once the 3-day window average crosses 0.1%, after about
        # 72h * 0.1/0.35 = 20.6 hours of sustained errors.
        log = clean_then_burn(3, 3, 0.0035)
        page_fired = any(
            rule.fires(log, TARGET, minute)
            for rule in WORKBOOK_RULES_999[:2]
            for minute in range(3 * MINUTES_PER_DAY, 6 * MINUTES_PER_DAY, 60)
        )
        self.assertFalse(page_fired)
        ticket = WORKBOOK_RULES_999[2]
        self.assertFalse(ticket.fires(log, TARGET, 3 * MINUTES_PER_DAY + 20 * 60))
        self.assertTrue(ticket.fires(log, TARGET, 3 * MINUTES_PER_DAY + 21 * 60))

    def test_raw_error_rate_alert_would_page_on_noise(self):
        # Alerting when the 10-minute error rate merely exceeds the SLO
        # (0.1%) fires on a 0.2% wobble that spends 0.02% of budget in
        # 10 minutes: up to 144 pages a day that never threaten the SLO.
        # The multiwindow rules do not page on it: a sustained 0.2%
        # error rate is a 2x burn, which correctly opens a ticket, not
        # a page.
        log = build_stream(60, RPM, 0.002)
        self.assertGreater(log.window_error_rate(10, 60), 0.001)
        self.assertAlmostEqual(
            burn_rate(log.window_error_rate(10, 60), TARGET), 2.0
        )
        self.assertFalse(any(r.fires(log, TARGET, 60) for r in WORKBOOK_RULES_999[:2]))
        self.assertTrue(WORKBOOK_RULES_999[2].fires(log, TARGET, 60))

    def test_raw_error_rate_alert_misses_a_slow_burn(self):
        # A 3.5x burn never crosses a "page on 14.4x" style threshold,
        # yet consumes the whole 30-day budget in 30 / 3.5 = 8.6 days.
        log = build_stream(9 * MINUTES_PER_DAY, RPM, 0.0035)
        self.assertLess(
            budget_remaining_fraction(log, TARGET, now=9 * MINUTES_PER_DAY), 0.05
        )
        self.assertFalse(WORKBOOK_RULES_999[0].fires(log, TARGET, 9 * MINUTES_PER_DAY))
        self.assertFalse(WORKBOOK_RULES_999[1].fires(log, TARGET, 9 * MINUTES_PER_DAY))

    def test_flapping_spikes_never_fire_a_for_duration_alert(self):
        # Workbook Figure 5-3: 100% errors for 5 minutes in every 10
        # never trips `for: 1h`, because each clean minute resets the
        # timer, while three spikes consume ~35% of the budget. The
        # budget share is a cumulative balance against the month's
        # expected traffic (1000 req/min * 43,200 min).
        log = build_flapping(minutes=30)
        naive = ForDurationAlert(threshold_rate=0.001, duration_min=60)
        self.assertFalse(any(naive.fires(log, minute) for minute in range(1, 31)))
        self.assertAlmostEqual(
            1 - budget_balance(log, TARGET, 1000 * DAYS_30, now=30),
            15 / 43.2,
            places=3,
        )

    def test_flapping_spikes_do_fire_the_multiwindow_page(self):
        # Evaluate inside an on-period (minute 25): the 5-minute short
        # window is all errors, and the 1-hour window sits at 60%.
        log = build_flapping(minutes=30)
        self.assertTrue(WORKBOOK_RULES_999[0].fires(log, TARGET, 25))

    def test_low_traffic_single_failure_is_a_100x_burn(self):
        # 10 requests/hour, one failure: a 10% hourly error rate, which
        # is 100x the 0.1% budget rate, and 1/7.2 = 13.9% of the budget.
        # (The workbook prints 1,000x for this case; the arithmetic
        # from its own 10% figure gives 100x, and this simulator
        # agrees with the arithmetic.) Evaluate one minute after the
        # failure, while it is still inside every short window.
        log = build_low_traffic()
        rate = log.window_error_rate(60, 1)
        self.assertAlmostEqual(rate, 0.10)
        self.assertAlmostEqual(burn_rate(rate, TARGET), 100.0)
        self.assertAlmostEqual(
            1 - budget_balance(log, TARGET, 10 * 24 * 30, now=1),
            1 / 7.2,
            places=3,
        )
        self.assertEqual(
            len([r for r in WORKBOOK_RULES_999 if r.fires(log, TARGET, 1)]), 3
        )


class TestRatioOfSums(unittest.TestCase):
    def test_ratio_of_sums_not_average_of_ratios(self):
        log = EventLog()
        log.append(0, 1000, 0)  # quiet minute, 0% errors
        log.append(1, 10, 10)  # tiny minute, 100% errors
        self.assertAlmostEqual(log.window_error_rate(2, 2), 10 / 1010)
        self.assertAlmostEqual(log.average_of_ratios(2, 2), 0.5)

    def test_empty_window_is_zero_not_an_error(self):
        log = EventLog()
        self.assertEqual(log.window_error_rate(60, 60), 0.0)
        self.assertEqual(budget_remaining_fraction(log, TARGET, now=60), 1.0)
        self.assertEqual(evaluate_rules(log, TARGET, 60), [])


class TestPolicy(unittest.TestCase):
    def test_policy_transitions(self):
        self.assertEqual(policy_action(0.9), "ship normally")
        self.assertEqual(policy_action(0.51), "ship normally")
        self.assertEqual(policy_action(0.5), "every release needs a tested rollback plan")
        self.assertEqual(policy_action(0.1), "every release needs a tested rollback plan")
        self.assertEqual(policy_action(0.0), "freeze features; work reliability until back in budget")
        self.assertEqual(policy_action(-0.2), "freeze features; work reliability until back in budget")


class TestGeneratedRules(unittest.TestCase):
    def test_generated_yaml_parses_and_matches_workbook_table(self):
        text = generate_prometheus_rules("checkout", 0.999)
        doc = yaml.safe_load(text)
        rules = doc["groups"][0]["rules"]
        self.assertEqual(len(rules), 2)
        page_expr = rules[0]["expr"]
        self.assertIn("ratio_rate1h", page_expr)
        self.assertIn("ratio_rate5m", page_expr)
        self.assertIn("14.4*0.001", page_expr)
        self.assertIn("ratio_rate6h", page_expr)
        self.assertIn("ratio_rate30m", page_expr)
        self.assertIn("6.0*0.001", page_expr)
        ticket_expr = rules[1]["expr"]
        self.assertIn("ratio_rate3d", ticket_expr)
        self.assertIn("ratio_rate6h", ticket_expr)
        self.assertIn("1.0*0.001", ticket_expr)
        self.assertEqual(rules[0]["labels"]["severity"], "page")
        self.assertEqual(rules[1]["labels"]["severity"], "ticket")

    def test_alert_rule_rejects_a_short_window_not_one_twelfth(self):
        with self.assertRaises(ValueError):
            AlertRule("bad", 60, 10, 14.4, "page")

    def test_bucket_rejects_more_bad_than_total(self):
        with self.assertRaises(ValueError):
            EventLog().append(0, 10, 11)


if __name__ == "__main__":
    unittest.main()
