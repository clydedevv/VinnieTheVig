#!/usr/bin/env python3
"""
LLM-Based Market Search Endpoint
Adds a new endpoint to the API that uses LLM-based semantic matching
"""
from fastapi import Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.flows.llm_market_matcher import LLMMarketMatcher, MarketData


class LLMSearchRequest(BaseModel):
    """Request model for LLM-based search"""
    query: str
    limit: int = 10
    include_reasoning: bool = True


class LLMMarketResult(BaseModel):
    """Enhanced market result with LLM reasoning"""
    market_id: str
    title: str
    category: Optional[str] = None
    end_date: Optional[str] = None
    relevance_score: float
    reasoning: Optional[str] = None
    market_slug: Optional[str] = None


class LLMSearchResponse(BaseModel):
    """Response for LLM-based search"""
    query: str
    query_understanding: dict
    markets: List[LLMMarketResult]
    search_method: str = "llm_semantic"


# This would be added to the main FastAPI app
async def search_markets_llm(
    request: LLMSearchRequest,
    # These would come from the database connection
    get_all_active_markets_func
):
    """
    Search markets using LLM-based semantic understanding
    
    This endpoint uses language models to understand the semantic meaning
    of queries rather than relying on keyword matching.
    """
    try:
        # Initialize LLM matcher
        matcher = LLMMarketMatcher()
        
        # Get all active markets from database
        all_markets = await get_all_active_markets_func()
        
        # Convert to MarketData objects
        market_candidates = []
        for market in all_markets:
            market_candidates.append(MarketData(
                id=market['market_id'],
                title=market['title'],
                category=market.get('category', ''),
                end_date=market.get('end_date'),
                active=market.get('active', True),
                market_slug=market.get('market_slug', '')
            ))
        
        # First, analyze the query to understand it
        query_context = matcher.analyze_query(request.query)
        
        # Find best matching markets
        results = matcher.find_best_markets(
            query=request.query,
            markets=market_candidates,
            top_k=request.limit
        )
        
        # Build response
        market_results = []
        for market, score, reasoning in results:
            result = LLMMarketResult(
                market_id=market.id,
                title=market.title,
                category=market.category,
                end_date=market.end_date,
                relevance_score=score,
                market_slug=market.market_slug
            )
            
            if request.include_reasoning:
                result.reasoning = reasoning
            
            market_results.append(result)
        
        return LLMSearchResponse(
            query=request.query,
            query_understanding={
                "main_topic": query_context.main_topic,
                "entities": query_context.entities,
                "time_context": query_context.time_context,
                "price_targets": query_context.price_targets,
                "intent": query_context.intent
            },
            markets=market_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example of how to add this to the main API
def add_llm_endpoints(app, get_db_connection):
    """Add LLM-based endpoints to the FastAPI app"""
    
    @app.post("/markets/search/llm", response_model=LLMSearchResponse)
    async def llm_search_endpoint(request: LLMSearchRequest):
        """
        Search markets using LLM-based semantic matching
        
        This uses language models to understand query intent and meaning,
        providing more accurate results for complex or ambiguous queries.
        
        Benefits over traditional search:
        - Understands semantic meaning, not just keywords
        - Handles typos, slang, and informal language
        - Identifies intent and context
        - No hardcoded rules to maintain
        - Automatically adapts to new market types
        """
        
        # Function to get all active markets
        async def get_all_active_markets():
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT market_id, title, category, end_date, active, market_slug
                        FROM polymarket_markets
                        WHERE active = true
                        ORDER BY last_refreshed DESC
                        LIMIT 1000
                    """)
                    return cur.fetchall()
        
        return await search_markets_llm(request, get_all_active_markets)
    
    @app.get("/markets/search/compare")
    async def compare_search_methods(
        q: str = Query(..., description="Search query"),
        limit: int = Query(5, description="Number of results")
    ):
        """
        Compare traditional vs LLM-based search results
        
        Useful for testing and understanding the differences between approaches.
        """
        # Get results from both methods
        
        # Traditional search (existing endpoint)
        traditional_response = await search_markets(q=q, limit=limit)
        
        # LLM-based search
        llm_request = LLMSearchRequest(query=q, limit=limit)
        llm_response = await llm_search_endpoint(llm_request)
        
        return {
            "query": q,
            "traditional_results": {
                "method": "keyword_matching",
                "total_found": traditional_response.total_count,
                "markets": [
                    {
                        "title": m.title,
                        "score": m.relevance_score
                    } for m in traditional_response.markets
                ]
            },
            "llm_results": {
                "method": "semantic_understanding",
                "query_understanding": llm_response.query_understanding,
                "markets": [
                    {
                        "title": m.title,
                        "score": m.relevance_score,
                        "reasoning": m.reasoning
                    } for m in llm_response.markets
                ]
            }
        }


# Usage in main.py:
# from api.llm_search_endpoint import add_llm_endpoints
# add_llm_endpoints(app, get_db_connection)