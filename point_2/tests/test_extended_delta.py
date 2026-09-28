"""Tests de M3 (engine/extended_delta.py)."""
import unittest

from engine.errors import InvalidWordError
from engine.extended_delta import accepts, extended_delta, move
from tests.test_model import a_star_b_star


class ExtendedDeltaTests(unittest.TestCase):
    def test_delta_star_de_la_palabra_vacia(self):
        self.assertEqual(extended_delta(a_star_b_star(), ""), frozenset({"q0", "q1"}))

    def test_delta_star_sigue_la_definicion_recursiva(self):
        automaton = a_star_b_star()
        self.assertEqual(extended_delta(automaton, "aab"), frozenset({"q1"}))
        self.assertEqual(move(automaton, {"q0", "q1"}, "a"), frozenset({"q0"}))

    def test_delta_star_desde_otro_estado(self):
        self.assertEqual(extended_delta(a_star_b_star(), "b", from_state="q1"),
                         frozenset({"q1"}))

    def test_aceptacion(self):
        automaton = a_star_b_star()
        for word in ["", "a", "b", "aabb"]:
            self.assertTrue(accepts(automaton, word), word)
        for word in ["ba", "aba"]:
            self.assertFalse(accepts(automaton, word), word)

    def test_palabra_invalida_muestra_el_alfabeto(self):
        with self.assertRaises(InvalidWordError) as ctx:
            accepts(a_star_b_star(), "abcx")
        message = str(ctx.exception)
        self.assertIn("'c' en la posición 3", message)
        self.assertIn("Σ = {a, b}", message)

    def test_epsilon_no_es_simbolo_de_entrada(self):
        with self.assertRaises(InvalidWordError):
            accepts(a_star_b_star(), "aεb")


if __name__ == "__main__":
    unittest.main()