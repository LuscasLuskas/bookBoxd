import api from './client';
import type { BookClub } from '../types';

export const listClubs = async (): Promise<BookClub[]> => {
  const res = await api.get<BookClub[]>('/clubs');
  return res.data;
};

export const getClub = async (id: string): Promise<BookClub> => {
  const res = await api.get<BookClub>(`/clubs/${id}`);
  return res.data;
};

export const createClub = async (data: {
  name: string;
  description?: string;
}): Promise<BookClub> => {
  const res = await api.post<BookClub>('/clubs', data);
  return res.data;
};

export const updateClub = async (
  id: string,
  data: { name?: string; description?: string }
): Promise<BookClub> => {
  const res = await api.patch<BookClub>(`/clubs/${id}`, data);
  return res.data;
};

export const deleteClub = async (id: string): Promise<void> => {
  await api.delete(`/clubs/${id}`);
};
