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

/** Profile of someone other than the logged-in user — never includes email. */
export interface PublicUser {
  id: string;
  name: string;
  role: 'USER' | 'MASTER';
  avatar_url: string | null;
  bio: string | null;
  favorite_book_id: string | null;
  favorite_book: Book | null;
  created_at: string;
}

export interface BookTag {
  id: string;
  name: string;
  added_by: string | null;
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
  /** Average of all users' star ratings (null when nobody has rated it). */
  avg_rating: number | null;
  ratings_count: number;
  genres: string[];
  /** Community tags — only populated on the single-book detail endpoint. */
  tags?: BookTag[];
}

export interface Genre {
  id: string;
  name: string;
}

export interface Shelf {
  id: string;
  user_id: string;
  name: string;
  book_count: number;
  created_at: string;
}

export interface ShelfDetail extends Shelf {
  books: Book[];
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
  /** Caller's review rating, 0.5–5.0 in half steps. null = unreviewed. */
  rating: number | null;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: string;
  /** Null when the review was soft-deleted (excluded). */
  user_id: string | null;
  user_name: string | null;
  user_avatar_url: string | null;
  book_id: string;
  /** Populated when the review is listed on a user's profile (so we can show the book). */
  book_title?: string | null;
  book_cover_url?: string | null;
  /** Null when the review was soft-deleted. */
  rating: number | null;
  body: string | null;
  is_public: boolean;
  is_deleted: boolean;
  is_edited: boolean;
  likes_count: number;
  liked_by_me: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReviewListResponse {
  items: Review[];
  total: number;
}

export interface ReviewLikeResult {
  review_id: string;
  liked: boolean;
  likes_count: number;
}

export interface ForumThread {
  id: string;
  club_id: string;
  book_id: string | null;
  book_title: string | null;
  book_cover_url: string | null;
  title: string;
  is_pinned: boolean;
  auto_created: boolean;
  created_by: string | null;
  created_by_name: string | null;
  posts_count: number;
  created_at: string;
}

export interface ForumPost {
  id: string;
  thread_id: string;
  /** Null when the post was soft-deleted (excluded). */
  user_id: string | null;
  user_name: string | null;
  user_avatar_url: string | null;
  body: string;
  is_deleted: boolean;
  is_edited: boolean;
  created_at: string;
}

export interface ForumThreadDetail extends ForumThread {
  posts: ForumPost[];
}

export interface ForumThreadListResponse {
  items: ForumThread[];
  total: number;
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

export interface ReadingGoal {
  id: string;
  user_id: string;
  pages_per_day: number;
  streak_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface PublicReadingStreak {
  user_id: string;
  pages_per_day: number;
  current_streak: number;
  longest_streak: number;
  total_days_met: number;
}

export interface DailyReadingLog {
  id: string;
  user_id: string;
  date: string;
  pages_read: number;
  goal_target: number;
  goal_met: boolean;
  updated_at: string;
}

export interface ReadingStreakStats {
  current_streak: number;
  longest_streak: number;
  total_days_met: number;
  today_logged: boolean;
  today_goal_met: boolean;
  today_pages_read: number;
  today_goal_target: number | null;
}

export interface DailyLogHistory {
  items: DailyReadingLog[];
}
