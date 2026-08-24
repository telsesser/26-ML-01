"""
BEST-FIRST-SEARCH  -  Russell & Norvig 4ta ed., figura 3.7

El algoritmo general de busqueda en grafo. Recibe una funcion f y saca
siempre de la frontera el nodo con f minimo. TODOS los algoritmos
informados y no informados del capitulo 3 son este mismo codigo con
distinta f:

    f(n) = g(n)              ->  costo uniforme (Dijkstra)
    f(n) = h(n)              ->  voraz / greedy best-first
    f(n) = g(n) + h(n)       ->  A*
    f(n) = profundidad(n)    ->  amplitud / BFS

Uso:  uv run best_first.py
"""

from __future__ import annotations

import heapq
from typing import Callable, Iterator

from romania import Nodo, ProblemaRuta, arad_a_bucharest
from traza import Evento, Extraer, Fallo, Generar, Inicio, Obsoleto, Solucion


# --------------------------------------------------------------------------
# El algoritmo
# --------------------------------------------------------------------------

def best_first_search(
    problema: ProblemaRuta,
    f: Callable[[Nodo], float],
    saltar_obsoletos: bool = False,
) -> Iterator[Evento]:
    """BEST-FIRST-SEARCH(problem, f).

    Es un generador: emite un evento por cada decision que toma, y el
    ultimo evento es Solucion o Fallo. Para obtener solo el resultado:

        solucion, traza = ejecutar(best_first_search(p, f))

    `saltar_obsoletos` no esta en el pseudocodigo del libro; ver la nota
    al final del bucle.
    """
    # node <- NODE(STATE=problem.INITIAL)
    nodo = problema.estado_inicial

    # frontier <- a priority queue ordered by f, with node as an element
    #
    # heapq no acepta desempates arbitrarios, asi que metemos un contador
    # de insercion. Con eso, ante f iguales gana el que entro primero:
    # el recorrido queda determinista y reproducible en clase (y ademas
    # hace que f=profundidad se comporte exactamente como BFS).
    orden = 0
    frontera: list[tuple[float, int, Nodo]] = [(f(nodo), orden, nodo)]

    # reached <- a lookup table, with one entry with key problem.INITIAL
    #            and value node
    #
    # `alcanzados` es la memoria del algoritmo: para cada ciudad, el
    # mejor nodo con el que llegamos hasta ahora. Es lo que evita dar
    # vueltas en circulos y lo que distingue busqueda en GRAFO de
    # busqueda en ARBOL.
    alcanzados: dict[str, Nodo] = {problema.inicio: nodo}

    paso = 0
    yield Inicio(nodo=nodo, f=f(nodo), paso=paso,
                 frontera=_foto(frontera), alcanzados=list(alcanzados))

    # while not IS-EMPTY(frontier) do
    while frontera:
        paso += 1

        # node <- POP(frontier)
        f_nodo, _, nodo = heapq.heappop(frontera)

        # Nota (fuera del libro): el nodo que sacamos puede estar
        # obsoleto. Mientras esperaba en la cola pudimos haber
        # encontrado un camino mejor a esa misma ciudad, y quedaron las
        # dos copias adentro. El pseudocodigo de la figura 3.7 lo
        # expande igual -- es correcto, porque los hijos van a ser
        # descartados por el chequeo de `reached`, solo se pierde
        # trabajo. Con saltar_obsoletos=True lo salteamos y se puede
        # comparar cuantos nodos de menos se expanden.
        if saltar_obsoletos and alcanzados[nodo.estado] is not nodo:
            yield Obsoleto(nodo=nodo, mejor=alcanzados[nodo.estado].costo_camino,
                           paso=paso, frontera=_foto(frontera),
                           alcanzados=list(alcanzados))
            continue

        yield Extraer(nodo=nodo, f=f_nodo, paso=paso,
                      frontera=_foto(frontera), alcanzados=list(alcanzados))

        # if problem.IS-GOAL(node.STATE) then return node
        #
        # El test de objetivo va aca, al EXTRAER, no al generar. Es la
        # diferencia que hace optimos a costo uniforme y a A*: recien
        # cuando el objetivo es el mejor de la frontera sabemos que
        # ningun camino pendiente puede mejorarlo.
        if problema.es_objetivo(nodo.estado):
            yield Solucion(nodo=nodo, paso=paso, frontera=_foto(frontera),
                           alcanzados=list(alcanzados))
            return

        # for each child in EXPAND(problem, node) do
        for hijo in problema.expandir(nodo):
            s = hijo.estado

            # if s is not in reached or
            #    child.PATH-COST < reached[s].PATH-COST then
            if s not in alcanzados:
                decision, previo = "nuevo", None
            elif hijo.costo_camino < alcanzados[s].costo_camino:
                decision, previo = "mejora", alcanzados[s].costo_camino
            else:
                decision, previo = "descartado", alcanzados[s].costo_camino

            if decision != "descartado":
                alcanzados[s] = hijo            # reached[s] <- child
                orden += 1
                heapq.heappush(frontera, (f(hijo), orden, hijo))  # add to frontier

            yield Generar(nodo=hijo, f=f(hijo), decision=decision,
                          costo_previo=previo, paso=paso,
                          frontera=_foto(frontera), alcanzados=list(alcanzados))

    # return failure
    yield Fallo(paso=paso, frontera=[], alcanzados=list(alcanzados))


def _foto(frontera) -> list[tuple[str, float]]:
    """La frontera como la veria alguien mirando el pizarron: ciudades
    ordenadas por f. (El heap por dentro no esta ordenado del todo.)"""
    return [(n.estado, v) for v, _, n in sorted(frontera)]


# --------------------------------------------------------------------------
# Las funciones f: aca vive la diferencia entre un algoritmo y otro
# --------------------------------------------------------------------------

def f_costo_uniforme(problema: ProblemaRuta) -> Callable[[Nodo], float]:
    """f(n) = g(n). Costo uniforme, o Dijkstra. No usa heuristica:
    se expande siempre el camino mas barato conocido."""
    return lambda n: n.costo_camino


def f_voraz(problema: ProblemaRuta) -> Callable[[Nodo], float]:
    """f(n) = h(n). Voraz: va siempre al que PARECE mas cerca del
    objetivo, ignorando lo que ya gasto. Rapido pero no optimo."""
    return lambda n: problema.h(n.estado)


def f_a_estrella(problema: ProblemaRuta) -> Callable[[Nodo], float]:
    """f(n) = g(n) + h(n). A*: lo gastado mas lo estimado que falta.
    Con h admisible y consistente, encuentra el optimo."""
    return lambda n: n.costo_camino + problema.h(n.estado)


def f_amplitud(problema: ProblemaRuta) -> Callable[[Nodo], float]:
    """f(n) = profundidad(n). Da BFS: primero todo lo que esta a un
    paso, despues a dos... Optimo en CANTIDAD DE SALTOS, no en km."""
    return lambda n: n.profundidad


ALGORITMOS = {
    "amplitud (f=profundidad)":   f_amplitud,
    "costo uniforme (f=g)":       f_costo_uniforme,
    "voraz (f=h)":                f_voraz,
    "A* (f=g+h)":                 f_a_estrella,
}


# --------------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------------

if __name__ == "__main__":
    from traza import ejecutar, imprimir, resumen

    problema = arad_a_bucharest()

    print("=" * 66)
    print("A* de Arad a Bucharest, paso a paso")
    print("=" * 66)
    imprimir(best_first_search(problema, f_a_estrella(problema)),
             mostrar_frontera=True)

    print()
    print("=" * 66)
    print("El mismo codigo, cambiando f")
    print("=" * 66)
    print(f"{'algoritmo':<26} {'costo':>6} {'expand':>7} {'gener':>6} "
          f"{'max|F|':>7}  camino")
    print("-" * 66)
    for nombre, factory in ALGORITMOS.items():
        _, traza = ejecutar(best_first_search(problema, factory(problema)))
        r = resumen(traza)
        camino = " -> ".join(c[:4] for c in r["camino"])
        print(f"{nombre:<26} {r['costo']:>6g} {r['expandidos']:>7} "
              f"{r['generados']:>6} {r['frontera_max']:>7}  {camino}")
