import api from './client';
import type {
  ForumPost,
  ForumThread,
  ForumThreadDetail,
  ForumThreadListResponse,
} from '../types';

export const listThreads = async (
  clubId: string
): Promise<ForumThreadListResponse> => {
  const res = await api.get<ForumThreadListResponse>(
    `/clubs/${clubId}/forum/threads`
  );
  return res.data;
};

export const getThread = async (
  clubId: string,
  threadId: string
): Promise<ForumThreadDetail> => {
  const res = await api.get<ForumThreadDetail>(
    `/clubs/${clubId}/forum/threads/${threadId}`
  );
  return res.data;
};

export const createThread = async (
  clubId: string,
  body: { title: string; book_id?: string | null }
): Promise<ForumThread> => {
  const res = await api.post<ForumThread>(
    `/clubs/${clubId}/forum/threads`,
    body
  );
  return res.data;
};

export const deleteThread = async (
  clubId: string,
  threadId: string
): Promise<void> => {
  await api.delete(`/clubs/${clubId}/forum/threads/${threadId}`);
};

export const createPost = async (
  clubId: string,
  threadId: string,
  body: string
): Promise<ForumPost> => {
  const res = await api.post<ForumPost>(
    `/clubs/${clubId}/forum/threads/${threadId}/posts`,
    { body }
  );
  return res.data;
};

export const updatePost = async (
  clubId: string,
  threadId: string,
  postId: string,
  body: string
): Promise<ForumPost> => {
  const res = await api.patch<ForumPost>(
    `/clubs/${clubId}/forum/threads/${threadId}/posts/${postId}`,
    { body }
  );
  return res.data;
};

export const deletePost = async (
  clubId: string,
  threadId: string,
  postId: string
): Promise<void> => {
  await api.delete(
    `/clubs/${clubId}/forum/threads/${threadId}/posts/${postId}`
  );
};
