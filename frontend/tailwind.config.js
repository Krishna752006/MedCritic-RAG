/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0a0f2c',
          800: '#111842',
          700: '#1a214d',
          600: '#232b5d',
        },
        cyan: {
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
        },
        medical: {
          primary: '#00d4ff',
          red: '#ff3b5c',
          green: '#10b981',
          bg: '#0a0f2c',
          card: '#12183d',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
