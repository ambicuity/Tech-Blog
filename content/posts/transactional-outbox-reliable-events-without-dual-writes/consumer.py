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
