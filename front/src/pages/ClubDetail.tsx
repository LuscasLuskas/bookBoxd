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
import { listMonthlyBooks, setMonthlyBook } from '../api/monthlyBooks';
import { useAuth } from '../contexts/AuthContext';
import { MembershipBadge } from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import BookCard from '../components/BookCard';
import MonthlyBookCard from '../components/MonthlyBookCard';
import AddBookModal from '../components/AddBookModal';
import { avatarSrc } from '../utils/avatar';
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

type Tab = 'books' | 'members' | 'reading';

export default function ClubDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>('books');
  const [showAddBook, setShowAddBook] = useState(false);
  const [showSetBook, setShowSetBook] = useState(false);
  const [mbSearch, setMbSearch] = useState('');

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

  const isOwner = club?.owner_id === user?.id;
  const myMembership = membersData?.items.find((m) => m.user_id === user?.id);
  const isMember = isOwner || myMembership?.status === 'ACTIVE';

  const { data: monthlyBooksData } = useQuery({
    queryKey: ['monthlyBooks', id],
    queryFn: () => listMonthlyBooks(id!),
    enabled: !!id && isMember,
  });

  const { data: mbSearchResults } = useQuery({
    queryKey: ['books', 10, 0, { title: mbSearch, ctx: 'monthly' }],
    queryFn: () => listBooks({ limit: 10, title: mbSearch || undefined }),
    enabled: showSetBook,
  });

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

  const removeBookMutation = useMutation({
    mutationFn: (bookId: string) => removeBookFromClub(id!, bookId),
    onSuccess: () => { invalidateClubBooks(); toast.success('Book removed'); },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error');
    },
  });

  const setMonthlyBookMutation = useMutation({
    mutationFn: (bookId: string) => setMonthlyBook(id!, bookId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['monthlyBooks', id] });
      toast.success('Monthly book set!');
      setShowSetBook(false);
      setMbSearch('');
    },
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
            {isMember && (
              <Link to={`/clubs/${id}/forum`} className="btn-ghost">
                Open Forum
              </Link>
            )}
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
        {(['books', 'members', 'reading'] as Tab[]).map((t) => (
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
            {t === 'reading' && monthlyBooksData && ` (${monthlyBooksData.total})`}
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
              <Link
                to={
                  member.user_id === user?.id
                    ? '/profile'
                    : `/users/${member.user_id}`
                }
                className="flex items-center gap-3 min-w-0 group"
              >
                <div className="w-8 h-8 rounded-full overflow-hidden bg-bb-surface border border-bb-border flex items-center justify-center text-bb-muted text-[10px] font-bold shrink-0">
                  {avatarSrc(member.user_avatar_url) ? (
                    <img
                      src={avatarSrc(member.user_avatar_url)!}
                      alt=""
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    (member.user_name ?? '?').charAt(0).toUpperCase()
                  )}
                </div>
                <div className="min-w-0">
                  <p className="text-bb-text text-sm font-medium truncate group-hover:text-white transition-colors">
                    {member.user_name ?? 'Unknown user'}
                    {member.user_id === user?.id && ' (you)'}
                    {member.user_id === club.owner_id && (
                      <span className="ml-2 text-bb-dim text-xs">(owner)</span>
                    )}
                  </p>
                </div>
              </Link>
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

      {/* Reading tab */}
      {tab === 'reading' && (
        <div>
          {!isMember ? (
            <div className="text-center py-20 text-bb-muted">
              Join the club to see and join its reading challenges.
            </div>
          ) : (
            <>
              {isOwner && (
                <div className="mb-5">
                  <button
                    onClick={() => setShowSetBook(true)}
                    className="btn-primary"
                  >
                    + Set Monthly Book
                  </button>
                </div>
              )}
              {monthlyBooksData?.items.length === 0 ? (
                <div className="text-center py-20 text-bb-muted">
                  No monthly book set yet.
                  {isOwner && (
                    <button
                      onClick={() => setShowSetBook(true)}
                      className="block mx-auto mt-3 text-bb-accent hover:underline text-sm"
                    >
                      Set the first one
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-5">
                  {monthlyBooksData?.items.map((mb) => (
                    <MonthlyBookCard
                      key={mb.id}
                      monthlyBook={mb}
                      clubId={id!}
                      isOwner={isOwner}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Add book modal */}
      {showAddBook && (
        <AddBookModal
          heading="Add Book to Club"
          pickLabel="Add to club"
          onClose={() => setShowAddBook(false)}
          onPicked={async (book) => {
            await addBookToClub(id!, book.id);
            invalidateClubBooks();
          }}
        />
      )}

      {/* Set monthly book modal */}
      {showSetBook && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-white font-semibold">Set Monthly Book</h2>
              <button
                onClick={() => {
                  setShowSetBook(false);
                  setMbSearch('');
                }}
                className="text-bb-muted hover:text-white text-lg leading-none"
              >
                ×
              </button>
            </div>
            <p className="text-bb-muted text-xs mb-4">
              Starts a 30-day reading cycle and creates a reading register for
              every active member.
            </p>
            <input
              className="input mb-4"
              placeholder="Search books by title..."
              value={mbSearch}
              onChange={(e) => setMbSearch(e.target.value)}
              autoFocus
            />
            <div className="space-y-1 max-h-72 overflow-y-auto">
              {mbSearchResults?.items.map((book) => {
                const active = monthlyBooksData?.items.some(
                  (mb) => mb.book_id === book.id && mb.is_active
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
                      onClick={() => setMonthlyBookMutation.mutate(book.id)}
                      disabled={active || setMonthlyBookMutation.isPending}
                      className={
                        active
                          ? 'text-bb-dim text-xs shrink-0'
                          : 'btn-primary text-xs py-1 px-2 shrink-0'
                      }
                    >
                      {active ? 'Active' : 'Set'}
                    </button>
                  </div>
                );
              })}
              {mbSearchResults?.items.length === 0 && (
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
