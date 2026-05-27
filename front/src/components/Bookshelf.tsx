/** Animated bookshelf for the login hero.
 *
 * Each book sits on a shelf and stays still most of the time. On its own slow
 * cycle (offset so they don't fall together), a single book wobbles, tips
 * forward off the shelf, pauses out of view, then springs back into place.
 *
 * When `flying` is true, the whole shelf scales down and translates toward the
 * navbar — used by the login → app transition.
 */

type Book = { w: number; h: number; color: string; accent: string };

// Muted library palette — warm tones with a few cool counterpoints. Sizes vary
// a few pixels so it reads like real books, not identical tiles.
const BOOKS: Book[] = [
  { w: 16, h: 90, color: '#5b21b6', accent: '#3b0f80' },
  { w: 13, h: 82, color: '#991b1b', accent: '#7f1d1d' },
  { w: 18, h: 96, color: '#e8a000', accent: '#b97c00' },
  { w: 12, h: 78, color: '#15803d', accent: '#0f5c2c' },
  { w: 15, h: 86, color: '#1e40af', accent: '#1e3a8a' },
  { w: 17, h: 94, color: '#d97706', accent: '#92400e' },
  { w: 14, h: 84, color: '#1c1917', accent: '#0c0a09' },
];

function SpineBook({ w, h, color, accent }: Book) {
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width={w} height={h} aria-hidden="true">
      <rect x="0" y="0" width={w} height={h} rx="1" fill={color} />
      <rect x="0" y="0" width="2.5" height={h} fill={accent} />
      <rect x="2.5" y="0" width="0.6" height={h} fill="#ffffff" opacity="0.18" />
      {/* Title bands */}
      <rect
        x={w * 0.25}
        y={h * 0.22}
        width={w * 0.5}
        height="1.5"
        fill="#fef3c7"
        opacity="0.7"
      />
      <rect
        x={w * 0.3}
        y={h * 0.3}
        width={w * 0.4}
        height="1"
        fill="#fef3c7"
        opacity="0.45"
      />
      {/* Author band near the bottom */}
      <rect
        x={w * 0.3}
        y={h * 0.82}
        width={w * 0.4}
        height="0.8"
        fill="#fef3c7"
        opacity="0.35"
      />
    </svg>
  );
}

export default function Bookshelf({ flying = false }: { flying?: boolean }) {
  return (
    <div
      className={`relative inline-block ${flying ? 'shelf-fly-home' : ''}`}
      style={{ width: 'fit-content' }}
    >
      {/* Soft glow behind the shelf */}
      <div
        className="absolute inset-0 -inset-x-6 -top-4 blur-2xl opacity-40 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 50% 50%, rgba(232,160,0,0.4), transparent 70%)',
        }}
      />

      {/* The books, standing on the shelf */}
      <div
        className="relative flex items-end justify-center gap-[2px] h-[100px] px-1"
      >
        {BOOKS.map((b, i) => (
          <div
            key={i}
            className={flying ? '' : 'shelf-book'}
            style={{
              transformOrigin: 'bottom center',
              // Spread the falls out so only one book moves at a time.
              animationDelay: `${2 + i * 8}s`,
            }}
          >
            <SpineBook {...b} />
          </div>
        ))}
      </div>

      {/* Shelf plank */}
      <div className="relative h-[5px] bg-gradient-to-b from-amber-900 to-stone-950 rounded-sm shadow-[0_2px_6px_rgba(0,0,0,0.5)]" />
      {/* Plank under-shadow */}
      <div
        className="mx-2 h-[6px] mt-[1px] rounded-full opacity-60"
        style={{ background: 'radial-gradient(ellipse 80% 100% at 50% 0%, rgba(0,0,0,0.6), transparent 70%)' }}
      />

      <style>{`
        @keyframes shelfFall {
          0%, 93% {
            transform: rotate(0deg) translateY(0);
            opacity: 1;
          }
          93.5% { transform: rotate(-3deg) translateY(0); }
          94% { transform: rotate(2deg) translateY(0); }
          94.5% { transform: rotate(-4deg) translateY(0); }
          95.5% {
            transform: rotate(70deg) translateY(20px);
            opacity: 1;
          }
          96.5% {
            transform: rotate(95deg) translateY(60px);
            opacity: 0.5;
          }
          97% {
            transform: rotate(95deg) translateY(80px);
            opacity: 0;
          }
          98% {
            transform: rotate(95deg) translateY(80px);
            opacity: 0;
          }
          98.5% {
            transform: rotate(-8deg) translateY(-4px);
            opacity: 1;
          }
          99.3% {
            transform: rotate(3deg) translateY(0);
          }
          100% {
            transform: rotate(0deg) translateY(0);
            opacity: 1;
          }
        }
        .shelf-book {
          animation: shelfFall 56s ease-in-out infinite;
        }
        @keyframes shelfFlyHome {
          0% { transform: translate(0, 0) scale(1) rotate(0deg); opacity: 1; }
          40% { transform: translate(0, -12px) scale(1.04) rotate(-2deg); opacity: 1; }
          100% {
            transform: translate(calc(-50vw + 90px), calc(-50vh + 60px)) scale(0.18) rotate(0deg);
            opacity: 0.85;
          }
        }
        .shelf-fly-home {
          animation: shelfFlyHome 720ms cubic-bezier(0.55, 0.05, 0.35, 1) forwards;
          transform-origin: 50% 50%;
        }
      `}</style>
    </div>
  );
}
