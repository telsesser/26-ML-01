# Resolución de problemas mediante búsqueda

Material de clase sobre los algoritmos de búsqueda del capítulo 3 de
Russell & Norvig, *Artificial Intelligence: A Modern Approach*, 4ª edición.

Las búsquedas se pueden recorrer paso a paso, con el mapa o con el árbol de
búsqueda.

## Las tres carpetas

| carpeta | qué hay |
| --- | --- |
| [`0-lib/`](0-lib/) | lo común: `Problem`, `Node`, la frontera, el narrador (`view`, `web`) y los cinco algoritmos. Nada de esto sabe de Rumania ni del 8-puzzle. |
| [`1-romania/`](1-romania/) | **búsqueda no informada** sobre el mapa de Rumania: ir de Arad a Bucharest. Es el sitio Quarto que se publica. |
| [`2-8puzzle/`](2-8puzzle/) | **el 8-puzzle**: los mismos algoritmos sobre un problema donde el grafo no existe y el espacio tiene 181.440 estados. |

Cada carpeta de problema tiene su notebook y las piezas que solo le sirven a
ese problema: `1-romania/romania.py` es el mapa; `2-8puzzle/puzzle.py`,
`web_puzzle.py` y `plantilla_puzzle.html` son el tablero y su dibujo.

## Cómo se corre

```bash
uv sync

# el sitio de la clase de Rumania
cd 1-romania && quarto preview

# los algoritmos solos, contra el mapa de Rumania
uv run python 0-lib/breadth_first_search.py --view

# la tabla comparativa del 8-puzzle
cd 2-8puzzle && uv run python puzzle.py
```

Las páginas paso a paso que escriben esos scripts van a `salidas/`, que no se
versiona.

## Publicar

El sitio sale de `1-romania/`, no de la raíz:

```bash
cd 1-romania && quarto publish gh-pages
```
