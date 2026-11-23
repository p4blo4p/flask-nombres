"""
build.py — Genera el sitio estático en la carpeta build/

Uso:
    python build.py

El resultado es una carpeta build/ con:
    build/index.html
    build/nombre/<slug>/index.html   (una carpeta por nombre, URLs limpias)
    build/sobre/index.html
    build/404.html
    build/sitemap.xml
    build/robots.txt
    build/static/...                 (CSS, JS, favicon copiados)

Para subir a GitHub Pages:
    - Opción A (manual): copia el contenido de build/ a la rama gh-pages
      o a la raíz si activas Pages sobre la rama main + carpeta /docs.
    - Opción B (automática): el workflow .github/workflows/deploy.yml
      ejecuta este build.py en cada push y publica build/ en Pages.

Notas técnicas:
    - Frozen-Flask congela cada ruta de app.py a un fichero HTML.
    - FREEZER_RELATIVE_URLS=True produce enlaces relativos, ideales
      para GitHub Pages (el sitio puede servirse desde un subdirectorio).
    - Las URLs /nombre/<slug> se convierten en /nombre/<slug>/index.html.
"""
import os
import shutil
import sys

# Importar la app y el freezer ya configurados en app.py
from app import app, freezer, CONFIG, BASE_DIR

BUILD_DIR = app.config["FREEZER_DESTINATION"]


def main():
    # Limpiar build anterior
    if os.path.isdir(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)

    print(f"→ Generando sitio estático en: {BUILD_DIR}")
    print(f"→ URLs relativas: {app.config['FREEZER_RELATIVE_URLS']}")
    print(f"→ Base URL configurada: {CONFIG['base_url']}")
    print()

    # Congelar
    freezer.freeze()

    # Copiar robots.txt como fichero plano (Frozen-Flask ya lo hace,
    # pero aseguramos que no tenga extensión rara)
    robots_path = os.path.join(BUILD_DIR, "robots.txt")
    if not os.path.exists(robots_path):
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(f"User-agent: *\nAllow: /\n\nSitemap: {CONFIG['base_url']}/sitemap.xml\n")

    # Estadísticas
    n_html = 0
    n_other = 0
    for root, _, files in os.walk(BUILD_DIR):
        for fn in files:
            if fn.endswith(".html"):
                n_html += 1
            else:
                n_other += 1
    size_kb = sum(
        os.path.getsize(os.path.join(r, f))
        for r, _, fs in os.walk(BUILD_DIR) for f in fs
    ) // 1024

    print()
    print("✓ Build completado")
    print(f"  Páginas HTML:  {n_html}")
    print(f"  Otros ficheros (CSS/JS/img/xml/txt): {n_other}")
    print(f"  Tamaño total:  {size_kb} KB")
    print()
    print("Próximos pasos:")
    print(f"  1. Abre build/index.html en tu navegador para verificar.")
    print(f"  2. Sube el contenido de build/ a GitHub Pages (o deja que")
    print(f"     el workflow .github/workflows/deploy.yml lo haga solo).")
    print(f"  3. Antes de publicar: pon tu ID de AdSense en")
    print(f"     templates/partials/adsense.html y tu URL en app.py (CONFIG.base_url).")


if __name__ == "__main__":
    sys.exit(main())
