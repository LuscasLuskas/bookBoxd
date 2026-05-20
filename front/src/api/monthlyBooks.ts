import api from './client';
import type {
  GoalFrequency,
  MonthlyBook,
  MonthlyBookListResponse,
  ReadingRegister,
  ReadingUnit,
  RegisterListResponse,
} from '../types';

export const listMonthlyBooks = async (
  clubId: string
): Promise<MonthlyBookListResponse> => {
  const res = await api.get<MonthlyBookListResponse>(
    `/clubs/${clubId}/monthly-books`
  );
  return res.data;
};

export const setMonthlyBook = async (
  clubId: string,
  bookId: string
): Promise<MonthlyBook> => {
  const res = await api.post<MonthlyBook>(`/clubs/${clubId}/monthly-books`, {
    book_id: bookId,
  });
  return res.data;
};

export const clearMonthlyBook = async (
  clubId: string,
  monthlyBookId: string
): Promise<void> => {
  await api.delete(`/clubs/${clubId}/monthly-books/${monthlyBookId}`);
};

export const getMyRegister = async (
  clubId: string,
  monthlyBookId: string
): Promise<ReadingRegister> => {
  const res = await api.get<ReadingRegister>(
    `/clubs/${clubId}/monthly-books/${monthlyBookId}/register`
  );
  return res.data;
};

export interface RegisterUpdatePayload {
  unit?: ReadingUnit;
  goal_frequency?: GoalFrequency;
  total_amount?: number;
  current_position?: number;
}

export const updateMyRegister = async (
  clubId: string,
  monthlyBookId: string,
  data: RegisterUpdatePayload
): Promise<ReadingRegister> => {
  const res = await api.patch<ReadingRegister>(
    `/clubs/${clubId}/monthly-books/${monthlyBookId}/register`,
    data
  );
  return res.data;
};

export const listRegisters = async (
  clubId: string,
  monthlyBookId: string
): Promise<RegisterListResponse> => {
  const res = await api.get<RegisterListResponse>(
    `/clubs/${clubId}/monthly-books/${monthlyBookId}/registers`
  );
  return res.data;
};
