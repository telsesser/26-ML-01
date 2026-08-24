"""
Mapa de Rumania - Russell & Norvig, capitulo 3 (figura 3.1 / 3.2).

Modelo del grafo y del problema de busqueda. Sin dependencias externas:
todo lo que hay aca es Python puro para que se pueda leer en clase.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# --------------------------------------------------------------------------
# 1. Los datos del mapa
# --------------------------------------------------------------------------

# Aristas: (ciudad_a, ciudad_b, costo_en_km). El grafo es NO dirigido:
# cada arista se puede recorrer en los dos sentidos.
CARRETERAS: list[tuple[str, str, int]] = [
    ("Oradea",         "Zerind",         71),
    ("Oradea",         "Sibiu",         151),
    ("Zerind",         "Arad",           75),
    ("Arad",           "Sibiu",         140),
    ("Arad",           "Timisoara",     118),
    ("Timisoara",      "Lugoj",         111),
    ("Lugoj",          "Mehadia",        70),
    ("Mehadia",        "Drobeta",        75),
    ("Drobeta",        "Craiova",       120),
    ("Craiova",        "Rimnicu Vilcea", 146),
    ("Craiova",        "Pitesti",       138),
    ("Rimnicu Vilcea", "Sibiu",          80),
    ("Rimnicu Vilcea", "Pitesti",        97),
    ("Sibiu",          "Fagaras",        99),
    ("Fagaras",        "Bucharest",     211),
    ("Pitesti",        "Bucharest",     101),
    ("Bucharest",      "Giurgiu",        90),
    ("Bucharest",      "Urziceni",       85),
    ("Urziceni",       "Hirsova",        98),
    ("Hirsova",        "Eforie",         86),
    ("Urziceni",       "Vaslui",        142),
    ("Vaslui",         "Iasi",           92),
    ("Iasi",           "Neamt",          87),
]

# Distancia en linea recta a Bucharest (figura 3.22 del libro).
# Esta es la heuristica h(n) que usan greedy best-first y A*.
# OJO: es un dato *externo* al grafo. El agente lo sabe de antemano
# (mira un mapa, conoce las coordenadas), no lo deduce de las carreteras.
DISTANCIA_RECTA_A_BUCHAREST: dict[str, int] = {
    "Arad": 366,
    "Bucharest": 0,
    "Craiova": 160,
    "Drobeta": 242,
    "Eforie": 161,
    "Fagaras": 176,
    "Giurgiu": 77,
    "Hirsova": 151,
    "Iasi": 226,
    "Lugoj": 244,
    "Mehadia": 241,
    "Neamt": 234,
    "Oradea": 380,
    "Pitesti": 100,
    "Rimnicu Vilcea": 193,
    "Sibiu": 253,
    "Timisoara": 329,
    "Urziceni": 80,
    "Vaslui": 199,
    "Zerind": 374,
}

# Posicion de cada ciudad en el mapa (x crece hacia el este, y hacia el norte).
# Solo se usa para dibujar; los algoritmos no las miran.
COORDENADAS: dict[str, tuple[int, int]] = {
    "Arad": (91, 492),
    "Bucharest": (400, 327),
    "Craiova": (253, 288),
    "Drobeta": (165, 299),
    "Eforie": (562, 293),
    "Fagaras": (305, 449),
    "Giurgiu": (375, 270),
    "Hirsova": (534, 350),
    "Iasi": (473, 506),
    "Lugoj": (165, 379),
    "Mehadia": (168, 339),
    "Neamt": (406, 537),
    "Oradea": (131, 571),
    "Pitesti": (320, 368),
    "Rimnicu Vilcea": (233, 410),
    "Sibiu": (207, 457),
    "Timisoara": (94, 410),
    "Urziceni": (456, 350),
    "Vaslui": (509, 444),
    "Zerind": (108, 531),
}


# --------------------------------------------------------------------------
# 2. El grafo
# --------------------------------------------------------------------------

class Grafo:
    """Grafo no dirigido con pesos en las aristas."""

    def __init__(self, aristas: list[tuple[str, str, int]]):
        self._vecinos: dict[str, dict[str, int]] = {}
        for a, b, costo in aristas:
            self._vecinos.setdefault(a, {})[b] = costo
            self._vecinos.setdefault(b, {})[a] = costo

    @property
    def nodos(self) -> list[str]:
        return sorted(self._vecinos)

    def vecinos(self, ciudad: str) -> dict[str, int]:
        """{ciudad_vecina: costo}. Ordenado alfabeticamente para que el
        recorrido sea determinista y reproducible en clase."""
        return dict(sorted(self._vecinos[ciudad].items()))

    def costo(self, a: str, b: str) -> int:
        return self._vecinos[a][b]

    def aristas(self) -> list[tuple[str, str, int]]:
        """Cada arista una sola vez, en orden estable."""
        vistas = set()
        salida = []
        for a in self.nodos:
            for b, c in self.vecinos(a).items():
                if (b, a) not in vistas:
                    vistas.add((a, b))
                    salida.append((a, b, c))
        return salida

    def __len__(self) -> int:
        return len(self._vecinos)

    def __contains__(self, ciudad: str) -> bool:
        return ciudad in self._vecinos


# --------------------------------------------------------------------------
# 3. El nodo del arbol de busqueda
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Nodo:
    """Un nodo del arbol de busqueda (seccion 3.3.1).

    No confundir con una ciudad: la misma ciudad puede aparecer en varios
    nodos, alcanzada por caminos distintos y con distinto costo. Esa
    distincion es la que hace falta para entender por que existe el
    conjunto de explorados.
    """
    estado: str                      # la ciudad
    padre: "Nodo | None" = None      # de donde vinimos
    costo_camino: float = 0.0        # g(n): costo acumulado desde el inicio
    profundidad: int = 0             # cantidad de acciones desde el inicio

    def camino(self) -> list[str]:
        """La secuencia de ciudades desde el inicio hasta aca."""
        nodo, ruta = self, []
        while nodo is not None:
            ruta.append(nodo.estado)
            nodo = nodo.padre
        return list(reversed(ruta))

    def __repr__(self) -> str:
        return f"<Nodo {self.estado} g={self.costo_camino:g} d={self.profundidad}>"


# --------------------------------------------------------------------------
# 4. El problema
# --------------------------------------------------------------------------

@dataclass
class ProblemaRuta:
    """Problema de busqueda: llegar de `inicio` a `objetivo` en `grafo`.

    Es la interfaz que van a consumir TODOS los algoritmos. Ninguno de
    ellos conoce Rumania: solo saben pedir estado_inicial, es_objetivo()
    y expandir(). Cambiando esta clase, los mismos algoritmos resuelven
    el 8-puzzle o el laberinto.
    """
    grafo: Grafo
    inicio: str
    objetivo: str
    heuristica: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        for ciudad in (self.inicio, self.objetivo):
            if ciudad not in self.grafo:
                raise ValueError(f"{ciudad!r} no esta en el mapa")

    @property
    def estado_inicial(self) -> Nodo:
        return Nodo(self.inicio)

    def es_objetivo(self, estado: str) -> bool:
        return estado == self.objetivo

    def acciones(self, estado: str) -> list[str]:
        """Las ciudades a las que se puede ir desde `estado`."""
        return list(self.grafo.vecinos(estado))

    def costo_accion(self, desde: str, hacia: str) -> int:
        return self.grafo.costo(desde, hacia)

    def expandir(self, nodo: Nodo) -> list[Nodo]:
        """Genera los hijos de `nodo`. El corazon de cualquier busqueda."""
        return [
            Nodo(
                estado=vecino,
                padre=nodo,
                costo_camino=nodo.costo_camino + costo,
                profundidad=nodo.profundidad + 1,
            )
            for vecino, costo in self.grafo.vecinos(nodo.estado).items()
        ]

    def h(self, estado: str) -> float:
        """Heuristica: costo estimado desde `estado` hasta el objetivo."""
        return self.heuristica.get(estado, 0)


# --------------------------------------------------------------------------
# 5. Atajos para la clase
# --------------------------------------------------------------------------

RUMANIA = Grafo(CARRETERAS)


def arad_a_bucharest() -> ProblemaRuta:
    """El problema canonico del capitulo 3."""
    return ProblemaRuta(
        grafo=RUMANIA,
        inicio="Arad",
        objetivo="Bucharest",
        heuristica=DISTANCIA_RECTA_A_BUCHAREST,
    )


def costo_del_camino(grafo: Grafo, ciudades: list[str]) -> int:
    """Suma los costos de una ruta dada como lista de ciudades."""
    return sum(grafo.costo(a, b) for a, b in zip(ciudades, ciudades[1:]))


# --------------------------------------------------------------------------
# 6. Chequeos de sanidad (se corren con: python3 romania.py)
# --------------------------------------------------------------------------

if __name__ == "__main__":
    g = RUMANIA
    print(f"{len(g)} ciudades, {len(g.aristas())} carreteras\n")

    # Toda ciudad tiene heuristica y coordenadas.
    faltan_h = set(g.nodos) - set(DISTANCIA_RECTA_A_BUCHAREST)
    faltan_xy = set(g.nodos) - set(COORDENADAS)
    assert not faltan_h, f"sin heuristica: {faltan_h}"
    assert not faltan_xy, f"sin coordenadas: {faltan_xy}"

    # El grafo es conexo (si no, hay problemas sin solucion).
    vistos, pila = set(), ["Arad"]
    while pila:
        c = pila.pop()
        if c not in vistos:
            vistos.add(c)
            pila.extend(g.vecinos(c))
    assert vistos == set(g.nodos), f"desconectadas: {set(g.nodos) - vistos}"
    print("grafo conexo y datos completos")

    # La heuristica es admisible: h(n) nunca sobreestima el costo real.
    # Condicion necesaria para que A* con busqueda en arbol sea optimo.
    # Version debil pero suficiente para clase: h(a) - h(b) <= costo(a,b)
    # (consistencia), que implica admisibilidad.
    for a, b, costo in g.aristas():
        d = abs(DISTANCIA_RECTA_A_BUCHAREST[a] - DISTANCIA_RECTA_A_BUCHAREST[b])
        assert d <= costo, f"heuristica inconsistente en {a}-{b}: {d} > {costo}"
    print("heuristica consistente (y por lo tanto admisible)")

    # El camino optimo conocido del libro.
    optimo = ["Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"]
    print(f"\noptimo: {' -> '.join(optimo)} = {costo_del_camino(g, optimo)} km")

    # El camino que encuentra greedy best-first (mas corto en saltos, peor).
    goloso = ["Arad", "Sibiu", "Fagaras", "Bucharest"]
    print(f"goloso: {' -> '.join(goloso)} = {costo_del_camino(g, goloso)} km")

    # Un paso de expansion, para mostrar la estructura Nodo.
    p = arad_a_bucharest()
    raiz = p.estado_inicial
    print(f"\nexpandir {raiz}:")
    for hijo in p.expandir(raiz):
        print(f"   {hijo}  h={p.h(hijo.estado):3g}  f={hijo.costo_camino + p.h(hijo.estado):g}")
