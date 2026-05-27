import api from './client';
import type {
  DailyLogHistory,
  DailyReadingLog,
  PublicReadingStreak,
  ReadingGoal,
  ReadingStreakStats,
} from '../types';

export const getReadingGoal = async (): Promise<ReadingGoal | null> => {
  const res = await api.get<ReadingGoal | null>('/me/reading-goal');
  return res.data;
};

export const upsertReadingGoal = async (
  pages_per_day: number,
  streak_public?: boolean
): Promise<ReadingGoal> => {
  const body: { pages_per_day: number; streak_public?: boolean } = {
    pages_per_day,
  };
  if (streak_public !== undefined) body.streak_public = streak_public;
  const res = await api.put<ReadingGoal>('/me/reading-goal', body);
  return res.data;
};

export const getPublicReadingStreak = async (
  userId: string
): Promise<PublicReadingStreak | null> => {
  try {
    const res = await api.get<PublicReadingStreak>(
      `/users/${userId}/reading-streak`
    );
    return res.data;
  } catch (err: unknown) {
    const e = err as { response?: { status?: number } };
    if (e?.response?.status === 404) return null;
    throw err;
  }
};

export const deleteReadingGoal = async (): Promise<void> => {
  await api.delete('/me/reading-goal');
};

export const logToday = async (
  pages_read: number,
  date?: string
): Promise<DailyReadingLog> => {
  const res = await api.post<DailyReadingLog>('/me/reading-goal/log', {
    pages_read,
    date,
  });
  return res.data;
};

export const getTodayLog = async (): Promise<DailyReadingLog | null> => {
  const res = await api.get<DailyReadingLog | null>('/me/reading-goal/log/today');
  return res.data;
};

export const getReadingStats = async (): Promise<ReadingStreakStats> => {
  const res = await api.get<ReadingStreakStats>('/me/reading-goal/stats');
  return res.data;
};

export const getReadingHistory = async (days = 30): Promise<DailyLogHistory> => {
  const res = await api.get<DailyLogHistory>('/me/reading-goal/history', {
    params: { days },
  });
  return res.data;
};
