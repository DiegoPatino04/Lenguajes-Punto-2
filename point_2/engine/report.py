"""M7 - Ejecutor de evidencia compartido por el run.py de cada punto.

QUÉ
    Cada punto solo declara su configuración (título, palabras válidas e
    inválidas). Este módulo hace el resto: carga el autómata, imprime el
    formalismo, la matriz extendida y una traza por palabra, compara el
    veredicto con lo esperado, y guarda todo con marca de tiempo en evidence/.

POR QUÉ
    La rúbrica exige evidencia con marca de tiempo y trazas completas para cada
    palabra. Generarla desde un solo módulo evita que 2.1 y 2.2 diverjan en el
    formato del reporte, y garantiza que el registro coincide con el código que
    lo produjo.
"""
import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from engine.errors import AutomatonError
from engine.exporters import formal_definition, render_diagram, transition_matrix
from engine.model import load
from engine.tracer import build_trace, format_full_trace


@dataclass
class Report:
    """Imprime cada línea y la conserva para poder guardarla en el log de evidencia."""

    lines: list

    def __init__(self):
        self.lines = []

    def add(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def section(self, title: str) -> None:
        self.add()
        self.add("=" * 78)
        self.add(title)
        self.add("=" * 78)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def _trace_words(report: Report, automaton, words, expected, label, with_edges) -> int:
    """Traza cada palabra; devuelve cuántos veredictos difieren de `expected` (None = sin chequeo)."""
    unexpected = 0
    for word in words:
        trace = build_trace(automaton, word)
        report.add()
        report.add(f"--- {label}: {word if word else 'λ'} " + "-" * 40)
        report.add(format_full_trace(automaton, trace, with_edges=with_edges))
        if expected is not None and trace.accepted != expected:
            unexpected += 1
            report.add(f"!! INESPERADO: el diseño dice {trace.accepted}, se esperaba {expected}")
    return unexpected


def run_point(folder: Path, title: str, valid_words, invalid_words, extra_words=(),
             diagram_title="diagram") -> int:
    """Ejecuta un punto completo. `extra_words` es una lista de (palabra, motivo)
    que no cuentan en el veredicto (por ejemplo, casos a confirmar con el docente).
    Devuelve 0 si todo salió como se esperaba, 1 si algo no coincidió, 2 en errores de carga.
    """
    for stream in (sys.stdout, sys.stderr):
        try:  # mantiene λ, ε, δ, ∅ imprimibles en consolas de Windows
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(description=title)
    parser.add_argument("--word", nargs="+", help="traza solo estas palabras")
    parser.add_argument("--edges", action="store_true", help="incluye las aristas disparadas")
    args = parser.parse_args()

    report = Report()
    started = datetime.now()
    try:
        automaton = load(folder / "automaton.json")
        report.add(title)
        report.add(f"Ejecución iniciada: {started.strftime('%Y-%m-%d %H:%M:%S')}")

        if args.word:  # modo rápido: solo las palabras pedidas, sin guardar evidencia
            _trace_words(report, automaton, args.word, None, "palabra", True)
            return 0

        failures = 0
        report.section("1. Definición formal")
        report.add(formal_definition(automaton))

        report.section("2. Matriz de transición extendida (→ inicial, * finales)")
        report.add(transition_matrix(automaton))

        report.section("3. Diagrama")
        files = render_diagram(automaton, folder / "evidence" / diagram_title)
        for path in files:
            report.add(f"escrito: {path}")
        if len(files) == 1:
            report.add("Graphviz ('dot') no encontrado: renderice el .dot con "
                       "'dot -Tpng archivo.dot -o archivo.png'.")

        report.section("4. Trazas δ*")
        failures += _trace_words(report, automaton, valid_words, True, "PALABRA VÁLIDA", args.edges)
        failures += _trace_words(report, automaton, invalid_words, False, "PALABRA INVÁLIDA", args.edges)
        for word, reason in extra_words:
            report.add()
            report.add(f"Palabra adicional (no cuenta en el veredicto): {word}")
            report.add(f"Motivo: {reason}")
            _trace_words(report, automaton, [word], None, "A CONFIRMAR", args.edges)

        report.section("Resultado")
        report.add("TODAS LAS PALABRAS DIERON EL VEREDICTO ESPERADO" if failures == 0
                   else f"FALLÓ: {failures} palabra(s) con veredicto inesperado")
        log_name = f"run_{started.strftime('%Y%m%d_%H%M%S')}.log"
        report.save(folder / "evidence" / log_name)
        print(f"\nEvidencia guardada en: {folder / 'evidence' / log_name}")
        return 0 if failures == 0 else 1
    except (AutomatonError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2