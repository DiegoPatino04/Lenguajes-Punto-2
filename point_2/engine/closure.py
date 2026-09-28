"""M2 - Clausura-ε.

QUÉ
    ECLOSE(S) = conjunto de estados alcanzables desde S usando solo transiciones
    ε, incluidos los propios estados de S [1, Sec. 2.5]. Es la operación que
    hace "gratuitas" las transiciones ε: estar en un estado también significa
    estar en todo estado alcanzable desde él sin consumir entrada.

CÓMO
    Recorrido iterativo con una pila de "pendientes" y un conjunto `closure` de
    estados ya descubiertos:
        1. iniciar closure = S y pending = S;
        2. sacar un estado, agregar cada destino ε aún no descubierto, apilarlo;
        3. terminar cuando no queda nada pendiente.

POR QUÉ así
    * La clausura INCLUYE al propio estado (cero pasos ε): si no, un estado sin
      transiciones ε tendría clausura vacía y la simulación lo perdería.
    * El conjunto `closure` funciona también como "visitados", así los CICLOS ε
      (como los usados para modelar "una o más veces") se recorren una sola vez
      y el algoritmo siempre termina.
    * Es iterativo, no recursivo, para que cadenas ε largas no agoten el límite
      de recursión de Python.
    Costo: O(|Q| + |transiciones ε|) por llamada.

[1] J. E. Hopcroft, R. Motwani y J. D. Ullman, Introduction to Automata Theory,
    Languages, and Computation, 3rd ed. Pearson, 2007.
"""
from engine.model import EPSILON, NFAe


def epsilon_closure(automaton: NFAe, states) -> frozenset:
    """ECLOSE(states): todo estado alcanzable usando solo transiciones ε (incluye states)."""
    unknown = set(states) - set(automaton.states)
    if unknown:
        raise ValueError(f"Los estados {sorted(unknown)} no están en Q de {automaton.name!r}")
    closure = set(states)
    pending = list(states)
    while pending:
        state = pending.pop()
        for target in automaton.targets(state, EPSILON):
            if target not in closure:
                closure.add(target)
                pending.append(target)
    return frozenset(closure)


def closure_table(automaton: NFAe) -> dict:
    """ECLOSE({q}) para cada estado q; usada por la matriz de transición extendida."""
    return {state: epsilon_closure(automaton, {state}) for state in automaton.states}