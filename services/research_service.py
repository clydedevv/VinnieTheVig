from typing import Dict, List, Optional
from uuid import UUID
import json
from db.connection import get_db_cursor

class ResearchService:
    @staticmethod
    def store_research(
        market_id: str,
        title: str,
        raw_text: str,
        source_url: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> UUID:
        """Store new research data and return its ID"""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO research (market_id, title, raw_text, source_url, keywords)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (market_id, title, raw_text, source_url, json.dumps(keywords or [])))
            return cur.fetchone()["id"]

    @staticmethod
    def store_analysis(
        research_id: UUID,
        analyst: str,
        analysis_type: str,
        insights: Dict
    ) -> UUID:
        """Store analysis of research"""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO analysis (research_id, analyst, analysis_type, insights)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (research_id, analyst, analysis_type, json.dumps(insights)))
            return cur.fetchone()["id"]

    @staticmethod
    def store_conclusion(
        analysis_id: UUID,
        conclusion_text: str,
        confidence_score: float,
        supporting_evidence: Dict,
        created_by: str
    ) -> UUID:
        """Store conclusion based on analysis"""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO conclusions 
                (analysis_id, conclusion_text, confidence_score, supporting_evidence, created_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (analysis_id, conclusion_text, confidence_score, 
                 json.dumps(supporting_evidence), created_by))
            return cur.fetchone()["id"] 