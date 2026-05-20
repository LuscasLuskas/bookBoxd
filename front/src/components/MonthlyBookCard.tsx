import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  clearMonthlyBook,
  getMyRegister,
  listRegisters,
  updateMyRegister,
} from '../api/monthlyBooks';
import { useAuth } from '../contexts/AuthContext';
import type { GoalFrequency, MonthlyBook, ReadingUnit } from '../types';

const UNIT_LABEL: Record<ReadingUnit, { one: string; many: string }> = {
  PAGE: { one: 'page', many: 'pages' },
  CHAPTER: { one: 'chapter', many: 'chapters' },
};

function errMsg(err: unknown): string {
  const e = err as { response?: { data?: { detail?: string } } };
  return e?.response?.data?.detail || 'Something went wrong';
}

function plural(n: number, unit: ReadingUnit): string {
  return n === 1 ? UNIT_LABEL[unit].one : UNIT_LABEL[unit].many;
}

function ProgressBar({ percent }: { percent: number }) {
  return (
    <div className="h-2 rounded-full bg-bb-surface overflow-hidden">
      <div
        className="h-full bg-bb-accent rounded-full transition-all"
        style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
      />
    </div>
  );
}

function Toggle<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="inline-flex rounded-md border border-bb-border overflow-hidden">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={`px-3 py-1.5 text-xs font-medium transition-colors ${
            value === o.value
              ? 'bg-bb-accent text-white'
              : 'bg-bb-surface text-bb-muted hover:text-white'
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export default function MonthlyBookCard({
  monthlyBook,
  clubId,
  isOwner,
}: {
  monthlyBook: MonthlyBook;
  clubId: string;
  isOwner: boolean;
}) {
  const mb = monthlyBook;
  const qc = useQueryClient();
  const { user } = useAuth();

  const { data: register } = useQuery({
    queryKey: ['myRegister', clubId, mb.id],
    queryFn: () => getMyRegister(clubId, mb.id),
  });

  const { data: board } = useQuery({
    queryKey: ['registers', clubId, mb.id],
    queryFn: () => listRegisters(clubId, mb.id),
  });

  const [unit, setUnit] = useState<ReadingUnit>('PAGE');
  const [freq, setFreq] = useState<GoalFrequency>('DAILY');
  const [total, setTotal] = useState('');
  const [pos, setPos] = useState('');

  useEffect(() => {
    if (register) {
      setUnit(register.unit);
      setFreq(register.goal_frequency);
      setTotal(register.total_amount?.toString() ?? '');
      setPos(register.current_position.toString());
    }
  }, [register]);

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload: {
        unit: ReadingUnit;
        goal_frequency: GoalFrequency;
        total_amount?: number;
        current_position?: number;
      } = { unit, goal_frequency: freq };
      const t = parseInt(total, 10);
      const p = parseInt(pos, 10);
      if (!Number.isNaN(t) && t >= 1) payload.total_amount = t;
      if (!Number.isNaN(p) && p >= 0) payload.current_position = p;
      return updateMyRegister(clubId, mb.id, payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['myRegister', clubId, mb.id] });
      qc.invalidateQueries({ queryKey: ['registers', clubId, mb.id] });
      toast.success('Reading register saved');
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const endMutation = useMutation({
    mutationFn: () => clearMonthlyBook(clubId, mb.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['monthlyBooks', clubId] });
      toast.success('Monthly book ended');
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const dirty =
    !!register &&
    (unit !== register.unit ||
      freq !== register.goal_frequency ||
      total !== (register.total_amount?.toString() ?? '') ||
      pos !== register.current_position.toString());

  return (
    <div className="card p-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-white font-semibold">{mb.book_title}</h3>
            {mb.is_active ? (
              <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-green-900/50 text-green-300 font-bold">
                Active
              </span>
            ) : (
              <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-bb-surface text-bb-dim font-bold">
                Ended
              </span>
            )}
          </div>
          <p className="text-bb-muted text-sm">{mb.book_author}</p>
        </div>
        <div className="text-right text-xs text-bb-dim shrink-0">
          {mb.is_active ? (
            <span>
              {mb.days_remaining} of {mb.cycle_days} days left
            </span>
          ) : (
            <span>Cycle closed</span>
          )}
        </div>
      </div>

      {/* Cycle progress */}
      <div className="mt-3">
        <ProgressBar percent={(mb.days_elapsed / mb.cycle_days) * 100} />
        <p className="text-bb-dim text-[11px] mt-1">
          Day {mb.days_elapsed} of {mb.cycle_days} · {mb.member_count} member
          {mb.member_count === 1 ? '' : 's'} reading
        </p>
      </div>

      {/* My register */}
      <div className="mt-5 border-t border-bb-border pt-4">
        <p className="text-bb-text text-sm font-medium mb-3">Your reading</p>

        {!register ? (
          <p className="text-bb-muted text-sm">Loading your register…</p>
        ) : (
          <>
            <div className="flex flex-wrap gap-4 mb-3">
              <div>
                <label className="block text-bb-dim text-[11px] mb-1">
                  Track by
                </label>
                <Toggle<ReadingUnit>
                  value={unit}
                  onChange={setUnit}
                  options={[
                    { value: 'PAGE', label: 'Pages' },
                    { value: 'CHAPTER', label: 'Chapters' },
                  ]}
                />
              </div>
              <div>
                <label className="block text-bb-dim text-[11px] mb-1">
                  Goal shown per
                </label>
                <Toggle<GoalFrequency>
                  value={freq}
                  onChange={setFreq}
                  options={[
                    { value: 'DAILY', label: 'Day' },
                    { value: 'WEEKLY', label: 'Week' },
                  ]}
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-4 items-end">
              <div>
                <label className="block text-bb-dim text-[11px] mb-1">
                  Total {plural(2, unit)} in your edition
                </label>
                <input
                  type="number"
                  min={1}
                  className="input w-36"
                  placeholder="e.g. 320"
                  value={total}
                  onChange={(e) => setTotal(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-bb-dim text-[11px] mb-1">
                  Current {UNIT_LABEL[unit].one}
                </label>
                <input
                  type="number"
                  min={0}
                  className="input w-36"
                  placeholder="0"
                  value={pos}
                  onChange={(e) => setPos(e.target.value)}
                />
              </div>
              <button
                onClick={() => saveMutation.mutate()}
                disabled={!dirty || saveMutation.isPending}
                className="btn-primary"
              >
                {saveMutation.isPending ? 'Saving…' : 'Save'}
              </button>
            </div>

            {/* Stats */}
            {register.is_configured ? (
              <div className="mt-4 bg-bb-surface/50 rounded-lg p-3">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-bb-text">
                    {UNIT_LABEL[register.unit].one[0].toUpperCase() +
                      UNIT_LABEL[register.unit].one.slice(1)}{' '}
                    {register.current_position} of {register.total_amount}
                  </span>
                  <span className="text-bb-muted">
                    {register.progress_percent}%
                  </span>
                </div>
                <ProgressBar percent={register.progress_percent} />
                <div className="flex items-center justify-between gap-2 mt-2.5 flex-wrap">
                  <span className="text-xs text-bb-muted">
                    {register.is_completed
                      ? '🎉 You finished this book!'
                      : `Goal: ${register.current_goal} ${plural(
                          register.current_goal ?? 0,
                          register.unit
                        )} per ${
                          register.goal_frequency === 'DAILY' ? 'day' : 'week'
                        }`}
                  </span>
                  {register.is_completed ? (
                    <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-green-900/50 text-green-300 font-bold">
                      Completed
                    </span>
                  ) : register.on_pace ? (
                    <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-green-900/50 text-green-300 font-bold">
                      On pace
                    </span>
                  ) : (
                    <span className="text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-900/50 text-amber-300 font-bold">
                      Behind
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-bb-dim text-xs mt-3">
                Enter your edition's total length above to start tracking a
                daily goal.
              </p>
            )}
          </>
        )}
      </div>

      {/* Club leaderboard */}
      {board && board.items.length > 0 && (
        <div className="mt-5 border-t border-bb-border pt-4">
          <p className="text-bb-text text-sm font-medium mb-3">Club progress</p>
          <div className="space-y-2">
            {board.items.map((r) => (
              <div key={r.id} className="flex items-center gap-3">
                <span
                  className={`text-xs w-32 truncate shrink-0 ${
                    r.user_id === user?.id
                      ? 'text-bb-accent font-medium'
                      : 'text-bb-muted'
                  }`}
                >
                  {r.user_id === user?.id ? 'You' : r.user_name}
                </span>
                <div className="flex-1">
                  <ProgressBar percent={r.progress_percent} />
                </div>
                <span className="text-bb-dim text-[11px] w-10 text-right shrink-0">
                  {r.progress_percent}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Owner control */}
      {isOwner && mb.is_active && (
        <div className="mt-5 border-t border-bb-border pt-4">
          <button
            onClick={() => {
              if (window.confirm('End this monthly book? Members keep their progress.'))
                endMutation.mutate();
            }}
            disabled={endMutation.isPending}
            className="btn-ghost text-xs py-1 px-2"
          >
            End monthly book
          </button>
        </div>
      )}
    </div>
  );
}
