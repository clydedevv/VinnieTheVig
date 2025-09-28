from typing import Dict, List, Optional
from uuid import UUID
from .research_service import ResearchService
from db.connection import get_db_cursor

class MarketResearchService:
    def __init__(self):
        self.research_service = ResearchService()

    async def get_market_with_research(self, market_id: str) -> Dict:
        """Get market data enriched with research and analysis"""
        with get_db_cursor() as cur:
            # Get market data
            cur.execute("""
                SELECT * FROM polymarket_odds 
                WHERE market_id = %s
            """, (market_id,))
            market = cur.fetchone()

            if not market:
                return None

            # Get associated research
            cur.execute("""
                SELECT r.*, a.insights, c.conclusion_text, c.confidence_score
                FROM research r
                LEFT JOIN analysis a ON a.research_id = r.id
                LEFT JOIN conclusions c ON c.analysis_id = a.id
                WHERE r.market_id = %s
                ORDER BY r.last_updated DESC
            """, (market_id,))
            research_data = cur.fetchall()

            # Combine market data with research
            return {
                **market,
                "research": research_data
            }

    async def store_market_research(
        self,
        market_id: str,
        title: str,
        raw_text: str,
        analysis_insights: Dict,
        conclusion_text: str,
        confidence_score: float,
        analyst: str = "AI",
        analysis_type: str = "NLP Summary"
    ) -> Dict[str, UUID]:
        """Store complete market research pipeline"""
        # Store research
        research_id = self.research_service.store_research(
            market_id=market_id,
            title=title,
            raw_text=raw_text
        )

        # Store analysis
        analysis_id = self.research_service.store_analysis(
            research_id=research_id,
            analyst=analyst,
            analysis_type=analysis_type,
            insights=analysis_insights
        )

        # Store conclusion
        conclusion_id = self.research_service.store_conclusion(
            analysis_id=analysis_id,
            conclusion_text=conclusion_text,
            confidence_score=confidence_score,
            supporting_evidence=analysis_insights,
            created_by=analyst
        )

        return {
            "research_id": research_id,
            "analysis_id": analysis_id,
            "conclusion_id": conclusion_id
        } 