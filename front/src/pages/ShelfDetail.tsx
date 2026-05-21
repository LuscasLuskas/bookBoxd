import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getShelf, removeBookFromShelf } from '../api/shelves';
import BookCard from '../components/BookCard';
import LoadingSpinner from '../components/LoadingSpinner';

function errMessage(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } };
  return e?.response?.data?.detail || 'Error';
}

export default function ShelfDetail() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();

  const { data: shelf, isLoading } = useQuery({
    queryKey: ['shelf', id],
    queryFn: () => getShelf(id!),
    enabled: !!id,
  });

  const removeMutation = useMutation({
    mutationFn: (bookId: string) => removeBookFromShelf(id!, bookId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['shelf', id] });
      qc.invalidateQueries({ queryKey: ['shelves'] });
      toast.success('Removed from shelf');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  if (isLoading)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );
  if (!shelf)
    return (
      <div className="text-center py-20 text-bb-muted">Shelf not found</div>
    );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        to="/shelves"
        className="text-bb-muted text-sm hover:text-white transition-colors inline-flex items-center gap-1 mb-6"
      >
        ← Back to Shelves
      </Link>

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">{shelf.name}</h1>
        <p className="text-bb-muted text-sm mt-0.5">
          {shelf.book_count} {shelf.book_count === 1 ? 'book' : 'books'}
        </p>
      </div>

      {shelf.books.length === 0 ? (
        <div className="text-center py-20 text-bb-muted">
          <p>This shelf is empty.</p>
          <Link to="/books" className="btn-primary inline-flex mt-4">
            Browse Books
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-4">
          {shelf.books.map((book) => (
            <div key={book.id} className="relative">
              <BookCard book={book} />
              <button
                onClick={() => removeMutation.mutate(book.id)}
                disabled={removeMutation.isPending}
                className="absolute top-1 right-1 z-10 w-6 h-6 rounded-full bg-black/70 text-white text-sm leading-none flex items-center justify-center hover:bg-red-600 transition-colors"
                title="Remove from shelf"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
