/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        forest: '#064C35',
        deep: '#0A3323',
        lime: '#A7E84B',
        cream: '#F5F2E8',
        offwhite: '#FBFAF1',
        charcoal: '#263C32',
        sage: '#A6B69A',
      },
      fontFamily: {
        serif: ['"DM Serif Display"', '"Noto Serif Bengali"', 'Georgia', 'serif'],
        sans: ['Manrope', '"Noto Sans Bengali"', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        sway: {
          '0%,100%': { transform: 'rotate(-4deg)' },
          '50%': { transform: 'rotate(4deg)' },
        },
        grow: {
          '0%': { transform: 'scaleY(0.4)', opacity: '0.4' },
          '100%': { transform: 'scaleY(1)', opacity: '1' },
        },
      },
      animation: {
        'fade-up': 'fadeUp .6s cubic-bezier(.2,.7,.2,1) both',
        'fade-in': 'fadeIn .4s ease both',
        sway: 'sway 3.2s ease-in-out infinite',
        grow: 'grow 1.6s ease-in-out infinite alternate',
      },
    },
  },
  plugins: [],
}
