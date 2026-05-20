import api from './client';
import type { Book, BookListResponse, ExternalBookResult } from '../types';

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

export interface CreateBookInput {
  title: string;
  author: string;
  synopsis?: string;
  cover_url?: string | null;
  external_id?: string | null;
  published_year?: number | null;
  isbn?: string | null;
}

export const createBook = async (data: CreateBookInput): Promise<Book> => {
  const res = await api.post<Book>('/books', data);
  return res.data;
};

/** Searches the Open Library catalog (results are not yet saved). */
export const searchExternalBooks = async (
  q: string,
): Promise<ExternalBookResult[]> => {
  const res = await api.get<{ items: ExternalBookResult[] }>(
    '/books/search-external',
    { params: { q } },
  );
  return res.data.items;
};
