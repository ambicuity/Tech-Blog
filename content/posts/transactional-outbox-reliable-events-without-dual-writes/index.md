---
title: "Transactional Outbox: Reliable Events Without Dual Writes"
description: >-
  A database commit and a Kafka publish cannot share a transaction. How the
  transactional outbox closes that gap, with tested code, ordering and dedupe.
date: 2026-09-29 03:18:23 +0000
updated: 2026-09-29 15:11:57 +0000
author: ritesh
categories: [Distributed Systems, Reliability]
tags: [outbox-pattern, event-driven, postgresql, kafka, microservices]
kind: Guide
draft: false
cover:
  image: cover.webp
  alt: Database holding orders and outbox tables, a relay gear, and a broker with event queues showing the flow.
---

Your service takes an order: it inserts a row into the `orders` table and publishes an `OrderPlaced` event so the warehouse, billing and notification services can react. Two writes, two systems, and no transaction that spans both. If the database commit succeeds but the publish fails, downstream services never hear about the order. If the publish succeeds but the commit rolls back, they react to an order that does not exist.

The transactional outbox solves this structurally: write the event into an `outbox` table in the same database transaction as the order, then let a separate relay deliver it to the broker. The hard part is not the table. It is the relay: getting it wrong quietly loses events, reorders them, or leaves consumers unable to tell a duplicate from a new event. This article builds one that gets those details right, and tests it against PostgreSQL 16 and Kafka 4.3.

> [!NOTE]
> **In short**
> - Write the event row in the same transaction as the business row. An event then exists exactly when the data does.
> - Mark a row published only after the broker acknowledged *that record*. `flush()` does not tell you.
> - Delivery is at-least-once. Every event carries a stable `event_id` for deduplication and a per-aggregate `version` for ordering.
> - Run one active relay per outbox (an advisory lock does this), or you give up per-aggregate ordering.
> - Watch the age of the oldest pending row, and delete published rows on a schedule.

## The dual-write problem

A relational database and a message broker cannot join the same transaction in any practical setup. Two-phase commit across heterogeneous systems is slow and fragile, and Kafka does not take part in XA transactions at all. So every real system performs the two writes separately, and separately means one can fail while the other succeeds.

The failure modes are mirror images:

| Order of writes | Failure | Result |
| :--- | :--- | :--- |
| Commit, then publish | Crash or network error between the two | Event lost; downstream never reacts |
| Publish, then commit | Rollback after a successful publish | Ghost event; downstream reacts to nothing |

> [!WARNING]
> "Publish first, then commit" does not merely risk duplicates: it creates events for state that never existed. Downstream services cannot distinguish a ghost event from a real one.

Retrying the failed half narrows the window but never closes it: a crash can always land between the two writes. The fix is to stop doing two writes and do one, then deliver the second as a consequence of the first.

## How the outbox closes the gap

The service commits the order and its event row together. A relay then moves committed events to Kafka, and only records a row as published once the broker has acknowledged it. The one remaining crash window, after the broker acknowledged but before the rows were marked, produces a duplicate, never a loss:

![An order row and its outbox row are committed in one transaction. The relay locks the pending outbox row, sends the event to Kafka keyed by order ID so it lands in partition p1, waits for the broker to acknowledge that record, and only then marks the row sent. A crash before that last step sends the event again; it never loses it.](outbox-flow.svg "The relay's five steps. Until step 5 the row stays pending, so a crash can only cause a resend."){: .figure}

## The outbox table

```sql
CREATE TABLE orders (
    id          uuid PRIMARY KEY,
    customer_id uuid NOT NULL,
    status      text NOT NULL,
    total       numeric(12, 2) NOT NULL,
    version     integer NOT NULL
);

CREATE TABLE outbox (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate         text NOT NULL,
    aggregate_id      uuid NOT NULL,
    aggregate_version integer NOT NULL,
    event_type        text NOT NULL,
    payload           jsonb NOT NULL,
    created_at        timestamptz NOT NULL DEFAULT now(),
    published_at      timestamptz,
    attempts          integer NOT NULL DEFAULT 0,
    last_error        text,
    UNIQUE (aggregate, aggregate_id, aggregate_version)
);

CREATE INDEX outbox_pending_idx
    ON outbox (aggregate_id, aggregate_version)
    WHERE published_at IS NULL;
```

- `id` is the event's identity. It travels with the message as `event_id`, and it is what consumers deduplicate on. (`gen_random_uuid()` is built into PostgreSQL 13 and later.)
- `aggregate_id` and `aggregate_version` identify the order and the position of this event in that order's history. The unique constraint makes a duplicate version impossible.
- `attempts` and `last_error` let the relay give up on a row the broker keeps rejecting instead of retrying it forever.
- The partial index covers only pending rows, so the relay's query stays fast no matter how much published history accumulates.

## Writing events with the data

The application writes the event in the same transaction as the change it describes:

```python
def _stage(conn, order_id, version, event_type, state):
    conn.execute(
        """
        INSERT INTO outbox (aggregate, aggregate_id, aggregate_version, event_type, payload)
        VALUES ('order', %s, %s, %s, %s)
        """,
        (order_id, version, event_type, Jsonb(state)),
    )


def place_order(conn, customer_id: uuid.UUID, total: Decimal) -> uuid.UUID:
    order_id = uuid.uuid4()
    with conn.transaction():
        conn.execute(
            "INSERT INTO orders (id, customer_id, status, total, version)"
            " VALUES (%s, %s, 'placed', %s, 1)",
            (order_id, customer_id, total),
        )
        _stage(conn, order_id, 1, "OrderPlaced", {
            "order_id": str(order_id), "customer_id": str(customer_id),
            "status": "placed", "total": str(total),
        })
    return order_id


def change_status(conn, order_id: uuid.UUID, status: str) -> int:
    with conn.transaction():
        # The row lock taken by UPDATE serializes writers of this order, so
        # version N+1 can only commit after version N.
        row = conn.execute(
            "UPDATE orders SET status = %s, version = version + 1"
            " WHERE id = %s RETURNING customer_id, total, version",
            (status, order_id),
        ).fetchone()
        if row is None:
            raise LookupError(f"order {order_id} not found")
        customer_id, total, version = row
        _stage(conn, order_id, version, f"Order{status.capitalize()}", {
            "order_id": str(order_id), "customer_id": str(customer_id),
            "status": status, "total": str(total),
        })
    return version
```

Three details matter here.

**The version comes from the row lock, not the clock.** It is tempting to order events by `created_at`, but `now()` in PostgreSQL returns the time the *transaction started*, not when it committed. Two concurrent transactions can commit in the opposite order of their timestamps, and a relay polling by `created_at` would then publish them in the wrong order. `UPDATE … SET version = version + 1` takes the order's row lock, so the transaction for version 3 cannot commit until version 2 has. Any snapshot that sees version 3 also sees version 2.

**The payload is the full state, not a diff.** Each event says "this order is now *paid*, total 42.50", rather than "status changed". A consumer that receives versions out of order, or twice, can still converge on the right state by keeping the highest version it has seen.

**Money stays exact.** `json.dumps` cannot serialize `Decimal`, and converting to `float` loses cents. The total travels as a string, `"42.50"`.

## The event on the wire

The relay wraps each row in an envelope. Two fields do the heavy lifting: `event_id` identifies a delivery for deduplication, and `version` orders events within one order.

```python
def envelope(row) -> dict:
    event_id, aggregate, aggregate_id, version, event_type, payload, created_at = row
    return {
        "event_id": str(event_id),  # stable across redeliveries: the dedupe key
        "type": event_type,
        "aggregate": aggregate,
        "aggregate_id": str(aggregate_id),
        "version": version,         # per-order sequence: the ordering key
        "occurred_at": created_at.isoformat(),
        "data": payload,
    }
```

## The relay

```python
def make_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        acks="all",               # wait for all in-sync replicas
        enable_idempotence=True,  # retries cannot duplicate or reorder within a partition
    )


def relay_batch(conn, producer, topic="orders.events", batch_size=100, timeout_s=10.0) -> int:
    """Publish up to batch_size pending events; return how many the broker acknowledged."""
    with conn.transaction():
        # Row locks are held while we wait for the broker. If this session ever sits
        # idle that long, PostgreSQL ends it: the rows stay pending and are retried.
        conn.execute(
            "SELECT set_config('idle_in_transaction_session_timeout', %s, true)",
            (f"{int(timeout_s * 3)}s",),
        )
        rows = conn.execute(
            """
            SELECT id, aggregate, aggregate_id, aggregate_version, event_type, payload, created_at
            FROM outbox
            WHERE published_at IS NULL AND attempts < %s
            ORDER BY aggregate_id, aggregate_version
            LIMIT %s
            FOR UPDATE SKIP LOCKED
            """,
            (MAX_ATTEMPTS, batch_size),
        ).fetchall()

        acked, failed, sends = [], [], []
        for row in rows:
            try:
                value = json.dumps(envelope(row)).encode()
                sends.append((row[0], producer.send(topic, key=str(row[2]).encode(), value=value)))
            except KafkaError as exc:  # rejected before sending, e.g. record too large
                failed.append((row[0], repr(exc)[:500]))

        deadline = time.monotonic() + timeout_s
        for event_id, future in sends:
            try:
                # flush() would not raise for a failed record; the future does.
                future.get(timeout=max(0.0, deadline - time.monotonic()))
                acked.append(event_id)
            except KafkaError as exc:
                failed.append((event_id, repr(exc)[:500]))

        if acked:
            conn.execute("UPDATE outbox SET published_at = now() WHERE id = ANY(%s)", (acked,))
        for event_id, error in failed:
            conn.execute(
                "UPDATE outbox SET attempts = attempts + 1, last_error = %s WHERE id = %s",
                (error, event_id),
            )
    return len(acked)
```

Every line of this function exists because of a failure the naive version has:

- **Check each record's result.** The obvious relay calls `producer.flush()` and then marks the whole batch published. But kafka-python's `flush()` returns once each request is "successfully acknowledged … or it results in an error": it does not raise. Against a Kafka 4.3 broker, a record rejected by the topic's `max.message.bytes` left `flush()` returning normally while that record's `future.get()` raised `MessageSizeTooLargeError`. Mark rows based on `flush()` alone and that event is silently gone.
- **`send()` can fail before it sends.** A record larger than the producer's `max_request_size` makes `send()` itself raise. Without the `try` around it, one oversized row aborts the batch's transaction on every run and blocks every event behind it.
- **The wait is bounded.** All acknowledgements share one deadline, so a slow broker cannot hold the row locks indefinitely.
- **There is a backstop.** Row locks are held while the relay waits for the broker. `idle_in_transaction_session_timeout` (set only for this transaction) makes PostgreSQL end the session if it ever sits idle three times longer than the deadline, for example if the process freezes. The rows then roll back to pending, and the next relay picks them up.
- **Poison rows stop.** A row the broker keeps rejecting is retried `MAX_ATTEMPTS` times, then left for a human, with the error recorded in `last_error`.
- **The producer is configured for ordering.** Kafka's producer documentation warns that with more than one in-flight request and idempotence disabled, "there is a risk of message reordering after a failed send due to retries". `enable_idempotence=True` and `acks="all"` remove that risk. They are kafka-python 3's defaults; setting them explicitly keeps the guarantee from depending on a library default.

> [!IMPORTANT]
> The relay delivers at-least-once, never exactly-once. A crash after the broker acknowledged but before the `UPDATE` sends the same events again. Consumers must tolerate duplicates; the consumer below does, and [Idempotent Operations in Distributed Systems](/posts/idempotent-operations-in-distributed-systems-a-practical-guide/) covers the general technique.

### Run exactly one active relay

```python
def run_relay(dsn: str, bootstrap_servers: str, idle_sleep_s: float = 1.0) -> None:
    """Relay forever. Many copies may run; one holds the lock and works, the rest wait."""
    producer = make_producer(bootstrap_servers)
    while True:
        try:
            with psycopg.connect(dsn) as conn:
                conn.autocommit = True  # each relay_batch() manages its own transaction
                # A session-level advisory lock makes this the only active relay, which
                # keeps each order's events in version order. It is released if we die.
                lock = "SELECT pg_try_advisory_lock(hashtext('outbox-relay'))"
                if not conn.execute(lock).fetchone()[0]:
                    time.sleep(idle_sleep_s * 5)
                    continue
                while True:
                    if relay_batch(conn, producer) == 0:
                        time.sleep(idle_sleep_s)
        except RECONNECT_ERRORS:
            time.sleep(idle_sleep_s)
```

`FOR UPDATE SKIP LOCKED` lets several relays poll the same table without blocking each other, which is tempting for throughput. It also destroys ordering: two relays can pick up versions 2 and 3 of the same order and publish them in either order. The advisory lock makes one relay active and the others standbys. If the active one dies, its connection closes, the lock is released, and a standby takes over within seconds. Kafka then preserves order within a partition, and keying every record by `aggregate_id` puts all of an order's events in the same partition. The same idea applies to queues: SQS FIFO queues use [message groups](/posts/leveraging-aws-sqs-message-groups-for-ordered-processing/) for it.

If one relay cannot keep up, shard rather than share: run N relays, each owning the orders where `abs(hashtext(aggregate_id::text)) % N` equals its shard number (add that condition to the relay's query), each with its own advisory lock.

## A consumer that survives duplicates and reordering

```python
"""A consumer that tolerates duplicates and out-of-order events."""

VIEW_SCHEMA = """
CREATE TABLE order_view (
    order_id uuid PRIMARY KEY,
    status   text NOT NULL,
    total    numeric(12, 2) NOT NULL,
    version  integer NOT NULL
);
"""


def apply_event(conn, event: dict) -> bool:
    """Apply an order event. Returns False for duplicates and stale versions."""
    data = event["data"]
    with conn.transaction():
        cur = conn.execute(
            """
            INSERT INTO order_view (order_id, status, total, version)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id) DO UPDATE
                SET status = EXCLUDED.status, total = EXCLUDED.total, version = EXCLUDED.version
                WHERE order_view.version < EXCLUDED.version
            """,
            (event["aggregate_id"], data["status"], data["total"], event["version"]),
        )
    return cur.rowcount == 1
```

The `WHERE order_view.version < EXCLUDED.version` clause is the whole trick. A duplicate carries a version the view already has, so the update does nothing. An old event arriving after a newer one carries a lower version, so it also does nothing. The view converges on the latest state no matter how many times or in what order events arrive.

## Proving it

The complete code and tests are next to this article: [schema.sql](schema.sql), [outbox.py](outbox.py), [consumer.py](consumer.py) and [test_outbox.py](test_outbox.py). They were run against PostgreSQL 16.15 and a single-node Kafka 4.3.1 broker (KRaft), with Python 3.14, psycopg 3.3.6 and kafka-python 3.0.11.

The test that matters most kills the relay in its crash window, after the broker acknowledged and before the rows were marked:

```python
def test_crash_after_publish_redelivers_and_consumer_converges(conn):
    order = outbox.place_order(conn, uuid.uuid4(), Decimal("99.99"))
    outbox.change_status(conn, order, "paid")
    outbox.change_status(conn, order, "shipped")

    # Crash after the broker acknowledged but before the rows were marked:
    # the transaction rolls back, so every event is sent again.
    first = FakeProducer()
    real_update = conn.execute

    def crash_on_mark(query, *args, **kwargs):
        if query.startswith("UPDATE outbox SET published_at"):
            raise RuntimeError("relay killed")
        return real_update(query, *args, **kwargs)

    conn.execute = crash_on_mark
    with pytest.raises(RuntimeError):
        outbox.relay_batch(conn, first)
    conn.execute = real_update
    assert pending(conn) == 3

    second = FakeProducer()
    assert outbox.relay_batch(conn, second) == 3
    delivered = [value for _, value in first.sent + second.sent]
    assert len(delivered) == 6  # every event twice
    assert len({e["event_id"] for e in delivered}) == 3  # but only three distinct events

    random.seed(7)
    random.shuffle(delivered)  # duplicates, in any order
    for event in delivered:
        consumer.apply_event(conn, json.loads(json.dumps(event)))
    status, version = conn.execute("SELECT status, version FROM order_view").fetchone()
    assert (status, version) == ("shipped", 3)
```

It produces six deliveries of three events, shuffles them, and the consumer still ends with the order *shipped* at version 3. The other tests cover a record the broker rejects (stays pending with `attempts = 1`, then succeeds on retry), a record `send()` refuses (does not block the rest of the batch), a poison row (stops at `MAX_ATTEMPTS`), a broker call that hangs (PostgreSQL ends the transaction and the row stays pending), and an end-to-end run through a real broker.

```bash
OUTBOX_DSN="dbname=outbox_test" KAFKA_BOOTSTRAP=localhost:9092 pytest test_outbox.py
```

## Operating the relay

**Watch the lag.** The number to alert on is the age of the oldest pending row: it grows when the relay is down, stuck or too slow, whatever the cause.

```sql
SELECT count(*) FILTER (WHERE attempts < 10)  AS pending,
       count(*) FILTER (WHERE attempts >= 10) AS stuck,
       coalesce(extract(epoch FROM now() - min(created_at) FILTER (WHERE attempts < 10)), 0)
           AS oldest_pending_seconds
FROM outbox
WHERE published_at IS NULL;
```

Export these three values as gauges. A reasonable starting point is to page when `oldest_pending_seconds` stays above a few minutes and to open a ticket whenever `stuck` is above zero; tune both to how quickly your consumers need events.

**Delete published rows in batches.** The outbox is a queue, not an archive. A scheduled job keeps it small without long-running deletes:

```sql
DELETE FROM outbox
WHERE id IN (SELECT id FROM outbox
             WHERE published_at < now() - interval '7 days'
             LIMIT 10000);
```

Keep rows only as long as you might need to replay them; if consumers rebuild read models from history, archive instead of delete. At high volume, partition the table by day and drop old partitions instead: dropping a partition is instant and leaves nothing for `VACUUM` to clean.

**Mind long transactions.** The relay's transaction is short by design, but anything that holds a transaction open on this database keeps `VACUUM` from reclaiming dead outbox rows, and a busy outbox produces them constantly. Watch `pg_stat_activity` for old `xact_start` values.

## Log tailing instead of polling

Instead of polling, a change-data-capture connector can tail PostgreSQL's write-ahead log and stream committed outbox rows to Kafka with lower latency and no polling queries. [Debezium's Outbox Event Router](https://debezium.io/documentation/reference/transformations/outbox-event-router.html) is built for exactly this table. The trade-off is operational: you run a Kafka Connect cluster and a replication slot, and a stalled slot makes PostgreSQL retain WAL until it catches up. The application side does not change: commit the event row, and it will be delivered. Teams can start with the polling relay and move to log tailing later.

## When not to use an outbox

| Situation | Better choice |
| :--- | :--- |
| The source of truth is Kafka itself (consume, transform, produce) | Kafka transactions: consumed offsets and produced records commit atomically |
| Consumers only need the current state, not events | Change-data-capture on the business tables, or an API they call |
| Every state change is already stored as an event | Event sourcing: the event log is the data |
| One service owns both the write and the reaction | Do the work in the same transaction; no event needed |

## Checklist

- [ ] The event row is written in the same transaction as the data it describes.
- [ ] Rows are marked published only after that record's acknowledgement, never after `flush()` alone.
- [ ] `send()` failures and acknowledgement failures are recorded per row, with a retry limit.
- [ ] Each message carries a stable event ID and a per-aggregate version.
- [ ] Messages are keyed by aggregate ID; the producer uses `acks="all"` and idempotence.
- [ ] Exactly one relay is active per outbox (or per shard).
- [ ] Consumers deduplicate and ignore stale versions.
- [ ] Alerts exist on the age of the oldest pending row and on stuck rows; published rows are deleted on a schedule.

## References

- Chris Richardson, [Pattern: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html), *microservices.io*
- PostgreSQL documentation, [Date/time functions (`now()` is the transaction start time)](https://www.postgresql.org/docs/current/functions-datetime.html)
- PostgreSQL documentation, [The locking clause (`FOR UPDATE … SKIP LOCKED`)](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)
- PostgreSQL documentation, [Advisory lock functions](https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS)
- PostgreSQL documentation, [`idle_in_transaction_session_timeout`](https://www.postgresql.org/docs/current/runtime-config-client.html)
- PostgreSQL documentation, [`INSERT … ON CONFLICT`](https://www.postgresql.org/docs/current/sql-insert.html)
- Apache Kafka documentation, [Producer configs (`max.in.flight.requests.per.connection`, `enable.idempotence`)](https://kafka.apache.org/documentation/#producerconfigs)
- kafka-python, [KafkaProducer API (`send`, `flush`)](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html)
- Debezium documentation, [Outbox Event Router](https://debezium.io/documentation/reference/transformations/outbox-event-router.html)
