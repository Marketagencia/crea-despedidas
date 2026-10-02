/** Configuración de Tailwind para compilar css/tailwind.css (ver scripts/build_css.sh).
 *  Sustituye al Play CDN (cdn.tailwindcss.com), que bloqueaba el render y compilaba en el navegador. */
module.exports = {
  content: ['./**/*.html', './js/**/*.js', '!./node_modules/**', '!./social/**'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Sora', 'system-ui', 'sans-serif'],
        sans: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: '#0B0B0F',
        surface: '#121218',
        neon: { cyan: '#00F2FE', blue: '#4FACFE', pink: '#FF2FB9', orange: '#FF7A18' },
      },
    },
  },
};
