# Market API

FastAPI service providing programmatic access to market data and analysis.

## API Flow

```mermaid
flowchart LR
    subgraph Clients
        WEB[Web App]
        CLI[CLI Tool]
        BOT[Twitter Bot]
    end

    subgraph "Market API [:8001]"
        EP[Endpoints]

        subgraph Routes
            HEALTH[/health]
            SEARCH[/markets/search]
            DETAIL[/markets/{id}]
            ANALYZE[/analyze]
        end

        subgraph Processing
            VAL[Validation]
            CACHE[Cache Layer]
            MATCH[Market Matcher]
        end
    end

    subgraph Backend
        DB[(PostgreSQL)]
        REDIS[(Redis)]
        LLM[Fireworks AI]
    end

    WEB --> EP
    CLI --> EP
    BOT --> EP

    EP --> HEALTH
    EP --> SEARCH
    EP --> DETAIL
    EP --> ANALYZE

    SEARCH --> VAL
    ANALYZE --> VAL
    VAL --> CACHE
    CACHE --> MATCH
    MATCH --> DB
    MATCH --> LLM
    CACHE --> REDIS
```

## Endpoints

### GET /health

System health check.

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "markets_count": 51234,
  "active_markets": 3168,
  "uptime": 86400
}
```

### GET /markets/search

Search markets by query.

```bash
curl "http://localhost:8001/markets/search?q=bitcoin&limit=5"
```

Parameters:
- `q`: Search query (required)
- `limit`: Max results (default: 10)
- `category`: Filter by category
- `active_only`: Only active markets (default: true)

Response:
```json
{
  "results": [
    {
      "market_id": "0x123...",
      "question": "Will Bitcoin reach $200,000 by December 31, 2025?",
      "category": "Crypto",
      "probability": 0.085,
      "volume_24h": 125000.50,
      "url": "https://polymarket.com/event/bitcoin-200k-2025"
    }
  ],
  "count": 5,
  "query_time_ms": 245
}
```

### GET /markets/{market_id}

Get specific market details.

```bash
curl http://localhost:8001/markets/0x123abc
```

Response:
```json
{
  "market_id": "0x123abc",
  "question": "Will Bitcoin reach $200,000 by December 31, 2025?",
  "category": "Crypto",
  "outcomes": [
    {"name": "Yes", "price": 0.085},
    {"name": "No", "price": 0.915}
  ],
  "probability": 0.085,
  "volume_24h": 125000.50,
  "liquidity": 500000.00,
  "end_date": "2025-12-31T23:59:59Z",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### POST /analyze

Trigger market analysis.

```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Will Bitcoin reach 200k?",
    "include_research": true
  }'
```

Request:
```json
{
  "query": "Will Bitcoin reach 200k?",
  "include_research": true,
  "persona": "technical"
}
```

Response:
```json
{
  "market": {
    "market_id": "0x123...",
    "question": "Will Bitcoin reach $200,000 by December 31, 2025?"
  },
  "analysis": {
    "recommendation": "BUY_NO",
    "confidence": 0.82,
    "reasoning": "Bitcoin struggling below $110K...",
    "research_data": {...}
  },
  "processing_time_ms": 8234
}
```

## WebSocket Support (Planned)

Real-time market updates via WebSocket. *This feature is planned for future implementation.*

```javascript
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    markets: ['0x123...', '0x456...']
  }));
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Market update:', update);
};
```

## Authentication

Currently uses API key authentication for write operations.

```python
headers = {
    "X-API-Key": "your_api_key_here"
}
```

## Rate Limiting

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| /health | 100/min | 1 minute |
| /markets/search | 60/min | 1 minute |
| /markets/{id} | 100/min | 1 minute |
| /analyze | 10/min | 1 minute |

## Error Responses

Standard error format:

```json
{
  "error": {
    "code": "MARKET_NOT_FOUND",
    "message": "Market with ID 0x999 not found",
    "details": {...}
  }
}
```

Error codes:
- `MARKET_NOT_FOUND`: Market doesn't exist
- `INVALID_QUERY`: Malformed search query
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Implementation

### FastAPI Application

From `api/main.py`:

```python
from fastapi import FastAPI, Query, HTTPException
from typing import Optional, List

app = FastAPI(title="AIGG Market API", version="1.0.0")

@app.get("/markets/search")
async def search_markets(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None
) -> dict:
    # Implementation
    matcher = LLMMarketMatcherV2()
    results = await matcher.search(q, limit, category)
    return {"results": results, "count": len(results)}
```

### Caching Strategy

Redis caching for common queries:

```python
@cache(expire=300)  # 5 minute cache
async def get_market_data(market_id: str):
    return await db.fetch_market(market_id)
```

### Database Connection Pool

```python
from databases import Database

database = Database(
    DATABASE_URL,
    min_connections=5,
    max_connections=20
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
```

## Testing

### Unit Tests
```bash
pytest tests/api/test_markets.py
```

### Load Testing
```bash
locust -f tests/load/api_load_test.py --host=http://localhost:8001
```

### Integration Tests
```python
def test_search_endpoint():
    response = client.get("/markets/search?q=bitcoin")
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Production Settings
```python
uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 4 \
    --loop uvloop \
    --log-level info
```