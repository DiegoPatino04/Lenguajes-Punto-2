"""Ejecutable del punto 2.2. Ejecutar desde la carpeta point_2:

    python -m p22_arithmetic_properties.build             (solo tras editar rules/)
    python -m p22_arithmetic_properties.run                corrida completa (log + diagrama)
    python -m p22_arithmetic_properties.run --word 0111    traza solo esta palabra

Lenguaje: cantidad de ceros impar, O cantidad de unos múltiplo de 3.
"""
import sys
from pathlib import Path

from engine.report import run_point

HERE = Path(__file__).parent

# Exigido por el enunciado: 3 palabras válidas y 2 inválidas.
VALID = ["101",   # ejemplo del enunciado: 1 cero (impar) y 2 unos -> válida solo por R1
         "111",   # 0 ceros, 3 unos -> válida solo por R2
         "0111"]  # 1 cero (impar) y 3 unos -> válida por ambas reglas
INVALID = ["1111",  # ejemplo del enunciado: 0 ceros, 4 unos -> ninguna regla se cumple
           "0110"]  # 2 ceros (par), 2 unos (no múltiplo de 3)

# No cuentan en las 3+2 exigidas: dependen de la decisión "¿0 unos es múltiplo de 3?"
EXTRA = [(w, "depende de si '0 unos' cuenta como múltiplo de 3; ver design.md")
        for w in ["", "00", "0000"]]

if __name__ == "__main__":
    sys.exit(run_point(HERE, "Punto 2.2 - ceros impares O unos múltiplo de 3", VALID, INVALID,
                       EXTRA, diagram_title="p22_diagram"))