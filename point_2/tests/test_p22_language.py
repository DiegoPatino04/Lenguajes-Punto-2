"""El autómata de 2.2 debe implementar: ceros impares O unos múltiplo de 3."""
import unittest
from pathlib import Path

from engine.extended_delta import accepts
from engine.model import load
from p22_arithmetic_properties import oracle
from p22_arithmetic_properties.build import build_union
from tests.helpers import verify_against_oracle

FOLDER = Path(__file__).resolve().parents[1] / "p22_arithmetic_properties"
AUTOMATON = load(FOLDER / "automaton.json")


class P22Tests(unittest.TestCase):
    def test_coincide_con_el_oraculo_hasta_longitud_12(self):
        checked, mismatches = verify_against_oracle(AUTOMATON, oracle.in_language, 12)
        self.assertEqual(checked, 8191)
        self.assertEqual(mismatches, [])

    def test_palabras_validas(self):
        for word in ["101", "111", "0111", "0", "000", "111111"]:
            self.assertTrue(accepts(AUTOMATON, word), word)

    def test_palabras_invalidas(self):
        for word in ["1111", "0110", "11", "1"]:
            self.assertFalse(accepts(AUTOMATON, word), word)

    def test_1111_del_enunciado_falla_ambas_reglas(self):
        self.assertFalse(oracle.odd_zeros("1111"))
        self.assertFalse(oracle.ones_multiple_of_3("1111"))
        self.assertFalse(accepts(AUTOMATON, "1111"))

    def test_palabras_sin_unos_siguen_la_decision_documentada(self):
        expected = oracle.ALLOW_ZERO_ONES
        for word in ["", "00", "0000"]:
            self.assertEqual(accepts(AUTOMATON, word), expected, word)
        self.assertTrue(accepts(AUTOMATON, "0"))
        self.assertTrue(accepts(AUTOMATON, "000"))

    def test_automaton_json_esta_sincronizado_con_los_fragmentos(self):
        _parts, rebuilt = build_union()
        self.assertEqual(rebuilt.states, AUTOMATON.states)
        self.assertEqual(rebuilt.finals, AUTOMATON.finals)
        self.assertEqual(rebuilt.delta, AUTOMATON.delta)

    def test_nombres_de_regla_coinciden_entre_fragmentos_y_oraculo(self):
        parts, _union = build_union()
        self.assertEqual({part.name for part in parts}, set(oracle.RULES))

    def test_cada_fragmento_por_si_solo_coincide_con_su_predicado(self):
        parts, _union = build_union()
        for part in parts:
            _checked, mismatches = verify_against_oracle(part, oracle.RULES[part.name], 12)
            self.assertEqual(mismatches, [], part.name)


if __name__ == "__main__":
    unittest.main()