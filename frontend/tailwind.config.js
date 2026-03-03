/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        table: '#0b3b2e',
        felt: '#0f5132',
        chip: {
          red: '#c0392b',
          blue: '#2980b9',
          green: '#27ae60',
          yellow: '#f1c40f',
        },
      },
    },
  },
  plugins: [],
};
