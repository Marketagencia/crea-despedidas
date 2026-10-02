#!/bin/bash
# Regenera css/tailwind.css (solo las utilidades Tailwind realmente usadas en el HTML/JS).
# Ejecutar desde la raíz del repo cada vez que se añadan clases Tailwind nuevas:
#   bash scripts/build_css.sh
cd "$(dirname "$0")/.." || exit 1
npx --yes tailwindcss@3.4.17 -c scripts/tailwind.config.js -i scripts/tailwind.input.css -o css/tailwind.css --minify
