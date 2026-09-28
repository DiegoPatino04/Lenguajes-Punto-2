"""Tests de M1 (engine/model.py)."""
import unittest

from engine.errors import InvalidAutomatonError
from engine.model import EPSILON, build, from_dict


def a_star_b_star():
    """a*b*: q0 loop en a, q0 -ε-> q1, q1 loop en b, q1 final; q2 es inalcanzable."""
    return build("a_star_b_star", ["q0", "q1", "q2"], ["a", "b"], "q0", ["q1"],
                 [["q0", "a", "q0"], ["q0", EPSILON, "q1"], ["q1", "b", "q1"]])


class ModelTests(unittest.TestCase):
    def test_transicion_no_definida_es_vacio(self):
        self.assertEqual(a_star_b_star().targets("q1", "a"), frozenset())

    def test_delta_devuelve_conjuntos(self):
        self.assertEqual(a_star_b_star().targets("q0", EPSILON), frozenset({"q1"}))

    def test_se_reportan_todos_los_errores_de_definicion(self):
        with self.assertRaises(InvalidAutomatonError) as ctx:
            from_dict({"states": ["q0", "q0"], "alphabet": ["a", "ε", "bb"], "start": "q9",
                      "finals": ["q7"], "transitions": [["q0", "z", "q5"], ["q0", "a"]]})
        message = str(ctx.exception)
        for fragment in ["repetidos", "reservado", "un carácter", "inicial",
                        "final", "destino", "no está en Σ", "debe ser [origen"]:
            self.assertIn(fragment, message)

    def test_faltan_claves(self):
        with self.assertRaises(InvalidAutomatonError):
            from_dict({"states": ["q0"]})

    def test_transitions_ordena_por_declaracion(self):
        automaton = a_star_b_star()
        self.assertEqual(automaton.transitions(),
                         [("q0", "a", "q0"), ("q0", EPSILON, "q1"), ("q1", "b", "q1")])


if __name__ == "__main__":
    unittest.main()