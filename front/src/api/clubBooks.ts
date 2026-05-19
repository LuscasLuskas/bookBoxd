import api from './client';
import type { ClubBook, ClubBookListResponse } from '../types';

export const listClubBooks = async (
  clubId: string,
  params?: { limit?: number; offset?: number }
): Promise<ClubBookListResponse> => {
  const res = await api.get<ClubBookListResponse>(`/clubs/${clubId}/books`, { params });
  return res.data;
};

export const addBookToClub = async (
  clubId: string,
  bookId: string
): Promise<ClubBook> => {
  const res = await api.post<ClubBook>(`/clubs/${clubId}/books`, { book_id: bookId });
  return res.data;
};

export const removeBookFromClub = async (
  clubId: string,
  bookId: string
): Promise<void> => {
  await api.delete(`/clubs/${clubId}/books/${bookId}`);
};
