#!/usr/bin/env python3
"""
Enhanced AIGG Flow - With optional database persistence
Main flow: input query -> find relevant market -> research -> analysis -> recommendation -> store results
"""
import os
import json
import requests
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

@dataclass
class Market:
    """Simple market data structure"""
    id: str
    question: str
    description: str = ""
    volume_24h: float = 0.0
    active: bool = True
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

class PolymarketAPI:
    """Simple Polymarket API client with optional database integration"""
    
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self, use_database: bool = False):
        self.use_database = use_database
        if use_database:
            try:
                from db.connection import get_db_cursor_context
                self.get_db_cursor_context = get_db_cursor_context
            except ImportError:
                print("⚠️ Database modules not available, running without persistence")
                self.use_database = False
    
    def fetch_markets(self, limit: int = 50) -> List[Market]:
        """Fetch active markets from Polymarket with optional database cache"""
        
        # Try database first if available
        if self.use_database:
            try:
                with self.get_db_cursor_context() as cur:
                    cur.execute("""
                        SELECT market_id, question, description, volume_24h, active, outcomes, outcome_prices
                        FROM polymarket_odds 
                        WHERE active = true 
                        ORDER BY volume_24h DESC 
                        LIMIT %s
                    """, (limit,))
                    
                    db_markets = cur.fetchall()
                    if db_markets:
                        print(f"📊 Using {len(db_markets)} markets from database cache")
                        markets = []
                        for row in db_markets:
                            market = Market(
                                id=row['market_id'],
                                question=row['question'],
                                description=row['description'] or "",
                                volume_24h=float(row['volume_24h'] or 0),
                                active=row['active'],
                                outcomes=row['outcomes'] if isinstance(row['outcomes'], list) else [],
                                prices=row['outcome_prices'] if isinstance(row['outcome_prices'], dict) else {}
                            )
                            markets.append(market)
                        return markets
            except Exception as e:
                print(f"⚠️ Database query failed, fetching from API: {e}")
        
        # Fetch from API (fallback or primary method)
        try:
            url = f"{self.BASE_URL}/markets"
            params = {
                "limit": limit,
                "active": "true",
                "closed": "false"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            response_data = response.json()
            
            # Handle new API structure where markets are in 'data' field
            if isinstance(response_data, dict) and 'data' in response_data:
                markets_data = response_data['data']
            else:
                markets_data = response_data
            
            markets = []
            
            for market_data in markets_data:
                if isinstance(market_data, dict):
                    # Handle the actual API field names
                    market = Market(
                        id=market_data.get('condition_id', market_data.get('id', '')),
                        question=market_data.get('question', market_data.get('description', 'Unknown market')),
                        description=market_data.get('description', ''),
                        volume_24h=float(market_data.get('volume', market_data.get('volume_24h', 0))),
                        active=market_data.get('active', True),
                        outcomes=market_data.get('outcomes', []),
                        prices=market_data.get('outcome_prices', {})
                    )
                    markets.append(market)
            
            print(f"📊 Fetched {len(markets)} markets from Polymarket API")
            return markets
            
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def find_relevant_market(self, query: str, markets: List[Market]) -> Optional[Market]:
        """Find the most relevant market for a given query using simple text matching"""
        if not markets:
            return None
        
        query_lower = query.lower()
        scored_markets = []
        
        for market in markets:
            score = 0
            market_text = f"{market.question} {market.description}".lower()
            
            # Simple keyword matching
            for word in query_lower.split():
                if len(word) > 2:  # Skip very short words
                    if word in market_text:
                        score += 1
            
            # Bonus for high volume (market activity indicator)
            if market.volume_24h > 1000:
                score += 0.5
            
            if score > 0:
                scored_markets.append((market, score))
        
        if scored_markets:
            # Return highest scoring market
            scored_markets.sort(key=lambda x: x[1], reverse=True)
            return scored_markets[0][0]
        
        return None

class PerplexityResearcher:
    """Research using Perplexity API for web search and reasoning"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
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
    
    def search_web_for_topic(self, topic: str) -> str:
        """Use Perplexity's Sonar model for web search on the topic"""
        messages = [
            {
                "role": "system",
                "content": "You are a research assistant. Search the web and provide comprehensive, factual information with recent developments and multiple perspectives on the given topic. Include sources and dates when possible."
            },
            {
                "role": "user", 
                "content": f"Research current information about: {topic}. Focus on recent developments, key factors, and different viewpoints that would be relevant for prediction markets."
            }
        ]
        
        return self._make_perplexity_request(messages, model="sonar")
    
    def analyze_with_reasoning(self, topic: str, web_research: str) -> str:
        """Use Perplexity's reasoning model to analyze the research"""
        messages = [
            {
                "role": "system",
                "content": """You are an expert analyst for prediction markets. Given web research about a topic, provide a structured analysis including:
                1. Current situation summary
                2. Key factors influencing the outcome
                3. Supporting evidence
                4. Opposing evidence or risks
                5. Your confidence level (0.0 to 1.0) in predicting the outcome
                
                Be objective, consider multiple perspectives, and base your confidence on the quality and consistency of available evidence."""
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nWeb Research:\n{web_research}\n\nProvide your structured analysis:"
            }
        ]
        
        return self._make_perplexity_request(messages, model="r1-1776")
    
    def research_topic(self, topic: str) -> ResearchResult:
        """Conduct comprehensive research using both Perplexity models"""
        if not self.perplexity_key:
            return ResearchResult(
                topic=topic,
                summary="No Perplexity API key available for research",
                key_points=["API key missing"],
                confidence=0.0
            )
        
        try:
            print("  🌐 Searching web with Perplexity Sonar...")
            web_research = self.search_web_for_topic(topic)
            
            print("  🧠 Analyzing with Perplexity reasoning model...")
            analysis = self.analyze_with_reasoning(topic, web_research)
            
            # Parse the analysis to extract components
            lines = analysis.split('\n')
            summary_lines = []
            key_points = []
            confidence = 0.7  # Default
            
            current_section = ""
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for confidence mentions
                if "confidence" in line.lower():
                    confidence_match = re.search(r'(\d*\.?\d+)', line)
                    if confidence_match:
                        try:
                            confidence = float(confidence_match.group(1))
                            if confidence > 1.0:  # If given as percentage
                                confidence = confidence / 100.0
                        except:
                            pass
                
                # Collect key points (lines starting with numbers, bullets, etc.)
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                    key_points.append(line)
                elif len(summary_lines) < 3:  # First few lines for summary
                    summary_lines.append(line)
            
            summary = ' '.join(summary_lines)[:300]
            
            return ResearchResult(
                topic=topic,
                summary=summary,
                key_points=key_points[:5],
                confidence=confidence,
                sources=["Perplexity Sonar web search", "Perplexity R1-1776 analysis"],
                web_research=web_research
            )
            
        except Exception as e:
            print(f"Research error: {e}")
            return ResearchResult(
                topic=topic,
                summary=f"Research failed: {str(e)}",
                key_points=["Research unavailable"],
                confidence=0.0
            )

class MarketAnalyzer:
    """Analyze research and market data to make recommendations"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def _make_perplexity_request(self, messages: List[Dict], model: str = "r1-1776") -> str:
        """Make a request to Perplexity API for analysis"""
        if not self.perplexity_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def analyze_market(self, market: Market, research: ResearchResult) -> Recommendation:
        """Analyze market and research to generate recommendation using Perplexity reasoning"""
        
        # First, try AI-powered analysis if we have Perplexity
        if self.perplexity_key:
            try:
                print("  🤖 Using Perplexity reasoning for recommendation...")
                
                messages = [
                    {
                        "role": "system",
                        "content": """You are an expert prediction market analyst. Given a market question and research data, provide a betting recommendation.

                        Consider:
                        - Research confidence and evidence quality
                        - Market volume and activity
                        - Risk vs. reward potential
                        - Information edge vs. market consensus

                        Respond with:
                        1. Recommendation: "yes", "no", or "pass"
                        2. Bet size: "small", "medium", "large", or "none"
                        3. Confidence: decimal between 0.0-1.0
                        4. Reasoning: brief explanation

                        Format: RECOMMENDATION|BET_SIZE|CONFIDENCE|REASONING"""
                    },
                    {
                        "role": "user",
                        "content": f"""Market Question: {market.question}
                        
Research Summary: {research.summary}
Key Points: {', '.join(research.key_points[:3])}
Research Confidence: {research.confidence}
Market Volume: ${market.volume_24h:,.0f}

Please provide your betting recommendation:"""
                    }
                ]
                
                ai_response = self._make_perplexity_request(messages)
                
                if ai_response:
                    # Parse AI response
                    parts = ai_response.split('|')
                    if len(parts) >= 4:
                        recommendation = parts[0].strip().lower()
                        bet_size = parts[1].strip().lower()
                        try:
                            confidence = float(parts[2].strip())
                        except:
                            confidence = research.confidence
                        reasoning = parts[3].strip()
                        
                        return Recommendation(
                            market=market,
                            research=research,
                            recommendation=recommendation,
                            confidence=confidence,
                            reasoning=reasoning,
                            bet_size=bet_size
                        )
                        
            except Exception as e:
                print(f"  ⚠️ AI analysis failed, falling back to simple logic: {e}")
        
        # Fallback to simple logic
        confidence = research.confidence
        
        if confidence < 0.3:
            return Recommendation(
                market=market,
                research=research,
                recommendation="pass",
                confidence=confidence,
                reasoning="Insufficient confidence in research to make a bet",
                bet_size="none"
            )
        
        # Simple recommendation logic based on research confidence
        if confidence > 0.8:
            recommendation = "yes"
            bet_size = "medium"
            reasoning = "High confidence research supports positive outcome"
        elif confidence > 0.6:
            recommendation = "yes"  
            bet_size = "small"
            reasoning = "Moderate confidence supports cautious positive position"
        else:
            recommendation = "pass"
            bet_size = "none"
            reasoning = "Research inconclusive for betting decision"
        
        return Recommendation(
            market=market,
            research=research,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            bet_size=bet_size
        )

class EnhancedAIGGFlow:
    """Enhanced flow orchestrator with optional database persistence"""
    
    def __init__(self, use_database: bool = False):
        self.use_database = use_database
        self.polymarket = PolymarketAPI(use_database=use_database)
        self.researcher = PerplexityResearcher()
        self.analyzer = MarketAnalyzer()
        
        # Initialize database services if requested
        if use_database:
            try:
                from services.market_research_service import MarketResearchService
                self.market_research_service = MarketResearchService()
                print("🗄️ Database persistence enabled")
            except ImportError:
                print("⚠️ Database services not available, running without persistence")
                self.use_database = False
    
    def run_analysis(self, query: str) -> Optional[Recommendation]:
        """Run the complete analysis flow with optional database storage"""
        print(f"🔍 Analyzing query: '{query}'")
        
        # Step 1: Fetch markets
        print("📊 Fetching Polymarket data...")
        markets = self.polymarket.fetch_markets(limit=50)
        if not markets:
            print("❌ No markets found")
            return None
        print(f"✅ Found {len(markets)} markets")
        
        # Step 2: Find relevant market
        print("🎯 Finding relevant market...")
        relevant_market = self.polymarket.find_relevant_market(query, markets)
        if not relevant_market:
            print("❌ No relevant market found")
            return None
        print(f"✅ Found relevant market: {relevant_market.question}")
        
        # Step 3: Research the topic
        print("🔬 Conducting research...")
        research = self.researcher.research_topic(relevant_market.question)
        print(f"✅ Research completed (confidence: {research.confidence:.2f})")
        
        # Step 4: Generate recommendation
        print("💡 Generating recommendation...")
        recommendation = self.analyzer.analyze_market(relevant_market, research)
        print(f"✅ Analysis complete: {recommendation.recommendation} ({recommendation.confidence:.2f})")
        
        # Step 5: Store in database if enabled
        if self.use_database and hasattr(self, 'market_research_service'):
            try:
                print("💾 Storing results in database...")
                # Use synchronous version since we're not in an async context
                result_ids = self._store_research_sync(
                    market=relevant_market,
                    research=research,
                    recommendation=recommendation
                )
                print(f"✅ Stored with research_id: {result_ids['research_id']}")
            except Exception as e:
                print(f"⚠️ Database storage failed: {e}")
        
        return recommendation
    
    def _store_research_sync(self, market: Market, research: ResearchResult, recommendation: Recommendation) -> Dict[str, Any]:
        """Store research results synchronously in the database"""
        from services.research_service import ResearchService
        
        research_service = ResearchService()
        
        # Store research
        research_id = research_service.store_research(
            market_id=market.id,
            title=f"Analysis: {market.question}",
            raw_text=research.web_research
        )
        
        # Store analysis
        analysis_id = research_service.store_analysis(
            research_id=research_id,
            analyst="AIGG-Enhanced",
            analysis_type="AI Analysis",
            insights={
                "confidence": research.confidence,
                "key_points": research.key_points,
                "sources": research.sources,
                "recommendation": recommendation.recommendation,
                "bet_size": recommendation.bet_size,
                "reasoning": recommendation.reasoning
            }
        )
        
        # Store conclusion
        conclusion_id = research_service.store_conclusion(
            analysis_id=analysis_id,
            conclusion_text=recommendation.reasoning,
            confidence_score=recommendation.confidence,
            supporting_evidence={
                "key_points": research.key_points,
                "sources": research.sources
            },
            created_by="AIGG-Enhanced"
        )
        
        return {
            "research_id": research_id,
            "analysis_id": analysis_id,
            "conclusion_id": conclusion_id
        }
    
    def print_recommendation(self, rec: Recommendation):
        """Print a formatted recommendation"""
        print("\n" + "="*60)
        print("🎯 ENHANCED AIGG MARKET ANALYSIS RESULT")
        print("="*60)
        print(f"🏆 Market: {rec.market.question}")
        print(f"💰 Volume: ${rec.market.volume_24h:,.0f}")
        print(f"🔍 Research Sources: {', '.join(rec.research.sources)}")
        print(f"🔬 Research Summary: {rec.research.summary[:150]}...")
        print(f"📊 Key Points:")
        for point in rec.research.key_points[:3]:
            print(f"   • {point}")
        print(f"📊 Recommendation: {rec.recommendation.upper()}")
        print(f"🎲 Bet Size: {rec.bet_size}")
        print(f"🧠 Confidence: {rec.confidence:.1%}")
        print(f"💭 Reasoning: {rec.reasoning}")
        if self.use_database:
            print(f"💾 Results stored in database")
        print("="*60)

def main():
    """Test the enhanced flow"""
    # Initialize with database if available
    use_db = os.getenv("DATABASE_URL") is not None
    flow = EnhancedAIGGFlow(use_database=use_db)
    
    # Test query
    test_query = "Bitcoin will hit $150k in 2024"
    
    result = flow.run_analysis(test_query)
    if result:
        flow.print_recommendation(result)
    else:
        print("❌ No analysis result generated")

if __name__ == "__main__":
    main() 