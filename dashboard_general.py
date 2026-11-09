# streamlit run "dashboard_general.py"
import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
for subdir in ["lab_3", "lab_4", "lab_5", "lab_6", "lab_7"]:
    p = str(ROOT_DIR / subdir)
    if p not in sys.path:
        sys.path.insert(0, p)
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lab_4.dashboard_lab4 import render_lab4
from lab_5.dashboard_lab5 import render_lab5
from lab_6.dashboard_lab6 import render_lab6
from lab_7.dashboard_lab7 import render_lab7

st.set_page_config(
    page_title="Suite Interactiva de Métodos Computacionales (UNNE)",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos visuales para botones de 1 clic y tarjetas de unidades temáticas
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
    .unidad-card {
        background: rgba(31, 119, 180, 0.06);
        border-left: 5px solid #1f77b4;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Registro global de páginas para permitir navegación cruzada con 1 clic
PAGINAS_REGISTRADAS = {}


def barra_volver_catalogo(unidad_titulo: str, metodo_titulo: str):
    """Renderiza siempre arriba el botón destacado para volver al Catálogo de Métodos."""
    c_back, c_info = st.columns([1.4, 3.6])
    with c_back:
        if st.button("⬅️ Volver al Catálogo de Métodos", use_container_width=True, type="primary"):
            st.switch_page(PAGINAS_REGISTRADAS["catalogo"])
    with c_info:
        st.caption(f"📍 **Unidad:** {unidad_titulo}  |  **Método activo:** {metodo_titulo}")
    st.markdown("---")


def crear_pagina_lab3():
    def _vista_lab3():
        barra_volver_catalogo("Laboratorio 3: Búsqueda de Raíces", "Comparativa Newton-Raphson vs. Interpolación Lineal")
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
    """Pantalla de Inicio: Catálogo Visual de Métodos con acceso directo en 1 clic."""
    st.title("🎓 Catálogo Interactivo de Métodos Computacionales")
    st.markdown(
        "Bienvenida/o a la suite educativa interactiva. **Haga un solo clic sobre el nombre matemático del método** "
        "que desea estudiar para abrir directamente su teoría, casos de estudio, tablas paso a paso y gráficas interactivas."
    )
    st.markdown("---")

    # Fila 1: Búsqueda de Raíces (Lab 3) + Sistemas de Ecuaciones Lineales (Lab 4)
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown(
            """
            <div class="unidad-card">
                <h3 style="margin:0;">🔍 1. Búsqueda de Raíces (Lab 3)</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Resolución de ecuaciones no lineales f(x) = 0, Teorema de Bolzano, Regla de Descartes y barrido previo.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📌 Comparativa Newton-Raphson vs. Interpolación Lineal", key="btn_cat_lab3", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab3_raices"])

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="unidad-card">
                <h3 style="margin:0;">🎯 3. Autovalores y Autovectores (Lab 4)</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Cálculo iterativo del autovalor dominante y obtención del polinomio característico P(λ) = 0.</p>
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
        if st.button("📊 Vista Comparativa del Laboratorio (Autovalores y SEL)", key="btn_cat_comp4_aut", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_comp"])

    with col_b:
        st.markdown(
            """
            <div class="unidad-card">
                <h3 style="margin:0;">🧮 2. Sistemas de Ecuaciones Lineales (Lab 4)</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Métodos directos matriciales (A·x = b) y métodos iterativos con análisis de dominancia diagonal.</p>
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
        if st.button("📊 Vista Comparativa del Laboratorio (Sistemas Lineales)", key="btn_cat_comp4_sel", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab4_comp"])

    st.markdown("---")

    # Fila 2: Interpolación Polinomial (Lab 5) + Integración y Diferenciación (Lab 6)
    col_c, col_d = st.columns(2, gap="large")

    with col_c:
        st.markdown(
            """
            <div class="unidad-card">
                <h3 style="margin:0;">📈 4. Interpolación Polinomial (Lab 5)</h3>
                <p style="margin:4px 0 0 0; font-size:0.92rem;">Construcción simbólica y numérica de polinomios interpoladores desde tablas de puntos o funciones f(x).</p>
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
        if st.button("📊 Vista Comparativa del Laboratorio (Interpolación)", key="btn_cat_comp5", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab5_comp"])

    with col_d:
        st.markdown(
            """
            <div class="unidad-card">
                <h3 style="margin:0;">📐 5. Integración y Diferenciación Numérica (Lab 6)</h3>
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
        if st.button("📊 Vista Comparativa del Laboratorio (Integración)", key="btn_cat_comp6", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab6_comp"])

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="unidad-card">
                <h3 style="margin:0;">🚀 6. Ecuaciones Diferenciales Ordinarias - PVI (Lab 7)</h3>
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
        if st.button("📊 Vista Comparativa del Laboratorio (EDO - PVI)", key="btn_cat_comp7", use_container_width=True):
            st.switch_page(PAGINAS_REGISTRADAS["lab7_comp"])


# Definición de todas las páginas individuales y comparativas
PAGINAS_REGISTRADAS["catalogo"] = st.Page(
    vista_catalogo_principal,
    title="Catálogo de Métodos (Inicio)",
    icon="🏠",
    url_path="catalogo",
    default=True,
)

# Lab 3: Búsqueda de Raíces
PAGINAS_REGISTRADAS["lab3_raices"] = st.Page(
    crear_pagina_lab3(),
    title="Newton-Raphson vs. Interpolación Lineal",
    icon="🔍",
    url_path="lab3_raices",
)

# Lab 4: Sistemas de Ecuaciones Lineales
PAGINAS_REGISTRADAS["lab4_gauss"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Sistemas de Ecuaciones Lineales", "Eliminación de Gauss"),
    title="Eliminación de Gauss",
    icon="🧮",
    url_path="lab4_gauss",
)
PAGINAS_REGISTRADAS["lab4_gj"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Sistemas de Ecuaciones Lineales", "Método de Gauss-Jordan"),
    title="Método de Gauss-Jordan",
    icon="🧮",
    url_path="lab4_gauss_jordan",
)
PAGINAS_REGISTRADAS["lab4_lu"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Sistemas de Ecuaciones Lineales", "Factorización LU"),
    title="Factorización LU",
    icon="🧮",
    url_path="lab4_lu",
)
PAGINAS_REGISTRADAS["lab4_gs"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Sistemas de Ecuaciones Lineales", "Método Iterativo de Gauss-Seidel"),
    title="Método Iterativo de Gauss-Seidel",
    icon="🔄",
    url_path="lab4_gauss_seidel",
)

# Lab 4: Autovalores y Autovectores
PAGINAS_REGISTRADAS["lab4_potencias"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Autovalores y Autovectores", "Método de las Potencias"),
    title="Método de las Potencias",
    icon="⚡",
    url_path="lab4_potencias",
)
PAGINAS_REGISTRADAS["lab4_pot_mejorado"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Autovalores y Autovectores", "Método de la Potencia Mejorado"),
    title="Método de la Potencia Mejorado",
    icon="🚀",
    url_path="lab4_potencia_mejorado",
)
PAGINAS_REGISTRADAS["lab4_faddeev"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Autovalores y Autovectores", "Método de Faddeev-Leverrier"),
    title="Método de Faddeev-Leverrier",
    icon="🎯",
    url_path="lab4_faddeev_leverrier",
)
PAGINAS_REGISTRADAS["lab4_comp"] = st.Page(
    crear_pagina_metodo(render_lab4, "Lab 4: Sistemas Lineales y Autovalores", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 4)",
    icon="📊",
    url_path="lab4_comparativa",
)

# Lab 5: Interpolación Polinomial
PAGINAS_REGISTRADAS["lab5_lineal"] = st.Page(
    crear_pagina_metodo(render_lab5, "Lab 5: Interpolación Polinomial", "Interpolación Lineal"),
    title="Interpolación Lineal",
    icon="📏",
    url_path="lab5_lineal",
)
PAGINAS_REGISTRADAS["lab5_cuad_inv"] = st.Page(
    crear_pagina_metodo(render_lab5, "Lab 5: Interpolación Polinomial", "Interpolación Cuadrática Inversa"),
    title="Interpolación Cuadrática Inversa",
    icon="🔄",
    url_path="lab5_cuadratica_inversa",
)
PAGINAS_REGISTRADAS["lab5_lagrange"] = st.Page(
    crear_pagina_metodo(render_lab5, "Lab 5: Interpolación Polinomial", "Método de Lagrange"),
    title="Método de Lagrange",
    icon="📈",
    url_path="lab5_lagrange",
)
PAGINAS_REGISTRADAS["lab5_ng_asc"] = st.Page(
    crear_pagina_metodo(render_lab5, "Lab 5: Interpolación Polinomial", "Newton-Gregory Ascendente"),
    title="Newton-Gregory Ascendente",
    icon="⬆️",
    url_path="lab5_newton_gregory_asc",
)
PAGINAS_REGISTRADAS["lab5_ng_desc"] = st.Page(
    crear_pagina_metodo(render_lab5, "Lab 5: Interpolación Polinomial", "Newton-Gregory Descendente"),
    title="Newton-Gregory Descendente",
    icon="⬇️",
    url_path="lab5_newton_gregory_desc",
)
PAGINAS_REGISTRADAS["lab5_comp"] = st.Page(
    crear_pagina_metodo(render_lab5, "Lab 5: Interpolación Polinomial", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 5)",
    icon="📊",
    url_path="lab5_comparativa",
)

# Lab 6: Integración y Diferenciación Numérica
PAGINAS_REGISTRADAS["lab6_diff"] = st.Page(
    crear_pagina_metodo(render_lab6, "Lab 6: Integración y Diferenciación Numérica", "Diferenciación Numérica (Gregory Ascendente-Descendente)"),
    title="Diferenciación Numérica (Gregory)",
    icon="📈",
    url_path="lab6_diferenciacion",
)
PAGINAS_REGISTRADAS["lab6_trapecio"] = st.Page(
    crear_pagina_metodo(render_lab6, "Lab 6: Integración y Diferenciación Numérica", "Regla del Trapecio"),
    title="Regla del Trapecio",
    icon="📐",
    url_path="lab6_trapecio",
)
PAGINAS_REGISTRADAS["lab6_simpson"] = st.Page(
    crear_pagina_metodo(render_lab6, "Lab 6: Integración y Diferenciación Numérica", "Regla de Simpson (1/3, 3/8 y Combinado)"),
    title="Regla de Simpson (1/3, 3/8 y Comb.)",
    icon="📐",
    url_path="lab6_simpson",
)
PAGINAS_REGISTRADAS["lab6_comp"] = st.Page(
    crear_pagina_metodo(render_lab6, "Lab 6: Integración y Diferenciación Numérica", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 6)",
    icon="📊",
    url_path="lab6_comparativa",
)

# Lab 7: Ecuaciones Diferenciales - PVI
PAGINAS_REGISTRADAS["lab7_euler"] = st.Page(
    crear_pagina_metodo(render_lab7, "Lab 7: Ecuaciones Diferenciales (PVI)", "Método de Euler y Euler Modificado"),
    title="Método de Euler y Euler Modificado",
    icon="📐",
    url_path="lab7_euler",
)
PAGINAS_REGISTRADAS["lab7_rk"] = st.Page(
    crear_pagina_metodo(render_lab7, "Lab 7: Ecuaciones Diferenciales (PVI)", "Método de Runge-Kutta"),
    title="Método de Runge-Kutta",
    icon="🚀",
    url_path="lab7_runge_kutta",
)
PAGINAS_REGISTRADAS["lab7_milne"] = st.Page(
    crear_pagina_metodo(render_lab7, "Lab 7: Ecuaciones Diferenciales (PVI)", "Método de Milne (Predictor-Corrector)"),
    title="Método de Milne (Predictor-Corrector)",
    icon="🔮",
    url_path="lab7_milne",
)
PAGINAS_REGISTRADAS["lab7_comp"] = st.Page(
    crear_pagina_metodo(render_lab7, "Lab 7: Ecuaciones Diferenciales (PVI)", "📊 Vista Comparativa del Laboratorio"),
    title="📊 Vista Comparativa (Lab 7)",
    icon="📊",
    url_path="lab7_comparativa",
)

nav = st.navigation(
    {
        "Inicio": [PAGINAS_REGISTRADAS["catalogo"]],
        "1. Búsqueda de Raíces (Lab 3)": [
            PAGINAS_REGISTRADAS["lab3_raices"],
        ],
        "2. Sistemas Lineales (Lab 4)": [
            PAGINAS_REGISTRADAS["lab4_gauss"],
            PAGINAS_REGISTRADAS["lab4_gj"],
            PAGINAS_REGISTRADAS["lab4_lu"],
            PAGINAS_REGISTRADAS["lab4_gs"],
            PAGINAS_REGISTRADAS["lab4_comp"],
        ],
        "3. Autovalores y Autovectores (Lab 4)": [
            PAGINAS_REGISTRADAS["lab4_potencias"],
            PAGINAS_REGISTRADAS["lab4_pot_mejorado"],
            PAGINAS_REGISTRADAS["lab4_faddeev"],
        ],
        "4. Interpolación Polinomial (Lab 5)": [
            PAGINAS_REGISTRADAS["lab5_lineal"],
            PAGINAS_REGISTRADAS["lab5_cuad_inv"],
            PAGINAS_REGISTRADAS["lab5_lagrange"],
            PAGINAS_REGISTRADAS["lab5_ng_asc"],
            PAGINAS_REGISTRADAS["lab5_ng_desc"],
            PAGINAS_REGISTRADAS["lab5_comp"],
        ],
        "5. Integración y Diferenciación (Lab 6)": [
            PAGINAS_REGISTRADAS["lab6_diff"],
            PAGINAS_REGISTRADAS["lab6_trapecio"],
            PAGINAS_REGISTRADAS["lab6_simpson"],
            PAGINAS_REGISTRADAS["lab6_comp"],
        ],
        "6. Ecuaciones Diferenciales - PVI (Lab 7)": [
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
        "Seleccione cualquier método en el menú o regrese al **Catálogo de Métodos (Inicio)** "
        "para elegir por tema con un solo clic."
    )

nav.run()
