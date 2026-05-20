const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Resolves a stored avatar path into a full URL.
 * The backend stores avatars as a relative path like "/uploads/avatars/x.jpg".
 */
export function avatarSrc(url: string | null | undefined): string | null {
  if (!url) return null;
  return url.startsWith('http') ? url : `${API_URL}${url}`;
}
