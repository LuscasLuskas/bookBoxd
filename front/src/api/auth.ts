import api from './client';

export const loginWithGoogle = async (idToken: string): Promise<string> => {
  const res = await api.post<{ access_token: string }>('/auth/google', { id_token: idToken });
  return res.data.access_token;
};
