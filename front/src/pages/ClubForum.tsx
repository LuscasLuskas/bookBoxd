import { useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getClub } from '../api/clubs';
import { listClubBooks } from '../api/clubBooks';
import { getBook } from '../api/books';
import {
  createPost,
  createThread,
  deletePost,
  deleteThread,
  getThread,
  listThreads,
  updatePost,
} from '../api/forum';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import SpoilerText from '../components/SpoilerText';
import { getBookGradient } from '../utils/bookCover';
import { avatarSrc } from '../utils/avatar';
import type { Book, ForumPost, ForumThread } from '../types';

/**
 * Wraps the textarea's current selection in /.../. If nothing is selected,
 * inserts /spoiler/ at the cursor and pre-selects the word so the user can
 * type over it.
 */
function wrapSelectionAsSpoiler(
  textarea: HTMLTextAreaElement,
  setValue: (next: string) => void,
) {
  const { value, selectionStart, selectionEnd } = textarea;
  const selected = value.slice(selectionStart, selectionEnd);
  if (selected) {
    const next =
      value.slice(0, selectionStart) +
      `/${selected}/` +
      value.slice(selectionEnd);
    setValue(next);
    requestAnimationFrame(() => {
      textarea.focus();
      const end = selectionEnd + 2;
      textarea.setSelectionRange(end, end);
    });
  } else {
    const placeholder = 'spoiler';
    const next =
      value.slice(0, selectionStart) +
      `/${placeholder}/` +
      value.slice(selectionEnd);
    setValue(next);
    requestAnimationFrame(() => {
      textarea.focus();
      const start = selectionStart + 1;
      textarea.setSelectionRange(start, start + placeholder.length);
    });
  }
}

function errMessage(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } };
  return e?.response?.data?.detail || 'Error';
}

function BookCoverThumb({
  title,
  coverUrl,
  size = 36,
}: {
  title: string;
  coverUrl: string | null;
  size?: number;
}) {
  const [errored, setErrored] = useState(false);
  return (
    <div
      className="rounded-sm overflow-hidden shrink-0 bg-bb-surface"
      style={{ width: size, height: size * 1.5 }}
    >
      {coverUrl && !errored ? (
        <img
          src={coverUrl}
          alt={title}
          onError={() => setErrored(true)}
          className="w-full h-full object-cover"
        />
      ) : (
        <div
          className="w-full h-full"
          style={{ background: getBookGradient(title) }}
        />
      )}
    </div>
  );
}

interface PostItemProps {
  post: ForumPost;
  clubId: string;
  threadId: string;
  currentUserId: string | undefined;
  canModerate: boolean;
}

function PostItem({
  post,
  clubId,
  threadId,
  currentUserId,
  canModerate,
}: PostItemProps) {
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(post.body);
  const draftRef = useRef<HTMLTextAreaElement>(null);

  const invalidateThread = () =>
    Promise.all([
      qc.invalidateQueries({ queryKey: ['forumThread', clubId, threadId] }),
      qc.invalidateQueries({ queryKey: ['forumThreads', clubId] }),
    ]);

  const editMutation = useMutation({
    mutationFn: (body: string) => updatePost(clubId, threadId, post.id, body),
    onSuccess: () => {
      invalidateThread();
      setEditing(false);
      toast.success('Updated');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deletePost(clubId, threadId, post.id),
    onSuccess: () => {
      invalidateThread();
      toast.success('Comment excluded');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  if (post.is_deleted) {
    return (
      <div className="flex items-start gap-3 opacity-60">
        <div className="w-7 h-7 rounded-full bg-bb-surface border border-bb-border shrink-0" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-bb-dim text-xs italic">No name</span>
            <span className="text-bb-dim text-[10px]">
              {new Date(post.created_at).toLocaleString()}
            </span>
          </div>
          <p className="text-bb-dim text-sm mt-1 italic">[excluded comment]</p>
        </div>
      </div>
    );
  }

  const isAuthor = currentUserId != null && post.user_id === currentUserId;
  const canEdit = isAuthor;
  const canDelete = isAuthor || canModerate;

  return (
    <div className="flex items-start gap-3">
      <div className="w-7 h-7 rounded-full overflow-hidden bg-bb-surface border border-bb-border flex items-center justify-center text-bb-muted text-[10px] font-bold shrink-0">
        {avatarSrc(post.user_avatar_url) ? (
          <img
            src={avatarSrc(post.user_avatar_url)!}
            alt=""
            className="w-full h-full object-cover"
          />
        ) : (
          (post.user_name ?? '?').charAt(0).toUpperCase()
        )}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-bb-text text-xs font-medium">
            {post.user_name ?? 'Unknown'}
          </span>
          <span className="text-bb-dim text-[10px]">
            {new Date(post.created_at).toLocaleString()}
          </span>
          {post.is_edited && (
            <span className="text-bb-dim text-[10px] italic">(edited)</span>
          )}
        </div>
        {editing ? (
          <div className="mt-2 space-y-2">
            <textarea
              ref={draftRef}
              className="input text-sm w-full min-h-16"
              maxLength={10000}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
            />
            <div className="flex items-center gap-2 flex-wrap">
              <button
                type="button"
                onClick={() => {
                  if (draftRef.current)
                    wrapSelectionAsSpoiler(draftRef.current, setDraft);
                }}
                className="text-[11px] px-2 py-0.5 rounded border border-bb-border text-bb-muted hover:text-white hover:border-bb-accent/50 transition-colors"
                title="Wrap selected text in /.../ to blur it"
              >
                ⚠ Add spoiler
              </button>
              <button
                type="button"
                onClick={() => {
                  setDraft(post.body);
                  setEditing(false);
                }}
                className="btn-ghost text-[11px] ml-auto"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  const body = draft.trim();
                  if (body) editMutation.mutate(body);
                }}
                disabled={editMutation.isPending || !draft.trim()}
                className="btn-primary text-[11px]"
              >
                Save
              </button>
            </div>
          </div>
        ) : (
          <>
            <SpoilerText
              text={post.body}
              className="text-bb-muted text-sm mt-1 leading-relaxed block"
            />
            {(canEdit || canDelete) && (
              <div className="flex gap-2 mt-1.5">
                {canEdit && (
                  <button
                    onClick={() => {
                      setDraft(post.body);
                      setEditing(true);
                    }}
                    className="text-[11px] text-bb-dim hover:text-bb-accent transition-colors"
                  >
                    Edit
                  </button>
                )}
                {canDelete && (
                  <button
                    onClick={() => {
                      if (window.confirm('Exclude this comment?'))
                        deleteMutation.mutate();
                    }}
                    disabled={deleteMutation.isPending}
                    className="text-[11px] text-bb-dim hover:text-red-400 transition-colors"
                  >
                    Exclude
                  </button>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

interface ThreadRowProps {
  thread: ForumThread;
  expanded: boolean;
  canDelete: boolean;
  canModerate: boolean;
  currentUserId: string | undefined;
  clubId: string;
  onToggle: () => void;
  onDelete: () => void;
}

function ThreadRow({
  thread,
  expanded,
  canDelete,
  canModerate,
  currentUserId,
  clubId,
  onToggle,
  onDelete,
}: ThreadRowProps) {
  const qc = useQueryClient();
  const [reply, setReply] = useState('');
  const replyRef = useRef<HTMLTextAreaElement>(null);

  const { data: detail, isLoading } = useQuery({
    queryKey: ['forumThread', clubId, thread.id],
    queryFn: () => getThread(clubId, thread.id),
    enabled: expanded,
  });

  const replyMutation = useMutation({
    mutationFn: (body: string) => createPost(clubId, thread.id, body),
    onSuccess: () => {
      setReply('');
      qc.invalidateQueries({ queryKey: ['forumThread', clubId, thread.id] });
      qc.invalidateQueries({ queryKey: ['forumThreads', clubId] });
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const isBookThread = thread.book_id != null;
  const bookTitle = thread.book_title ?? 'Removed book';

  return (
    <div className="card">
      <button
        onClick={onToggle}
        className="w-full text-left p-4 flex items-start gap-3 hover:bg-bb-surface/40 transition-colors rounded"
      >
        {isBookThread ? (
          <BookCoverThumb title={bookTitle} coverUrl={thread.book_cover_url} />
        ) : (
          <div className="w-9 h-[54px] rounded-sm bg-bb-surface border border-bb-border flex items-center justify-center text-bb-dim text-xl shrink-0">
            #
          </div>
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 flex-wrap">
            {thread.is_pinned && (
              <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-bb-accent/20 text-bb-accent">
                PINNED
              </span>
            )}
            {thread.auto_created && (
              <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-bb-surface text-bb-muted border border-bb-border">
                MONTHLY BOOK
              </span>
            )}
            {isBookThread ? (
              <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-bb-accent/10 text-bb-accent border border-bb-accent/30">
                ABOUT A BOOK
              </span>
            ) : (
              <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                OFF-TOPIC
              </span>
            )}
          </div>
          <h3 className="text-white text-sm font-semibold mt-1 truncate">
            <SpoilerText text={thread.title} />
          </h3>
          {isBookThread && (
            <p className="text-bb-muted text-xs mt-0.5 truncate">
              About{' '}
              <span className="text-bb-accent font-medium">{bookTitle}</span>
            </p>
          )}
          <p className="text-bb-dim text-xs mt-1">
            {thread.posts_count}{' '}
            {thread.posts_count === 1 ? 'reply' : 'replies'} ·{' '}
            {thread.created_by_name ?? 'Unknown'} ·{' '}
            {new Date(thread.created_at).toLocaleDateString()}
          </p>
        </div>
        {thread.book_id && (
          <Link
            to={`/books/${thread.book_id}`}
            onClick={(e) => e.stopPropagation()}
            className="text-bb-accent text-xs hover:underline shrink-0 self-center"
          >
            View book →
          </Link>
        )}
      </button>

      {expanded && (
        <div className="border-t border-bb-border p-4 space-y-3">
          {isBookThread && (
            <div className="flex items-center gap-2 text-xs text-bb-muted bg-bb-surface/50 rounded p-2">
              <span aria-hidden>📖</span>
              <span>
                This discussion is about{' '}
                <Link
                  to={`/books/${thread.book_id}`}
                  className="text-bb-accent hover:underline font-medium"
                >
                  {bookTitle}
                </Link>
                .
              </span>
            </div>
          )}
          {!isBookThread && (
            <div className="text-xs text-amber-300/90 bg-amber-500/5 border border-amber-500/20 rounded p-2">
              Off-topic thread — not tied to any specific book.
            </div>
          )}
          {isLoading ? (
            <LoadingSpinner />
          ) : (
            <>
              {detail?.posts.length === 0 && (
                <p className="text-bb-dim text-xs">
                  No replies yet. Start the conversation.
                </p>
              )}
              {detail?.posts.map((p) => (
                <PostItem
                  key={p.id}
                  post={p}
                  clubId={clubId}
                  threadId={thread.id}
                  currentUserId={currentUserId}
                  canModerate={canModerate}
                />
              ))}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const body = reply.trim();
                  if (body) replyMutation.mutate(body);
                }}
                className="pt-2"
              >
                <textarea
                  ref={replyRef}
                  className="input text-sm w-full min-h-16"
                  placeholder="Write a reply… wrap /spoilers/ in slashes"
                  maxLength={10000}
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                />
                <div className="flex justify-between items-center gap-3 mt-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        if (replyRef.current)
                          wrapSelectionAsSpoiler(replyRef.current, setReply);
                      }}
                      className="text-xs px-2 py-1 rounded border border-bb-border text-bb-muted hover:text-white hover:border-bb-accent/50 transition-colors"
                      title="Wrap the selected text in /.../ to blur it"
                    >
                      ⚠ Add spoiler
                    </button>
                    {canDelete && (
                      <button
                        type="button"
                        onClick={() => {
                          if (window.confirm('Delete this thread?')) onDelete();
                        }}
                        className="btn-danger text-xs"
                      >
                        Delete thread
                      </button>
                    )}
                  </div>
                  <button
                    type="submit"
                    disabled={replyMutation.isPending || !reply.trim()}
                    className="btn-primary text-xs ml-auto"
                  >
                    Reply
                  </button>
                </div>
              </form>
            </>
          )}
        </div>
      )}
    </div>
  );
}

interface CreateThreadFormProps {
  clubId: string;
  clubBooks: Book[];
  onCreated: () => void;
}

function CreateThreadForm({ clubId, clubBooks, onCreated }: CreateThreadFormProps) {
  const qc = useQueryClient();
  const [title, setTitle] = useState('');
  const [topic, setTopic] = useState<'book' | 'other'>('book');
  const [bookId, setBookId] = useState<string>('');

  const createMutation = useMutation({
    mutationFn: () =>
      createThread(clubId, {
        title: title.trim(),
        book_id: topic === 'book' ? bookId || null : null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['forumThreads', clubId] });
      setTitle('');
      setBookId('');
      toast.success('Thread created');
      onCreated();
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  const canSubmit =
    !!title.trim() &&
    (topic === 'other' || (topic === 'book' && !!bookId)) &&
    !createMutation.isPending;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (canSubmit) createMutation.mutate();
      }}
      className="card p-4 mb-4 space-y-3"
    >
      <div>
        <label className="text-bb-muted text-xs block mb-1">Topic</label>
        <div className="flex gap-2 flex-wrap">
          <label
            className={`px-3 py-1.5 rounded text-xs font-medium cursor-pointer border ${
              topic === 'book'
                ? 'border-bb-accent bg-bb-accent/10 text-bb-accent'
                : 'border-bb-border text-bb-muted hover:text-white'
            }`}
          >
            <input
              type="radio"
              name="topic"
              checked={topic === 'book'}
              onChange={() => setTopic('book')}
              className="sr-only"
            />
            📖 About a book in this club
          </label>
          <label
            className={`px-3 py-1.5 rounded text-xs font-medium cursor-pointer border ${
              topic === 'other'
                ? 'border-amber-500/60 bg-amber-500/10 text-amber-300'
                : 'border-bb-border text-bb-muted hover:text-white'
            }`}
          >
            <input
              type="radio"
              name="topic"
              checked={topic === 'other'}
              onChange={() => setTopic('other')}
              className="sr-only"
            />
            💬 Off-topic / general
          </label>
        </div>
      </div>

      {topic === 'book' && (
        <div>
          <label className="text-bb-muted text-xs block mb-1">
            Which book?
          </label>
          {clubBooks.length === 0 ? (
            <p className="text-bb-dim text-xs">
              This club has no books yet. Add one first, or pick the off-topic
              option.
            </p>
          ) : (
            <select
              className="input text-sm w-full"
              value={bookId}
              onChange={(e) => setBookId(e.target.value)}
            >
              <option value="">Pick a book…</option>
              {clubBooks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.title} — {b.author}
                </option>
              ))}
            </select>
          )}
        </div>
      )}

      <div>
        <label className="text-bb-muted text-xs block mb-1">Thread title</label>
        <input
          className="input text-sm w-full"
          placeholder={
            topic === 'book'
              ? 'e.g. "Chapter 3 was a wild ride"'
              : 'e.g. "Next month\'s pick suggestions"'
          }
          maxLength={255}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={!canSubmit}
          className="btn-primary text-sm"
        >
          Create thread
        </button>
      </div>
    </form>
  );
}

export default function ClubForum() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const qc = useQueryClient();
  const [openThreadId, setOpenThreadId] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const { data: club } = useQuery({
    queryKey: ['club', id],
    queryFn: () => getClub(id!),
    enabled: !!id,
  });

  const { data: threads, isLoading } = useQuery({
    queryKey: ['forumThreads', id],
    queryFn: () => listThreads(id!),
    enabled: !!id,
  });

  const { data: clubBooksData } = useQuery({
    queryKey: ['clubBooks', id],
    queryFn: () => listClubBooks(id!, { limit: 100 }),
    enabled: !!id,
  });

  // Hydrate club book metadata in parallel for the thread-create dropdown.
  const bookQueries = useQueries({
    queries: (clubBooksData?.items ?? []).map((cb) => ({
      queryKey: ['book', cb.book_id],
      queryFn: () => getBook(cb.book_id),
    })),
  });
  const clubBooks: Book[] = bookQueries
    .map((q) => q.data)
    .filter((b): b is Book => !!b);

  const deleteMutation = useMutation({
    mutationFn: (threadId: string) => deleteThread(id!, threadId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['forumThreads', id] });
      setOpenThreadId(null);
      toast.success('Thread deleted');
    },
    onError: (err) => toast.error(errMessage(err)),
  });

  if (isLoading)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );

  const canModerate =
    user != null && (user.role === 'MASTER' || club?.owner_id === user.id);

  const canDeleteThread = (thread: ForumThread) => {
    if (!user) return false;
    if (canModerate) return true;
    return thread.created_by === user.id;
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        to={`/clubs/${id}`}
        className="text-bb-muted text-sm hover:text-white transition-colors inline-flex items-center gap-1 mb-6"
      >
        ← Back to club
      </Link>

      <div className="flex items-center justify-between mb-6 gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">
            {club?.name ?? 'Forum'}
          </h1>
          <p className="text-bb-muted text-sm">Forum</p>
        </div>
        <button onClick={() => setShowCreate((v) => !v)} className="btn-primary">
          {showCreate ? 'Cancel' : '+ New Thread'}
        </button>
      </div>

      {showCreate && (
        <CreateThreadForm
          clubId={id!}
          clubBooks={clubBooks}
          onCreated={() => setShowCreate(false)}
        />
      )}

      {threads && threads.items.length === 0 ? (
        <div className="text-center py-20 text-bb-muted">
          No threads yet. Start the discussion!
        </div>
      ) : (
        <div className="space-y-3">
          {threads?.items.map((t) => (
            <ThreadRow
              key={t.id}
              thread={t}
              expanded={openThreadId === t.id}
              canDelete={canDeleteThread(t)}
              canModerate={canModerate}
              currentUserId={user?.id}
              clubId={id!}
              onToggle={() =>
                setOpenThreadId((cur) => (cur === t.id ? null : t.id))
              }
              onDelete={() => deleteMutation.mutate(t.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
