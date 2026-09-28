"""M5 - Exportadores: definición formal, matriz de transición extendida y diagrama.

QUÉ
    Tres vistas del MISMO objeto autómata, una por cada entregable del taller:
        * formal_definition   : M = (Q, Σ, δ, q0, F) con cada valor de δ listado;
        * transition_matrix   : matriz con una columna por símbolo de Σ, una
                                columna ε y una columna de clausura-ε (la matriz
                                "extendida");
        * to_dot / render_diagram : diagrama Graphviz con las transiciones ε
                                dibujadas punteadas y etiquetadas ε.

CÓMO
    Las tres se generan a partir de los datos del autómata, nunca escritas a mano.

POR QUÉ
    Como la definición, la matriz, el diagrama y la simulación provienen de una
    sola fuente, no pueden contradecirse entre sí. Un diagrama dibujado a mano
    que difiera del código es la inconsistencia más común en este tipo de
    informe; generarlo elimina ese riesgo. Se usa Graphviz [1] porque dispone el
    grafo automáticamente a partir de una descripción textual.

[1] E. R. Gansner y S. C. North, "An open graph visualization system and its
    applications to software engineering," Softw.: Pract. Exper., vol. 30,
    no. 11, pp. 1203-1233, 2000.
"""
import shutil
import subprocess
from pathlib import Path

from engine.closure import closure_table
from engine.formatting import fmt_set, render_table
from engine.model import EPSILON, NFAe


def formal_definition(automaton: NFAe) -> str:
    """Texto de M = (Q, Σ, δ, q0, F) con δ listada como una línea por par definido."""
    lines = [
        f"M = (Q, Σ, δ, q0, F)      [{automaton.name}]",
        f"Q  = {{{', '.join(automaton.states)}}}",
        f"Σ  = {{{', '.join(automaton.alphabet)}}}",
        f"q0 = {automaton.start}",
        f"F  = {fmt_set(automaton.finals)}",
        "δ  (los pares no listados equivalen a ∅):",
    ]
    order = list(automaton.alphabet) + [EPSILON]
    for state in automaton.states:
        for symbol in order:
            targets = automaton.targets(state, symbol)
            if targets:
                lines.append(f"   δ({state}, {symbol}) = {fmt_set(targets)}")
    return "\n".join(lines)


def transition_matrix(automaton: NFAe, with_closure: bool = True) -> str:
    """Matriz de transición extendida como tabla de texto.

    → marca el estado inicial y * los estados finales. La columna ε solo se
    muestra si el autómata tiene transiciones ε; la última columna da
    ECLOSE({q}).
    """
    symbols = list(automaton.alphabet)
    if automaton.has_epsilon_transitions():
        symbols.append(EPSILON)
    headers = ["δ"] + symbols + (["ε-cierre"] if with_closure else [])
    closures = closure_table(automaton) if with_closure else {}
    rows = []
    for state in automaton.states:
        marker = ("→" if state == automaton.start else "") + (
            "*" if state in automaton.finals else "")
        row = [marker + state] + [fmt_set(automaton.targets(state, s)) for s in symbols]
        if with_closure:
            row.append(fmt_set(closures[state]))
        rows.append(row)
    return render_table(headers, rows)


def to_dot(automaton: NFAe) -> str:
    """Fuente DOT de Graphviz. Las ε van punteadas, azules y etiquetadas ε; los finales, doble círculo."""
    merged: dict = {}
    for source, symbol, target in automaton.transitions():
        merged.setdefault((source, target, symbol == EPSILON), []).append(symbol)
    lines = [
        "digraph automaton {",
        "  rankdir=LR;",
        '  node [shape=circle, fontname="Times-Roman"];',
        '  edge [fontname="Times-Roman"];',
        '  __start [shape=point, label=""];',
    ]
    for state in automaton.states:
        if state in automaton.finals:
            lines.append(f'  "{state}" [shape=doublecircle];')
    lines.append(f'  __start -> "{automaton.start}";')
    for (source, target, is_epsilon), labels in merged.items():
        style = ', style=dashed, color="#1f4fbf", fontcolor="#1f4fbf"' if is_epsilon else ""
        lines.append(f'  "{source}" -> "{target}" [label="{",".join(sorted(labels))}"{style}];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_diagram(automaton: NFAe, base_path, formats=("png", "svg")) -> list:
    """Escribe <base_path>.dot y, si Graphviz está instalado, las imágenes renderizadas.

    Devuelve la lista de archivos creados. Sin el programa `dot` solo se escribe
    el archivo .dot (se puede renderizar después o pegar en un visor en línea).
    """
    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    dot_file = base.with_suffix(".dot")
    dot_file.write_text(to_dot(automaton), encoding="utf-8")
    created = [dot_file]
    executable = shutil.which("dot")
    if executable:
        for fmt in formats:
            target = base.with_suffix("." + fmt)
            subprocess.run([executable, f"-T{fmt}", str(dot_file), "-o", str(target)],
                           check=True, capture_output=True)
            created.append(target)
    return created