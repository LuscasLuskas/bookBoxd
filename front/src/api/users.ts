import api from './client';
import type { User } from '../types';

export const getMe = async (): Promise<User> => {
  const res = await api.get<User>('/users/me');
  return res.data;
};

export interface UpdateMeInput {
  name?: string;
  bio?: string | null;
  favorite_book_id?: string | null;
}

export const updateMe = async (data: UpdateMeInput): Promise<User> => {
  const res = await api.patch<User>('/users/me', data);
  return res.data;
};

export const uploadAvatar = async (file: File): Promise<User> => {
  const form = new FormData();
  form.append('file', file);
  const res = await api.post<User>('/users/me/avatar', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const deleteMe = async (): Promise<void> => {
  await api.delete('/users/me');
};
