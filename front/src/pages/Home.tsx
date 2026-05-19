import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listBooks } from '../api/books';
import { listClubs } from '../api/clubs';
import { useAuth } from '../contexts/AuthContext';
import BookCard from '../components/BookCard';
import ClubCard from '../components/ClubCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Home() {
  const { user } = useAuth();

  const { data: booksData, isLoading: loadingBooks } = useQuery({
    queryKey: ['books', 10, 0, {}],
    queryFn: () => listBooks({ limit: 10 }),
  });

  const { data: clubs, isLoading: loadingClubs } = useQuery({
    queryKey: ['clubs'],
    queryFn: listClubs,
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero */}
      <div className="relative rounded-xl overflow-hidden mb-12 border border-bb-border bg-gradient-to-br from-bb-card via-bb-surface to-bb-dark">
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage:
              'repeating-linear-gradient(45deg, #e8a000 0, #e8a000 1px, transparent 0, transparent 50%)',
            backgroundSize: '12px 12px',
          }}
        />
        <div className="relative px-8 py-10">
          <p className="text-bb-muted text-xs font-semibold uppercase tracking-widest mb-1">
            Welcome back
          </p>
          <h1 className="text-3xl font-bold text-white">
            {user?.name ?? 'Reader'}
          </h1>
          <p className="text-bb-muted mt-2 max-w-md leading-relaxed">
            Track your reading journey, discover new books, and connect with fellow readers in book clubs.
          </p>
          <div className="flex gap-3 mt-6 flex-wrap">
            <Link to="/books" className="btn-primary">
              Explore Books
            </Link>
            <Link to="/library" className="btn-ghost">
              My Library
            </Link>
          </div>
        </div>
      </div>

      {/* Recent books */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-white font-semibold">Recent Books</h2>
          <Link
            to="/books"
            className="text-bb-muted text-sm hover:text-white transition-colors"
          >
            Browse all →
          </Link>
        </div>

        {loadingBooks ? (
          <div className="py-12">
            <LoadingSpinner />
          </div>
        ) : booksData?.items.length === 0 ? (
          <div className="text-center py-16 text-bb-muted">
            No books yet.{' '}
            <Link to="/books" className="text-bb-accent hover:underline">
              Add the first one!
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-3">
            {booksData?.items.map((book) => (
              <BookCard key={book.id} book={book} compact />
            ))}
          </div>
        )}
      </section>

      {/* Clubs */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-white font-semibold">Book Clubs</h2>
          <Link
            to="/clubs"
            className="text-bb-muted text-sm hover:text-white transition-colors"
          >
            All clubs →
          </Link>
        </div>

        {loadingClubs ? (
          <div className="py-12">
            <LoadingSpinner />
          </div>
        ) : clubs?.length === 0 ? (
          <div className="text-center py-16 text-bb-muted">
            No clubs yet.{' '}
            <Link to="/clubs" className="text-bb-accent hover:underline">
              Create one!
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {clubs?.slice(0, 6).map((club) => (
              <ClubCard key={club.id} club={club} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
