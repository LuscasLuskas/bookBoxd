import api from './client';
import type {
  LibraryStats,
  PublicUser,
  ReviewListResponse,
  User,
  UserBookListResponse,
  UserBookStatus,
} from '../types';

export const getMe = async (): Promise<User> => {
  const res = await api.get<User>('/users/me');
  return res.data;
};

export const getUserProfile = async (userId: string): Promise<PublicUser> => {
  const res = await api.get<PublicUser>(`/users/${userId}`);
  return res.data;
};

export const getUserBooks = async (
  userId: string,
  params?: { limit?: number; offset?: number; status?: UserBookStatus },
): Promise<UserBookListResponse> => {
  const res = await api.get<UserBookListResponse>(`/users/${userId}/books`, {
    params,
  });
  return res.data;
};

export const getUserBookStats = async (userId: string): Promise<LibraryStats> => {
  const res = await api.get<LibraryStats>(`/users/${userId}/books/stats`);
  return res.data;
};

export const getUserReviews = async (
  userId: string,
): Promise<ReviewListResponse> => {
  const res = await api.get<ReviewListResponse>(`/users/${userId}/reviews`);
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
