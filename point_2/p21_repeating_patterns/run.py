"""Ejecutable del punto 2.1. Ejecutar desde la carpeta point_2:

    python -m p21_repeating_patterns.run                 corrida completa (log + diagrama)
    python -m p21_repeating_patterns.run --word 010010    traza solo esta palabra
    python -m p21_repeating_patterns.run --edges          incluye también las aristas disparadas

Lenguaje: L = (01)+ ∪ (010)+, es decir, "01" repetido una o más veces, O
"010" repetido una o más veces (una palabra no puede mezclar ambos patrones).
"""
import sys
from pathlib import Path

from engine.report import run_point

HERE = Path(__file__).parent

# Exigido por el enunciado: 3 palabras válidas y 2 inválidas.
VALID = ["010101",      # patrón A: "01" tres veces (ejemplo del enunciado)
         "010010",      # patrón B: "010" dos veces  (ejemplo del enunciado)
         "010010010"]   # patrón B: "010" tres veces
INVALID = ["0110",      # contiene "11": ningún patrón lo produce
           "10"]        # empieza en 1

# No cuenta en las 3+2 exigidas. Se deja como evidencia adicional; ver design.md.
EXTRA = [("0101010", "el enunciado lo lista como válido, pero no es una repetición de "
                     "01 ni de 010; el autómata sigue la definición formal")]

if __name__ == "__main__":
    sys.exit(run_point(HERE, "Punto 2.1 - L = (01)+ ∪ (010)+", VALID, INVALID, EXTRA,
                       diagram_title="p21_diagram"))