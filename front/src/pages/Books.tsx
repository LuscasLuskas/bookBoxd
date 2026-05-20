import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listBooks } from '../api/books';
import BookCard from '../components/BookCard';
import AddBookModal from '../components/AddBookModal';
import LoadingSpinner from '../components/LoadingSpinner';

const LIMIT = 20;

export default function Books() {
  const [search, setSearch] = useState({ title: '', author: '' });
  const [debounced, setDebounced] = useState({ title: '', author: '' });
  const [offset, setOffset] = useState(0);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  const { data, isLoading } = useQuery({
    queryKey: ['books', LIMIT, offset, debounced],
    queryFn: () =>
      listBooks({
        limit: LIMIT,
        offset,
        title: debounced.title || undefined,
        author: debounced.author || undefined,
      }),
  });

  const handleSearchChange = (field: 'title' | 'author', value: string) => {
    setSearch((prev) => ({ ...prev, [field]: value }));
    setOffset(0);
  };

  const totalPages = data ? Math.ceil(data.total / LIMIT) : 0;
  const currentPage = Math.floor(offset / LIMIT) + 1;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">Books</h1>
          {data && (
            <p className="text-bb-muted text-sm mt-0.5">
              {data.total.toLocaleString()} books in catalog
            </p>
          )}
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          + Add Book
        </button>
      </div>

      {/* Search */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
        <input
          className="input"
          placeholder="Search by title..."
          value={search.title}
          onChange={(e) => handleSearchChange('title', e.target.value)}
        />
        <input
          className="input"
          placeholder="Search by author..."
          value={search.author}
          onChange={(e) => handleSearchChange('author', e.target.value)}
        />
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="py-20">
          <LoadingSpinner />
        </div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-20 text-bb-muted">
          <p>No books found.</p>
          <button
            onClick={() => setShowCreate(true)}
            className="mt-4 text-bb-accent hover:underline text-sm"
          >
            Add the first one!
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-4">
            {data?.items.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-10">
              <button
                className="btn-ghost"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - LIMIT))}
              >
                ← Prev
              </button>
              <span className="text-bb-muted text-sm">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="btn-ghost"
                disabled={offset + LIMIT >= (data?.total ?? 0)}
                onClick={() => setOffset(offset + LIMIT)}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {showCreate && <AddBookModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
