# AIGG Insights API Documentation

## Overview

AIGG Insights API is a FastAPI-based service providing access to Polymarket data and research insights.

## Endpoints

### 1. GET /markets

Returns a list of prediction markets.

**Parameters:**
- **active** (bool, default: true) – Only return active markets.
- **include_closed** (bool, default: false) – Include closed markets.
- **limit** (int, default: 10, max: 100) – Number of markets to return.

**Example:**
```bash
curl "http://37.27.54.184:8000/markets?limit=5"
```

**Response:**
```json
{
  "market_id": "523138",
  "question": "Will Nottingham Forest finish in 2nd place?",
  "description": "...",
  "volume_24h": 100251.615116,
  "active": true,
  "end_date": "2025-05-25T12:00:00+00:00",
  "outcomes": ["Yes", "No"],
  "outcome_prices": ["0.055", "0.945"],
  "last_updated": "2025-02-14T07:18:19.856050+00:00"
}
```

### 2. GET /markets/{market_id}

Returns details for a specific market.

**Example:**
```bash
curl "http://37.27.54.184:8000/markets/523138"
```

### 3. GET /health

Health check endpoint.

**Example:**
```bash
curl "http://37.27.54.184:8000/health"
```

## Setup

### Environment Variables

Define the following environment variable:

```env
DATABASE_URL=postgresql://user:password@localhost/aigg_dev
```

### Service Configuration

Create a service configuration file at `/etc/systemd/system/aigg-api.service` with the following content:

```ini
[Unit]
Description=AIGG Insights API
After=network.target postgresql.service

[Service]
User=cosmos
Group=cosmos
WorkingDirectory=/home/cosmos/aigg-insights
Environment="PATH=/home/cosmos/aigg-insights/venv/bin"
ExecStart=/home/cosmos/aigg-insights/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Logging

- **Location:** /var/log/aigg-api.log
- **Format:** timestamp - name - level - message
- **Rotation:** Daily with 7 days retention

## Error Handling

- **404:** Market not found
- **500:** Database connection/query errors