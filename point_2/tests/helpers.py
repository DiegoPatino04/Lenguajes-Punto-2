"""Ayuda compartida por los tests: comparación exhaustiva autómata vs oráculo."""
import itertools

from engine.extended_delta import accepts


def all_words(alphabet, max_len: int):
    """Toda palabra sobre `alphabet` de longitud 0..max_len (la vacía primero)."""
    for length in range(max_len + 1):
        for chars in itertools.product(alphabet, repeat=length):
            yield "".join(chars)


def verify_against_oracle(automaton, oracle, max_len: int = 12):
    """Devuelve (revisadas, discrepancias); cada discrepancia es (palabra, esperado, obtenido)."""
    checked, mismatches = 0, []
    for word in all_words(automaton.alphabet, max_len):
        checked += 1
        expected, obtained = oracle(word), accepts(automaton, word)
        if expected != obtained:
            mismatches.append((word, expected, obtained))
    return checked, mismatches