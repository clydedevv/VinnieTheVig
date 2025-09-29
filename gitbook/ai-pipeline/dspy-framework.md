# DSPy Framework Integration

## Overview

AIGG leverages DSPy (Declarative Self-improving Language Programs) to create structured, reliable AI pipelines that generate consistent trading recommendations. DSPy enables us to define complex reasoning chains while maintaining output quality and format consistency.

## Why DSPy?

### Traditional LLM Challenges
```python
# Without DSPy - Inconsistent outputs
response = llm.complete("Analyze Bitcoin market")
# Output varies wildly in format and structure
```

### DSPy Solution
```python
# With DSPy - Structured, consistent outputs
class MarketAnalysis(dspy.Signature):
    """Analyze market and provide trading recommendation."""
    market_title: str = dspy.InputField()
    current_context: str = dspy.InputField()

    analysis: str = dspy.OutputField(desc="Market analysis")
    recommendation: str = dspy.OutputField(desc="BUY_YES or BUY_NO")
    confidence: int = dspy.OutputField(desc="0-100 confidence score")
```

## Core Implementation

### Configuration

```python
# src/utils/dspy_utilities.py
import dspy
from dspy import FunctionalModule, Signature

def configure_dspy_environment(
    api_provider="groq",
    model="llama-3.3-70b-versatile",
    api_key=None,
    temperature=0.1,
    top_p=0.5,
    max_tokens=512
):
    """Configure DSPy with specified LLM backend."""

    if api_provider == "fireworks":
        lm = dspy.LM(
            model=f'fireworks/{model}',
            api_key=api_key,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            cache=False
        )
    elif api_provider == "groq":
        lm = dspy.LM(
            model=f'groq/{model}',
            api_key=api_key,
            temperature=temperature,
            cache=False
        )

    dspy.configure(lm=lm)
    return lm
```

### Signature Definitions

```python
# Market Analysis Signature
class AnalyzeMarket(dspy.Signature):
    """Generate trading analysis for prediction market."""

    market_title: str = dspy.InputField(
        desc="The prediction market question"
    )
    market_description: str = dspy.InputField(
        desc="Additional market details"
    )
    current_context: str = dspy.InputField(
        desc="Current real-world context from research"
    )

    key_factors: str = dspy.OutputField(
        desc="3-4 key factors affecting this market"
    )
    analysis: str = dspy.OutputField(
        desc="Brief analysis in Vinnie's voice"
    )
    recommendation: str = dspy.OutputField(
        desc="BUY_YES, BUY_NO, or HOLD"
    )
    confidence: int = dspy.OutputField(
        desc="Confidence percentage (0-100)"
    )
```

### Module Architecture

```python
class DSPyEnhancedAIGGFlow(FunctionalModule):
    """Main analysis pipeline using DSPy."""

    def __init__(self):
        super().__init__()

        # Configure DSPy environment
        self.lm = configure_dspy_environment(
            api_provider="fireworks",
            model="accounts/fireworks/models/qwen3-235b-a22b-instruct-2507",
            temperature=0.7
        )

        # Initialize analysis modules
        self.market_analyzer = dspy.ChainOfThought(AnalyzeMarket)
        self.response_formatter = dspy.Predict(FormatResponse)

    def forward(self, market_query: str) -> AnalysisResult:
        """Process market query through analysis pipeline."""

        # Step 1: Find relevant market
        market = self.find_market(market_query)

        # Step 2: Gather context if needed
        context = self.gather_context(market)

        # Step 3: Generate analysis
        analysis = self.market_analyzer(
            market_title=market.title,
            market_description=market.description,
            current_context=context
        )

        # Step 4: Format response
        response = self.response_formatter(
            analysis=analysis.analysis,
            recommendation=analysis.recommendation,
            confidence=analysis.confidence,
            market_url=market.url
        )

        return response
```

## Advanced Features

### Chain of Thought Reasoning

```python
class ChainOfThoughtAnalysis(dspy.Module):
    """Multi-step reasoning for complex markets."""

    def __init__(self):
        self.think = dspy.ChainOfThought(
            "question -> rationale -> answer"
        )

    def forward(self, question):
        # DSPy automatically generates reasoning steps
        return self.think(question=question)
```

### Response Validation

```python
class ValidatedResponse(dspy.Module):
    """Ensure response meets quality standards."""

    def __init__(self):
        self.generate = dspy.ChainOfThought(AnalyzeMarket)
        self.validate = dspy.Assert(
            lambda x: x.confidence >= 50,
            "Confidence must be at least 50%"
        )

    def forward(self, **kwargs):
        response = self.generate(**kwargs)
        self.validate(response)
        return response
```

### Persona Integration

```python
class VinniePersona(dspy.Signature):
    """Format response in Vinnie's Brooklyn bookmaker voice."""

    analysis: str = dspy.InputField()
    recommendation: str = dspy.InputField()

    vinnie_says: str = dspy.OutputField(
        desc="""Rewrite in Vinnie's voice:
        - Start with 'Word is...' or 'Smart money says...'
        - Use betting slang: 'the line', 'juice', 'action'
        - Keep it under 280 chars
        - End with confidence and recommendation"""
    )
```

## Performance Optimization

### Prompt Caching

```python
# Cache commonly used prompts
@lru_cache(maxsize=100)
def cached_analysis(market_hash: str, context_hash: str):
    return dspy.Predict(AnalyzeMarket)(
        market_title=market_from_hash(market_hash),
        current_context=context_from_hash(context_hash)
    )
```

### Batch Processing

```python
def batch_analyze_markets(markets: List[Market]):
    """Analyze multiple markets efficiently."""

    with dspy.context(vectorize=True):
        results = []
        for market_batch in chunks(markets, size=10):
            batch_results = self.analyzer(
                market_titles=[m.title for m in market_batch],
                contexts=[m.context for m in market_batch]
            )
            results.extend(batch_results)
    return results
```

### Token Optimization

```python
class OptimizedAnalysis(dspy.Signature):
    """Minimize token usage while maintaining quality."""

    # Compressed inputs
    market: str = dspy.InputField(desc="Market title only")
    facts: str = dspy.InputField(desc="Key facts, bullet points")

    # Structured outputs
    rec: str = dspy.OutputField(desc="YES/NO/HOLD")
    conf: int = dspy.OutputField(desc="50-100")
    why: str = dspy.OutputField(desc="1-2 sentences max")
```

## Error Handling

### Graceful Degradation

```python
class RobustAnalysis(dspy.Module):
    """Handle failures gracefully."""

    def forward(self, market_query: str):
        try:
            # Primary analysis path
            return self.primary_analyzer(market_query)
        except Exception as e:
            logger.warning(f"Primary failed: {e}")

            try:
                # Fallback to simpler analysis
                return self.fallback_analyzer(market_query)
            except Exception as e2:
                logger.error(f"Fallback failed: {e2}")

                # Return safe default
                return AnalysisResult(
                    recommendation="HOLD",
                    confidence=50,
                    analysis="Market unclear, checking again soon."
                )
```

### Retry Logic

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10)
)
def analyze_with_retry(self, market):
    """Retry analysis on transient failures."""
    return self.analyzer(market)
```

## Testing DSPy Modules

### Unit Tests

```python
def test_analysis_signature():
    """Test DSPy signature outputs."""

    with dspy.context(lm=dspy.MockLM()):
        analyzer = dspy.Predict(AnalyzeMarket)

        result = analyzer(
            market_title="Will Bitcoin reach $200k?",
            current_context="Bitcoin at $95k, declining"
        )

        assert result.recommendation in ["BUY_YES", "BUY_NO", "HOLD"]
        assert 0 <= result.confidence <= 100
        assert len(result.analysis) > 0
```

### Integration Tests

```python
def test_full_pipeline():
    """Test complete DSPy pipeline."""

    flow = DSPyEnhancedAIGGFlow()

    test_queries = [
        "Will Bitcoin hit 200k?",
        "Fed rate cuts coming?",
        "Trump 2028 possible?"
    ]

    for query in test_queries:
        result = flow.analyze_query(query)
        assert result.market_url
        assert result.confidence >= 50
        assert result.recommendation != "UNCLEAR"
```

## DSPy Best Practices

### 1. Signature Design
- Keep input fields focused and specific
- Use clear output field descriptions
- Validate outputs with assertions

### 2. Module Composition
- Build complex flows from simple modules
- Use ChainOfThought for reasoning tasks
- Apply Predict for straightforward mappings

### 3. Performance
- Cache frequently used signatures
- Batch similar requests
- Monitor token usage

### 4. Debugging
```python
# Enable DSPy tracing
with dspy.context(trace=True):
    result = analyzer(market)
    print(dspy.inspect())  # Shows reasoning steps
```

## Configuration Examples

### Development Setup
```python
# Fast, cheap testing
configure_dspy_environment(
    api_provider="groq",
    model="alternative-model",
    temperature=0.3,
    max_tokens=256
)
```

### Production Setup
```python
# High quality, consistent
configure_dspy_environment(
    api_provider="fireworks",
    model="qwen3-235b-a22b-instruct-2507",
    temperature=0.7,
    max_tokens=512,
    top_p=0.9
)
```

## Next Steps

- [Analysis Flow](analysis-flow.md) - Complete pipeline walkthrough
- [Response Formatting](response-formatting.md) - Output structure
- [Research Integration](research-integration.md) - Context gathering