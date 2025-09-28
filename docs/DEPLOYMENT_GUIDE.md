# 🚀 AIGG Insights Deployment Guide

## Overview

AIGG Insights is an AI-powered Twitter bot that analyzes Polymarket prediction markets. The system runs as three independent microservices, providing real-time market analysis through Twitter mentions.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TWITTER BOT   │───▶│ WRAPPER API     │───▶│  MARKET API     │
│   (Monitor)     │    │  (Analysis)     │    │  (Database)     │
│   Port: N/A     │    │  Port: 8003     │    │  Port: 8001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    Twitter API            DSPy + Perplexity       PostgreSQL DB
   (Mentions/Replies)      (AI Analysis)         (114,450+ markets)
```

## Prerequisites

### Required Services
- PostgreSQL database with Polymarket data
- Twitter Developer Account (X Premium recommended)
- API Keys:
  - Twitter API v2 credentials
  - Perplexity API key
  - Fireworks AI API key

### System Requirements
- Python 3.9+
- tmux (for session management)
- 4GB+ RAM
- Stable internet connection

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/zeroth-tech/aigg-insights.git
cd aigg-insights

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Database Setup

```bash
# Initialize the database
python scripts/populate_polymarket_data_clob.py

# Verify database health
python main.py status
```

### 3. Start Services (Production)

Use tmux sessions for persistent services:

```bash
# Start Market API (Database Service)
tmux new -s market-api -d
tmux send-keys -t market-api "python main.py api-server --port 8001" Enter

# Start Twitter Wrapper (Analysis Service)
tmux new -s twitter-wrapper -d
tmux send-keys -t twitter-wrapper "python3 main.py wrapper-api --port 8003" Enter

# Start Twitter Bot (Monitor Service)
tmux new -s aigg-bot -d
tmux send-keys -t aigg-bot "python3 main.py twitter-bot --interval 30 --disable-whitelist" Enter
```

### 4. Verify Deployment

```bash
# Check service health
curl http://localhost:8001/health  # Market API
curl http://localhost:8003/health  # Twitter Wrapper

# Monitor logs
tmux attach -t aigg-bot  # View bot logs
# Use Ctrl+B, D to detach

# Check system status
python main.py status
```

## Service Configuration

### Market API (Port 8001)
- **Purpose**: Database access and market search
- **Database**: PostgreSQL with 114,450+ markets
- **Auto-cleanup**: Maintains ~6,991 active markets
- **Command**: `python main.py api-server --port 8001`

### Twitter Wrapper API (Port 8003)
- **Purpose**: AI analysis using DSPy framework
- **LLM**: Fireworks AI (Qwen 3.5 72B)
- **Research**: Perplexity Sonar for real-time data
- **Rate Limiting**: 1 request/minute per user
- **Command**: `python3 main.py wrapper-api --port 8003`

### Twitter Bot
- **Purpose**: Monitor @aigginsights mentions
- **Interval**: 30 seconds (X Premium)
- **Response Format**: 2-tweet thread with analysis + URL
- **Command**: `python3 main.py twitter-bot --interval 30 --disable-whitelist`

## Production Deployment

### Using systemd (Recommended)

Create service files for each component:

```bash
# /etc/systemd/system/aigg-market-api.service
[Unit]
Description=AIGG Market API Service
After=network.target postgresql.service

[Service]
Type=simple
User=aigg
WorkingDirectory=/home/aigg/aigg-insights
Environment="PATH=/home/aigg/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 /home/aigg/aigg-insights/main.py api-server --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/systemd/system/aigg-wrapper-api.service
[Unit]
Description=AIGG Twitter Wrapper API
After=network.target aigg-market-api.service

[Service]
Type=simple
User=aigg
WorkingDirectory=/home/aigg/aigg-insights
Environment="PATH=/home/aigg/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 /home/aigg/aigg-insights/main.py wrapper-api --port 8003
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/systemd/system/aigg-twitter-bot.service
[Unit]
Description=AIGG Twitter Bot
After=network.target aigg-wrapper-api.service

[Service]
Type=simple
User=aigg
WorkingDirectory=/home/aigg/aigg-insights
Environment="PATH=/home/aigg/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 /home/aigg/aigg-insights/main.py twitter-bot --interval 30 --disable-whitelist
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable aigg-market-api aigg-wrapper-api aigg-twitter-bot
sudo systemctl start aigg-market-api
sudo systemctl start aigg-wrapper-api
sudo systemctl start aigg-twitter-bot

# Check status
sudo systemctl status aigg-*
```

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: polymarket
      POSTGRES_USER: aigg
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  market-api:
    build: .
    command: python main.py api-server --port 8001
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://aigg:${DB_PASSWORD}@postgres:5432/polymarket
    depends_on:
      - postgres
    restart: always

  wrapper-api:
    build: .
    command: python main.py wrapper-api --port 8003
    ports:
      - "8003:8003"
    environment:
      PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}
      FIREWORKS_API_KEY: ${FIREWORKS_API_KEY}
      MARKET_API_URL: http://market-api:8001
    depends_on:
      - market-api
    restart: always

  twitter-bot:
    build: .
    command: python main.py twitter-bot --interval 30 --disable-whitelist
    environment:
      TWITTER_BEARER_TOKEN: ${TWITTER_BEARER_TOKEN}
      TWITTER_API_KEY: ${TWITTER_API_KEY}
      TWITTER_API_SECRET: ${TWITTER_API_SECRET}
      TWITTER_ACCESS_TOKEN: ${TWITTER_ACCESS_TOKEN}
      TWITTER_ACCESS_SECRET: ${TWITTER_ACCESS_SECRET}
      WRAPPER_API_URL: http://wrapper-api:8003
    depends_on:
      - wrapper-api
    restart: always

volumes:
  postgres_data:
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check all services
python main.py status

# Individual health endpoints
curl http://localhost:8001/health
curl http://localhost:8003/health

# Database metrics
curl http://localhost:8001/metrics
```

### Log Management

```bash
# View logs in tmux
tmux attach -t market-api
tmux attach -t twitter-wrapper
tmux attach -t aigg-bot

# Or with systemd
journalctl -u aigg-market-api -f
journalctl -u aigg-wrapper-api -f
journalctl -u aigg-twitter-bot -f
```

### Database Maintenance

```bash
# Update market data
python scripts/populate_polymarket_data_clob.py

# Clean inactive markets
python scripts/cleanup_inactive_markets.py

# Check database stats
python main.py status
```

## Environment Variables

Create a `.env` file with the following:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/polymarket

# Twitter API
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# AI Services
PERPLEXITY_API_KEY=your_perplexity_key
FIREWORKS_API_KEY=your_fireworks_key

# Optional
OPENAI_API_KEY=your_openai_key  # Fallback LLM
```

## Performance Tuning

### Response Times
- **Target**: 13-25 seconds per analysis
- **Bottlenecks**: Perplexity research (5-10s), LLM inference (3-5s)

### Rate Limiting
- **Twitter**: 30-second polling interval (X Premium)
- **Per User**: 1 request/minute
- **API Limits**: Monitor Perplexity/Fireworks quotas

### Database Optimization
```sql
-- Ensure indexes exist
CREATE INDEX idx_markets_active ON polymarket_markets(active);
CREATE INDEX idx_markets_slug ON polymarket_markets(market_slug);
CREATE INDEX idx_markets_title ON polymarket_markets(title);
```

## Troubleshooting

### Common Issues

1. **Bot not responding to mentions**
   - Check Twitter API credentials
   - Verify bot is running: `tmux ls`
   - Check logs for rate limiting

2. **Slow response times**
   - Monitor Perplexity API latency
   - Check database query performance
   - Consider caching frequently accessed markets

3. **URL preview not working**
   - URLs are hardcoded in `src/utils/polymarket_url_fixer.py`
   - Need to implement dynamic URL resolution (TODO)

4. **Database connection errors**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env
   - Ensure database migrations are applied

### Debug Commands

```bash
# Test single analysis
python main.py analyze "Will Bitcoin hit 200k?"

# Test market search
curl "http://localhost:8001/markets/search?q=bitcoin&limit=5"

# Test Twitter wrapper
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Bitcoin 200k?", "user_id": "test", "user_handle": "test"}'
```

## Security Considerations

1. **API Keys**: Never commit .env file
2. **Rate Limiting**: Implement per-user limits
3. **Access Control**: Use whitelist for beta testing
4. **Database**: Use read-only credentials where possible
5. **HTTPS**: Use reverse proxy (nginx) for production

## Scaling Considerations

### Horizontal Scaling
- Market API: Can run multiple instances behind load balancer
- Wrapper API: Stateless, easily scalable
- Twitter Bot: Single instance (avoid duplicate replies)

### Caching Strategy
- Redis for market data caching
- Response caching for popular queries
- Rate limit tracking in Redis

## Support & Resources

- **Documentation**: `/docs` directory
- **Tests**: `python -m pytest tests/`
- **Issues**: GitHub Issues
- **Logs**: Check `/logs` directory

## Known Issues & TODOs

### High Priority
- [ ] Fix automatic Polymarket URL generation (currently hardcoded)
- [ ] Integrate live Polymarket data feeds
- [ ] Implement WebSocket for real-time updates

### Medium Priority
- [ ] Add Redis caching layer
- [ ] Implement request queuing system
- [ ] Add Grafana monitoring dashboard

### Low Priority
- [ ] Multi-language support
- [ ] Web dashboard for analytics
- [ ] Automated testing in CI/CD

## Version History

- **v1.0.0**: Initial deployment with DSPy framework
- **v0.9.0**: Migrated from hardcoded to LLM-based matching
- **v0.8.0**: Added Fireworks AI integration

## Contact

For issues or questions:
- GitHub: https://github.com/zeroth-tech/aigg-insights
- Twitter: @aigginsights