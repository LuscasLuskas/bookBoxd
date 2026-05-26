import { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  getUserBooks,
  getUserBookStats,
  getUserProfile,
  getUserReviews,
} from '../api/users';
import { getBook } from '../api/books';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import ReviewCard from '../components/ReviewCard';
import { UserBookBadge } from '../components/StatusBadge';
import StarRating from '../components/StarRating';
import { avatarSrc } from '../utils/avatar';
import { getBookGradient } from '../utils/bookCover';
import type { LibraryStats, UserBook, UserBookStatus } from '../types';

const STATS: { status: UserBookStatus; label: string; color: string }[] = [
  { status: 'COMPLETED', label: 'Completed', color: 'text-amber-400' },
  { status: 'READING', label: 'Reading', color: 'text-green-400' },
  { status: 'WISHLIST', label: 'Wishlist', color: 'text-purple-400' },
  { status: 'DROPPED', label: 'Dropped', color: 'text-gray-400' },
];

const FILTERS: { value: UserBookStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'READING', label: 'Reading' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'WISHLIST', label: 'Wishlist' },
  { value: 'ADDED', label: 'Added' },
  { value: 'DROPPED', label: 'Dropped' },
];

const RATEABLE: UserBookStatus[] = ['COMPLETED', 'DROPPED'];

function errStatus(err: unknown): number | undefined {
  const e = err as { response?: { status?: number } };
  return e?.response?.status;
}

function VisitedLibraryRow({ userBook }: { userBook: UserBook }) {
  const { data: book } = useQuery({
    queryKey: ['book', userBook.book_id],
    queryFn: () => getBook(userBook.book_id),
  });
  const [imgError, setImgError] = useState(false);

  const title = book?.title ?? '...';
  const hasCover = !!book?.cover_url && !imgError;
  const canReview = RATEABLE.includes(userBook.status);

  return (
    <div className="card p-3 sm:p-4 flex items-center gap-3 sm:gap-4">
      <Link to={`/books/${userBook.book_id}`} className="shrink-0 w-10 sm:w-12">
        <div className="aspect-[2/3] rounded-sm w-full overflow-hidden">
          {hasCover ? (
            <img
              src={book!.cover_url!}
              alt={title}
              loading="lazy"
              onError={() => setImgError(true)}
              className="w-full h-full object-cover"
            />
          ) : (
            <div
              className="w-full h-full"
              style={{ background: getBookGradient(title) }}
            />
          )}
        </div>
      </Link>
      <div className="flex-1 min-w-0">
        <Link
          to={`/books/${userBook.book_id}`}
          className="text-bb-text hover:text-white font-medium transition-colors truncate block text-sm"
        >
          {title}
        </Link>
        <p className="text-bb-muted text-xs truncate">{book?.author ?? ''}</p>
        {canReview && userBook.rating != null && (
          <div className="mt-1 flex items-center gap-1.5">
            <StarRating value={userBook.rating} readOnly size={15} />
            <span className="text-bb-dim text-[11px] tabular-nums">
              {userBook.rating.toFixed(1)}
            </span>
          </div>
        )}
      </div>
      <UserBookBadge status={userBook.status} />
    </div>
  );
}

export default function UserProfile() {
  const { userId } = useParams<{ userId: string }>();
  const { user: me } = useAuth();
  const navigate = useNavigate();
  const [filter, setFilter] = useState<UserBookStatus | 'all'>('all');

  // Clicking your own name lands here — bounce to the editable own profile.
  if (userId && me && userId === me.id) {
    navigate('/profile', { replace: true });
    return null;
  }

  const profileQ = useQuery({
    queryKey: ['userProfile', userId],
    queryFn: () => getUserProfile(userId!),
    enabled: !!userId,
    retry: false,
  });

  const statsQ = useQuery({
    queryKey: ['userProfile', userId, 'stats'],
    queryFn: () => getUserBookStats(userId!),
    enabled: !!userId && !!profileQ.data,
  });

  const booksQ = useQuery({
    queryKey: ['userProfile', userId, 'books', filter],
    queryFn: () =>
      getUserBooks(userId!, {
        limit: 100,
        status: filter === 'all' ? undefined : filter,
      }),
    enabled: !!userId && !!profileQ.data,
  });

  const reviewsQ = useQuery({
    queryKey: ['userProfile', userId, 'reviews'],
    queryFn: () => getUserReviews(userId!),
    enabled: !!userId && !!profileQ.data,
  });

  if (profileQ.isLoading)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );

  if (profileQ.isError) {
    const code = errStatus(profileQ.error);
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        {code === 403 ? (
          <>
            <p className="text-bb-text font-medium">This profile is private to you.</p>
            <p className="text-bb-muted text-sm mt-2">
              You can only view profiles of people you share an active club with.
            </p>
          </>
        ) : code === 404 ? (
          <p className="text-bb-muted">User not found.</p>
        ) : (
          <p className="text-bb-muted">Could not load this profile.</p>
        )}
        <Link to="/clubs" className="btn-ghost text-sm mt-6 inline-flex">
          Back to clubs
        </Link>
      </div>
    );
  }

  const user = profileQ.data!;
  const stats = statsQ.data;
  const photo = avatarSrc(user.avatar_url);
  const isMaster = user.role === 'MASTER';
  const stat = (s: UserBookStatus): number =>
    stats?.[s.toLowerCase() as keyof LibraryStats] ?? 0;
  const booksRead = stat('COMPLETED');

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Profile header */}
      <div className="card p-6 mb-6">
        <div className="flex items-start gap-5">
          <div className="w-20 h-20 rounded-full overflow-hidden bg-bb-accent/20 border-2 border-bb-accent/40 flex items-center justify-center shrink-0">
            {photo ? (
              <img src={photo} alt={user.name} className="w-full h-full object-cover" />
            ) : (
              <span className="text-bb-accent font-bold text-3xl">
                {user.name.charAt(0).toUpperCase()}
              </span>
            )}
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold text-white truncate">{user.name}</h1>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <span
                className={`text-xs px-2 py-0.5 rounded border font-medium ${
                  isMaster
                    ? 'bg-purple-900/50 text-purple-300 border-purple-700'
                    : 'bg-bb-surface text-bb-muted border-bb-border'
                }`}
              >
                {user.role}
              </span>
              <span className="text-bb-dim text-xs">
                Joined{' '}
                {new Date(user.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                })}
              </span>
            </div>
          </div>
        </div>

        <div className="mt-5 flex items-baseline gap-2">
          <span className="text-3xl font-bold text-amber-400">{booksRead}</span>
          <span className="text-bb-muted text-sm">
            book{booksRead === 1 ? '' : 's'} read
          </span>
        </div>

        <div className="mt-5">
          <h3 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-1.5">
            Bio
          </h3>
          {user.bio ? (
            <p className="text-bb-text text-sm leading-relaxed whitespace-pre-line">
              {user.bio}
            </p>
          ) : (
            <p className="text-bb-dim text-sm italic">No bio.</p>
          )}
        </div>

        <div className="mt-5">
          <h3 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-1.5">
            Favorite Book
          </h3>
          {user.favorite_book ? (
            <Link
              to={`/books/${user.favorite_book.id}`}
              className="flex items-center gap-3 p-2 rounded bg-white/5 hover:bg-bb-surface transition-colors"
            >
              <div className="w-10 h-14 rounded-sm overflow-hidden shrink-0">
                {user.favorite_book.cover_url ? (
                  <img
                    src={user.favorite_book.cover_url}
                    alt={user.favorite_book.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div
                    className="w-full h-full"
                    style={{ background: getBookGradient(user.favorite_book.title) }}
                  />
                )}
              </div>
              <div className="min-w-0">
                <p className="text-bb-text text-sm font-medium truncate">
                  {user.favorite_book.title}
                </p>
                <p className="text-bb-muted text-xs truncate">
                  {user.favorite_book.author}
                </p>
              </div>
            </Link>
          ) : (
            <p className="text-bb-dim text-sm italic">No favorite book picked.</p>
          )}
        </div>
      </div>

      {/* Stats grid */}
      <div className="mb-6">
        <h2 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-3">
          Reading Stats
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STATS.map(({ status, label, color }) => (
            <div key={status} className="card p-4 text-center">
              <p className={`text-2xl font-bold ${color}`}>{stat(status)}</p>
              <p className="text-bb-muted text-xs mt-1">{label}</p>
            </div>
          ))}
        </div>
        <p className="text-bb-dim text-xs mt-3 text-center">
          {stats?.total ?? 0} total books in library
        </p>
      </div>

      {/* Library */}
      <div className="mb-8">
        <h2 className="text-white text-lg font-semibold mb-3">
          {user.name.split(' ')[0]}'s Library
          {booksQ.data && (
            <span className="text-bb-muted text-sm font-normal ml-2">
              ({booksQ.data.total})
            </span>
          )}
        </h2>
        <div className="flex gap-1 mb-4 overflow-x-auto pb-1 scrollbar-none">
          {FILTERS.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className={`px-3 py-1.5 rounded text-sm font-medium whitespace-nowrap transition-colors ${
                filter === value
                  ? 'bg-bb-accent text-black'
                  : 'text-bb-muted hover:text-white hover:bg-bb-surface'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        {booksQ.isLoading ? (
          <div className="py-10">
            <LoadingSpinner />
          </div>
        ) : booksQ.data && booksQ.data.items.length > 0 ? (
          <div className="space-y-2">
            {booksQ.data.items.map((ub) => (
              <VisitedLibraryRow key={ub.id} userBook={ub} />
            ))}
          </div>
        ) : (
          <p className="text-bb-dim text-sm text-center py-8">
            No books in this section.
          </p>
        )}
      </div>

      {/* Reviews */}
      <div>
        <h2 className="text-white text-lg font-semibold mb-3">
          Reviews
          {reviewsQ.data && (
            <span className="text-bb-muted text-sm font-normal ml-2">
              ({reviewsQ.data.total})
            </span>
          )}
        </h2>
        {reviewsQ.isLoading ? (
          <div className="py-10">
            <LoadingSpinner />
          </div>
        ) : reviewsQ.data && reviewsQ.data.items.length > 0 ? (
          <div className="space-y-3">
            {reviewsQ.data.items.map((r) => (
              <ReviewCard key={r.id} review={r} />
            ))}
          </div>
        ) : (
          <p className="text-bb-dim text-sm">No public reviews yet.</p>
        )}
      </div>
    </div>
  );
}
