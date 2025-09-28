# AIGG Flows

## The ONE Flow to Use

### `dspy_enhanced_aigg_flow.py`
This is the **ONLY** flow you should use. It includes:
- ✅ DSPy framework for structured prompting
- ✅ Category-based market matching (V2)
- ✅ Enhanced Perplexity research (without prediction bias)
- ✅ Clean, simple implementation
- ✅ Twitter-optimized responses

## Support Files
- `llm_market_matcher_v2.py` - Category-based market matcher
- `models.py` - Data models (if exists)
- `archive/` - Old deprecated code (DO NOT USE)

## Usage

```python
from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow

flow = DSPyEnhancedAIGGFlow()
result = flow.analyze_query("yo is btc hitting 200k or nah")

print(result.recommendation)  # BUY/SELL/HOLD
print(result.confidence)      # 0.0-1.0
print(result.short_analysis)  # Twitter-ready response
```

## API Endpoint
The flow expects the Market API to be running:
- Local: `http://localhost:8001`
- Production: `http://65.108.231.245:8001`

Make sure to use `/markets/search` endpoint, NOT `/markets`.