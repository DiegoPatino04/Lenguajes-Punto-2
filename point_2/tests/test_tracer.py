"""Tests de M4 (engine/tracer.py)."""
import unittest

from engine.tracer import build_trace, format_delta_star_chain, format_step_table
from tests.test_model import a_star_b_star


class TracerTests(unittest.TestCase):
    def test_traza_de_palabra_aceptada(self):
        trace = build_trace(a_star_b_star(), "ab")
        self.assertTrue(trace.accepted)
        self.assertEqual([s.position for s in trace.steps], [0, 1, 2])
        self.assertEqual(trace.final_states, frozenset({"q1"}))

    def test_traza_se_detiene_donde_muere_la_configuracion(self):
        trace = build_trace(a_star_b_star(), "bab")
        self.assertFalse(trace.accepted)
        self.assertEqual(trace.dead_at, 2)
        self.assertEqual(trace.steps[-1].remaining, "b")

    def test_despues_de_delta_se_guarda_separado_de_despues_del_cierre(self):
        primero = build_trace(a_star_b_star(), "a").steps[1]
        self.assertEqual(primero.moved, frozenset({"q0"}))
        self.assertEqual(primero.closed, frozenset({"q0", "q1"}))

    def test_cadena_delta_star_usa_prefijos(self):
        chain = format_delta_star_chain(a_star_b_star(), build_trace(a_star_b_star(), "ab"))
        self.assertTrue(chain.startswith("δ*(q0, λ) = ECLOSE({q0}) = {q0, q1}"))
        self.assertIn("δ*(q0, ab)", chain)

    def test_tabla_muestra_lambda_cuando_termino_la_entrada(self):
        self.assertIn("λ", format_step_table(build_trace(a_star_b_star(), "a")))


if __name__ == "__main__":
    unittest.main()