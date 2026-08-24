"""
Convierte trazas de busqueda en JSON, para alimentar el visualizador.

Los algoritmos no saben que existe esto: solo emiten eventos. Aca los
traducimos a un formato que puede leer cualquier renderer.
"""

from __future__ import annotations

import json

from best_first import ALGORITMOS, best_first_search
from romania import CARRETERAS, COORDENADAS, DISTANCIA_RECTA_A_BUCHAREST, ProblemaRuta
from traza import Evento, Extraer, Fallo, Generar, Inicio, Obsoleto, Solucion, resumen


def evento_a_dict(ev: Evento, arbol: dict[str, str]) -> dict:
    """Un evento como diccionario plano.

    `arbol` es el mapa hijo->padre de los nodos alcanzados hasta este
    momento; lo reconstruimos afuera del algoritmo para no ensuciar el
    codigo que se lee en clase.
    """
    d = {
        "tipo": type(ev).__name__.lower(),
        "paso": ev.paso,
        "texto": str(ev).replace("\n", "  "),
        "frontera": [[ciudad, v] for ciudad, v in ev.frontera],
        "alcanzados": ev.alcanzados,
        "arbol": [[padre, hijo] for hijo, padre in arbol.items() if padre],
    }
    nodo = getattr(ev, "nodo", None)
    if nodo is not None:
        d |= {
            "ciudad": nodo.estado,
            "g": nodo.costo_camino,
            "camino": nodo.camino(),
        }
    if isinstance(ev, (Inicio, Extraer, Generar)):
        d["f"] = ev.f
    if isinstance(ev, Generar):
        d["decision"] = ev.decision
        d["costo_previo"] = ev.costo_previo
    if isinstance(ev, Obsoleto):
        d["mejor"] = ev.mejor
    return d


def traza_a_dict(problema: ProblemaRuta, eventos) -> dict:
    """Recorre la traza rearmando el arbol de busqueda paso a paso."""
    arbol: dict[str, str | None] = {problema.inicio: None}
    salida, crudos = [], []

    for ev in eventos:
        # El arbol se actualiza ANTES de fotografiarlo cuando un hijo
        # entra o mejora: reached[s] <- child tambien cambia el padre.
        if isinstance(ev, Generar) and ev.decision != "descartado":
            arbol[ev.nodo.estado] = ev.nodo.padre.estado
        salida.append(evento_a_dict(ev, arbol))
        crudos.append(ev)

    return {"eventos": salida, "resumen": resumen(crudos)}


def exportar(problema: ProblemaRuta, algoritmos=ALGORITMOS) -> dict:
    return {
        "problema": {"inicio": problema.inicio, "objetivo": problema.objetivo},
        "ciudades": {c: list(xy) for c, xy in COORDENADAS.items()},
        "carreteras": [[a, b, km] for a, b, km in CARRETERAS],
        "heuristica": DISTANCIA_RECTA_A_BUCHAREST,
        "algoritmos": [
            {"nombre": nombre,
             **traza_a_dict(problema, best_first_search(problema, factory(problema)))}
            for nombre, factory in algoritmos.items()
        ],
    }


if __name__ == "__main__":
    from romania import arad_a_bucharest

    datos = exportar(arad_a_bucharest())
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    with open("datos.json", "w", encoding="utf-8") as fh:
        fh.write(texto)
    print(f"datos.json: {len(texto) / 1024:.1f} KB")
    for a in datos["algoritmos"]:
        print(f"  {a['nombre']:<26} {len(a['eventos'])} eventos, "
              f"costo {a['resumen']['costo']:g}")
