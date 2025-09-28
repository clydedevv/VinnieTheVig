# AIGG - A Polymarket Companion

## Introduction

AIGG lets anyone ask a market question on Twitter and get a concise answer they can act on: a one-paragraph rationale, a clear BUY/SELL/HOLD with confidence, and the exact Polymarket link.

## The Problem We're Tackling

Prediction markets are having a moment. Crypto Twitter and mainstream outlets are paying attention, especially when volatility spikes. But attention and capital are scattered across thousands of tokens and feeds.

- Discovery is noisy
- Naming is inconsistent
- Timing matters

Most people either can't find the right market quickly or don't have the time to research it. Generic bots make this worse by producing vague text that doesn't help you trade.

## The Solution

AIGG is a Twitter-native companion for Polymarket. Mention @aigginsights with a question and it does the heavy lifting: it identifies the correct market, adds current context when needed, and replies with a short, opinionated take and a confidence number; plus the official link that opens the market.

- If you have domain expertise, AIGG accelerates you
- If you don't, it gives you a usable starting point instead of sending you down a research rabbit hole

## Live Examples

### Bitcoin Market Query
```
@user: "Will Bitcoin reach 200k?"
@aigginsights: "Word is Bitcoin's struggling below $110K after brutal selloffs.
Smart money's laying action on NO with Fed tightening. (85% confidence)

BUY NO

https://polymarket.com/event/bitcoin-200k-2025"
```

### Fed Rates Query
```
@user: "Fed cutting rates?"
@aigginsights: "Word is the Fed already dropped rates in July and Powell's
signaling more cuts. Smart money's leaning hard on YES. (90% confidence)

BUY YES

https://polymarket.com/event/will-1-fed-rate-cut-happen-in-2025"
```

## Key Innovations

AIGG stands on three pillars:

### 1. Custom, Clean Market Index
We ingest Polymarket's corpus and maintain an "active only" index. From 114,450 total markets, we automatically remove expired and inactive ones daily, leaving about 6,991 active markets (a 94% reduction). This makes search roughly 10× faster and keeps results relevant. Live searches resolve in under a second.

### 2. AI Matcher That Understands Real Questions
We combine fuzzy matching (handles typos and phrasing) with semantic matching (understands meaning and entities). Candidates are ranked by relevance, recency, and market status, then validated against the official Polymarket slug so links always work. When several candidates are close, AIGG runs a quick research pass and selects the best of the top ten.

### 3. Structured, Professional Replies
Answers follow a consistent shape: what matters now, the stance (BUY/SELL/HOLD), a confidence percentage, and the exact link. Responses respect Twitter's character limit without cutting sentences, so the message stays readable and complete.

Under the hood, we use an LLM-guided pipeline and DSPy-style prompting to enforce structure and consistency. A lightweight research step (e.g., Perplexity Sonar) is triggered only for time-sensitive topics to keep latency and costs predictable.

## How It Works

You mention @aigginsights with a question: "BTC at 200k in 2025?" or "Ukraine-Russia ceasefire before July?"

1. **Parse & Normalize**: AiGG parses the intent, normalizes entities and dates, and queries the active index
2. **Match & Verify**: The matcher returns high-confidence candidates and verifies the official slug to guarantee a correct link
3. **Research & Analyze**: If the topic is moving fast, AiGG pulls fresh public context
4. **Synthesize & Reply**: Creates a tight paragraph that surfaces key drivers (policy, flows, deadlines, technical levels, diplomatic constraints), adds a clear stance with confidence, and replies with the full Polymarket URL

End-to-end, the flow typically completes in 30-90 seconds.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TWITTER BOT   │───>│ WRAPPER API     │───>│  MARKET API     │
│   (Monitor)     │    │  (Analysis)     │    │  (Database)     │
│   Port: N/A     │    │  Port: 8003     │    │  Port: 8001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    Twitter API            DSPy + Perplexity       PostgreSQL DB
   (Mentions/Replies)      (AI Analysis)         (114,450 markets)
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/zeroth-tech/aigg-insights.git
cd aigg-insights

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add API keys: FIREWORKS_API_KEY, PERPLEXITY_API_KEY, TWITTER_*

# Initialize database
python main.py database init
python main.py database load-markets

# Test analysis
python main.py analyze "Will Bitcoin reach 200k?"

# Start services
python main.py api-server --port 8001
python main.py wrapper-api --port 8003
python main.py twitter-bot --interval 30
```

## Performance Metrics

| Component | Latency | Description |
|-----------|---------|-------------|
| Market Matching | 1-3s | Semantic search across 114K markets |
| Research | 5-10s | Real-time context gathering |
| Analysis | 3-5s | DSPy structured generation |
| Total Response | 30-90s | End-to-end from mention to reply |

## Future Vision

As attention and capital fragment across thousands of tokens, traders are shifting toward venues where information edges matter more than access edges. Adoption is compounding: Polymarket and Kalshi keep growing users, volume, and mindshare, while web2 platforms (DraftKings, FanDuel, Underdog) chase adjacent demand.

There's still some friction: liquidity is thin, discovery is clunky, and pricing is fragmented. AIGG helps turn that fragmentation into opportunity.

By matching users to the right market, adding timely context, and giving a clear, link-backed stance, it reduces discovery cost and speeds up decision-making.

Pair AIGG with emerging aggregators and market-making vaults, and you get a practical path to better routing, fewer mispricings, and more confident participation in prediction markets.

## Documentation

- [What is AIGG?](getting-started/what-is-aigg.md) - Deep technical overview
- [Quick Start](getting-started/quick-start.md) - Setup instructions
- [System Architecture](architecture/system-overview.md) - Infrastructure details
- [Deployment Guide](deployment/deployment-guide.md) - Production deployment
- [AI Pipeline](ai-pipeline/analysis-pipeline.md) - How insights are generated
- [Product Roadmap](roadmap/product-roadmap.md) - Future platform vision

## Resources

- GitHub: [zeroth-tech/aigg-insights](https://github.com/zeroth-tech/aigg-insights)
- Twitter: [@aigginsights](https://twitter.com/aigginsights)
- Demo Video: [Loom](https://www.loom.com/share/YOUR_LOOM_VIDEO_ID_HERE)

Built with Polygon grant support.