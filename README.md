# Crea Despedidas — Landing premium

Landing page moderna y disruptiva para la organización de despedidas de soltero/a
y eventos exclusivos. Estética *dark* con acentos de neón, Bento Grid,
glassmorphism, configurador interactivo y carrusel infinito de reseñas.

Contenido basado en la web actual **creadespedidas.com** (Valencia).

## Estructura

```
web crea despedidas/
├── index.html                                  # Home (una sola página con anclas)
├── restaurantes-despedidas-cumpleanos-valencia/
│   └── index.html                              # Subpágina · Restaurante Propio
├── experiencias-actividades-valencia/
│   └── index.html                              # Subpágina · Experiencias & Actividades
├── alojamientos-despedidas-valencia/
│   └── index.html                              # Subpágina · Alojamientos (buscador Booking)
├── traslados-valencia/
│   └── index.html                              # Subpágina · Traslados
├── css/
│   └── styles.css       # Estilos propios: neón, glass, animaciones, responsive
├── js/
│   └── main.js          # Microinteracciones en JS nativo (sin dependencias)
├── Logos/               # Logos originales de marca (fuente)
└── assets/              # logo.png (recoloreado) + fish.png (pez del cursor)
```

### Subpáginas de servicio

Comparten `css/styles.css` y `js/main.js` (rutas absolutas `/css`, `/js`, `/assets`).
El menú **Servicios** de la nav es un desplegable con las 4, y cada tarjeta del Bento
de la home enlaza a la suya (`.tile-cover`).

- **Alojamientos** incluye un buscador que envía a `booking.com/searchresults` con el
  `aid=304142` (cuenta de afiliado de Crea Despedidas). Si en el futuro usas el widget
  oficial de Booking, pega su código donde indica el comentario HTML.

### Secciones

| Sección           | Descripción |
|-------------------|-------------|
| **Hero**          | Título con *text-gradient* animado + 2 CTAs magnéticas ("Crea tu experiencia" / "Explorar destinos"). |
| **Bento Grid**    | Cuadrícula asimétrica: Destinos Top · Experiencias VIP · Alojamientos Exclusivos · Transporte de Lujo. *Spotlight* que sigue al cursor + borde degradado en hover. |
| **Fast Planner**  | Constructor real: tipo de evento (tarjetas) + nº de personas (slider) + control segmentado **"Elige un pack" / "A la carta"**. Modo pack: los 7 packs con precio/persona, selección única. Modo à la carte: chips multi-selección de actividades, comida, alojamiento y transporte. El resumen muestra el desglose, la estimación total en vivo y genera un enlace de WhatsApp con todo el detalle. |
| **Validación social** | Doble carrusel infinito (reseñas + actividades) en CSS puro, con pausa al pasar el cursor. |
| **Footer**        | Enlaces por columnas, iconos sociales, newsletter con validación y datos de contacto reales. |

## Cómo verlo

Es HTML estático: sirve la carpeta con cualquier servidor.

```bash
cd "web crea despedidas"
python3 -m http.server 8822
# abre http://localhost:8822
```

## Personalización rápida

- **Colores / tipografía:** tokens en `:root` dentro de `css/styles.css` y en el
  bloque `tailwind.config` de `index.html`.
- **Logo:** `assets/logo.png` (Logo 2026, recortado) en nav y footer, recoloreado a
  los cian/azul de la web con un filtro CSS (`sepia + hue-rotate + saturate`) en
  `.brand-logo`. Para dejarlo naranja original, quita ese `filter`.
- **Pez tras el cursor:** `assets/fish.png` (recorte del "logo PEZ 2026"), en su color
  original. Lo mueve `initFishCursor()` en `js/main.js` (estela con retardo, morro
  orientado a la dirección de nado, giro limitado para que nunca nade boca abajo).
  Se desactiva en móvil, puntero táctil y con `prefers-reduced-motion`.
- **Packs, actividades y precios del planner:** se definen en el HTML (`data-price`,
  `data-desc`, `data-cat` de cada `input`); `js/main.js` solo lee esos valores.
- **Teléfono de WhatsApp:** constante `WHATSAPP` en `js/main.js`.
- **Imágenes reales:** sustituir los fondos `.tile-media--*` por `<img>`/`<video>`
  dentro de cada `.bento-tile` y las reseñas por vídeos en las `.review-card`.

## Nota para producción

`index.html` carga **Tailwind por CDN (Play CDN)**, ideal para prototipar pero no
para producción. Antes de publicar:

```bash
npm install -D tailwindcss
npx tailwindcss init
npx tailwindcss -i ./css/tailwind.src.css -o ./css/tailwind.build.css --minify
```

…y reemplazar el `<script src="https://cdn.tailwindcss.com">` por el CSS compilado.

## Accesibilidad

- HTML semántico con *landmarks* (`header`, `main`, `nav`, `footer`, `address`).
- `:focus-visible` visible, *skip link*, `aria-label` en iconos, `aria-live` en el
  resumen del planner.
- Respeta `prefers-reduced-motion` (desactiva orbes, marquesinas y reveals).
- El contenido es visible sin JavaScript (los *reveals* solo se ocultan si hay JS).
