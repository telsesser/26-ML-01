"""
El view web.

Graba lo que va haciendo un algoritmo de busqueda y despues escribe una
pagina HTML que se recorre paso a paso. No cambia nada del algoritmo:
es el mismo objeto narrador que view.Silent, pero que en vez de
descartar los avisos los guarda.

Sirve para los cinco algoritmos. Lo unico que cambia entre ellos:

    best-first      reached es un dict estado -> nodo
    breadth-first   reached es un conjunto de estados
    depth-first     no hay reached
    prof. iterativa igual que depth-first, pero en varias vueltas
    bidireccional   dos reached: el del lado que trabaja y el del otro
"""

import json
import webbrowser
from pathlib import Path

from node import depth, path_states
from view import Silent

PLANTILLA = Path(__file__).with_name("plantilla.html")


class Web(Silent):
    """Graba un cuadro por cada vuelta del while: un POP y sus hijos.

    `key` es el numero que ordena la frontera: f(n) en best-first,
    la profundidad en breadth-first y depth-first.
    """

    def __init__(self, problem, name, label, key, key_name="f"):
        self.problem = problem
        self.name = name
        self.label = label
        self.key = key
        self.key_name = key_name
        self.frames = []
        self.node = None
        self.children = []
        self.note = None
        self.pops = 0  # cuantos nodos se expandieron en total
        self.round = None  # que vuelta es esta, si el algoritmo da vueltas
        self.others = None  # los estados del otro lado, en bidireccional
        self.ids = {}  # un numero por nodo, para poder dibujar el arbol

    # ---- lo que le avisa el algoritmo ----

    def ROUND(self, label, others=None):
        self.round = label
        self.others = sorted(others) if others else None

    def POP(self, node, frontier, reached):
        self.node = node
        self.children = []
        self.note = None
        self.pops += 1

    def CHILD(self, child, reached):
        self.children.append(self._datos(child) | self._veredicto(child, reached))

    def NOTE(self, texto):
        self.note = texto

    def STEP(self, frontier, reached):
        self.frames.append(self._frame(frontier, reached))

    def DONE(self, node, frontier, reached):
        frame = self._frame(frontier, reached)
        if node.STATE in ("failure", "cutoff"):
            frame["done"] = {"kind": node.STATE}
        else:
            frame["done"] = {
                "kind": "goal",
                "path": path_states(node),
                "cost": node.PATH_COST,
            }
        self.frames.append(frame)

    # ---- armado de los datos ----

    def _veredicto(self, child, reached):
        """Que se hizo con el hijo, mirando `reached` antes de tocarlo."""
        s = child.STATE
        if reached is None:
            # depth-first no lleva reached: todos los hijos entran.
            return {"kind": "nuevo", "nota": ""}
        if isinstance(reached, dict):
            # best-first guarda el mejor nodo conocido de cada estado.
            previous = reached.get(s)
            if previous is None:
                return {"kind": "nuevo", "nota": "visto por primera vez"}
            if child.PATH_COST < previous.PATH_COST:
                return {
                    "kind": "mejora",
                    "nota": f"antes teniamos g {previous.PATH_COST:g}",
                }
            return {
                "kind": "descartado",
                "nota": f"ya teniamos g {previous.PATH_COST:g}",
            }
        # breadth-first guarda solo los estados alcanzados.
        if s in reached:
            return {"kind": "descartado", "nota": "ya alcanzado"}
        return {"kind": "nuevo", "nota": "visto por primera vez"}

    def _id(self, node):
        """Un numero por nodo del arbol de busqueda.

        No alcanza con la ciudad: en el arbol la misma ciudad aparece una
        vez por cada camino que llega hasta ella.
        """
        if node is None:
            return None
        clave = id(node)
        if clave not in self.ids:
            # se guarda el nodo tambien: si se perdiera, Python reusa el id()
            self.ids[clave] = (len(self.ids), node)
        return self.ids[clave][0]

    def _datos(self, node):
        return {
            "state": node.STATE,
            "g": node.PATH_COST,
            "key": self.key(node),
            # lo que hace falta para el arbol
            "id": self._id(node),
            "parent": self._id(node.PARENT),
            "depth": depth(node),
        }

    def _frame(self, frontier, reached):
        mejor = reached if isinstance(reached, dict) else {}
        return {
            "step": len(self.frames) + 1,
            "round": self.round,
            "otros": self.others,
            "pop": self._datos(self.node) | {"path": path_states(self.node)},
            "children": self.children,
            "note": self.note,
            # Una copia es obsoleta si `reached` ya guarda otra mejor para
            # esa ciudad. El libro las deja en la cola: expandirlas no
            # rompe nada, solo cuesta.
            "frontier": [
                {
                    "state": n.STATE,
                    "key": self.key(n),
                    "stale": mejor.get(n.STATE, n) is not n,
                }
                for n in frontier.nodes()
            ],
            "reached": self._reached(reached),
            "done": None,
        }

    def _reached(self, reached):
        if reached is None:
            return None
        if isinstance(reached, dict):
            return sorted([s, n.PATH_COST] for s, n in reached.items())
        return [[s, None] for s in sorted(reached)]

    # ---- la pagina ----

    def datos(self):
        mapa = self.problem.map
        xs = [x for x, y in mapa.locations.values()]
        ys = [y for x, y in mapa.locations.values()]
        borde = 46
        alto = max(ys) + min(ys)  # para dar vuelta el eje y
        return {
            "name": self.name,
            "label": self.label,
            "keyName": self.key_name,
            "initial": self.problem.INITIAL,
            "goal": self.problem.GOAL,
            # En el libro el eje y va para arriba; en SVG va para abajo.
            "cities": {c: [x, alto - y] for c, (x, y) in mapa.locations.items()},
            "links": sorted(
                {(min(a, b), max(a, b), d) for (a, b), d in mapa.distances.items()}
            ),
            "viewBox": (
                f"{min(xs) - borde} {min(ys) - borde} "
                f"{max(xs) - min(xs) + 2 * borde} "
                f"{max(ys) - min(ys) + 2 * borde}"
            ),
            "frames": self.frames,
        }

    def html(self):
        """La pagina entera, en un string."""
        return PLANTILLA.read_text(encoding="utf-8").replace(
            "__DATA__", json.dumps(self.datos(), ensure_ascii=False)
        )

    def write(self, destino, open_browser=True):
        # Las paginas generadas van todas juntas a salidas/, fuera de lib/.
        carpeta = Path(__file__).resolve().parent.parent / "salidas"
        carpeta.mkdir(exist_ok=True)
        salida = carpeta / destino
        salida.write_text(self.html(), encoding="utf-8")
        if open_browser:
            webbrowser.open(salida.as_uri())
        return salida
