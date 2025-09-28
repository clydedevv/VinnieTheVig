# Quick Start Guide

Get AIGG Insights running in under 5 minutes with this quick start guide.

## Prerequisites

Before starting, ensure you have:

* Python 3.11+ installed
* PostgreSQL 14+ running
* API keys for OpenAI, Fireworks AI, and Perplexity
* Twitter API credentials (for bot functionality)

## 1. Clone the Repository

```bash
git clone https://github.com/clydedevv/VinnieTheVig.git
cd VinnieTheVig
```

## 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Fireworks AI (Primary LLM)
FIREWORKS_API_KEY=your_fireworks_api_key

# Perplexity (Research)
PERPLEXITY_API_KEY=your_perplexity_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aigg_insights

# Twitter API (Optional for bot)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

## 4. Initialize the Database

```bash
# Run database migrations
python main.py database init

# Load initial market data
python main.py database load-markets
```

## 5. Test the System

Run a simple market analysis to verify everything works:

```bash
python main.py analyze "Will Bitcoin reach 200k in 2025?"
```

Expected output:

```
Finding relevant markets...
Analyzing: BTC Above $200,000 by Dec 31, 2025
Current probability: 8.5%
Recommendation: Strong Buy (High upside potential)
```

## 6. Start the API Server

```bash
# Start the market API
python main.py api-server --port 8001
```

Test the API:

```bash
curl http://localhost:8001/health
```

## 7. Run the Twitter Bot (Optional)

If you have Twitter API credentials:

```bash
# Start bot with 30-second interval
python main.py twitter-bot --interval 30 --disable-whitelist
```

## Next Steps

* Read the [System Overview](../architecture/system-overview.md) to understand the architecture
* Check out [Demo Examples](demo-examples.md) for more usage scenarios
* Configure your [API Keys](../setup/api-keys.md) for production use
* Learn about [Running the System](../setup/running-the-system.md) in different modes

## Quick Command Reference

```bash
# Analysis
python main.py analyze "Your market question"

# API Server
python main.py api-server --port 8001

# Twitter Bot
python main.py twitter-bot --interval 30

# System Status
python main.py status

# Run Tests
python main.py test
```

## Troubleshooting

### Common Issues

**Database Connection Error**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection
psql -U your_user -d aigg_insights
```

**API Key Errors**

* Ensure all API keys in `.env` are valid
* Check rate limits haven't been exceeded
* Verify API subscriptions are active

**Module Import Errors**

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

For more help, see the [Troubleshooting Guide](../appendix/troubleshooting.md).
