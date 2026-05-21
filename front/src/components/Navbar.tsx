import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const navLink = ({ isActive }: { isActive: boolean }) =>
    `text-[11px] font-semibold uppercase tracking-wider transition-colors ${
      isActive ? 'text-white' : 'text-bb-muted hover:text-white'
    }`;

  return (
    <nav className="bg-bb-dark border-b border-bb-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center h-12 gap-6">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0 group">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              className="w-5 h-5 text-bb-accent"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <span className="font-bold text-white text-base tracking-tight">
              Book<span className="text-bb-accent">Boxd</span>
            </span>
          </Link>

          {/* Nav links */}
          <div className="flex items-center gap-5">
            <NavLink to="/books" className={navLink}>
              Books
            </NavLink>
            <NavLink to="/clubs" className={navLink}>
              Clubs
            </NavLink>
            <NavLink to="/library" className={navLink}>
              Library
            </NavLink>
            <NavLink to="/shelves" className={navLink}>
              Shelves
            </NavLink>
          </div>

          {/* User menu */}
          {user && (
            <div className="ml-auto relative" ref={ref}>
              <button
                onClick={() => setOpen((v) => !v)}
                className="flex items-center gap-2 text-bb-muted hover:text-white transition-colors"
              >
                <div className="w-7 h-7 rounded-full bg-bb-accent/20 border border-bb-accent/40 flex items-center justify-center text-bb-accent font-bold text-xs">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <span className="text-sm font-medium hidden sm:block">
                  {user.name.split(' ')[0]}
                </span>
                <svg
                  className="w-3 h-3 hidden sm:block"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {open && (
                <div className="absolute right-0 top-full mt-1 w-44 bg-bb-surface border border-bb-border rounded-lg shadow-2xl overflow-hidden">
                  <Link
                    to="/profile"
                    className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-bb-muted hover:text-white hover:bg-bb-card transition-colors"
                    onClick={() => setOpen(false)}
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                    Profile
                  </Link>
                  <div className="border-t border-bb-border" />
                  <button
                    onClick={() => {
                      logout();
                      navigate('/login');
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-bb-muted hover:text-white hover:bg-bb-card transition-colors"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      />
                    </svg>
                    Sign out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
