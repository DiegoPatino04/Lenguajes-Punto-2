# Punto 2.1 — Reconocedor de patrones repetitivos

## 1. Lenguaje

L = (01)⁺ ∪ (010)⁺ = { (01)ⁿ : n ≥ 1 } ∪ { (010)ⁿ : n ≥ 1 }

"01" repetido una o más veces, O "010" repetido una o más veces. Una palabra
que mezcla ambos patrones (ej. 01001, 01010) NO pertenece a L, porque el
enunciado exige repetir *un mismo* patrón.

## 2. Decisiones de diseño

### 2.1 Un reconocedor por patrón, unidos con ε
Dos ramas independientes desde un q0 nuevo, cada una alcanzada con una
transición ε (q0→q1 rama A, q0→q4 rama B). La unión de dos lenguajes
regulares se construye así [1, Sec. 2.5]: un estado inicial nuevo con ε hacia
cada parte, sin necesidad de un producto de ambos reconocedores.

### 2.2 "Una o más veces" con una ε de vuelta a SU PROPIA rama
Rama A: q1 -0→ q2 -1→ q3, con q3 -ε→ q1. Rama B: q4 -0→ q5 -1→ q6 -0→ q7, con
q7 -ε→ q4. Al completar una repetición, la clausura-ε reactiva el inicio de la
rama para permitir otra repetición, sin apagar el estado final ya alcanzado.

La ε **debe volver a q1/q4, nunca a q0**: si volviera a q0, después de "01"
podría arrancar la rama B y se aceptarían mezclas como 01010 (=01·010), que no
pertenecen a L. Con el retorno a la propia rama, ningún camino cambia de
patrón una vez que sale de q0.

### 2.3 Estados finales
F = {q3, q7}: solo se llega a ellos completando una repetición entera. Ningún
estado intermedio es final, así que las repeticiones incompletas se rechazan.

## 3. Formalismo

M = (Q, Σ, δ, q0, F)
Q = {q0..q7}, Σ = {0, 1}, q0 = q0, F = {q3, q7}

| Origen | Símbolo | Destino |
|---|---|---|
| q0 | ε | {q1, q4} |
| q1 | 0 | {q2} |
| q2 | 1 | {q3} |
| q3 | ε | {q1} |
| q4 | 0 | {q5} |
| q5 | 1 | {q6} |
| q6 | 0 | {q7} |
| q7 | ε | {q4} |

(Matriz de transición extendida y diagrama: generados por `run.py` en
`evidence/`, ver `formal_definition`/`transition_matrix` de `engine/exporters.py`.)

## 4. Resultado de las palabras procesadas (ver evidence/run_*.log)

| Palabra | Estructura | Esperado | Resultado |
|---|---|---|---|
| 010101 | A ×3 | válida | ACEPTADA (q3 ∈ F) |
| 010010 | B ×2 | válida | ACEPTADA (q7 ∈ F) |
| 010010010 | B ×3 | válida | ACEPTADA (q7 ∈ F) |
| 0110 | "11" no ocurre en L | inválida | RECHAZADA (∅ tras símbolo 3) |
| 10 | orden incorrecto | inválida | RECHAZADA (∅ tras símbolo 1) |

## 5. Verificación

Comparado contra la expresión regular `(01)+|(010)+` (oráculo independiente,
`oracle.py`) sobre las 8191 palabras binarias de longitud 0 a 12: **0
discrepancias** (`tests/test_p21_language.py`).

## 6. Análisis técnico

**Paralelismo de hipótesis.** ECLOSE({q0}) = {q0, q1, q4} activa ambas ramas a
la vez. En la traza de 010101, tras "01" hay tres hipótesis simultáneas
({q1, q3, q6}: reiniciar A, aceptar A, continuar B); en 010010, el segundo
símbolo "0" dentro de la palabra deja únicamente {q5}, porque la rama A no
tiene transición de q2 con "0" — la rama A queda descartada y solo B sigue
viva. El no determinismo se resuelve por eliminación de hipótesis, no por
adivinación.

**Argumento de corrección.** Todo camino aceptador parte de q0, elige una rama
por una ε y ya no puede abandonarla (las únicas ε de salida de cada rama
regresan a ella). Dentro de una rama, la única forma de llegar al estado final
es recorrer completa la secuencia del patrón, y la ε permite repetirla. Las
palabras aceptadas son exactamente las repeticiones completas de "01" o de
"010", es decir, L.

## 7. Hallazgo sobre el enunciado (por confirmar con el docente)

El enunciado lista "0101010" como ejemplo válido del patrón A. Tiene 7
símbolos: no es múltiplo de 2 (repetición de "01") ni de 3 (repetición de
"010"). Con la definición formal del enunciado, **no pertenece a L**, y el
diseño la rechaza (δ*(q0, 0101010) = {q2}, sin estado final). Se dejó como
palabra "a confirmar" fuera de las 3 válidas exigidas por la rúbrica.

## 8. Referencias
[1] J. E. Hopcroft, R. Motwani y J. D. Ullman, Introduction to Automata
Theory, Languages, and Computation, 3rd ed. Pearson, 2007.