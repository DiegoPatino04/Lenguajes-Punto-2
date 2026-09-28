"""M6 - Combinadores: construir un autómata más grande a partir de otros más chicos.

QUÉ
    Construye un NFA-ε que acepta L(R1) ∪ L(R2) ∪ ... a partir de autómatas
    independientes.

CÓMO
    Unión al estilo de Thompson [1], [2, Sec. 1.2]: un estado inicial NUEVO con
    una transición ε hacia el inicial de cada parte; los finales de la unión son
    los finales de todas las partes. Los estados se renombran para que ninguna
    parte choque con otra:
        numbered=False -> "<parte>_<estado>"   (se puede rastrear al fragmento)
        numbered=True  -> q1, q2, ...          (compacto; q0 es el nuevo inicio)

POR QUÉ
    El punto 2.2 define el lenguaje como "regla 1 O regla 2". Modelar cada regla
    como su propio autómata pequeño mantiene cada una simple de diseñar y de
    verificar, y una regla nueva se agrega con un archivo más, sin rediseñar un
    autómata monolítico. Las transiciones ε son lo que hace trivial esta unión:
    una construcción producto necesitaría |Q1|·|Q2| estados.

[1] K. Thompson, "Programming techniques: Regular expression search algorithm,"
    Commun. ACM, vol. 11, no. 6, pp. 419-422, 1968.
[2] M. Sipser, Introduction to the Theory of Computation, 3rd ed. Cengage, 2012.
"""
from engine.errors import InvalidAutomatonError
from engine.model import EPSILON, NFAe, build


def state_mapping(parts: list, numbered: bool = False) -> dict:
    """Mapea (nombre de parte, estado original) -> nombre de estado dentro de la unión."""
    mapping, counter = {}, 1
    for part in parts:
        for state in part.states:
            mapping[(part.name, state)] = f"q{counter}" if numbered else f"{part.name}_{state}"
            counter += 1
    return mapping


def epsilon_union(name: str, parts: list, start_name: str = "q0",
                  numbered: bool = False) -> NFAe:
    """NFA-ε para la unión de los lenguajes de `parts` (ver docstring del módulo)."""
    names = [part.name for part in parts]
    if len(set(names)) != len(names):
        raise InvalidAutomatonError(f"Los nombres de las partes deben ser únicos, se recibió {names}")
    mapping = state_mapping(parts, numbered)

    states, alphabet, finals, transitions = [start_name], [], [], []
    for part in parts:
        def rename(state, owner=part.name):
            return mapping[(owner, state)]

        states += [rename(state) for state in part.states]
        alphabet += [symbol for symbol in part.alphabet if symbol not in alphabet]
        finals += [rename(state) for state in sorted(part.finals)]
        transitions.append([start_name, EPSILON, rename(part.start)])
        transitions += [[rename(s), sym, rename(t)] for s, sym, t in part.transitions()]
    return build(name, states, alphabet, start_name, finals, transitions)