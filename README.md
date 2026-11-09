# 🎓 Suite Interactiva de Métodos Computacionales (Laboratorios 3 al 7)

Suite educativa interactiva desarrollada en **Python + Streamlit** para el estudio teórico, algebraico y geométrico de los métodos numéricos correspondientes a los **Laboratorios 3, 4, 5, 6 y 7** de la asignatura **Métodos Computacionales**.

La aplicación está diseñada especialmente para ofrecer una **experiencia visual de 1 clic sin necesidad de usar la terminal ni escribir código**: al abrir el sistema, se presenta un **Catálogo Visual de Métodos** organizado por unidad temática donde basta con hacer clic sobre el nombre matemático de cualquier método para acceder a su teoría en $\LaTeX$, casos de estudio predefinidos, entrada de funciones o tablas editables, desarrollo paso a paso y gráficas interactivas en Plotly.

---

## 🚀 Guía Rápida de Inicio (Cómo abrir el programa)

### Opción A: Inicio Directo con 1 Clic en Windows (Recomendado para Docentes)
1. Abra la carpeta del proyecto en el Explorador de Windows.
2. Haga **doble clic** sobre el archivo **`Abrir_Dashboard_Metodos.bat`**.
3. Se abrirá automáticamente una pestaña en su navegador web predeterminado con el **Catálogo Visual de Métodos**.
4. Haga clic sobre el botón del método matemático que desee explorar. Para regresar al catálogo en cualquier momento, pulse el botón superior **`⬅️ Volver al Catálogo de Métodos`**.

---

### Opción B: Ejecución desde la Terminal
Si prefiere lanzar la suite completa o un laboratorio específico por línea de comandos:

```bash
# Ejecutar el Catálogo General Unificado (Labs 3, 4, 5, 6 y 7)
streamlit run dashboard_general.py

# O bien ejecutar cada laboratorio de manera individual:
streamlit run lab_3/dashboard_comparativo.py
streamlit run lab_4/dashboard_lab4.py
streamlit run lab_5/dashboard_lab5.py
streamlit run lab_6/dashboard_lab6.py
streamlit run lab_7/dashboard_lab7.py
```

---

### Opción C: Instalación en una PC Nueva
Si ejecuta el proyecto por primera vez en una computadora nueva (con Python 3.10 o superior instalado), instale todas las librerías necesarias en un único paso ejecutando:

```bash
pip install -r requirements.txt
```

Esto instalará automáticamente `streamlit`, `sympy`, `numpy`, `pandas` y `plotly`.

---

## 🏛️ Arquitectura y Convivencia con el Código Legacy de Consola

El proyecto mantiene una **separación estricta y sin regresiones** entre los algoritmos base de la cátedra (que funcionan por consola) y la capa de visualización interactiva en Streamlit:

```text
metodos2026/
├── Abrir_Dashboard_Metodos.bat        # Lanzador automático de 1 clic para Windows
├── dashboard_general.py               # Punto de entrada unificado (Catálogo Visual + Navegación por método)
├── requirements.txt                   # Dependencias portables del proyecto
├── README.md                          # Documentación general del proyecto
│
├── lab_3/                             # Unidad: Búsqueda de Raíces de Ecuaciones No Lineales
│   ├── metodos_lab3.py                # [Legacy / Base] Regla de Descartes, Barrido y Tanteo
│   ├── newton_raphson.py              # [Legacy Consola] Script interactivo de Newton-Raphson
│   ├── interpolacion_lineal.py        # [Legacy Consola] Script interactivo de Regula Falsi
│   └── dashboard_comparativo.py       # [Streamlit] Dashboard comparativo Lab 3
│
├── lab_4/                             # Unidad: Sistemas de Ecuaciones Lineales y Autovalores
│   ├── metodo_eliminacion_gauss.py    # [Legacy / Base] Eliminación de Gauss con pivoteo parcial
│   ├── metodo_gauss_jordan.py         # [Legacy / Base] Gauss-Jordan e inversión matricial
│   ├── metodo_factorisacion_lu.py     # [Legacy / Base] Descomposición LU y sustitución
│   ├── metodo_gaus_seidel.py          # [Legacy / Base] Método iterativo de Gauss-Seidel
│   ├── metodo_potencias.py            # [Legacy / Base] Método de las Potencias (autovalor dominante)
│   ├── metodo_potencias_mejorado.py   # [Legacy / Base] Método de la Potencia Mejorado
│   ├── metodo_FadeevLeverrier.py      # [Legacy / Base] Polinomio característico por Faddeev-Leverrier
│   └── dashboard_lab4.py              # [Streamlit] Vistas individuales y comparativa del Lab 4
│
├── lab_5/                             # Unidad: Interpolación y Aproximación Polinomial
│   ├── interpolacion_lineal.py        # [Legacy / Base] Interpolación lineal por tramos
│   ├── interpolacion_cuadratica_inversa.py # [Legacy / Base] Interpolación cuadrática inversa x(y)
│   ├── metodo_lagrange.py             # [Legacy / Base] Polinomio interpolador de Lagrange
│   ├── newton_grgegory_ascendente.py  # [Legacy / Base] Newton-Gregory con diferencias progresivas
│   ├── newton_gregory_descendente.py  # [Legacy / Base] Newton-Gregory con diferencias retrógradas
│   └── dashboard_lab5.py              # [Streamlit] Vistas individuales y comparativa del Lab 5
│
├── lab_6/                             # Unidad: Integración y Diferenciación Numérica
│   ├── gregory_asc_dsc.py             # [Legacy / Base] Derivación numérica 1° y 2° orden (Asc/Desc)
│   ├── trapecio.py                    # [Legacy / Base] Regla del Trapecio simple, compuesta y cota de error
│   ├── simpson.py                     # [Legacy / Base] Simpson 1/3, Simpson 3/8 y Simpson Combinado
│   └── dashboard_lab6.py              # [Streamlit] Vistas individuales y comparativa del Lab 6
│
└── lab_7/                             # Unidad: Ecuaciones Diferenciales Ordinarias (PVI)
    ├── metodo_euler_y_mod_euler.py    # [Legacy / Base] Método de Euler y Euler Modificado (Heun)
    ├── rungge_kutta.py                # [Legacy / Base] Runge-Kutta 2° orden Estándar y Punto Medio
    ├── milner.py                      # [Legacy / Base] Arranque con RK4 y Predictor-Corrector de Milne
    └── dashboard_lab7.py              # [Streamlit] Vistas individuales y comparativa del Lab 7
```

> **Nota sobre compatibilidad:** Todos los scripts originales de consola dentro de `lab_3` a `lab_7` conservan intactas sus funciones, firmas y menús `main()`. Los dashboards importan directamente dichas funciones (y utilizan *wrappers* no invasivos cuando se requiere inspeccionar pasos matriciales intermedios), garantizando que los programas originales sigan ejecutándose normalmente desde la consola.

---

## 📊 Tabla Resumen de Métodos Implementados

| Unidad Temática | Nombre del Método (Acceso en 1 Clic) | Archivo de Algoritmo Base | Archivo de Dashboard |
| :--- | :--- | :--- | :--- |
| **1. Búsqueda de Raíces (Lab 3)** | Comparativa Newton-Raphson vs. Interpolación Lineal | `lab_3/metodos_lab3.py`, `lab_3/newton_raphson.py`, `lab_3/interpolacion_lineal.py` | `lab_3/dashboard_comparativo.py` |
| **2. Sistemas de Ecuaciones Lineales (Lab 4)** | Eliminación de Gauss | `lab_4/metodo_eliminacion_gauss.py` | `lab_4/dashboard_lab4.py` |
| **2. Sistemas de Ecuaciones Lineales (Lab 4)** | Método de Gauss-Jordan | `lab_4/metodo_gauss_jordan.py` | `lab_4/dashboard_lab4.py` |
| **2. Sistemas de Ecuaciones Lineales (Lab 4)** | Factorización LU | `lab_4/metodo_factorisacion_lu.py` | `lab_4/dashboard_lab4.py` |
| **2. Sistemas de Ecuaciones Lineales (Lab 4)** | Método Iterativo de Gauss-Seidel | `lab_4/metodo_gaus_seidel.py` | `lab_4/dashboard_lab4.py` |
| **3. Autovalores y Autovectores (Lab 4)** | Método de las Potencias | `lab_4/metodo_potencias.py` | `lab_4/dashboard_lab4.py` |
| **3. Autovalores y Autovectores (Lab 4)** | Método de la Potencia Mejorado | `lab_4/metodo_potencias_mejorado.py` | `lab_4/dashboard_lab4.py` |
| **3. Autovalores y Autovectores (Lab 4)** | Método de Faddeev-Leverrier | `lab_4/metodo_FadeevLeverrier.py` | `lab_4/dashboard_lab4.py` |
| **4. Interpolación Polinomial (Lab 5)** | Interpolación Lineal | `lab_5/interpolacion_lineal.py` | `lab_5/dashboard_lab5.py` |
| **4. Interpolación Polinomial (Lab 5)** | Interpolación Cuadrática Inversa | `lab_5/interpolacion_cuadratica_inversa.py` | `lab_5/dashboard_lab5.py` |
| **4. Interpolación Polinomial (Lab 5)** | Método de Lagrange | `lab_5/metodo_lagrange.py` | `lab_5/dashboard_lab5.py` |
| **4. Interpolación Polinomial (Lab 5)** | Newton-Gregory Ascendente | `lab_5/newton_grgegory_ascendente.py` | `lab_5/dashboard_lab5.py` |
| **4. Interpolación Polinomial (Lab 5)** | Newton-Gregory Descendente | `lab_5/newton_gregory_descendente.py` | `lab_5/dashboard_lab5.py` |
| **5. Integración y Diferenciación Numérica (Lab 6)** | Diferenciación Numérica (Gregory Ascendente-Descendente) | `lab_6/gregory_asc_dsc.py` | `lab_6/dashboard_lab6.py` |
| **5. Integración y Diferenciación Numérica (Lab 6)** | Regla del Trapecio | `lab_6/trapecio.py` | `lab_6/dashboard_lab6.py` |
| **5. Integración y Diferenciación Numérica (Lab 6)** | Regla de Simpson (1/3, 3/8 y Combinado) | `lab_6/simpson.py` | `lab_6/dashboard_lab6.py` |
| **6. Ecuaciones Diferenciales - PVI (Lab 7)** | Método de Euler y Euler Modificado | `lab_7/metodo_euler_y_mod_euler.py` | `lab_7/dashboard_lab7.py` |
| **6. Ecuaciones Diferenciales - PVI (Lab 7)** | Método de Runge-Kutta | `lab_7/rungge_kutta.py`, `lab_7/milner.py` | `lab_7/dashboard_lab7.py` |
| **6. Ecuaciones Diferenciales - PVI (Lab 7)** | Método de Milne (Predictor-Corrector) | `lab_7/milner.py` | `lab_7/dashboard_lab7.py` |

