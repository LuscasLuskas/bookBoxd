import { Link } from 'react-router-dom';
import StarRating from './StarRating';
import { avatarSrc } from '../utils/avatar';
import { getBookGradient } from '../utils/bookCover';
import { useAuth } from '../contexts/AuthContext';
import type { Review } from '../types';

interface Props {
  review: Review;
  /** Omit for deleted reviews — they're not interactive. */
  onLike?: () => void;
  liking?: boolean;
}

export default function ReviewCard({ review, onLike, liking }: Props) {
  const { user: me } = useAuth();

  if (review.is_deleted) {
    return (
      <div className="card p-4 opacity-60">
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-full bg-bb-surface border border-bb-border shrink-0" />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-bb-dim text-sm italic">No name</span>
              <span className="text-bb-dim text-xs">
                {new Date(review.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-bb-dim text-sm mt-2 italic">[excluded comment]</p>
          </div>
        </div>
      </div>
    );
  }

  const initial = (review.user_name ?? '?').charAt(0).toUpperCase();
  // Self → editable own profile; others → public view. Placeholder reviews
  // (no user_id) don't link anywhere.
  const profileHref = review.user_id
    ? me && me.id === review.user_id
      ? '/profile'
      : `/users/${review.user_id}`
    : null;

  const avatarBox = (
    <div className="w-9 h-9 rounded-full overflow-hidden bg-bb-surface border border-bb-border flex items-center justify-center text-bb-muted text-xs font-bold shrink-0">
      {avatarSrc(review.user_avatar_url) ? (
        <img
          src={avatarSrc(review.user_avatar_url)!}
          alt=""
          className="w-full h-full object-cover"
        />
      ) : (
        initial
      )}
    </div>
  );

  return (
    <div className="card p-4">
      {/* Book strip — only present on profile review lists (book_title set). */}
      {review.book_title && (
        <Link
          to={`/books/${review.book_id}`}
          className="flex items-center gap-2 mb-3 p-2 rounded bg-white/5 hover:bg-bb-surface transition-colors"
        >
          <div className="w-6 h-9 rounded-sm overflow-hidden shrink-0">
            {review.book_cover_url ? (
              <img
                src={review.book_cover_url}
                alt={review.book_title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div
                className="w-full h-full"
                style={{ background: getBookGradient(review.book_title) }}
              />
            )}
          </div>
          <span className="text-bb-text text-xs font-medium truncate">
            {review.book_title}
          </span>
        </Link>
      )}
      <div className="flex items-start gap-3">
        {profileHref ? (
          <Link to={profileHref} className="shrink-0">
            {avatarBox}
          </Link>
        ) : (
          avatarBox
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            {profileHref ? (
              <Link
                to={profileHref}
                className="text-bb-text text-sm font-medium hover:text-white transition-colors"
              >
                {review.user_name ?? 'Unknown'}
              </Link>
            ) : (
              <span className="text-bb-text text-sm font-medium">
                {review.user_name ?? 'Unknown'}
              </span>
            )}
            {review.rating != null && (
              <StarRating value={review.rating} readOnly size={14} />
            )}
            <span className="text-bb-dim text-xs">
              {new Date(review.created_at).toLocaleDateString()}
            </span>
            {review.is_edited && (
              <span className="text-bb-dim text-xs italic">(edited)</span>
            )}
          </div>
          {review.body && (
            <p className="text-bb-muted text-sm mt-2 whitespace-pre-wrap leading-relaxed">
              {review.body}
            </p>
          )}
          {onLike && (
            <div className="mt-3">
              <button
                onClick={onLike}
                disabled={liking}
                className={`inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded border transition-colors ${
                  review.liked_by_me
                    ? 'border-bb-accent/40 bg-bb-accent/10 text-bb-accent'
                    : 'border-bb-border text-bb-muted hover:text-white'
                }`}
              >
                <span aria-hidden>{review.liked_by_me ? '♥' : '♡'}</span>
                <span className="tabular-nums">{review.likes_count}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
