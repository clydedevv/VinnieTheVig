#!/usr/bin/env python3
"""
Cleanup Old Markets Script
Removes outdated/closed markets from database to fix bot responses
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def cleanup_old_markets():
    """Remove old/closed markets from database"""
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    
    try:
        # Get initial counts
        cur.execute('SELECT COUNT(*) FROM polymarket_markets')
        initial_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM polymarket_markets WHERE active = true')
        active_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM polymarket_markets WHERE active = false')
        inactive_count = cur.fetchone()[0]
        
        print(f"📊 Initial database state:")
        print(f"   Total markets: {initial_count}")
        print(f"   Active markets: {active_count}")
        print(f"   Inactive markets: {inactive_count}")
        
        # Check for markets with end_date in the past
        cur.execute("""
            SELECT COUNT(*) FROM polymarket_markets 
            WHERE end_date < NOW() AND active = true
        """)
        expired_active = cur.fetchone()[0]
        
        print(f"   Expired but marked active: {expired_active}")
        
        # Strategy 1: Delete all inactive markets (they're old anyway)
        print(f"\n🗑️ Deleting {inactive_count} inactive markets...")
        cur.execute('DELETE FROM polymarket_markets WHERE active = false')
        deleted_inactive = cur.rowcount
        
        # Strategy 2: Delete markets with end_date in the past
        print(f"🗑️ Deleting expired markets...")
        cur.execute('DELETE FROM polymarket_markets WHERE end_date < NOW()')
        deleted_expired = cur.rowcount
        
        # Strategy 3: Delete markets from before 2025 (old sports/election markets)
        print(f"🗑️ Deleting pre-2025 markets...")
        cur.execute("DELETE FROM polymarket_markets WHERE end_date < '2025-01-01'")
        deleted_old = cur.rowcount
        
        # Strategy 4: Delete markets with NULL end_date (probably broken data)
        print(f"🗑️ Deleting markets with NULL end_date...")
        cur.execute('DELETE FROM polymarket_markets WHERE end_date IS NULL')
        deleted_null = cur.rowcount
        
        # Commit changes
        conn.commit()
        
        # Get final counts
        cur.execute('SELECT COUNT(*) FROM polymarket_markets')
        final_count = cur.fetchone()[0]
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Markets deleted: {initial_count - final_count}")
        print(f"   Markets remaining: {final_count}")
        print(f"   Deleted inactive: {deleted_inactive}")
        print(f"   Deleted expired: {deleted_expired}")
        print(f"   Deleted pre-2025: {deleted_old}")
        print(f"   Deleted NULL dates: {deleted_null}")
        
        # Show remaining markets
        if final_count > 0:
            cur.execute('SELECT title, end_date FROM polymarket_markets ORDER BY end_date DESC LIMIT 10')
            remaining = cur.fetchall()
            print(f"\n📋 Remaining markets (top 10):")
            for title, end_date in remaining:
                print(f"   {end_date} | {title[:80]}")
        else:
            print("\n⚠️ No markets remaining! Database is empty.")
            print("   You need to run the populate script to add current markets.")
    
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        conn.rollback()
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("🧹 AIGG Markets Database Cleanup")
    print("=" * 50)
    
    response = input("This will delete old/inactive markets. Continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        cleanup_old_markets()
    else:
        print("Cleanup cancelled.") 