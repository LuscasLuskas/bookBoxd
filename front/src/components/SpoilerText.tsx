import { useState, type ReactNode } from 'react';

interface Props {
  /** Raw text with ||...|| segments marking spoilers. */
  text: string;
  className?: string;
}

// /text/ marks a spoiler. Guards keep URLs (https://…/path/) and fractions
// (1/2) from matching: opening / can't follow a word char, colon, dot or
// slash, and closing / can't precede a word char.
const SPOILER_RE = /(?<![\w:./])\/([^/\n]+?)\/(?!\w)/g;

/**
 * Renders text with /spoiler/ segments blurred until clicked.
 * Newlines outside spoiler markers are preserved by whitespace-pre-wrap.
 */
export default function SpoilerText({ text, className }: Props) {
  const parts: ReactNode[] = [];
  let lastIndex = 0;
  let i = 0;
  for (const match of text.matchAll(SPOILER_RE)) {
    const start = match.index ?? 0;
    if (start > lastIndex) {
      parts.push(text.slice(lastIndex, start));
    }
    parts.push(<Spoiler key={i++} content={match[1]} />);
    lastIndex = start + match[0].length;
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }
  return (
    <span className={`whitespace-pre-wrap ${className ?? ''}`}>{parts}</span>
  );
}

function Spoiler({ content }: { content: string }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <button
      type="button"
      onClick={(e) => {
        // Don't let the click bubble to a clickable ancestor (e.g. a thread row).
        e.stopPropagation();
        setRevealed((v) => !v);
      }}
      title={revealed ? 'Click to hide spoiler' : 'Click to reveal spoiler'}
      className={`mx-0.5 px-1 rounded transition-all align-baseline text-left ${
        revealed
          ? 'bg-bb-surface text-bb-text'
          : 'bg-bb-text/15 text-transparent select-none [text-shadow:0_0_8px_rgba(255,255,255,0.45)] hover:bg-bb-text/20 cursor-pointer'
      }`}
    >
      {content}
    </button>
  );
}
