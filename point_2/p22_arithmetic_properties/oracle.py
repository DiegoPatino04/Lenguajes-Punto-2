"""Referencia independiente del punto 2.2 (sin autómatas).

L = { w : ceros(w) impar  O  unos(w) múltiplo de 3 }

Decisión de diseño: "0 unos" NO cuenta como múltiplo de 3 (ver rules/ones_multiple_of_3.json,
donde el estado "sin_unos" no es final). Para invertir la decisión, poner
ALLOW_ZERO_ONES = True aquí Y agregar "sin_unos" a "finals" en ese archivo.
"""

ALLOW_ZERO_ONES = False


def odd_zeros(word: str) -> bool:
    return word.count("0") % 2 == 1


def ones_multiple_of_3(word: str) -> bool:
    ones = word.count("1")
    return ones % 3 == 0 and (ones > 0 or ALLOW_ZERO_ONES)


RULES = {"odd_zeros": odd_zeros, "ones_multiple_of_3": ones_multiple_of_3}


def in_language(word: str) -> bool:
    return any(rule(word) for rule in RULES.values())