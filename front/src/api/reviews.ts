import api from './client';
import type { Review, ReviewLikeResult, ReviewListResponse } from '../types';

export interface ReviewUpsertBody {
  book_id: string;
  rating: number;
  body?: string | null;
  is_public: boolean;
}

export const upsertReview = async (body: ReviewUpsertBody): Promise<Review> => {
  const res = await api.post<Review>('/me/reviews', body);
  return res.data;
};

export const getMyReview = async (bookId: string): Promise<Review | null> => {
  try {
    const res = await api.get<Review>(`/me/reviews/${bookId}`);
    return res.data;
  } catch (err: unknown) {
    const e = err as { response?: { status?: number } };
    if (e?.response?.status === 404) return null;
    throw err;
  }
};

export const deleteMyReview = async (bookId: string): Promise<void> => {
  await api.delete(`/me/reviews/${bookId}`);
};

export const listBookReviews = async (
  bookId: string
): Promise<ReviewListResponse> => {
  const res = await api.get<ReviewListResponse>(`/books/${bookId}/reviews`);
  return res.data;
};

export const toggleReviewLike = async (
  reviewId: string
): Promise<ReviewLikeResult> => {
  const res = await api.post<ReviewLikeResult>(`/reviews/${reviewId}/like`);
  return res.data;
};
