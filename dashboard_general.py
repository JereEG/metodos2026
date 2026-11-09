# streamlit run "dashboard_general.py"
import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
for subdir in ["lab_1", "lab_2", "lab_3", "lab_4", "lab_5", "lab_6", "lab_7"]:
    p = str(ROOT_DIR / subdir)
    if p not in sys.path:
        sys.path.insert(0, p)
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lab_1.dashboard_lab1 import render_lab1
from lab_2.dashboard_lab2 import render_lab2
from lab_4.dashboard_lab4 import render_lab4
from lab_5.dashboard_lab5 import render_lab5
from lab_6.dashboard_lab6 import render_lab6
from lab_7.dashboard_lab7 import render_lab7

st.set_page_config(
    page_title="Métodos Computacionales - Suite Educativa Interactiva",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos UX/UI limpios y académicos para el catálogo visual de 1 clic
st.markdown(
    """
    <style>
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.55rem 0.9rem;
        transition: all 0.15s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
    }
    .modulo-card {
        background: rgba(31, 119, 180, 0.06);
        border-left: 5px solid #1f77b4;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .header-banner {
        background: linear-gradient(90deg, rgba(31,119,180,0.12) 0%, rgba(0,204,150,0.08) 100%);
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 16px;
        border: 1px solid rgba(31,119,180,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Registro global de páginas para permitir navegación cruzada en 1 clic
PAGINAS_REGISTRADAS = {}


def barra_volver_catalogo(unidad_titulo: str, metodo_titulo: str):
    """Renderiza siempre en la parte superior el botón fijo para regresar al Catálogo Principal."""
    c_back, c_info = st.columns([1.5, 3.5])
    with c_back:
        if st.button("⬅️ Volver al Catálogo Principal", use_container_width=True, type="primary"):
            st.switch_page(PAGINAS_REGISTRADAS["catalogo"])
    with c_info:
        st.caption(f"📍 **{unidad_titulo}**  |  **Sección activa:** {metodo_titulo}")
    st.markdown("---")


def crear_pagina_lab3():
    def _vista_lab3():
        barra_volver_catalogo("Módulo 3 (Lab 3): Búsqueda de Raíces", "Comparativa Newton-Raphson vs. Interpolación Lineal")
        lab3_script = ROOT_DIR / "lab_3" / "dashboard_comparativo.py"
        codigo = lab3_script.read_text(encoding="utf-8")
        orig_spc = st.set_page_config
        try:
            st.set_page_config = lambda *args, **kwargs: None
            exec(compile(codigo, str(lab3_script), "exec"), {"__name__": "__main__", "__file__": str(lab3_script)})
        finally:
            st.set_page_config = orig_spc

    return _vista_lab3


def crear_pagina_metodo(render_fn, unidad_titulo: str, nombre_metodo: str):
    def _vista():
        barra_volver_catalogo(unidad_titulo, nombre_metodo)
        render_fn(nombre_metodo)

    return _vista


def vista_catalogo_principal():
    """Pantalla Principal: Catálogo Unificado de los Módulos 1 al 7 con acceso directo de 1 clic."""
    st.markdown(
        """
        <div class="header-banner">
            <h1 style="margin:0; font-size:2.0rem;">🎓 Métodos Computacionales - Suite Educativa Interactiva</h1>
            <p style="margin:6px 0 0 0; font-size:1.05rem;">
                Facultad de Ciencias Exactas y Naturales y Agrimensura (FaCENA - UNNE) &bull;
                <b>Seleccione con un solo clic cualquier tema o método matemático para abrir su desarrollo teórico, tablas y gráficas interactivas.</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================================================================
    # FILA 1: MÓDULO 1 (LAB 1) Y MÓDULO 2 (LAB 2)
    # ==========================================================================
    col_m1, col_m2 = st.columns(2, gap="large")

    with col_m1:
        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">🧮 Módulo 1 (Lab 1): Modelos Algorítmicos, Tiempos y Series Básicas</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Clasificación de algoritmos directos e iterativos, medición de tiempos y convergencia de series de Taylor.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Suma de N Números y Suma de 200 Pares", key="btn_cat_l1_sumas", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab1_sumas"])
        if st.button("📌 Sucesión de Fibonacci (N = 200) y Razón Áurea", key="btn_cat_l1_fib", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab1_fib"])
        if st.button("📌 Ecuación Cuadrática Analítica", key="btn_cat_l1_cuad", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab1_cuad"])
        if st.button("📌 Aproximación de e y π por Series (Euler y Leibniz)", key="btn_cat_l1_series", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab1_series"])
        if st.button("📊 Vista Completa por Pestañas del Laboratorio 1", key="btn_cat_l1_comp", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab1_comp"])

    with col_m2:
        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">🔬 Módulo 2 (Lab 2): Teoría de Errores, Aritmética de Máquina y Estabilidad</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Errores absolutos/relativos, punto flotante con redondeo/truncamiento, cancelación catastrófica y esquema de Horner.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Errores Absolutos, Relativos y Cifras Significativas", key="btn_cat_l2_err", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab2_err"])
        if st.button("📌 Aritmética de Máquina: Redondeo vs. Truncamiento (3/4 Dígitos)", key="btn_cat_l2_fl", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab2_fl"])
        if st.button("📌 Estabilidad Numérica y Cancelación Catastrófica (Cuadrática)", key="btn_cat_l2_cuad", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab2_cuad"])
        if st.button("📌 Evaluación Polinómica: Estándar vs. Forma Anidada (Horner)", key="btn_cat_l2_horner", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab2_horner"])
        if st.button("📊 Vista Completa por Pestañas del Laboratorio 2", key="btn_cat_l2_comp", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab2_comp"])

    st.markdown("---")

    # ==========================================================================
    # FILA 2: MÓDULO 3 (LAB 3) Y MÓDULO 4 (LAB 4)
    # ==========================================================================
    col_m3, col_m4 = st.columns(2, gap="large")

    with col_m3:
        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">🔍 Módulo 3 (Lab 3): Búsqueda de Raíces de Ecuaciones No Lineales</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Teorema de Bolzano, Regla de los Signos de Descartes, barrido previo y comparación de convergencia.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Comparativa Newton-Raphson vs. Interpolación Lineal (Regula Falsi)", key="btn_cat_lab3", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab3_raices"])

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">🎯 Módulo 4B (Lab 4): Autovalores y Autovectores</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Aproximación iterativa del autovalor dominante y construcción del polinomio característico P(λ) = 0.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Método de las Potencias", key="btn_cat_pot", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_potencias"])
        if st.button("📌 Método de la Potencia Mejorado", key="btn_cat_pot_mej", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_pot_mejorado"])
        if st.button("📌 Método de Faddeev-Leverrier", key="btn_cat_fad", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_faddeev"])
        if st.button("📊 Vista Comparativa del Laboratorio 4 (Autovalores y SEL)", key="btn_cat_comp4_aut", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_comp"])

    with col_m4:
        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">🏛️ Módulo 4A (Lab 4): Sistemas de Ecuaciones Lineales (A·x = b)</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Métodos directos matriciales (escalonamiento, inversa, LU) y método iterativo con dominancia diagonal.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Eliminación de Gauss", key="btn_cat_gauss", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_gauss"])
        if st.button("📌 Método de Gauss-Jordan", key="btn_cat_gj", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_gj"])
        if st.button("📌 Factorización LU", key="btn_cat_lu", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_lu"])
        if st.button("📌 Método Iterativo de Gauss-Seidel", key="btn_cat_gs", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_gs"])
        if st.button("📊 Vista Comparativa del Laboratorio 4 (Sistemas Lineales)", key="btn_cat_comp4_sel", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_comp"])

    st.markdown("---")

    # ==========================================================================
    # FILA 3: MÓDULO 5 (LAB 5), MÓDULO 6 (LAB 6) Y MÓDULO 7 (LAB 7)
    # ==========================================================================
    col_m5, col_m67 = st.columns(2, gap="large")

    with col_m5:
        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">📈 Módulo 5 (Lab 5): Interpolación y Aproximación Polinomial</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Polinomios interpoladores desde tablas de datos o funciones f(x), diferencias finitas y fenómeno de Runge.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Interpolación Lineal", key="btn_cat_ilin", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_lineal"])
        if st.button("📌 Interpolación Cuadrática Inversa", key="btn_cat_icuad", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_cuad_inv"])
        if st.button("📌 Método de Lagrange", key="btn_cat_lag", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_lagrange"])
        if st.button("📌 Newton-Gregory Ascendente", key="btn_cat_nga", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_ng_asc"])
        if st.button("📌 Newton-Gregory Descendente", key="btn_cat_ngd", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_ng_desc"])
        if st.button("📊 Vista Comparativa del Laboratorio 5 (Interpolación)", key="btn_cat_comp5", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_comp"])

    with col_m67:
        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">📐 Módulo 6 (Lab 6): Integración y Diferenciación Numérica</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Fórmulas de cuadratura de Newton-Cotes, cotas teóricas de error y derivación por diferencias finitas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Diferenciación Numérica (Gregory Ascendente-Descendente)", key="btn_cat_diff6", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab6_diff"])
        if st.button("📌 Regla del Trapecio", key="btn_cat_trap6", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab6_trapecio"])
        if st.button("📌 Regla de Simpson (1/3, 3/8 y Combinado)", key="btn_cat_simp6", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab6_simpson"])
        if st.button("📊 Vista Comparativa del Laboratorio 6 (Integración)", key="btn_cat_comp6", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab6_comp"])

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="modulo-card">
                <h3 style="margin:0;">🚀 Módulo 7 (Lab 7): Ecuaciones Diferenciales Ordinarias - PVI</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Resolución numérica de Problemas de Valor Inicial y' = f(x, y) mediante métodos de un paso y multipaso.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Método de Euler y Euler Modificado", key="btn_cat_euler7", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab7_euler"])
        if st.button("📌 Método de Runge-Kutta", key="btn_cat_rk7", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab7_rk"])
        if st.button("📌 Método de Milne (Predictor-Corrector)", key="btn_cat_milne7", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab7_milne"])
        if st.button("📊 Vista Comparativa del Laboratorio 7 (EDO - PVI)", key="btn_cat_comp7", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab7_comp"])


# ==============================================================================
# REGISTRO DE PÁGINAS EN ST.NAVIGATION (MÓDULOS 1 AL 7)
# ==============================================================================

PAGINAS_REGISTRADAS["catalogo"] = st.Page(
    vista_catalogo_principal,
    title="Catálogo Principal (Inicio)",
    icon="🏠",
    url_path="catalogo",
    default=True,
)

# Módulo 1 (Lab 1): Modelos Algorítmicos y Series
PAGINAS_REGISTRADAS["lab1_sumas"] = st.Page(
    crear_pagina_metodo(render_lab1, "Módulo 1 (Lab 1): Modelos Algorítmicos y Series", "Suma de N Números y Suma de Pares"),
    title="Suma de N Números y 200 Pares",
    icon="➕",
    url_path="lab1_sumas",
)
PAGINAS_REGISTRADAS["lab1_fib"] = st.Page(
    crear_pagina_metodo(render_lab1, "Módulo 1 (Lab 1): Modelos Algorítmicos y Series", "Sucesión de Fibonacci (N = 200)"),
    title="Sucesión de Fibonacci (N = 200)",
    icon="🌱",
    url_path="lab1_fibonacci",
)
PAGINAS_REGISTRADAS["lab1_cuad"] = st.Page(
    crear_pagina_metodo(render_lab1, "Módulo 1 (Lab 1): Modelos Algorítmicos y Series", "Ecuación Cuadrática Analítica"),
    title="Ecuación Cuadrática Analítica",
    icon="📐",
    url_path="lab1_cuadratica",
)
PAGINAS_REGISTRADAS["lab1_series"] = st.Page(
    crear_pagina_metodo(render_lab1, "Módulo 1 (Lab 1): Modelos Algorítmicos y Series", "Aproximación de e y π por Series"),
    title="Series de Euler (e) y Leibniz (π)",
    icon="♾️",
    url_path="lab1_series",
)
PAGINAS_REGISTRADAS["lab1_comp"] = st.Page(
    crear_pagina_metodo(render_lab1, "Módulo 1 (Lab 1): Modelos Algorítmicos y Series", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Completa (Lab 1)",
    icon="📊",
    url_path="lab1_completo",
)

# Módulo 2 (Lab 2): Teoría de Errores, Aritmética de Máquina y Estabilidad
PAGINAS_REGISTRADAS["lab2_err"] = st.Page(
    crear_pagina_metodo(render_lab2, "Módulo 2 (Lab 2): Errores y Estabilidad Numérica", "Errores Absolutos y Relativos"),
    title="Errores Absolutos y Relativos",
    icon="📏",
    url_path="lab2_errores",
)
PAGINAS_REGISTRADAS["lab2_fl"] = st.Page(
    crear_pagina_metodo(render_lab2, "Módulo 2 (Lab 2): Errores y Estabilidad Numérica", "Aritmética de Máquina (Redondeo vs. Truncamiento)"),
    title="Redondeo vs. Truncamiento",
    icon="🖥️",
    url_path="lab2_aritmetica",
)
PAGINAS_REGISTRADAS["lab2_cuad"] = st.Page(
    crear_pagina_metodo(render_lab2, "Módulo 2 (Lab 2): Errores y Estabilidad Numérica", "Estabilidad Numérica y Cancelación Catastrófica"),
    title="Cancelación Catastrófica (Cuadrática)",
    icon="⚠️",
    url_path="lab2_cancelacion",
)
PAGINAS_REGISTRADAS["lab2_horner"] = st.Page(
    crear_pagina_metodo(render_lab2, "Módulo 2 (Lab 2): Errores y Estabilidad Numérica", "Evaluación Polinómica y Forma Anidada (Horner)"),
    title="Evaluación Polinómica (Horner)",
    icon="📉",
    url_path="lab2_horner",
)
PAGINAS_REGISTRADAS["lab2_comp"] = st.Page(
    crear_pagina_metodo(render_lab2, "Módulo 2 (Lab 2): Errores y Estabilidad Numérica", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Completa (Lab 2)",
    icon="📊",
    url_path="lab2_completo",
)

# Módulo 3 (Lab 3): Búsqueda de Raíces
PAGINAS_REGISTRADAS["lab3_raices"] = st.Page(
    crear_pagina_lab3(),
    title="Newton-Raphson vs. Interpolación Lineal",
    icon="🔍",
    url_path="lab3_raices",
)

# Módulo 4 (Lab 4): Sistemas Lineales y Autovalores
PAGINAS_REGISTRADAS["lab4_gauss"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Sistemas de Ecuaciones Lineales", "Eliminación de Gauss"),
    title="Eliminación de Gauss",
    icon="🧮",
    url_path="lab4_gauss",
)
PAGINAS_REGISTRADAS["lab4_gj"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Sistemas de Ecuaciones Lineales", "Método de Gauss-Jordan"),
    title="Método de Gauss-Jordan",
    icon="🧮",
    url_path="lab4_gauss_jordan",
)
PAGINAS_REGISTRADAS["lab4_lu"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Sistemas de Ecuaciones Lineales", "Factorización LU"),
    title="Factorización LU",
    icon="🧮",
    url_path="lab4_lu",
)
PAGINAS_REGISTRADAS["lab4_gs"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Sistemas de Ecuaciones Lineales", "Método Iterativo de Gauss-Seidel"),
    title="Método Iterativo de Gauss-Seidel",
    icon="🔄",
    url_path="lab4_gauss_seidel",
)
PAGINAS_REGISTRADAS["lab4_potencias"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Autovalores y Autovectores", "Método de las Potencias"),
    title="Método de las Potencias",
    icon="⚡",
    url_path="lab4_potencias",
)
PAGINAS_REGISTRADAS["lab4_pot_mejorado"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Autovalores y Autovectores", "Método de la Potencia Mejorado"),
    title="Método de la Potencia Mejorado",
    icon="🚀",
    url_path="lab4_potencia_mejorado",
)
PAGINAS_REGISTRADAS["lab4_faddeev"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Autovalores y Autovectores", "Método de Faddeev-Leverrier"),
    title="Método de Faddeev-Leverrier",
    icon="🎯",
    url_path="lab4_faddeev_leverrier",
)
PAGINAS_REGISTRADAS["lab4_comp"] = st.Page(
    crear_pagina_metodo(render_lab4, "Módulo 4 (Lab 4): Sistemas Lineales y Autovalores", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 4)",
    icon="📊",
    url_path="lab4_comparativa",
)

# Módulo 5 (Lab 5): Interpolación Polinomial
PAGINAS_REGISTRADAS["lab5_lineal"] = st.Page(
    crear_pagina_metodo(render_lab5, "Módulo 5 (Lab 5): Interpolación Polinomial", "Interpolación Lineal"),
    title="Interpolación Lineal",
    icon="📏",
    url_path="lab5_lineal",
)
PAGINAS_REGISTRADAS["lab5_cuad_inv"] = st.Page(
    crear_pagina_metodo(render_lab5, "Módulo 5 (Lab 5): Interpolación Polinomial", "Interpolación Cuadrática Inversa"),
    title="Interpolación Cuadrática Inversa",
    icon="🔄",
    url_path="lab5_cuadratica_inversa",
)
PAGINAS_REGISTRADAS["lab5_lagrange"] = st.Page(
    crear_pagina_metodo(render_lab5, "Módulo 5 (Lab 5): Interpolación Polinomial", "Método de Lagrange"),
    title="Método de Lagrange",
    icon="📈",
    url_path="lab5_lagrange",
)
PAGINAS_REGISTRADAS["lab5_ng_asc"] = st.Page(
    crear_pagina_metodo(render_lab5, "Módulo 5 (Lab 5): Interpolación Polinomial", "Newton-Gregory Ascendente"),
    title="Newton-Gregory Ascendente",
    icon="⬆️",
    url_path="lab5_newton_gregory_asc",
)
PAGINAS_REGISTRADAS["lab5_ng_desc"] = st.Page(
    crear_pagina_metodo(render_lab5, "Módulo 5 (Lab 5): Interpolación Polinomial", "Newton-Gregory Descendente"),
    title="Newton-Gregory Descendente",
    icon="⬇️",
    url_path="lab5_newton_gregory_desc",
)
PAGINAS_REGISTRADAS["lab5_comp"] = st.Page(
    crear_pagina_metodo(render_lab5, "Módulo 5 (Lab 5): Interpolación Polinomial", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 5)",
    icon="📊",
    url_path="lab5_comparativa",
)

# Módulo 6 (Lab 6): Integración y Diferenciación Numérica
PAGINAS_REGISTRADAS["lab6_diff"] = st.Page(
    crear_pagina_metodo(render_lab6, "Módulo 6 (Lab 6): Integración y Diferenciación Numérica", "Diferenciación Numérica (Gregory Ascendente-Descendente)"),
    title="Diferenciación Numérica (Gregory)",
    icon="📈",
    url_path="lab6_diferenciacion",
)
PAGINAS_REGISTRADAS["lab6_trapecio"] = st.Page(
    crear_pagina_metodo(render_lab6, "Módulo 6 (Lab 6): Integración y Diferenciación Numérica", "Regla del Trapecio"),
    title="Regla del Trapecio",
    icon="📐",
    url_path="lab6_trapecio",
)
PAGINAS_REGISTRADAS["lab6_simpson"] = st.Page(
    crear_pagina_metodo(render_lab6, "Módulo 6 (Lab 6): Integración y Diferenciación Numérica", "Regla de Simpson (1/3, 3/8 y Combinado)"),
    title="Regla de Simpson (1/3, 3/8 y Comb.)",
    icon="📐",
    url_path="lab6_simpson",
)
PAGINAS_REGISTRADAS["lab6_comp"] = st.Page(
    crear_pagina_metodo(render_lab6, "Módulo 6 (Lab 6): Integración y Diferenciación Numérica", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 6)",
    icon="📊",
    url_path="lab6_comparativa",
)

# Módulo 7 (Lab 7): Ecuaciones Diferenciales - PVI
PAGINAS_REGISTRADAS["lab7_euler"] = st.Page(
    crear_pagina_metodo(render_lab7, "Módulo 7 (Lab 7): Ecuaciones Diferenciales (PVI)", "Método de Euler y Euler Modificado"),
    title="Método de Euler y Euler Modificado",
    icon="📐",
    url_path="lab7_euler",
)
PAGINAS_REGISTRADAS["lab7_rk"] = st.Page(
    crear_pagina_metodo(render_lab7, "Módulo 7 (Lab 7): Ecuaciones Diferenciales (PVI)", "Método de Runge-Kutta"),
    title="Método de Runge-Kutta",
    icon="🚀",
    url_path="lab7_runge_kutta",
)
PAGINAS_REGISTRADAS["lab7_milne"] = st.Page(
    crear_pagina_metodo(render_lab7, "Módulo 7 (Lab 7): Ecuaciones Diferenciales (PVI)", "Método de Milne (Predictor-Corrector)"),
    title="Método de Milne (Predictor-Corrector)",
    icon="🔮",
    url_path="lab7_milne",
)
PAGINAS_REGISTRADAS["lab7_comp"] = st.Page(
    crear_pagina_metodo(render_lab7, "Módulo 7 (Lab 7): Ecuaciones Diferenciales (PVI)", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 7)",
    icon="📊",
    url_path="lab7_comparativa",
)

nav = st.navigation(
    {
        "Inicio": [PAGINAS_REGISTRADAS["catalogo"]],
        "Módulo 1: Modelos y Series (Lab 1)": [
            PAGINAS_REGISTRADAS["lab1_sumas"],
            PAGINAS_REGISTRADAS["lab1_fib"],
            PAGINAS_REGISTRADAS["lab1_cuad"],
            PAGINAS_REGISTRADAS["lab1_series"],
            PAGINAS_REGISTRADAS["lab1_comp"],
        ],
        "Módulo 2: Errores y Estabilidad (Lab 2)": [
            PAGINAS_REGISTRADAS["lab2_err"],
            PAGINAS_REGISTRADAS["lab2_fl"],
            PAGINAS_REGISTRADAS["lab2_cuad"],
            PAGINAS_REGISTRADAS["lab2_horner"],
            PAGINAS_REGISTRADAS["lab2_comp"],
        ],
        "Módulo 3: Búsqueda de Raíces (Lab 3)": [
            PAGINAS_REGISTRADAS["lab3_raices"],
        ],
        "Módulo 4: Sistemas Lineales y Autovalores (Lab 4)": [
            PAGINAS_REGISTRADAS["lab4_gauss"],
            PAGINAS_REGISTRADAS["lab4_gj"],
            PAGINAS_REGISTRADAS["lab4_lu"],
            PAGINAS_REGISTRADAS["lab4_gs"],
            PAGINAS_REGISTRADAS["lab4_potencias"],
            PAGINAS_REGISTRADAS["lab4_pot_mejorado"],
            PAGINAS_REGISTRADAS["lab4_faddeev"],
            PAGINAS_REGISTRADAS["lab4_comp"],
        ],
        "Módulo 5: Interpolación Polinomial (Lab 5)": [
            PAGINAS_REGISTRADAS["lab5_lineal"],
            PAGINAS_REGISTRADAS["lab5_cuad_inv"],
            PAGINAS_REGISTRADAS["lab5_lagrange"],
            PAGINAS_REGISTRADAS["lab5_ng_asc"],
            PAGINAS_REGISTRADAS["lab5_ng_desc"],
            PAGINAS_REGISTRADAS["lab5_comp"],
        ],
        "Módulo 6: Integración y Diferenciación (Lab 6)": [
            PAGINAS_REGISTRADAS["lab6_diff"],
            PAGINAS_REGISTRADAS["lab6_trapecio"],
            PAGINAS_REGISTRADAS["lab6_simpson"],
            PAGINAS_REGISTRADAS["lab6_comp"],
        ],
        "Módulo 7: Ecuaciones Diferenciales - PVI (Lab 7)": [
            PAGINAS_REGISTRADAS["lab7_euler"],
            PAGINAS_REGISTRADAS["lab7_rk"],
            PAGINAS_REGISTRADAS["lab7_milne"],
            PAGINAS_REGISTRADAS["lab7_comp"],
        ],
    }
)

with st.sidebar:
    st.markdown("### 🎓 Métodos Computacionales")
    st.caption(
        "FaCENA - UNNE • Navegue con un clic por cualquiera de los 7 Laboratorios o pulse "
        "**Catálogo Principal (Inicio)**."
    )

nav.run()
