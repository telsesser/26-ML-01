"""
El view web del 8-puzzle.

Es el mismo grabador que web.Web -- hereda de el -- con dos cambios, que
son los dos unicos lugares donde Web sabia algo de Rumania:

    datos()   no manda el mapa: en el 8-puzzle los estados no tienen
              coordenadas, asi que no hay mapa que dibujar.
    html()    usa plantilla_puzzle.html, que dibuja tableros de 3x3
              donde la otra plantilla dibujaba nombres de ciudades.

Todo lo demas se recicla tal cual, incluido lo mas delicado: _veredicto,
que decide si un hijo es nuevo, una mejora o un descarte, y la marca de
los nodos obsoletos en la frontera.

Lo que hace que el resto funcione sin cambios es que un estado del
8-puzzle es una tupla de nueve numeros, y json.dumps escribe una tupla
como un array. Del lado de JavaScript llega [1,2,3,4,8,5,7,6,0], que es
lo que la plantilla necesita para dibujar el tablero.
"""

import json
from pathlib import Path

from web import Web

PLANTILLA = Path(__file__).with_name("plantilla_puzzle.html")


class WebPuzzle(Web):
    """Graba una busqueda sobre el 8-puzzle y escribe la pagina."""

    def _datos(self, node):
        # La accion importa mas aca que en Rumania: alla se lee en el
        # nombre de la ciudad a la que se llega, aca no se ve en el
        # tablero cual de las cuatro se aplico.
        return super()._datos(node) | {"action": node.ACTION}

    def datos(self):
        return {
            "name": self.name,
            "label": self.label,
            "keyName": self.key_name,
            "initial": self.problem.INITIAL,
            "goal": self.problem.GOAL,
            "frames": self.frames,
        }

    def html(self):
        """La pagina entera, en un string."""
        return PLANTILLA.read_text(encoding="utf-8").replace(
            "__DATA__", json.dumps(self.datos(), ensure_ascii=False)
        )
