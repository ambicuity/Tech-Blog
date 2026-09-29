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
