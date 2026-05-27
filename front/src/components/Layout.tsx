import type { ReactNode } from 'react';
import Navbar from './Navbar';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen flex flex-col bg-black overflow-x-hidden">
      {/* Amber spotlight from top — same as login */}
      <div
        className="fixed inset-x-0 top-0 h-screen pointer-events-none z-0"
        style={{
          background:
            'radial-gradient(ellipse 90% 60% at 50% -5%, rgba(232,160,0,0.18) 0%, rgba(232,160,0,0.05) 35%, rgba(0,0,0,0) 65%)',
        }}
      />
      {/* Warm floor glow at the bottom of the viewport */}
      <div
        className="fixed inset-x-0 bottom-0 h-1/3 pointer-events-none z-0"
        style={{
          background:
            'radial-gradient(ellipse 80% 100% at 50% 110%, rgba(232,160,0,0.10) 0%, rgba(0,0,0,0) 70%)',
        }}
      />
      {/* Faint amber grid, masked into the center */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.05] z-0"
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

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-bb-accent/10 mt-16">
          <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between flex-wrap gap-2">
            <p className="text-neutral-600 text-xs">
              © 2026 <span className="text-neutral-500">bookboxd</span>
            </p>
            <p className="text-bb-accent/70 text-xs italic tracking-wide">
              For people who read.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
