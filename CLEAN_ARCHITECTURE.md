# Clean Architecture Summary

## ONE Solution, Simple & Clear

### 1. THE API (Port 8001)
- **File**: `api/main.py`
- **Purpose**: Serves market data with search endpoints
- **Key Endpoints**:
  - `/markets/search` - Search for relevant markets
  - `/markets` - Get all markets
  - `/health` - Health check

### 2. THE Flow
- **File**: `src/flows/dspy_enhanced_aigg_flow.py`
- **Purpose**: Complete analysis pipeline
- **Features**:
  - Category-based market matching (V2)
  - Enhanced Perplexity research (no prediction bias)
  - DSPy for structured outputs
  - Twitter-optimized responses

### 3. Support Files
- `src/flows/llm_market_matcher_v2.py` - Market matching logic
- `src/utils/dspy_utilities.py` - DSPy configuration
- `src/api_wrapper/twitter_wrapper.py` - Twitter integration

### 4. Archived (DO NOT USE)
- `src/flows/archive/` - All old flows
- `api/archive/` - Unused API files

## How It Works

1. **Query comes in** → Twitter or CLI
2. **Market Matching** → Categories selected by LLM → Markets scored
3. **Research** → Topic extracted → Perplexity searches (no prediction context)
4. **Analysis** → DSPy generates recommendation
5. **Response** → Twitter-ready output

## Performance
- ~45-50 seconds total (with optimizations)
- Parallel batch scoring
- Reduced market candidates (30 instead of 50)

## To Run
```bash
# Start API
python main.py api-server --port 8001

# Test with Streamlit
./scripts/run_streamlit.sh --production

# Run Twitter bot
python main.py twitter-bot --interval 30
```

## Environment Variables
```
FIREWORKS_API_KEY=xxx
PERPLEXITY_API_KEY=xxx
DB_HOST=37.27.54.184
DB_PORT=5432
DB_NAME=aigg
DB_USER=aigg_user
DB_PASSWORD=xxx
```

That's it. One API, one flow, clean and simple.