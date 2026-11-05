"""SLOs and error budgets for one service.

A minute-resolution simulator for a request-driven service (checkout) that
computes every number in the companion article, so none of them is asserted:

* error budget arithmetic for a 99.9% SLO over a rolling 30-day window,
* burn rate, the speed at which the budget is consumed,
* the SRE Workbook's multiwindow, multi-burn-rate alert rules
  (14.4x over 1h + 5m pages, 6x over 6h + 30m pages, 1x over 3d + 6h
  tickets), evaluated against a simulated event stream,
* the naive alternatives that fail: alerting on the raw error rate, and
  using ``for:`` duration to fake a longer window,
* the error-budget policy state machine: what the team does as the
  budget drains.

Conventions, all from the SRE Workbook (Google, "Alerting on SLOs" and
"Implementing SLOs"):

* An SLI is a ratio of good events to total events. The error budget is
  ``100% - SLO``. For 99.9% over 30 days the budget is 0.1% of all
  events in the window, which for a service that is either fully up or
  fully down is 43.2 minutes of outage.
* Burn rate is the error rate divided by the budget rate: an error rate
  of 0.1% against a 99.9% SLO is a burn rate of 1, and consumes the
  budget exactly over the 30-day window.
* A window's error rate is always a ratio of sums (bad events / total
  events over the window), never an average of per-minute ratios.
* Each alert rule needs BOTH a long window and a short window (the short
  window is 1/12 of the long one). The long window decides whether the
  spend is significant; the short window decides whether the service is
  still burning, so the alert stops firing soon after the errors stop.

Python 3.12, standard library only. Run the tests with::

    python3 -m unittest test_slo -v
    python3 -m unittest test_slo -v -W error::DeprecationWarning
"""

from __future__ import annotations

from dataclasses import dataclass, field

MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class Bucket:
    """One minute of traffic: ``total`` requests, ``bad`` of them failed."""

    minute: int
    total: int
    bad: int

    def __post_init__(self) -> None:
        if self.total < 0 or self.bad < 0 or self.bad > self.total:
            raise ValueError(f"invalid bucket: {self!r}")


class EventLog:
    """An append-only, minute-resolution record of requests and failures.

    Buckets must be appended in increasing minute order. Windows are
    trailing: ``ratio(window, now)`` covers minutes ``now - window``
    through ``now - 1``. Minutes with no bucket count as zero traffic,
    which matters for the low-traffic case: a quiet hour must not
    silently shrink the denominator. Prefix sums make window queries
    O(log n) even for a 30-day log evaluated every minute.
    """

    def __init__(self) -> None:
        self.buckets: list[Bucket] = []
        self._minutes: list[int] = []
        self._cum_total: list[int] = [0]
        self._cum_bad: list[int] = [0]

    def append(self, minute: int, total: int, bad: int) -> None:
        bucket = Bucket(minute, total, bad)
        if self._minutes and minute <= self._minutes[-1]:
            raise ValueError("buckets must be appended in increasing minute order")
        self.buckets.append(bucket)
        self._minutes.append(minute)
        self._cum_total.append(self._cum_total[-1] + total)
        self._cum_bad.append(self._cum_bad[-1] + bad)

    def extend(self, start_minute: int, totals: list[int], bads: list[int]) -> None:
        for offset, (total, bad) in enumerate(zip(totals, bads)):
            self.append(start_minute + offset, total, bad)

    def window_totals(self, window_minutes: int, now: int) -> tuple[int, int]:
        """(bad, total) over the trailing window, as a ratio of sums."""
        import bisect

        lo = now - window_minutes
        left = bisect.bisect_left(self._minutes, lo)
        right = bisect.bisect_left(self._minutes, now)
        bad = self._cum_bad[right] - self._cum_bad[left]
        total = self._cum_total[right] - self._cum_total[left]
        return bad, total

    def window_error_rate(self, window_minutes: int, now: int) -> float:
        """Error rate over the trailing window, or 0.0 with no traffic."""
        bad, total = self.window_totals(window_minutes, now)
        return bad / total if total else 0.0

    def average_of_ratios(self, window_minutes: int, now: int) -> float:
        """The wrong way to combine per-minute rates: average of ratios.

        Kept only to demonstrate the trap. A minute with 10 requests and
        10 failures (100%) weighs the same as a minute with 1000 requests
        and 0 failures (0%), so the average says 50% while the true
        error rate is under 1%.
        """
        lo = now - window_minutes
        rates = [
            bucket.bad / bucket.total
            for bucket in self.buckets
            if lo <= bucket.minute < now and bucket.total
        ]
        return sum(rates) / len(rates) if rates else 0.0


def burn_rate(error_rate: float, target: float) -> float:
    """How fast the budget is consumed: error rate / budget rate.

    A burn rate of 1 spends exactly the budget over the SLO window.
    """
    if not 0.0 < target < 1.0:
        raise ValueError("target must be a fraction strictly between 0 and 1")
    return error_rate / (1.0 - target)


def full_outage_budget_minutes(target: float, window_days: int = 30) -> float:
    """Minutes of total outage that exhaust the budget.

    For 99.9% over 30 days: 0.1% of 43,200 minutes = 43.2 minutes.
    """
    return (1.0 - target) * window_days * MINUTES_PER_DAY


def budget_remaining_fraction(
    log: EventLog, target: float, window_days: int = 30, now: int = 0
) -> float:
    """Fraction of the error budget left in the trailing SLO window.

    1.0 means untouched, 0.0 means exactly spent, negative means
    overdrawn. The allowed number of bad events is the budget rate
    times the total events actually seen in the window.
    """
    window_minutes = window_days * MINUTES_PER_DAY
    bad, total = log.window_totals(window_minutes, now)
    allowed = (1.0 - target) * total
    if allowed == 0:
        return 1.0
    return 1.0 - bad / allowed


def budget_balance(
    log: EventLog,
    target: float,
    expected_total_events: int,
    window_days: int = 30,
    now: int = 0,
) -> float:
    """Budget left as a bank balance against the window's expected traffic.

    The rolling-window fraction above is constant under a steady error
    rate, which makes it useless for drawing the budget draining over
    time. Dashboards instead track cumulative bad events against the
    budget the month's *expected* traffic allows:
    ``1 - bad_so_far / ((1 - target) * expected_total)``. At a steady
    burn rate of 1 the balance falls linearly to 0.0 at the end of the
    window; a 20-minute total outage on a 99.9% SLO drops it by
    20 / 43.2 = 46.3% in one step. Say which view a number uses whenever
    you quote it.
    """
    window_minutes = window_days * MINUTES_PER_DAY
    bad, _ = log.window_totals(window_minutes, now)
    allowed = (1.0 - target) * expected_total_events
    return 1.0 - bad / allowed


@dataclass(frozen=True)
class AlertRule:
    """One multiwindow, multi-burn-rate rule (SRE Workbook Table 5-8).

    Fires only when the error rate over BOTH the long window and the
    short window exceeds ``burn`` times the budget rate. The long
    window makes the spend significant; the short window (1/12 of the
    long one) makes the alert stop soon after the errors stop.
    """

    label: str
    long_window_min: int
    short_window_min: int
    burn: float
    severity: str  # "page" or "ticket"

    def __post_init__(self) -> None:
        if self.short_window_min * 12 != self.long_window_min:
            raise ValueError(
                f"{self.label}: short window must be 1/12 of the long window, "
                f"got {self.short_window_min} vs {self.long_window_min}"
            )

    def threshold_rate(self, target: float) -> float:
        return self.burn * (1.0 - target)

    def fires(self, log: EventLog, target: float, now: int) -> bool:
        threshold = self.threshold_rate(target)
        return (
            log.window_error_rate(self.long_window_min, now) > threshold
            and log.window_error_rate(self.short_window_min, now) > threshold
        )


# The SRE Workbook's recommended starting point for a 99.9% SLO
# (Table 5-8): 2% of budget in one hour pages, 5% in six hours pages,
# 10% in three days opens a ticket.
WORKBOOK_RULES_999: tuple[AlertRule, ...] = (
    AlertRule("fast-burn-page", 60, 5, 14.4, "page"),
    AlertRule("medium-burn-page", 360, 30, 6.0, "page"),
    AlertRule("slow-burn-ticket", 4320, 360, 1.0, "ticket"),
)


def evaluate_rules(
    log: EventLog, target: float, now: int, rules: tuple[AlertRule, ...] = WORKBOOK_RULES_999
) -> list[AlertRule]:
    """Rules firing at ``now``, most urgent first (page before ticket)."""
    fired = [rule for rule in rules if rule.fires(log, target, now)]
    fired.sort(key=lambda rule: (0 if rule.severity == "page" else 1, rule.burn))
    return fired


class ForDurationAlert:
    """The naive alert: rate above threshold for ``duration_min`` straight.

    This is what ``for: 1h`` does in Prometheus. One clean minute
    resets the timer, so a service that fails 5 minutes in every 10
    never pages, however much budget the spikes consume.
    """

    def __init__(self, threshold_rate: float, duration_min: int) -> None:
        self.threshold_rate = threshold_rate
        self.duration_min = duration_min

    def fires(self, log: EventLog, now: int) -> bool:
        for minute in range(now - self.duration_min, now):
            bad, total = log.window_totals(1, minute + 1)
            rate = bad / total if total else 0.0
            if rate <= self.threshold_rate:
                return False
        return True


def policy_action(remaining: float) -> str:
    """What the team does, given the fraction of budget remaining.

    The thresholds are the article's policy for the example service:
    above half the budget, ship normally; below half, every release
    needs a tested rollback plan; at or below zero, features freeze
    and the team works reliability until the service is back in budget.
    The workbook's point is that the policy is agreed in advance, by
    the product manager, the development team and the SREs, not
    negotiated during an incident.
    """
    if remaining > 0.5:
        return "ship normally"
    if remaining > 0.0:
        return "every release needs a tested rollback plan"
    return "freeze features; work reliability until back in budget"


def _window_name(minutes: int) -> str:
    """Render a window the way the workbook names recording rules."""
    if minutes % (24 * 60) == 0:
        return f"{minutes // (24 * 60)}d"
    if minutes % 60 == 0:
        return f"{minutes // 60}h"
    return f"{minutes}m"


def generate_prometheus_rules(
    service: str, target: float, window_days: int = 30
) -> str:
    """Render the workbook rules as Prometheus alerting rules.

    The expressions use the recording-rule naming from the workbook
    (``job:slo_errors_per_request:ratio_rate<window>``) with the
    ``<service>`` job substituted. Burn rates and windows are computed
    from :data:`WORKBOOK_RULES_999`, so the generated file cannot drift
    from the table the article prints.
    """
    budget_rate = 1.0 - target
    rate_str = f"{budget_rate:.4g}"  # "0.001", not the float artifact
    lines = [
        "# Generated by slo.py from WORKBOOK_RULES_999.",
        "# Do not edit by hand: regenerate with `python3 slo.py`.",
        f"# SLO: {target:.1%} over {window_days} days, service {service!r}.",
        "groups:",
        "- name: slo-alerts",
        "  rules:",
    ]
    page_rules = [r for r in WORKBOOK_RULES_999 if r.severity == "page"]
    ticket_rules = [r for r in WORKBOOK_RULES_999 if r.severity == "ticket"]
    for group, rules in (("page", page_rules), ("ticket", ticket_rules)):
        conditions = " or ".join(
            f"(\n"
            f"          job:slo_errors_per_request:ratio_rate{_window_name(rule.long_window_min)}"
            f'{{job="{service}"}} > ({rule.burn}*{rate_str})\n'
            f"        and\n"
            f"          job:slo_errors_per_request:ratio_rate{_window_name(rule.short_window_min)}"
            f'{{job="{service}"}} > ({rule.burn}*{rate_str})\n'
            f"        )"
            for rule in rules
        )
        lines += [
            "  - alert: SloBudgetBurn" + ("Page" if group == "page" else "Ticket"),
            f"    expr: {conditions}",
            "    labels:",
            f"      severity: {group}",
            "    annotations:",
            f'      summary: "Error budget burning too fast for {service}"',
        ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Scenario builders: deterministic traffic for the tests and the demo.
# ---------------------------------------------------------------------------


def build_stream(
    minutes: int,
    requests_per_minute: int,
    error_rate: float,
    start_minute: int = 0,
) -> EventLog:
    """A flat stream: the same rate every minute, errors spread evenly."""
    log = EventLog()
    bad_per_minute = int(round(requests_per_minute * error_rate))
    for minute in range(start_minute, start_minute + minutes):
        log.append(minute, requests_per_minute, bad_per_minute)
    return log


def build_with_outage(
    days: int = 30,
    requests_per_minute: int = 1000,
    baseline_error_rate: float = 0.0,
    outage_start_minute: int = 10 * MINUTES_PER_DAY,
    outage_minutes: int = 20,
) -> EventLog:
    """Baseline traffic with one total outage in the middle."""
    log = EventLog()
    total_minutes = days * MINUTES_PER_DAY
    baseline_bad = int(round(requests_per_minute * baseline_error_rate))
    for minute in range(total_minutes):
        if outage_start_minute <= minute < outage_start_minute + outage_minutes:
            log.append(minute, requests_per_minute, requests_per_minute)
        else:
            log.append(minute, requests_per_minute, baseline_bad)
    return log


def build_flapping(
    minutes: int = 30,
    requests_per_minute: int = 1000,
    on_minutes: int = 5,
    off_minutes: int = 5,
) -> EventLog:
    """100% errors for ``on_minutes``, clean for ``off_minutes``, repeating.

    The workbook's Figure 5-3 case: spikes that never trigger a
    ``for:`` alert while consuming a third of the budget.
    """
    log = EventLog()
    cycle = on_minutes + off_minutes
    for minute in range(minutes):
        if minute % cycle < on_minutes:
            log.append(minute, requests_per_minute, requests_per_minute)
        else:
            log.append(minute, requests_per_minute, 0)
    return log


def build_low_traffic(
    hours: int = 24 * 30, requests_per_hour: int = 10, failures: int = 1
) -> EventLog:
    """A quiet service: few requests, so one failure is a large share."""
    log = EventLog()
    for hour in range(hours):
        minute = hour * 60
        log.append(minute, requests_per_hour, failures if hour == 0 else 0)
        for rest in range(1, 60):
            log.append(minute + rest, 0, 0)
    return log


if __name__ == "__main__":
    print(generate_prometheus_rules("checkout", 0.999))
