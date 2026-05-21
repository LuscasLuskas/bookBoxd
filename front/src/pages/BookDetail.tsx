import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getBook } from '../api/books';
import {
  listLibrary,
  addToLibrary,
  updateBookStatus,
  removeFromLibrary,
  rateBook,
} from '../api/userBooks';
import { addTag, removeTag } from '../api/tags';
import { listShelves, addBookToShelf } from '../api/shelves';
import { UserBookBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import StarRating from '../components/StarRating';
import { getBookGradient } from '../utils/bookCover';
import { useAuth } from '../contexts/AuthContext';
import type { UserBookStatus } from '../types';

const STATUS_OPTIONS: { value: UserBookStatus; label: string }[] = [
  { value: 'WISHLIST', label: 'Wishlist' },
  { value: 'ADDED', label: 'Want to Read' },
  { value: 'READING', label: 'Currently Reading' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'DROPPED', label: 'Dropped' },
];

function errMessage(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } };
  return e?.response?.data?.detail || 'Error';
}

export default function BookDetail() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const { user } = useAuth();
  const [coverError, setCoverError] = useState(false);
  const [tagInput, setTagInput] = useState('');

  const { data: book, isLoading } = useQuery({
    queryKey: ['book', id],
    queryFn: () => getBook(id!),
    enabled: !!id,
  });

  const { data: library } = useQuery({
    queryKey: ['library'],
    queryFn: () => listLibrary({ limit: 100 }),
  });

  const { data: shelves } = useQuery({
    queryKey: ['shelves'],
    queryFn: listShelves,
  });

  const userBook = library?.items.find((ub) => ub.book_id === id);

  const invalidateBook = () => {
    qc.invalidateQueries({ queryKey: ['library'] });
    qc.invalidateQueries({ queryKey: ['book', id] });
  };

  const addMutation = useMutation({
    mutationFn: (status: UserBookStatus) => addToLibrary(id!, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Added to library!');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const updateMutation = useMutation({
    mutationFn: (status: UserBookStatus) => updateBookStatus(id!, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Status updated!');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const removeMutation = useMutation({
    mutationFn: () => removeFromLibrary(id!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Removed from library');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const rateMutation = useMutation({
    mutationFn: (rating: number | null) => rateBook(id!, rating),
    onSuccess: invalidateBook,
    onError: (err) => toast.error(errMessage(err)),
  });

  const addTagMutation = useMutation({
    mutationFn: (name: string) => addTag(id!, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['book', id] });
      setTagInput('');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const removeTagMutation = useMutation({
    mutationFn: (tagId: string) => removeTag(id!, tagId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['book', id] }),
    onError: (err) => toast.error(errMessage(err)),
  });

  const addToShelfMutation = useMutation({
    mutationFn: (shelfId: string) => addBookToShelf(shelfId, id!),
    onSuccess: (shelf) => {
      qc.invalidateQueries({ queryKey: ['shelves'] });
      qc.invalidateQueries({ queryKey: ['shelf', shelf.id] });
      toast.success(`Added to "${shelf.name}"`);
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  if (isLoading)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );
  if (!book)
    return (
      <div className="text-center py-20 text-bb-muted">Book not found</div>
    );

  const handleAddTag = (e: React.FormEvent) => {
    e.preventDefault();
    const name = tagInput.trim();
    if (name) addTagMutation.mutate(name);
  };

  const canRemoveTag = (addedBy: string | null) =>
    user != null && (addedBy === user.id || user.role === 'MASTER');

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        to="/books"
        className="text-bb-muted text-sm hover:text-white transition-colors inline-flex items-center gap-1 mb-8"
      >
        ← Back to Books
      </Link>

      <div className="flex gap-8 flex-col sm:flex-row">
        {/* Cover */}
        <div className="shrink-0 w-40 sm:w-52">
          <div className="aspect-[2/3] rounded w-full relative overflow-hidden shadow-2xl">
            {book.cover_url && !coverError ? (
              <img
                src={book.cover_url}
                alt={book.title}
                onError={() => setCoverError(true)}
                className="absolute inset-0 w-full h-full object-cover"
              />
            ) : (
              <>
                <div
                  className="absolute inset-0"
                  style={{ background: getBookGradient(book.title) }}
                />
                <div className="absolute left-0 top-0 bottom-0 w-2 bg-black/30" />
                <div className="absolute inset-0 flex flex-col justify-end p-4 bg-gradient-to-t from-black/70 via-transparent to-transparent">
                  <p className="text-white text-sm font-bold leading-tight">{book.title}</p>
                  <p className="text-white/50 text-xs mt-1">{book.author}</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h1 className="text-3xl font-bold text-white leading-tight">{book.title}</h1>
          <p className="text-bb-accent text-lg mt-1 font-medium">{book.author}</p>

          {/* Average rating */}
          {book.avg_rating != null ? (
            <div className="flex items-center gap-2 mt-2">
              <StarRating value={book.avg_rating} readOnly size={18} />
              <span className="text-bb-text text-sm font-semibold tabular-nums">
                {book.avg_rating.toFixed(2)}
              </span>
              <span className="text-bb-dim text-xs">
                ({book.ratings_count}{' '}
                {book.ratings_count === 1 ? 'rating' : 'ratings'})
              </span>
            </div>
          ) : (
            <p className="text-bb-dim text-xs mt-2">Not rated yet</p>
          )}

          {(book.published_year || book.isbn) && (
            <p className="text-bb-muted text-sm mt-2 flex gap-3 flex-wrap">
              {book.published_year && <span>First published {book.published_year}</span>}
              {book.isbn && <span>ISBN {book.isbn}</span>}
            </p>
          )}

          {/* Genres */}
          {book.genres.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {book.genres.map((g) => (
                <span
                  key={g}
                  className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-bb-accent/10 text-bb-accent border border-bb-accent/25"
                >
                  {g}
                </span>
              ))}
            </div>
          )}

          {book.synopsis && (
            <p className="text-bb-muted mt-4 leading-relaxed text-sm max-w-prose">
              {book.synopsis}
            </p>
          )}

          <p className="mt-3 text-bb-dim text-xs">
            Added by{' '}
            <span className="text-bb-muted">
              {book.created_by_name_snapshot ?? 'Unknown'}
            </span>{' '}
            · {new Date(book.created_at).toLocaleDateString()}
          </p>

          {/* Library actions */}
          <div className="mt-8">
            {userBook ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-bb-muted text-sm">In your library:</span>
                  <UserBookBadge status={userBook.status} />
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <select
                    className="input w-auto text-sm"
                    value={userBook.status}
                    onChange={(e) =>
                      updateMutation.mutate(e.target.value as UserBookStatus)
                    }
                    disabled={updateMutation.isPending}
                  >
                    {STATUS_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                  </select>
                  <button
                    onClick={() => removeMutation.mutate()}
                    disabled={removeMutation.isPending}
                    className="btn-danger text-xs py-1.5"
                  >
                    Remove
                  </button>
                </div>
                {(userBook.status === 'COMPLETED' ||
                  userBook.status === 'DROPPED') && (
                  <div className="flex items-center gap-3 flex-wrap pt-1">
                    <span className="text-bb-muted text-sm">Your rating:</span>
                    <StarRating
                      value={userBook.rating}
                      onChange={(r) => rateMutation.mutate(r)}
                      disabled={rateMutation.isPending}
                      size={24}
                    />
                    <span className="text-bb-muted text-sm tabular-nums">
                      {userBook.rating != null
                        ? userBook.rating.toFixed(1)
                        : 'Not rated'}
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <p className="text-bb-muted text-sm mb-2">Add to your library:</p>
                <div className="flex flex-wrap gap-2">
                  {STATUS_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => addMutation.mutate(opt.value)}
                      disabled={addMutation.isPending}
                      className="btn-ghost text-xs"
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Add to shelf */}
          <div className="mt-6">
            <span className="text-bb-muted text-sm mr-2">Add to shelf:</span>
            {shelves && shelves.length > 0 ? (
              <select
                className="input w-auto text-sm"
                value=""
                disabled={addToShelfMutation.isPending}
                onChange={(e) => {
                  if (e.target.value) addToShelfMutation.mutate(e.target.value);
                }}
              >
                <option value="">Choose a shelf…</option>
                {shelves.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            ) : (
              <Link to="/shelves" className="text-bb-accent text-sm hover:underline">
                Create a shelf first
              </Link>
            )}
          </div>

          {/* Community tags */}
          <div className="mt-8">
            <h3 className="text-white text-sm font-semibold mb-2">
              Community Tags
            </h3>
            <div className="flex flex-wrap gap-1.5 items-center">
              {book.tags && book.tags.length > 0 ? (
                book.tags.map((t) => (
                  <span
                    key={t.id}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-bb-surface text-bb-text border border-bb-border"
                  >
                    {t.name}
                    {canRemoveTag(t.added_by) && (
                      <button
                        onClick={() => removeTagMutation.mutate(t.id)}
                        disabled={removeTagMutation.isPending}
                        className="text-bb-dim hover:text-red-400 transition-colors leading-none"
                        title="Remove tag"
                      >
                        ×
                      </button>
                    )}
                  </span>
                ))
              ) : (
                <span className="text-bb-dim text-xs">No tags yet.</span>
              )}
            </div>
            <form onSubmit={handleAddTag} className="flex gap-2 mt-3 max-w-xs">
              <input
                className="input text-sm"
                placeholder="Add a tag…"
                maxLength={50}
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
              />
              <button
                type="submit"
                disabled={addTagMutation.isPending || !tagInput.trim()}
                className="btn-ghost text-xs"
              >
                Add
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
