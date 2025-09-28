#!/usr/bin/env python3
"""
Database cleanup script to remove inactive/outdated markets
Improves query performance by keeping only active, relevant markets
"""

import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarketCleanup:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'aigg'),
            'user': os.getenv('DB_USER', 'aigg_user'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_market_stats(self):
        """Get current market statistics"""
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                # Total markets
                cur.execute("SELECT COUNT(*) FROM polymarket_markets")
                total_markets = cur.fetchone()[0]
                
                # Markets by status
                cur.execute("SELECT active, COUNT(*) FROM polymarket_markets GROUP BY active")
                status_counts = dict(cur.fetchall())
                
                # Markets by end date (expired)
                now = datetime.now()
                cur.execute("SELECT COUNT(*) FROM polymarket_markets WHERE end_date < %s", (now,))
                expired_markets = cur.fetchone()[0]
                
                # Markets with NULL end dates (likely old/inactive)
                cur.execute("SELECT COUNT(*) FROM polymarket_markets WHERE end_date IS NULL")
                null_end_date = cur.fetchone()[0]
                
                # Markets older than 6 months (based on last_refreshed)
                six_months_ago = now - timedelta(days=180)
                cur.execute("SELECT COUNT(*) FROM polymarket_markets WHERE last_refreshed < %s", (six_months_ago,))
                old_markets = cur.fetchone()[0]
                
                return {
                    'total': total_markets,
                    'active': status_counts.get(True, 0),
                    'inactive': status_counts.get(False, 0),
                    'expired': expired_markets,
                    'null_end_date': null_end_date,
                    'old': old_markets
                }
    
    def cleanup_expired_markets(self, dry_run=True):
        """Remove markets that have already ended"""
        now = datetime.now()
        
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                # Find expired markets
                cur.execute("""
                    SELECT market_id, title, end_date, last_refreshed
                    FROM polymarket_markets 
                    WHERE end_date < %s
                    ORDER BY end_date DESC
                """, (now,))
                
                expired_markets = cur.fetchall()
                
                if not expired_markets:
                    logger.info("No expired markets found")
                    return 0
                
                logger.info(f"Found {len(expired_markets)} expired markets")
                
                # Show some examples
                for i, (market_id, title, end_date, last_refreshed) in enumerate(expired_markets[:5]):
                    logger.info(f"  {i+1}. {title[:60]}... (ended: {end_date})")
                
                if len(expired_markets) > 5:
                    logger.info(f"  ... and {len(expired_markets) - 5} more")
                
                if not dry_run:
                    # Delete expired markets
                    expired_ids = [m[0] for m in expired_markets]
                    cur.execute("""
                        DELETE FROM polymarket_markets 
                        WHERE market_id = ANY(%s)
                    """, (expired_ids,))
                    
                    logger.info(f"✅ Deleted {len(expired_markets)} expired markets")
                    conn.commit()
                else:
                    logger.info("🔍 DRY RUN - No markets deleted")
                
                return len(expired_markets)
    
    def cleanup_inactive_markets(self, dry_run=True):
        """Remove markets marked as inactive"""
        
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                
                cur.execute("""
                    SELECT market_id, title, last_refreshed, end_date
                    FROM polymarket_markets 
                    WHERE active = false 
                    ORDER BY last_refreshed ASC
                """)
                
                inactive_markets = cur.fetchall()
                
                if not inactive_markets:
                    logger.info("No inactive markets found")
                    return 0
                
                logger.info(f"Found {len(inactive_markets)} inactive markets")
                
                # Show some examples
                for i, (market_id, title, last_refreshed, end_date) in enumerate(inactive_markets[:5]):
                    logger.info(f"  {i+1}. {title[:60]}... (refreshed: {last_refreshed})")
                
                if not dry_run:
                    # Delete inactive markets
                    inactive_ids = [m[0] for m in inactive_markets]
                    cur.execute("""
                        DELETE FROM polymarket_markets 
                        WHERE market_id = ANY(%s)
                    """, (inactive_ids,))
                    
                    logger.info(f"✅ Deleted {len(inactive_markets)} inactive markets")
                    conn.commit()
                else:
                    logger.info("🔍 DRY RUN - No markets deleted")
                
                return len(inactive_markets)
    
    def cleanup_null_end_date_markets(self, dry_run=True):
        """Remove markets with NULL end dates (likely old/broken)"""
        
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                
                cur.execute("""
                    SELECT market_id, title, last_refreshed, active
                    FROM polymarket_markets 
                    WHERE end_date IS NULL
                    AND active = false
                    ORDER BY last_refreshed ASC
                """)
                
                null_markets = cur.fetchall()
                
                if not null_markets:
                    logger.info("No markets with NULL end dates found")
                    return 0
                
                logger.info(f"Found {len(null_markets)} markets with NULL end dates")
                
                if not dry_run:
                    # Delete null end date markets
                    null_ids = [m[0] for m in null_markets]
                    cur.execute("""
                        DELETE FROM polymarket_markets 
                        WHERE market_id = ANY(%s)
                    """, (null_ids,))
                    
                    logger.info(f"✅ Deleted {len(null_markets)} NULL end date markets")
                    conn.commit()
                else:
                    logger.info("🔍 DRY RUN - No markets deleted")
                
                return len(null_markets)
    
    def optimize_database(self):
        """Run database optimization after cleanup"""
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                logger.info("🔧 Running database optimization...")
                
                # Update statistics
                cur.execute("ANALYZE polymarket_markets")
                
            # Vacuum to reclaim space (must be outside transaction)
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                cur.execute("VACUUM polymarket_markets")
                
            logger.info("✅ Database optimization complete")
    
    def find_iran_nuclear_market(self):
        """Find the specific Iran nuclear deal market"""
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT market_id, title, market_slug, end_date, active, last_refreshed
                    FROM polymarket_markets 
                    WHERE title ILIKE '%iran%nuclear%' 
                    OR title ILIKE '%nuclear%iran%'
                    OR market_slug ILIKE '%iran%nuclear%'
                    OR (title ILIKE '%iran%' AND title ILIKE '%deal%')
                    OR market_slug = 'us-x-iran-nuclear-deal-in-2025'
                    ORDER BY last_refreshed DESC
                """)
                
                markets = cur.fetchall()
                
                if markets:
                    logger.info(f"Found {len(markets)} Iran nuclear markets:")
                    for i, (market_id, title, slug, end_date, active, last_refreshed) in enumerate(markets):
                        status = "✅ Active" if active else "❌ Inactive"
                        logger.info(f"  {i+1}. {title}")
                        logger.info(f"      Slug: {slug}")
                        logger.info(f"      End: {end_date} | Refreshed: {last_refreshed} | {status}")
                        logger.info(f"      URL: https://polymarket.com/event/{slug}")
                        logger.info("")
                else:
                    logger.info("❌ No Iran nuclear markets found in database")
                    logger.info("🔍 The market might need to be fetched from Polymarket API")
                
                return markets

def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up inactive Polymarket markets')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Show what would be deleted without actually deleting')
    parser.add_argument('--execute', action='store_true', help='Actually execute the cleanup (removes --dry-run)')
    parser.add_argument('--find-iran', action='store_true', help='Find Iran nuclear deal markets')
    
    args = parser.parse_args()
    
    # If --execute is used, disable dry-run
    if args.execute:
        args.dry_run = False
    
    cleanup = MarketCleanup()
    
    logger.info("🧹 AIGG Market Database Cleanup")
    logger.info("=" * 50)
    
    # Show current stats
    stats = cleanup.get_market_stats()
    logger.info("📊 Current Market Statistics:")
    logger.info(f"   Total markets: {stats['total']:,}")
    logger.info(f"   Active: {stats['active']:,}")
    logger.info(f"   Inactive: {stats['inactive']:,}")
    logger.info(f"   Expired: {stats['expired']:,}")
    logger.info(f"   NULL end dates: {stats['null_end_date']:,}")
    logger.info(f"   Old (6+ months): {stats['old']:,}")
    logger.info("")
    
    if args.find_iran:
        cleanup.find_iran_nuclear_market()
        return
    
    # Show the impact
    inactive_pct = (stats['inactive'] / stats['total']) * 100 if stats['total'] > 0 else 0
    logger.info(f"⚠️  {inactive_pct:.1f}% of markets are INACTIVE - this slows down queries!")
    logger.info("")
    
    # Run cleanup
    total_deleted = 0
    
    # 1. Clean expired markets
    logger.info("🗓️ Cleaning expired markets...")
    deleted = cleanup.cleanup_expired_markets(dry_run=args.dry_run)
    total_deleted += deleted
    logger.info("")
    
    # 2. Clean inactive markets
    logger.info("❌ Cleaning inactive markets...")
    deleted = cleanup.cleanup_inactive_markets(dry_run=args.dry_run)
    total_deleted += deleted
    logger.info("")
    
    # 3. Clean NULL end date markets
    logger.info("🚫 Cleaning NULL end date markets...")
    deleted = cleanup.cleanup_null_end_date_markets(dry_run=args.dry_run)
    total_deleted += deleted
    logger.info("")
    
    # Final stats
    if not args.dry_run and total_deleted > 0:
        cleanup.optimize_database()
        logger.info("")
        
        new_stats = cleanup.get_market_stats()
        logger.info("🏆 Cleanup Complete!")
        logger.info(f"   Markets deleted: {total_deleted:,}")
        logger.info(f"   Markets remaining: {new_stats['total']:,}")
        saved_pct = ((stats['total'] - new_stats['total']) / stats['total'] * 100) if stats['total'] > 0 else 0
        logger.info(f"   Database reduced by: {saved_pct:.1f}%")
        logger.info("   🚀 Queries should be MUCH faster now!")
    else:
        logger.info("🔍 DRY RUN Complete - Use --execute to actually delete markets")

if __name__ == "__main__":
    main() 