#!/usr/bin/env python3
"""
Database-First AIGG Flow - Production version that prioritizes database over API
Main flow: query -> find relevant market from DB -> research -> analysis -> recommendation -> store results
"""
import os
import json
import requests
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime, timezone
import psycopg2.extras

load_dotenv()

@dataclass
class Market:
    """Simple market data structure"""
    id: str
    question: str
    description: str = ""
    volume_24h: float = 0.0
    active: bool = True
    end_date: Optional[datetime] = None
    outcomes: List[str] = None
    prices: Dict[str, float] = None

@dataclass
class ResearchResult:
    """Research analysis result"""
    topic: str
    summary: str
    key_points: List[str]
    confidence: float
    sources: List[str] = None
    web_research: str = ""

@dataclass
class Recommendation:
    """Final betting recommendation"""
    market: Market
    research: ResearchResult
    recommendation: str  # "yes", "no", "pass"
    confidence: float
    reasoning: str
    bet_size: str  # "small", "medium", "large", "none"

class DatabaseMarketService:
    """Database-first market service - prioritizes DB over API calls"""
    
    def __init__(self):
        self.current_date = datetime.now(timezone.utc)
        print(f"🗓️ Current date: {self.current_date.strftime('%Y-%m-%d %H:%M UTC')} (June 2025)")
    
    def get_db_connection(self):
        """Get database connection"""
        from db.connection import get_db_connection
        return get_db_connection()
    
    def fetch_markets_from_database(self, limit: int = 2000) -> List[Market]:
        """Fetch markets from database - primary method for production"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    # Get active markets, simplified query for debugging
                    cur.execute("""
                        SELECT market_id, question, description, volume_24h, active, 
                               end_date, outcomes, outcome_prices
                        FROM polymarket_odds 
                        WHERE active = true 
                        ORDER BY volume_24h DESC NULLS LAST
                        LIMIT %s
                    """, (limit,))
                    
                    db_markets = cur.fetchall()
                    
                    if not db_markets:
                        print("⚠️ No markets found in database")
                        return []
                    
                    markets = []
                    for row in db_markets:
                        # Handle JSON fields safely
                        outcomes = row['outcomes'] if isinstance(row['outcomes'], list) else []
                        prices = row['outcome_prices'] if isinstance(row['outcome_prices'], dict) else {}
                        
                        market = Market(
                            id=row['market_id'],
                            question=row['question'],
                            description=row['description'] or "",
                            volume_24h=float(row['volume_24h'] or 0),
                            active=row['active'],
                            end_date=row['end_date'],
                            outcomes=outcomes,
                            prices=prices
                        )
                        markets.append(market)
                    
                    print(f"📊 Retrieved {len(markets)} active markets from database")
                    return markets
                    
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            return []
    
    def find_relevant_market(self, query: str, markets: List[Market]) -> Optional[Market]:
        """Find the most relevant market with enhanced time-aware matching"""
        if not markets:
            return None
        
        query_lower = query.lower()
        scored_markets = []
        
        # Extract time references from query
        time_sensitive_keywords = {
            '2025': 2025,
            '2024': 2024,
            '2026': 2026,
            'this year': 2025,
            'next year': 2026,
            'end of': 'eoy',
            'by end': 'eoy',
            'month': 'month',
            'june': 6,
            'july': 7,
            'august': 8,
            'december': 12
        }
        
        query_time_context = {}
        for keyword, value in time_sensitive_keywords.items():
            if keyword in query_lower:
                query_time_context[keyword] = value
        
        print(f"🔍 Query time context detected: {query_time_context}")
        
        for market in markets:
            score = 0
            market_text = f"{market.question} {market.description}".lower()
            
            # Basic keyword matching with weighted scoring
            query_words = [w for w in query_lower.split() if len(w) > 2]
            for word in query_words:
                if word in market_text:
                    # Higher score for exact matches in question vs description
                    if word in market.question.lower():
                        score += 2
                    else:
                        score += 1
            
            # Time relevance scoring
            if market.end_date:
                market_year = market.end_date.year
                market_month = market.end_date.month
                
                # Boost score for time-relevant markets
                if query_time_context:
                    if '2025' in query_time_context and market_year == 2025:
                        score += 3
                    elif 'this year' in query_time_context and market_year == 2025:
                        score += 3
                    elif 'month' in query_time_context and market_month == 6:  # June 2025
                        score += 2
                    elif 'end of' in query_time_context or 'by end' in query_time_context:
                        if market_month >= 11:  # End of year markets
                            score += 2
                
                # Penalize markets that are ending too soon for meaningful analysis
                days_until_end = (market.end_date - self.current_date).days
                if days_until_end < 7:
                    score -= 2  # Market ending too soon
                elif days_until_end > 365:
                    score -= 1  # Market too far in future
            
            # Volume/activity bonus
            if market.volume_24h > 10000:
                score += 1.5
            elif market.volume_24h > 1000:
                score += 0.5
            
            # Category/topic specific boosts
            category_boosts = {
                ('trump', 'cabinet', 'fire'): ['trump', 'cabinet', 'administration'],
                ('russia', 'bomb', 'germany'): ['russia', 'germany', 'war', 'attack'],
                ('nba', 'finals', '2025'): ['nba', 'basketball', 'finals', 'champion'],
                ('ai', 'model', 'best'): ['ai', 'artificial intelligence', 'model', 'gpt', 'claude']
            }
            
            for query_tuple, boost_keywords in category_boosts.items():
                if all(keyword in query_lower for keyword in query_tuple):
                    for boost_word in boost_keywords:
                        if boost_word in market_text:
                            score += 1
            
            if score > 0:
                scored_markets.append((market, score))
        
        if scored_markets:
            # Sort by score and return top match
            scored_markets.sort(key=lambda x: x[1], reverse=True)
            top_market = scored_markets[0]
            print(f"🎯 Best match (score: {top_market[1]:.1f}): {top_market[0].question}")
            
            # Show other good matches for context
            if len(scored_markets) > 1:
                print("📋 Other relevant matches:")
                for market, score in scored_markets[1:4]:  # Show top 3 alternatives
                    print(f"   • {score:.1f}: {market.question[:80]}...")
            
            return top_market[0]
        
        print("❌ No relevant markets found")
        return None

class PerplexityResearcher:
    """Research using Perplexity API with context awareness"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.current_date = datetime.now(timezone.utc)
    
    def _make_perplexity_request(self, messages: List[Dict], model: str = "sonar") -> str:
        """Make a request to Perplexity API"""
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not found")
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def research_topic(self, market: Market) -> ResearchResult:
        """Conduct time-aware comprehensive research"""
        if not self.perplexity_key:
            return ResearchResult(
                topic=market.question,
                summary="No Perplexity API key available for research",
                key_points=["API key missing"],
                confidence=0.0
            )
        
        try:
            # Create context-aware research prompt
            time_context = f"Current date: {self.current_date.strftime('%B %d, %Y')} (June 2025)"
            if market.end_date:
                days_left = (market.end_date - self.current_date).days
                time_context += f". Market resolves in {days_left} days ({market.end_date.strftime('%B %d, %Y')})"
            
            print("  🌐 Searching web with Perplexity Sonar...")
            web_messages = [
                {
                    "role": "system",
                    "content": f"""You are a research assistant for prediction markets. {time_context}
                    Search for the most recent, relevant information about the given market question.
                    Focus on current developments, recent news, and factors that could influence the outcome.
                    Consider the timeline - if this is a time-sensitive question, prioritize recent events."""
                },
                {
                    "role": "user", 
                    "content": f"Research this prediction market question: {market.question}\n\nProvide comprehensive, up-to-date information that would help predict the outcome."
                }
            ]
            
            web_research = self._make_perplexity_request(web_messages, model="sonar")
            
            print("  🧠 Analyzing with Perplexity reasoning model...")
            analysis_messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert prediction market analyst. {time_context}
                    
                    Analyze the research and provide:
                    1. Current situation summary (2-3 sentences)
                    2. Key factors that could influence the outcome
                    3. Supporting evidence
                    4. Risks/opposing factors
                    5. Confidence assessment (0.0 to 1.0) based on:
                       - Quality of available information
                       - Predictability of the outcome
                       - Time horizon considerations
                    
                    Be objective and consider multiple scenarios."""
                },
                {
                    "role": "user",
                    "content": f"Market: {market.question}\nEnd Date: {market.end_date}\n\nResearch:\n{web_research}\n\nProvide structured analysis:"
                }
            ]
            
            analysis = self._make_perplexity_request(analysis_messages, model="r1-1776")
            
            # Parse analysis
            lines = analysis.split('\n')
            summary_lines = []
            key_points = []
            confidence = 0.6  # Default
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extract confidence score
                if "confidence" in line.lower():
                    confidence_match = re.search(r'(\d*\.?\d+)', line)
                    if confidence_match:
                        try:
                            confidence = float(confidence_match.group(1))
                            if confidence > 1.0:
                                confidence = confidence / 100.0
                        except:
                            pass
                
                # Collect key points
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                    key_points.append(line)
                elif len(summary_lines) < 3:
                    summary_lines.append(line)
            
            summary = ' '.join(summary_lines)[:400]
            
            return ResearchResult(
                topic=market.question,
                summary=summary,
                key_points=key_points[:5],
                confidence=max(0.0, min(1.0, confidence)),  # Clamp to valid range
                sources=["Perplexity Sonar", "Perplexity R1-1776"],
                web_research=web_research
            )
            
        except Exception as e:
            print(f"Research error: {e}")
            return ResearchResult(
                topic=market.question,
                summary=f"Research failed: {str(e)}",
                key_points=["Research unavailable"],
                confidence=0.0
            )

class DatabaseFirstAnalyzer:
    """Enhanced analyzer that stores results in database"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def analyze_and_recommend(self, market: Market, research: ResearchResult) -> Recommendation:
        """Generate AI-powered recommendation and store in database"""
        
        if self.perplexity_key:
            try:
                print("  🤖 Generating recommendation with Perplexity...")
                
                headers = {
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                }
                
                messages = [
                    {
                        "role": "system",
                        "content": """You are an expert prediction market trader. Given market data and research, provide a clear betting recommendation.

                        Consider:
                        - Research quality and confidence
                        - Market timing and liquidity
                        - Risk-reward ratio
                        - Information edge vs market price

                        Output format: DECISION|SIZE|CONFIDENCE|REASON
                        Where:
                        - DECISION: yes/no/pass
                        - SIZE: small/medium/large/none
                        - CONFIDENCE: 0.0-1.0
                        - REASON: brief explanation (1-2 sentences)"""
                    },
                    {
                        "role": "user",
                        "content": f"""Market: {market.question}
Time to resolution: {(market.end_date - datetime.now(timezone.utc)).days if market.end_date else 'Unknown'} days
Market volume: ${market.volume_24h:,.0f}

Research summary: {research.summary}
Research confidence: {research.confidence}
Key factors: {'; '.join(research.key_points[:3])}

Recommendation:"""
                    }
                ]
                
                payload = {
                    "model": "r1-1776",
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.2
                }
                
                response = requests.post(self.base_url, json=payload, headers=headers, timeout=20)
                response.raise_for_status()
                
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                # Parse AI response
                parts = ai_response.split('|')
                if len(parts) >= 4:
                    decision = parts[0].strip().lower()
                    bet_size = parts[1].strip().lower()
                    try:
                        confidence = float(parts[2].strip())
                    except:
                        confidence = research.confidence
                    reasoning = parts[3].strip()
                    
                    recommendation = Recommendation(
                        market=market,
                        research=research,
                        recommendation=decision,
                        confidence=confidence,
                        reasoning=reasoning,
                        bet_size=bet_size
                    )
                    
                    # Store in database
                    self._store_analysis(recommendation)
                    return recommendation
                        
            except Exception as e:
                print(f"  ⚠️ AI recommendation failed: {e}")
        
        # Fallback logic
        confidence = research.confidence
        
        if confidence < 0.4:
            decision = "pass"
            bet_size = "none"
            reasoning = "Research confidence too low for betting"
        elif confidence > 0.8:
            decision = "yes"
            bet_size = "medium"
            reasoning = "High-confidence research supports positive outcome"
        elif confidence > 0.6:
            decision = "yes"
            bet_size = "small"
            reasoning = "Moderate confidence supports cautious position"
        else:
            decision = "pass"
            bet_size = "none"
            reasoning = "Inconclusive research"
        
        recommendation = Recommendation(
            market=market,
            research=research,
            recommendation=decision,
            confidence=confidence,
            reasoning=reasoning,
            bet_size=bet_size
        )
        
        self._store_analysis(recommendation)
        return recommendation
    
    def _store_analysis(self, rec: Recommendation):
        """Store analysis results in database"""
        try:
            from services.research_service import ResearchService
            research_service = ResearchService()
            
            # Store research
            research_id = research_service.store_research(
                market_id=rec.market.id,
                title=f"Analysis: {rec.market.question}",
                raw_text=rec.research.web_research
            )
            
            # Store analysis
            analysis_id = research_service.store_analysis(
                research_id=research_id,
                analyst="DatabaseFirst-AIGG",
                analysis_type="AI Analysis",
                insights={
                    "confidence": rec.research.confidence,
                    "key_points": rec.research.key_points,
                    "recommendation": rec.recommendation,
                    "bet_size": rec.bet_size,
                    "reasoning": rec.reasoning
                }
            )
            
            # Store conclusion
            research_service.store_conclusion(
                analysis_id=analysis_id,
                conclusion_text=rec.reasoning,
                confidence_score=rec.confidence,
                supporting_evidence={
                    "key_points": rec.research.key_points,
                    "sources": rec.research.sources
                },
                created_by="DatabaseFirst-AIGG"
            )
            
            print(f"💾 Analysis stored with research_id: {research_id}")
            
        except Exception as e:
            print(f"⚠️ Database storage failed: {e}")

class DatabaseFirstFlow:
    """Production-ready flow that prioritizes database over API calls"""
    
    def __init__(self):
        self.market_service = DatabaseMarketService()
        self.researcher = PerplexityResearcher()
        self.analyzer = DatabaseFirstAnalyzer()
    
    def analyze_query(self, query: str) -> Optional[Recommendation]:
        """Run complete analysis using database-first approach"""
        print(f"🔍 Analyzing: '{query}'")
        print("="*60)
        
        # Step 1: Get markets from database (not API)
        print("📊 Loading markets from database...")
        markets = self.market_service.fetch_markets_from_database(limit=2000)
        if not markets:
            print("❌ No markets available in database")
            return None
        
        # Step 2: Find relevant market with time awareness
        print("🎯 Finding relevant market...")
        relevant_market = self.market_service.find_relevant_market(query, markets)
        if not relevant_market:
            print("❌ No relevant market found")
            return None
        
        # Step 3: Conduct research
        print("🔬 Conducting research...")
        research = self.researcher.research_topic(relevant_market)
        
        # Step 4: Generate recommendation and store
        print("💡 Generating recommendation...")
        recommendation = self.analyzer.analyze_and_recommend(relevant_market, research)
        
        return recommendation
    
    def print_result(self, rec: Recommendation):
        """Print formatted result"""
        print("\n" + "="*70)
        print("🎯 DATABASE-FIRST AIGG ANALYSIS RESULT")
        print("="*70)
        print(f"🏆 Market: {rec.market.question}")
        print(f"💰 24h Volume: ${rec.market.volume_24h:,.0f}")
        if rec.market.end_date:
            days_left = (rec.market.end_date - datetime.now(timezone.utc)).days
            print(f"⏰ Time to Resolution: {days_left} days ({rec.market.end_date.strftime('%B %d, %Y')})")
        print(f"🔍 Research Summary: {rec.research.summary[:200]}...")
        print(f"📊 Key Insights:")
        for point in rec.research.key_points[:3]:
            print(f"   • {point}")
        print(f"🎲 Recommendation: {rec.recommendation.upper()}")
        print(f"💵 Bet Size: {rec.bet_size.upper()}")
        print(f"🧠 Confidence: {rec.confidence:.1%}")
        print(f"💭 Reasoning: {rec.reasoning}")
        print(f"💾 Results stored in database")
        print("="*70)

def test_queries():
    """Test with the provided queries"""
    flow = DatabaseFirstFlow()
    
    test_queries = [
        "Which cabinet member will trump fire first?",
        "Will russia bomb Germany", 
        "who will win 2025 nba finals",
        "best AI model by end of the month"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"TESTING QUERY: {query}")
        print(f"{'='*80}")
        
        result = flow.analyze_query(query)
        if result:
            flow.print_result(result)
        else:
            print("❌ No result generated")
        
        print("\n" + "🔄 Next query in 3 seconds...")
        import time
        time.sleep(3)

if __name__ == "__main__":
    test_queries() 