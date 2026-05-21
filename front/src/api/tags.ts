import api from './client';
import type { BookTag } from '../types';

/** Adds a community tag to a book (creating the tag if it's new). */
export const addTag = async (bookId: string, name: string): Promise<BookTag> => {
  const res = await api.post<BookTag>(`/books/${bookId}/tags`, { name });
  return res.data;
};

/** Removes a tag from a book. Allowed for the tag's author or a master. */
export const removeTag = async (bookId: string, tagId: string): Promise<void> => {
  await api.delete(`/books/${bookId}/tags/${tagId}`);
};
