#!/usr/bin/env python3
"""
Twitter Wrapper API for AIGG Insights
Optimized endpoint for Twitter bot integration with enhanced formatting
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
import time
import logging
from datetime import datetime, timezone
import re

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import dspy
from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
from src.utils.dspy_utilities import lm_vision

app = FastAPI(
    title="AIGG Twitter Wrapper API",
    description="Optimized API for Twitter bot integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/twitter_wrapper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize AIGG flow
aigg_flow = DSPyEnhancedAIGGFlow()

# Request/Response models
class TwitterAnalysisRequest(BaseModel):
    query: str
    user_id: str
    tweet_id: Optional[str] = None
    user_handle: Optional[str] = None
    # Optional image URLs extracted from the tweet
    media_urls: Optional[list[str]] = None

class TwitterAnalysisResponse(BaseModel):
    success: bool
    tweet_text: str
    market_title: str
    analysis: str
    recommendation: str
    confidence: float
    polymarket_url: str
    processing_time: float
    error_message: Optional[str] = None
    # NEW: Optional follow-up tweet for detailed analysis
    follow_up_tweet: Optional[str] = None
    has_follow_up: bool = False

# Rate limiting storage (in production, use Redis)
user_last_request = {}
RATE_LIMIT_SECONDS = 60  # 1 minute between requests per user (reduced for better responsiveness)

def check_rate_limit(user_id: str) -> bool:
    """Check if user is within rate limits"""
    # Allow admin users to bypass rate limiting
    if user_id == "195487174":  # clydedevv admin user ID
        return True
    
    now = time.time()
    last_request = user_last_request.get(user_id, 0)
    return (now - last_request) >= RATE_LIMIT_SECONDS

def record_request(user_id: str):
    """Record user request timestamp"""
    user_last_request[user_id] = time.time()

def clean_ai_response(text: str) -> str:
    """Clean AI response text by removing thinking tags and malformed content"""
    # Remove <think> tags and content
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Remove standalone <think> without closing
    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)
    
    # Clean up extra whitespace and newlines
    text = ' '.join(text.split())
    
    # Remove "ANALYSIS:" and "RECOMMENDATION:" prefixes
    text = re.sub(r'^(ANALYSIS:|RECOMMENDATION:)\s*', '', text, flags=re.IGNORECASE)
    
    return text.strip()

class VinniePersonality(dspy.Signature):
    """Transform analysis into Vinnie 'The Vig' Lombardi's voice
    
    Examples based on confidence levels:
    - 90%+ BUY_YES: "Trust me on this one - sharp money's moving heavy. My cousin's cousin knows a guy. This is a screaming bargain, capisce?"
    - 80%+ BUY_NO: "Word from the street - this is a sucker bet. The wise ones are talking. Stay away from this action, kid"
    - 70%+ HOLD: "Something's cooking here but keep your powder dry. The vig's telling a story. Numbers don't lie but timing's everything"
    - 60%+ mixed: "Whispers from the neighborhood say tread careful. Decent value play but watch the juice"
    - <60%: "Fuggedaboutit for now - too murky for my taste. Even my nonna's confused. The tea leaves are mixed on this one"
    
    Key phrases to use: 'the vig', 'smart money', 'the line', 'juice', 'action', 'sharp', 'square', 'the wise ones', 'capisce', 'fuggedaboutit'
    Brooklyn expressions: 'my cousin's cousin', 'word from the street', 'from the social club', 'my nonna', 'take it to the bank'
    """
    analysis: str = dspy.InputField(description="Market analysis")
    recommendation: str = dspy.InputField(description="BUY_YES, BUY_NO, or HOLD")
    confidence: float = dspy.InputField(description="Confidence 0.0-1.0")
    
    vinnie_take: str = dspy.OutputField(description="Vinnie's street-smart Brooklyn bookmaker take using betting slang (max 200 chars)")
    
class PersonalityLayer:
    """Clean personality system using DSPy"""
    def __init__(self):
        self.vinnie = dspy.Predict(VinniePersonality)
    
    def apply_vinnie(self, analysis: str, recommendation: str, confidence: float) -> str:
        """Apply Vinnie personality to analysis"""
        try:
            result = self.vinnie(
                analysis=analysis,
                recommendation=recommendation,
                confidence=confidence
            )
            return result.vinnie_take[:200]
        except:
            # Fallback to simple format
            conf_pct = int(confidence * 100)
            return f"{analysis[:150]} ({conf_pct}% confidence)"

# Initialize personality layer
personality = PersonalityLayer()

def format_for_twitter(analysis_result) -> str:
    """Format analysis for Twitter - Vinnie personality already applied in DSPy flow"""
    # Extract components - short_analysis already has Vinnie personality from DSPy
    vinnie_take = clean_ai_response(analysis_result.short_analysis)
    url = analysis_result.polymarket_url
    recommendation = str(analysis_result.recommendation.value if hasattr(analysis_result.recommendation, 'value') else analysis_result.recommendation)
    confidence = analysis_result.confidence
    
    # Only use fallback personality if short_analysis is missing/empty
    if not vinnie_take or len(vinnie_take) < 20:
        # Fallback: use regular analysis with personality layer
        analysis = clean_ai_response(analysis_result.analysis)
        vinnie_take = personality.apply_vinnie(analysis, recommendation, confidence)
    
    # Twitter Premium: we have up to 4000 chars for premium accounts
    # But keep it readable - aim for 280-500 for main tweet
    
    # Add confidence and recommendation info if not already in the take
    conf_pct = int(confidence * 100)
    if str(conf_pct) not in vinnie_take and "confidence" not in vinnie_take.lower():
        vinnie_take = f"{vinnie_take} ({conf_pct}% confidence)"
    
    # Build tweet with proper spacing (no emojis)
    # For multi-choice markets, include more specific recommendation
    rec_line = recommendation.replace('_', ' ')
    
    # Check if the market title suggests multi-choice and add specifics
    market_title = analysis_result.selected_market.title if hasattr(analysis_result, 'selected_market') else ""
    
    # For Fed markets, be specific about the rate change
    if "bps" in market_title.lower() or "basis points" in market_title.lower():
        if "25 bps" in market_title:
            rec_line = "BUY '25 bps decrease' at market price" if "YES" in recommendation else "SELL '25 bps decrease'"
        elif "50 bps" in market_title:
            rec_line = "BUY '50 bps decrease' at market price" if "YES" in recommendation else "SELL '50 bps decrease'"
        elif "no change" in market_title.lower():
            rec_line = "BUY 'No change' at market price" if "YES" in recommendation else "SELL 'No change'"
    # For Trump pardon markets
    elif "pardon" in market_title.lower() and "trump" in market_title.lower():
        # Extract the person's name if available
        if "hunter biden" in market_title.lower():
            rec_line = "BUY 'Hunter Biden' at market price" if "YES" in recommendation else "SELL 'Hunter Biden'"
        else:
            rec_line = "BUY top candidate at market price" if "YES" in recommendation else rec_line
    # For Bitcoin price targets
    elif "bitcoin" in market_title.lower() and any(x in market_title.lower() for x in ["125k", "150k", "200k"]):
        if "125k" in market_title.lower():
            rec_line = "BUY '$125K' at market price" if "YES" in recommendation else "SELL '$125K'"
        elif "150k" in market_title.lower():
            rec_line = "BUY '$150K' at market price" if "YES" in recommendation else "SELL '$150K'"
        elif "200k" in market_title.lower():
            rec_line = "BUY '$200K' at market price" if "YES" in recommendation else "SELL '$200K'"
    
    # Don't include URL in main tweet since we'll post it as follow-up for rich preview
    tweet_parts = [
        vinnie_take,
        "",  # Empty line for readability
        rec_line
    ]
    
    tweet_text = "\n".join(tweet_parts)
    
    # For Twitter Premium we have much more room, no need for aggressive truncation
    # Maximum reasonable tweet is ~500 chars for readability
    if len(tweet_text) > 500:
        # Only trim if really excessive
        lines = vinnie_take.split('. ')
        if len(lines) > 2:
            # Keep first 2-3 sentences
            vinnie_take = '. '.join(lines[:3]) + '.'
            tweet_parts[0] = vinnie_take
            tweet_text = "\n".join(tweet_parts)
    
    return tweet_text

def generate_follow_up_tweet(analysis_result) -> Optional[str]:
    """Generate a follow-up tweet with just the URL for rich preview"""
    try:
        # Always post the URL as a follow-up for better rich preview
        # Twitter treats standalone URLs better for preview generation
        polymarket_url = analysis_result.polymarket_url
        
        if polymarket_url and "polymarket.com" in polymarket_url:
            # Just the URL, nothing else - maximizes chance of rich preview
            return polymarket_url
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating follow-up: {e}")
        return None

@app.post("/analyze", response_model=TwitterAnalysisResponse)
async def analyze_for_twitter(request: TwitterAnalysisRequest):
    """Analyze prediction market query optimized for Twitter response"""
    start_time = time.time()
    
    try:
        # Check rate limiting
        if not check_rate_limit(request.user_id):
            time_left = RATE_LIMIT_SECONDS - (time.time() - user_last_request.get(request.user_id, 0))
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limited. Try again in {int(time_left/60)} minutes."
            )
        
        # Record request
        record_request(request.user_id)
        
        # Log request
        logger.info(f"Twitter analysis request from {request.user_handle or request.user_id}: {request.query}")
        
        # Enrich query with image context if available
        from .twitter_wrapper_vision import enrich_query_with_images
        enriched_query = enrich_query_with_images(
            request.query,
            request.media_urls,
            lm_vision
        )
        
        # Run AIGG analysis
        result = aigg_flow.analyze_query(enriched_query)
        
        if not result:
            # Vinnie-style "no markets" response
            vinnie_no_market = "Fuggedaboutit, kid - can't find any good action on that query. Try something with real juice, capisce?"
            return TwitterAnalysisResponse(
                success=True,  # Still a success, just no markets
                tweet_text=vinnie_no_market,
                market_title="No relevant market",
                analysis="Query didn't match any prediction markets with sufficient confidence",
                recommendation="N/A",
                confidence=0.0,
                polymarket_url="https://polymarket.com",
                processing_time=time.time() - start_time,
                error_message=None
            )
        
        # Quality check: Verify the selected market is actually relevant to the query
        def check_relevance(query: str, market_title: str) -> float:
            """Check how relevant the market is to the query"""
            query_lower = query.lower()
            market_lower = market_title.lower()
            
            # Special cases for known queries
            if "alcaraz" in query_lower:
                # Must be about tennis/sports - Alcaraz is a tennis player
                if "gaza" in market_lower or "israel" in market_lower or "palestine" in market_lower:
                    return 0.0  # Definitely wrong
                if "alcaraz" not in market_lower and "tennis" not in market_lower and "us open" not in market_lower.replace("u.s.", "us"):
                    return 0.0
                return 1.0 if "alcaraz" in market_lower else 0.5
            
            # Check for US Open specifically (not U.S. politics)
            if "us open" in query_lower.replace("u.s.", "us") or "open" in query_lower:
                if "tennis" in query_lower or "alcaraz" in query_lower or "sinner" in query_lower:
                    # Looking for tennis
                    if "gaza" in market_lower or "israel" in market_lower or "recession" in market_lower:
                        return 0.0  # Wrong topic
                    return 0.8 if "open" in market_lower else 0.2
            
            if "trump" in query_lower and "pardon" in query_lower:
                # Must be about pardons
                if "pardon" not in market_lower and "trump" not in market_lower:
                    return 0.0
                return 1.0 if "pardon" in market_lower else 0.5
            
            if "bitcoin" in query_lower or "btc" in query_lower:
                # Must be about crypto
                if "bitcoin" not in market_lower and "btc" not in market_lower and "crypto" not in market_lower:
                    return 0.0
                return 1.0
            
            # Extract key terms from query
            important_terms = []
            for word in query_lower.split():
                if len(word) > 3 and word not in ['will', 'what', 'when', 'where', 'odds', 'chance', 'probability', 'word', 'whats']:
                    important_terms.append(word.strip('?.,!'))
            
            # Check how many important terms appear in market title
            matches = sum(1 for term in important_terms if term in market_lower)
            
            if len(important_terms) == 0:
                return 0.5  # Can't determine relevance
            
            relevance = matches / len(important_terms)
            
            # Special case: if query mentions specific entities (like Perplexity, Chrome) 
            # they MUST be in the market title
            critical_entities = ['perplexity', 'chrome', 'google', 'bitcoin', 'trump', 'tesla']
            for entity in critical_entities:
                if entity in query_lower and entity not in market_lower:
                    relevance = 0.0  # Critical mismatch
                    break
            
            return relevance
        
        # Check relevance
        relevance_score = check_relevance(request.query, result.selected_market.title)
        logger.info(f"Market relevance score: {relevance_score:.2f} for '{result.selected_market.title}' vs query '{request.query[:50]}'")
        
        if relevance_score < 0.2:
            # Market is not relevant enough
            logger.warning(f"Rejecting irrelevant market: '{result.selected_market.title}' for query '{request.query}'")
            vinnie_no_market = "Listen kid, I can't find any good action on that specific query. The markets ain't matching what you're asking. Try being more specific, capisce?"
            return TwitterAnalysisResponse(
                success=True,
                tweet_text=vinnie_no_market,
                market_title="No relevant market",
                analysis="Selected market didn't match query criteria",
                recommendation="N/A",
                confidence=0.0,
                polymarket_url="https://polymarket.com",
                processing_time=time.time() - start_time,
                error_message=None
            )
        
        # Format for Twitter
        tweet_text = format_for_twitter(result)
        
        # Generate follow-up tweet for additional details
        follow_up_tweet = generate_follow_up_tweet(result)
        
        processing_time = time.time() - start_time
        
        # Log successful response
        logger.info(f"Successful analysis for {request.user_handle or request.user_id} in {processing_time:.2f}s")
        
        return TwitterAnalysisResponse(
            success=True,
            tweet_text=tweet_text,
            market_title=result.selected_market.title,
            analysis=result.analysis,
            recommendation=result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation),
            confidence=result.confidence,
            polymarket_url=result.polymarket_url,
            processing_time=processing_time,
            follow_up_tweet=follow_up_tweet,
            has_follow_up=follow_up_tweet is not None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Twitter analysis: {str(e)}")
        return TwitterAnalysisResponse(
            success=False,
            tweet_text="Analysis error. Please try again.",
            market_title="",
            analysis="",
            recommendation="",
            confidence=0.0,
            polymarket_url="",
            processing_time=time.time() - start_time,
            error_message=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check for Twitter wrapper API"""
    return {
        "status": "healthy",
        "timestamp": str(datetime.now(timezone.utc)),
        "service": "aigg-twitter-wrapper",
        "version": "1.0.0"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    test_result = aigg_flow.analyze_query("Will Bitcoin reach $150k this year?")
    
    if test_result:
        tweet_text = format_for_twitter(test_result)
        return {
            "test_status": "success",
            "sample_tweet": tweet_text,
            "tweet_length": len(tweet_text)
        }
    else:
        return {
            "test_status": "failed",
            "error": "Could not generate test analysis"
        }

@app.post("/clear-rate-limits")
async def clear_rate_limits():
    """Clear all rate limiting data (admin only)"""
    global user_last_request
    user_last_request.clear()
    return {
        "status": "success",
        "message": "All rate limits cleared",
        "timestamp": str(datetime.now(timezone.utc))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info") 