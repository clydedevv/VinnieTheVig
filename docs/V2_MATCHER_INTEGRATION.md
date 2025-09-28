# V2 Matcher Integration

## Overview
The V2 matcher is now integrated and enabled by default. It uses a two-stage category-based approach for better market matching.

## How It Works

### Stage 1: Category Selection
- LLM analyzes the query and selects relevant categories
- Example: "china taiwan" → ["Geopolitics", "Politics"]

### Stage 2: Market Scoring
- Only markets from selected categories are scored
- Strict relevance checking prevents false matches
- Tiered scoring (HIGH/MEDIUM/LOW) for better differentiation

## Configuration

### Enable/Disable V2
```bash
# Enable V2 (default)
export USE_V2_MATCHER=true

# Disable V2 (fallback to V1)
export USE_V2_MATCHER=false
```

## Performance Impact

### V1 Approach:
- Fetches 30-50 markets from search
- Scores ALL of them
- ~20 seconds for scoring

### V2 Approach:
- Fetches categories first (~1 sec)
- LLM selects relevant categories (~3 sec)
- Scores only markets in those categories
- Better relevance, similar speed

## Benefits

1. **Better Relevance**: No more China→Bitcoin false matches
2. **Scalable**: Works well even with 51K+ markets
3. **Flexible**: Handles cross-category queries
4. **Fallback**: Automatically falls back to V1 if error

## Category Data
Categories are now properly populated in the database:
- Crypto
- Politics
- Business
- TikTok
- SpaceX
- Bitcoin
- 2025 Predictions
- Bird Flu
- Trump
- LTC
- And many more...

## Testing
Run the Streamlit app to see V2 in action:
```bash
./scripts/run_streamlit.sh --production
```

Look for: "📂 Using V2 matcher with category filtering" in the logs.