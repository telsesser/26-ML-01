"""
Problem  -  Russell & Norvig, seccion 3.1.1

La definicion formal de un problema de busqueda. Un algoritmo solo
conoce esta interfaz: no sabe nada de Rumania ni de mapas.
"""


class Problem:
    """Problema abstracto. Para definir uno concreto se heredan
    ACTIONS, RESULT y, si el costo no es uniforme, ACTION_COST."""

    def __init__(self, INITIAL=None, GOAL=None, **kwds):
        self.INITIAL = INITIAL
        self.GOAL = GOAL
        self.__dict__.update(**kwds)

    def ACTIONS(self, state):
        """Las acciones aplicables en `state`."""
        raise NotImplementedError

    def RESULT(self, state, action):
        """El estado que resulta de aplicar `action` en `state`."""
        raise NotImplementedError

    def ACTION_COST(self, s, action, s_prime):
        """El costo de ir de `s` a `s_prime` con `action`."""
        return 1

    def IS_GOAL(self, state):
        return state == self.GOAL

    def h(self, node):
        """Heuristica: costo estimado desde node.STATE hasta el objetivo.
        Por defecto 0, que no informa nada."""
        return 0

    def __str__(self):
        return f"{type(self).__name__}({self.INITIAL!r}, {self.GOAL!r})"


class RouteProblem(Problem):
    """Ir de una ciudad a otra sobre un mapa.

    Una accion es, simplemente, la ciudad vecina a la que uno se mueve.
    """

    def __init__(self, INITIAL, GOAL, map):
        super().__init__(INITIAL, GOAL, map=map)

    def ACTIONS(self, state):
        return self.map.neighbors[state]

    def RESULT(self, state, action):
        # La accion es la ciudad destino, siempre que sea vecina.
        return action if action in self.map.neighbors[state] else state

    def ACTION_COST(self, s, action, s_prime):
        return self.map.distances[s, s_prime]

    def h(self, node):
        """Distancia en linea recta hasta el objetivo (figura 3.22)."""
        return self.map.straight_line_distance.get(node.STATE, 0)
