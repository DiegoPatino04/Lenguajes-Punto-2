"""M4 - Traza paso a paso de δ* para una palabra.

QUÉ
    Un registro completo de cómo el autómata procesa una palabra, en las tres
    vistas que pide el taller:
        * tabla de configuración : posición, símbolo leído, entrada restante,
                                   estados activos antes / después de δ / después
                                   de la clausura-ε;
        * cadena δ*              : δ*(q0, prefijo) escrito prefijo por prefijo,
                                   que es la traza clásica hecha a mano;
        * aristas disparadas     : cada (estado_actual, símbolo_leído, estado_siguiente).

CÓMO
    `build_trace` ejecuta las mismas fases que extended_delta (move, luego
    closure) pero conserva cada conjunto intermedio en un TraceStep en vez de
    descartarlo. Las funciones de formato solo leen ese registro; nunca vuelven
    a simular.

POR QUÉ
    * Registrar el conjunto "después de δ" por separado del "después de la
      clausura-ε" hace visible el efecto de las transiciones ε, que es el
      objetivo del ejercicio.
    * Separar simulación de presentación permite alimentar consola, archivo de
      registro e informe con la misma traza, sin ejecutar el autómata dos veces.
    * La traza se detiene en la primera configuración vacía y dice dónde y por
      qué se rechazó la palabra, como exige la rúbrica.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from engine.extended_delta import initial_states, step, validate_word
from engine.formatting import fmt_set, fmt_word, render_table, sort_states
from engine.model import EPSILON, NFAe


@dataclass
class TraceStep:
    position: int                  # símbolos consumidos hasta ahora (0 = configuración inicial)
    symbol: Optional[str]          # símbolo leído en este paso (None en la posición 0)
    remaining: str                 # entrada que falta por leer después de este paso
    before: frozenset              # estados activos antes de leer el símbolo
    moved: frozenset               # estados activos después de δ, antes de la clausura-ε
    closed: frozenset              # estados activos después de la clausura-ε
    symbol_edges: list = field(default_factory=list)   # (origen, símbolo, destino) disparadas por δ
    epsilon_edges: list = field(default_factory=list)  # (origen, ε, destino) dentro de la clausura


@dataclass
class Trace:
    word: str
    steps: list
    accepted: bool
    dead_at: Optional[int]         # símbolo tras el cual ningún estado quedó activo, o None

    @property
    def final_states(self) -> frozenset:
        """δ*(q0, w): el conjunto activo después del último símbolo procesado."""
        return self.steps[-1].closed


def _epsilon_edges(automaton: NFAe, closed) -> list:
    """Aristas ε que salen del conjunto cerrado; todas se usaron para construir la clausura."""
    return [
        (source, EPSILON, target)
        for source in sort_states(closed)
        for target in sort_states(automaton.targets(source, EPSILON))
    ]


def build_trace(automaton: NFAe, word: str) -> Trace:
    """Procesa `word` registrando cada configuración."""
    validate_word(automaton, word)
    first = initial_states(automaton)
    steps = [TraceStep(0, None, word, frozenset(), frozenset({automaton.start}), first,
                       [], _epsilon_edges(automaton, first))]
    dead_at = None
    for position, symbol in enumerate(word, start=1):
        before = steps[-1].closed
        moved, closed = step(automaton, before, symbol)
        fired = [
            (source, symbol, target)
            for source in sort_states(before)
            for target in sort_states(automaton.targets(source, symbol))
        ]
        steps.append(TraceStep(position, symbol, word[position:], before, moved, closed,
                               fired, _epsilon_edges(automaton, closed)))
        if not closed:
            dead_at = position
            break
    accepted = dead_at is None and bool(steps[-1].closed & automaton.finals)
    return Trace(word, steps, accepted, dead_at)


def format_step_table(trace: Trace) -> str:
    """Tabla de configuración (posición, símbolo leído, entrada restante, conjuntos activos)."""
    headers = ["pos", "leído", "restante", "activos antes", "después de δ", "después de ε-cierre"]
    rows = []
    for item in trace.steps:
        initial = item.symbol is None
        rows.append([
            item.position,
            "-" if initial else item.symbol,
            fmt_word(item.remaining),
            "-" if initial else fmt_set(item.before),
            fmt_set(item.moved),
            fmt_set(item.closed),
        ])
    return render_table(headers, rows)


def format_delta_star_chain(automaton: NFAe, trace: Trace) -> str:
    """δ*(q0, prefijo) para cada prefijo leído, en la notación de la definición.

    δ(S, a) significa la unión de δ(p, a) para p en S.
    """
    lines = []
    for item in trace.steps:
        head = f"δ*({automaton.start}, {fmt_word(trace.word[:item.position])})"
        if item.symbol is None:
            lines.append(f"{head} = ECLOSE({{{automaton.start}}}) = {fmt_set(item.closed)}")
        else:
            lines.append(
                f"{head} = ECLOSE(δ({fmt_set(item.before)}, {item.symbol})) "
                f"= ECLOSE({fmt_set(item.moved)}) = {fmt_set(item.closed)}"
            )
    return "\n".join(lines)


def _fmt_edge(edge) -> str:
    source, symbol, target = edge
    return f"({source}, {symbol}, {target})"


def format_edges(trace: Trace) -> str:
    """Por paso, las aristas (estado_actual, símbolo_leído, estado_siguiente) disparadas."""
    lines = []
    for item in trace.steps:
        label = "inicio" if item.symbol is None else f"lee {item.symbol}"
        fired = "  ".join(_fmt_edge(e) for e in item.symbol_edges) or "-"
        eps = "  ".join(_fmt_edge(e) for e in item.epsilon_edges) or "-"
        lines.append(f"pos {item.position:>2} {label:<8} | δ: {fired}  | ε: {eps}")
    return "\n".join(lines)


def format_verdict(automaton: NFAe, trace: Trace) -> str:
    """Una línea que dice si la palabra se acepta y exactamente dónde/por qué."""
    if trace.dead_at is not None:
        unread = fmt_word(trace.steps[-1].remaining)
        return (f"RECHAZADA: ningún estado activo tras leer el símbolo {trace.dead_at}; "
                f"δ*({automaton.start}, w) = ∅ (entrada sin leer: {unread})")
    reached = trace.final_states
    text = f"δ*({automaton.start}, w) = {fmt_set(reached)}"
    hit = reached & automaton.finals
    if hit:
        return f"ACEPTADA: {text} contiene el/los estado(s) final(es) {fmt_set(hit)}"
    return f"RECHAZADA: {text} no contiene ningún estado final (F = {fmt_set(automaton.finals)})"


def format_full_trace(automaton: NFAe, trace: Trace, with_edges: bool = True) -> str:
    """El informe completo para una palabra: tabla, cadena δ*, aristas y veredicto."""
    parts = [
        f"Palabra: {fmt_word(trace.word)}   (longitud {len(trace.word)})",
        "",
        format_step_table(trace),
        "",
        "Cadena δ*:",
        format_delta_star_chain(automaton, trace),
    ]
    if with_edges:
        parts += ["", "Aristas disparadas (estado actual, símbolo leído, estado siguiente):",
                  format_edges(trace)]
    parts += ["", format_verdict(automaton, trace)]
    return "\n".join(parts)