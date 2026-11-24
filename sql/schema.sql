CREATE TABLE IF NOT EXISTS ihsg_daily(
    trade_date DATE PRIMARY KEY,
    open NUMERIC(18,4),
    high NUMERIC(18,4),
    low NUMERIC(18,4),
    close NUMERIC(18,4),
    volume BIGINT,
    ingested_at_utc TIMESTAMPTZ
);


CREATE TABLE IF NOT EXISTS bi_jisdor(
    rate_date DATE,
    currency VARCHAR(10),
    buy_rate NUMERIC(18,6),
    sell_rate NUMERIC(18,6),
    ingested_at_utc TIMESTAMPTZ,
    PRIMARY KEY (rate_date, currency)
);

CREATE TABLE IF NOT EXISTS cnn_articles(
    guid TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    pub_date_raw TEXT,
    published_utc TIMESTAMPTZ,
    ingested_at_utc TIMESTAMPTZ
);
