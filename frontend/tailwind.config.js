/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        retail: {
          lider: '#0071CE',
          jumbo: '#00A859',
          santaisabel: '#E31837',
          unimarc: '#E30613'
        }
      }
    },
  },
  plugins: [],
}
