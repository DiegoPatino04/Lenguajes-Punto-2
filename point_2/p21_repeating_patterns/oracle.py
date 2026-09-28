"""Referencia independiente del punto 2.1 (sin autómatas).

L = (01)+ ∪ (010)+: "01" repetido una o más veces, O "010" repetido una o más
veces. Una palabra que mezcla ambos patrones (ej. 01001, 01010) NO pertenece a L.
"""
import re

_PATTERN = re.compile(r"(01)+|(010)+")


def in_language(word: str) -> bool:
    """True si y solo si `word` pertenece a L = (01)+ ∪ (010)+."""
    return _PATTERN.fullmatch(word) is not None