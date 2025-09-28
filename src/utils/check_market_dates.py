#!/usr/bin/env python3
"""
Check market date distribution and identify old markets that should be deactivated
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def check_market_dates():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'), 
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

    cur = conn.cursor(cursor_factory=RealDictCursor)

    print('📊 Current market distribution by year:')
    cur.execute("""
        SELECT 
            EXTRACT(YEAR FROM end_date) as year,
            COUNT(*) as count,
            COUNT(CASE WHEN active = true THEN 1 END) as active_count
        FROM polymarket_markets 
        WHERE end_date IS NOT NULL
        GROUP BY EXTRACT(YEAR FROM end_date)
        ORDER BY year
    """)

    for row in cur.fetchall():
        year = int(row["year"]) if row["year"] else "NULL"
        print(f'  {year}: {row["count"]} total, {row["active_count"]} marked active')

    print('\n📅 Markets with end_date > June 1, 2025:')
    cur.execute("""
        SELECT COUNT(*) as count
        FROM polymarket_markets 
        WHERE end_date > '2025-06-01'
    """)
    future_count = cur.fetchone()['count']
    print(f'  {future_count} markets end after June 1, 2025')

    print('\n🕐 Sample of markets marked active but ended before 2025:')
    cur.execute("""
        SELECT title, end_date, active
        FROM polymarket_markets 
        WHERE active = true AND end_date < '2025-01-01'
        ORDER BY end_date DESC
        LIMIT 5
    """)
    
    for row in cur.fetchall():
        print(f'  "{row["title"][:60]}..." - ends {row["end_date"]} - active: {row["active"]}')

    conn.close()

if __name__ == "__main__":
    check_market_dates() 