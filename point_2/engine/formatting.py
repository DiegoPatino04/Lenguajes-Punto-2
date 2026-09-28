"""Notación compartida por la traza, los exportadores y el demo.

QUÉ: cómo se imprime un conjunto de estados, la palabra vacía y las tablas.
CÓMO: funciones puras, sin dependencia de las clases del autómata.
POR QUÉ: el informe exige notación consistente; centralizarla garantiza que un
         conjunto se imprima igual en una traza, una matriz y un registro.
"""
import re

LAMBDA = "λ"      # la palabra vacía (λ para palabras, ε para transiciones)
EMPTY_SET = "∅"


def natural_key(name: str) -> list:
    """Orden natural: q2 antes que q10 (el orden alfabético puro fallaría)."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def sort_states(states) -> list:
    """Estados en orden natural, para que cada conjunto impreso sea determinista."""
    return sorted(states, key=natural_key)


def fmt_set(states) -> str:
    """Formatea un conjunto de estados como {q1, q2}; el vacío se muestra como ∅."""
    if not states:
        return EMPTY_SET
    return "{" + ", ".join(sort_states(states)) + "}"


def fmt_word(word: str) -> str:
    """Muestra la palabra vacía como λ para que sea visible en tablas y registros."""
    return word if word else LAMBDA


def render_table(headers, rows) -> str:
    """Tabla de texto alineada: legible en consola y Markdown válido para el informe."""
    widths = [max(len(str(cell)) for cell in column) for column in zip(headers, *rows)]

    def line(cells) -> str:
        return "| " + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths)) + " |"

    separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    return "\n".join([line(headers), separator] + [line(row) for row in rows])