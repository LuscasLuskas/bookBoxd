import { useState } from 'react';

const STAR_PATH =
  'M12 .587l3.668 7.431 8.2 1.192-5.934 5.784 1.401 8.169L12 18.896l-7.335 3.867 1.401-8.169L.132 9.21l8.2-1.192z';

interface Props {
  /** Current rating, 0.5–5.0 in half steps, or null when unrated. */
  value: number | null;
  /** Omit (or pass readOnly) to render a static display. */
  onChange?: (value: number | null) => void;
  readOnly?: boolean;
  /** Star size in pixels. */
  size?: number;
  disabled?: boolean;
}

/**
 * Five-star rating with half-star precision. Hovering the left/right half of
 * a star previews x.5 / x.0; clicking commits it. Clicking the current value
 * again clears the rating (passes null to onChange).
 */
export default function StarRating({
  value,
  onChange,
  readOnly = false,
  size = 20,
  disabled = false,
}: Props) {
  const [hover, setHover] = useState<number | null>(null);
  const interactive = !readOnly && !disabled && !!onChange;
  const display = hover ?? value ?? 0;

  const pick = (next: number) => {
    if (!onChange) return;
    onChange(value === next ? null : next);
  };

  return (
    <div
      className="inline-flex items-center gap-0.5"
      onMouseLeave={() => setHover(null)}
    >
      {[1, 2, 3, 4, 5].map((i) => {
        const fill = Math.max(0, Math.min(1, display - (i - 1)));
        return (
          <div
            key={i}
            className="relative"
            style={{ width: size, height: size }}
          >
            <svg
              viewBox="0 0 24 24"
              className="absolute inset-0 h-full w-full fill-bb-dim/40"
            >
              <path d={STAR_PATH} />
            </svg>
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ width: `${fill * 100}%` }}
            >
              <svg
                viewBox="0 0 24 24"
                className="h-full fill-bb-accent"
                style={{ width: size }}
              >
                <path d={STAR_PATH} />
              </svg>
            </div>
            {interactive && (
              <>
                <button
                  type="button"
                  aria-label={`Rate ${i - 0.5} stars`}
                  className="absolute inset-y-0 left-0 z-10 w-1/2 cursor-pointer"
                  onMouseEnter={() => setHover(i - 0.5)}
                  onClick={() => pick(i - 0.5)}
                />
                <button
                  type="button"
                  aria-label={`Rate ${i} stars`}
                  className="absolute inset-y-0 right-0 z-10 w-1/2 cursor-pointer"
                  onMouseEnter={() => setHover(i)}
                  onClick={() => pick(i)}
                />
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}
