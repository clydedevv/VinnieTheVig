#!/usr/bin/env python3
"""
LLM-Based Market Matching using DSPy
No hardcoded logic - pure semantic understanding using LLMs
"""
import os
import dspy
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class MarketData:
    """Market data for matching"""
    id: str
    title: str
    category: str
    end_date: Optional[str]
    active: bool
    market_slug: Optional[str] = None


class MarketRelevance(BaseModel):
    """Structured output for market relevance scoring"""
    relevance_score: float = Field(description="Relevance score from 0.0 to 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of the relevance score")
    key_matches: List[str] = Field(description="Key concepts that matched between query and market")
    time_relevance: str = Field(description="How well the market's timeframe matches the query's time context")


class QueryContext(BaseModel):
    """Extracted context from user query"""
    main_topic: str = Field(description="Primary topic/subject of the query")
    entities: List[str] = Field(description="Key entities mentioned (people, organizations, etc)")
    time_context: str = Field(description="Time references in the query (e.g., 'this year', 'by June', 'in 2025')")
    price_targets: List[str] = Field(description="Any price levels or numerical targets mentioned")
    intent: str = Field(description="What the user is trying to find out")


class ScoreMarket(dspy.Signature):
    """Score a single market's relevance to a query using semantic understanding"""
    
    query: str = dspy.InputField(description="User's search query")
    market_title: str = dspy.InputField(description="The market's title/question")
    market_category: str = dspy.InputField(description="Market category")
    market_end_date: str = dspy.InputField(description="When the market resolves")
    current_date: str = dspy.InputField(description="Today's date for time context")
    
    relevance_score: float = dspy.OutputField(description="Relevance score from 0.0 to 1.0")
    reasoning: str = dspy.OutputField(description="Why this score was given")


class ExtractQueryContext(dspy.Signature):
    """Extract semantic context from user query"""
    
    query: str = dspy.InputField(description="User's search query")
    current_date: str = dspy.InputField(description="Today's date for time context")
    
    main_topic: str = dspy.OutputField(description="Primary topic (e.g., 'Bitcoin price prediction', 'NBA championship')")
    entities: str = dspy.OutputField(description="Comma-separated key entities")
    time_context: str = dspy.OutputField(description="Time references (e.g., 'end of 2025', 'next 6 months')")
    price_targets: str = dspy.OutputField(description="Comma-separated price levels or numbers")
    intent: str = dspy.OutputField(description="User's intent in 10 words or less")


class BatchScoreMarkets(dspy.Signature):
    """Score multiple markets at once for efficiency"""
    
    query: str = dspy.InputField(description="User's search query")
    query_context: str = dspy.InputField(description="Extracted context from the query")
    markets_json: str = dspy.InputField(description="JSON array of markets with id, title, category, end_date")
    current_date: str = dspy.InputField(description="Today's date for time context")
    
    scores_json: str = dspy.OutputField(description="JSON array of {id, score, reasoning} for each market")


class LLMMarketMatcher:
    """Pure LLM-based market matching - no hardcoded logic"""
    
    def __init__(self, lm_model: Optional[str] = None):
        """Initialize with DSPy configuration"""
        # Configure LLM
        if lm_model:
            # Use specified model
            perplexity_key = os.getenv("PERPLEXITY_API_KEY")
            if perplexity_key and "perplexity" in lm_model:
                lm = dspy.LM(
                    model=lm_model,
                    api_key=perplexity_key,
                    api_base="https://api.perplexity.ai"
                )
                dspy.configure(lm=lm)
            else:
                # Default to a different model if needed
                lm = dspy.LM(model=lm_model)
                dspy.configure(lm=lm)
        else:
            # Use default Fireworks configuration
            self._configure_default_lm()
        
        # Initialize DSPy modules
        self.query_analyzer = dspy.Predict(ExtractQueryContext)
        self.market_scorer = dspy.Predict(ScoreMarket)
        self.batch_scorer = dspy.Predict(BatchScoreMarkets)
        
        self.current_date = datetime.now().strftime("%Y-%m-%d")
    
    def _configure_default_lm(self):
        """Configure default LLM (Fireworks)"""
        fireworks_key = os.getenv("FIREWORKS_API_KEY")
        if fireworks_key:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            try:
                from src.utils.dspy_utilities import lm as fireworks_lm
                dspy.configure(lm=fireworks_lm)
            except:
                # Fallback to direct configuration
                lm = dspy.LM(
                    model="accounts/fireworks/models/qwen3p5-72b-instruct",
                    api_key=fireworks_key,
                    api_base="https://api.fireworks.ai/inference/v1"
                )
                dspy.configure(lm=lm)
    
    def analyze_query(self, query: str) -> QueryContext:
        """Extract semantic context from query using LLM"""
        try:
            result = self.query_analyzer(
                query=query,
                current_date=self.current_date
            )
            
            # Parse the outputs
            entities = [e.strip() for e in result.entities.split(',') if e.strip()]
            price_targets = [p.strip() for p in result.price_targets.split(',') if p.strip()]
            
            return QueryContext(
                main_topic=result.main_topic,
                entities=entities,
                time_context=result.time_context,
                price_targets=price_targets,
                intent=result.intent
            )
        except Exception as e:
            print(f"Error analyzing query: {e}")
            return QueryContext(
                main_topic=query,
                entities=[],
                time_context="",
                price_targets=[],
                intent="Find relevant prediction markets"
            )
    
    def score_single_market(self, query: str, market: MarketData) -> Tuple[float, str]:
        """Score a single market using LLM understanding"""
        try:
            result = self.market_scorer(
                query=query,
                market_title=market.title,
                market_category=market.category,
                market_end_date=market.end_date or "No end date specified",
                current_date=self.current_date
            )
            
            # Ensure score is valid
            score = float(result.relevance_score)
            score = max(0.0, min(1.0, score))
            
            return score, result.reasoning
        except Exception as e:
            print(f"Error scoring market {market.id}: {e}")
            return 0.0, "Error in scoring"
    
    def score_markets_batch(self, query: str, markets: List[MarketData], 
                           query_context: Optional[QueryContext] = None) -> List[Dict[str, Any]]:
        """Score multiple markets in a single LLM call for efficiency"""
        if not markets:
            return []
        
        # Get query context if not provided
        if not query_context:
            query_context = self.analyze_query(query)
        
        # Prepare markets for JSON
        markets_data = []
        for market in markets:
            markets_data.append({
                "id": market.id,
                "title": market.title,
                "category": market.category,
                "end_date": market.end_date or "No end date"
            })
        
        try:
            # Create context string
            context_str = f"Topic: {query_context.main_topic}, "
            if query_context.entities:
                context_str += f"Entities: {', '.join(query_context.entities)}, "
            if query_context.time_context:
                context_str += f"Time: {query_context.time_context}, "
            if query_context.price_targets:
                context_str += f"Prices: {', '.join(query_context.price_targets)}, "
            context_str += f"Intent: {query_context.intent}"
            
            # Batch score markets
            result = self.batch_scorer(
                query=query,
                query_context=context_str,
                markets_json=json.dumps(markets_data),
                current_date=self.current_date
            )
            
            # Parse the JSON response
            scores_data = json.loads(result.scores_json)
            
            # Create results with validation
            results = []
            for score_item in scores_data:
                try:
                    score = float(score_item.get('score', 0.0))
                    score = max(0.0, min(1.0, score))
                    
                    results.append({
                        'market_id': score_item['id'],
                        'relevance_score': score,
                        'reasoning': score_item.get('reasoning', 'No reasoning provided')
                    })
                except Exception as e:
                    print(f"Error parsing score item: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error in batch scoring: {e}")
            # Fallback to individual scoring
            return self._fallback_individual_scoring(query, markets)
    
    def _score_batch_with_logging(self, query: str, batch: List[MarketData], 
                                  query_context: QueryContext, batch_num: int, 
                                  total_batches: int) -> List[Dict[str, Any]]:
        """Score a batch with progress logging"""
        print(f"   🔄 Scoring batch {batch_num}/{total_batches}...")
        return self.score_markets_batch(query, batch, query_context)
    
    def _fallback_individual_scoring(self, query: str, markets: List[MarketData]) -> List[Dict[str, Any]]:
        """Fallback to scoring markets individually if batch fails"""
        results = []
        for market in markets:
            score, reasoning = self.score_single_market(query, market)
            results.append({
                'market_id': market.id,
                'relevance_score': score,
                'reasoning': reasoning
            })
        return results
    
    def find_best_markets(self, query: str, markets: List[MarketData], 
                         top_k: int = 10) -> List[Tuple[MarketData, float, str]]:
        """Find the best matching markets using pure LLM understanding"""
        if not markets:
            return []
        
        print(f"🤖 LLM analyzing query: '{query}'")
        
        # Analyze query context
        query_context = self.analyze_query(query)
        print(f"   📌 Topic: {query_context.main_topic}")
        print(f"   👥 Entities: {', '.join(query_context.entities) if query_context.entities else 'None'}")
        print(f"   ⏰ Time context: {query_context.time_context or 'None'}")
        print(f"   💰 Price targets: {', '.join(query_context.price_targets) if query_context.price_targets else 'None'}")
        
        # Score markets in batches for efficiency - PARALLELIZED
        batch_size = 20  # Process 20 markets at a time
        all_scores = []
        
        # Create batches
        batches = []
        for i in range(0, len(markets), batch_size):
            batch = markets[i:i + batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(markets) + batch_size - 1)//batch_size
            batches.append((batch_num, total_batches, batch))
        
        print(f"   🚀 Scoring {len(batches)} batches in parallel...")
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all batch scoring tasks
            future_to_batch = {}
            for batch_num, total_batches, batch in batches:
                future = executor.submit(
                    self._score_batch_with_logging,
                    query, batch, query_context, batch_num, total_batches
                )
                future_to_batch[future] = batch
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    batch_scores = future.result()
                    
                    # Map scores back to markets
                    score_map = {score['market_id']: score for score in batch_scores}
                    
                    for market in batch:
                        if market.id in score_map:
                            score_data = score_map[market.id]
                            all_scores.append((
                                market,
                                score_data['relevance_score'],
                                score_data['reasoning']
                            ))
                except Exception as e:
                    print(f"   ⚠️ Batch scoring failed: {e}")
                    # Fallback to individual scoring for this batch
                    for market in batch:
                        score, reasoning = self.score_single_market(query, market)
                        all_scores.append((market, score, reasoning))
        
        # Sort by score
        all_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top K
        top_markets = all_scores[:top_k]
        
        print(f"   ✅ Found {len(top_markets)} relevant markets")
        if top_markets:
            print("   🎯 Top matches:")
            for i, (market, score, reasoning) in enumerate(top_markets[:3], 1):
                print(f"      {i}. [{score:.3f}] {market.title[:60]}...")
                print(f"         → {reasoning[:80]}...")
        
        return top_markets


class DSPySearchOptimizer(dspy.Module):
    """DSPy Module for optimizing search queries for better market matching"""
    
    def __init__(self):
        super().__init__()
        self.generate_searches = dspy.ChainOfThought("query -> search_terms")
    
    def forward(self, query: str) -> str:
        """Generate optimized search terms"""
        prediction = self.generate_searches(query=query)
        return prediction.search_terms


def test_llm_matcher():
    """Test the LLM-based matcher"""
    matcher = LLMMarketMatcher("perplexity/sonar")
    
    # Test markets
    test_markets = [
        MarketData(
            id="btc-200k",
            title="Will Bitcoin reach $200,000 by end of 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="btc-150k-june",
            title="Will Bitcoin hit $150,000 by June 2025?",
            category="Crypto",
            end_date="2025-06-30T23:59:59Z",
            active=True
        ),
        MarketData(
            id="fed-cuts",
            title="How many times will the Fed cut rates in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="ukraine-ceasefire",
            title="Will Russia and Ukraine agree to a ceasefire in 2025?",
            category="Geopolitics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        )
    ]
    
    # Test queries
    test_queries = [
        "Bitcoin reaching $200k this year",
        "Federal Reserve interest rate policy",
        "Russia Ukraine conflict resolution"
    ]
    
    print("="*80)
    print("TESTING LLM-BASED MARKET MATCHER")
    print("="*80)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-"*60)
        
        results = matcher.find_best_markets(query, test_markets, top_k=3)
        
        for market, score, reasoning in results:
            print(f"\n[{score:.3f}] {market.title}")
            print(f"       Reasoning: {reasoning}")


if __name__ == "__main__":
    test_llm_matcher()