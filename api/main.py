#!/usr/bin/env python3
"""
AIGG Insights API - FastAPI service for market data and insights
Provides endpoints for Ankur to test market matching and research functionality
"""
import logging
import os
import re
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIGG Insights API",
    description="API for accessing Polymarket data and research insights",
    version="1.0.0"
)

# Add CORS middleware so Ankur can access from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    """Get database connection using environment variables"""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Response models
class Market(BaseModel):
    market_id: str
    title: str
    category: Optional[str] = None
    end_date: Optional[datetime] = None
    active: bool = True
    relevance_score: Optional[float] = None
    market_slug: Optional[str] = None  # NEW: Official market slug for URLs

class MarketsResponse(BaseModel):
    markets: List[Market]
    total_count: int
    query: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_status: str
    total_markets: int
    active_markets: int

# Utility functions
def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calculate Levenshtein similarity ratio between two strings"""
    if len(s1) < len(s2):
        return levenshtein_ratio(s2, s1)

    if len(s2) == 0:
        return 0.0

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    max_len = max(len(s1), len(s2))
    return 1.0 - (previous_row[-1] / max_len)

def calculate_market_relevance(query: str, market: Dict[str, Any]) -> float:
    """Calculate relevance score for a market given a query - ENHANCED WITH DATE CONTEXT"""
    query_lower = query.lower().strip()
    title_lower = (market.get('title') or '').lower()
    category_lower = (market.get('category') or '').lower()
    
    relevance_score = 0.0
    
    # Parse end_date for time-based scoring
    end_date = market.get('end_date')
    market_month = None
    market_year = None
    if end_date:
        try:
            if isinstance(end_date, str):
                # Handle ISO format
                parsed_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                market_month = parsed_date.month
                market_year = parsed_date.year
            else:
                market_month = end_date.month
                market_year = end_date.year
        except:
            pass
    
    # 1. EXACT PHRASE MATCHING (highest priority)
    if query_lower in title_lower:
        relevance_score += 0.8  # Reduced from 1.0 to prevent domination
    
    # 1b. PHRASE-LEVEL MATCHING (new)
    # Check for important multi-word phrases
    important_phrases = [
        'federal reserve', 'interest rate', 'interest rates',
        'rate cut', 'rate cuts', 'rate hike',
        'champions league', 'premier league', 'nba championship',
        'this year', 'by june', 'by end of', 'end of year'
    ]
    
    for phrase in important_phrases:
        if phrase in query_lower and phrase in title_lower:
            relevance_score += 0.5
    
    # 2. INDIVIDUAL KEYWORD MATCHING (more conservative)
    query_terms = set(re.findall(r'\b\w+\b', query_lower))
    title_terms = set(re.findall(r'\b\w+\b', title_lower))
    
    if query_terms and title_terms:
        exact_matches = query_terms.intersection(title_terms)
        exact_match_ratio = len(exact_matches) / len(query_terms)
        
        # Penalize if important terms are missing
        if len(query_terms) > 2 and exact_match_ratio < 0.5:
            relevance_score += exact_match_ratio * 0.4  # Reduced penalty
        else:
            relevance_score += exact_match_ratio * 0.6  # Reduced from 0.8
        
        # Bonus for multiple keyword matches (more selective)
        if len(exact_matches) >= 3:  # Increased threshold from 2 to 3
            relevance_score += 0.2  # Reduced from 0.3
    
    # 3. TIME CONTEXT AWARENESS (NEW - HIGH PRIORITY FOR DATE-SENSITIVE QUERIES)
    time_context_bonus = 0.0
    
    # Check for time-related keywords in query
    year_2025_refs = ['2025', 'this year', 'by end of year', 'year end', 'december', 'end of the year']
    near_term_refs = ['june', 'july', 'august', 'september', 'this month', 'next month', 'soon']
    
    has_year_context = any(ref in query_lower for ref in year_2025_refs)
    has_near_term_context = any(ref in query_lower for ref in near_term_refs)
    
    if market_month and market_year == 2025:
        if has_year_context and not has_near_term_context:
            # Query is asking about "this year" - prefer markets ending later in 2025
            if market_month >= 11:  # Nov-Dec markets
                time_context_bonus += 0.4  # Strong bonus for end-of-year markets
            elif market_month >= 9:  # Sep-Oct markets  
                time_context_bonus += 0.2  # Medium bonus
            elif market_month >= 7:  # Jul-Aug markets
                time_context_bonus += 0.1  # Small bonus
            else:  # Jan-Jun markets
                time_context_bonus -= 0.2  # Penalty for early-year markets when asking about "this year"
        
        elif has_near_term_context:
            # Query is asking about near-term - prefer markets ending soon
            if market_month <= 7:  # Jan-Jul markets
                time_context_bonus += 0.3
            elif market_month <= 9:  # Aug-Sep markets
                time_context_bonus += 0.1
            else:  # Oct-Dec markets
                time_context_bonus -= 0.1
    
    relevance_score += time_context_bonus
    
    # 4. SEMANTIC/SYNONYM MATCHING
    synonym_map = {
        'trump': ['donald'],
        'donald': ['trump'],
        'bitcoin': ['btc', 'crypto'],
        'btc': ['bitcoin', 'crypto'],
        'crypto': ['bitcoin', 'btc', 'cryptocurrency'],
        'election': ['voting', 'vote', 'elections'],
        'championship': ['finals', 'champion', 'winner'],
        'price': ['value', 'cost', 'hit', 'reach', 'reaching'],
        'ai': ['artificial intelligence'],
        'artificial intelligence': ['ai'],
        'federal reserve': ['fed', 'fomc', 'federal', 'reserve'],
        'fed': ['federal reserve', 'fomc', 'federal', 'reserve'],
        'interest': ['rate', 'rates'],
        'rate': ['interest', 'rates'],
        'rates': ['interest', 'rate'],
        'nuclear': ['atomic'],
        'war': ['conflict', 'fighting'],
        'this year': ['2025', 'end of year', 'year end'],
        'year': ['2025'],
        '200k': ['200000', '$200k', '$200,000'],
        '120k': ['120000', '$120k', '$120,000'],
        '150k': ['150000', '$150k', '$150,000']
    }
    
    synonym_bonus = 0.0
    for term in query_terms:
        if term in synonym_map:
            for synonym in synonym_map[term]:
                if synonym in title_lower:
                    synonym_bonus += 0.1  # Reduced from 0.2
    
    relevance_score += min(synonym_bonus, 0.2)  # Reduced cap from 0.4
    
    # 5. CATEGORY MATCHING
    category_map = {
        'trump': ['us-current-affairs', 'politics'],
        'election': ['us-current-affairs', 'politics'],
        'bitcoin': ['crypto'],
        'nba': ['sports', 'nba'],
        'basketball': ['sports', 'nba'],
        'tesla': ['tech', 'stocks'],
        'stock': ['tech', 'finance'],
        'federal reserve': ['economics', 'finance'],
        'nuclear': ['geopolitics', 'military'],
        'ai': ['tech', 'artificial intelligence'],
        'russia': ['geopolitics'],
        'ukraine': ['geopolitics']
    }
    
    category_bonus = 0.0
    for term in query_terms:
        if term in category_map:
            for expected_cat in category_map[term]:
                if expected_cat.lower() in category_lower:
                    category_bonus += 0.15  # Reduced from 0.3
    
    relevance_score += min(category_bonus, 0.2)  # Reduced cap from 0.4
    
    # 6. STRING SIMILARITY (refined)
    title_similarity = levenshtein_ratio(query_lower, title_lower)
    if title_similarity > 0.3:
        relevance_score += title_similarity * 0.3
    
    # 7. QUERY LENGTH CONSIDERATION
    if len(query_terms) <= 2:
        if exact_match_ratio < 0.5:
            relevance_score *= 0.7
    
    # 8. TITLE LENGTH CONSIDERATION
    title_word_count = len(title_terms)
    if title_word_count < 10:
        relevance_score += 0.1
    
    # 9. ACTIVE MARKET BONUS
    if market.get('active'):
        relevance_score += 0.05
    
    return min(relevance_score, 1.0)

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with database stats"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Test connection
                cur.execute("SELECT 1")
                
                # Get market counts
                cur.execute("SELECT COUNT(*) as total FROM polymarket_markets")
                total_count = cur.fetchone()['total']
                
                cur.execute("SELECT COUNT(*) as active FROM polymarket_markets WHERE active = true")
                active_count = cur.fetchone()['active']
                
                return HealthResponse(
                    status="healthy",
                    timestamp=str(datetime.utcnow()),
                    database_status="connected",
                    total_markets=total_count,
                    active_markets=active_count
                )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/markets", response_model=MarketsResponse)
async def get_markets(
    active: Optional[bool] = True,
    limit: int = Query(default=20, le=100),
    category: Optional[str] = None
):
    """Get markets with optional filters"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        market_id,
                        title,
                        category,
                        end_date,
                        active
                    FROM polymarket_markets 
                    WHERE 1=1
                """
                params = []

                if active:
                    query += " AND active = true"
                
                if category:
                    query += " AND category ILIKE %s"
                    params.append(f"%{category}%")

                query += " ORDER BY last_refreshed DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)
                markets_data = cur.fetchall()
                
                # Get total count
                count_query = "SELECT COUNT(*) as total FROM polymarket_markets WHERE 1=1"
                count_params = []
                if active:
                    count_query += " AND active = true"
                if category:
                    count_query += " AND category ILIKE %s"
                    count_params.append(f"%{category}%")
                
                cur.execute(count_query, count_params)
                total_count = cur.fetchone()['total']

                markets = [Market(**dict(market)) for market in markets_data]
                return MarketsResponse(markets=markets, total_count=total_count)

    except Exception as e:
        logger.error(f"Error fetching markets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/markets/search", response_model=MarketsResponse)
async def search_markets(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Number of results"),
    use_llm: bool = Query(False, description="Use LLM-based matching (slower but more accurate)")
):
    """Search markets with enhanced relevance scoring or LLM matching"""
    
    # If LLM matching requested, use the LLM matcher
    if use_llm:
        try:
            from flows.llm_market_matcher_v2 import LLMMarketMatcherV2
            import dspy
            
            # Initialize DSPy with Fireworks
            os.environ['FIREWORKS_API_KEY'] = os.getenv('FIREWORKS_API_KEY', '')
            lm = dspy.Fireworks(
                api_key=os.environ['FIREWORKS_API_KEY'],
                model="accounts/fireworks/models/qwen2p5-72b-instruct",
                max_tokens=1000
            )
            dspy.configure(lm=lm)
            
            matcher = LLMMarketMatcherV2()
            
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get all active markets
                    cur.execute("""
                        SELECT market_id, title, category, end_date, active, market_slug
                        FROM polymarket_markets 
                        WHERE active = true
                    """)
                    all_markets = cur.fetchall()
                    
                    # Get unique categories
                    cur.execute("""
                        SELECT DISTINCT category 
                        FROM polymarket_markets 
                        WHERE active = true AND category IS NOT NULL
                    """)
                    categories = [row['category'] for row in cur.fetchall()]
                    
                    # Group markets by category
                    markets_by_category = {}
                    for market in all_markets:
                        cat = market.get('category', 'Unknown')
                        if cat not in markets_by_category:
                            markets_by_category[cat] = []
                        markets_by_category[cat].append(dict(market))
                    
                    # Use LLM matcher
                    matches = matcher.find_best_markets(
                        query=q,
                        markets_by_category=markets_by_category,
                        available_categories=categories,
                        top_k=limit
                    )
                    
                    # Convert to API response format
                    top_markets = []
                    for match in matches:
                        # Find the full market data
                        for market in all_markets:
                            if market['market_id'] == match.market_id:
                                market_dict = dict(market)
                                market_dict['relevance_score'] = match.score
                                top_markets.append(market_dict)
                                break
                    
                    markets = [Market(**m) for m in top_markets]
                    return MarketsResponse(
                        markets=markets,
                        total_count=len(matches),
                        query=q
                    )
                    
        except Exception as e:
            logger.error(f"LLM matching failed: {e}, falling back to keyword matching")
            # Fall back to keyword matching
            use_llm = False
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if market_slug column exists
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'polymarket_markets' AND column_name = 'market_slug'
                """)
                has_slug = cur.fetchone() is not None
                
                # Get all active markets
                if has_slug:
                    cur.execute("""
                        SELECT market_id, title, category, end_date, active, market_slug
                        FROM polymarket_markets 
                        WHERE active = true
                    """)
                else:
                    cur.execute("""
                        SELECT market_id, title, category, end_date, active
                        FROM polymarket_markets 
                        WHERE active = true
                    """)
                markets_data = cur.fetchall()
                
                # Calculate relevance scores using Python function
                scored_markets = []
                for market in markets_data:
                    market_dict = dict(market)
                    relevance_score = calculate_market_relevance(q, market_dict)
                    if relevance_score > 0.1:  # Only include markets with some relevance
                        market_dict['relevance_score'] = relevance_score
                        scored_markets.append(market_dict)
                
                # Sort by relevance score
                scored_markets.sort(key=lambda x: x['relevance_score'], reverse=True)
                
                # Limit results
                top_markets = scored_markets[:limit]
                
                # Build response
                results = []
                for market in top_markets:
                    result = {
                        "market_id": market['market_id'],
                        "title": market['title'],
                        "category": market['category'] or "",
                        "end_date": market['end_date'].isoformat() if market['end_date'] else None,
                        "active": market['active'],
                        "relevance_score": float(market['relevance_score'])
                    }
                    
                    # Add market_slug if available
                    if has_slug and market.get('market_slug'):
                        result["market_slug"] = market['market_slug']
                    
                    results.append(result)
                
                # Convert to Market objects
                markets = [Market(**result) for result in results]
                
                return MarketsResponse(
                    markets=markets,
                    total_count=len(scored_markets),
                    query=q
                )
        
    except Exception as e:
        logger.error(f"Error searching markets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/markets/{market_id}")
async def get_market(market_id: str):
    """Get specific market by ID"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        market_id,
                        title,
                        category,
                        end_date,
                        active,
                        last_refreshed
                    FROM polymarket_markets 
                    WHERE market_id = %s
                """, (market_id,))
                market = cur.fetchone()
                
                if not market:
                    raise HTTPException(status_code=404, detail="Market not found")
                
                return dict(market)

    except Exception as e:
        logger.error(f"Error fetching market {market_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get list of available market categories"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM polymarket_markets 
                    WHERE active = true AND category IS NOT NULL 
                    GROUP BY category 
                    ORDER BY count DESC
                """)
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AIGG Insights API")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 