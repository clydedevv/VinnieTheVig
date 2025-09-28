-- Base tables for market data and research
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE polymarket_odds (
    market_id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
    image TEXT,
    icon TEXT,
    outcomes JSONB NOT NULL,
    outcome_prices JSONB NOT NULL,
    volume NUMERIC DEFAULT 0,
    volume_24h NUMERIC DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    closed BOOLEAN DEFAULT FALSE,
    liquidity NUMERIC DEFAULT 0,
    end_date TIMESTAMPTZ NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    market_slug TEXT UNIQUE,
    clob_token_ids JSONB,
    resolution_source TEXT,
    last_trade_price NUMERIC,
    best_bid NUMERIC,
    best_ask NUMERIC,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Research schema (based on Ankur's proposal)
CREATE TABLE research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market_id TEXT REFERENCES polymarket_odds(market_id),
    title TEXT NOT NULL,
    description TEXT,
    keywords JSONB,
    source_url TEXT,
    authors JSONB,
    publication_date TIMESTAMP,
    organization TEXT,
    category TEXT,
    raw_text TEXT,
    citations JSONB,
    ai_generated_summary TEXT,
    last_updated TIMESTAMP DEFAULT now()
);

CREATE TABLE analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_id UUID NOT NULL REFERENCES research(id) ON DELETE CASCADE,
    market_id TEXT REFERENCES polymarket_odds(market_id),
    analyst TEXT,
    analysis_type TEXT CHECK (analysis_type IN ('NLP Summary', 'Statistical Breakdown', 'Comparative Study')),
    insights JSONB,
    created_at TIMESTAMP DEFAULT now(),
    last_updated TIMESTAMP DEFAULT now()
);

CREATE TABLE conclusions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    market_id TEXT REFERENCES polymarket_odds(market_id),
    conclusion_text TEXT NOT NULL,
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    supporting_evidence JSONB,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- User management
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    twitter_handle TEXT UNIQUE,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    chain TEXT CHECK (chain IN ('EVM', 'Cosmos', 'Solana')),
    address TEXT UNIQUE NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_polymarket_end_date ON polymarket_odds(end_date);
CREATE INDEX idx_polymarket_active ON polymarket_odds(active);
CREATE INDEX idx_polymarket_category ON polymarket_odds(category_id);
CREATE INDEX idx_research_market ON research(market_id);
CREATE INDEX idx_analysis_market ON analysis(market_id);
CREATE INDEX idx_conclusions_market ON conclusions(market_id); 