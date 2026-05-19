import api from './client';
import type { Book, BookListResponse } from '../types';

export const listBooks = async (params?: {
  limit?: number;
  offset?: number;
  title?: string;
  author?: string;
}): Promise<BookListResponse> => {
  const res = await api.get<BookListResponse>('/books', { params });
  return res.data;
};

export const getBook = async (id: string): Promise<Book> => {
  const res = await api.get<Book>(`/books/${id}`);
  return res.data;
};

export const createBook = async (data: {
  title: string;
  author: string;
  synopsis?: string;
}): Promise<Book> => {
  const res = await api.post<Book>('/books', data);
  return res.data;
};
