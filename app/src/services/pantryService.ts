/**
 * Pantry Service
 *
 * Wrapped API calls for pantry management.
 */

import apiClient from './api';
import type {
  CreatePantryItemRequest,
  PantryItem,
  UpdatePantryItemRequest,
} from '../types/models';

export const pantryService = {
  async getPantry(): Promise<PantryItem[]> {
    const response = await apiClient.get<PantryItem[]>('/users/pantry');
    return response.data;
  },

  async addPantryItem(item: CreatePantryItemRequest): Promise<PantryItem> {
    const response = await apiClient.post<PantryItem>('/users/pantry/items', item);
    return response.data;
  },

  async updatePantryItem(itemId: string, data: UpdatePantryItemRequest): Promise<PantryItem> {
    const response = await apiClient.patch<PantryItem>(`/users/pantry/items/${itemId}`, data);
    return response.data;
  },

  async deletePantryItem(itemId: string): Promise<void> {
    await apiClient.delete(`/users/pantry/items/${itemId}`);
  },

  async getPantryStaples(): Promise<any[]> {
    const response = await apiClient.get<any[]>('/users/pantry/staples');
    return response.data;
  },

  async updatePantry(items: Array<{product_id: string; quantity_g: number; expiry_date?: string}>): Promise<void> {
    await apiClient.put('/users/pantry', { items });
  },
};
