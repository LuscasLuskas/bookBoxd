import type { MembershipStatus, UserBookStatus } from '../types';

const MEMBERSHIP_COLORS: Record<MembershipStatus, string> = {
  PENDING: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  ACTIVE: 'bg-green-900/50 text-green-300 border-green-700',
  LEFT: 'bg-gray-700/50 text-gray-400 border-gray-600',
  REJECTED: 'bg-red-900/50 text-red-300 border-red-700',
  BANNED: 'bg-red-950 text-red-400 border-red-900',
  KICKED: 'bg-orange-900/50 text-orange-300 border-orange-700',
};

const USER_BOOK_COLORS: Record<UserBookStatus, string> = {
  WISHLIST: 'bg-purple-900/50 text-purple-300 border-purple-700',
  ADDED: 'bg-blue-900/50 text-blue-300 border-blue-700',
  READING: 'bg-green-900/50 text-green-300 border-green-700',
  COMPLETED: 'bg-amber-900/50 text-amber-300 border-amber-700',
  DROPPED: 'bg-gray-700/50 text-gray-400 border-gray-600',
};

const USER_BOOK_LABELS: Record<UserBookStatus, string> = {
  WISHLIST: 'Wishlist',
  ADDED: 'Added',
  READING: 'Reading',
  COMPLETED: 'Completed',
  DROPPED: 'Dropped',
};

export function MembershipBadge({ status }: { status: MembershipStatus }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border capitalize ${MEMBERSHIP_COLORS[status]}`}
    >
      {status}
    </span>
  );
}

export function UserBookBadge({ status }: { status: UserBookStatus }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${USER_BOOK_COLORS[status]}`}
    >
      {USER_BOOK_LABELS[status]}
    </span>
  );
}
