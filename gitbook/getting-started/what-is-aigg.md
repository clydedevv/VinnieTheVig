# What is AIGG?

AIGG is a Twitter-native companion for Polymarket that transforms market discovery from a research rabbit hole into a 30-second decision. Mention @VigVinnie with any market question and receive an actionable trading recommendation with the exact Polymarket link.

## The Problem

Prediction markets are exploding in popularity, but the user experience remains fragmented:

- **Discovery is noisy**: 114,450+ markets across different categories
- **Naming is inconsistent**: Same events titled differently
- **Timing matters**: Markets move fast, research takes time
- **Generic bots fail**: Vague responses that don't help trading decisions

Most traders either can't find the right market quickly or don't have time to research it properly. This friction prevents confident participation and creates missed opportunities.

## The Solution

AIGG eliminates this friction with three key innovations:

### 1. Custom, Clean Market Index

We maintain an "active only" index that dramatically improves search performance:

- **Before**: 114,450 total markets (many expired, duplicates, low volume)
- **After**: 6,991 active markets (94% reduction)
- **Result**: 10× faster search, more relevant results
- **Updates**: Daily cleanup at 03:00 UTC

### 2. AI Matcher That Understands Real Questions

Our matching engine combines multiple techniques for accuracy:

- **Fuzzy Matching**: Handles typos, abbreviations, variations
- **Semantic Matching**: Understands meaning and context
- **Entity Recognition**: Identifies people, dates, events
- **Relevance Ranking**: Prioritizes by volume, recency, status

When matches are close, we run additional research to select the best option.

### 3. Structured, Professional Replies

Every response follows a consistent format optimized for Twitter:

- **Analysis**: Key market drivers in 1-2 sentences
- **Stance**: Clear BUY/SELL/HOLD recommendation
- **Confidence**: Percentage score (50-100)
- **Link**: Direct Polymarket URL with preview

Responses respect Twitter's character limits while maintaining completeness.

## How It Works

The entire flow from question to answer takes 30-90 seconds:

### Step 1: Query Processing
You tweet: "@VigVinnie Will Bitcoin reach 200k?"
- Parse natural language
- Extract entities (Bitcoin, 200k)
- Normalize for search

### Step 2: Market Matching
- Search across 6,991 active markets
- Use LLM to rank candidates semantically
- Verify official Polymarket slug
- Return best match with metadata

### Step 3: Research & Analysis
- Check if market is time-sensitive
- Gather real-time context via Perplexity
- Analyze current odds and volume
- Generate trading thesis

### Step 4: Response Generation
- Format analysis in "Vinnie" voice (Brooklyn bookmaker persona)
- Add confidence score
- Include clean Polymarket URL
- Post as threaded reply

## Technical Architecture

### Core Technologies
- **LLM**: Fireworks AI with Qwen 3.5 72B (2-3s latency)
- **Research**: Perplexity Sonar for real-time data
- **Framework**: DSPy for structured generation
- **Database**: PostgreSQL with 114K markets indexed
- **APIs**: FastAPI microservices (ports 8001, 8003)

### Performance Metrics
| Component | Latency | Description |
|-----------|---------|-------------|
| Market Search | 1-3s | Semantic matching across database |
| Research | 5-10s | Real-time context gathering |
| Analysis | 3-5s | DSPy structured generation |
| Total | 30-90s | End-to-end response time |

## Use Cases

### For Domain Experts
AIGG accelerates your workflow:
- Skip manual market search
- Get instant context updates
- Focus on trading decisions
- Validate your thesis quickly

### For Casual Users
AIGG provides accessible entry points:
- No research rabbit holes
- Clear, actionable recommendations
- Confidence scores for risk assessment
- Direct links to trade

## Live Examples

### Political Markets
```
Q: "Trump winning 2028?"
A: "Word is Trump's barred from 2028 run by the 22nd Amendment.
    Smart money knows this is dead. SELL at 95% confidence."
```

### Crypto Markets
```
Q: "ETH flipping BTC?"
A: "The line says ETH/BTC ratio stuck at 0.03, lowest in years.
    Flippening dreams on ice. BUY NO at 80% confidence."
```

### Economic Markets
```
Q: "Fed cutting rates next meeting?"
A: "Powell's signaling more cuts with inflation cooling.
    Markets pricing 75% chance. BUY YES at 70% confidence."
```

## Why AIGG Matters

As prediction markets grow from niche to mainstream, the need for intelligent discovery becomes critical:

- **Volume Growth**: Polymarket alone has $3B+ in total volume
- **Market Expansion**: New platforms launching monthly
- **Mainstream Adoption**: Traditional finance entering the space

AIGG positions itself as the intelligence layer between users and markets, reducing friction and enabling confident participation.

By matching users to the right market, adding timely context, and providing clear recommendations, AIGG transforms prediction market trading from complex research into simple, actionable decisions.

## Next Steps

- [Quick Start Guide](quick-start.md) - Set up AIGG locally
- [Demo Examples](demo-examples.md) - Try working queries
- [System Architecture](../architecture/system-overview.md) - Technical deep dive
- [Product Roadmap](../roadmap/product-roadmap.md) - Platform vision