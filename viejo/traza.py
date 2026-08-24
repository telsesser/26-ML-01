"""
Eventos de una busqueda.

Los algoritmos no imprimen ni dibujan: emiten eventos. Una traza es la
lista completa de lo que hizo el algoritmo, paso a paso, y es un dato
serializable. Con la misma traza despues alimentamos la consola, una
figura de matplotlib o un visualizador interactivo.

La ventaja pedagogica: se ve que todos los algoritmos de busqueda son
el mismo bucle, y que lo unico que cambia es el orden en que sacan
nodos de la frontera.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from romania import Nodo


@dataclass
class Evento:
    """Base. Cada evento lleva una foto de la frontera para poder
    reconstruir el estado de la busqueda en cualquier instante."""
    paso: int = field(default=0, kw_only=True)
    frontera: list[tuple[str, float]] = field(default_factory=list, kw_only=True)
    alcanzados: list[str] = field(default_factory=list, kw_only=True)


@dataclass
class Inicio(Evento):
    """Arranca la busqueda. frontier <- {nodo inicial}"""
    nodo: Nodo = None
    f: float = 0.0

    def __str__(self):
        return f"INICIO   {self.nodo.estado} (f={self.f:g})"


@dataclass
class Extraer(Evento):
    """node <- POP(frontier). El nodo elegido para expandir."""
    nodo: Nodo = None
    f: float = 0.0

    def __str__(self):
        return (f"EXTRAER  {self.nodo.estado:<15} f={self.f:<6g} "
                f"g={self.nodo.costo_camino:g}")


@dataclass
class Obsoleto(Evento):
    """El nodo extraido quedo obsoleto: ya encontramos un camino mejor
    a esa ciudad mientras esperaba en la cola. Se descarta sin expandir."""
    nodo: Nodo = None
    mejor: float = 0.0

    def __str__(self):
        return (f"  obsoleto {self.nodo.estado}: g={self.nodo.costo_camino:g} "
                f"pero ya conocemos {self.mejor:g}")


@dataclass
class Generar(Evento):
    """Un hijo producido por EXPAND, con la decision que se tomo.

    decision:
      'nuevo'      - ciudad nunca alcanzada, entra a la frontera
      'mejora'     - la alcanzamos por un camino mas barato, entra de nuevo
      'descartado' - ya teniamos un camino igual o mejor, se tira
    """
    nodo: Nodo = None
    f: float = 0.0
    decision: str = "nuevo"
    costo_previo: float | None = None

    def __str__(self):
        marca = {"nuevo": "+", "mejora": "^", "descartado": "-"}[self.decision]
        linea = (f"  {marca} {self.nodo.estado:<15} g={self.nodo.costo_camino:<6g} "
                 f"f={self.f:g}")
        if self.costo_previo is not None:
            linea += f"  (antes {self.costo_previo:g})"
        return linea


@dataclass
class Solucion(Evento):
    """IS-GOAL dio verdadero. Terminamos."""
    nodo: Nodo = None

    def __str__(self):
        return (f"SOLUCION {' -> '.join(self.nodo.camino())}\n"
                f"         costo = {self.nodo.costo_camino:g}")


@dataclass
class Fallo(Evento):
    """La frontera se vacio sin encontrar el objetivo."""

    def __str__(self):
        return "FALLO    frontera vacia, no hay solucion"


# --------------------------------------------------------------------------
# Utilidades para consumir trazas
# --------------------------------------------------------------------------

def ejecutar(busqueda) -> tuple[Nodo | None, list[Evento]]:
    """Consume un algoritmo (generador de eventos) hasta el final.

    Devuelve (nodo_solucion_o_None, traza_completa).
    """
    traza = list(busqueda)
    final = traza[-1] if traza else None
    solucion = final.nodo if isinstance(final, Solucion) else None
    return solucion, traza


def imprimir(busqueda, mostrar_frontera: bool = False) -> Nodo | None:
    """Corre la busqueda mostrando cada paso por consola."""
    solucion = None
    for ev in busqueda:
        print(ev)
        if mostrar_frontera and isinstance(ev, (Inicio, Extraer)):
            cola = ", ".join(f"{c}:{v:g}" for c, v in ev.frontera)
            print(f"           frontera [{cola}]")
        if isinstance(ev, Solucion):
            solucion = ev.nodo
    return solucion


def resumen(traza: list[Evento]) -> dict:
    """Metricas para comparar algoritmos entre si."""
    expandidos = [e for e in traza if isinstance(e, Extraer)]
    generados = [e for e in traza if isinstance(e, Generar)]
    final = traza[-1] if traza else None
    return {
        "expandidos": len(expandidos),
        "generados": len(generados),
        "descartados": sum(1 for e in generados if e.decision == "descartado"),
        "obsoletos": sum(1 for e in traza if isinstance(e, Obsoleto)),
        "frontera_max": max((len(e.frontera) for e in traza), default=0),
        "costo": final.nodo.costo_camino if isinstance(final, Solucion) else None,
        "camino": final.nodo.camino() if isinstance(final, Solucion) else None,
    }
