# LLM-Based Market Matching

## Overview

We've replaced the hardcoded market matching logic with a scalable, LLM-based approach that uses semantic understanding to match user queries to prediction markets.

## Key Components

### 1. `llm_market_matcher.py`
- **Pure LLM-based matching** - no hardcoded rules
- **DSPy Signatures** for structured LLM interactions:
  - `ExtractQueryContext`: Understands user intent, entities, time context
  - `ScoreMarket`: Scores individual market relevance 
  - `BatchScoreMarkets`: Efficiently scores multiple markets at once
- **Semantic Understanding**: LLM comprehends meaning, not just keywords

### 2. Integration with DSPy Flow
- `dspy_enhanced_aigg_flow.py` now uses `LLMMarketMatcher`
- Replaces hardcoded `preprocess_search_query()` and keyword matching
- Fetches all active markets and lets LLM rank them by relevance

### 3. API Enhancement
- New endpoint: `/markets/search/llm` for semantic search
- Compare endpoint: `/markets/search/compare` to see both approaches
- Returns reasoning for each match

## Benefits Over Hardcoded Approach

### 1. **No Maintenance Required**
```python
# OLD: Hardcoded synonyms that need constant updates
synonym_map = {
    'bitcoin': ['btc', 'crypto'],
    'federal reserve': ['fed', 'fomc'],
    # ... hundreds of manual mappings
}

# NEW: LLM understands semantics automatically
"Bitcoin moon when?" → Understands crypto price increase intent
"Fed dovish?" → Understands monetary policy question
```

### 2. **Handles Complex Queries**
- Natural language: "Is the war ending soon?"
- Slang/informal: "Crypto to the moon 🚀"
- Ambiguous: "200k EOY?" → Bitcoin $200k by end of year
- Novel concepts: Automatically handles new market types

### 3. **Semantic Understanding**
```python
# Query: "Interest rate environment 2025"
# LLM understands this relates to:
# - Federal Reserve policy
# - Economic conditions
# - Monetary decisions
# → Matches Fed-related markets with explanation
```

### 4. **Scalability**
- Add new market categories without code changes
- Handles emerging topics (quantum computing, Mars missions)
- Adapts to new terminology automatically

## Example Usage

```python
from src.flows.llm_market_matcher import LLMMarketMatcher, MarketData

# Initialize matcher
matcher = LLMMarketMatcher()

# Define markets
markets = [
    MarketData(
        id="btc-200k",
        title="Will Bitcoin reach $200,000 by end of 2025?",
        category="Crypto",
        end_date="2025-12-31T23:59:59Z",
        active=True
    ),
    # ... more markets
]

# Find best matches
results = matcher.find_best_markets(
    query="Bitcoin moon when?",
    markets=markets,
    top_k=5
)

# Results include score and reasoning
for market, score, reasoning in results:
    print(f"[{score:.3f}] {market.title}")
    print(f"   → {reasoning}")
```

## Query Understanding

The LLM extracts structured context from queries:

```python
Query: "Bitcoin reaching $200k this year"

Extracted Context:
{
    "main_topic": "Bitcoin price prediction",
    "entities": ["Bitcoin"],
    "time_context": "end of 2025",
    "price_targets": ["$200k", "200000"],
    "intent": "Find Bitcoin price prediction for 2025"
}
```

## Performance Considerations

1. **Batch Processing**: Scores multiple markets in single LLM call
2. **Caching**: Results can be cached for common queries
3. **Fallback**: Individual scoring if batch fails
4. **Configurable**: Can use different LLMs (Fireworks, Perplexity, etc.)

## Testing

Run comprehensive tests:
```bash
python test_llm_market_matching.py
```

This compares:
- Hardcoded vs LLM approach
- Edge case handling
- Scalability to new domains

## Future Enhancements

1. **Embeddings**: Use vector similarity for initial filtering
2. **Fine-tuning**: Train specialized model on market matching
3. **Multi-stage**: Combine embeddings + LLM for best performance
4. **User Feedback**: Learn from user selections to improve

## Migration Path

1. **Current**: Both approaches available
2. **Testing**: Use `/markets/search/compare` endpoint
3. **Gradual**: Route percentage of traffic to LLM approach
4. **Full Migration**: Once validated, remove hardcoded logic