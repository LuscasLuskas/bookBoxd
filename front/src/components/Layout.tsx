import type { ReactNode } from 'react';
import Navbar from './Navbar';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-bb-dark">
      <Navbar />
      <main className="flex-1">{children}</main>
      <footer className="border-t border-bb-border mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between flex-wrap gap-2">
          <p className="text-bb-dim text-xs">
            © 2024 <span className="text-bb-muted">BookBoxd</span>
          </p>
          <p className="text-bb-dim text-xs italic">
            Track your reading. Share your passion.
          </p>
        </div>
      </footer>
    </div>
  );
}
