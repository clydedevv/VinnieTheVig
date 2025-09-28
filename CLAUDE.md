# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIGG Insights is an AI-powered Twitter bot using the DSPy framework to analyze Polymarket prediction markets and provide trading recommendations via Twitter mentions (@aigginsights).

## Architecture

The system consists of:
- **Twitter Bot**: Monitors mentions and responds with market analysis (X Premium: 30-second intervals)
- **Market API** (port 8001): FastAPI service with LLM-based market matching for 51K+ markets
- **Twitter Wrapper API** (port 8003): Handles Twitter integration and rate limiting
- **DSPy Enhanced AIGG Flow**: Core analysis engine using DSPy framework with Fireworks AI (Qwen 3.5 72B) and Perplexity Sonar for research

## Common Development Commands

### Running Services
```bash
# Start Twitter bot (X Premium: 30-second intervals)
python main.py twitter-bot --interval 30 --disable-whitelist

# Start Market API server
python main.py api-server --port 8001

# Start Twitter Wrapper API
python main.py wrapper-api --port 8003

# Run single analysis
python main.py analyze "Will Bitcoin hit 200k?"

# Check system status
python main.py status

# Run tests
python main.py test
python main.py test --component flow
```

### Testing & Linting
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run specific test files
python tests/integration/test_pipeline_2025_queries.py
python tests/unit/test_llm_market_matching.py

# No specific linting command found - ask user for lint/typecheck commands if needed
```

## Key Files & Entry Points

- `main.py`: Central CLI interface for all operations
- `api/main.py`: THE market API server (port 8001)
- `src/flows/dspy_enhanced_aigg_flow.py`: THE analysis flow (uses DSPy)
- `src/flows/llm_market_matcher_v2.py`: Category-based market matching
- `src/utils/dspy_utilities.py`: DSPy configuration
- `src/flows/archive/`: Old deprecated code (DO NOT USE)

## Database

PostgreSQL database with key tables:
- `polymarket_markets`: Core market data (51K+ markets)
- `research`: Market research data
- `analysis`: AI-generated analysis results
- `conclusions`: Final trading recommendations

## API Endpoints

```bash
# Health check
curl http://localhost:8001/health

# Search markets
curl "http://localhost:8001/markets/search?q=bitcoin&limit=10"

# Twitter wrapper analysis
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Bitcoin 200k?", "user_id": "123", "user_handle": "test"}'
```

## Important Notes

- The system uses a 4-tier access control (admin/vip/whitelist/blocked)
- Twitter API rate limiting is strictly enforced (X Premium: 30-second intervals)
- Market matching uses pure LLM-based semantic search (no hardcoded rules)
- DSPy framework ensures structured, consistent outputs
- Fireworks AI (Qwen 3.5 72B) provides fast, intelligent analysis
- Response time is typically 13-25 seconds per analysis
- Database auto-cleanup maintains ~3,168 active markets from 51K+ total

## Recent Architectural Changes

- Migrated from hardcoded market matching to LLM-based semantic search
- Implemented DSPy framework for structured prompting and consistent outputs
- Added Fireworks AI integration for faster inference
- Cleaned up repository structure (tests/, docs/, scripts/, tools/)
- Updated to use `dspy_enhanced_aigg_flow.py` as the main analysis pipeline