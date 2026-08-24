"""
El mapa de Rumania  -  Russell & Norvig, figuras 3.1 y 3.22
"""

from collections import defaultdict


class Map:
    """Ciudades unidas por rutas con distancia."""

    def __init__(self, links, locations=None, straight_line_distance=None,
                 directed=False):
        self.distances = {}
        self.neighbors = defaultdict(list)
        for (city1, city2, distance) in links:
            self.distances[city1, city2] = distance
            self.neighbors[city1].append(city2)
            if not directed:
                self.distances[city2, city1] = distance
                self.neighbors[city2].append(city1)
        # Orden alfabetico: hace que la busqueda sea reproducible.
        for city in self.neighbors:
            self.neighbors[city].sort()
        self.locations = locations or {}
        self.straight_line_distance = straight_line_distance or {}


# Las 23 rutas del mapa, con su distancia en km.
links = [
    ("Arad", "Zerind", 75),          ("Arad", "Sibiu", 140),
    ("Arad", "Timisoara", 118),      ("Bucharest", "Fagaras", 211),
    ("Bucharest", "Pitesti", 101),   ("Bucharest", "Giurgiu", 90),
    ("Bucharest", "Urziceni", 85),   ("Craiova", "Drobeta", 120),
    ("Craiova", "Rimnicu", 146),     ("Craiova", "Pitesti", 138),
    ("Drobeta", "Mehadia", 75),      ("Eforie", "Hirsova", 86),
    ("Fagaras", "Sibiu", 99),        ("Hirsova", "Urziceni", 98),
    ("Iasi", "Vaslui", 92),          ("Iasi", "Neamt", 87),
    ("Lugoj", "Timisoara", 111),     ("Lugoj", "Mehadia", 70),
    ("Oradea", "Zerind", 71),        ("Oradea", "Sibiu", 151),
    ("Pitesti", "Rimnicu", 97),      ("Rimnicu", "Sibiu", 80),
    ("Urziceni", "Vaslui", 142),
]

# Distancia en linea recta hasta Bucharest: la heuristica h(n).
straight_line_distance = {
    "Arad": 366,    "Bucharest": 0,   "Craiova": 160,  "Drobeta": 242,
    "Eforie": 161,  "Fagaras": 176,   "Giurgiu": 77,   "Hirsova": 151,
    "Iasi": 226,    "Lugoj": 244,     "Mehadia": 241,  "Neamt": 234,
    "Oradea": 380,  "Pitesti": 100,   "Rimnicu": 193,  "Sibiu": 253,
    "Timisoara": 329, "Urziceni": 80, "Vaslui": 199,   "Zerind": 374,
}

# Posicion de cada ciudad. Solo sirve para dibujar.
locations = {
    "Arad": (91, 492),      "Bucharest": (400, 327),  "Craiova": (253, 288),
    "Drobeta": (165, 299),  "Eforie": (562, 293),     "Fagaras": (305, 449),
    "Giurgiu": (375, 270),  "Hirsova": (534, 350),    "Iasi": (473, 506),
    "Lugoj": (165, 379),    "Mehadia": (168, 339),    "Neamt": (406, 537),
    "Oradea": (131, 571),   "Pitesti": (320, 368),    "Rimnicu": (233, 410),
    "Sibiu": (207, 457),    "Timisoara": (94, 410),   "Urziceni": (456, 350),
    "Vaslui": (509, 444),   "Zerind": (108, 531),
}

romania = Map(links, locations, straight_line_distance)
