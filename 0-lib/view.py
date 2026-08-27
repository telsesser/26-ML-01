"""
El narrador de la busqueda.

Un algoritmo le avisa a un `view` lo que va haciendo. Por defecto ese
view es Silent y no hace nada, asi que el algoritmo corre igual de
rapido y se lee igual que en el libro.

El view que dibuja esta en web.py.
"""


class Silent:
    """View nulo: el algoritmo no narra nada."""

    # ROUND marca que empieza una vuelta nueva: una iteracion de
    # profundidad iterativa, o un lado de la busqueda bidireccional.
    # `others` son los estados que ya alcanzo el otro lado, si lo hay.
    def ROUND(self, label, others=None): pass
    def POP(self, node, frontier, reached): pass
    def CHILD(self, child, reached): pass
    def NOTE(self, texto): pass
    def STEP(self, frontier, reached): pass
    def DONE(self, node, frontier, reached): pass


silent = Silent()
