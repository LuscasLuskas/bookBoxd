import api from './client';
import type { User } from '../types';

export const getMe = async (): Promise<User> => {
  const res = await api.get<User>('/users/me');
  return res.data;
};

export const deleteMe = async (): Promise<void> => {
  await api.delete('/users/me');
};
