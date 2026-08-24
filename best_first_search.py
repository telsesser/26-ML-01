"""
BEST-FIRST-SEARCH  -  Russell & Norvig, figura 3.7

Con f(n) = g(n) esto es uniform-cost search (Dijkstra): siempre expande
el nodo mas barato encontrado hasta ahora. Cambiando f se obtienen los
demas algoritmos de la familia.

Uso:
    uv run best_first_search.py           solo el resultado
    uv run best_first_search.py --view    ademas abre la pagina paso a paso
"""

from frontier import PriorityQueue
from node import Node, expand, failure
from view import silent


def best_first_search(problem, f, view=silent):
    """Busca un nodo objetivo expandiendo siempre el de f minimo.

    Las cinco lineas `view.` son lo unico que se agrega al pseudocodigo:
    le cuentan a un narrador lo que va pasando. Con el view por defecto
    no hacen nada.
    """
    node = Node(STATE=problem.INITIAL)
    frontier = PriorityQueue([node], key=f)
    reached = {problem.INITIAL: node}
    while not frontier.IS_EMPTY():
        node = frontier.POP()
        view.POP(node, frontier, reached)
        if problem.IS_GOAL(node.STATE):
            view.DONE(node, frontier, reached)
            return node
        for child in expand(problem, node):
            s = child.STATE
            view.CHILD(child, reached)
            if s not in reached or child.PATH_COST < reached[s].PATH_COST:
                reached[s] = child
                frontier.ADD(child)
        view.STEP(frontier, reached)
    view.DONE(failure, frontier, reached)
    return failure


def g(node):
    """El costo del camino hasta el nodo. En el libro: g(n)."""
    return node.PATH_COST


if __name__ == "__main__":
    import sys

    from node import path_states
    from problem import RouteProblem
    from romania import romania
    from web import Web

    problem = RouteProblem("Arad", "Bucharest", map=romania)

    # uniform-cost search: f(n) = g(n), el costo del camino y nada mas.
    f = g

    ver = "--view" in sys.argv
    view = Web(problem, "BEST-FIRST-SEARCH", "f(n) = g(n)", key=f) if ver else silent

    solution = best_first_search(problem, f, view=view)

    print(" -> ".join(path_states(solution)))
    print(f"costo: {solution.PATH_COST}")

    if ver:
        print(f"pagina: {view.write('best_first.html')}")
