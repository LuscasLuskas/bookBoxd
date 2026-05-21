import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listShelves, createShelf, deleteShelf } from '../api/shelves';
import LoadingSpinner from '../components/LoadingSpinner';

function errMessage(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } };
  return e?.response?.data?.detail || 'Error';
}

export default function Shelves() {
  const qc = useQueryClient();
  const [name, setName] = useState('');

  const { data: shelves, isLoading } = useQuery({
    queryKey: ['shelves'],
    queryFn: listShelves,
  });

  const createMutation = useMutation({
    mutationFn: () => createShelf(name.trim()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['shelves'] });
      setName('');
      toast.success('Shelf created');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: (shelfId: string) => deleteShelf(shelfId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['shelves'] });
      toast.success('Shelf deleted');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) createMutation.mutate();
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">My Shelves</h1>
        <p className="text-bb-muted text-sm mt-0.5">
          Custom collections of books
        </p>
      </div>

      {/* Create */}
      <form onSubmit={handleCreate} className="flex gap-2 mb-8">
        <input
          className="input flex-1"
          placeholder="New shelf name (e.g. Favorites)"
          maxLength={100}
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button
          type="submit"
          disabled={createMutation.isPending || !name.trim()}
          className="btn-primary text-sm whitespace-nowrap"
        >
          + New Shelf
        </button>
      </form>

      {isLoading ? (
        <div className="py-20">
          <LoadingSpinner />
        </div>
      ) : shelves && shelves.length > 0 ? (
        <div className="space-y-2">
          {shelves.map((shelf) => (
            <div
              key={shelf.id}
              className="card p-4 flex items-center justify-between gap-3"
            >
              <Link
                to={`/shelves/${shelf.id}`}
                className="flex-1 min-w-0 group"
              >
                <p className="text-bb-text group-hover:text-white font-medium transition-colors truncate">
                  {shelf.name}
                </p>
                <p className="text-bb-muted text-xs">
                  {shelf.book_count}{' '}
                  {shelf.book_count === 1 ? 'book' : 'books'}
                </p>
              </Link>
              <button
                onClick={() => {
                  if (
                    window.confirm(`Delete the shelf "${shelf.name}"?`)
                  )
                    deleteMutation.mutate(shelf.id);
                }}
                disabled={deleteMutation.isPending}
                className="text-bb-dim hover:text-red-400 transition-colors text-lg leading-none shrink-0"
                title="Delete shelf"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-bb-muted">
          <p>No shelves yet.</p>
          <p className="text-bb-dim text-sm mt-1">
            Create one above to start organizing your books.
          </p>
        </div>
      )}
    </div>
  );
}
