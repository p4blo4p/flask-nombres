"""
Significados de Nombres — aplicación Flask + generador de sitio estático.

ESTE ARCHIVO NO SE EDITA para cambiar el contenido ni el AdSense:
- Contenido: edita data/nombres.json (o añade más entradas).
- AdSense:   edita templates/partials/adsense.html (una sola vez, todas las páginas lo heredan).
- Datos del sitio (título, URL, autor): edita el bloque CONFIG aquí abajo.

Uso:
    python app.py                       # servidor de desarrollo en http://127.0.0.1:5000
    python build.py                     # genera la carpeta build/ con HTML estático para GitHub Pages
"""
import json
import os
from datetime import datetime
from flask import Flask, render_template, abort, send_from_directory, Response

# ────────────────────────────────────────────────────────────────────
# CONFIG  —  edita estos valores una sola vez
# ────────────────────────────────────────────────────────────────────
CONFIG = {
    "site_name":      "Significados de Nombres",
    "site_tagline":   "Origen, etimología y curiosidades de cada nombre",
    "base_url":       "https://TUARIO.github.io/significados-nombres",  # ← pon tu usuario/Repo
    "language":       "es",
    "author":         "Tu Nombre",
    "description":    "Diccionario de significados de nombres: origen, etimología, características, variantes y curiosidades de cada nombre.",
    # AdSense: solo se usa si templates/partials/adsense.html tiene tu ID.
    # El partial se incluye una vez en base.html y aparece en todas las páginas.
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "nombres.json")

app = Flask(__name__)
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_DESTINATION"] = os.path.join(BASE_DIR, "build")
app.config["FREEZER_IGNORE_404"] = False
app.jinja_env.add_extension("jinja2.ext.do")


def load_nombres():
    """Carga y normaliza los nombres desde el JSON."""
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    # Asegurar slug y orden alfabético
    for n in data:
        n.setdefault("slug", _slugify(n["nombre"]))
    data.sort(key=lambda x: x["nombre"].lower())
    return data


def _slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().replace(" ", "-").replace("ñ", "n")


NOMBRES = load_nombres()
NOMBRES_BY_SLUG = {n["slug"]: n for n in NOMBRES}


@app.context_processor
def inject_config():
    """Inyecta CONFIG y el año en todas las plantillas."""
    return {"cfg": CONFIG, "now": datetime.now(), "total_nombres": len(NOMBRES)}


# ────────────────────────────────────────────────────────────────────
# RUTAS
# ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Portada: listado alfabético de nombres + buscador."""
    # Agrupar por inicial
    grupos = {}
    for n in NOMBRES:
        inicial = n["nombre"][0].upper()
        grupos.setdefault(inicial, []).append(n)
    iniciales = sorted(grupos.keys())
    return render_template(
        "index.html",
        nombres=NOMBRES,
        grupos=grupos,
        iniciales=iniciales,
        titulo="Significados de nombres: origen y etimología",
        descripcion=CONFIG["description"],
    )


@app.route("/nombre/<slug>/")
def nombre(slug):
    """Página individual de un nombre."""
    n = NOMBRES_BY_SLUG.get(slug)
    if n is None:
        abort(404)
    # Nombres relacionados como objetos completos
    relacionados = []
    for r in n.get("relacionados", [])[:6]:
        # Buscar coincidencia por nombre (sin distinguir mayúsculas)
        match = next((x for x in NOMBRES if x["nombre"].lower() == r.lower()), None)
        if match:
            relacionados.append(match)
    # Relleno si no hay suficientes relacionados en el dataset
    if len(relacionados) < 3:
        for x in NOMBRES:
            if x["slug"] != slug and x not in relacionados:
                relacionados.append(x)
                if len(relacionados) >= 6:
                    break
    titulo = f"Significado del nombre {n['nombre']} — origen y etimología"
    descripcion = n.get("meta_description") or f"Significado del nombre {n['nombre']}: origen {n['origen']}, etimología y características."
    # Datos estructurados (JSON-LD) para SEO
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"Significado del nombre {n['nombre']}",
        "description": descripcion,
        "inLanguage": "es",
        "author": {"@type": "Person", "name": CONFIG["author"]},
        "publisher": {"@type": "Organization", "name": CONFIG["site_name"]},
        "about": {
            "@type": "Thing",
            "name": f"Nombre {n['nombre']}",
            "description": n["significado"],
        },
    }
    return render_template(
        "nombre.html",
        n=n,
        relacionados=relacionados,
        titulo=titulo,
        descripcion=descripcion,
        jsonld=json.dumps(jsonld, ensure_ascii=False),
    )


@app.route("/sobre/")
def sobre():
    """Página 'sobre' con explicación del proyecto."""
    return render_template(
        "sobre.html",
        titulo="Sobre este sitio",
        descripcion="Página sobre el proyecto Significados de Nombres.",
    )


@app.route("/sitemap.xml")
def sitemap():
    """Sitemap XML para Google Search Console."""
    urls = []
    lastmod = datetime.now().strftime("%Y-%m-%d")
    urls.append({"loc": CONFIG["base_url"] + "/", "priority": "1.0"})
    for n in NOMBRES:
        urls.append({
            "loc": CONFIG["base_url"] + "/nombre/" + n["slug"],
            "priority": "0.8",
        })
    body = render_template("sitemap.xml", urls=urls, lastmod=lastmod)
    return Response(body, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\n\nSitemap: {CONFIG['base_url']}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", titulo="Página no encontrada"), 404


# Ruta explícita para que Frozen-Flask genere build/404.html
# (GitHub Pages usa este fichero como página 404 personalizada).
@app.route("/404.html")
def error_page():
    return render_template("404.html", titulo="Página no encontrada")


# ────────────────────────────────────────────────────────────────────
# URL GENERATORS PARA FROZEN-FLASK  (necesario para que build.py congele
# todas las URLs dinámicas /nombre/<slug>)
# ────────────────────────────────────────────────────────────────────
from flask_frozen import Freezer
freezer = Freezer(app)


@freezer.register_generator
def nombre_pages():
    # Devuelve tuplas (endpoint, kwargs) para que Frozen-Flask no infiera
    # el endpoint del nombre de la función.
    for n in NOMBRES:
        yield ("nombre", {"slug": n["slug"]})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
