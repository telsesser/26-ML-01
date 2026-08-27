"""
ITERATIVE-DEEPENING-SEARCH  -  Russell & Norvig, figura 3.12

Corre depth-limited una y otra vez, subiendo el limite de a uno, hasta
que deja de dar cutoff.

Suena a desperdicio: cada vuelta rehace todo el trabajo de la anterior.
No lo es. En un arbol, casi todos los nodos estan en el ultimo nivel, y
ese nivel se genera una sola vez; el nivel de arriba se repite dos
veces, el siguiente tres, y asi. La cuenta total sigue siendo O(b^d).

A cambio se queda con lo mejor de los dos:

    memoria    la de depth-first, lineal en la profundidad
    respuesta  la de breadth-first, la solucion menos profunda

Es el algoritmo que conviene cuando el espacio de busqueda es grande y
no se sabe de antemano que tan lejos esta el objetivo.

Uso:
    uv run iterative_deepening_search.py           solo el resultado
    uv run iterative_deepening_search.py --view    ademas abre la pagina paso a paso
"""

from itertools import count

from depth_first_search import depth_limited_search
from node import cutoff
from view import silent


def iterative_deepening_search(problem, view=silent):
    """Prueba con limite 0, 1, 2, ... hasta encontrar."""
    # En el libro esta variable se llama `depth`; aca `l`, para no pisar
    # la funcion DEPTH(node) y para que se lea igual que el parametro de
    # depth-limited.
    for l in count():
        view.ROUND(f"l = {l}")
        result = depth_limited_search(problem, l, view=view)
        if result is not cutoff:
            return result


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
    view = (Web(problem, "ITERATIVE-DEEPENING-SEARCH", "depth-limited con l = 0, 1, 2, ...",
                key=depth, key_name="prof")
            if ver else silent)

    solution = iterative_deepening_search(problem, view=view)

    print(" -> ".join(path_states(solution)))
    print(f"costo: {solution.PATH_COST}")

    if ver:
        print(f"pagina: {view.write('iterative_deepening.html')}")
