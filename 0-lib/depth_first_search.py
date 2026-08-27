"""
DEPTH-FIRST-SEARCH  -  Russell & Norvig, figura 3.12

El libro no le da figura propia: da DEPTH-LIMITED-SEARCH, y depth-first
es esa misma con limite infinito. Asi que eso es lo que esta aca.

Dos diferencias con los otros dos:

  1. La frontera es una LIFO, una pila. Sale siempre el ultimo hijo
     generado, asi que se baja por una rama hasta el fondo antes de
     probar la siguiente.
  2. NO hay `reached`. Por eso la memoria es lineal en la profundidad y
     no exponencial, que es toda la gracia de depth-first. El precio es
     que puede volver a un estado por el que ya paso: IS_CYCLE lo
     corta mirando los ancestros del nodo.

No garantiza nada: ni el camino mas corto ni el mas barato.

Uso:
    uv run depth_first_search.py               solo el resultado
    uv run depth_first_search.py --view        ademas abre la pagina paso a paso
    uv run depth_first_search.py --limite 3    corre depth-limited con l = 3
"""

import math

from frontier import LIFOQueue
from node import Node, cutoff, depth, expand, failure, is_cycle
from view import silent


def depth_limited_search(problem, l=math.inf, view=silent):
    """Baja por una rama hasta el limite `l` antes de probar la siguiente."""
    frontier = LIFOQueue([Node(STATE=problem.INITIAL)])
    result = failure
    while not frontier.IS_EMPTY():
        node = frontier.POP()
        view.POP(node, frontier, None)
        if problem.IS_GOAL(node.STATE):
            view.DONE(node, frontier, None)
            return node
        if depth(node) > l:
            result = cutoff
            view.NOTE(f"pasa el limite l = {l}: no se expande")
        elif not is_cycle(node):
            for child in expand(problem, node):
                view.CHILD(child, None)
                frontier.ADD(child)
        else:
            view.NOTE("IS_CYCLE: esta ciudad ya esta en el camino, no se expande")
        view.STEP(frontier, None)
    view.DONE(result, frontier, None)
    return result


def depth_first_search(problem, view=silent):
    """Depth-first es depth-limited sin limite."""
    return depth_limited_search(problem, math.inf, view=view)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # El mapa de Rumania vive en la carpeta del problema, no en 0-lib.
    sys.path.append(str(Path(__file__).resolve().parent.parent / "1-romania"))

    from node import depth, path_states
    from problem import RouteProblem
    from romania import romania
    from web import Web

    problem = RouteProblem("Arad", "Bucharest", map=romania)

    # Sin --limite el limite es infinito, y eso es depth-first search.
    l = math.inf
    if "--limite" in sys.argv:
        l = int(sys.argv[sys.argv.index("--limite") + 1])

    nombre = "DEPTH-FIRST-SEARCH" if l == math.inf else "DEPTH-LIMITED-SEARCH"
    label = "pila LIFO, sin reached" if l == math.inf else f"pila LIFO, l = {l}"
    archivo = "depth_first.html" if l == math.inf else f"depth_limited_{l}.html"

    ver = "--view" in sys.argv
    view = (Web(problem, nombre, label, key=depth, key_name="prof")
            if ver else silent)

    solution = depth_limited_search(problem, l, view=view)

    # Depth-limited puede devolver tres cosas distintas, y el limite es
    # justamente lo que hace aparecer la tercera.
    if solution is cutoff:
        print(f"cutoff: puede haber solucion mas abajo de l = {l}")
    elif solution is failure:
        print("failure: no hay solucion")
    else:
        print(" -> ".join(path_states(solution)))
        print(f"costo: {solution.PATH_COST}")

    if ver:
        print(f"pagina: {view.write(archivo)}")
