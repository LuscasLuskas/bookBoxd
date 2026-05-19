import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { getMe, deleteMe } from '../api/users';
import { listLibrary } from '../api/userBooks';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import type { UserBookStatus } from '../types';

const STATS: { status: UserBookStatus; label: string; color: string }[] = [
  { status: 'COMPLETED', label: 'Completed', color: 'text-amber-400' },
  { status: 'READING', label: 'Reading', color: 'text-green-400' },
  { status: 'WISHLIST', label: 'Wishlist', color: 'text-purple-400' },
  { status: 'DROPPED', label: 'Dropped', color: 'text-gray-400' },
];

export default function Profile() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const { data: user, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  });

  const { data: library } = useQuery({
    queryKey: ['library', 'all-for-stats'],
    queryFn: () => listLibrary({ limit: 1000 }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteMe,
    onSuccess: () => {
      toast.success('Account deleted');
      logout();
      navigate('/login');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Error deleting account');
    },
  });

  if (isLoading)
    return (
      <div className="py-20">
        <LoadingSpinner />
      </div>
    );
  if (!user) return null;

  const counts = STATS.reduce(
    (acc, { status }) => ({
      ...acc,
      [status]: library?.items.filter((ub) => ub.status === status).length ?? 0,
    }),
    {} as Record<UserBookStatus, number>
  );
  const total = library?.total ?? 0;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Profile card */}
      <div className="card p-6 mb-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-full bg-bb-accent/20 border-2 border-bb-accent/40 flex items-center justify-center text-bb-accent font-bold text-2xl shrink-0">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-white truncate">{user.name}</h1>
            <p className="text-bb-muted text-sm mt-0.5">{user.email}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <span
                className={`text-xs px-2 py-0.5 rounded border font-medium ${
                  user.role === 'master'
                    ? 'bg-purple-900/50 text-purple-300 border-purple-700'
                    : 'bg-bb-surface text-bb-muted border-bb-border'
                }`}
              >
                {user.role.toUpperCase()}
              </span>
              <span className="text-bb-dim text-xs">
                Joined{' '}
                {new Date(user.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                })}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Reading stats */}
      <div className="mb-6">
        <h2 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-3">
          Reading Stats
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STATS.map(({ status, label, color }) => (
            <div key={status} className="card p-4 text-center">
              <p className={`text-2xl font-bold ${color}`}>{counts[status]}</p>
              <p className="text-bb-muted text-xs mt-1">{label}</p>
            </div>
          ))}
        </div>
        <p className="text-bb-dim text-xs mt-3 text-center">
          {total} total books in library
        </p>
      </div>

      {/* Danger zone */}
      <div className="card p-5 border-red-900/40">
        <h3 className="text-red-400 font-medium mb-1">Danger Zone</h3>
        <p className="text-bb-muted text-sm mb-4 leading-relaxed">
          Permanently delete your account and all your data. Clubs you own will be
          transferred or deleted. This cannot be undone.
        </p>
        <button
          onClick={() => {
            if (
              window.confirm(
                'Are you sure? This will permanently delete your account and cannot be undone.'
              )
            )
              deleteMutation.mutate();
          }}
          disabled={deleteMutation.isPending}
          className="btn-danger"
        >
          {deleteMutation.isPending ? 'Deleting…' : 'Delete Account'}
        </button>
      </div>
    </div>
  );
}
