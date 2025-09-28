# Core Components

The AIGG system consists of three main services and supporting components that work together to provide intelligent market analysis.

## 1. Twitter Bot Service

The front-facing interface that monitors Twitter mentions and orchestrates responses.

### Key Features
- Mention Monitoring: Polls for @aigginsights mentions every 30 seconds
- Response Generation: Posts threaded responses with analysis
- Access Control: 4-tier system (admin/vip/whitelist/blocked)
- State Management: Tracks processed tweets to prevent duplicates

### Implementation
- Location: `src/twitter/bot.py`
- Process: `python main.py twitter-bot --interval 30 --disable-whitelist`
- Dependencies: Twitter API v2, Wrapper API connection

## 2. Market API Server

FastAPI service providing database access and market search capabilities.

### Key Features
- Database Operations: Direct PostgreSQL access for market data
- Search Endpoints: LLM-based semantic market matching
- Health Monitoring: Status checks for system components
- Performance: Sub-second query response times

### Implementation
- Location: `api/main.py`
- Process: `python main.py api-server --port 8001`
- Database: PostgreSQL with 114,450 markets

### Endpoints
- `GET /health`: System health check
- `GET /markets/search`: Search markets by query
- `GET /markets/{market_id}`: Get specific market details
- `POST /markets/batch`: Batch market retrieval

## 3. Twitter Wrapper API

Middleware service that handles rate limiting and orchestrates the analysis pipeline.

### Key Features
- Rate Limiting: User-based request throttling
- Analysis Orchestration: Coordinates DSPy flow execution
- Error Handling: Graceful degradation for failures
- Response Formatting: Twitter-compatible output

### Implementation
- Location: `src/api_wrapper/twitter_wrapper.py`
- Process: `python main.py wrapper-api --port 8003`
- Dependencies: Market API, DSPy pipeline

## 4. DSPy Analysis Pipeline

The core AI engine that generates market insights and trading recommendations.

### Components
- Market Matcher: LLM-based semantic search
- Research Engine: Perplexity Sonar integration
- Analysis Module: DSPy structured generation
- Response Formatter: Twitter-optimized output

### Implementation
- Location: `src/flows/dspy_enhanced_aigg_flow.py`
- LLM: Fireworks AI with Qwen 3.5 72B
- Research: Perplexity Sonar for real-time news

## 5. LLM Market Matcher

Semantic search engine for finding relevant markets from the database.

### Matching Strategy
- Category-Based Search: Groups markets by theme
- LLM-Powered Matching: Semantic understanding via Qwen 3.5 72B
- Multi-Stage Filtering: Progressive result narrowing
- Relevance Scoring: Query similarity ranking

### Implementation
- Location: `src/flows/llm_market_matcher_v2.py`
- Performance: 1-3 seconds for semantic search
- Coverage: 114,450 markets indexed

## 6. Database Layer

PostgreSQL database managing market data and analysis results.

### Key Tables
- `polymarket_markets`: 114,450 market records (6,991 active)
- `research`: Market research cache
- `analysis`: AI-generated insights
- `conclusions`: Trading recommendations
- `twitter_interactions`: User engagement tracking

### Maintenance
- Automatic cleanup of inactive markets
- Real-time Polymarket synchronization
- Connection pooling for performance
- Indexed searches on key fields

## 7. External Integrations

### Fireworks AI
- Model: Qwen 3.5 72B
- Purpose: Market matching and analysis
- Response Time: 2-3 seconds
- Configuration: Via DSPy utilities

### Perplexity API
- Model: Sonar Large
- Purpose: Real-time news research
- Response Time: 3-5 seconds
- Features: Current information with citations

### Twitter API v2
- Purpose: Mention monitoring and replies
- Rate Limits: X Premium tier (30-second intervals)
- Features: Threaded conversations, media attachments

## 8. Utility Components

### DSPy Utilities
- Location: `src/utils/dspy_utilities.py`
- Functions: Model configuration, prompt templates, response parsing

### Database Utilities
- Location: `src/utils/database.py`
- Functions: Connection pooling, query optimization

### Polymarket URL Fixer
- Location: `src/utils/polymarket_url_fixer.py`
- Functions: Clean URL generation for Twitter previews

## Communication Flow

### Service Communication
- Twitter Bot -> Wrapper API (HTTP POST to port 8003)
- Wrapper API -> Market API (HTTP GET to port 8001)
- All services: Independent tmux sessions
- State persistence: JSON files and PostgreSQL

### Error Handling
- Retry logic with exponential backoff
- Fallback strategies for external APIs
- Graceful degradation for partial failures
- Structured logging to `logs/` directory

## Monitoring and Health Checks

### Health Endpoints
- Market API: `GET http://localhost:8001/health`
- Wrapper API: `GET http://localhost:8003/health`
- Response includes: version, uptime, component status

### Key Metrics
- Response times: 30-90 seconds end-to-end
- Market coverage: 114,450 total, 6,991 active
- Rate limits: 1 request/minute per user
- Uptime: Continuous via tmux persistence