# 🎓 Suite Interactiva de Métodos Computacionales (FaCENA - UNNE)

Presentación oficial de la **Suite Educativa Interactiva de Métodos Computacionales**, desarrollada para la cátedra de **Métodos Computacionales** de la **Facultad de Ciencias Exactas y Naturales y Agrimensura (FaCENA - UNNE)**.

Esta plataforma unifica el estudio teórico, algebraico, algorítmico y geométrico de los **Laboratorios 1 al 7** en una interfaz gráfica moderna basada en **Streamlit, SymPy, NumPy, Pandas y Plotly**. Fue diseñada bajo un enfoque **100% matemático y conceptual**, permitiendo que docentes y estudiantes accedan a cualquier método o ejercicio con **un solo clic** desde el **Catálogo Principal**, sin necesidad de utilizar la terminal ni escribir código.

---

## 🚀 Guía de Uso para Docentes y Alumnos

### 1. Cómo iniciar la aplicación con 1 Clic en Windows (Sin usar Terminal)
1. Abra la carpeta principal del proyecto (`metodos2026`) en el Explorador de Windows.
2. Haga **doble clic** sobre el archivo **`Abrir_Dashboard_Metodos.bat`**.
3. Se abrirá automáticamente su navegador web con el **Catálogo Principal de los Módulos 1 al 7**.
4. Haga clic sobre el botón del método o ejercicio matemático que desee proyectar en clase o estudiar.
5. En cualquier vista individual, pulse el botón superior **`⬅️ Volver al Catálogo Principal`** para regresar inmediatamente al menú de tarjetas temáticas.

---

### 2. Instalación de Dependencias (Por única vez en una PC nueva)
Si ejecuta el repositorio por primera vez en una computadora (con Python 3.10+ instalado), instale las librerías científicas y gráficas ejecutando:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` instala automáticamente:
- `streamlit` (Interfaz gráfica educativa multipágina)
- `sympy` (Cálculo simbólico exacto, derivadas, integrales, series y PVI)
- `numpy` (Álgebra lineal y cálculo matricial)
- `pandas` (Tablas de iteraciones, diferencias finitas y análisis de errores)
- `plotly` (Visualizaciones geométricas interactivas con zoom e inspección punto a punto)

---

### 3. Ejecución Manual desde Línea de Comandos (Opcional)
Para lanzar la suite completa o un laboratorio específico desde una terminal:

```bash
# Ejecutar la Suite Completa Unificada (Laboratorios 1 al 7)
streamlit run dashboard_general.py

# Ejecutar un laboratorio individual de forma autónoma:
streamlit run lab_1/dashboard_lab1.py
streamlit run lab_2/dashboard_lab2.py
streamlit run lab_3/dashboard_comparativo.py
streamlit run lab_4/dashboard_lab4.py
streamlit run lab_5/dashboard_lab5.py
streamlit run lab_6/dashboard_lab6.py
streamlit run lab_7/dashboard_lab7.py
```

---

## 🏛️ Estructura del Repositorio (`lab_1/` a `lab_7/`)

El repositorio preserva **intactos** todos los notebooks, guías en PDF y scripts originales de consola de la cátedra, incorporando en cada carpeta su correspondiente módulo visual de Streamlit:

```text
metodos2026/
├── Abrir_Dashboard_Metodos.bat            # Lanzador automático de 1 clic para Windows
├── dashboard_general.py                   # Punto de entrada unificado (Catálogo Visual Módulos 1 al 7)
├── requirements.txt                       # Dependencias portables del proyecto
├── README.md                              # Documentación general de la cátedra
├── 1°_Trabajo_Evaluación_Laboratorio-Consignas.pdf
│
├── lab_1/                                 # Módulo 1: Modelos Algorítmicos, Tiempos y Series Básicas
│   ├── Guía de laboratorio 1 -2026.pdf    # [Guía Oficial] Enunciados del Laboratorio 1
│   ├── Laboratorio_1.ipynb                # [Legacy Notebook] Ejercicios 1 al 6 (Sumas, Fibonacci, e y π)
│   ├── compl_ejer_1.py                    # [Legacy Consola] Conteo de términos de serie de impares
│   ├── compl_ejer_2.py                    # [Legacy Consola] Serie de Taylor para e^x
│   └── dashboard_lab1.py                  # [Streamlit] Dashboard interactivo del Laboratorio 1
│
├── lab_2/                                 # Módulo 2: Teoría de Errores, Aritmética de Máquina y Estabilidad
│   ├── Guía de Laboratorio 2 - 2026.pdf   # [Guía Oficial] Enunciados del Laboratorio 2
│   ├── ejer_1.py                          # [Legacy / Base] Errores absolutos, relativos y porcentuales
│   ├── ejer_2.py                          # [Legacy / Base] Aritmética de punto flotante con redondeo (k=3)
│   ├── ejer_3.py                          # [Legacy / Base] Aritmética de punto flotante con truncamiento (k=3)
│   ├── ejer_4.py                          # [Legacy / Base] Cancelación catastrófica en cuadrática y racionalización
│   ├── ejer_5.py                          # [Legacy / Base] Evaluación polinómica estándar vs. anidada (Horner)
│   └── dashboard_lab2.py                  # [Streamlit] Dashboard interactivo del Laboratorio 2
│
├── lab_3/                                 # Módulo 3: Búsqueda de Raíces de Ecuaciones No Lineales
│   ├── metodos_lab3.py                    # [Legacy / Base] Regla de Descartes, Barrido y Tanteo
│   ├── newton_raphson.py                  # [Legacy Consola] Script interactivo de Newton-Raphson
│   ├── interpolacion_lineal.py            # [Legacy Consola] Script interactivo de Regula Falsi
│   └── dashboard_comparativo.py           # [Streamlit] Dashboard comparativo del Laboratorio 3
│
├── lab_4/                                 # Módulo 4: Sistemas de Ecuaciones Lineales y Autovalores
│   ├── metodo_eliminacion_gauss.py        # [Legacy / Base] Eliminación de Gauss con pivoteo parcial
│   ├── metodo_gauss_jordan.py             # [Legacy / Base] Gauss-Jordan e inversión matricial
│   ├── metodo_factorisacion_lu.py         # [Legacy / Base] Factorización LU y resolución triangular
│   ├── metodo_gaus_seidel.py              # [Legacy / Base] Método iterativo de Gauss-Seidel
│   ├── metodo_potencias.py                # [Legacy / Base] Método de las Potencias (autovalor dominante)
│   ├── metodo_potencias_mejorado.py       # [Legacy / Base] Método de la Potencia Mejorado (Rayleigh)
│   ├── metodo_FadeevLeverrier.py          # [Legacy / Base] Polinomio característico por Faddeev-Leverrier
│   └── dashboard_lab4.py                  # [Streamlit] Dashboard interactivo del Laboratorio 4
│
├── lab_5/                                 # Módulo 5: Interpolación y Aproximación Polinomial
│   ├── interpolacion_lineal.py            # [Legacy / Base] Interpolación lineal por tramos
│   ├── interpolacion_cuadratica_inversa.py # [Legacy / Base] Interpolación cuadrática inversa x(y)
│   ├── metodo_lagrange.py                 # [Legacy / Base] Polinomio interpolador de Lagrange
│   ├── newton_grgegory_ascendente.py      # [Legacy / Base] Newton-Gregory con diferencias progresivas
│   ├── newton_gregory_descendente.py      # [Legacy / Base] Newton-Gregory con diferencias retrógradas
│   └── dashboard_lab5.py                  # [Streamlit] Dashboard interactivo del Laboratorio 5
│
├── lab_6/                                 # Módulo 6: Integración y Diferenciación Numérica
│   ├── gregory_asc_dsc.py                 # [Legacy / Base] Derivación numérica de 1° y 2° orden (Asc/Desc)
│   ├── trapecio.py                        # [Legacy / Base] Regla del Trapecio simple, compuesta y cota de error
│   ├── simpson.py                         # [Legacy / Base] Reglas de Simpson 1/3, 3/8 y Combinada
│   └── dashboard_lab6.py                  # [Streamlit] Dashboard interactivo del Laboratorio 6
│
└── lab_7/                                 # Módulo 7: Ecuaciones Diferenciales Ordinarias (PVI)
    ├── metodo_euler_y_mod_euler.py        # [Legacy / Base] Método de Euler y Euler Modificado (Heun)
    ├── rungge_kutta.py                    # [Legacy / Base] Runge-Kutta de 2° orden Estándar y Punto Medio
    ├── milner.py                          # [Legacy / Base] Arranque con RK4 y Predictor-Corrector de Milne
    └── dashboard_lab7.py                  # [Streamlit] Dashboard interactivo del Laboratorio 7
```

---

## 📊 Índice Completo de Módulos, Temáticas y Métodos Implementados

| Módulo / Laboratorio | Temática Teórica | Ejercicios y Métodos con Acceso en 1 Clic | Scripts / Algoritmos Base | Dashboard de Streamlit |
| :--- | :--- | :--- | :--- | :--- |
| **Módulo 1 (Lab 1)** | Modelos Algorítmicos, Tiempos de Cómputo y Series Básicas | • Suma de $N$ números positivos ($[1, 255]$ y $10.000$)<br>• Suma de pares de 200 enteros<br>• Sucesión de Fibonacci ($N=200$) y Razón Áurea $\varphi$<br>• Ecuación cuadrática analítica<br>• Series de Taylor para $e$, $e^x$ y $\pi$ (Gregory-Leibniz con criterio de Scarborough) | `lab_1/Laboratorio_1.ipynb`<br>`lab_1/compl_ejer_1.py`<br>`lab_1/compl_ejer_2.py` | `lab_1/dashboard_lab1.py` |
| **Módulo 2 (Lab 2)** | Teoría de Errores, Aritmética de Máquina y Estabilidad Numérica | • Errores Absolutos, Relativos y Cifras Significativas<br>• Aritmética de punto flotante normalizada ($k$ dígitos): Redondeo vs. Truncamiento y pérdida de asociatividad<br>• Cancelación catastrófica en la cuadrática ($x^2 + 62.10x + 1 = 0$) y racionalización<br>• Evaluación polinómica estándar vs. Forma Anidada de Horner | `lab_2/ejer_1.py`<br>`lab_2/ejer_2.py`<br>`lab_2/ejer_3.py`<br>`lab_2/ejer_4.py`<br>`lab_2/ejer_5.py` | `lab_2/dashboard_lab2.py` |
| **Módulo 3 (Lab 3)** | Búsqueda de Raíces de Ecuaciones No Lineales $f(x) = 0$ | • Regla de los Signos de Descartes y Barrido Previo<br>• Método de Newton-Raphson (Tangentes)<br>• Método de Interpolación Lineal (*Regula Falsi*) | `lab_3/metodos_lab3.py`<br>`lab_3/newton_raphson.py`<br>`lab_3/interpolacion_lineal.py` | `lab_3/dashboard_comparativo.py` |
| **Módulo 4 (Lab 4)** | Sistemas de Ecuaciones Lineales ($A\mathbf{x} = \mathbf{b}$) y Autovalores ($A\mathbf{v} = \lambda\mathbf{v}$) | • Eliminación de Gauss<br>• Método de Gauss-Jordan e Inversa<br>• Factorización $LU$<br>• Método Iterativo de Gauss-Seidel (Dominancia Diagonal)<br>• Método de las Potencias y Potencia Mejorado<br>• Polinomio Característico de Faddeev-Leverrier | `lab_4/metodo_eliminacion_gauss.py`<br>`lab_4/metodo_gauss_jordan.py`<br>`lab_4/metodo_factorisacion_lu.py`<br>`lab_4/metodo_gaus_seidel.py`<br>`lab_4/metodo_potencias.py`<br>`lab_4/metodo_potencias_mejorado.py`<br>`lab_4/metodo_FadeevLeverrier.py` | `lab_4/dashboard_lab4.py` |
| **Módulo 5 (Lab 5)** | Interpolación y Aproximación Polinomial | • Interpolación Lineal por Tramos<br>• Interpolación Cuadrática Inversa $x(y)$<br>• Polinomio Interpolador de Lagrange<br>• Newton-Gregory Ascendente ($\Delta^k y_0$)<br>• Newton-Gregory Descendente ($\nabla^k y_n$) | `lab_5/interpolacion_lineal.py`<br>`lab_5/interpolacion_cuadratica_inversa.py`<br>`lab_5/metodo_lagrange.py`<br>`lab_5/newton_grgegory_ascendente.py`<br>`lab_5/newton_gregory_descendente.py` | `lab_5/dashboard_lab5.py` |
| **Módulo 6 (Lab 6)** | Integración y Diferenciación Numérica | • Diferenciación Numérica por Newton-Gregory (Ascendente y Descendente, 1° y 2° derivada)<br>• Regla del Trapecio (Simple, Compuesta y Cota $O(h^2)$)<br>• Reglas de Simpson 1/3, Simpson 3/8 y Simpson Combinado ($O(h^4)$) | `lab_6/gregory_asc_dsc.py`<br>`lab_6/trapecio.py`<br>`lab_6/simpson.py` | `lab_6/dashboard_lab6.py` |
| **Módulo 7 (Lab 7)** | Ecuaciones Diferenciales Ordinarias — Problemas de Valor Inicial (PVI) | • Método de Euler Explícito $O(h)$ y Euler Modificado (Heun) $O(h^2)$<br>• Familia Runge-Kutta: RK2 Estándar, RK2 Punto Medio y RK4 $O(h^4)$<br>• Método Multipaso Predictor-Corrector de Milne (con arranque RK4) | `lab_7/metodo_euler_y_mod_euler.py`<br>`lab_7/rungge_kutta.py`<br>`lab_7/milner.py` | `lab_7/dashboard_lab7.py` |
