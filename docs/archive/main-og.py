import logging
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from db.connection import get_db_connection

# Add the insights router import
from api.insights import router as insights_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/aigg-api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIGG Insights API",
    description="API for accessing Polymarket data and research insights"
)

# Add the router inclusion here
app.include_router(insights_router, prefix="")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AIGG API")
    # Test database connection
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return {"status": "healthy", "timestamp": str(datetime.utcnow())}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/markets")
async def get_markets(
    active: Optional[bool] = True,
    include_closed: Optional[bool] = False,
    limit: int = Query(default=10, le=100)
):
    """Get markets with optional filters"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        market_id,
                        question,
                        description,
                        volume_24h,
                        active,
                        end_date,
                        outcomes,
                        outcome_prices,
                        closed,
                        last_updated
                    FROM polymarket_odds 
                    WHERE 1=1
                """
                params = []

                if active and not include_closed:
                    query += """ 
                        AND active = true 
                        AND end_date > NOW() 
                        AND closed = false
                    """
                elif include_closed:
                    query += " AND end_date <= NOW() OR closed = true"

                query += " ORDER BY volume_24h DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)
                markets = cur.fetchall()
                return markets

    except Exception as e:
        logger.error(f"Error fetching markets: {str(e)}")
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
                        question,
                        description,
                        volume_24h,
                        active,
                        end_date,
                        outcomes,
                        outcome_prices,
                        last_updated
                    FROM polymarket_odds 
                    WHERE market_id = %s
                """, (market_id,))
                market = cur.fetchone()
                
                if not market:
                    raise HTTPException(status_code=404, detail="Market not found")
                
                return market

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get list of available categories"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM categories")
                return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 