"""
Node  -  Russell & Norvig, seccion 3.3.1

Un nodo del arbol de busqueda. Los nombres de los atributos son los del
libro:

    node.STATE      el estado al que corresponde el nodo
    node.PARENT     el nodo que lo genero
    node.ACTION     la accion que se aplico al padre para generarlo
    node.PATH_COST  el costo total del camino desde el estado inicial
                    (en las formulas se escribe g(n))
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Node:
    STATE: Any
    PARENT: "Node | None" = None
    ACTION: Any = None
    PATH_COST: float = 0

    def __repr__(self) -> str:
        return f"<{self.STATE} g={self.PATH_COST:g}>"


# Nodos especiales que devuelven los algoritmos cuando no hay solucion.
failure = Node(STATE="failure", PATH_COST=math.inf)
cutoff = Node(STATE="cutoff", PATH_COST=math.inf)


def expand(problem, node):
    """EXPAND(problem, node) yields nodes.

    Genera los hijos de `node` aplicando cada accion posible.
    """
    s = node.STATE
    for action in problem.ACTIONS(s):
        s_prime = problem.RESULT(s, action)
        cost = node.PATH_COST + problem.ACTION_COST(s, action, s_prime)
        yield Node(STATE=s_prime, PARENT=node, ACTION=action, PATH_COST=cost)


def depth(node) -> int:
    """DEPTH(node): cuantas acciones hay desde el estado inicial."""
    if node is None or node.PARENT is None:
        return 0
    return 1 + depth(node.PARENT)


def is_cycle(node, k=30) -> bool:
    """IS-CYCLE(node): el estado del nodo ya aparece en sus ancestros.

    Depth-first no lleva `reached`, asi que sin esto se quedaria dando
    vueltas entre dos ciudades vecinas para siempre.
    """
    def find(ancestor, k):
        return (ancestor is not None and k > 0
                and (ancestor.STATE == node.STATE or find(ancestor.PARENT, k - 1)))
    return find(node.PARENT, k)


def path_states(node) -> list:
    """La secuencia de estados desde el inicial hasta `node`."""
    if node is None:
        return []
    return path_states(node.PARENT) + [node.STATE]


def path_actions(node) -> list:
    """La secuencia de acciones desde el inicial hasta `node`."""
    if node is None or node.PARENT is None:
        return []
    return path_actions(node.PARENT) + [node.ACTION]
