/**
 * Product Service
 * OptiMeal Mobile App
 *
 * API client for product operations.
 */

import apiClient from './api';

export interface ProductSearchResult {
  product_id: string;
  product_name: string;
  category: string;
  unit: string;
}

export const productService = {
  /**
   * Search products by name.
   */
  async searchProducts(query: string, limit: number = 20): Promise<ProductSearchResult[]> {
    if (!query || query.trim().length < 2) {
      return [];
    }
    
    const params = new URLSearchParams();
    params.append('q', query.trim());
    params.append('limit', limit.toString());

    const response = await apiClient.get<ProductSearchResult[]>(
      `/users/pantry/products/search?${params.toString()}`
    );
    return response.data;
  },
};
