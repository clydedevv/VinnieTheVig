# Performance Optimization

## Parallelized Batch Scoring

### What Changed
- **Before**: Batches scored sequentially (batch 1 → batch 2 → batch 3)
- **After**: Batches scored in parallel using ThreadPoolExecutor

### Implementation Details
```python
# Uses 3 worker threads to process batches concurrently
with ThreadPoolExecutor(max_workers=3) as executor:
    # All batches submitted at once
    # Results collected as they complete
```

### Expected Performance Gain
- **Before**: 3 batches × 7 sec = 21 seconds sequential
- **After**: 3 batches in parallel ≈ 7-10 seconds total
- **Savings**: ~10-14 seconds

### Additional Optimization
- Reduced market candidates from 50 → 30
- Saves ~7 seconds of scoring time
- Still gets good coverage from search API

## Overall Impact
Expected reduction from 62 seconds to ~45-50 seconds:
- Parallel batch scoring: -10 sec
- Fewer markets to score: -7 sec
- Total savings: ~17 seconds (27% faster)

## Why This Is Safe
1. Each batch is independent - no shared state
2. LLM calls are thread-safe
3. Fallback to sequential if parallel fails
4. Results collected and sorted after all complete

## Further Optimizations (Not Implemented)
- Cache Perplexity research for repeated queries
- Use category-based filtering (v2 matcher) when categories are reliable
- Reduce Perplexity research depth for faster queries