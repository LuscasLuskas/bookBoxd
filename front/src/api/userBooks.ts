import api from './client';
import type {
  LibraryStats,
  UserBook,
  UserBookListResponse,
  UserBookStatus,
} from '../types';

export const listLibrary = async (params?: {
  limit?: number;
  offset?: number;
  status?: UserBookStatus;
}): Promise<UserBookListResponse> => {
  const res = await api.get<UserBookListResponse>('/me/books', { params });
  return res.data;
};

/** Reading-stats counts per status — accurate regardless of library size. */
export const getLibraryStats = async (): Promise<LibraryStats> => {
  const res = await api.get<LibraryStats>('/me/books/stats');
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

/** Set the personal star rating (0.5–5.0). Pass null to clear it. */
export const rateBook = async (
  bookId: string,
  rating: number | null
): Promise<UserBook> => {
  const res = await api.patch<UserBook>(`/me/books/${bookId}/rating`, { rating });
  return res.data;
};

export const removeFromLibrary = async (bookId: string): Promise<void> => {
  await api.delete(`/me/books/${bookId}`);
};
