import { Link } from 'react-router-dom';
import type { BookClub } from '../types';

interface Props {
  club: BookClub;
  isOwner?: boolean;
  memberStatus?: string;
}

export default function ClubCard({ club, isOwner, memberStatus }: Props) {
  return (
    <Link
      to={`/clubs/${club.id}`}
      className="group card p-4 hover:border-bb-accent/40 transition-colors block"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-bb-text group-hover:text-white transition-colors truncate">
            {club.name}
          </h3>
          {club.description && (
            <p className="text-bb-muted text-sm mt-1 line-clamp-2 leading-relaxed">
              {club.description}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          {isOwner && (
            <span className="text-[10px] font-semibold px-1.5 py-0.5 bg-bb-accent/20 text-bb-accent rounded">
              Owner
            </span>
          )}
          {memberStatus && !isOwner && (
            <span className="text-[10px] font-medium px-1.5 py-0.5 bg-green-900/50 text-green-300 rounded border border-green-700">
              {memberStatus}
            </span>
          )}
        </div>
      </div>
      <div className="mt-3 text-bb-dim text-xs">
        {new Date(club.created_at).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
        })}
      </div>
    </Link>
  );
}
