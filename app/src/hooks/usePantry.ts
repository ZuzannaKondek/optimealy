/**
 * Pantry Management Hook
 * 
 * Manages user's pantry items (ingredients they already have).
 */

import { useState, useCallback } from 'react';
import { pantryService } from '../services/pantryService';
import { productService, type ProductSearchResult } from '../services/productService';
import type { PantryItem } from '../types/models';

export interface PantryStaple {
  product_id: string;
  product_name: string;
  category: string;
  default_quantity_g: number;
  icon: string;
}

interface PantryState {
  items: PantryItem[];
  staples: PantryStaple[];
  isLoading: boolean;
  error: string | null;
}

export const usePantry = () => {
  const [state, setState] = useState<PantryState>({
    items: [],
    staples: [],
    isLoading: false,
    error: null,
  });

  /**
   * Fetch user's current pantry items
   */
  const fetchPantry = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const pantryItems = await pantryService.getPantry();
      setState((prev) => ({
        ...prev,
        items: pantryItems,
        isLoading: false,
      }));
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Failed to fetch pantry',
      }));
      throw error;
    }
  }, []);

  /**
   * Fetch available pantry staples (curated list)
   */
  const fetchStaples = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const staples = await pantryService.getPantryStaples();
      setState((prev) => ({
        ...prev,
        staples,
        isLoading: false,
      }));
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Failed to fetch staples',
      }));
      throw error;
    }
  }, []);

  /**
   * Update user's pantry with items and quantities
   */
  const updatePantry = useCallback(async (items: Array<{product_id: string, quantity_g: number, expiry_date?: string}>) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      await pantryService.updatePantry(items);
      
      // Refresh pantry after update
      await fetchPantry();
      
      return true;
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Failed to update pantry',
      }));
      throw error;
    }
  }, [fetchPantry]);

  /**
   * Search products by name
   */
  const searchProducts = useCallback(async (query: string): Promise<ProductSearchResult[]> => {
    try {
      return await productService.searchProducts(query);
    } catch (error: any) {
      console.error('Product search failed:', error);
      return [];
    }
  }, []);

  return {
    ...state,
    fetchPantry,
    fetchStaples,
    updatePantry,
    searchProducts,
  };
};
