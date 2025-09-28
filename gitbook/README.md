# AIGG - A Polymarket Companion

## Introduction

AIGG is the underlying technology that powers intelligent prediction market analysis. The system lets anyone ask a market question on Twitter and get a concise answer they can act on: a one-paragraph rationale, a clear BUY/SELL/HOLD with confidence, and the exact Polymarket link.

## The Problem We're Tackling

Prediction markets are having a moment. Crypto Twitter and mainstream outlets are paying attention, especially when volatility spikes. But attention and capital are scattered across thousands of tokens and feeds.

- Discovery is noisy
- Naming is inconsistent
- Timing matters

Most people either can't find the right market quickly or don't have the time to research it. Generic bots make this worse by producing vague text that doesn't help you trade.

## Meet VigVinnie

While AIGG is the technology, **@VigVinnie** is the character who brings it to life on Twitter. VigVinnie is an Italian-American Brooklyn bookmaker with a Pepe profile picture who talks like he's been taking bets his whole life.

**Follow VigVinnie:** [@VigVinnie](https://x.com/VigVinnie)

### The Character
- **Personality**: Brooklyn bookmaker with old-school betting parlor wisdom
- **Voice**: Uses gambling terminology ("the line's wobbling", "smart money's drifting")  
- **Background**: Italian-American who knows the streets and the books
- **Style**: Direct, opinionated, and always ready with a take

### How It Works
Mention @VigVinnie with any market question and he does the heavy lifting: identifies the correct market, adds current context when needed, and replies with a short, opinionated take and confidence number, plus the official Polymarket link.

- If you have domain expertise, VigVinnie accelerates you
- If you don't, he gives you a usable starting point instead of sending you down a research rabbit hole

## Example Interaction

Here's how VigVinnie responds to market questions:

**User:** "@VigVinnie NYC mayoral election thoughts?"

**VigVinnie's Analysis Tweet:**
> Word is Mamdani's pulling early traction with 26%-50% in the books, and the line's wobbling. Adams and Cuomo split the Dem vote, so the smart money's drifting toward the progressive yes side. With debates near and the juice shifting, there's value before the late action hits.

**VigVinnie's Follow-up Tweet:**
> [Polymarket link with clean preview]

This two-tweet pattern gives you both the Brooklyn bookmaker analysis and direct market access.

## Key Innovations

AIGG stands on three pillars:

### 1. Custom, Clean Market Index
We ingest Polymarket's corpus and maintain an "active only" index. From 114,450 total markets, we automatically remove expired and inactive ones daily, leaving about 6,991 active markets (a 94% reduction). This makes search roughly 10× faster and keeps results relevant. Live searches resolve in under a second.

### 2. AI Matcher That Understands Real Questions
We combine fuzzy matching (handles typos and phrasing) with semantic matching (understands meaning and entities). Candidates are ranked by relevance, recency, and market status, then validated against the official Polymarket slug so links always work. When several candidates are close, AIGG runs a quick research pass and selects the best of the top ten.

### 3. Structured, Professional Replies
Answers follow a consistent shape: what matters now, the stance (BUY/SELL/HOLD), a confidence percentage, and the exact link. Responses respect Twitter's character limit without cutting sentences, so the message stays readable and complete.

Under the hood, we use an LLM-guided pipeline and DSPy-style prompting to enforce structure and consistency. A lightweight research step (e.g., Perplexity Sonar) is triggered only for time-sensitive topics to keep latency and costs predictable.

## Technical Flow

When you mention @VigVinnie with a question like "BTC at 200k in 2025?" or "Ukraine-Russia ceasefire before July?", here's what happens behind the scenes:

1. **Parse & Normalize**: AIGG parses the intent, normalizes entities and dates, and queries the active market index
2. **Match & Verify**: The matcher returns high-confidence candidates and verifies the official slug to guarantee a correct link
3. **Research & Analyze**: If the topic is moving fast, AIGG pulls fresh public context via Perplexity
4. **Character Voice**: VigVinnie's Brooklyn bookmaker personality shapes the response with gambling terminology and street-smart analysis
5. **Synthesize & Reply**: Creates a tight paragraph that surfaces key drivers, adds a clear stance with confidence, and replies with the full Polymarket URL

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
git clone https://github.com/clydedevv/VinnieTheVig.git
cd VinnieTheVig

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

- GitHub: [clydedevv/VinnieTheVig](https://github.com/clydedevv/VinnieTheVig)
- Twitter: [@VigVinnie](https://twitter.com/VigVinnie)
- Demo Video: [Loom](https://www.loom.com/share/YOUR_LOOM_VIDEO_ID_HERE)

Built with Polygon grant support.