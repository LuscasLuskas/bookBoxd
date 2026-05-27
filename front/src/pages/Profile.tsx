import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { getMe, updateMe, uploadAvatar, deleteMe } from '../api/users';
import { getLibraryStats } from '../api/userBooks';
import { listBooks } from '../api/books';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import ReadingGoalCard from '../components/ReadingGoalCard';
import { avatarSrc } from '../utils/avatar';
import { getBookGradient } from '../utils/bookCover';
import type { Book, LibraryStats, UserBookStatus } from '../types';

const STATS: { status: UserBookStatus; label: string; color: string }[] = [
  { status: 'COMPLETED', label: 'Completed', color: 'text-amber-400' },
  { status: 'READING', label: 'Reading', color: 'text-green-400' },
  { status: 'WISHLIST', label: 'Wishlist', color: 'text-purple-400' },
  { status: 'DROPPED', label: 'Dropped', color: 'text-gray-400' },
];

/** Small book cover thumbnail with gradient fallback. */
function BookThumb({ book, className = '' }: { book: Book; className?: string }) {
  const [err, setErr] = useState(false);
  return (
    <div className={`rounded-sm overflow-hidden shrink-0 ${className}`}>
      {book.cover_url && !err ? (
        <img
          src={book.cover_url}
          alt={book.title}
          onError={() => setErr(true)}
          className="w-full h-full object-cover"
        />
      ) : (
        <div
          className="w-full h-full"
          style={{ background: getBookGradient(book.title) }}
        />
      )}
    </div>
  );
}

/** Catalog search used to pick a favorite book while editing. */
function FavoriteBookPicker({
  value,
  onChange,
}: {
  value: Book | null;
  onChange: (book: Book | null) => void;
}) {
  const [query, setQuery] = useState('');
  const [debounced, setDebounced] = useState('');

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), 350);
    return () => clearTimeout(t);
  }, [query]);

  const { data } = useQuery({
    queryKey: ['books', 'fav-picker', debounced],
    queryFn: () => listBooks({ limit: 6, title: debounced || undefined }),
    enabled: debounced.length > 0,
  });

  return (
    <div>
      {value && (
        <div className="flex items-center gap-3 mb-2 p-2 rounded bg-white/5">
          <BookThumb book={value} className="w-8 h-12" />
          <div className="min-w-0 flex-1">
            <p className="text-bb-text text-sm font-medium truncate">{value.title}</p>
            <p className="text-bb-muted text-xs truncate">{value.author}</p>
          </div>
          <button
            type="button"
            onClick={() => onChange(null)}
            className="text-bb-dim hover:text-red-400 text-xs"
          >
            Remove
          </button>
        </div>
      )}
      <input
        className="input"
        placeholder="Search the catalog for your favorite book..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {debounced && (
        <div className="mt-2 space-y-1 max-h-44 overflow-y-auto">
          {data?.items.length === 0 && (
            <p className="text-bb-muted text-xs text-center py-3">No books found.</p>
          )}
          {data?.items.map((book) => (
            <button
              key={book.id}
              type="button"
              onClick={() => {
                onChange(book);
                setQuery('');
                setDebounced('');
              }}
              className="w-full flex items-center gap-3 p-2 rounded hover:bg-bb-surface transition-colors text-left"
            >
              <BookThumb book={book} className="w-7 h-10" />
              <div className="min-w-0">
                <p className="text-bb-text text-sm truncate">{book.title}</p>
                <p className="text-bb-muted text-xs truncate">{book.author}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Profile() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);

  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [bio, setBio] = useState('');
  const [favorite, setFavorite] = useState<Book | null>(null);

  const { data: user, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  });

  const { data: stats } = useQuery({
    queryKey: ['library', 'stats'],
    queryFn: getLibraryStats,
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      updateMe({
        name: name.trim(),
        bio: bio.trim() || null,
        favorite_book_id: favorite?.id ?? null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['me'] });
      toast.success('Profile updated');
      setEditing(false);
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Failed to update profile');
    },
  });

  const avatarMutation = useMutation({
    mutationFn: (file: File) => uploadAvatar(file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['me'] });
      toast.success('Photo updated');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Failed to upload photo');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMe,
    onSuccess: () => {
      toast.success('Account deleted');
      logout();
      navigate('/login');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error deleting account');
    },
  });

  if (isLoading)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );
  if (!user) return null;

  const stat = (s: UserBookStatus): number =>
    stats?.[s.toLowerCase() as keyof LibraryStats] ?? 0;
  const booksRead = stat('COMPLETED');
  const total = stats?.total ?? 0;
  const isMaster = user.role.toUpperCase() === 'MASTER';
  const photo = avatarSrc(user.avatar_url);

  const startEdit = () => {
    setName(user.name);
    setBio(user.bio ?? '');
    setFavorite(user.favorite_book);
    setEditing(true);
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) avatarMutation.mutate(file);
    e.target.value = '';
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Profile card */}
      <div className="card p-6 mb-6">
        <div className="flex items-start gap-5">
          {/* Avatar */}
          <div className="relative shrink-0">
            <div className="w-20 h-20 rounded-full overflow-hidden bg-bb-accent/20 border-2 border-bb-accent/40 flex items-center justify-center">
              {photo ? (
                <img src={photo} alt={user.name} className="w-full h-full object-cover" />
              ) : (
                <span className="text-bb-accent font-bold text-3xl">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <button
              onClick={() => fileRef.current?.click()}
              disabled={avatarMutation.isPending}
              title="Change photo"
              className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-bb-accent text-black flex items-center justify-center text-sm shadow-md hover:brightness-110 transition disabled:opacity-50"
            >
              {avatarMutation.isPending ? '…' : '📷'}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={onFileChange}
              className="hidden"
            />
          </div>

          {/* Identity */}
          <div className="min-w-0 flex-1">
            {editing ? (
              <input
                className="input text-lg font-bold"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                maxLength={255}
              />
            ) : (
              <h1 className="text-2xl font-bold text-white truncate">{user.name}</h1>
            )}
            <p className="text-bb-muted text-sm mt-0.5">{user.email}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <span
                className={`text-xs px-2 py-0.5 rounded border font-medium ${
                  isMaster
                    ? 'bg-purple-900/50 text-purple-300 border-purple-700'
                    : 'bg-bb-surface text-bb-muted border-bb-border'
                }`}
              >
                {user.role.toUpperCase()}
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

          {!editing && (
            <button onClick={startEdit} className="btn-ghost text-sm shrink-0">
              Edit Profile
            </button>
          )}
        </div>

        {/* Books read highlight */}
        <div className="mt-5 flex items-baseline gap-2">
          <span className="text-3xl font-bold text-amber-400">{booksRead}</span>
          <span className="text-bb-muted text-sm">
            book{booksRead === 1 ? '' : 's'} read
          </span>
        </div>

        {/* Bio */}
        <div className="mt-5">
          <h3 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-1.5">
            Bio
          </h3>
          {editing ? (
            <textarea
              className="textarea"
              rows={3}
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Tell other readers a bit about yourself..."
              maxLength={2000}
            />
          ) : user.bio ? (
            <p className="text-bb-text text-sm leading-relaxed whitespace-pre-line">
              {user.bio}
            </p>
          ) : (
            <p className="text-bb-dim text-sm italic">No bio yet.</p>
          )}
        </div>

        {/* Favorite book */}
        <div className="mt-5">
          <h3 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-1.5">
            Favorite Book
          </h3>
          {editing ? (
            <FavoriteBookPicker value={favorite} onChange={setFavorite} />
          ) : user.favorite_book ? (
            <Link
              to={`/books/${user.favorite_book.id}`}
              className="flex items-center gap-3 p-2 rounded bg-white/5 hover:bg-bb-surface transition-colors"
            >
              <BookThumb book={user.favorite_book} className="w-10 h-14" />
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
            <p className="text-bb-dim text-sm italic">No favorite book picked yet.</p>
          )}
        </div>

        {/* Edit actions */}
        {editing && (
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending || !name.trim()}
              className="btn-primary flex-1"
            >
              {saveMutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              onClick={() => setEditing(false)}
              disabled={saveMutation.isPending}
              className="btn-ghost"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Daily reading goal & streak (private) */}
      <ReadingGoalCard />

      {/* Reading stats */}
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
          {total} total books in library
        </p>
      </div>

      {/* Danger zone */}
      <div className="card p-5 border-red-900/40">
        <h3 className="text-red-400 font-medium mb-1">Danger Zone</h3>
        <p className="text-bb-muted text-sm mb-4 leading-relaxed">
          Permanently delete your account and all your data. Clubs you own will be
          transferred or deleted. This cannot be undone.
        </p>
        <button
          onClick={() => {
            if (
              window.confirm(
                'Are you sure? This will permanently delete your account and cannot be undone.'
              )
            )
              deleteMutation.mutate();
          }}
          disabled={deleteMutation.isPending}
          className="btn-danger"
        >
          {deleteMutation.isPending ? 'Deleting…' : 'Delete Account'}
        </button>
      </div>
    </div>
  );
}
