# System Overview

## Architecture

The AIGG system runs as three independent microservices communicating via HTTP APIs:

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

## Core Components

### 1. Twitter Bot Service
- Purpose: Monitor and respond to @VigVinnie mentions
- Technology: Python Twitter API v2 client
- Polling Interval: 30 seconds (X Premium rate limits)
- Access Control: 4-tier system (admin/vip/whitelist/blocked)
- Process: `python main.py twitter-bot --interval 30 --disable-whitelist`

### 2. Market API Server (Port 8001)
- Purpose: Database access and market search
- Technology: FastAPI with async handlers
- Database: PostgreSQL with 114,450 markets (6,991 active)
- Features: LLM-based semantic search using category matching
- Performance: Sub-second market matching from live database
- Process: `python main.py api-server --port 8001`

### 3. Twitter Wrapper API (Port 8003)
- Purpose: AI analysis engine with rate limiting
- Technology: FastAPI service orchestrating DSPy pipeline
- Features: User-based rate limiting, structured analysis
- Process: `python main.py wrapper-api --port 8003`

### 4. DSPy Analysis Pipeline
- Purpose: Generate trading recommendations
- Technology: DSPy framework with Fireworks AI (Qwen 3.0 235B)
- Research: Perplexity Sonar for real-time news
- Output: Structured analysis with BUY/SELL/HOLD recommendations

### 5. PostgreSQL Database
- Purpose: Market data storage and analysis persistence
- Scale: 114,450 total markets, 6,991 actively traded
- Tables: polymarket_markets, research, analysis, conclusions
- Maintenance: Automatic cleanup of inactive markets
- Updates: Real-time synchronization with Polymarket

## Data Flow

### Request Processing

1. User tweets mention to @VigVinnie
2. Bot polls Twitter mentions every 30 seconds
3. Bot extracts query and posts to Wrapper API (port 8003)
4. Wrapper searches markets via Market API (port 8001)
5. Wrapper performs AI analysis using DSPy and Perplexity
6. Wrapper returns formatted response
7. Bot posts threaded reply with analysis and Polymarket URL

### Response Format

- Tweet 1: Market analysis with trading recommendation
- Tweet 2: Clean Polymarket URL (threaded for preview card)

## Processing Pipeline

### Request Lifecycle

1. **Mention Detection** (1-2 seconds)
   - Twitter bot polls for new mentions
   - Filters out already processed tweets
   - Extracts query from mention text

2. **Market Matching** (1-3 seconds)
   - Category-based semantic search
   - Ranks by relevance and activity
   - Returns best matching market

3. **Research Phase** (5-10 seconds)
   - Perplexity Sonar gathers current news
   - Only for time-sensitive markets
   - Provides real-time context

4. **Analysis Generation** (3-5 seconds)
   - DSPy structured generation
   - Fireworks AI inference
   - Produces trading recommendation

5. **Response Posting** (1-2 seconds)
   - Formats analysis for Twitter
   - Posts threaded reply
   - Updates state to prevent duplicates

## Performance Metrics

- Response Time: 30-90 seconds (includes research and analysis)
- Polling Interval: 30 seconds for mention checks
- Rate Limiting: 1 request per minute per user
- Market Coverage: 114,450 total markets, 6,991 active
- Analysis Accuracy: High confidence with DSPy structured outputs
- Uptime: Continuous operation via tmux sessions

## External Dependencies

- Twitter API v2: Mention polling and reply posting
- Polymarket API: Market data synchronization
- Fireworks AI: LLM inference (Qwen 3.0 235B)
- Perplexity API: Real-time news research
- PostgreSQL: Data persistence

## Scaling Considerations

### Current Capacity
- Mentions: 1,000+ per day capacity
- Markets: 114,450 total (6,991 active)
- Response Time: 30-90 seconds end-to-end
- Concurrent Requests: 10-20

### Future Scaling
- Horizontal scaling with multiple bot instances
- Redis caching for frequent queries
- Message queue for asynchronous processing
- Database read replicas for load distribution


## Security and Access Control

- Twitter OAuth 2.0 authentication
- Environment-based API key management
- 4-tier access system (admin/vip/whitelist/blocked)
- User-based rate limiting
- No PII storage or logging


## Code Organization

```
aigg-insights/
├── main.py             # Central CLI interface
├── api/
│   └── main.py        # Market API server
├── src/
│   ├── flows/         # DSPy analysis pipeline
│   ├── twitter/       # Bot implementation
│   ├── api_wrapper/   # Twitter wrapper service
│   └── utils/         # Shared utilities
├── tests/             # Test suites
├── scripts/           # Maintenance scripts
└── docs/              # Documentation
```

## Key Technologies

### AI Framework
- DSPy: Structured prompting and consistent outputs
- Fireworks AI: Fast inference with Qwen 3.0 235B
- Perplexity Sonar: Real-time news and research

### Infrastructure
- PostgreSQL: Market data storage
- FastAPI: RESTful API services
- Twitter API v2: Social media integration
- Tmux: Process persistence