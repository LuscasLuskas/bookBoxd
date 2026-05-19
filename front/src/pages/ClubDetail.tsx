import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getClub, deleteClub } from '../api/clubs';
import {
  joinClub,
  leaveClub,
  listMembers,
  approveMember,
  rejectMember,
  banMember,
} from '../api/membership';
import { listClubBooks, addBookToClub, removeBookFromClub } from '../api/clubBooks';
import { getBook, listBooks } from '../api/books';
import { useAuth } from '../contexts/AuthContext';
import { MembershipBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import BookCard from '../components/BookCard';
import type { ClubBook } from '../types';

function ClubBookTile({
  clubBook,
  isOwner,
  onRemove,
}: {
  clubBook: ClubBook;
  isOwner: boolean;
  onRemove: (bookId: string) => void;
}) {
  const { data: book } = useQuery({
    queryKey: ['book', clubBook.book_id],
    queryFn: () => getBook(clubBook.book_id),
  });

  if (!book)
    return (
      <div className="aspect-[2/3] rounded animate-pulse bg-bb-surface" />
    );

  return (
    <div className="relative group">
      <BookCard book={book} compact />
      {isOwner && (
        <button
          onClick={(e) => {
            e.preventDefault();
            onRemove(clubBook.book_id);
          }}
          className="absolute top-1 right-1 w-5 h-5 bg-red-700/90 text-white rounded-full text-xs hidden group-hover:flex items-center justify-center leading-none"
          title="Remove"
        >
          ×
        </button>
      )}
    </div>
  );
}

type Tab = 'books' | 'members';

export default function ClubDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>('books');
  const [showAddBook, setShowAddBook] = useState(false);
  const [bookSearch, setBookSearch] = useState('');

  const { data: club, isLoading: loadingClub } = useQuery({
    queryKey: ['club', id],
    queryFn: () => getClub(id!),
    enabled: !!id,
  });

  const { data: membersData } = useQuery({
    queryKey: ['members', id],
    queryFn: () => listMembers(id!),
    enabled: !!id,
  });

  const { data: clubBooksData, isLoading: loadingBooks } = useQuery({
    queryKey: ['clubBooks', id],
    queryFn: () => listClubBooks(id!),
    enabled: !!id,
  });

  const { data: searchResults } = useQuery({
    queryKey: ['books', 10, 0, { title: bookSearch }],
    queryFn: () => listBooks({ limit: 10, title: bookSearch || undefined }),
    enabled: showAddBook,
  });

  const isOwner = club?.owner_id === user?.id;
  const myMembership = membersData?.items.find((m) => m.user_id === user?.id);

  const invalidateMembers = () => qc.invalidateQueries({ queryKey: ['members', id] });
  const invalidateClubBooks = () => qc.invalidateQueries({ queryKey: ['clubBooks', id] });

  const joinMutation = useMutation({
    mutationFn: () => joinClub(id!),
    onSuccess: () => { invalidateMembers(); toast.success('Join request sent!'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const leaveMutation = useMutation({
    mutationFn: () => leaveClub(id!),
    onSuccess: () => { invalidateMembers(); toast.success('Left club'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const addBookMutation = useMutation({
    mutationFn: (bookId: string) => addBookToClub(id!, bookId),
    onSuccess: () => {
      invalidateClubBooks();
      toast.success('Book added!');
      setShowAddBook(false);
      setBookSearch('');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const removeBookMutation = useMutation({
    mutationFn: (bookId: string) => removeBookFromClub(id!, bookId),
    onSuccess: () => { invalidateClubBooks(); toast.success('Book removed'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const approveMutation = useMutation({
    mutationFn: (userId: string) => approveMember(id!, userId),
    onSuccess: () => { invalidateMembers(); toast.success('Member approved!'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (userId: string) => rejectMember(id!, userId),
    onSuccess: () => { invalidateMembers(); toast.success('Member rejected'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const banMutation = useMutation({
    mutationFn: (userId: string) => banMember(id!, userId),
    onSuccess: () => { invalidateMembers(); toast.success('Member banned'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteClub(id!),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clubs'] });
      toast.success('Club deleted');
      navigate('/clubs');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  if (loadingClub)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );
  if (!club)
    return (
      <div className="text-center py-20 text-bb-muted">Club not found</div>
    );

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        to="/clubs"
        className="text-bb-muted text-sm hover:text-white transition-colors inline-flex items-center gap-1 mb-6"
      >
        ← All Clubs
      </Link>

      {/* Club header */}
      <div className="card p-6 mb-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-white">{club.name}</h1>
            {club.description && (
              <p className="text-bb-muted mt-2 leading-relaxed">{club.description}</p>
            )}
            <div className="flex items-center gap-3 mt-3 text-xs text-bb-dim flex-wrap">
              <span>
                Created{' '}
                {new Date(club.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
              {isOwner && (
                <span className="px-1.5 py-0.5 bg-bb-accent/20 text-bb-accent rounded font-medium">
                  You own this club
                </span>
              )}
            </div>
          </div>

          <div className="flex gap-2 flex-wrap shrink-0">
            {!isOwner && (
              <>
                {!myMembership && (
                  <button
                    onClick={() => joinMutation.mutate()}
                    disabled={joinMutation.isPending}
                    className="btn-primary"
                  >
                    Join Club
                  </button>
                )}
                {myMembership?.status === 'PENDING' && (
                  <span className="text-bb-muted text-sm self-center">
                    Request pending…
                  </span>
                )}
                {myMembership?.status === 'ACTIVE' && (
                  <button
                    onClick={() => leaveMutation.mutate()}
                    disabled={leaveMutation.isPending}
                    className="btn-ghost"
                  >
                    Leave Club
                  </button>
                )}
              </>
            )}
            {isOwner && (
              <button
                onClick={() => {
                  if (window.confirm('Delete this club? This cannot be undone.'))
                    deleteMutation.mutate();
                }}
                disabled={deleteMutation.isPending}
                className="btn-danger"
              >
                Delete Club
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0 mb-6 border-b border-bb-border">
        {(['books', 'members'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2.5 text-sm font-medium capitalize transition-colors border-b-2 -mb-px ${
              tab === t
                ? 'border-bb-accent text-bb-accent'
                : 'border-transparent text-bb-muted hover:text-white'
            }`}
          >
            {t}
            {t === 'books' && clubBooksData && ` (${clubBooksData.total})`}
            {t === 'members' && membersData && ` (${membersData.total})`}
          </button>
        ))}
      </div>

      {/* Books tab */}
      {tab === 'books' && (
        <div>
          {isOwner && (
            <div className="mb-5">
              <button
                onClick={() => setShowAddBook(true)}
                className="btn-primary"
              >
                + Add Book
              </button>
            </div>
          )}

          {loadingBooks ? (
            <div className="py-10">
              <LoadingSpinner />
            </div>
          ) : clubBooksData?.items.length === 0 ? (
            <div className="text-center py-20 text-bb-muted">
              No books in this club yet.
              {isOwner && (
                <button
                  onClick={() => setShowAddBook(true)}
                  className="block mx-auto mt-3 text-bb-accent hover:underline text-sm"
                >
                  Add the first book
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-4">
              {clubBooksData?.items.map((cb) => (
                <ClubBookTile
                  key={cb.id}
                  clubBook={cb}
                  isOwner={isOwner}
                  onRemove={(bookId) => removeBookMutation.mutate(bookId)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Members tab */}
      {tab === 'members' && (
        <div className="space-y-2">
          {membersData?.items.map((member) => (
            <div
              key={member.id}
              className="card p-4 flex items-center justify-between gap-4 flex-wrap"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded-full bg-bb-surface border border-bb-border flex items-center justify-center text-bb-muted text-[10px] font-bold shrink-0">
                  {member.user_id.slice(0, 2).toUpperCase()}
                </div>
                <div className="min-w-0">
                  <p className="text-bb-text text-sm font-medium truncate">
                    {member.user_id === user?.id
                      ? user.name + ' (you)'
                      : member.user_id.slice(0, 12) + '…'}
                    {member.user_id === club.owner_id && (
                      <span className="ml-2 text-bb-dim text-xs">(owner)</span>
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0 flex-wrap">
                <MembershipBadge status={member.status} />
                {isOwner &&
                  member.user_id !== user?.id &&
                  member.status === 'PENDING' && (
                    <div className="flex gap-1">
                      <button
                        onClick={() => approveMutation.mutate(member.user_id)}
                        disabled={approveMutation.isPending}
                        className="btn-primary text-xs py-1 px-2"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => rejectMutation.mutate(member.user_id)}
                        disabled={rejectMutation.isPending}
                        className="btn-ghost text-xs py-1 px-2"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                {isOwner &&
                  member.user_id !== user?.id &&
                  member.status === 'ACTIVE' && (
                    <button
                      onClick={() => {
                        if (window.confirm('Ban this member?'))
                          banMutation.mutate(member.user_id);
                      }}
                      disabled={banMutation.isPending}
                      className="btn-danger text-xs py-1 px-2"
                    >
                      Ban
                    </button>
                  )}
              </div>
            </div>
          ))}
          {membersData?.items.length === 0 && (
            <div className="text-center py-16 text-bb-muted">No members yet</div>
          )}
        </div>
      )}

      {/* Add book modal */}
      {showAddBook && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-white font-semibold">Add Book to Club</h2>
              <button
                onClick={() => {
                  setShowAddBook(false);
                  setBookSearch('');
                }}
                className="text-bb-muted hover:text-white text-lg leading-none"
              >
                ×
              </button>
            </div>
            <input
              className="input mb-4"
              placeholder="Search books by title..."
              value={bookSearch}
              onChange={(e) => setBookSearch(e.target.value)}
              autoFocus
            />
            <div className="space-y-1 max-h-72 overflow-y-auto">
              {searchResults?.items.map((book) => {
                const inClub = clubBooksData?.items.some(
                  (cb) => cb.book_id === book.id
                );
                return (
                  <div
                    key={book.id}
                    className="flex items-center justify-between gap-3 p-3 rounded hover:bg-bb-surface transition-colors"
                  >
                    <div className="min-w-0">
                      <p className="text-bb-text text-sm font-medium truncate">
                        {book.title}
                      </p>
                      <p className="text-bb-muted text-xs">{book.author}</p>
                    </div>
                    <button
                      onClick={() => addBookMutation.mutate(book.id)}
                      disabled={inClub || addBookMutation.isPending}
                      className={
                        inClub
                          ? 'text-bb-dim text-xs shrink-0'
                          : 'btn-primary text-xs py-1 px-2 shrink-0'
                      }
                    >
                      {inClub ? 'Added' : '+ Add'}
                    </button>
                  </div>
                );
              })}
              {searchResults?.items.length === 0 && (
                <p className="text-bb-muted text-sm text-center py-6">
                  No books found
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
