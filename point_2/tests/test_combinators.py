"""Tests de engine/combinators.py (unión-ε)."""
import unittest

from engine.combinators import epsilon_union
from engine.errors import InvalidAutomatonError
from engine.extended_delta import accepts
from engine.model import build


def uno(name, symbol):
    return build(name, ["s", "f"], [symbol], "s", ["f"], [["s", symbol, "f"]])


class CombinatorTests(unittest.TestCase):
    def test_union_epsilon(self):
        union = epsilon_union("a_o_b", [uno("solo_a", "a"), uno("solo_b", "b")])
        self.assertTrue(accepts(union, "a") and accepts(union, "b"))
        self.assertFalse(accepts(union, "ab") or accepts(union, ""))

    def test_nombres_numerados(self):
        union = epsilon_union("u", [uno("x", "a"), uno("y", "b")], numbered=True)
        self.assertEqual(union.states, ("q0", "q1", "q2", "q3", "q4"))

    def test_nombres_de_parte_deben_ser_unicos(self):
        parte = uno("igual", "a")
        with self.assertRaises(InvalidAutomatonError):
            epsilon_union("mal", [parte, parte])


if __name__ == "__main__":
    unittest.main()