import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import type { CredentialResponse } from '@react-oauth/google';
import toast from 'react-hot-toast';
import { loginWithGoogle } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { getBookGradient } from '../utils/bookCover';

const SAMPLE_TITLES = [
  'The Great Gatsby', 'To Kill a Mockingbird', '1984', 'Pride and Prejudice',
  'The Catcher in the Rye', 'Brave New World', 'One Hundred Years of Solitude',
  'The Lord of the Rings', 'Harry Potter', 'Don Quixote', 'Crime and Punishment',
  'Moby Dick', 'War and Peace', 'Anna Karenina', 'The Brothers Karamazov',
  'Ulysses', 'Hamlet', 'Lolita', 'The Odyssey', 'Middlemarch',
  'Jane Eyre', 'Wuthering Heights', 'David Copperfield', 'Madame Bovary',
  'In Search of Lost Time', 'The Trial', 'The Metamorphosis', 'Invisible Man',
  'Beloved', 'The Sound and the Fury', 'As I Lay Dying', 'Light in August',
  'Catch-22', 'Slaughterhouse-Five', 'The Sun Also Rises', 'A Farewell to Arms',
  'For Whom the Bell Tolls', 'The Old Man and the Sea', 'East of Eden',
  'Of Mice and Men', 'Grapes of Wrath', 'To the Lighthouse', 'Mrs Dalloway',
  'The Waves', 'Orlando', 'A Room With a View', 'Howards End', 'The Remains of the Day',
  'Never Let Me Go', 'The Unconsoled', 'Disgrace', 'Waiting for the Barbarians',
  'The God of Small Things', 'Midnight Children', 'White Teeth', 'Atonement',
  'Saturday', 'On Chesil Beach', 'Amsterdam', 'The Corrections', 'Freedom',
  'The Road', 'No Country for Old Men', 'Blood Meridian', 'Suttree',
];

function BackgroundGrid() {
  return (
    <div className="absolute inset-0 overflow-hidden">
      <div
        className="grid gap-1.5 p-2"
        style={{ gridTemplateColumns: 'repeat(9, 1fr)' }}
      >
        {SAMPLE_TITLES.map((title, i) => (
          <div
            key={i}
            className="aspect-[2/3] rounded-sm opacity-40"
            style={{ background: getBookGradient(title) }}
          />
        ))}
      </div>
    </div>
  );
}

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSuccess = async (res: CredentialResponse) => {
    if (!res.credential) return;
    setLoading(true);
    try {
      const token = await loginWithGoogle(res.credential);
      login(token);
      navigate('/');
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-bb-dark flex items-center justify-center overflow-hidden">
      <BackgroundGrid />
      <div className="absolute inset-0 bg-gradient-to-b from-bb-dark/60 via-bb-dark/80 to-bb-dark/95" />

      <div className="relative z-10 w-full max-w-sm px-4">
        {/* Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-bb-accent/10 border border-bb-accent/20 mb-5">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              className="w-8 h-8 text-bb-accent"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tight">
            Book<span className="text-bb-accent">Boxd</span>
          </h1>
          <p className="text-bb-muted mt-2 text-sm leading-relaxed">
            Track your reading journey.<br />Discover. Connect. Share.
          </p>
        </div>

        {/* Card */}
        <div className="card p-6">
          <h2 className="text-center text-bb-text font-medium mb-6 text-sm uppercase tracking-wider">
            Sign in to continue
          </h2>

          {loading ? (
            <div className="flex items-center justify-center py-4">
              <div className="w-6 h-6 border-2 border-bb-border border-t-bb-accent rounded-full animate-spin" />
            </div>
          ) : (
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleSuccess}
                onError={() => toast.error('Google login failed')}
                theme="filled_black"
                shape="pill"
                size="large"
                text="signin_with"
              />
            </div>
          )}

          <p className="mt-6 text-center text-bb-dim text-xs">
            By signing in, you agree to read more books than you'll ever finish.
          </p>
        </div>
      </div>
    </div>
  );
}
