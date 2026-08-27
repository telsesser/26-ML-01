"""
BREADTH-FIRST-SEARCH  -  Russell & Norvig, figura 3.9

Dos diferencias con best-first search, y las dos importan:

  1. La frontera es una FIFO, no una cola de prioridad. Sale siempre el
     nodo que entro primero, asi que el arbol se recorre por niveles.
  2. La prueba de objetivo es TEMPRANA: se hace al generar el hijo, no
     al sacarlo de la cola. Como todos los niveles anteriores ya se
     expandieron, el primer objetivo que aparece es el mas superficial.

Ojo con lo que eso significa aca: el camino que devuelve es el de menos
ciudades, no el mas corto en kilometros.

Uso:
    uv run breadth_first_search.py           solo el resultado
    uv run breadth_first_search.py --view    ademas abre la pagina paso a paso
"""

from frontier import FIFOQueue
from node import Node, expand, failure
from view import silent


def breadth_first_search(problem, view=silent):
    """Expande primero los nodos menos profundos."""
    node = Node(STATE=problem.INITIAL)
    if problem.IS_GOAL(node.STATE):
        return node
    frontier = FIFOQueue([node])
    reached = {problem.INITIAL}          # un conjunto de estados, no de nodos
    while not frontier.IS_EMPTY():
        node = frontier.POP()
        view.POP(node, frontier, reached)
        for child in expand(problem, node):
            s = child.STATE
            view.CHILD(child, reached)
            if problem.IS_GOAL(s):
                view.DONE(child, frontier, reached)
                return child
            if s not in reached:
                reached.add(s)
                frontier.ADD(child)
        view.STEP(frontier, reached)
    view.DONE(failure, frontier, reached)
    return failure


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

    ver = "--view" in sys.argv
    view = (Web(problem, "BREADTH-FIRST-SEARCH", "cola FIFO, objetivo al generar",
                key=depth, key_name="prof")
            if ver else silent)

    solution = breadth_first_search(problem, view=view)

    print(" -> ".join(path_states(solution)))
    print(f"costo: {solution.PATH_COST}")

    if ver:
        print(f"pagina: {view.write('breadth_first.html')}")
