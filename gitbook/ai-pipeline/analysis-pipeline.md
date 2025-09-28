# AI Analysis Pipeline

## Overview

The AIGG analysis pipeline transforms Twitter mentions into structured market insights using a multi-stage AI process. The pipeline leverages DSPy for structured generation and integrates multiple LLM providers for different tasks.

## Pipeline Architecture

```
User Query → Market Matching → Research → Analysis → Response Formatting → Twitter Reply
```

## Stage 1: Query Processing

### Input Extraction
Extracts the market query from Twitter mentions:

```python
# Example input
"@VigVinnie Will Bitcoin hit 200k by end of year?"

# Extracted query
"Bitcoin 200k end of year"
```

### Query Normalization
- Removes social media artifacts (@mentions, hashtags)
- Expands abbreviations (BTC → Bitcoin)
- Standardizes date references
- Identifies key entities and timeframes

## Stage 2: Market Matching

### Semantic Search Process

The system uses LLM-based category matching to find relevant markets:

1. **Category Identification**
   - Query analyzed to determine market categories
   - Categories: Politics, Crypto, Sports, Economics, etc.

2. **Candidate Retrieval**
   - Database query for markets in identified categories
   - Filters for active markets only
   - Returns top 100 candidates

3. **LLM Ranking**
   - Qwen 3.0 235B model ranks candidates by relevance
   - Considers query intent and market specificity
   - Returns best matching market

### Matching Examples

```
Query: "Fed rate decision October"
Match: "Will the Federal Reserve cut rates in October 2024?"

Query: "NYC mayor race"
Match: "Who will win the 2025 NYC mayoral election?"

Query: "Bitcoin 200k"
Match: "Will Bitcoin reach $200,000 before 2025?"
```

## Stage 3: Research Phase

### Perplexity Integration

For time-sensitive markets, the system gathers real-time context:

```python
class ResearchEngine:
    def should_research(self, market):
        # Research if market is time-sensitive
        return any([
            "today" in market.title.lower(),
            "tomorrow" in market.title.lower(),
            datetime_near(market.end_date, days=7)
        ])

    def gather_context(self, market):
        # Use Perplexity Sonar for current information
        return perplexity.search(
            query=market.title,
            recency="day",
            sources=["news", "twitter", "reddit"]
        )
```

### Research Output
- Current news and events
- Recent developments
- Market sentiment indicators
- Key statistics and facts

## Stage 4: Analysis Generation

### DSPy Structured Analysis

The system uses DSPy signatures to ensure consistent output:

```python
class MarketAnalysis(dspy.Signature):
    market_title: str = dspy.InputField()
    current_context: str = dspy.InputField()

    key_factors: str = dspy.OutputField(desc="3-4 bullet points")
    analysis: str = dspy.OutputField(desc="2-3 sentences")
    recommendation: str = dspy.OutputField(desc="BUY_YES/BUY_NO/HOLD")
    confidence: int = dspy.OutputField(desc="50-100")
```

### Analysis Components

1. **Key Factors**: Main drivers affecting the market
2. **Trend Analysis**: Direction and momentum
3. **Risk Assessment**: Potential volatility
4. **Recommendation**: Clear trading action
5. **Confidence Score**: Certainty level (50-100)

## Stage 5: Response Formatting

### Vinnie Persona

Responses are formatted in the voice of "Vinnie," a Brooklyn bookmaker:

```python
class VinnieFormatter:
    def format_response(self, analysis):
        templates = [
            "Word is {analysis}. {action} at {confidence}% confidence.",
            "Smart money says {analysis}. I'm {action} with {confidence}% juice.",
            "The line's moving - {analysis}. {action}, {confidence}% sure."
        ]
        return random.choice(templates).format(
            analysis=analysis.summary,
            action=analysis.recommendation,
            confidence=analysis.confidence
        )
```

### Twitter Constraints
- Maximum 280 characters per tweet
- Thread format for analysis + URL
- Clean Polymarket URLs for preview cards

## Processing Times

### Performance Breakdown

- Query Processing: < 1 second
- Market Matching: 1-3 seconds
- Research (if needed): 5-10 seconds
- Analysis Generation: 3-5 seconds
- Response Formatting: < 1 second

**Total: 30-90 seconds end-to-end**

## Quality Assurance

### Validation Checks

1. **Market Relevance**: Ensure match relates to query
2. **Confidence Threshold**: Minimum 50% confidence required
3. **Response Coherence**: Grammar and logic validation
4. **URL Verification**: Ensure valid Polymarket link

### Fallback Strategies

```python
def analyze_with_fallback(query):
    try:
        # Primary: Fireworks AI with Qwen 3.0 235B
        return primary_analysis(query)
    except:
        try:
            # Fallback: Alternative model (configurable)
            return fallback_analysis(query)
        except:
            # Safe default
            return {
                "recommendation": "HOLD",
                "confidence": 50,
                "analysis": "Market conditions unclear."
            }
```

## Model Selection

### Primary Models

**Fireworks AI - Qwen 3.0 235B**
- Purpose: Market matching and analysis
- Speed: 2-3 seconds per request
- Cost: $0.40/million tokens

**Perplexity Sonar**
- Purpose: Real-time research
- Speed: 3-5 seconds per request
- Features: Web search with citations

### Alternative Models
- Purpose: Backup analysis when primary model is unavailable
- Note: Any compatible LLM can be substituted here
- Use case: High-volume periods or model failover

## Error Handling

### Common Issues and Solutions

1. **Market Not Found**
   - Solution: Return closest match with disclaimer
   - Response: "Closest market I found..."

2. **Research Timeout**
   - Solution: Proceed without research
   - Response: Based on market data only

3. **LLM Rate Limit**
   - Solution: Switch to backup provider
   - Automatic failover logic

4. **Invalid Query**
   - Solution: Ask for clarification
   - Response: "Can you be more specific?"

## Optimization Techniques

### Caching Strategy

```python
# Cache recent analyses (5 minutes)
@cache(ttl=300)
def get_analysis(market_id, context_hash):
    return generate_analysis(market_id, context)

# Cache market searches (1 hour)
@cache(ttl=3600)
def search_markets(query_normalized):
    return database.search(query_normalized)
```

### Parallel Processing

```python
async def process_mention(mention):
    # Run in parallel
    market_task = find_market(mention.query)
    research_task = gather_context(mention.query)

    market = await market_task
    context = await research_task

    return analyze(market, context)
```

## Monitoring and Metrics

### Key Performance Indicators

- Response Time: Target < 60 seconds
- Match Accuracy: Target > 85%
- Confidence Average: Target > 70%
- Error Rate: Target < 5%

### Logging

```python
logger.info({
    "query": user_query,
    "market_matched": market.title,
    "confidence": analysis.confidence,
    "response_time": elapsed_time,
    "model_used": model_name
})
```

## Future Enhancements

### Planned Improvements

1. **Multi-Market Analysis**: Compare related markets
2. **Historical Performance**: Track prediction accuracy
3. **Sentiment Analysis**: Incorporate social media sentiment
4. **Custom Models**: Fine-tuned models for market analysis
5. **Streaming Responses**: Real-time updates as analysis progresses