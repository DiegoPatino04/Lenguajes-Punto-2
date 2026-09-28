"""Tests de M5 (engine/exporters.py)."""
import unittest

from engine.exporters import formal_definition, to_dot, transition_matrix
from tests.test_model import a_star_b_star


class ExporterTests(unittest.TestCase):
    def test_matriz_marca_inicial_final_epsilon_y_cierre(self):
        matrix = transition_matrix(a_star_b_star())
        self.assertIn("→q0", matrix)
        self.assertIn("*q1", matrix)
        self.assertIn("ε", matrix)
        self.assertIn("ε-cierre", matrix)

    def test_definicion_formal_lista_los_cinco_componentes(self):
        text = formal_definition(a_star_b_star())
        for fragment in ["Q  =", "Σ  =", "q0 =", "F  =", "δ(q0, ε) = {q1}"]:
            self.assertIn(fragment, text)

    def test_dot_dibuja_epsilon_punteada(self):
        dot = to_dot(a_star_b_star())
        self.assertIn('label="ε", style=dashed', dot)
        self.assertIn('"q1" [shape=doublecircle]', dot)


if __name__ == "__main__":
    unittest.main()