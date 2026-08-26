"""
La frontera  -  Russell & Norvig, seccion 3.3.2

La frontera es una cola. Las unicas operaciones que necesita un
algoritmo de busqueda son:

    IS_EMPTY(frontier)   true solo si no quedan nodos
    POP(frontier)        saca y devuelve el nodo de arriba
    TOP(frontier)        mira el nodo de arriba sin sacarlo
    ADD(node, frontier)  inserta el nodo en el lugar que le corresponde

Lo unico que cambia entre un algoritmo y otro es que significa
"el nodo de arriba".
"""

import heapq
from collections import deque
from itertools import count


class PriorityQueue:
    """Arriba esta el nodo de menor key(node).

    Es la frontera de best-first search: `key` es la funcion f.
    """

    def __init__(self, items=(), key=lambda node: node):
        self.key = key
        self.tie = count()      # desempata por orden de llegada
        self.heap = []
        for item in items:
            self.ADD(item)

    def ADD(self, node):
        heapq.heappush(self.heap, (self.key(node), next(self.tie), node))

    def POP(self):
        return heapq.heappop(self.heap)[2]

    def TOP(self):
        return self.heap[0][2]

    def IS_EMPTY(self):
        return not self.heap

    def nodes(self):
        """Los nodos en el orden en que van a salir. Solo para mostrar."""
        return [node for _, _, node in sorted(self.heap)]

    def __len__(self):
        return len(self.heap)

    def __repr__(self):
        return " ".join(f"{n.STATE}:{k:g}" for k, _, n in sorted(self.heap))


class FIFOQueue:
    """Arriba esta el nodo que entro primero.

    Es la frontera de breadth-first search: los nodos salen en el mismo
    orden en que se generaron, asi que se recorre el arbol por niveles.
    """

    def __init__(self, items=()):
        self.items = deque(items)

    def ADD(self, node):
        self.items.append(node)

    def POP(self):
        return self.items.popleft()

    def TOP(self):
        return self.items[0]

    def IS_EMPTY(self):
        return not self.items

    def nodes(self):
        """Los nodos en el orden en que van a salir. Solo para mostrar."""
        return list(self.items)

    def __len__(self):
        return len(self.items)


class LIFOQueue:
    """Arriba esta el ultimo nodo que entro: una pila.

    Es la frontera de depth-first search: siempre sale el hijo recien
    generado, asi que se baja por una rama hasta el fondo.
    """

    def __init__(self, items=()):
        self.items = list(items)

    def ADD(self, node):
        self.items.append(node)

    def POP(self):
        return self.items.pop()

    def TOP(self):
        return self.items[-1]

    def IS_EMPTY(self):
        return not self.items

    def nodes(self):
        return list(reversed(self.items))

    def __len__(self):
        return len(self.items)
