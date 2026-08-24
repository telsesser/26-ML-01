"""
Dibuja el mapa de Rumania a partir del modelo, para verificar que los
datos que cargamos coinciden con la figura 3.1 del libro.

Uso:  uv run mapa.py
"""

import matplotlib.pyplot as plt

from romania import COORDENADAS, RUMANIA, costo_del_camino


def dibujar(grafo, camino=None, titulo="Rumania", archivo="mapa.png"):
    fig, ax = plt.subplots(figsize=(11, 7))

    # Carreteras.
    for a, b, costo in grafo.aristas():
        (xa, ya), (xb, yb) = COORDENADAS[a], COORDENADAS[b]
        ax.plot([xa, xb], [ya, yb], color="#999", lw=1.2, zorder=1)
        ax.text((xa + xb) / 2, (ya + yb) / 2, str(costo),
                fontsize=8, color="#444", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"),
                zorder=2)

    # Camino resaltado (si se pide).
    if camino:
        xs = [COORDENADAS[c][0] for c in camino]
        ys = [COORDENADAS[c][1] for c in camino]
        ax.plot(xs, ys, color="#d62728", lw=3, alpha=0.7, zorder=3)

    # Ciudades.
    for ciudad, (x, y) in COORDENADAS.items():
        en_camino = camino and ciudad in camino
        ax.scatter([x], [y], s=90, marker="s", zorder=4,
                   color="#d62728" if en_camino else "#8b1a1a",
                   edgecolors="black", linewidths=0.6)
        ax.text(x, y + 13, ciudad, fontsize=9, ha="center",
                fontweight="bold" if en_camino else "normal", zorder=5)

    ax.set_title(titulo)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(archivo, dpi=140)
    print(f"guardado: {archivo}")


if __name__ == "__main__":
    optimo = ["Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"]
    dibujar(RUMANIA, titulo="Rumania - Russell & Norvig fig. 3.1",
            archivo="mapa.png")
    dibujar(RUMANIA, camino=optimo,
            titulo=f"Camino optimo Arad -> Bucharest ({costo_del_camino(RUMANIA, optimo)} km)",
            archivo="mapa_optimo.png")
