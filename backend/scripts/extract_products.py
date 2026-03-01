"""Extract product data for recipe generation."""
import json
from pathlib import Path


def load_products():
    """Load products and return as lookup dict."""
    products_file = Path(__file__).parent.parent / 'data' / 'products' / 'sample-products.json'
    with open(products_file, 'r') as f:
        products = json.load(f)
    
    # Create lookup by name
    product_lookup = {}
    for p in products:
        product_lookup[p['name']] = {
            'calories_per_100g': p['nutritional_info_per_100g']['calories'],
            'protein_per_100g': p['nutritional_info_per_100g']['protein'],
            'carbs_per_100g': p['nutritional_info_per_100g']['carbs'],
            'fat_per_100g': p['nutritional_info_per_100g']['fat'],
            'fiber_per_100g': p['nutritional_info_per_100g'].get('fiber', 0),
        }
    
    return product_lookup, list(product_lookup.keys())


if __name__ == '__main__':
    lookup, names = load_products()
    print(f'Loaded {len(names)} products')
    print(f'Available ingredients: {", ".join(sorted(names)[:10])}...')
