/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bb: {
          dark: '#14181c',
          surface: '#1f2937',
          card: '#252d38',
          border: '#2d3748',
          accent: '#e8a000',
          'accent-dark': '#c67c00',
          text: '#cdd8e3',
          muted: '#87a5bb',
          dim: '#456070',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
