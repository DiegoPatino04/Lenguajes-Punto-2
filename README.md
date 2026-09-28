# Punto 2 — NFA-ε (Taller Primer 50%, Lenguajes Formales)

Todos los comandos se ejecutan **desde esta carpeta** (`point_2/`), con el
entorno virtual activado. Nunca uses el botón ▶ "Run Python File" de VS Code:
siempre `python -m <paquete>.<módulo>`.

## Instalación

    python -m venv .venv
    .venv\Scripts\Activate.ps1          # PowerShell (Windows)
    pip install -r requirements.txt     # si existe; si no, no hay dependencias externas

Graphviz (para el diagrama .png/.svg): instalar desde https://graphviz.org/download/
y agregarlo al PATH. Sin Graphviz, run.py igual funciona pero solo genera el .dot
(se renderiza luego con `dot -Tpng archivo.dot -o archivo.png`).

## 1. Reconstruir el autómata de 2.2 (solo si editaste rules/)

    python -m p22_arithmetic_properties.build

Lee cada archivo de `p22_arithmetic_properties/rules/` y regenera
`p22_arithmetic_properties/automaton.json` como la unión-ε de todas las reglas.
Imprime el mapeo regla→estado para documentarlo en el informe.

## 2. Pruebas automáticas (evidencia de corrección)

    python -m unittest discover -s tests -t . -v

Corre 41 pruebas: el motor (M1-M5) y la comparación de cada autómata contra
8191 palabras frente a un oráculo independiente (regex para 2.1, conteo para
2.2). Debe terminar en `OK`.

## 3. Generar la evidencia de cada punto (log + diagrama con timestamp)

    python -m p21_repeating_patterns.run
    python -m p22_arithmetic_properties.run

Cada uno imprime en consola: definición formal, matriz de transición
extendida, ruta del diagrama, y la traza δ* completa de cada palabra exigida
(3 válidas + 2 inválidas), y guarda todo en
`<punto>/evidence/run_<fecha_hora>.log`. **De aquí salen los pantallazos con
timestamp que pide la rúbrica.**

## 4. Probar una palabra suelta (sin guardar evidencia)

    python -m p21_repeating_patterns.run --word 010010
    python -m p22_arithmetic_properties.run --word 0111
    python -m p21_repeating_patterns.run --word 010010 --edges   # + aristas disparadas

## Estructura

    point_2/
    ├─ engine/                          # motor genérico NFA-ε
    │  ├─ errors.py                     # excepciones
    │  ├─ formatting.py                 # notación (conjuntos, λ, tablas)
    │  ├─ model.py        (M1)          # 5-tupla (Q, Σ, δ, q0, F) + validación
    │  ├─ closure.py      (M2)          # clausura-ε
    │  ├─ extended_delta.py (M3)        # move, δ*, aceptación
    │  ├─ tracer.py       (M4)          # traza paso a paso
    │  ├─ exporters.py    (M5)          # matriz extendida + diagrama Graphviz
    │  ├─ combinators.py  (M6)          # unión-ε (usada por 2.2)
    │  └─ report.py       (M7)          # ejecutor de evidencia compartido
    ├─ p21_repeating_patterns/          # punto 2.1: (01)+ ∪ (010)+
    │  ├─ automaton.json, oracle.py, run.py, design.md, evidence/
    ├─ p22_arithmetic_properties/       # punto 2.2: ceros impares O unos múltiplo de 3
    │  ├─ rules/*.json, build.py, automaton.json, oracle.py, run.py, design.md, evidence/
    └─ tests/                           # 41 pruebas unitarias + verificación exhaustiva

## Declaración de uso de IA

Herramienta de IA (Claude) usada como tutor: explicó los conceptos (clausura-ε,
δ*, construcción de subconjuntos) y generó el andamiaje del motor genérico
(`engine/`) bajo supervisión y revisión del estudiante. El diseño de los
autómatas de 2.1 y 2.2 (qué estados, qué transiciones, por qué la ε vuelve a
la propia rama y no a q0, la decisión sobre "0 unos") fue discutido, razonado
y decidido por el estudiante, verificado exhaustivamente contra oráculos
independientes escritos sin autómatas.