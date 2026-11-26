CREATE TABLE IF NOT EXISTS ihsg_daily(
    trade_date DATE PRIMARY KEY,
    open NUMERIC(18,4) NOT NULL CHECK (open > 0),
    high NUMERIC(18,4) NOT NULL CHECK (high > 0),
    low NUMERIC(18,4) NOT NULL CHECK (low > 0),
    close NUMERIC(18,4) NOT NULL CHECK (close > 0),
    volume BIGINT,
    ingested_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE TABLE IF NOT EXISTS bi_jisdor(
    rate_date DATE,
    currency VARCHAR(10),
    buy_rate NUMERIC(18,6) NOT NULL CHECK (buy_rate > 0),
    sell_rate NUMERIC(18,6) NOT NULL CHECK (sell_rate > 0),
    ingested_at_utc TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (rate_date, currency)
);

CREATE TABLE IF NOT EXISTS cnn_articles(
    guid TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    pub_date_raw TEXT,
    published_utc TIMESTAMPTZ,
    ingested_at_utc TIMESTAMPTZ NOT NULL DEFAULT now()
);
