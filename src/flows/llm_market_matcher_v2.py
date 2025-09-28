"""
LLM Market Matcher V2 - Two-stage category-based matching with strict relevance
"""
import os
from typing import List, Dict, Optional, Any, Tuple
import dspy
from dspy import InputField, OutputField
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class CategorySelection(dspy.Signature):
    """Select Polymarket categories that might contain relevant markets"""
    query: str = InputField(desc="User's search query")
    available_categories: List[str] = InputField(desc="All available Polymarket categories")
    selected_categories: List[str] = OutputField(
        desc="Categories that might have relevant markets (can be multiple)"
    )
    reasoning: str = OutputField(desc="Brief explanation of category selection")


class StrictRelevanceCheck(dspy.Signature):
    """Check if a market is directly relevant to the query (not just tangentially related)"""
    query: str = InputField(desc="User's search query")
    market_title: str = InputField(desc="The market's title/question")
    is_relevant: bool = OutputField(
        desc="True only if market directly addresses the query topic"
    )
    keywords_matched: List[str] = OutputField(
        desc="Specific words/concepts that connect query to market"
    )


class TieredMarketScoring(dspy.Signature):
    """Score market relevance with explicit tiers"""
    query: str = InputField(desc="User's search query")
    market_title: str = InputField(desc="The market's title/question")
    relevance_tier: str = OutputField(
        desc="HIGH (0.8-1.0): Direct match | MEDIUM (0.4-0.7): Related | LOW (0.0-0.3): Weak"
    )
    score: float = OutputField(desc="Exact score within the tier range")
    reasoning: str = OutputField(desc="Why this score was assigned")


class MarketMatch(BaseModel):
    """Structured market match result"""
    market_id: str
    title: str
    category: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_tier: str
    reasoning: str
    keywords_matched: List[str] = Field(default_factory=list)


class LLMMarketMatcherV2:
    """Two-stage market matcher with category filtering and strict relevance"""
    
    def __init__(self, lm: Optional[dspy.LM] = None):
        """Initialize with optional language model"""
        self.lm = lm
        if not self.lm:
            self._configure_default_lm()
            
        # Initialize DSPy modules
        self.category_selector = dspy.ChainOfThought(CategorySelection)
        self.relevance_checker = dspy.ChainOfThought(StrictRelevanceCheck)
        self.market_scorer = dspy.ChainOfThought(TieredMarketScoring)
        
        logger.info("LLMMarketMatcherV2 initialized with two-stage matching")
    
    def _configure_default_lm(self):
        """Configure Fireworks AI as default LLM"""
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError("FIREWORKS_API_KEY not found in environment")
        
        self.lm = dspy.LM(
            model="fireworks_ai/accounts/fireworks/models/qwen3-235b-a22b-instruct-2507",
            api_key=api_key,
            temperature=0.1  # Low temperature for consistent scoring
        )
        dspy.configure(lm=self.lm)
        logger.info("Configured Fireworks AI LLM for market matching")
    
    def select_categories(
        self, 
        query: str, 
        available_categories: List[str]
    ) -> Tuple[List[str], str]:
        """Stage 1: Select relevant categories for the query"""
        try:
            result = self.category_selector(
                query=query,
                available_categories=available_categories
            )
            
            selected = result.selected_categories
            reasoning = result.reasoning
            
            logger.info(f"Selected {len(selected)} categories for query '{query}': {selected}")
            return selected, reasoning
            
        except Exception as e:
            logger.error(f"Category selection failed: {e}")
            # Fallback: return all categories
            return available_categories, "Error in category selection, including all"
    
    def check_relevance(self, query: str, market_title: str) -> Tuple[bool, List[str]]:
        """Check if market is directly relevant (not tangentially)"""
        try:
            result = self.relevance_checker(
                query=query,
                market_title=market_title
            )
            
            return result.is_relevant, result.keywords_matched
            
        except Exception as e:
            logger.error(f"Relevance check failed: {e}")
            # Conservative fallback
            return False, []
    
    def score_market(self, query: str, market_title: str) -> Tuple[str, float, str]:
        """Score a relevant market with tiered scoring"""
        try:
            result = self.market_scorer(
                query=query,
                market_title=market_title
            )
            
            tier = result.relevance_tier
            score = result.score
            reasoning = result.reasoning
            
            # Validate score is within tier range
            if tier == "HIGH" and not (0.8 <= score <= 1.0):
                score = 0.9
            elif tier == "MEDIUM" and not (0.4 <= score <= 0.7):
                score = 0.55
            elif tier == "LOW" and not (0.0 <= score <= 0.3):
                score = 0.2
                
            return tier, score, reasoning
            
        except Exception as e:
            logger.error(f"Market scoring failed: {e}")
            return "LOW", 0.1, f"Scoring error: {e}"
    
    def find_best_markets(
        self,
        query: str,
        markets_by_category: Dict[str, List[Dict[str, Any]]],
        available_categories: List[str],
        top_k: int = 10
    ) -> List[MarketMatch]:
        """
        Two-stage market matching process
        
        Args:
            query: User's search query
            markets_by_category: Dict mapping category -> list of markets in that category
            available_categories: List of all available categories
            top_k: Number of top markets to return
            
        Returns:
            List of best matching markets with scores
        """
        # Stage 1: Select relevant categories
        selected_categories, category_reasoning = self.select_categories(
            query, available_categories
        )
        
        logger.info(f"Stage 1 - Categories selected: {selected_categories}")
        
        # Gather all markets from selected categories
        candidate_markets = []
        for category in selected_categories:
            if category in markets_by_category:
                markets = markets_by_category[category]
                for market in markets:
                    market['category'] = category  # Tag with category
                    candidate_markets.append(market)
        
        logger.info(f"Stage 1 - Found {len(candidate_markets)} candidate markets")
        
        # Stage 2: Check relevance and score markets
        matches = []
        
        for market in candidate_markets:
            market_id = market.get('market_id', market.get('id', 'unknown'))
            title = market.get('title', market.get('question', ''))
            category = market.get('category', '')
            
            # First, check if directly relevant
            is_relevant, keywords = self.check_relevance(query, title)
            
            if not is_relevant:
                logger.debug(f"Filtered out irrelevant market: {title[:50]}...")
                continue
            
            # If relevant, get tiered score
            tier, score, reasoning = self.score_market(query, title)
            
            match = MarketMatch(
                market_id=market_id,
                title=title,
                category=category,
                relevance_score=score,
                relevance_tier=tier,
                reasoning=reasoning,
                keywords_matched=keywords
            )
            
            matches.append(match)
            logger.debug(f"Scored market: {title[:50]}... -> {tier} ({score:.3f})")
        
        # Sort by score and return top k
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"Stage 2 - Returning top {top_k} of {len(matches)} relevant markets")
        return matches[:top_k]


# Example usage for testing
def test_matcher():
    """Test the two-stage matcher"""
    matcher = LLMMarketMatcherV2()
    
    # Mock categories
    categories = [
        "Crypto", "Politics", "Sports", "Entertainment", 
        "Geopolitics", "Technology", "Economics"
    ]
    
    # Mock markets by category
    markets_by_category = {
        "Crypto": [
            {"id": "1", "title": "Will Bitcoin reach $200,000 by end of 2025?"},
            {"id": "2", "title": "Will Ethereum flip Bitcoin in market cap?"}
        ],
        "Geopolitics": [
            {"id": "3", "title": "Will China invade Taiwan before 2026?"},
            {"id": "4", "title": "Will Russia Ukraine conflict end in 2025?"}
        ],
        "Politics": [
            {"id": "5", "title": "Will Biden run for second term?"},
            {"id": "6", "title": "Will Trump win 2024 Republican nomination?"}
        ]
    }
    
    # Test query
    query = "china taiwan tensions escalating"
    
    results = matcher.find_best_markets(
        query=query,
        markets_by_category=markets_by_category,
        available_categories=categories,
        top_k=5
    )
    
    for i, match in enumerate(results, 1):
        print(f"\n{i}. {match.title}")
        print(f"   Category: {match.category}")
        print(f"   Tier: {match.relevance_tier} (Score: {match.relevance_score:.3f})")
        print(f"   Keywords: {match.keywords_matched}")
        print(f"   Reasoning: {match.reasoning}")


if __name__ == "__main__":
    test_matcher()