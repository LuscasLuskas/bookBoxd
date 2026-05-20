export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'master';
  avatar_url: string | null;
  bio: string | null;
  favorite_book_id: string | null;
  favorite_book: Book | null;
  created_at: string;
}

export interface Book {
  id: string;
  title: string;
  author: string;
  synopsis: string | null;
  cover_url: string | null;
  external_id: string | null;
  published_year: number | null;
  isbn: string | null;
  created_by: string | null;
  created_by_name_snapshot: string | null;
  created_at: string;
}

export interface ExternalBookResult {
  external_id: string;
  title: string;
  author: string;
  cover_url: string | null;
  published_year: number | null;
  isbn: string | null;
}

export interface BookListResponse {
  items: Book[];
  total: number;
  limit: number;
  offset: number;
}

export interface BookClub {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
}

export type MembershipStatus =
  | 'PENDING'
  | 'ACTIVE'
  | 'LEFT'
  | 'REJECTED'
  | 'BANNED'
  | 'KICKED';

export interface Membership {
  id: string;
  user_id: string;
  user_name: string | null;
  user_avatar_url: string | null;
  club_id: string;
  status: MembershipStatus;
  kicked_until: string | null;
  created_at: string;
  updated_at: string;
}

export interface MembershipListResponse {
  items: Membership[];
  total: number;
}

export type UserBookStatus =
  | 'WISHLIST'
  | 'ADDED'
  | 'READING'
  | 'COMPLETED'
  | 'DROPPED';

export interface UserBook {
  id: string;
  user_id: string;
  book_id: string;
  status: UserBookStatus;
  created_at: string;
  updated_at: string;
}

export interface UserBookListResponse {
  items: UserBook[];
  total: number;
  limit: number;
  offset: number;
}

export interface LibraryStats {
  wishlist: number;
  added: number;
  reading: number;
  completed: number;
  dropped: number;
  total: number;
}

export interface ClubBook {
  id: string;
  club_id: string;
  book_id: string;
  added_by: string | null;
  created_at: string;
}

export interface ClubBookListResponse {
  items: ClubBook[];
  total: number;
  limit: number;
  offset: number;
}

export type ReadingUnit = 'PAGE' | 'CHAPTER';
export type GoalFrequency = 'DAILY' | 'WEEKLY';

export interface MonthlyBook {
  id: string;
  club_id: string;
  book_id: string;
  book_title: string;
  book_author: string;
  set_by: string | null;
  start_date: string;
  end_date: string;
  is_active: boolean;
  cycle_days: number;
  days_elapsed: number;
  days_remaining: number;
  member_count: number;
}

export interface MonthlyBookListResponse {
  items: MonthlyBook[];
  total: number;
}

export interface ReadingRegister {
  id: string;
  monthly_book_id: string;
  user_id: string;
  user_name: string;
  unit: ReadingUnit;
  goal_frequency: GoalFrequency;
  total_amount: number | null;
  current_position: number;
  is_configured: boolean;
  amount_remaining: number | null;
  days_remaining: number;
  weeks_remaining: number;
  daily_goal: number | null;
  weekly_goal: number | null;
  current_goal: number | null;
  progress_percent: number;
  expected_position: number | null;
  on_pace: boolean | null;
  is_completed: boolean;
  updated_at: string;
}

export interface RegisterListResponse {
  monthly_book: MonthlyBook;
  items: ReadingRegister[];
  total: number;
}
