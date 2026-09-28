"""Construye automaton.json del punto 2.2 como la unión-ε de cada fragmento en rules/.

QUÉ: lee rules/*.json (un autómata pequeño por regla) y escribe automaton.json.
CÓMO: engine.combinators.epsilon_union agrega un estado inicial nuevo q0 con una
      transición ε hacia el inicial de cada regla; los estados se renombran
      q1, q2, ...
POR QUÉ: el lenguaje es "regla 1 O regla 2", así que cada regla se diseña y
         verifica por separado, y una regla nueva se agrega con un archivo más
         en rules/, sin rediseñar un autómata monolítico.

Agregar una regla:
    1. crear rules/<nombre>.json  (su campo "name" es el nombre de la regla),
    2. correr:  python -m p22_arithmetic_properties.build

Ejecutar (desde la carpeta point_2):
    python -m p22_arithmetic_properties.build
"""
import sys
from pathlib import Path

from engine.combinators import epsilon_union, state_mapping
from engine.errors import AutomatonError
from engine.model import load, save

HERE = Path(__file__).parent
RULES_DIR = HERE / "rules"
OUTPUT = HERE / "automaton.json"


def build_union():
    """Devuelve (partes, unión) construidas a partir de cada fragmento, en orden de archivo."""
    files = sorted(RULES_DIR.glob("*.json"))
    if not files:
        raise AutomatonError(f"no se encontraron fragmentos de regla en {RULES_DIR}")
    parts = [load(path) for path in files]
    return parts, epsilon_union("p22_arithmetic_properties", parts, numbered=True)


def main() -> int:
    try:
        parts, union = build_union()
    except AutomatonError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    save(union, OUTPUT)
    print(f"Construido {OUTPUT.name} a partir de {len(parts)} regla(s): "
         f"{[part.name for part in parts]}")
    print("Mapeo de estados (regla.estado -> estado de la unión):")
    for (part_name, state), new_name in state_mapping(parts, numbered=True).items():
        print(f"  {part_name}.{state} -> {new_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())