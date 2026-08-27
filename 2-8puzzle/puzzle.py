"""
El 8-puzzle  -  Russell & Norvig, seccion 3.2.1 y figura 3.4

El otro problema clasico del capitulo 3. Un tablero de 3x3 con ocho
fichas numeradas y un hueco; se corre una ficha por vez al hueco, hasta
dejar el tablero ordenado.

    7 2 4         1 2 3
    _ 5 6   --->  4 5 6
    8 3 1         7 8 _

Sirve para lo mismo que Rumania y no hace falta cambiar una sola linea
de los algoritmos: entran por la misma interfaz de `Problem`. Lo que
cambia es lo que el mapa de Rumania esconde por ser un caso comodo.

  1. El grafo NO existe. En Rumania los vecinos estan escritos en un
     diccionario. Aca ACTIONS los calcula en el momento: nadie guarda
     los 181.440 estados alcanzables en ningun lado.
  2. El espacio es grande. 181.440 estados contra 20 ciudades.
  3. Todos los pasos cuestan 1. Por eso busqueda en amplitud y costo
     uniforme devuelven el mismo camino, y la unica diferencia queda en
     cuantos nodos expande cada uno.

Ojo con el punto 2: busqueda en profundidad no termina aca. No es que
tarde, es que se hunde y no vuelve. La explicacion esta abajo, en la
seccion de resultados.

Uso:
    uv run puzzle.py            la tabla comparativa de los cinco
    uv run puzzle.py --view     ademas escribe las paginas paso a paso
"""

import sys
from pathlib import Path

# Los modulos comunes viven en la carpeta 0-lib/ de al lado.
LIB = str(Path(__file__).resolve().parent.parent / "0-lib")
if LIB not in sys.path:
    sys.path.append(LIB)

import random

from problem import Problem
from view import Silent

# El hueco es el 0. Las posiciones van de 0 a 8, por filas.
GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)

# Cuanto se mueve el hueco dentro de la tupla con cada accion.
PASOS = {"abajo": +3, "arriba": -3, "derecha": +1, "izquierda": -1}


class EightPuzzle(Problem):
    """El 8-puzzle. Una accion mueve EL HUECO, no la ficha.

    Es la convencion del libro y simplifica todo: hay a lo sumo cuatro
    acciones, y son las mismas cuatro siempre. Mover el hueco "arriba"
    se ve en el tablero como una ficha que baja.
    """

    def __init__(self, INITIAL, GOAL=GOAL):
        super().__init__(INITIAL, GOAL)

    def ACTIONS(self, state):
        fila, col = divmod(state.index(0), 3)
        bordes = {"arriba": fila == 0, "abajo": fila == 2,
                  "izquierda": col == 0, "derecha": col == 2}
        # Orden alfabetico, por lo mismo que en romania.py: que dos
        # corridas den siempre el mismo arbol.
        return [a for a in sorted(PASOS) if not bordes[a]]

    def RESULT(self, state, action):
        i = state.index(0)
        j = i + PASOS[action]
        fichas = list(state)
        fichas[i], fichas[j] = fichas[j], fichas[i]
        return tuple(fichas)

    # ACTION_COST no se define: cada movimiento cuesta 1, que es lo que
    # ya devuelve Problem. h() tampoco, todavia: las heuristicas del
    # 8-puzzle (fichas mal puestas, distancia Manhattan) son de la
    # clase que viene, cuando aparezcan greedy y A*.


# ---- tableros ----

# Cuatro movimientos desde el objetivo. Chico a proposito: expande entre
# 10 y 51 nodos segun el algoritmo, igual que el mapa de Rumania, asi que
# el arbol entero se puede recorrer a mano. El hueco arranca ya en su
# lugar y tiene que salir y volver: no se puede ir derecho al objetivo.
CHICO = (1, 2, 3,
         4, 8, 5,
         7, 6, 0)

# El de la figura 3.4 del libro. Veintiun movimientos: sirve para la
# tabla de numeros, no para mirar paso a paso.
FIGURA_34 = (7, 2, 4,
             0, 5, 6,
             8, 3, 1)


def mezclar(n, semilla=0):
    """Un tablero a `n` movimientos del objetivo, o menos.

    Se arranca del objetivo y se desordena hacia atras. Es la unica
    forma segura de inventar tableros: la mitad de las 362.880
    permutaciones de un 3x3 NO se pueden resolver, y con una de esas la
    busqueda recorre los 181.440 estados alcanzables para nada.
    """
    rnd = random.Random(semilla)
    p = EightPuzzle(GOAL)
    estado, previo = GOAL, None
    for _ in range(n):
        siguiente = p.RESULT(estado, rnd.choice(p.ACTIONS(estado)))
        if siguiente != previo:              # no deshacer el paso anterior
            previo, estado = estado, siguiente
    return estado


def tablero(state, hueco="_"):
    """El tablero en tres lineas, para imprimir."""
    fila = lambda f: " ".join(hueco if v == 0 else str(v) for v in f)
    return "\n".join(fila(state[i:i + 3]) for i in (0, 3, 6))


def lado_a_lado(*estados, sep="   ->   "):
    """Varios tableros en la misma linea."""
    columnas = [tablero(e).split("\n") for e in estados]
    return "\n".join(sep.join(c[i] for c in columnas) for i in range(3))


# ---- para medir ----

class Tope(Exception):
    """La busqueda se corto: paso el tope de expansiones."""


class Contador(Silent):
    """View que solo cuenta. Mismo papel que Web, sin dibujar nada.

    `pops` se llama igual que en Web a proposito: la tabla comparativa
    lee ese atributo sin preguntar que view es.
    """

    def __init__(self, tope=None):
        self.pops = 0
        self.hondo = 0        # la profundidad mas grande a la que llego
        self.tope = tope
        self.corte = None     # por que se corto, si se corto

    def POP(self, node, frontier, reached):
        self.pops += 1
        self.hondo = max(self.hondo, self._profundidad(node))
        if self.tope is not None and self.pops >= self.tope:
            raise Tope

    @staticmethod
    def _profundidad(node):
        """Como DEPTH(node), pero sin recursion.

        node.depth recursivo se queda sin pila justo en el caso que mas
        importa medir: el de busqueda en profundidad hundiendose.
        """
        d = 0
        while node.PARENT is not None:
            node, d = node.PARENT, d + 1
        return d


# ---- la tabla comparativa ----

def comparar(inicio, tope=None):
    """Corre los cinco algoritmos sobre el mismo tablero y los mide.

    Devuelve una lista de (nombre, solucion, contador). `solucion` es
    None si la busqueda no termino: hizo `tope` expansiones y se corto.
    """
    from best_first_search import best_first_search, g
    from bidirectional_search import bidirectional_search
    from breadth_first_search import breadth_first_search
    from depth_first_search import depth_first_search
    from iterative_deepening_search import iterative_deepening_search

    problem = EightPuzzle(inicio)
    problem_b = EightPuzzle(GOAL, inicio)   # el mismo problema al reves

    algoritmos = [
        ("búsqueda en amplitud", lambda v: breadth_first_search(problem, view=v)),
        ("costo uniforme", lambda v: best_first_search(problem, g, view=v)),
        ("búsqueda en profundidad", lambda v: depth_first_search(problem, view=v)),
        ("profundidad iterativa", lambda v: iterative_deepening_search(problem, view=v)),
        ("búsqueda bidireccional", lambda v: bidirectional_search(problem, problem_b, view=v)),
    ]

    resultados = []
    for nombre, correr in algoritmos:
        view = Contador(tope)
        try:
            resultados.append((nombre, correr(view), view))
        except Tope:
            view.corte = f"llegó al tope de {tope} expansiones"
            resultados.append((nombre, None, view))
        except RecursionError:
            # DEPTH(node) es recursiva. Cuando busqueda en profundidad baja
            # mil niveles, Python se queda sin pila antes de que salte el
            # tope. Es otra forma de decir lo mismo: no vuelve.
            view.corte = f"se quedó sin pila a {view.hondo} niveles"
            resultados.append((nombre, None, view))
    return resultados


def imprimir(inicio, tope=None, titulo=""):
    from node import path_states

    if titulo:
        print(titulo)
        print()
    print(lado_a_lado(inicio, GOAL))
    print()
    print(f"{'algoritmo':<25}{'pasos':>7}{'expande':>9}{'más hondo':>11}")
    print("-" * 52)
    cortes = []
    for nombre, solucion, view in comparar(inicio, tope):
        if solucion is None:
            pasos = "  -"
            cortes.append(f"{nombre}: {view.corte}")
        else:
            pasos = len(path_states(solucion)) - 1
        print(f"{nombre:<25}{pasos:>7}{view.pops:>9}{view.hondo:>11}")
    for corte in cortes:
        print(f"  - {corte}")
    print()


def paginas(inicio=CHICO, l=5, abrir=False):
    """Escribe las cinco paginas paso a paso del tablero `inicio`.

    Son las mismas cinco busquedas de comparar(), pero grabadas con
    WebPuzzle en vez de contadas con Contador. Va la version limitada de
    busqueda en profundidad y no la que no tiene limite, por lo obvio:
    la que no tiene limite no llega nunca al final.
    """
    from best_first_search import best_first_search, g
    from bidirectional_search import bidirectional_search
    from breadth_first_search import breadth_first_search
    from depth_first_search import depth_limited_search
    from iterative_deepening_search import iterative_deepening_search
    from node import depth
    from web_puzzle import WebPuzzle

    problem = EightPuzzle(inicio)
    problem_b = EightPuzzle(GOAL, inicio)

    paginas = [
        ("puzzle_amplitud.html", "BREADTH-FIRST-SEARCH",
         "cola FIFO, objetivo al generar", depth, "prof",
         lambda v: breadth_first_search(problem, view=v)),
        ("puzzle_uniforme.html", "BEST-FIRST-SEARCH",
         "f(n) = g(n)", g, "f",
         lambda v: best_first_search(problem, g, view=v)),
        (f"puzzle_limitada_{l}.html", "DEPTH-LIMITED-SEARCH",
         f"pila LIFO, l = {l}", depth, "prof",
         lambda v: depth_limited_search(problem, l, view=v)),
        ("puzzle_iterativa.html", "ITERATIVE-DEEPENING-SEARCH",
         "depth-limited con l = 0, 1, 2, ...", depth, "prof",
         lambda v: iterative_deepening_search(problem, view=v)),
        ("puzzle_bidireccional.html", "BIBF-SEARCH",
         "dos frentes, f(n) = g(n)", lambda n: n.PATH_COST, "g",
         lambda v: bidirectional_search(problem, problem_b, view=v)),
    ]

    escritas = []
    for archivo, nombre, label, key, key_name, correr in paginas:
        view = WebPuzzle(problem, nombre, label, key=key, key_name=key_name)
        correr(view)
        escritas.append(view.write(archivo, open_browser=abrir))
    return escritas


if __name__ == "__main__":
    import sys

    imprimir(CHICO, tope=1_000,
             titulo="Tablero chico: a cuatro movimientos del objetivo")
    imprimir(FIGURA_34, tope=200_000,
             titulo="Figura 3.4 del libro: a veintiún movimientos")

    if "--view" in sys.argv:
        for archivo in paginas():
            print(f"pagina: {archivo}")
