"""Tests de M2 (engine/closure.py)."""
import unittest

from engine.closure import closure_table, epsilon_closure
from engine.model import EPSILON, build
from tests.test_model import a_star_b_star


class ClosureTests(unittest.TestCase):
    def test_incluye_al_propio_estado(self):
        self.assertEqual(epsilon_closure(a_star_b_star(), {"q1"}), frozenset({"q1"}))

    def test_sigue_transiciones_epsilon(self):
        self.assertEqual(epsilon_closure(a_star_b_star(), {"q0"}), frozenset({"q0", "q1"}))

    def test_termina_con_ciclos_epsilon(self):
        ciclo = build("ciclo", ["a", "b", "c"], ["x"], "a", ["c"],
                     [["a", EPSILON, "b"], ["b", EPSILON, "c"], ["c", EPSILON, "a"]])
        self.assertEqual(epsilon_closure(ciclo, {"a"}), frozenset({"a", "b", "c"}))

    def test_clausura_de_un_conjunto_es_la_union(self):
        self.assertEqual(epsilon_closure(a_star_b_star(), {"q0", "q2"}),
                         frozenset({"q0", "q1", "q2"}))

    def test_estado_desconocido_se_rechaza(self):
        with self.assertRaises(ValueError):
            epsilon_closure(a_star_b_star(), {"zzz"})

    def test_closure_table(self):
        self.assertEqual(closure_table(a_star_b_star())["q0"], frozenset({"q0", "q1"}))


if __name__ == "__main__":
    unittest.main()