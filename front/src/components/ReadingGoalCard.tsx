import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  deleteReadingGoal,
  getReadingGoal,
  getReadingHistory,
  getReadingStats,
  logToday,
  upsertReadingGoal,
} from '../api/readingGoal';
import type { DailyReadingLog } from '../types';

/** Returns a YYYY-MM-DD key in UTC, matching how the backend stores log dates. */
function dateKeyUTC(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** Last 30 days as an array of date keys, oldest first. */
function last30Days(): string[] {
  const out: string[] = [];
  const today = new Date();
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today);
    d.setUTCDate(today.getUTCDate() - i);
    out.push(dateKeyUTC(d));
  }
  return out;
}

/** A simple 30-cell heatmap of met/partial/missed days. */
function HistoryStrip({ logs }: { logs: DailyReadingLog[] }) {
  const byDate = new Map(logs.map((l) => [l.date, l]));
  const days = last30Days();
  return (
    <div className="grid grid-cols-30 gap-[3px]" style={{ gridTemplateColumns: 'repeat(30, minmax(0, 1fr))' }}>
      {days.map((day) => {
        const log = byDate.get(day);
        let cls = 'bg-bb-surface';
        let title = `${day}: no entry`;
        if (log) {
          const pct = log.goal_target > 0 ? log.pages_read / log.goal_target : 0;
          if (pct >= 1) {
            cls = 'bg-amber-400/80';
            title = `${day}: ${log.pages_read}/${log.goal_target} pages — goal met`;
          } else if (pct > 0) {
            cls = 'bg-amber-400/30';
            title = `${day}: ${log.pages_read}/${log.goal_target} pages — partial`;
          } else {
            cls = 'bg-red-900/30';
            title = `${day}: 0/${log.goal_target} pages`;
          }
        }
        return (
          <div
            key={day}
            title={title}
            className={`aspect-square rounded-sm ${cls}`}
          />
        );
      })}
    </div>
  );
}

export default function ReadingGoalCard() {
  const qc = useQueryClient();
  const [editingGoal, setEditingGoal] = useState(false);
  const [goalInput, setGoalInput] = useState('');
  const [pagesInput, setPagesInput] = useState('');

  const { data: goal, isLoading: goalLoading } = useQuery({
    queryKey: ['reading-goal'],
    queryFn: getReadingGoal,
  });

  const { data: stats } = useQuery({
    queryKey: ['reading-goal', 'stats'],
    queryFn: getReadingStats,
  });

  const { data: history } = useQuery({
    queryKey: ['reading-goal', 'history'],
    queryFn: () => getReadingHistory(30),
  });

  const saveGoal = useMutation({
    mutationFn: (pages: number) => upsertReadingGoal(pages),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['reading-goal'] });
      toast.success('Goal saved');
      setEditingGoal(false);
      setGoalInput('');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Failed to save goal');
    },
  });

  const toggleVisibility = useMutation({
    mutationFn: (nextPublic: boolean) =>
      upsertReadingGoal(goal!.pages_per_day, nextPublic),
    onSuccess: (g) => {
      qc.invalidateQueries({ queryKey: ['reading-goal'] });
      toast.success(g.streak_public ? 'Streak is now public' : 'Streak is now private');
    },
    onError: () => toast.error('Failed to update visibility'),
  });

  const removeGoal = useMutation({
    mutationFn: deleteReadingGoal,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['reading-goal'] });
      toast.success('Goal removed');
    },
    onError: () => toast.error('Failed to remove goal'),
  });

  const logPages = useMutation({
    mutationFn: (pages: number) => logToday(pages),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['reading-goal'] });
      setPagesInput('');
      toast.success('Logged');
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Failed to log');
    },
  });

  if (goalLoading) return null;

  // ---- No goal yet ----
  if (!goal) {
    return (
      <div className="card p-5 mb-6">
        <h3 className="text-bb-muted text-xs font-semibold uppercase tracking-wider mb-2">
          Daily Reading Goal
        </h3>
        <p className="text-bb-text text-sm mb-3 leading-relaxed">
          Set a small daily target. Just for you — no one else sees it.
        </p>
        <div className="flex gap-2">
          <input
            type="number"
            min={1}
            max={10000}
            placeholder="Pages per day"
            value={goalInput}
            onChange={(e) => setGoalInput(e.target.value)}
            className="input flex-1"
          />
          <button
            onClick={() => {
              const n = Number(goalInput);
              if (!Number.isFinite(n) || n < 1) {
                toast.error('Enter a positive number of pages');
                return;
              }
              saveGoal.mutate(Math.floor(n));
            }}
            disabled={saveGoal.isPending}
            className="btn-primary"
          >
            {saveGoal.isPending ? '…' : 'Set Goal'}
          </button>
        </div>
      </div>
    );
  }

  // ---- Goal set ----
  const todayPct = stats && stats.today_goal_target
    ? Math.min(100, Math.round((stats.today_pages_read / stats.today_goal_target) * 100))
    : 0;

  return (
    <div className="card p-5 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-bb-muted text-xs font-semibold uppercase tracking-wider">
          Daily Reading Goal
        </h3>
        {!editingGoal && (
          <button
            onClick={() => {
              setGoalInput(String(goal.pages_per_day));
              setEditingGoal(true);
            }}
            className="text-bb-dim hover:text-bb-text text-xs"
          >
            Edit
          </button>
        )}
      </div>

      {/* Goal value / editor */}
      {editingGoal ? (
        <div className="flex gap-2 mb-4">
          <input
            type="number"
            min={1}
            max={10000}
            value={goalInput}
            onChange={(e) => setGoalInput(e.target.value)}
            className="input flex-1"
          />
          <button
            onClick={() => {
              const n = Number(goalInput);
              if (!Number.isFinite(n) || n < 1) {
                toast.error('Enter a positive number of pages');
                return;
              }
              saveGoal.mutate(Math.floor(n));
            }}
            disabled={saveGoal.isPending}
            className="btn-primary"
          >
            Save
          </button>
          <button
            onClick={() => setEditingGoal(false)}
            className="btn-ghost"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="mb-4">
          <span className="text-3xl font-bold text-amber-400">
            {goal.pages_per_day}
          </span>
          <span className="text-bb-muted text-sm ml-2">pages / day</span>
        </div>
      )}

      {/* Today's progress + log input */}
      <div className="mb-5">
        <div className="flex items-baseline justify-between mb-1">
          <span className="text-bb-muted text-xs uppercase tracking-wider">Today</span>
          <span className="text-bb-text text-sm">
            {stats?.today_pages_read ?? 0} / {goal.pages_per_day} pages
          </span>
        </div>
        <div className="h-2 bg-bb-surface rounded overflow-hidden mb-2">
          <div
            className={`h-full transition-all ${
              todayPct >= 100 ? 'bg-amber-400' : 'bg-amber-400/60'
            }`}
            style={{ width: `${todayPct}%` }}
          />
        </div>
        {stats?.today_goal_met ? (
          <p className="text-amber-400 text-xs">Goal met for today.</p>
        ) : (
          <div className="flex gap-2 mt-2">
            <input
              type="number"
              min={0}
              max={100000}
              placeholder="Pages read today"
              value={pagesInput}
              onChange={(e) => setPagesInput(e.target.value)}
              className="input flex-1"
            />
            <button
              onClick={() => {
                const n = Number(pagesInput);
                if (!Number.isFinite(n) || n < 0) {
                  toast.error('Enter a non-negative number');
                  return;
                }
                logPages.mutate(Math.floor(n));
              }}
              disabled={logPages.isPending}
              className="btn-primary"
            >
              {logPages.isPending ? '…' : 'Log'}
            </button>
          </div>
        )}
      </div>

      {/* Streak stats */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="text-center">
          <p className="text-2xl font-bold text-amber-400">
            {stats?.current_streak ?? 0}
          </p>
          <p className="text-bb-muted text-xs mt-1">Current streak</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-bb-text">
            {stats?.longest_streak ?? 0}
          </p>
          <p className="text-bb-muted text-xs mt-1">Longest</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-bb-text">
            {stats?.total_days_met ?? 0}
          </p>
          <p className="text-bb-muted text-xs mt-1">Days met</p>
        </div>
      </div>

      {/* 30-day strip */}
      {history && history.items.length > 0 && (
        <div>
          <p className="text-bb-muted text-xs uppercase tracking-wider mb-2">
            Last 30 days
          </p>
          <HistoryStrip logs={history.items} />
        </div>
      )}

      {/* Visibility toggle */}
      <div className="mt-5 pt-4 border-t border-bb-border">
        <label className="flex items-start gap-3 cursor-pointer select-none">
          <button
            type="button"
            role="switch"
            aria-checked={goal.streak_public}
            onClick={() => toggleVisibility.mutate(!goal.streak_public)}
            disabled={toggleVisibility.isPending}
            className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors mt-0.5 ${
              goal.streak_public ? 'bg-amber-400' : 'bg-bb-surface border border-bb-border'
            } disabled:opacity-50`}
          >
            <span
              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                goal.streak_public ? 'translate-x-5' : 'translate-x-1'
              }`}
            />
          </button>
          <div className="min-w-0">
            <p className="text-bb-text text-sm">
              {goal.streak_public ? 'Streak is public' : 'Streak is private'}
            </p>
            <p className="text-bb-dim text-xs leading-relaxed mt-0.5">
              {goal.streak_public
                ? 'Visitors of your profile can see your current and longest streak. Daily history stays private.'
                : 'Only you can see your streak. No one else.'}
            </p>
          </div>
        </label>
      </div>

      {/* Remove goal */}
      <div className="mt-4">
        <button
          onClick={() => {
            if (window.confirm('Remove your reading goal? Your history is kept.')) {
              removeGoal.mutate();
            }
          }}
          disabled={removeGoal.isPending}
          className="text-bb-dim hover:text-red-400 text-xs"
        >
          Remove goal
        </button>
      </div>
    </div>
  );
}
