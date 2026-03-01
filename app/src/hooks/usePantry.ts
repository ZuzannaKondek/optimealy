/**
 * Pantry Management Hook
 * 
 * Manages user's pantry items (ingredients they already have).
 */

import { useState, useCallback } from 'react';
import apiClient from '../services/api';

export interface PantryItem {
  product_id: string;
  product_name: string;
  quantity_g: number;
  category: string;
}

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
      const response = await apiClient.get('/users/pantry');
      setState((prev) => ({
        ...prev,
        items: response.data,
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
      const response = await apiClient.get('/users/pantry/staples');
      setState((prev) => ({
        ...prev,
        staples: response.data,
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
  const updatePantry = useCallback(async (items: Array<{product_id: string, quantity_g: number}>) => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      await apiClient.put('/users/pantry', {
        items: items,
      });
      
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

  return {
    ...state,
    fetchPantry,
    fetchStaples,
    updatePantry,
  };
};
