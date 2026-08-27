# Trabajo práctico — El 8-puzzle

**Referencia:** Russell & Norvig, *Artificial Intelligence: A Modern Approach*,
4ª edición, secciones 3.1.1 y 3.2.1, figura 3.4.

En clase buscamos sobre el mapa de Rumania, un caso cómodo: veinte estados y el
grafo escrito de antemano en un diccionario. El 8-puzzle tiene 181.440 estados
alcanzables y nadie los enumera; los sucesores se calculan en el momento. El
objetivo del trabajo es comprobar que esa diferencia **no afecta a los
algoritmos**: si el modelado es correcto, los cinco vistos en clase corren sobre
el 8-puzzle sin modificar una sola línea.

---

## Parte 1 — Modelado del problema

Definir una clase `EightPuzzle` que herede de `Problem` (`lib/problem.py`) y
represente el problema de la figura 3.4:

```
    7 2 4          1 2 3
    _ 5 6   --->   4 5 6
    8 3 1          7 8 _
```

Se pide:

1. **Representación del estado.** Va dada: una tupla de nueve enteros, por
   filas, con el 0 en el lugar del hueco. Justificar por qué sirve. El requisito
   lo impone el algoritmo y no el problema: los estados se guardan en `reached`,
   que es un conjunto, y por lo tanto deben ser *hashables*. Una tupla lo es
   porque es inmutable, y de ahí sale el punto 3.

2. **`ACTIONS(state)`.** Las acciones aplicables. Conviene adoptar la convención
   del libro y mover **el hueco**, no la ficha: así hay a lo sumo cuatro
   acciones y son siempre las mismas cuatro. El orden debe ser determinista,
   para que dos corridas generen el mismo árbol.

3. **`RESULT(state, action)`.** El estado sucesor, sin modificar el recibido. Si
   los estados fueran mutables, `reached` guardaría referencias a tableros que la
   búsqueda cambia por debajo y dejaría de significar «los estados ya
   alcanzados».

4. **`ACTION_COST` e `IS_GOAL`.** Decidir si hace falta redefinirlos, y
   justificarlo.

5. **Verificación.** Comprobar, con al menos tres casos, que cada acción produce
   un estado válido y que aplicarla y deshacerla devuelve el tablero original.

### Punto de partida

```python
import random
import sys
sys.path.append("../lib")

from problem import Problem

# El hueco es el 0. Las nueve casillas van en una sola tupla, por filas:
# la casilla (fila, col) esta en la posicion fila * 3 + col.
GOAL = (1, 2, 3,
        4, 5, 6,
        7, 8, 0)


class EightPuzzle(Problem):
    """El 8-puzzle. Una acción mueve el hueco, no la ficha."""

    def __init__(self, INITIAL, GOAL=GOAL):
        super().__init__(INITIAL, GOAL)

    def ACTIONS(self, state):
        """Las acciones aplicables en `state`."""
        raise NotImplementedError

    def RESULT(self, state, action):
        """El estado que resulta de aplicar `action` en `state`."""
        raise NotImplementedError

    # ACTION_COST e IS_GOAL: ver el punto 4. `Problem` ya define los dos.


def mezclar(n, semilla=0):
    """Un tablero a lo sumo a `n` movimientos del objetivo."""
    rnd = random.Random(semilla)
    p = EightPuzzle(GOAL)
    estado, previo = GOAL, None
    for _ in range(n):
        siguiente = p.RESULT(estado, rnd.choice(p.ACTIONS(estado)))
        if siguiente != previo:          # no deshacer el paso anterior
            previo, estado = estado, siguiente
    return estado
```

`mezclar` va dada porque no es parte del problema de búsqueda, pero conviene
entender por qué está escrita así. **No sirve permutar las fichas al azar:** la
mitad de las 362.880 permutaciones de un 3×3 no son resolubles, y sobre una de
ellas la búsqueda recorre los 181.440 estados alcanzables para no encontrar
nada. Partir del objetivo y desordenar hacia atrás garantiza que existe camino
de vuelta, y de paso acota su longitud. Notar que la función usa `ACTIONS` y
`RESULT`: hasta que esos dos no estén, no genera ningún tablero.

El modelado está terminado cuando esto corre, tal cual está escrito, sin haber
tocado nada de `lib/`:

```python
from breadth_first_search import breadth_first_search
from node import path_states

problem = EightPuzzle(mezclar(4))
solucion = breadth_first_search(problem)
print(len(path_states(solucion)) - 1, "movimientos")
```

> **Restricción.** No se puede modificar el código de los algoritmos, ni el de
> `Node`, `expand` o las estructuras de frontera. Toda la comunicación entre el
> problema y el algoritmo pasa por la interfaz `Problem`. Si algo no encaja, el
> modelado es lo que hay que revisar.

---

## Parte 2 — Aplicación de los algoritmos

Correr los cinco algoritmos vistos en clase —amplitud, costo uniforme,
profundidad, profundidad iterativa y bidireccional— sobre dos tableros: uno a
unos cuatro movimientos del objetivo y el de la figura 3.4, que está a
veintiuno. Informar en una tabla, para cada algoritmo, la **longitud de la
solución**, los **nodos expandidos** y la **profundidad máxima alcanzada**.

Medir no debe alterar lo medido, y una de las cinco búsquedas no termina. Las
dos cosas las resuelve esta función, que también va dada:

```python
from view import Silent


class Tope(Exception):
    """La busqueda se corto: paso el tope de expansiones."""


class Contador(Silent):
    """Cuenta expansiones y profundidad mientras el algoritmo corre."""

    def __init__(self, tope):
        self.pops = 0
        self.hondo = 0
        self.tope = tope

    def POP(self, node, frontier, reached):
        self.pops += 1
        # Cada movimiento cuesta 1, asi que g(n) es la profundidad.
        self.hondo = max(self.hondo, node.PATH_COST)
        if self.pops >= self.tope:
            raise Tope


def medir(algoritmo, *args, tope):
    """Devuelve (solucion, expandidos, mas hondo).

    `solucion` es None si la busqueda no termino.
    """
    contador = Contador(tope)
    try:
        return algoritmo(*args, view=contador), contador.pops, contador.hondo
    except (Tope, RecursionError):
        # RecursionError: la cadena de nodos se hizo tan larga que Python
        # se quedo sin pila. Es la misma conclusion por otra via.
        return None, contador.pops, contador.hondo
```

Se usa así, y sirve para los cinco:

```python
solucion, expandidos, hondo = medir(breadth_first_search, problem, tope=200_000)
solucion, expandidos, hondo = medir(best_first_search, problem, g, tope=200_000)
solucion, expandidos, hondo = medir(bidirectional_search, problem, problem_b,
                                    tope=200_000)
```

`Contador` hereda de `Silent`, la clase de `lib/view.py` que los algoritmos usan
por omisión y que no hace nada. Los algoritmos van avisando lo que hacen —cada
vez que sacan un nodo de la frontera, por ejemplo— y `Contador` se limita a
escuchar y llevar la cuenta. Vale la pena notar por qué la medición se hace así
y no metiendo un contador dentro del algoritmo: **instrumentar no debe modificar
lo instrumentado**, y de hecho la restricción de la Parte 1 lo prohíbe.

A partir de la tabla, responder:

**a)** ¿Por qué amplitud y costo uniforme devuelven aquí la misma solución, y en
el mapa de Rumania no?

**b)** ¿Por qué la búsqueda en profundidad no termina? Distinguir *tardar* de
*no volver*, y explicar qué papel juega —y cuál no alcanza a jugar— la
verificación de ciclos.

**c)** Profundidad iterativa reexpande los niveles superiores en cada iteración.
Cuantificar ese costo con los números obtenidos y explicar qué se gana a cambio.

**d)** ¿Qué condición debe cumplir el problema para recorrerlo hacia atrás, como
necesita la búsqueda bidireccional? ¿La cumple el 8-puzzle? ¿La cumplía el mapa
de Rumania?

**e)** Con factor de ramificación aproximado 3 y soluciones de profundidad 21,
estimar cuántos nodos debería expandir la búsqueda en amplitud. Comparar con lo
medido y explicar la diferencia.

---

## Entrega

Un notebook con el código, la tabla y las respuestas. Se evalúa la argumentación,
no la extensión: un párrafo por pregunta, apoyado en los números que produjo el
propio trabajo.

**Criterios:** corrección del modelado (40 %), mediciones (20 %), calidad de las
respuestas (40 %).
