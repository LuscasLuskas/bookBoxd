/** Brand mark — a tiny three-book shelf. Used in the navbar and as the
 * landing-spot icon on the login page. Colors match the full Bookshelf on the
 * login hero, with amber as the centerpiece. */
export default function BookMark({
  size = 24,
  className = '',
}: {
  size?: number;
  className?: string;
}) {
  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      aria-hidden="true"
    >
      {/* Left book — purple */}
      <g>
        <rect x="6" y="14" width="24" height="76" rx="1.5" fill="#5b21b6" />
        <rect x="6" y="14" width="3" height="76" fill="#3b0f80" />
        <rect x="9" y="14" width="0.8" height="76" fill="#ffffff" opacity="0.15" />
        <rect x="12" y="32" width="12" height="2" fill="#fef3c7" opacity="0.6" />
      </g>

      {/* Center book — amber (brand), tallest */}
      <g>
        <rect x="36" y="6" width="28" height="84" rx="1.5" fill="#e8a000" />
        <rect x="36" y="6" width="3.5" height="84" fill="#b97c00" />
        <rect x="39.5" y="6" width="1" height="84" fill="#ffffff" opacity="0.2" />
        <rect x="42" y="26" width="16" height="2.5" fill="#fef3c7" opacity="0.85" />
        <rect x="44" y="32" width="12" height="1.5" fill="#fef3c7" opacity="0.6" />
        {/* Bookmark ribbon */}
        <path d="M54 6 L54 22 L58 19 L62 22 L62 6 Z" fill="#b14aed" />
      </g>

      {/* Right book — burgundy */}
      <g>
        <rect x="70" y="16" width="24" height="74" rx="1.5" fill="#991b1b" />
        <rect x="70" y="16" width="3" height="74" fill="#7f1d1d" />
        <rect x="73" y="16" width="0.8" height="74" fill="#ffffff" opacity="0.15" />
        <rect x="76" y="34" width="12" height="2" fill="#fef3c7" opacity="0.6" />
      </g>

      {/* Shelf plank */}
      <rect x="2" y="90" width="96" height="4" rx="1" fill="#78350f" />
      <rect x="2" y="93.5" width="96" height="1.5" fill="#451a03" />
    </svg>
  );
}
