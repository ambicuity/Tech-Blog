"""Tests for the outbox article. Needs PostgreSQL (OUTBOX_DSN); Kafka is optional
(KAFKA_BOOTSTRAP) and only used by the end-to-end test."""
import json
import os
import random
import time
import uuid
from decimal import Decimal

import psycopg
import pytest
from kafka.errors import KafkaTimeoutError, MessageSizeTooLargeError

import consumer
import outbox

DSN = os.environ["OUTBOX_DSN"]
HERE = os.path.dirname(__file__)


@pytest.fixture
def conn():
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS outbox, orders, order_view")
        c.execute(open(os.path.join(HERE, "schema.sql")).read())
        c.execute(consumer.VIEW_SCHEMA)
        yield c


class Future:
    def __init__(self, error=None):
        self.error = error

    def get(self, timeout=None):
        if self.error:
            raise self.error
        return "ok"


class FakeProducer:
    """Records what was sent; fails the sends whose event type is in fail_types."""

    def __init__(self, fail_types=(), reject_types=()):
        self.sent, self.fail_types, self.reject_types = [], set(fail_types), set(reject_types)

    def send(self, topic, key, value):
        value = json.loads(value)
        if value["type"] in self.reject_types:
            raise MessageSizeTooLargeError("record too large")  # raised by send() itself
        if value["type"] in self.fail_types:
            return Future(KafkaTimeoutError("broker did not acknowledge"))
        self.sent.append((key, value))
        return Future()


def pending(conn):
    return conn.execute("SELECT count(*) FROM outbox WHERE published_at IS NULL").fetchone()[0]


def test_event_is_staged_with_the_data_or_not_at_all(conn):
    order = outbox.place_order(conn, uuid.uuid4(), Decimal("42.50"))
    assert outbox.change_status(conn, order, "paid") == 2
    with pytest.raises(LookupError):
        outbox.change_status(conn, uuid.uuid4(), "paid")  # rolled back: nothing staged
    rows = conn.execute("SELECT aggregate_version, event_type, payload FROM outbox ORDER BY 1").fetchall()
    assert [(v, t) for v, t, _ in rows] == [(1, "OrderPlaced"), (2, "OrderPaid")]
    assert rows[0][2]["total"] == "42.50"  # Decimal survives as an exact string


def test_failed_send_is_not_marked_published(conn):
    order = outbox.place_order(conn, uuid.uuid4(), Decimal("10"))
    outbox.change_status(conn, order, "paid")
    producer = FakeProducer(fail_types={"OrderPaid"})
    assert outbox.relay_batch(conn, producer) == 1
    left = conn.execute("SELECT event_type, attempts, last_error FROM outbox WHERE published_at IS NULL").fetchall()
    assert [(t, a) for t, a, _ in left] == [("OrderPaid", 1)]
    assert "KafkaTimeoutError" in left[0][2]
    assert outbox.relay_batch(conn, FakeProducer()) == 1  # retried later, now acknowledged
    assert pending(conn) == 0


def test_record_rejected_by_send_does_not_block_the_batch(conn):
    bad = outbox.place_order(conn, uuid.uuid4(), Decimal("1"))
    outbox.change_status(conn, bad, "paid")
    outbox.place_order(conn, uuid.uuid4(), Decimal("2"))
    assert outbox.relay_batch(conn, FakeProducer(reject_types={"OrderPaid"})) == 2
    assert conn.execute("SELECT event_type, attempts FROM outbox WHERE published_at IS NULL").fetchall() == [("OrderPaid", 1)]


class HangingFuture:
    def get(self, timeout=None):
        time.sleep(2.5)  # a broker call that ignores its timeout
        return "ok"


class HangingProducer:
    def send(self, topic, key, value):
        return HangingFuture()


def test_hung_broker_call_is_cut_off_and_rows_stay_pending(conn):
    outbox.place_order(conn, uuid.uuid4(), Decimal("3"))
    with psycopg.connect(DSN, autocommit=True) as relay_conn:
        with pytest.raises(outbox.RECONNECT_ERRORS):
            outbox.relay_batch(relay_conn, HangingProducer(), timeout_s=0.5)  # idle limit: 1s
    assert pending(conn) == 1  # rolled back by the server; retried by the next relay


def test_poison_row_stops_after_max_attempts(conn):
    outbox.place_order(conn, uuid.uuid4(), Decimal("1"))
    producer = FakeProducer(fail_types={"OrderPlaced"})
    for _ in range(outbox.MAX_ATTEMPTS + 3):
        outbox.relay_batch(conn, producer)
    assert conn.execute("SELECT attempts FROM outbox").fetchone()[0] == outbox.MAX_ATTEMPTS


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


def test_events_for_one_order_are_sent_in_version_order(conn):
    orders = [outbox.place_order(conn, uuid.uuid4(), Decimal("5")) for _ in range(3)]
    for o in orders:
        outbox.change_status(conn, o, "paid")
        outbox.change_status(conn, o, "shipped")
    producer = FakeProducer()
    outbox.relay_batch(conn, producer)
    for o in orders:
        versions = [v["version"] for k, v in producer.sent if k == str(o).encode()]
        assert versions == [1, 2, 3]


@pytest.mark.skipif("KAFKA_BOOTSTRAP" not in os.environ, reason="needs a Kafka broker")
def test_end_to_end_with_kafka(conn):
    from kafka import KafkaConsumer

    topic = f"orders.events.{uuid.uuid4().hex[:8]}"
    order = outbox.place_order(conn, uuid.uuid4(), Decimal("12.34"))
    outbox.change_status(conn, order, "paid")
    producer = outbox.make_producer(os.environ["KAFKA_BOOTSTRAP"])
    assert outbox.relay_batch(conn, producer, topic=topic) == 2
    assert pending(conn) == 0

    reader = KafkaConsumer(topic, bootstrap_servers=os.environ["KAFKA_BOOTSTRAP"],
                           auto_offset_reset="earliest", consumer_timeout_ms=10000)
    events = [json.loads(m.value) for m in reader]
    reader.close()
    assert [e["version"] for e in events] == [1, 2]
    for event in events:
        consumer.apply_event(conn, event)
    assert conn.execute("SELECT status, total FROM order_view").fetchone() == ("paid", Decimal("12.34"))
