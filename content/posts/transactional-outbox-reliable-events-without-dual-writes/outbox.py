"""Transactional outbox: stage events with the data, relay them to Kafka."""
import json
import time
import uuid
from decimal import Decimal

import psycopg
from kafka import KafkaProducer
from kafka.errors import KafkaError
from psycopg.types.json import Jsonb

MAX_ATTEMPTS = 10  # after this, a row stops being retried and needs a human
# Errors after which the relay reconnects and carries on. The idle-transaction
# timeout is an InternalError in psycopg, not an OperationalError.
RECONNECT_ERRORS = (psycopg.OperationalError, psycopg.errors.IdleInTransactionSessionTimeout)


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
            time.sleep(idle_sleep_s)  # database restart or idle timeout: reconnect
