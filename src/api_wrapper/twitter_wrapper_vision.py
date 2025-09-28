"""Clean implementation of vision support using DSPy's Image API"""

import dspy
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DescribeMarketImage(dspy.Signature):
    """Extract market-relevant information from an image."""
    image: dspy.Image = dspy.InputField(desc="Image to analyze")
    query: str = dspy.InputField(desc="User's query for context") 
    description: str = dspy.OutputField(desc="Market-relevant facts from the image")

def process_image_with_dspy(image_url: str, query: str, lm_vision) -> Optional[str]:
    """
    Process an image using DSPy's Image API and vision model.
    
    Args:
        image_url: URL of the image to process
        query: User's query for context
        lm_vision: DSPy LM instance configured for vision
        
    Returns:
        Description of market-relevant content or None if failed
    """
    try:
        # Configure DSPy with the vision model
        with dspy.context(lm=lm_vision):
            # Create the image object
            img = dspy.Image.from_url(image_url)
            
            # Create predictor
            predict = dspy.Predict(DescribeMarketImage)
            
            # Get prediction
            result = predict(image=img, query=query)
            
            if result.description:
                # Clean up whitespace
                description = ' '.join(result.description.split())
                logger.info(f"Vision extracted: {description[:100]}...")
                return description
            else:
                logger.warning("Vision model returned empty description")
                return None
                
    except Exception as e:
        logger.error(f"Vision processing failed: {e}")
        return None

def enrich_query_with_images(
    query: str, 
    media_urls: Optional[List[str]], 
    lm_vision
) -> str:
    """
    Enrich a query with context from images if available.
    
    Args:
        query: Original user query
        media_urls: List of image URLs (if any)
        lm_vision: DSPy LM instance configured for vision
        
    Returns:
        Enriched query with image context or original query
    """
    if not media_urls:
        return query
        
    # Process up to 3 images
    trimmed = [u for u in media_urls if isinstance(u, str) and u.strip()][:3]
    
    if not trimmed:
        return query
        
    logger.info(f"Processing {len(trimmed)} image(s) for vision analysis")
    
    # Process each image and combine descriptions
    descriptions = []
    for url in trimmed:
        desc = process_image_with_dspy(url, query, lm_vision)
        if desc:
            descriptions.append(desc)
    
    if descriptions:
        combined = " ".join(descriptions)
        enriched = f"{query}\n[Image context]: {combined}"
        logger.info(f"Query enriched with {len(descriptions)} image description(s)")
        return enriched
    else:
        logger.warning("No image descriptions extracted")
        return query