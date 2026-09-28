"""El autómata de 2.1 debe implementar L = (01)+ ∪ (010)+."""
import unittest
from pathlib import Path

from engine.extended_delta import accepts, extended_delta
from engine.model import load
from p21_repeating_patterns.oracle import in_language
from tests.helpers import verify_against_oracle

AUTOMATON = load(Path(__file__).resolve().parents[1] / "p21_repeating_patterns" / "automaton.json")


class P21Tests(unittest.TestCase):
    def test_coincide_con_el_oraculo_hasta_longitud_12(self):
        checked, mismatches = verify_against_oracle(AUTOMATON, in_language, 12)
        self.assertEqual(checked, 8191)
        self.assertEqual(mismatches, [])

    def test_palabras_validas(self):
        for word in ["01", "0101", "010101", "010", "010010", "010010010"]:
            self.assertTrue(accepts(AUTOMATON, word), word)

    def test_palabras_invalidas(self):
        for word in ["", "0", "1", "10", "0110", "01001", "01010", "0101010"]:
            self.assertFalse(accepts(AUTOMATON, word), word)

    def test_no_se_pueden_mezclar_los_patrones(self):
        self.assertFalse(accepts(AUTOMATON, "01" + "010"))
        self.assertFalse(accepts(AUTOMATON, "010" + "01"))

    def test_ambas_ramas_se_exploran_en_paralelo_desde_el_inicio(self):
        self.assertEqual(extended_delta(AUTOMATON, ""), frozenset({"q0", "q1", "q4"}))


if __name__ == "__main__":
    unittest.main()