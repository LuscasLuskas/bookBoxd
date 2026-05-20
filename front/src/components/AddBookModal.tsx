import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { createBook, searchExternalBooks } from '../api/books';
import type { CreateBookInput } from '../api/books';
import type { Book, ExternalBookResult } from '../types';
import { getBookGradient } from '../utils/bookCover';
import LoadingSpinner from './LoadingSpinner';

interface Props {
  onClose: () => void;
  /** Modal heading. Defaults to "Add Book". */
  heading?: string;
  /** Label for the per-result action button. Defaults to "Add". */
  pickLabel?: string;
  /**
   * Runs after the picked book is in the global catalog — e.g. add it to a
   * club or to the user's library. When omitted, the modal just imports into
   * the catalog (the Books page behavior).
   */
  onPicked?: (book: Book) => Promise<void>;
}

type Tab = 'search' | 'manual';

function errMessage(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } };
  return e?.response?.data?.detail || '';
}

export default function AddBookModal({
  onClose,
  heading = 'Add Book',
  pickLabel = 'Add',
  onPicked,
}: Props) {
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>('search');

  // --- Open Library search ---
  const [query, setQuery] = useState('');
  const [debounced, setDebounced] = useState('');
  const [added, setAdded] = useState<Set<string>>(new Set());
  const [busyId, setBusyId] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), 450);
    return () => clearTimeout(t);
  }, [query]);

  const { data: results, isFetching } = useQuery({
    queryKey: ['external-books', debounced],
    queryFn: () => searchExternalBooks(debounced),
    enabled: debounced.length > 0,
  });

  // --- Manual entry ---
  const [form, setForm] = useState({ title: '', author: '', synopsis: '' });
  const [manualBusy, setManualBusy] = useState(false);

  // Imports the book into the global catalog, then runs the optional hook.
  const importBook = async (input: CreateBookInput): Promise<Book> => {
    const book = await createBook(input);
    qc.invalidateQueries({ queryKey: ['books'] });
    if (onPicked) await onPicked(book);
    return book;
  };

  const handleImport = async (book: ExternalBookResult) => {
    setBusyId(book.external_id);
    try {
      await importBook({
        title: book.title,
        author: book.author,
        cover_url: book.cover_url,
        external_id: book.external_id,
        published_year: book.published_year,
        isbn: book.isbn,
      });
      setAdded((prev) => new Set(prev).add(book.external_id));
      toast.success(`"${book.title}" added!`);
    } catch (err) {
      toast.error(errMessage(err) || 'Failed to add book');
    } finally {
      setBusyId(null);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.author.trim()) return;
    setManualBusy(true);
    try {
      await importBook({
        title: form.title.trim(),
        author: form.author.trim(),
        synopsis: form.synopsis.trim() || undefined,
      });
      toast.success('Book added!');
      onClose();
    } catch (err) {
      toast.error(errMessage(err) || 'Failed to add book');
    } finally {
      setManualBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="card w-full max-w-lg p-6 max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-white font-semibold text-lg">{heading}</h2>
          <button
            onClick={onClose}
            className="text-bb-muted hover:text-white transition-colors text-lg leading-none"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-5 border-b border-white/10">
          <button
            onClick={() => setTab('search')}
            className={`px-3 py-2 text-sm transition-colors border-b-2 -mb-px ${
              tab === 'search'
                ? 'border-bb-accent text-white'
                : 'border-transparent text-bb-muted hover:text-white'
            }`}
          >
            Search Open Library
          </button>
          <button
            onClick={() => setTab('manual')}
            className={`px-3 py-2 text-sm transition-colors border-b-2 -mb-px ${
              tab === 'manual'
                ? 'border-bb-accent text-white'
                : 'border-transparent text-bb-muted hover:text-white'
            }`}
          >
            Manual entry
          </button>
        </div>

        {tab === 'search' ? (
          <div className="flex flex-col min-h-0">
            <input
              className="input"
              placeholder="Search by title, author or ISBN..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />

            <div className="mt-4 overflow-y-auto -mr-2 pr-2 space-y-2">
              {isFetching && (
                <div className="py-8">
                  <LoadingSpinner />
                </div>
              )}

              {!isFetching && debounced && results?.length === 0 && (
                <p className="text-bb-muted text-sm text-center py-8">
                  No results on Open Library for "{debounced}".
                </p>
              )}

              {!isFetching && !debounced && (
                <p className="text-bb-muted text-sm text-center py-8">
                  Start typing to search millions of books from Open Library.
                </p>
              )}

              {!isFetching &&
                results?.map((book) => {
                  const isAdded = added.has(book.external_id);
                  const isBusy = busyId === book.external_id;
                  return (
                    <div
                      key={book.external_id}
                      className="flex items-center gap-3 p-2 rounded bg-white/5"
                    >
                      <div className="w-10 h-14 shrink-0 rounded-sm overflow-hidden">
                        {book.cover_url ? (
                          <img
                            src={book.cover_url}
                            alt=""
                            className="w-full h-full object-cover"
                            loading="lazy"
                          />
                        ) : (
                          <div
                            className="w-full h-full"
                            style={{ background: getBookGradient(book.title) }}
                          />
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-bb-text text-sm font-medium truncate">
                          {book.title}
                        </p>
                        <p className="text-bb-muted text-xs truncate">
                          {book.author}
                          {book.published_year ? ` · ${book.published_year}` : ''}
                        </p>
                      </div>
                      <button
                        onClick={() => handleImport(book)}
                        disabled={isAdded || busyId !== null}
                        className={isAdded ? 'btn-ghost text-xs' : 'btn-primary text-xs'}
                      >
                        {isAdded ? '✓ Added' : isBusy ? '...' : pickLabel}
                      </button>
                    </div>
                  );
                })}
            </div>
          </div>
        ) : (
          <form onSubmit={handleManualSubmit} className="space-y-4">
            <div>
              <label className="label">Title *</label>
              <input
                className="input"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="Book title"
                required
                autoFocus
              />
            </div>
            <div>
              <label className="label">Author *</label>
              <input
                className="input"
                value={form.author}
                onChange={(e) => setForm((f) => ({ ...f, author: e.target.value }))}
                placeholder="Author name"
                required
              />
            </div>
            <div>
              <label className="label">Synopsis</label>
              <textarea
                className="textarea"
                rows={4}
                value={form.synopsis}
                onChange={(e) => setForm((f) => ({ ...f, synopsis: e.target.value }))}
                placeholder="Brief description (optional)"
              />
            </div>
            <div className="flex gap-3 pt-1">
              <button
                type="submit"
                disabled={manualBusy}
                className="btn-primary flex-1"
              >
                {manualBusy ? 'Adding...' : 'Add Book'}
              </button>
              <button type="button" onClick={onClose} className="btn-ghost">
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
