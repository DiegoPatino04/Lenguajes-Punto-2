"""Excepciones del motor.

QUÉ: dos tipos de excepción, una por cada tipo de error que puede cometer el usuario.
CÓMO: ambas heredan de ValueError, así los manejadores genéricos las capturan igual.
POR QUÉ: un error de DISEÑO (el autómata está mal definido) y un error de USO (la
         palabra de entrada tiene símbolos que no existen) ocurren en momentos
         distintos: el primero al cargar el autómata (M1), el segundo antes de
         simular una palabra (M3). Separarlos permite mensajes precisos en cada caso.
"""


class AutomatonError(ValueError):
    """Clase base de todo error lanzado por el motor."""


class InvalidAutomatonError(AutomatonError):
    """La definición (Q, Σ, δ, q0, F) viola una regla del modelo formal."""


class InvalidWordError(AutomatonError):
    """La palabra de entrada contiene símbolos que no pertenecen al alfabeto Σ."""