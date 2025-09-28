"""
Polymarket URL Fixer
Maps database slugs to correct Polymarket URLs
"""

import requests
from typing import Optional
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

# Known correct URLs for popular markets - with proper child URLs for previews
KNOWN_CORRECT_URLS = {
    # Fed markets - use child URLs for better previews
    "fed-decreases-interest-rates-by-25-bps-after-september-2025-meeting": "https://polymarket.com/event/fed-decision-in-september/fed-decreases-interest-rates-by-25-bps-after-september-2025-meeting?tid=1756309420955",
    "fed-increases-interest-rates-by-25-bps-after-september-2025-meeting": "https://polymarket.com/event/fed-decision-in-september/fed-increases-interest-rates-by-25-bps-after-september-2025-meeting?tid=1756309478512",
    "no-change-in-fed-interest-rates-after-september-2025-meeting": "https://polymarket.com/event/fed-decision-in-september/no-change-in-fed-interest-rates-after-september-2025-meeting?tid=1756309466874",
    "fed-rate-cut-by-september-meeting": "https://polymarket.com/event/fed-decision-in-september/fed-decreases-interest-rates-by-25-bps-after-september-2025-meeting?tid=1756309420955",
    "fed-decision-in-september": "https://polymarket.com/event/fed-decision-in-september?tid=1756309481745",
    
    # October Fed markets - use exact URL from Polymarket for clean previews  
    "fed-decision-in-october": "https://polymarket.com/event/fed-decision-in-october?tid=1758975401095",
    "no-change-in-fed-interest-rates-after-october-2025-meeting": "https://polymarket.com/event/fed-decision-in-october?tid=1758975401095",
    "fed-decreases-interest-rates-by-25-bps-after-october-2025-meeting": "https://polymarket.com/event/fed-decision-in-october?tid=1758975401095",
    "fed-increases-interest-rates-by-25-bps-after-october-2025-meeting": "https://polymarket.com/event/fed-decision-in-october?tid=1758975401095",
    
    # Bitcoin markets - use milestone markets with good previews, not daily up/down
    "will-bitcoin-reach-200000-by-december-31-2025": "https://polymarket.com/event/will-bitcoin-reach-200000-by-december-31st-2025",
    "will-bitcoin-reach-200k-in-august": "https://polymarket.com/event/will-bitcoin-reach-200k-in-august-2025",
    "will-bitcoin-reach-150k-in-august": "https://polymarket.com/event/will-bitcoin-reach-150000-in-august-2025",
    "will-bitcoin-reach-125k-in-august": "https://polymarket.com/event/will-bitcoin-reach-125000-in-august-2025",
    "will-bitcoin-dip-to-100k-in-august": "https://polymarket.com/event/will-bitcoin-drop-below-100k-in-august-2025",
    # Avoid daily up/down markets - they have poor previews
    "bitcoin-up-or-down": "SKIP",  # Don't use daily markets
    
    # Trump markets
    "who-will-trump-pardon-in-2025": "https://polymarket.com/event/who-will-trump-pardon-in-2025",
    "will-trump-pardon-hunter-biden-in-2025": "https://polymarket.com/event/who-will-trump-pardon-in-2025",
    
    # Powell markets
    "jerome-powell-out-as-fed-chair-by-september-30": "https://polymarket.com/event/jerome-powell-out-as-fed-chair-2025",
    "jerome-powell-out-as-fed-chair-in-2025": "https://polymarket.com/event/jerome-powell-out-as-fed-chair-2025",
    
    # Bayrou French PM markets - use child URLs for excellent Twitter preview cards
    "bayrou-out-as-french-pm-by-september-30-767": "https://polymarket.com/event/bayrou-out-as-french-pm-in-2025/bayrou-out-as-french-pm-by-september-30-767?tid=1756310755822",
    "bayrou-out-as-french-pm-in-2025-833": "https://polymarket.com/event/bayrou-out-as-french-pm-in-2025/bayrou-out-as-french-pm-in-2025-833?tid=1756310780677",
    "will-francois-bayrou-be-the-next-french-prime-minister": "https://polymarket.com/event/will-francois-bayrou-be-the-next-french-prime-minister",
    
    # US Open 2025 markets - use child URLs for rich Twitter previews (with dynamic tid)
    "will-carlos-alcaraz-win-the-2025-us-open": "DYNAMIC_TID:https://polymarket.com/event/2025-us-open-winner-m/will-carlos-alcaraz-win-the-2025-us-open",
    "will-carlos-alcaraz-win-the-us-open": "DYNAMIC_TID:https://polymarket.com/event/2025-us-open-winner-m/will-carlos-alcaraz-win-the-2025-us-open",
    "will-jannik-sinner-win-the-2025-us-open": "https://polymarket.com/event/2025-us-open-winner-m/will-jannik-sinner-win-the-2025-us-open?tid=1756327934000",
    "will-novak-djokovic-win-the-2025-us-open": "https://polymarket.com/event/2025-us-open-winner-m/will-novak-djokovic-win-the-2025-us-open?tid=1756327935000",
    "will-taylor-fritz-win-the-2025-us-open": "https://polymarket.com/event/2025-us-open-winner-m/will-taylor-fritz-win-the-2025-us-open?tid=1756327936000",
    "2025-us-open-winner-m": "https://polymarket.com/event/2025-us-open-winner-m",
    
    # Women's US Open - also needs rich previews
    "will-ashlyn-krueger-win-the-2025-us-open": "https://polymarket.com/event/2025-us-open-winner-w/will-ashlyn-krueger-win-the-2025-us-open?tid=1756327940000",
    "2025-us-open-winner-w": "https://polymarket.com/event/2025-us-open-winner-w",
    
    # Popular markets with rich preview URLs (manually found tid values)
    # Super Bowl
    "super-bowl-winning-conference": "https://polymarket.com/event/super-bowl-winning-conference",
    "will-the-kansas-city-chiefs-win-the-super-bowl": "https://polymarket.com/event/super-bowl-2025-winner/will-the-kansas-city-chiefs-win-the-super-bowl?tid=1756331000000",
    
    # Russia Ukraine
    "russia-x-ukraine-ceasefire-by-october-31": "https://polymarket.com/event/russia-x-ukraine-ceasefire-by-october-31",
    
    # Recession markets
    "us-recession-in-2025": "https://polymarket.com/event/us-recession-in-2025",
}

def validate_url(url: str) -> bool:
    """Check if a Polymarket URL is valid"""
    try:
        # Quick check - don't follow redirects to save time
        response = requests.head(url, allow_redirects=False, timeout=2)
        # 200 or 301/302 redirects are OK
        return response.status_code in [200, 301, 302]
    except:
        return False

def get_corrected_url(market_slug: str, market_title: str = "", market_id: str = "") -> str:
    """Get the correct Polymarket URL for a market"""
    
    # Skip daily up/down markets - they have poor previews
    if "up-or-down" in market_slug.lower() and "bitcoin" in market_slug.lower():
        # Try to find a better Bitcoin market
        if "bitcoin" in market_title.lower():
            if "200" in market_title:
                return "https://polymarket.com/event/will-bitcoin-reach-200000-by-december-31st-2025"
            elif "150" in market_title:
                return "https://polymarket.com/event/will-bitcoin-reach-150000-in-august-2025"
            elif "125" in market_title:
                return "https://polymarket.com/event/will-bitcoin-reach-125000-in-august-2025"
            else:
                # Default to the 200K market for good preview
                return "https://polymarket.com/event/will-bitcoin-reach-200000-by-december-31st-2025"
    
    # Check if we have a known correct URL
    if market_slug in KNOWN_CORRECT_URLS:
        url = KNOWN_CORRECT_URLS[market_slug]
        if url == "SKIP":
            # This market should be skipped, find alternative
            return "https://polymarket.com/event/will-bitcoin-reach-200000-by-december-31st-2025"
        
        # Handle dynamic TID for fresh previews
        if url.startswith("DYNAMIC_TID:"):
            import time
            base_url = url.replace("DYNAMIC_TID:", "")
            tid = int(time.time() * 1000)
            return f"{base_url}?tid={tid}"
        
        return url
    
    # Special check for Alcaraz US Open markets - force rich preview URL regardless of exact slug
    if ("alcaraz" in market_slug.lower() and "us" in market_slug.lower()) or \
       ("alcaraz" in market_title.lower() and "us open" in market_title.lower()):
        return "https://polymarket.com/event/2025-us-open-winner-m/will-carlos-alcaraz-win-the-2025-us-open?tid=1756330398593"
    
    # Check partial matches for Fed markets - use correct month
    if "fed" in market_slug.lower() and ("september" in market_slug.lower() or "october" in market_slug.lower()):
        if "october" in market_slug.lower() or "october" in market_title.lower():
            # October Fed markets - use the exact clean preview URL
            return "https://polymarket.com/event/fed-decision-in-october?tid=1758975401095"
        elif "september" in market_slug.lower():
            parent = "fed-decision-in-september"
            # Determine which specific option based on the slug
            if "decrease" in market_slug.lower() and "25" in market_slug:
                return f"https://polymarket.com/event/{parent}/fed-decreases-interest-rates-by-25-bps-after-september-2025-meeting?tid=1756309420955"
            elif "increase" in market_slug.lower() and "25" in market_slug:
                return f"https://polymarket.com/event/{parent}/fed-increases-interest-rates-by-25-bps-after-september-2025-meeting?tid=1756309478512"
            elif "no-change" in market_slug.lower() or "no change" in market_title.lower():
                return f"https://polymarket.com/event/{parent}/no-change-in-fed-interest-rates-after-september-2025-meeting?tid=1756309466874"
            else:
                # Default to parent if we can't determine specific option
                return f"https://polymarket.com/event/{parent}?tid=1756309481745"
    
    # Check for Bitcoin markets - prefer milestone markets with good previews
    if ("bitcoin" in market_slug.lower() or "btc" in market_slug.lower()) and "up-or-down" not in market_slug.lower():
        if "200" in market_slug or "200k" in market_slug or "200000" in market_slug:
            return "https://polymarket.com/event/will-bitcoin-reach-200000-by-december-31st-2025"
        elif "150" in market_slug or "150k" in market_slug or "150000" in market_slug:
            return "https://polymarket.com/event/will-bitcoin-reach-150000-in-august-2025"
        elif "125" in market_slug or "125k" in market_slug or "125000" in market_slug:
            return "https://polymarket.com/event/will-bitcoin-reach-125000-in-august-2025"
        elif "100" in market_slug or "100k" in market_slug:
            return "https://polymarket.com/event/will-bitcoin-drop-below-100k-in-august-2025"
    
    # Check for Trump pardon markets - use child URLs for specific people
    if "trump" in market_slug.lower() and "pardon" in market_slug.lower():
        # For Matt Gaetz specifically
        if "matt-gaetz" in market_slug.lower() or "gaetz" in market_slug.lower():
            return "https://polymarket.com/event/who-will-trump-pardon-in-2025/will-trump-pardon-matt-gaetz-in-2025?tid=1756325631345"
        # For Derek Chauvin specifically  
        elif "derek-chauvin" in market_slug.lower() or "chauvin" in market_slug.lower():
            return "https://polymarket.com/event/who-will-trump-pardon-in-2025/will-trump-pardon-derek-chauvin-in-2025?tid=1756325635562"
        # For Diddy specifically
        elif "diddy" in market_slug.lower():
            return "https://polymarket.com/event/who-will-trump-pardon-in-2025/will-trump-pardon-diddy-in-2025?tid=1756325639299"
        # If general query, use parent URL
        elif market_title and "who will trump pardon" in market_title.lower():
            return "https://polymarket.com/event/who-will-trump-pardon-in-2025"
        # For other specific pardons, use the specific market slug
        else:
            return f"https://polymarket.com/event/who-will-trump-pardon-in-2025/{market_slug}?tid=1756325000000"
    
    # Check for Bayrou/French PM markets
    if "bayrou" in market_slug.lower() or "bayrou" in market_title.lower():
        if "september" in market_slug.lower() or "september" in market_title.lower():
            return "https://polymarket.com/event/bayrou-out-as-french-pm-in-2025/bayrou-out-as-french-pm-by-september-30-767?tid=1756310755822"
        elif "2025" in market_slug.lower() or "2025" in market_title.lower():
            return "https://polymarket.com/event/bayrou-out-as-french-pm-in-2025/bayrou-out-as-french-pm-in-2025-833?tid=1756310780677"
    
    # Check for US Open 2025 markets - route to specific players for rich previews
    if ("us open" in market_slug.lower() or "us open" in market_title.lower() or 
        "us-open" in market_slug.lower() or "2025-us-open" in market_slug.lower()):
        
        # Check for women's players first
        if ("krueger" in market_slug.lower() or "krueger" in market_title.lower() or
            "ashlyn" in market_slug.lower() or "ashlyn" in market_title.lower()):
            return "https://polymarket.com/event/2025-us-open-winner-w/will-ashlyn-krueger-win-the-2025-us-open?tid=1756327940000"
        
        # Check for men's players
        elif "alcaraz" in market_slug.lower() or "alcaraz" in market_title.lower():
            return "https://polymarket.com/event/2025-us-open-winner-m/will-carlos-alcaraz-win-the-2025-us-open?tid=1756327934093"
        elif "sinner" in market_slug.lower() or "sinner" in market_title.lower():
            return "https://polymarket.com/event/2025-us-open-winner-m/will-jannik-sinner-win-the-2025-us-open?tid=1756327934000"
        elif "djokovic" in market_slug.lower() or "djokovic" in market_title.lower():
            return "https://polymarket.com/event/2025-us-open-winner-m/will-novak-djokovic-win-the-2025-us-open?tid=1756327935000"
        elif "fritz" in market_slug.lower() or "fritz" in market_title.lower():
            return "https://polymarket.com/event/2025-us-open-winner-m/will-taylor-fritz-win-the-2025-us-open?tid=1756327936000"
        
        # For general US Open queries, check if it's women's specific
        elif ("women" in market_slug.lower() or "women" in market_title.lower() or
              "w)" in market_title.lower() or "winner-w" in market_slug.lower()):
            return "https://polymarket.com/event/2025-us-open-winner-w"
        
        else:
            # Default to men's Alcaraz for general US Open queries (most popular, best preview)
            return "https://polymarket.com/event/2025-us-open-winner-m/will-carlos-alcaraz-win-the-2025-us-open?tid=1756330398593"
    
    # Try to construct rich preview URLs for common patterns
    if try_construct_rich_url(market_slug, market_title):
        rich_url = try_construct_rich_url(market_slug, market_title)
        if rich_url:
            return rich_url
    
    # Default: construct URL from slug
    base_url = f"https://polymarket.com/event/{market_slug}"
    
    # Validate if possible (but don't block if network is slow)
    try:
        if validate_url(base_url):
            return base_url
    except:
        pass
    
    # If validation failed or we can't check, still return it
    # (better to have a potentially wrong URL than no URL)
    return base_url

def try_construct_rich_url(market_slug: str, market_title: str) -> Optional[str]:
    """Try to construct a rich preview URL for common market patterns"""
    import time
    
    # Generate current timestamp for tid (milliseconds)
    tid = int(time.time() * 1000)
    
    # Multi-choice market patterns - these need parent/child URL structure for rich previews
    
    # US Open patterns
    if "us-open" in market_slug or "us open" in market_title.lower():
        parent = "2025-us-open-winner-m"
        # Try to use the actual slug, or construct one
        if "alcaraz" in market_slug.lower() or "alcaraz" in market_title.lower():
            child = "will-carlos-alcaraz-win-the-2025-us-open"
        elif "sinner" in market_slug.lower() or "sinner" in market_title.lower():
            child = "will-jannik-sinner-win-the-2025-us-open"
        elif "fritz" in market_slug.lower() or "fritz" in market_title.lower():
            child = "will-taylor-fritz-win-the-2025-us-open"
        else:
            # Try to use the market slug if it looks right
            child = market_slug if "win" in market_slug else None
        
        if child:
            return f"https://polymarket.com/event/{parent}/{child}?tid={tid}"
    
    # Trump pardon patterns (multi-choice)
    if "trump" in market_slug.lower() and "pardon" in market_slug.lower():
        parent = "who-will-trump-pardon-in-2025"
        # Use actual market slug for child
        if market_slug.startswith("will-trump-pardon-"):
            return f"https://polymarket.com/event/{parent}/{market_slug}?tid={tid}"
        # Construct from title
        elif "gaetz" in market_title.lower():
            return f"https://polymarket.com/event/{parent}/will-trump-pardon-matt-gaetz-in-2025?tid={tid}"
        elif "chauvin" in market_title.lower():
            return f"https://polymarket.com/event/{parent}/will-trump-pardon-derek-chauvin-in-2025?tid={tid}"
        elif "diddy" in market_title.lower():
            return f"https://polymarket.com/event/{parent}/will-trump-pardon-diddy-in-2025?tid={tid}"
    
    # Fed decision patterns (multi-choice)
    if "fed" in market_slug.lower() and ("september" in market_slug.lower() or "rate" in market_slug.lower()):
        parent = "fed-decision-in-september"
        if "25-bps" in market_slug or "decrease" in market_slug:
            child = "fed-decreases-interest-rates-by-25-bps-after-september-2025-meeting"
        elif "increase" in market_slug:
            child = "fed-increases-interest-rates-by-25-bps-after-september-2025-meeting"
        elif "no-change" in market_slug:
            child = "no-change-in-fed-interest-rates-after-september-2025-meeting"
        else:
            child = None
        
        if child:
            return f"https://polymarket.com/event/{parent}/{child}?tid={tid}"
    
    return None

def get_polymarket_url(market_slug: str, market_title: str = "", market_id: str = "") -> str:
    """
    Get the best Polymarket URL for a market
    Tries correction first, then falls back to search if needed
    """
    
    # Get corrected URL - pass all parameters
    url = get_corrected_url(market_slug, market_title, market_id)
    
    # Log if we're using a correction
    if market_slug in KNOWN_CORRECT_URLS:
        logger.info(f"Using corrected URL for {market_slug}: {url}")
    
    return url