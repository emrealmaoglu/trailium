/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui', 'Arial'],
      },
      colors: {
        brand: {
          gray:      '#5d6675',   // subtitle
          black:     '#0f1720',   // title (koyu lacivert ton)
          grayLight: '#eef1f5',   // border yüzey
          gray2:     '#667a8d',   // yardımcı metin
          purple:    '#5f37d2',   // primary
        },
      },
      boxShadow: {
        card: '0 1px 3px rgba(16,24,40,.08), 0 1px 2px rgba(16,24,40,.06)',
      },
      borderRadius: {
        '2xl': '1rem',
      },
    },
  },
  plugins: [],
}
