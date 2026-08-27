# Solucionario — El 8-puzzle

*Uso interno. Las respuestas son de referencia: lo que se evalúa es el
argumento, no la coincidencia literal.*

## Mediciones de referencia

Con `mezclar(4)` reemplazado por el tablero chico del notebook y la figura 3.4.
Los números salen de la implementación de referencia; una implementación
correcta con otro orden de acciones puede dar conteos algo distintos, pero no
otro orden de magnitud ni otra longitud de solución.

**Tablero chico — a 4 movimientos** (tope 1.000)

| algoritmo | pasos | expande | más hondo |
|---|---:|---:|---:|
| amplitud | 4 | 13 | 3 |
| costo uniforme | 4 | 26 | 4 |
| profundidad | — | no termina | 633 |
| profundidad iterativa | 4 | 51 | 4 |
| bidireccional | 4 | 10 | 2 |

**Figura 3.4 — a 21 movimientos** (tope 200.000)

| algoritmo | pasos | expande | más hondo |
|---|---:|---:|---:|
| amplitud | 21 | 47.514 | 20 |
| costo uniforme | 21 | 64.732 | 21 |
| profundidad | — | no termina | — |
| profundidad iterativa | — | llega al tope | 18 |
| bidireccional | 21 | 1.477 | 10 |

Datos del espacio de estados, útiles para corregir: 181.440 estados
alcanzables, diámetro 31, ramificación media 2,67 (2 en las esquinas, 3 en los
bordes, 4 en el centro), 54.802 estados a distancia ≤ 20 del objetivo.

---

## a) Amplitud y costo uniforme

**Coinciden porque todos los pasos cuestan 1.** Con costo unitario el costo de
un camino es su profundidad, así que «la solución más superficial» y «la
solución más barata» son la misma cosa: los dos criterios de orden colapsan en
uno. En Rumania los arcos son kilómetros y no coinciden:

```
amplitud   Arad -> Sibiu -> Fagaras -> Bucharest              450 km, 3 pasos
uniforme   Arad -> Sibiu -> Rimnicu -> Pitesti -> Bucharest   418 km, 4 pasos
```

Amplitud minimiza *cantidad de ciudades* y costo uniforme minimiza
*kilómetros*. En el 8-puzzle no hay nada análogo a un arco largo, y por eso el
problema no distingue entre los dos algoritmos.

**Lo que sí los distingue es el trabajo:** 13 expansiones contra 26 en el
tablero chico, 47.514 contra 64.732 en la figura 3.4. La causa es *dónde* se
hace la prueba de objetivo. Amplitud la hace al **generar** el hijo, y puede
hacerlo porque con costo unitario el primer objetivo que aparece es
necesariamente el más superficial. Costo uniforme la hace al **sacar** el nodo
de la frontera, porque en el caso general un objetivo recién generado puede ser
caro y todavía puede aparecer otro más barato. Esa cautela cuesta expandir
entero el nivel anterior. Aquí es cautela desperdiciada, pero el algoritmo no
sabe que los costos son unitarios: no puede saberlo, sólo ve la interfaz.

Una respuesta que diga sólo «porque los costos son uniformes» está bien pero
incompleta; la buena observa además que el ahorro de amplitud viene de una
prueba de objetivo que costo uniforme no puede permitirse.

## b) Por qué no termina la búsqueda en profundidad

**Tardar** es recorrer un espacio grande hasta agotarlo: termina, más tarde o
más temprano. **No volver** es descender por una rama que no se acaba, y es lo
que pasa acá. La evidencia está en la medición: tras 1.000 expansiones sobre un
tablero **que se resuelve en 4 movimientos**, el nodo más hondo estaba a 633.
No es que le falte poco, es que va en la dirección equivocada y no tiene motivo
para volver. En profundidad la frontera es una pila: el último hijo generado es
el próximo en expandirse, así que la búsqueda se compromete con la primera rama
y sólo retrocede cuando se le agota — y en el 8-puzzle no se le agota nunca en
ningún plazo útil.

El espacio es finito (181.440 estados), y eso confunde: parecería que
necesariamente termina. No, porque lo que la búsqueda recorre no son estados
sino **caminos**, y la cantidad de caminos simples en este grafo es
astronómica.

**El papel de la verificación de ciclos.** `is_cycle` compara el estado del
nodo con el de sus ancestros: evita que la búsqueda quede oscilando entre dos
tableros —mover el hueco a la derecha y de vuelta a la izquierda, para
siempre—. Sin eso no se sale de un ciclo de largo 2.

Lo que **no** hace, y es el punto de la pregunta, son tres cosas:

1. No acota la profundidad. Un camino sin estados repetidos puede tener 181.439
   pasos.
2. No es un `reached` global: sólo mira la rama actual. Un estado ya visitado en
   otra rama se vuelve a expandir sin objeción.
3. En esta implementación mira **sólo los últimos 30 ancestros** (`is_cycle(node,
   k=30)`). Un ciclo más largo que 30 pasa desapercibido, de modo que ni
   siquiera está garantizado que los caminos sean simples.

Por (3), en rigor, la búsqueda puede no terminar *nunca*, no sólo tardar
demasiado. Conviene que alguien lo note; el límite `k` es la clase de detalle
que se pasa por alto al leer el pseudocódigo del libro.

Lo que se corta en la práctica es otra cosa: o el tope de expansiones, o
`RecursionError`, cuando la cadena de nodos se hace tan larga que Python se
queda sin pila. Las dos son formas de decir lo mismo.

## c) Cuánto repite profundidad iterativa

En el tablero chico: **51 expansiones contra 13** de amplitud para encontrar la
misma solución de 4 movimientos, casi cuatro veces el trabajo. Desglosado por
iteración:

| límite | expande | acumulado |
|---:|---:|---:|
| l = 0 | 3 | 3 |
| l = 1 | 9 | 12 |
| l = 2 | 21 | 33 |
| l = 3 | 18 | 51 |

(Encuentra el objetivo en la iteración `l = 3` porque, como amplitud, prueba el
objetivo al generar: lo ve al crear el hijo de profundidad 4.)

**Acá conviene ser preciso, porque la respuesta fácil es incorrecta.** El exceso
no viene todo de repetir iteraciones. Una sola búsqueda limitada a `l = 4`, sin
ninguna repetición, ya expande 30 nodos contra los 13 de amplitud. O sea:

- **2,3×** por no llevar `reached`: profundidad limitada re-expande estados que
  ya vio en otra rama, cosa que amplitud nunca hace.
- **1,7×** por rehacer los niveles superiores en cada iteración.

El segundo factor es el que suele citarse y es el menor de los dos. En teoría
tiende a `b/(b-1)` ≈ 1,5 para `b` ≈ 2,7: el nivel más profundo domina el conteo,
así que rehacer los de arriba es barato. Se nota poco justamente porque el árbol
crece exponencialmente.

En la figura 3.4 el trabajo se vuelve prohibitivo: llega al tope de 200.000
expansiones sin terminar, mientras amplitud resuelve con 47.514. Ahí el factor
que manda es el primero: sin `reached`, a profundidad 21 se re-expande el mismo
tablero un número enorme de veces.

**Qué se gana: memoria.** Amplitud guarda la frontera y `reached` —decenas de
miles de tableros en la figura 3.4—; profundidad iterativa guarda un camino y
los hermanos pendientes, O(b·d), unas decenas de nodos. Y conserva lo que
profundidad sola pierde: sigue siendo completa y, con costos unitarios, óptima.
Es el algoritmo que se elige cuando el espacio no entra en memoria.

## d) La condición para la búsqueda bidireccional

Hace falta poder **recorrer el problema hacia atrás**: dado un estado, saber de
qué estados se llega a él. Formalmente, poder calcular predecesores; en la
práctica, que las acciones sean invertibles. Se necesita además un **estado**
objetivo explícito y no sólo una prueba de objetivo: para arrancar el frente de
atrás hay que saber desde dónde.

**El 8-puzzle la cumple, y de la mejor manera posible.** Cada movimiento del
hueco se deshace con el movimiento opuesto, y el conjunto de acciones es
simétrico, así que el problema al revés *es el mismo problema* con `INITIAL` y
`GOAL` intercambiados:

```python
problem_b = EightPuzzle(GOAL, inicio)
```

No hay que escribir una sola línea de código nuevo. Eso no es casual: es
consecuencia de haber modelado las acciones como movimientos del hueco.

**Rumania también la cumplía**, y por la misma razón: las rutas son de doble
mano y la distancia es simétrica. El grafo no dirigido es su propio inverso.

El caso interesante es el que no la cumple, y conviene mencionarlo al corregir:
un problema con acciones irreversibles (romper algo, gastar un recurso) o con
objetivo definido por una propiedad —«cualquier tablero con la fila de arriba
ordenada»— no admite este algoritmo tal como está.

**El resultado justifica el esfuerzo:** 1.477 expansiones contra 47.514, 32
veces menos. Dos búsquedas de profundidad ~10 en vez de una de 21, y el árbol
crece exponencialmente: `2·b^(d/2)` contra `b^d`. Los números lo confirman con
precisión: hay 706 estados a distancia ≤ 10 del objetivo, y 2 × 706 = 1.412,
casi exactamente lo medido.

## e) La estimación y por qué falla

La estimación directa, con `b` ≈ 3 y `d` = 21:

```
3^21 ≈ 1,05 × 10^10 nodos
```

Lo medido son **47.514**. Cinco órdenes de magnitud menos.

La diferencia **no** es que la estimación esté mal calculada: es que `b^d` cuenta
otra cosa. Cuenta **nodos de un árbol de búsqueda**, es decir *caminos*. Y hay
del orden de 10^10 caminos de largo 21, es cierto. Pero la búsqueda en amplitud
lleva `reached` y **nunca expande dos veces el mismo estado**: cuenta *estados*,
y estados sólo hay 181.440.

La cota real es entonces `mín(b^d, |S|)`, y acá el mínimo lo pone el espacio de
estados por amplísimo margen. Se puede afinar todavía más: hay 54.802 estados a
distancia ≤ 20 del objetivo, y 47.514 —lo medido— es consistente con eso,
porque la búsqueda se detiene al generar el objetivo, sin llegar a expandir el
nivel 20 entero.

Dos observaciones que suman:

- `b` ≈ 3 es generoso. La ramificación media real es **2,67**: el hueco tiene 2
  movimientos en las esquinas, 3 en los bordes y 4 en el centro.
- La moraleja es la que atraviesa el capítulo: **la diferencia entre búsqueda en
  árbol y búsqueda en grafo no es un detalle de implementación.** Es la
  diferencia entre 10^10 y 10^4. Y es exactamente lo que le falta a la búsqueda
  en profundidad de la pregunta b), que no lleva `reached` y por eso se hunde en
  un espacio de apenas 181.440 estados.
