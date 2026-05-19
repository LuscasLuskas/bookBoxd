import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { listClubs, createClub } from '../api/clubs';
import { useAuth } from '../contexts/AuthContext';
import ClubCard from '../components/ClubCard';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Clubs() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', description: '' });

  const { data: clubs, isLoading } = useQuery({
    queryKey: ['clubs'],
    queryFn: listClubs,
  });

  const createMutation = useMutation({
    mutationFn: createClub,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clubs'] });
      toast.success('Club created!');
      setShowCreate(false);
      setForm({ name: '', description: '' });
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Failed to create club');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    createMutation.mutate({
      name: form.name.trim(),
      description: form.description.trim() || undefined,
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-start justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Book Clubs</h1>
          {clubs && (
            <p className="text-bb-muted text-sm mt-0.5">{clubs.length} clubs</p>
          )}
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          + Create Club
        </button>
      </div>

      {isLoading ? (
        <div className="py-20">
          <LoadingSpinner />
        </div>
      ) : clubs?.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-bb-muted mb-4">No clubs yet.</p>
          <button onClick={() => setShowCreate(true)} className="btn-primary">
            Create the first club
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {clubs?.map((club) => (
            <ClubCard
              key={club.id}
              club={club}
              isOwner={club.owner_id === user?.id}
            />
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-white font-semibold text-lg">Create Club</h2>
              <button
                onClick={() => setShowCreate(false)}
                className="text-bb-muted hover:text-white transition-colors text-lg leading-none"
              >
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Club Name *</label>
                <input
                  className="input"
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  placeholder="Name your club"
                  required
                  autoFocus
                />
              </div>
              <div>
                <label className="label">Description</label>
                <textarea
                  className="textarea"
                  rows={3}
                  value={form.description}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, description: e.target.value }))
                  }
                  placeholder="What is this club about?"
                />
              </div>
              <div className="flex gap-3 pt-1">
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="btn-primary flex-1"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create Club'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="btn-ghost"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
