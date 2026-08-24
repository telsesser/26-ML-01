"""
Genera el visualizador HTML: mete la traza JSON adentro de la plantilla.

El resultado es un unico archivo autocontenido, sin servidor ni CDN:
se abre con doble click o se comparte a los alumnos.

Uso:  uv run visualizador.py
"""

import json
from pathlib import Path

from exportar import exportar
from romania import arad_a_bucharest

AQUI = Path(__file__).parent


def construir(problema, plantilla="plantilla.html", salida="visualizador.html"):
    datos = exportar(problema)
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    html = (AQUI / plantilla).read_text(encoding="utf-8")
    if "/*__DATOS__*/ null" not in html:
        raise SystemExit(f"{plantilla}: falta el marcador /*__DATOS__*/ null")
    html = html.replace("/*__DATOS__*/ null", texto)
    destino = AQUI / salida
    destino.write_text(html, encoding="utf-8")
    return destino


if __name__ == "__main__":
    destino = construir(arad_a_bucharest())
    print(f"{destino.name}: {destino.stat().st_size / 1024:.0f} KB")
