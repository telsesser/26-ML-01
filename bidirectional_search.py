"""
BIBF-SEARCH  -  Russell & Norvig, figura 3.14

Busqueda bidireccional: dos busquedas al mismo tiempo, una que sale de
INITIAL hacia adelante y otra que sale de GOAL hacia atras, hasta que
las dos se cruzan en alguna ciudad del medio.

Por que conviene: dos arboles de profundidad d/2 tienen 2*b^(d/2)
nodos, y uno solo de profundidad d tiene b^d. Para b y d grandes la
diferencia es enorme.

Lo que hay que tener en cuenta:

  1. Hacen falta DOS problemas. El de ida y el de vuelta. Aca alcanza
     con dar vuelta INITIAL y GOAL, porque el mapa no es dirigido. En
     un problema donde las acciones no se pueden deshacer hay que
     construir el problema inverso a mano, y a veces no se puede: esa
     es la limitacion real de la busqueda bidireccional.
  2. El primer cruce no es la mejor solucion. Se sigue buscando y se
     guarda la mejor, hasta que TERMINATED dice que ya no puede
     aparecer ninguna mejor.

Uso:
    uv run bidirectional_search.py           solo el resultado
    uv run bidirectional_search.py --view    ademas abre la pagina paso a paso
"""

from frontier import PriorityQueue
from node import Node, expand, failure
from view import silent


def bibf_search(problem_f, f_f, problem_b, f_b, view=silent):
    """Best-first por los dos lados a la vez.

    En cada vuelta avanza el lado cuyo nodo de arriba es mas barato, asi
    los dos frentes crecen parejos y se encuentran cerca del medio.
    """
    node_f = Node(STATE=problem_f.INITIAL)      # nodo del estado inicial
    node_b = Node(STATE=problem_b.INITIAL)      # nodo del estado objetivo
    frontier_f = PriorityQueue([node_f], key=f_f)
    frontier_b = PriorityQueue([node_b], key=f_b)
    reached_f = {node_f.STATE: node_f}
    reached_b = {node_b.STATE: node_b}
    solution = failure
    while not terminated(solution, frontier_f, frontier_b, f_f, f_b):
        if f_f(frontier_f.TOP()) < f_b(frontier_b.TOP()):
            view.ROUND("adelante", reached_b)
            solution = proceed("F", problem_f, frontier_f,
                               reached_f, reached_b, solution, view)
        else:
            view.ROUND("atras", reached_f)
            solution = proceed("B", problem_b, frontier_b,
                               reached_b, reached_f, solution, view)
    # El ultimo cuadro muestra los dos lados juntos.
    view.ROUND("los dos lados", reached_b)
    view.DONE(solution, frontier_f, reached_f)
    return solution


def proceed(dir, problem, frontier, reached, reached2, solution, view=silent):
    """Expande un nodo de un lado y lo compara contra el otro lado.

    `dir` es F si el que avanza es el de ida, B si es el de vuelta.
    """
    node = frontier.POP()
    view.POP(node, frontier, reached)
    for child in expand(problem, node):
        s = child.STATE
        view.CHILD(child, reached)
        if s not in reached or child.PATH_COST < reached[s].PATH_COST:
            reached[s] = child
            frontier.ADD(child)
            if s in reached2:
                # Los dos lados llegaron a la misma ciudad: hay camino
                # entero. Puede que no sea el mejor, asi que se compara.
                solution2 = join_nodes(dir, child, reached2[s])
                if solution2.PATH_COST < solution.PATH_COST:
                    solution = solution2
                    view.NOTE(f"se cruzan en {s}: "
                              f"camino entero de {solution.PATH_COST:g}")
    view.STEP(frontier, reached)
    return solution


def terminated(solution, frontier_f, frontier_b, f_f, f_b):
    """TERMINATED: ya no puede aparecer una solucion mejor.

    Si los dos nodos de arriba juntos ya cuestan mas que el mejor camino
    que tenemos, cualquier camino que quede por armar va a ser peor.
    Mientras no haya solucion, PATH_COST de `failure` es infinito y esto
    nunca corta.
    """
    if frontier_f.IS_EMPTY() or frontier_b.IS_EMPTY():
        return True
    return f_f(frontier_f.TOP()) + f_b(frontier_b.TOP()) > solution.PATH_COST


def join_nodes(dir, node1, node2):
    """JOIN-NODES: pega el camino de ida con el de vuelta dado vuelta.

    Los dos nodos estan en la misma ciudad. El de ida trae el camino
    desde INITIAL; el de vuelta trae el camino hasta GOAL, pero armado
    al reves, asi que hay que rehacerlo hacia adelante.
    """
    ida, vuelta = (node1, node2) if dir == "F" else (node2, node1)
    node = ida
    while vuelta.PARENT is not None:
        paso = vuelta.PATH_COST - vuelta.PARENT.PATH_COST
        # El camino de vuelta sabe por que ciudades pasa, pero no con
        # que accion se llega a cada una yendo para adelante.
        node = Node(STATE=vuelta.PARENT.STATE, PARENT=node, ACTION=None,
                    PATH_COST=node.PATH_COST + paso)
        vuelta = vuelta.PARENT
    return node


def bidirectional_search(problem_f, problem_b, view=silent):
    """Bidireccional con f(n) = g(n) de los dos lados: uniform-cost."""
    def g(node):
        return node.PATH_COST
    return bibf_search(problem_f, g, problem_b, g, view=view)


if __name__ == "__main__":
    import sys

    from node import path_states
    from problem import RouteProblem
    from romania import romania
    from web import Web

    # El mismo mapa, de ida y de vuelta.
    problem_f = RouteProblem("Arad", "Bucharest", map=romania)
    problem_b = RouteProblem("Bucharest", "Arad", map=romania)

    ver = "--view" in sys.argv
    view = (Web(problem_f, "BIBF-SEARCH", "dos frentes, f(n) = g(n)",
                key=lambda node: node.PATH_COST, key_name="g")
            if ver else silent)

    solution = bidirectional_search(problem_f, problem_b, view=view)

    print(" -> ".join(path_states(solution)))
    print(f"costo: {solution.PATH_COST}")

    if ver:
        print(f"pagina: {view.write('bidirectional.html')}")
