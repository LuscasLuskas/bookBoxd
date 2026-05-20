import { useState } from 'react';
import { Link } from 'react-router-dom';
import { getBookGradient } from '../utils/bookCover';
import type { Book } from '../types';

interface Props {
  book: Book;
  compact?: boolean;
}

export default function BookCard({ book, compact = false }: Props) {
  const [imgError, setImgError] = useState(false);
  const hasCover = !!book.cover_url && !imgError;

  return (
    <Link to={`/books/${book.id}`} className="group block">
      <div className="relative overflow-hidden rounded-sm aspect-[2/3] w-full">
        {hasCover ? (
          <img
            src={book.cover_url!}
            alt={book.title}
            loading="lazy"
            onError={() => setImgError(true)}
            className="absolute inset-0 w-full h-full object-cover"
          />
        ) : (
          <>
            <div
              className="absolute inset-0"
              style={{ background: getBookGradient(book.title) }}
            />
            {/* Book spine */}
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-black/40" />
            {/* Text overlay (fallback only) */}
            <div className="absolute inset-0 flex flex-col justify-end p-2.5 bg-gradient-to-t from-black/80 via-black/10 to-transparent">
              <p className="text-white text-[11px] font-bold leading-tight line-clamp-3 group-hover:text-bb-accent transition-colors">
                {book.title}
              </p>
              {!compact && (
                <p className="text-white/50 text-[10px] mt-1 truncate">{book.author}</p>
              )}
            </div>
          </>
        )}
        {/* Hover highlight */}
        <div className="absolute inset-0 ring-1 ring-inset ring-transparent group-hover:ring-bb-accent/40 transition-all rounded-sm" />
      </div>
      {!compact && (
        <div className="mt-1.5 px-0.5">
          <p className="text-bb-text text-xs font-medium truncate group-hover:text-white transition-colors">
            {book.title}
          </p>
          <p className="text-bb-muted text-[11px] truncate">{book.author}</p>
        </div>
      )}
    </Link>
  );
}
