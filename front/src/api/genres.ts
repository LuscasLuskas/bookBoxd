import api from './client';
import type { Genre } from '../types';

/** All genres known to the catalog (used to build the Books filter). */
export const listGenres = async (): Promise<Genre[]> => {
  const res = await api.get<{ items: Genre[] }>('/genres');
  return res.data.items;
};
