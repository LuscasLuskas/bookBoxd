import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getBook } from '../api/books';
import { listLibrary, addToLibrary, updateBookStatus, removeFromLibrary } from '../api/userBooks';
import { UserBookBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { getBookGradient } from '../utils/bookCover';
import type { UserBookStatus } from '../types';

const STATUS_OPTIONS: { value: UserBookStatus; label: string }[] = [
  { value: 'WISHLIST', label: 'Wishlist' },
  { value: 'ADDED', label: 'Want to Read' },
  { value: 'READING', label: 'Currently Reading' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'DROPPED', label: 'Dropped' },
];

export default function BookDetail() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const [coverError, setCoverError] = useState(false);

  const { data: book, isLoading } = useQuery({
    queryKey: ['book', id],
    queryFn: () => getBook(id!),
    enabled: !!id,
  });

  const { data: library } = useQuery({
    queryKey: ['library'],
    queryFn: () => listLibrary({ limit: 100 }),
  });

  const userBook = library?.items.find((ub) => ub.book_id === id);

  const addMutation = useMutation({
    mutationFn: (status: UserBookStatus) => addToLibrary(id!, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Added to library!');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (status: UserBookStatus) => updateBookStatus(id!, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Status updated!');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const removeMutation = useMutation({
    mutationFn: () => removeFromLibrary(id!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Removed from library');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
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

          {(book.published_year || book.isbn) && (
            <p className="text-bb-muted text-sm mt-2 flex gap-3 flex-wrap">
              {book.published_year && <span>First published {book.published_year}</span>}
              {book.isbn && <span>ISBN {book.isbn}</span>}
            </p>
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
        </div>
      </div>
    </div>
  );
}
