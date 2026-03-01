"""Unit conversion utilities for nutritional calculations."""
import logging

logger = logging.getLogger(__name__)


def convert_to_grams(value: float, unit: str) -> float:
    """
    Convert various units to grams for nutritional calculation.
    
    Args:
        value: The quantity value
        unit: The unit of measurement (g, kg, ml, l, cup, tbsp, tsp)
        
    Returns:
        float: The value converted to grams
        
    Note:
        - For liquids (ml, l), assumes 1:1 density with water
        - Cup/tbsp/tsp are approximate conversions
        - Unknown units default to grams with a warning
    """
    conversions = {
        'g': 1.0,
        'kg': 1000.0,
        'ml': 1.0,  # Assume 1:1 for liquids (water density)
        'l': 1000.0,
        'cup': 240.0,  # Approximate
        'tbsp': 15.0,
        'tsp': 5.0,
    }
    
    unit_lower = unit.lower()
    
    if unit_lower not in conversions:
        logger.warning(f"Unknown unit '{unit}', treating as grams")
        return value
    
    return value * conversions[unit_lower]
