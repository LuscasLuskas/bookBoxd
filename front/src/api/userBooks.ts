import api from './client';
import type { UserBook, UserBookListResponse, UserBookStatus } from '../types';

export const listLibrary = async (params?: {
  limit?: number;
  offset?: number;
  status?: UserBookStatus;
}): Promise<UserBookListResponse> => {
  const res = await api.get<UserBookListResponse>('/me/books', { params });
  return res.data;
};

export const addToLibrary = async (
  bookId: string,
  status?: UserBookStatus
): Promise<UserBook> => {
  const res = await api.post<UserBook>('/me/books', { book_id: bookId, status });
  return res.data;
};

export const updateBookStatus = async (
  bookId: string,
  status: UserBookStatus
): Promise<UserBook> => {
  const res = await api.patch<UserBook>(`/me/books/${bookId}`, { status });
  return res.data;
};

export const removeFromLibrary = async (bookId: string): Promise<void> => {
  await api.delete(`/me/books/${bookId}`);
};
