module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef4ff',
          100: '#d9e2ff',
          200: '#b6c8ff',
          300: '#91aaff',
          400: '#6b8cff',
          500: '#4c6bff',
          600: '#3451e6',
          700: '#263cc4',
          800: '#1a2899',
          900: '#121d73'
        }
      },
      fontFamily: {
        sans: ['"Tajawal"', 'ui-sans-serif', 'system-ui']
      }
    }
  },
  plugins: []
};
