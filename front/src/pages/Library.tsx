import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listLibrary, updateBookStatus, removeFromLibrary } from '../api/userBooks';
import { getBook } from '../api/books';
import { UserBookBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { getBookGradient } from '../utils/bookCover';
import type { UserBook, UserBookStatus } from '../types';

const FILTERS: { value: UserBookStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'READING', label: 'Reading' },
  { value: 'WISHLIST', label: 'Wishlist' },
  { value: 'ADDED', label: 'Added' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'DROPPED', label: 'Dropped' },
];

function LibraryRow({ userBook }: { userBook: UserBook }) {
  const qc = useQueryClient();

  const { data: book } = useQuery({
    queryKey: ['book', userBook.book_id],
    queryFn: () => getBook(userBook.book_id),
  });

  const updateMutation = useMutation({
    mutationFn: (status: UserBookStatus) =>
      updateBookStatus(userBook.book_id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Status updated');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const removeMutation = useMutation({
    mutationFn: () => removeFromLibrary(userBook.book_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['library'] });
      toast.success('Removed');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const title = book?.title ?? '...';
  const gradient = getBookGradient(title);

  return (
    <div className="card p-3 sm:p-4 flex items-center gap-3 sm:gap-4">
      <Link to={`/books/${userBook.book_id}`} className="shrink-0 w-10 sm:w-12">
        <div
          className="aspect-[2/3] rounded-sm w-full"
          style={{ background: gradient }}
        />
      </Link>
      <div className="flex-1 min-w-0">
        <Link
          to={`/books/${userBook.book_id}`}
          className="text-bb-text hover:text-white font-medium transition-colors truncate block text-sm"
        >
          {title}
        </Link>
        <p className="text-bb-muted text-xs truncate">{book?.author ?? ''}</p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span className="hidden sm:block">
          <UserBookBadge status={userBook.status} />
        </span>
        <select
          className="input w-auto text-xs py-1 px-2"
          value={userBook.status}
          onChange={(e) => updateMutation.mutate(e.target.value as UserBookStatus)}
          disabled={updateMutation.isPending}
        >
          <option value="WISHLIST">Wishlist</option>
          <option value="ADDED">Added</option>
          <option value="READING">Reading</option>
          <option value="COMPLETED">Completed</option>
          <option value="DROPPED">Dropped</option>
        </select>
        <button
          onClick={() => removeMutation.mutate()}
          disabled={removeMutation.isPending}
          className="text-bb-dim hover:text-red-400 transition-colors text-base leading-none"
          title="Remove"
        >
          ×
        </button>
      </div>
    </div>
  );
}

export default function Library() {
  const [filter, setFilter] = useState<UserBookStatus | 'all'>('all');

  const { data, isLoading } = useQuery({
    queryKey: ['library', filter],
    queryFn: () =>
      listLibrary({
        limit: 100,
        status: filter === 'all' ? undefined : filter,
      }),
  });

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">My Library</h1>
          {data && (
            <p className="text-bb-muted text-sm mt-0.5">{data.total} books</p>
          )}
        </div>
        <Link to="/books" className="btn-ghost text-sm">
          + Browse Books
        </Link>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 mb-6 overflow-x-auto pb-1 scrollbar-none">
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

      {isLoading ? (
        <div className="py-20">
          <LoadingSpinner />
        </div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-bb-muted">No books here yet.</p>
          <Link to="/books" className="btn-primary inline-flex mt-4">
            Browse Catalog
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {data?.items.map((ub) => (
            <LibraryRow key={ub.id} userBook={ub} />
          ))}
        </div>
      )}
    </div>
  );
}
