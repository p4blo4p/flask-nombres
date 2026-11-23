# Significados de Nombres — generador de sitio estático con Flask

Plantilla lista para producir un sitio web estático (HTML + CSS + JS) que se
sirve gratis desde **GitHub Pages**, con **AdSense** configurado en un único
punto y contenido generado a partir de un JSON.

Pensado para que una sola persona pueda lanzar y monetizar un nicho de tipo
«diccionario de nombres» en una tarde, y escalarlo a cientos de páginas
simplemente añadiendo entradas a un archivo de datos.

---

## Qué incluye

```
significados-nombres/
├── app.py                     # App Flask (servidor de desarrollo + rutas)
├── build.py                   # Genera build/ estático con Frozen-Flask
├── requirements.txt           # Dependencias: Flask + Frozen-Flask
├── data/
│   └── nombres.json           # 53 nombres de muestra (añade los que quieras)
├── templates/
│   ├── base.html              # Esqueleto: head, header, footer, anuncio global
│   ├── index.html             # Portada: listado + buscador + índice A-Z
│   ├── nombre.html            # Página individual de cada nombre
│   ├── sobre.html             # Página «sobre»
│   ├── 404.html               # Página de error
│   ├── sitemap.xml            # Plantilla del sitemap
│   └── partials/
│       ├── adsense.html       # ★ ADSENSE: se edita UNA sola vez aquí ★
│       ├── header.html        # Cabecera del sitio
│       └── footer.html        # Pie del sitio
├── static/
│   ├── css/styles.css         # Hoja de estilo única, mobile-first
│   ├── js/main.js             # Buscador en cliente (sin servidor)
│   └── img/favicon.svg
└── .github/workflows/deploy.yml  # Autodespliegue a GitHub Pages
```

---

## Quickstart (3 pasos)

### 1. Desarrollo local

```bash
pip install -r requirements.txt
python app.py
# Abre http://127.0.0.1:5000
```

Cualquier cambio en plantillas o `data/nombres.json` se ve al refrescar.

### 2. Generar el sitio estático

```bash
python build.py
```

Se crea la carpeta `build/` con todo el HTML/CSS/JS listo. Ábrela con:

```bash
# macOS:    open build/index.html
# Linux:    xdg-open build/index.html
```

### 3. Subir a GitHub Pages

**Opción A — automática (recomendada):**

1. Crea un repo en GitHub (por ejemplo `significados-nombres`).
2. Sube este proyecto a la rama `main`:
   ```bash
   git init
   git add .
   git commit -m "Sitio inicial"
   git branch -M main
   git remote add origin https://github.com/TUARIO/significados-nombres.git
   git push -u origin main
   ```
3. En GitHub → **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. El workflow `.github/workflows/deploy.yml` se ejecuta en cada push y publica
   el sitio en `https://TUARIO.github.io/significados-nombres`.

**Opción B — manual:** copia el contenido de `build/` a la rama `gh-pages` y
configura Pages sobre esa rama.

---

## Configuración (una vez, antes de publicar)

Hay **solo dos sitios que tocar** para personalizar el proyecto:

### A. Tu ID de AdSense — `templates/partials/adsense.html`

```jinja
{% set ADSENSE_ENABLED = true %}
{% set PUB_ID = "ca-pub-0000000000000000" %}   ← pon aquí tu ID real
```

El partial define dos macros (`head()` y `unit()`) que se usan desde
`base.html` y desde las páginas individuales. **Cualquier página generada
hereda automáticamente el AdSense** sin que tengas que tocar nada más.

Para desactivarlo en pruebas, pon `ADSENSE_ENABLED = false`.

### B. URL y datos del sitio — `app.py` (bloque `CONFIG`)

```python
CONFIG = {
    "site_name":  "Significados de Nombres",
    "base_url":   "https://TUARIO.github.io/significados-nombres",  # ← tu URL
    "author":     "Tu Nombre",
    ...
}
```

`base_url` se usa en el `sitemap.xml`, `robots.txt`, `canonical` y Open Graph.
Pon la URL final que tendrá el sitio en GitHub Pages.

---

## Cómo añadir contenido

Edita `data/nombres.json`. Cada entrada es un objeto:

```json
{
  "nombre": "Lucía",
  "genero": "F",
  "origen": "latino",
  "significado": "«la que lleva la luz»",
  "etimologia": "Del latín Lucia, derivado de lux (luz).",
  "dia_onomastico": "13 de diciembre",
  "variantes": ["Lucy", "Lucie", "Luzia"],
  "caracteristicas": ["Alegre", "Vital", "Optimista"],
  "famosos": ["Lucía Lacarra (bailarina)"],
  "relacionados": ["Luz", "Lucero"],
  "curiosidad": "En Suecia, el 13 de diciembre se celebra...",
  "meta_description": "Significado del nombre Lucía: origen latino, etimología...",
  "meta_keywords": "significado Lucía, nombre Lucía, origen Lucía"
}
```

Tras añadir entradas, ejecuta `python build.py` y se generan todas las páginas
nuevas. El `slug` se genera automáticamente desde el `nombre`.

**El sistema vale para cualquier temática**, no solo nombres: cambia el
`nombres.json` por `recetas.json`, `ciudades.json`, `criptomonedas.json`…
y adapta las plantillas `index.html` y `nombre.html` al nuevo contenido.

---

## SEO incluido

- **Sitemap.xml** automático con todas las URLs.
- **robots.txt** que apunta al sitemap.
- **Meta description** y **Open Graph** por página.
- **JSON-LD** (datos estructurados `Article`) en cada página de nombre.
- **Canonical** absoluto en cada página.
- **Breadcrumbs** y **FAQ** con `<details>` (bueno para AI Overview).
- **Enlazado interno** automático entre nombres relacionados.
- **HTML semántico** (`<article>`, `<nav>`, `<section>`, `<header>`, `<footer>`).
- **Lighthouse-friendly**: CSS y JS mínimos, sin frameworks, mobile-first.

Tras el primer deploy, registra el sitio en **Google Search Console** y envía
el sitemap: `https://TUARIO.github.io/significados-nombres/sitemap.xml`.

---

## AdSense: cuándo y cómo

1. **No solicites AdSense hasta tener contenido:** Google exige un sitio con
   contenido original y navegación clara. Con ~50 nombres ya es suficiente.
2. Sustituye `PUB_ID` en `templates/partials/adsense.html` por tu ID.
3. Tras aprobar la cuenta, crea un bloque de anuncio **automático** (auto ads)
   y opcionalmente bloques manuales. Los `unit()` ya están puestos en
   posiciones estratégicas (cabecera de cada nombre, mitad del contenido y pie
   global).
4. Cuando superes 10 000 visitas/mes, evalúa migrar a Ezoic (+50 % RPM).

---

## Stack y costes

- **Flask 3 + Frozen-Flask**: generación estática en Python, sin JS de build.
- **Hosting**: GitHub Pages, 0 €/año.
- **Dominio**: 10-15 €/año (opcional; el `*.github.io` es gratis).
- **SSL**: incluido en GitHub Pages.
- **Total Año 1**: 0 € si usas el subdominio de GitHub, 12 € con dominio propio.

---

## Licencia y fuentes

- **Código**: MIT (libre para usar y modificar).
- **Contenido de muestra** (etimologías): basado en obras de referencia
  estándar de antroponimía. Las «características» asociadas a cada nombre son
  tradiciones populares, **no afirmaciones psicológicas** verificadas.
  Revisa y amplía cada entrada antes de publicar en producción.
