"""M1 - Modelo de datos de un NFA-ε: la 5-tupla M = (Q, Σ, δ, q0, F) y su validación.

QUÉ
    Traducción directa de la definición formal de un NFA con transiciones ε
    [1, Sec. 2.5]:
        Q  conjunto finito de estados        -> `states`   (tupla, conserva el orden)
        Σ  alfabeto de entrada               -> `alphabet` (tupla de un carácter c/u)
        δ  Q × (Σ ∪ {ε}) -> P(Q)            -> `delta`    (diccionario, ver abajo)
        q0 estado inicial, q0 ∈ Q            -> `start`
        F  estados finales, F ⊆ Q            -> `finals`

CÓMO
    * δ es un diccionario cuya CLAVE es el par (estado, símbolo) —el dominio
      Q × (Σ ∪ {ε})— y cuyo VALOR es un frozenset de estados —el codominio P(Q)—.
      Una consulta δ(q, a) es entonces una sola búsqueda.
    * Un par no almacenado significa δ(q, a) = ∅. `targets()` devuelve el
      frozenset vacío en ese caso, lo que hace de δ una función TOTAL como exige
      la definición, mientras el archivo solo lista las transiciones que existen.
    * ε es la constante EPSILON = "ε". Como cada símbolo de Σ debe ser un único
      carácter distinto de "ε", nunca puede confundirse con un símbolo de entrada.
    * La definición vive en un archivo JSON (una lista de tripletas
      [origen, símbolo, destino]) porque el autómata es el objeto que se
      documenta y debe sobrevivir entre ejecuciones; las palabras de prueba y
      las trazas no necesitan guardarse.

POR QUÉ se valida aquí
    Todos los módulos siguientes (clausura, δ*, traza) suponen un autómata bien
    formado. Rechazar una definición mal hecha al cargarla da un único error
    claro en el origen, en vez de un fallo confuso dentro de una simulación.

[1] J. E. Hopcroft, R. Motwani y J. D. Ullman, Introduction to Automata Theory,
    Languages, and Computation, 3rd ed. Pearson, 2007.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from engine.errors import InvalidAutomatonError
from engine.formatting import sort_states

EPSILON = "ε"  # etiqueta de las transiciones ε; nunca es miembro de Σ


@dataclass(frozen=True)
class NFAe:
    """Un NFA-ε. Todos los campos se tratan como inmutables una vez construidos."""

    name: str
    states: tuple                 # Q
    alphabet: tuple               # Σ
    start: str                    # q0
    finals: frozenset             # F
    delta: Mapping                # {(estado, símbolo): frozenset(estados)}

    def targets(self, state: str, symbol: str) -> frozenset:
        """δ(state, symbol) como frozenset; ∅ si la transición no está definida."""
        return self.delta.get((state, symbol), frozenset())

    def transitions(self) -> list:
        """Cada transición como (origen, símbolo, destino), ordenadas por declaración.

        Los estados siguen el orden de Q, los símbolos el orden de Σ, y ε va al final.
        """
        state_order = {state: i for i, state in enumerate(self.states)}
        symbol_order = {symbol: i for i, symbol in enumerate(self.alphabet)}
        symbol_order[EPSILON] = len(self.alphabet)
        triples = [
            (source, symbol, target)
            for (source, symbol), targets in self.delta.items()
            for target in targets
        ]
        return sorted(
            triples,
            key=lambda t: (state_order[t[0]], symbol_order[t[1]], state_order[t[2]]),
        )

    def has_epsilon_transitions(self) -> bool:
        return any(symbol == EPSILON for _source, symbol in self.delta)


def _check_definition(name, states, alphabet, start, finals, transitions) -> None:
    """Recolecta TODAS las violaciones del modelo formal y lanza un único error legible.

    Reglas verificadas (cada una es una cláusula de la definición):
      1. Q es un conjunto finito no vacío (sin nombres repetidos).
      2. Σ es un conjunto no vacío de caracteres únicos y ε ∉ Σ.
      3. q0 ∈ Q.
      4. F ⊆ Q.
      5. Cada transición tiene la forma [origen, símbolo, destino] con
         origen ∈ Q, símbolo ∈ Σ ∪ {ε} y destino ∈ Q.
    """
    problems = []
    if not states:
        problems.append("Q está vacío: un autómata necesita al menos un estado")
    if len(set(states)) != len(states):
        problems.append("Q tiene nombres de estado repetidos")
    if not alphabet:
        problems.append("Σ está vacío: un autómata necesita al menos un símbolo")
    if len(set(alphabet)) != len(alphabet):
        problems.append("Σ tiene símbolos repetidos")
    for symbol in alphabet:
        if len(symbol) != 1:
            problems.append(f"Σ contiene {symbol!r}: cada símbolo debe ser un carácter")
    if EPSILON in alphabet:
        problems.append(f"Σ contiene {EPSILON!r}, reservado para las transiciones ε")
    if start not in states:
        problems.append(f"el estado inicial {start!r} no está en Q")
    for state in sorted(finals - set(states)):
        problems.append(f"el estado final {state!r} no está en Q (F debe ser subconjunto de Q)")
    for edge in transitions:
        if len(edge) != 3:
            problems.append(f"la transición {list(edge)} debe ser [origen, símbolo, destino]")
            continue
        source, symbol, target = edge
        if source not in states:
            problems.append(f"transición {list(edge)}: el origen {source!r} no está en Q")
        if target not in states:
            problems.append(f"transición {list(edge)}: el destino {target!r} no está en Q")
        if symbol != EPSILON and symbol not in alphabet:
            problems.append(
                f"transición {list(edge)}: el símbolo {symbol!r} no está en Σ ∪ {{{EPSILON}}} "
                f"(Σ = {list(alphabet)})"
            )
    if problems:
        raise InvalidAutomatonError(
            f"Autómata inválido {name!r}:\n  - " + "\n  - ".join(problems)
        )


def build(name, states, alphabet, start, finals, transitions) -> NFAe:
    """Valida las piezas de la 5-tupla y ensambla el NFA-ε."""
    states, alphabet = tuple(states), tuple(alphabet)
    finals = frozenset(finals)
    transitions = [tuple(edge) for edge in transitions]
    _check_definition(name, states, alphabet, start, finals, transitions)

    grouped: dict = {}
    for source, symbol, target in transitions:
        grouped.setdefault((source, symbol), set()).add(target)
    delta = {key: frozenset(targets) for key, targets in grouped.items()}
    return NFAe(name, states, alphabet, start, finals, delta)


def from_dict(data: dict) -> NFAe:
    """Construye un NFA-ε a partir de un diccionario con la forma del archivo JSON."""
    required = ("states", "alphabet", "start", "finals", "transitions")
    missing = [key for key in required if key not in data]
    if missing:
        raise InvalidAutomatonError(f"Faltan claves en la definición del autómata: {missing}")
    return build(
        data.get("name", "unnamed"),
        data["states"], data["alphabet"], data["start"],
        data["finals"], data["transitions"],
    )


def load(path) -> NFAe:
    """Carga un autómata desde un archivo JSON (el nombre por defecto es el nombre del archivo)."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("name", Path(path).stem)
    return from_dict(data)


def save(automaton: NFAe, path) -> None:
    """Escribe el autómata como JSON, una transición por línea (fácil de leer y comparar)."""
    lines = [
        "{",
        f'  "name": {json.dumps(automaton.name, ensure_ascii=False)},',
        f'  "states": {json.dumps(list(automaton.states))},',
        f'  "alphabet": {json.dumps(list(automaton.alphabet))},',
        f'  "start": {json.dumps(automaton.start)},',
        f'  "finals": {json.dumps(sort_states(automaton.finals))},',
        '  "transitions": [',
        ",\n".join(
            "    " + json.dumps(list(edge), ensure_ascii=False)
            for edge in automaton.transitions()
        ),
        "  ]",
        "}",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")