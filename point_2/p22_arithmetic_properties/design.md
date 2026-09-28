# Punto 2.2 — Reconocedor de propiedades aritméticas

## 1. Lenguaje

L = { w ∈ {0,1}* : ceros(w) es impar  O  unos(w) es múltiplo de 3 }

## 2. Decisiones de diseño

### 2.1 Una regla por autómata, unidas con ε
Cada regla es un autómata pequeño e independiente en `rules/`:
- `odd_zeros.json`: paridad de ceros (2 estados: par/impar).
- `ones_multiple_of_3.json`: contador de unos módulo 3 (4 estados).

`build.py` los une con `epsilon_union` (`engine/combinators.py`): un q0 nuevo
con ε hacia el inicio de cada regla. El lenguaje es "regla 1 O regla 2"; una
regla nueva se agrega con un archivo más en `rules/`, sin rediseñar nada.

### 2.2 Decisión sobre "0 unos" (pendiente de confirmar con el docente)
Matemáticamente 0 = 3·0, pero se decidió que **una palabra sin ningún 1 NO
satisface la regla de los unos**. Por eso `ones_multiple_of_3.json` tiene un
estado separado `sin_unos` (no final) en vez de fusionarlo con `mod0`. Así:
λ, "00", "0000" → rechazadas (no tienen ningún 1, y su cantidad de ceros es
par); "0", "000" → aceptadas, pero por la regla de ceros impares, no por la de
unos.

Para invertir la decisión: agregar `"sin_unos"` a `"finals"` en
`ones_multiple_of_3.json` y `ALLOW_ZERO_ONES = True` en `oracle.py`, luego
correr `build.py` de nuevo. `tests/test_p22_language.py` falla si se cambia
solo uno de los dos lados.

## 3. Formalismo (autómata unido, generado por build.py)

M = (Q, Σ, δ, q0, F)
Q = {q0..q6}, Σ = {0, 1}, q0 = q0, F = {q2, q6}
(q1, q2 = paridad de ceros; q3, q4, q5, q6 = contador de unos módulo 3)

| Origen | Símbolo | Destino |
|---|---|---|
| q0 | ε | {q1, q3} |
| q1 | 0 | {q2} |
| q1 | 1 | {q1} |
| q2 | 0 | {q1} |
| q2 | 1 | {q2} |
| q3 | 0 | {q3} |
| q3 | 1 | {q4} |
| q4 | 0 | {q4} |
| q4 | 1 | {q5} |
| q5 | 0 | {q5} |
| q5 | 1 | {q6} |
| q6 | 0 | {q6} |
| q6 | 1 | {q4} |

## 4. Resultado de las palabras procesadas (ver evidence/run_*.log)

| Palabra | Ceros | Unos | Regla que cumple | Esperado | Resultado |
|---|---|---|---|---|---|
| 101 | 1 (impar) | 2 | R1 | válida | ACEPTADA |
| 111 | 0 (par) | 3 (mult. 3) | R2 | válida | ACEPTADA |
| 0111 | 1 (impar) | 3 (mult. 3) | R1 y R2 | válida | ACEPTADA |
| 1111 | 0 (par) | 4 | ninguna | inválida | RECHAZADA |
| 0110 | 2 (par) | 2 | ninguna | inválida | RECHAZADA |

## 5. Verificación

Comparado contra el predicado de conteo independiente (`oracle.py`) sobre las
8191 palabras binarias de longitud 0 a 12: **0 discrepancias**. Además, cada
fragmento de `rules/` se verificó por separado contra su propio predicado, y
`automaton.json` se comparó contra una reconstrucción fresca desde
`rules/` para confirmar que ambos archivos están sincronizados
(`tests/test_p22_language.py`).

## 6. Análisis técnico

**Independencia de las ramas.** Como la unión es por ε (no por producto), el
autómata de 6 estados basta para dos propiedades que, combinadas ingenuamente,
necesitarían 2 × 4 = 8 estados. La clausura-ε inicial {q0, q1, q3} mantiene
vivas ambas ramas desde el primer símbolo, y cada rama cuenta su propia
propiedad sin interferir con la otra: la rama de ceros nunca consume la
información de la rama de unos ni viceversa.

**Argumento de corrección.** Cada rama por sí sola es la construcción estándar
de un autómata de paridad / contador módulo n [1, Sec. 2.3]; el autómata
acepta w si y solo si al menos una de las dos ramas termina en su estado
final tras leer w completa, lo que es exactamente la definición de L como
unión de dos lenguajes.

## 7. Referencias
[1] J. E. Hopcroft, R. Motwani y J. D. Ullman, Introduction to Automata
Theory, Languages, and Computation, 3rd ed. Pearson, 2007.