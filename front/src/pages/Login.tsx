import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import type { CredentialResponse } from '@react-oauth/google';
import toast from 'react-hot-toast';
import { loginWithGoogle } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import BookMark from '../components/BookMark';
import Bookshelf from '../components/Bookshelf';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [flyingHome, setFlyingHome] = useState(false);

  const handleSuccess = async (res: CredentialResponse) => {
    if (!res.credential) return;
    setLoading(true);
    try {
      const token = await loginWithGoogle(res.credential);
      setFlyingHome(true);
      window.setTimeout(() => {
        login(token);
        navigate('/');
      }, 850);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      toast.error(e?.response?.data?.detail || 'Authentication failed');
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-black flex flex-col overflow-hidden">
      {/* Amber spotlight from top */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 90% 60% at 50% -5%, rgba(232,160,0,0.32) 0%, rgba(232,160,0,0.08) 35%, rgba(0,0,0,0) 65%)',
        }}
      />
      {/* Warm floor glow at the bottom */}
      <div
        className="absolute inset-x-0 bottom-0 h-1/3 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 100% at 50% 110%, rgba(232,160,0,0.18) 0%, rgba(0,0,0,0) 70%)',
        }}
      />
      {/* Faint grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.06]"
        style={{
          backgroundImage:
            'linear-gradient(to right, #e8a000 1px, transparent 1px), linear-gradient(to bottom, #e8a000 1px, transparent 1px)',
          backgroundSize: '80px 80px',
          maskImage:
            'radial-gradient(ellipse 70% 60% at 50% 50%, black 30%, transparent 75%)',
          WebkitMaskImage:
            'radial-gradient(ellipse 70% 60% at 50% 50%, black 30%, transparent 75%)',
        }}
      />

      {/* Header — destination of the book animation */}
      <header className="relative z-10 px-6 sm:px-10 py-5 flex items-center gap-2">
        <div className="w-6 h-6 relative">
          <div
            className={`absolute inset-0 transition-opacity duration-300 ${
              flyingHome ? 'opacity-100 delay-[700ms]' : 'opacity-0'
            }`}
          >
            <BookMark size={24} />
          </div>
        </div>
        <span className="text-white text-sm font-bold tracking-tight">qulmus</span>
        <span className="ml-auto text-bb-accent text-xs font-medium tracking-wider uppercase">
          Beta
        </span>
      </header>

      {/* Centered hero */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          {/* Animated bookshelf — books fall and return on their own slow cycles */}
          <div className="mx-auto mb-8 flex justify-center">
            <Bookshelf flying={flyingHome} />
          </div>

          <h1 className="text-white text-5xl sm:text-6xl font-bold tracking-tight leading-[1.05]">
            Welcome to <span className="text-bb-accent">qulmus</span>.
          </h1>
          <p className="text-neutral-400 mt-4 text-base sm:text-lg leading-relaxed">
            Sign in to keep track of what you read.
          </p>

          <div className="mt-10 flex justify-center">
            {loading && !flyingHome ? (
              <div className="flex items-center py-3">
                <div className="w-5 h-5 border-2 border-neutral-700 border-t-bb-accent rounded-full animate-spin" />
                <span className="ml-3 text-neutral-400 text-sm">Signing you in…</span>
              </div>
            ) : flyingHome ? (
              <div className="py-3 text-bb-accent text-sm font-medium">
                Welcome back.
              </div>
            ) : (
              <GoogleLogin
                onSuccess={handleSuccess}
                onError={() => toast.error('Google login failed')}
                theme="filled_black"
                shape="rectangular"
                size="large"
                width="320"
                text="signin_with"
              />
            )}
          </div>

          <div className="mt-12 pt-6 border-t border-bb-accent/10">
            <p className="text-neutral-500 text-xs leading-relaxed">
              No followers. No feed. No algorithm.<br />
              Just the books you've read.
            </p>
          </div>
        </div>
      </main>

      <footer className="relative z-10 px-6 sm:px-10 py-6 flex items-center justify-between">
        <span className="text-neutral-600 text-xs">© qulmus</span>
        <span className="text-bb-accent/70 text-xs tracking-wide">For people who read.</span>
      </footer>

    </div>
  );
}
