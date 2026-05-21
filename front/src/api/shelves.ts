import api from './client';
import type { Shelf, ShelfDetail } from '../types';

export const listShelves = async (): Promise<Shelf[]> => {
  const res = await api.get<{ items: Shelf[] }>('/me/shelves');
  return res.data.items;
};

export const getShelf = async (shelfId: string): Promise<ShelfDetail> => {
  const res = await api.get<ShelfDetail>(`/me/shelves/${shelfId}`);
  return res.data;
};

export const createShelf = async (name: string): Promise<Shelf> => {
  const res = await api.post<Shelf>('/me/shelves', { name });
  return res.data;
};

export const deleteShelf = async (shelfId: string): Promise<void> => {
  await api.delete(`/me/shelves/${shelfId}`);
};

export const addBookToShelf = async (
  shelfId: string,
  bookId: string
): Promise<Shelf> => {
  const res = await api.post<Shelf>(`/me/shelves/${shelfId}/books`, {
    book_id: bookId,
  });
  return res.data;
};

export const removeBookFromShelf = async (
  shelfId: string,
  bookId: string
): Promise<void> => {
  await api.delete(`/me/shelves/${shelfId}/books/${bookId}`);
};
