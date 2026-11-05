"""Demo: one month of checkout traffic, three incidents, one SLO.

Simulates 30 days at 10,000 requests/minute with a 99.9% SLO, a 0.05%
baseline error rate, and three incidents:

* day 10: a 20-minute total outage,
* day 20: a bad deploy that holds a 0.35% error rate for 6 hours,
* day 25: flapping 100% error spikes, 5 minutes on, 5 off, for 30 minutes.

Prints the budget balance at each day boundary, the policy action it
implies, and the first minute each alert rule fires for each incident.
Run:  python3 demo.py
"""

from slo import (
    MINUTES_PER_DAY,
    WORKBOOK_RULES_999,
    EventLog,
    budget_balance,
    budget_remaining_fraction,
    evaluate_rules,
    policy_action,
)

TARGET = 0.999
RPM = 10_000  # 10,000/min so a 0.05% baseline is a whole 5 bad/min
DAYS = 30
EXPECTED_TOTAL = RPM * DAYS * MINUTES_PER_DAY


def build_month() -> EventLog:
    log = EventLog()
    baseline_bad = int(round(RPM * 0.0005))  # 0.05% baseline errors
    for minute in range(DAYS * MINUTES_PER_DAY):
        day = minute // MINUTES_PER_DAY
        in_day = minute % MINUTES_PER_DAY
        if day == 9 and 720 <= in_day < 740:
            bad = RPM  # day 10: total outage, 12:00-12:20
        elif day == 19 and 480 <= in_day < 840:
            bad = int(round(RPM * 0.0035))  # day 20: 6h slow burn
        elif day == 24 and 600 <= in_day < 630 and (in_day - 600) % 10 < 5:
            bad = RPM  # day 25: flapping spikes
        else:
            bad = baseline_bad
        log.append(minute, RPM, bad)
    return log


def first_firing_minutes(log: EventLog, start: int, end: int) -> dict[str, int]:
    """First minute each rule fires in [start, end), or -1 if never."""
    first: dict[str, int] = {}
    for minute in range(start, end):
        for rule in evaluate_rules(log, TARGET, minute):
            first.setdefault(rule.label, minute)
    return first


def main() -> None:
    log = build_month()
    print("checkout, 99.9% SLO over 30 days, 10,000 req/min, 0.05% baseline")
    print("day  balance  policy")
    for day in range(DAYS + 1):
        now = day * MINUTES_PER_DAY
        balance = budget_balance(log, TARGET, EXPECTED_TOTAL, now=now)
        print(f"{day:3d}  {balance:7.1%}  {policy_action(balance)}")
    print()
    print("incidents: first minute each alert rule fires (minutes from 00:00)")
    for label, (day, start, end) in {
        "day-10 outage (20 min, 100% errors)": (9, 9 * MINUTES_PER_DAY + 720, 9 * MINUTES_PER_DAY + 900),
        "day-20 slow burn (6 h, 0.35% errors)": (19, 19 * MINUTES_PER_DAY + 480, 19 * MINUTES_PER_DAY + 900),
        "day-25 flapping spikes (30 min)": (24, 24 * MINUTES_PER_DAY + 600, 24 * MINUTES_PER_DAY + 700),
    }.items():
        fired = first_firing_minutes(log, start, end)
        print(f"  {label}")
        for rule in WORKBOOK_RULES_999:
            minute = fired.get(rule.label)
            if minute is None:
                print(f"    {rule.label}: never")
            else:
                print(
                    f"    {rule.label}: {minute - start} min into the incident "
                    f"({rule.severity})"
                )
    print()
    print(
        "rolling 30-day budget remaining at month end: "
        f"{budget_remaining_fraction(log, TARGET, now=DAYS * MINUTES_PER_DAY):.1%}"
    )


if __name__ == "__main__":
    main()
