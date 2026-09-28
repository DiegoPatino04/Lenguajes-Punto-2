"""M3 - Función de transición extendida δ*, movimiento de un símbolo y aceptación.

QUÉ
    δ*(q, w) = conjunto de estados en que puede estar el autómata tras leer toda
    la palabra w partiendo de q, combinando transiciones ε y de símbolo. Se
    define por recursión sobre la longitud de w [1, Sec. 2.5]:

        δ*(q, λ)  = ECLOSE({q})
        δ*(q, wa) = ECLOSE( ⋃ { δ(p, a) : p ∈ δ*(q, w) } )

    (λ es la palabra vacía.) Una palabra w se acepta si y solo si
    δ*(q0, w) ∩ F ≠ ∅.

CÓMO
    Como un NFA-ε puede estar en varios estados a la vez, la "configuración
    actual" es un CONJUNTO de estados. Leer un símbolo son dos fases:
        move    : unión de δ(p, a) sobre los estados activos p  (consume el símbolo)
        closure : ECLOSE del resultado                          (movimientos ε gratis)
    La recursión se vuelve un ciclo sobre los símbolos de la palabra.

POR QUÉ
    * Seguir todas las ramas a la vez (en vez de adivinar una) es la forma
      estándar de simular el no determinismo sin retroceso; el costo es
      O(|w| · |Q|²) como máximo, sin importar cuántas ramas existan.
    * El ciclo se detiene antes si el conjunto activo queda vacío: desde ∅
      ninguna continuación puede recuperarse.
    * La palabra se valida ANTES de simular. Un símbolo fuera de Σ es un error
      de uso, no un rechazo, así que lanza InvalidWordError y muestra Σ.

[1] J. E. Hopcroft, R. Motwani y J. D. Ullman, Introduction to Automata Theory,
    Languages, and Computation, 3rd ed. Pearson, 2007.
"""
from engine.closure import epsilon_closure
from engine.errors import InvalidWordError
from engine.model import EPSILON, NFAe


def validate_word(automaton: NFAe, word: str) -> None:
    """Lanza InvalidWordError (mostrando Σ) si `word` usa un símbolo fuera de Σ."""
    bad = [(i, char) for i, char in enumerate(word) if char not in automaton.alphabet]
    if not bad:
        return
    listing = ", ".join(f"{char!r} en la posición {i + 1}" for i, char in bad)
    hint = ""
    if any(char == EPSILON for _i, char in bad):
        hint = " (ε etiqueta transiciones; la palabra vacía se escribe como cadena vacía)"
    raise InvalidWordError(
        f"Palabra inválida: {listing}. El alfabeto de {automaton.name!r} es "
        f"Σ = {{{', '.join(automaton.alphabet)}}}{hint}"
    )


def initial_states(automaton: NFAe) -> frozenset:
    """δ*(q0, λ): la configuración antes de leer nada."""
    return epsilon_closure(automaton, {automaton.start})


def move(automaton: NFAe, states, symbol: str) -> frozenset:
    """⋃ δ(p, symbol) para p en `states`, SIN la clausura (el conjunto "después de δ")."""
    reached = set()
    for state in states:
        reached |= automaton.targets(state, symbol)
    return frozenset(reached)


def step(automaton: NFAe, states, symbol: str):
    """Lee un símbolo desde una configuración. Devuelve (moved, closed)."""
    moved = move(automaton, states, symbol)
    return moved, epsilon_closure(automaton, moved)


def extended_delta(automaton: NFAe, word: str, from_state: str = None) -> frozenset:
    """δ*(from_state, word); `from_state` por defecto es el estado inicial q0."""
    validate_word(automaton, word)
    origin = automaton.start if from_state is None else from_state
    current = epsilon_closure(automaton, {origin})
    for symbol in word:
        if not current:          # configuración muerta: ningún estado puede recuperarse
            break
        current = step(automaton, current, symbol)[1]
    return current


def accepts(automaton: NFAe, word: str) -> bool:
    """True si y solo si δ*(q0, word) contiene al menos un estado final."""
    return bool(extended_delta(automaton, word) & automaton.finals)