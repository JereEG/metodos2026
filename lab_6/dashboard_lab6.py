# streamlit run "lab_6/dashboard_lab6.py"
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

LAB6_DIR = Path(__file__).resolve().parent
if str(LAB6_DIR) not in sys.path:
    sys.path.insert(0, str(LAB6_DIR))

from gregory_asc_dsc import (
    calcular_diferencias_ascendentes,
    calcular_diferencias_descendentes,
    derivada_ascendente,
    derivada_descendente,
    encontrar_indice,
)
from simpson import (
    calcular_simpson_1_3,
    calcular_simpson_3_8,
    calcular_simpson_combinado,
)
from trapecio import (
    calcular_error_trapecios,
    calcular_integral_trapecios,
    calcular_trapecios_simple,
)


# --- FUNCIONES AUXILIARES Y COTAS TEÓRICAS ---

def calcular_cota_error_simpson_1_3(x_vals, max_f4):
    """Cota de error teórica para Simpson 1/3 compuesto: ((b-a)^5 / (180 * n^4)) * max|f^(4)(x)|."""
    a, b = float(x_vals[0]), float(x_vals[-1])
    n = len(x_vals) - 1
    return ((b - a) ** 5 / (180.0 * (n ** 4))) * max_f4


def calcular_cota_error_simpson_3_8(x_vals, max_f4):
    """Cota de error teórica para Simpson 3/8 compuesto: ((b-a)^5 / (80 * n^4)) * max|f^(4)(x)|."""
    a, b = float(x_vals[0]), float(x_vals[-1])
    n = len(x_vals) - 1
    return ((b - a) ** 5 / (80.0 * (n ** 4))) * max_f4


def calcular_integral_gregory(x_vals, y_vals):
    """
    Cuadratura de Gregory (Ascendente-Descendente): corrige la Regla del Trapecio
    en los extremos usando diferencias finitas ascendentes en x_0 y descendentes en x_n.
    """
    area_trap, det_trap = calcular_integral_trapecios(list(x_vals), list(y_vals))
    h = det_trap["h"]
    dif_asc = calcular_diferencias_ascendentes(list(y_vals))
    dif_desc = calcular_diferencias_descendentes(list(y_vals))

    corr_1 = 0.0
    corr_2 = 0.0
    if len(dif_asc) > 1 and len(dif_desc) > 1:
        delta_y0 = dif_asc[1][0]
        nabla_yn = dif_desc[1][-1]
        corr_1 = -(h / 12.0) * (nabla_yn - delta_y0)

    if len(dif_asc) > 2 and len(dif_desc) > 2:
        delta2_y0 = dif_asc[2][0]
        nabla2_yn = dif_desc[2][-1]
        corr_2 = -(h / 24.0) * (nabla2_yn + delta2_y0)

    return area_trap + corr_1 + corr_2, {
        "area_trapecio_base": area_trap,
        "correccion_orden_1": corr_1,
        "correccion_orden_2": corr_2,
        "h": h,
    }


def formatear_tabla_gregory_lista(x_vals, tabla_lista, simbolo="Δ"):
    """Convierte la lista de listas de gregory_asc_dsc.py en un DataFrame alineado por nodo."""
    n = len(x_vals)
    filas = []
    for i in range(n):
        fila = {"i": i, "x_i": x_vals[i], f"y_i ({simbolo}⁰f)": tabla_lista[0][i]}
        for k in range(1, len(tabla_lista)):
            if simbolo == "Δ":
                fila[f"{simbolo}^{k}f"] = tabla_lista[k][i] if i < len(tabla_lista[k]) else np.nan
            else:
                idx_desc = i - k
                fila[f"{simbolo}^{k}f"] = tabla_lista[k][idx_desc] if 0 <= idx_desc < len(tabla_lista[k]) else np.nan
        filas.append(fila)
    return pd.DataFrame(filas)


def construir_arco_parabolico(x0, x1, x2, y0, y1, y2, num_pts=40):
    """Genera los puntos de la parábola interpoladora que pasa por (x0,y0), (x1,y1), (x2,y2)."""
    xs = np.linspace(x0, x2, num_pts)
    L0 = (xs - x1) * (xs - x2) / ((x0 - x1) * (x0 - x2))
    L1 = (xs - x0) * (xs - x2) / ((x1 - x0) * (x1 - x2))
    L2 = (xs - x0) * (xs - x1) / ((x2 - x0) * (x2 - x1))
    ys = y0 * L0 + y1 * L1 + y2 * L2
    return xs, ys


def _ui_entrada_datos_lab6(key_prefix):
    """Panel común de selección de función f(x) o tabla discreta de puntos para Lab 6."""
    st.subheader("1. Definición de la Función $f(x)$ o Tabla Discreta de Puntos")

    modo_entrada = st.radio(
        "Seleccione el origen de los datos:",
        [
            "🧮 Función Simbólica f(x) en un intervalo [a, b] (con cálculo analítico exacto en SymPy)",
            "📊 Tabla Discreta de Puntos (x_i, y_i) Editable",
        ],
        horizontal=True,
        key=f"{key_prefix}_modo",
    )

    x_sym = sp.Symbol("x")
    f_simb = None
    f_fn = None
    d1_fn = None
    d2_fn = None
    d4_fn = None
    integral_exacta = None
    integral_simbolica_latex = None

    if "Función Simbólica" in modo_entrada:
        caso = st.selectbox(
            "Seleccione un Caso de Estudio o ingrese una función personalizada:",
            [
                "Caso A: Polinomio Cúbico -> f(x) = x**3 - 2*x**2 + x + 2 en [0, 3] (Simpson es 100% Exacto, Trapecio comete error)",
                "Caso B: Campana Gaussiana (Sin primitiva elemental) -> f(x) = exp(-x**2) en [0, 2]",
                "Caso C: Oscilación Trigonométrica -> f(x) = sin(x) + 0.5*cos(2*x) + 1.5 en [0, 3.14159265]",
                "Caso D: Curvatura Exponencial Pronunciada -> f(x) = x * exp(x) en [0, 2]",
                "Personalizado: Ingresar libremente cualquier f(x)",
            ],
            key=f"{key_prefix}_caso",
        )

        if "Caso A" in caso:
            eq_def, a_def, b_def, n_def = "x**3 - 2*x**2 + x + 2", 0.0, 3.0, 6
            contexto = (
                r"🎯 **¿Por qué Simpson brilla aquí?** La cota de error de Simpson depende de la **cuarta derivada** $f^{(4)}(x)$. "
                r"Para cualquier polinomio de grado $\le 3$, $f^{(4)}(x) = 0$, por lo que **Simpson 1/3 y 3/8 dan el valor exacto con error 0**, "
                r"mientras que la Regla del Trapecio aproxima con segmentos rectos y comete error de truncamiento $O(h^2)$."
            )
        elif "Caso B" in caso:
            eq_def, a_def, b_def, n_def = "exp(-x**2)", 0.0, 2.0, 6
            contexto = (
                r"🔬 **Integral de Gauss ($e^{-x^2}$):** No posee primitiva elemental expresable en funciones simples (define la función error $\text{erf}(x)$). "
                r"Es el caso clásico donde los métodos numéricos de cuadratura son indispensables en ingeniería y estadística."
            )
        elif "Caso C" in caso:
            eq_def, a_def, b_def, n_def = "sin(x) + 0.5*cos(2*x) + 1.5", 0.0, float(np.pi), 6
            contexto = (
                "🌊 **Señal Periódica con Cambios de Concavidad:** Los arcos parabólicos de **Simpson** acompañan las crestas y valles "
                "mucho mejor que las cuerdas rectilíneas del **Trapecio**."
            )
        elif "Caso D" in caso:
            eq_def, a_def, b_def, n_def = "x * exp(x)", 0.0, 2.0, 6
            contexto = (
                "📈 **Crecimiento Exponencial ($x e^x$):** Al tener derivadas sucesivas crecientes hacia el extremo derecho $b=2$, "
                "permite contrastar la precisión de la derivada por **Newton-Gregory Ascendente** (en $x_0$) vs. **Descendente** (en $x_n$)."
            )
        else:
            eq_def, a_def, b_def, n_def = "1 / (1 + x**2)", 0.0, 2.0, 6
            contexto = "✏️ **Modo Personalizado:** SymPy calculará automáticamente la integral analítica y las derivadas para evaluar las cotas teóricas de error."

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            eq_str = st.text_input("Ingrese f(x):", value=eq_def, key=f"{key_prefix}_eq")
        with c2:
            a_val = st.number_input("Límite inferior (a):", value=a_def, format="%.5f", key=f"{key_prefix}_a")
        with c3:
            b_val = st.number_input("Límite superior (b):", value=b_def, format="%.5f", key=f"{key_prefix}_b")
        with c4:
            n_sub = int(st.number_input("N° de subintervalos (n):", min_value=2, max_value=100, value=n_def, step=1, key=f"{key_prefix}_n"))

        if a_val >= b_val:
            st.error("El límite inferior 'a' debe ser estrictamente menor que 'b'.")
            st.stop()

        try:
            f_simb = sp.sympify(eq_str)
            d1_simb = sp.diff(f_simb, x_sym, 1)
            d2_simb = sp.diff(f_simb, x_sym, 2)
            d4_simb = sp.diff(f_simb, x_sym, 4)

            f_fn = sp.lambdify(x_sym, f_simb, "numpy")
            d1_fn = sp.lambdify(x_sym, d1_simb, "numpy")
            d2_fn = sp.lambdify(x_sym, d2_simb, "numpy")
            d4_fn = sp.lambdify(x_sym, d4_simb, "numpy")

            int_expr = sp.integrate(f_simb, (x_sym, a_val, b_val))
            integral_exacta = float(int_expr.evalf())
            primitiva_simb = sp.integrate(f_simb, x_sym)
            integral_simbolica_latex = (
                rf"\int_{{{a_val:.4g}}}^{{{b_val:.4g}}} \left({sp.latex(f_simb)}\right) dx = "
                rf"\left[ {sp.latex(primitiva_simb)} \right]_{{{a_val:.4g}}}^{{{b_val:.4g}}} = {integral_exacta:.10f}"
            )
        except Exception as e:
            st.error(f"Error al procesar la función simbólica con SymPy: {e}")
            st.stop()

        st.latex(integral_simbolica_latex)
        st.info(contexto)

        x_values = np.linspace(a_val, b_val, n_sub + 1)
        y_values = np.array([float(f_fn(float(xv))) for xv in x_values])

    else:
        st.info("📋 **Modo Tabla Discreta:** Ingrese o edite los pares $(x_i, y_i)$ equiespaciados. Se incluyen datos iniciales de ejemplo.")
        df_init_6 = pd.DataFrame({
            "x": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
            "y": [2.0, 2.125, 2.0, 2.375, 4.0, 7.625, 14.0],
        })
        df_edit_6 = st.data_editor(df_init_6, num_rows="dynamic", use_container_width=True, key=f"{key_prefix}_editor")
        df_edit_6 = df_edit_6.dropna().sort_values(by="x").reset_index(drop=True)
        x_values = df_edit_6["x"].to_numpy(dtype=float)
        y_values = df_edit_6["y"].to_numpy(dtype=float)
        if len(x_values) < 2:
            st.error("Se requieren al menos 2 puntos en la tabla.")
            st.stop()
        a_val, b_val = float(x_values[0]), float(x_values[-1])
        n_sub = len(x_values) - 1

    diffs_h = np.diff(x_values)
    es_equiespaciado = bool(np.allclose(diffs_h, diffs_h[0], rtol=1e-7, atol=1e-7))
    h_val = float(diffs_h[0])

    if not es_equiespaciado:
        st.error(
            rf"🚨 **Error de Validación Teórica:** Los nodos $x_i$ NO están equiespaciados ($\Delta x_i = {np.round(diffs_h, 5).tolist()}$). "
            "Las fórmulas cerradas de Newton-Cotes (Trapecio Compuesto, Simpson 1/3, Simpson 3/8) y las derivadas por diferencias finitas de Newton-Gregory "
            "exigen un paso constante $h$."
        )
        st.stop()

    return {
        "x_values": x_values,
        "y_values": y_values,
        "a_val": a_val,
        "b_val": b_val,
        "n_sub": n_sub,
        "h_val": h_val,
        "f_fn": f_fn,
        "d1_fn": d1_fn,
        "d2_fn": d2_fn,
        "d4_fn": d4_fn,
        "integral_exacta": integral_exacta,
    }


# ==============================================================================
# VISTAS INDIVIDUALES POR MÉTODO (1 CLIC)
# ==============================================================================

def vista_diferenciacion_gregory():
    st.header("📈 Diferenciación Numérica (Gregory Ascendente-Descendente)")
    st.markdown(
        """
        A partir del polinomio interpolador de Newton-Gregory, derivando respecto a $x$ ($du/dx = 1/h$) y evaluando en el nodo $x_i$, 
        se obtienen las fórmulas de **diferenciación numérica por diferencias finitas**:
        - **Newton-Gregory Ascendente** utiliza diferencias progresivas $\\Delta^k f_i$ y es ideal cerca del **inicio de la tabla**.
        - **Newton-Gregory Descendente** utiliza diferencias retrógradas $\\nabla^k f_i$ y es ideal cerca del **final de la tabla**.
        """
    )
    st.latex(
        r"\text{Ascendente (inicio): } f'(x_i) \approx \frac{1}{h}\left(\Delta f_i - \frac{1}{2}\Delta^2 f_i + \frac{1}{3}\Delta^3 f_i - \frac{1}{4}\Delta^4 f_i\right), \quad f''(x_i) \approx \frac{1}{h^2}\left(\Delta^2 f_i - \Delta^3 f_i + \frac{11}{12}\Delta^4 f_i\right)"
    )
    st.latex(
        r"\text{Descendente (final): } f'(x_i) \approx \frac{1}{h}\left(\nabla f_i + \frac{1}{2}\nabla^2 f_i + \frac{1}{3}\nabla^3 f_i + \frac{1}{4}\nabla^4 f_i\right), \quad f''(x_i) \approx \frac{1}{h^2}\left(\nabla^2 f_i + \nabla^3 f_i + \frac{11}{12}\nabla^4 f_i\right)"
    )

    datos = _ui_entrada_datos_lab6("diff_greg")
    x_values = datos["x_values"]
    y_values = datos["y_values"]
    a_val, b_val, h_val = datos["a_val"], datos["b_val"], datos["h_val"]
    f_fn, d1_fn, d2_fn = datos["f_fn"], datos["d1_fn"], datos["d2_fn"]

    st.success(f"✅ **Equiespaciamiento verificado:** Paso constante $h = {h_val:.6f}$ ({len(x_values)} nodos).")
    st.markdown("---")

    st.subheader("2. Selección del Nodo $x_i$ y Evaluación de $f'(x_i)$ y $f''(x_i)$")
    col_der1, col_der2 = st.columns(2)
    with col_der1:
        idx_sel = st.selectbox(
            "Seleccione el nodo x_i donde desea evaluar f'(x) y f''(x):",
            options=list(range(len(x_values))),
            format_func=lambda idx: f"Nodo i = {idx}:  x_{idx} = {x_values[idx]:.5f}  (y_{idx} = {y_values[idx]:.5f})",
            key="diff_greg_idx",
        )
    with col_der2:
        x_eval_der = float(x_values[idx_sel])
        mitad_n = (len(x_values) - 1) / 2.0
        if idx_sel <= mitad_n:
            st.info(
                rf"💡 **Recomendación Pedagógica:** El nodo $x_{{{idx_sel}}} = {x_eval_der:.4f}$ está cerca del **inicio del intervalo**. "
                r"El método **Newton-Gregory Ascendente** dispone de más diferencias progresivas $\Delta^k f_i$ hacia adelante y logra menor error."
            )
        else:
            st.info(
                rf"💡 **Recomendación Pedagógica:** El nodo $x_{{{idx_sel}}} = {x_eval_der:.4f}$ está cerca del **final del intervalo**. "
                r"El método **Newton-Gregory Descendente** dispone de más diferencias retrógradas $\nabla^k f_i$ hacia atrás y logra menor error."
            )

    x_list = list(x_values)
    y_list = list(y_values)

    d1_asc = derivada_ascendente(x_list, y_list, x_eval_der, orden=1)
    d1_desc = derivada_descendente(x_list, y_list, x_eval_der, orden=1)

    try:
        d2_asc = derivada_ascendente(x_list, y_list, x_eval_der, orden=2)
    except Exception:
        d2_asc = float("nan")

    try:
        d2_desc = derivada_descendente(x_list, y_list, x_eval_der, orden=2)
    except Exception:
        d2_desc = float("nan")

    d1_real = float(d1_fn(x_eval_der)) if d1_fn is not None else None
    d2_real = float(d2_fn(x_eval_der)) if d2_fn is not None else None

    filas_der = []
    for nombre_d, orden_str, val_num, val_ex in [
        ("Newton-Gregory Ascendente", "1° Derivada f'(x)", d1_asc, d1_real),
        ("Newton-Gregory Descendente", "1° Derivada f'(x)", d1_desc, d1_real),
        ("Newton-Gregory Ascendente", "2° Derivada f''(x)", d2_asc, d2_real),
        ("Newton-Gregory Descendente", "2° Derivada f''(x)", d2_desc, d2_real),
    ]:
        fila = {
            "Método": nombre_d,
            "Orden": orden_str,
            "Valor Numérico": f"{val_num:.8f}" if not np.isnan(val_num) else "Sin diferencias suficientes en este borde",
            "Valor Exacto (SymPy)": f"{val_ex:.8f}" if val_ex is not None else "N/A (Tabla)",
        }
        if val_ex is not None and not np.isnan(val_num):
            err_a = abs(val_num - val_ex)
            err_r = (err_a / abs(val_ex) * 100.0) if abs(val_ex) > 1e-14 else 0.0
            fila["Error Absoluto"] = f"{err_a:.4e}"
            fila["Error Relativo (%)"] = f"{err_r:.4f}%"
        else:
            fila["Error Absoluto"] = "—"
            fila["Error Relativo (%)"] = "—"
        filas_der.append(fila)

    st.dataframe(pd.DataFrame(filas_der), use_container_width=True)

    st.subheader("3. Interpretación Geométrica: Rectas Tangentes en $x_i$")
    y_eval_der = float(y_values[idx_sel])
    span_tang = max((b_val - a_val) * 0.25, h_val * 1.5)
    xs_tang = np.linspace(
        max(a_val - 0.1 * (b_val - a_val), x_eval_der - span_tang),
        min(b_val + 0.1 * (b_val - a_val), x_eval_der + span_tang),
        100,
    )

    fig_der = go.Figure()
    if f_fn is not None:
        xs_c = np.linspace(a_val, b_val, 300)
        ys_c = np.array([float(f_fn(float(pt))) for pt in xs_c])
        fig_der.add_trace(go.Scatter(x=xs_c, y=ys_c, mode="lines", name="f(x) Real", line=dict(color="#1f77b4", width=3)))
    else:
        fig_der.add_trace(go.Scatter(x=x_values, y=y_values, mode="lines", name="Poligonal de Datos", line=dict(color="#1f77b4", width=2)))

    if d1_real is not None:
        fig_der.add_trace(go.Scatter(
            x=xs_tang,
            y=y_eval_der + d1_real * (xs_tang - x_eval_der),
            mode="lines",
            name=f"Tangente Exacta (m = {d1_real:.4f})",
            line=dict(color="#00CC96", width=2.5),
        ))

    if not np.isnan(d1_asc):
        fig_der.add_trace(go.Scatter(
            x=xs_tang,
            y=y_eval_der + d1_asc * (xs_tang - x_eval_der),
            mode="lines",
            name=f"Tangente Gregory Ascendente (m = {d1_asc:.4f})",
            line=dict(color="#FF7F0E", width=2.2, dash="dash"),
        ))
    if not np.isnan(d1_desc):
        fig_der.add_trace(go.Scatter(
            x=xs_tang,
            y=y_eval_der + d1_desc * (xs_tang - x_eval_der),
            mode="lines",
            name=f"Tangente Gregory Descendente (m = {d1_desc:.4f})",
            line=dict(color="#9467BD", width=2.2, dash="dot"),
        ))
    fig_der.add_trace(go.Scatter(
        x=x_values, y=y_values, mode="markers", name="Nodos (x_i, y_i)",
        marker=dict(size=8, color="#D62728"),
    ))
    fig_der.add_trace(go.Scatter(
        x=[x_eval_der], y=[y_eval_der], mode="markers",
        name=f"Punto de Tangencia ({x_eval_der:.3f}, {y_eval_der:.3f})",
        marker=dict(size=14, color="gold", symbol="star", line=dict(width=1.5, color="black")),
    ))
    fig_der.update_layout(
        title=f"Comparación de Rectas Tangentes en x_{idx_sel} = {x_eval_der:.4f}",
        xaxis_title="x",
        yaxis_title="y",
        hovermode="x unified",
    )
    st.plotly_chart(fig_der, use_container_width=True)

    c_ta, c_td = st.columns(2)
    with c_ta:
        st.subheader(r"Tabla de Diferencias Ascendentes ($\Delta^k f$)")
        dif_asc_tbl = calcular_diferencias_ascendentes(y_list)
        st.dataframe(
            formatear_tabla_gregory_lista(x_values, dif_asc_tbl, "Δ").style.format(precision=6, na_rep="—"),
            use_container_width=True,
        )
    with c_td:
        st.subheader(r"Tabla de Diferencias Descendentes ($\nabla^k f$)")
        dif_desc_tbl = calcular_diferencias_descendentes(y_list)
        st.dataframe(
            formatear_tabla_gregory_lista(x_values, dif_desc_tbl, "∇").style.format(precision=6, na_rep="—"),
            use_container_width=True,
        )


def vista_trapecio():
    st.header("📐 Regla del Trapecio (Simple y Compuesta)")
    st.markdown(
        """
        La **Regla del Trapecio** aproxima la función $f(x)$ en cada subintervalo $[x_i, x_{i+1}]$ mediante una **cuerda rectilínea** 
        (polinomio interpolador de grado 1) y suma el área de los $n$ trapecios resultantes:
        """
    )
    st.latex(
        r"\int_{a}^{b} f(x)\,dx \approx \frac{h}{2}\Big( \underbrace{y_0 + y_n}_{E \text{ (Extremos)}} + 2\underbrace{\sum_{i=1}^{n-1} y_i}_{P + I \text{ (Interiores)}} \Big) = \frac{h}{2}(E + 2P + 2I), \qquad |E_T| \le \frac{(b-a)^3}{12\,n^2} \max_{x \in [a,b]} |f''(x)|"
    )

    datos = _ui_entrada_datos_lab6("trap")
    x_values, y_values = datos["x_values"], datos["y_values"]
    a_val, b_val, n_sub, h_val = datos["a_val"], datos["b_val"], datos["n_sub"], datos["h_val"]
    f_fn, d2_fn, integral_exacta = datos["f_fn"], datos["d2_fn"], datos["integral_exacta"]

    x_list = list(x_values)
    y_list = list(y_values)

    area_trap, det_trap = calcular_integral_trapecios(x_list, y_list)
    area_simple = calcular_trapecios_simple(x_list, y_list)

    cota_trap = None
    max_d2 = None
    if d2_fn is not None:
        xs_dense = np.linspace(a_val, b_val, 500)
        max_d2 = float(np.max(np.abs([float(d2_fn(float(pt))) for pt in xs_dense])))
        cota_trap = calcular_error_trapecios(x_list, max_d2)

    st.markdown("---")
    st.subheader("2. Resultados y Desglose Algebraico Paso a Paso")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Área Trapecio Compuesto", f"{area_trap:.8f}", f"n = {n_sub} trapecios (h = {h_val:.4f})")
    m2.metric("Área Trapecio Simple (1 tramo)", f"{area_simple:.8f}", "Usando solo extremos a y b")
    if integral_exacta is not None:
        err_abs = abs(area_trap - integral_exacta)
        err_rel = (err_abs / abs(integral_exacta) * 100.0) if abs(integral_exacta) > 1e-14 else 0.0
        m3.metric("Error Absoluto Real", f"{err_abs:.4e}", f"Relativo: {err_rel:.4f}%")
    else:
        m3.metric("Integral Exacta", "N/A (Tabla)", "Modo datos discretos")

    if cota_trap is not None:
        m4.metric("Cota de Error Teórica O(h²)", f"≤ {cota_trap:.4e}", f"máx |f''(x)| ≈ {max_d2:.4f}")
    else:
        m4.metric("Cota de Error Teórica", "Requiere f(x)", "Disponible en modo simbólico")

    col_alg1, col_alg2 = st.columns(2)
    with col_alg1:
        st.markdown("**Clasificación de Ordenadas ($E, P, I$):**")
        st.write(
            f"- **Paso constante:** $h = {det_trap['h']:.6f}$\n"
            f"- **Suma de Extremos ($E = y_0 + y_n$):** `{det_trap['E']:.8f}` (índices `{det_trap['extremos_idx']}`)\n"
            f"- **Suma de Índices Pares Interiores ($P$):** `{det_trap['P']:.8f}` (índices `{det_trap['pares_idx']}`)\n"
            f"- **Suma de Índices Impares ($I$):** `{det_trap['I']:.8f}` (índices `{det_trap['impares_idx']}`)\n"
            f"- **Sustitución en Fórmula:** `{det_trap['formula']} = {area_trap:.10f}`"
        )
    with col_alg2:
        # Tabla individual de cada trapecio
        filas_tramos = []
        for i in range(n_sub):
            area_i = 0.5 * h_val * (y_values[i] + y_values[i + 1])
            filas_tramos.append({
                "Trapecio #": i + 1,
                "Subintervalo [x_i, x_{i+1}]": f"[{x_values[i]:.4f}, {x_values[i+1]:.4f}]",
                "Base Izquierda y_i": y_values[i],
                "Base Derecha y_{i+1}": y_values[i + 1],
                "Área Parcial (h/2)·(y_i + y_{i+1})": area_i,
            })
        st.markdown("**Áreas individuales por cada subintervalo:**")
        st.dataframe(pd.DataFrame(filas_tramos).style.format(precision=6), use_container_width=True)

    st.subheader("3. Interpretación Geométrica: Trapecios Sombrados Bajo la Curva")
    fig_trap = go.Figure()
    if f_fn is not None:
        xs_smooth = np.linspace(a_val, b_val, 400)
        ys_smooth = np.array([float(f_fn(float(pt))) for pt in xs_smooth])
        fig_trap.add_trace(go.Scatter(
            x=xs_smooth, y=ys_smooth, mode="lines",
            name="Función Real f(x)",
            line=dict(color="#1f77b4", width=3),
        ))

    fig_trap.add_trace(go.Scatter(
        x=x_values, y=y_values, mode="lines+markers",
        name="Techos Rectilíneos (Trapecios)",
        line=dict(color="#FF7F0E", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(255, 127, 14, 0.25)",
        marker=dict(size=9, color="#D62728"),
    ))
    for xv, yv in zip(x_values, y_values):
        fig_trap.add_trace(go.Scatter(
            x=[xv, xv], y=[0.0, yv], mode="lines",
            line=dict(color="rgba(120,120,120,0.5)", width=1, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
    fig_trap.update_layout(
        title=f"Aproximación por {n_sub} Trapecios Rectilíneos (Área = {area_trap:.8f})",
        xaxis_title="x",
        yaxis_title="f(x)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_trap, use_container_width=True)


def vista_simpson():
    st.header("📐 Regla de Simpson (1/3, 3/8 y Combinado)")
    st.markdown(
        """
        Las **Reglas de Simpson** reemplazan los tramos rectos del trapecio por **polinomios de grado superior**, logrando un orden de convergencia $O(h^4)$ (exactitud total para polinomios de hasta 3° grado):
        - **Simpson 1/3 Compuesto:** Ajusta **parábolas de 2° grado** cada 3 puntos consecutivos (requiere un número **par** de subintervalos $n$).
        - **Simpson 3/8 Compuesto:** Ajusta **cúbicas de 3° grado** cada 4 puntos consecutivos (requiere $n$ **múltiplo de 3**).
        - **Simpson Combinado:** Permite integrar **cualquier número de subintervalos $n$** aplicando un bloque de Simpson 3/8 en los últimos 3 subintervalos cuando $n$ es impar y Simpson 1/3 en el resto.
        """
    )
    st.latex(
        r"I_{1/3} = \frac{h}{3}(E + 2P + 4I), \qquad I_{3/8} = \frac{3h}{8}\Big(y_0 + 3\sum_{i \not\equiv 0 (\text{mod } 3)} y_i + 2\sum_{i \equiv 0 (\text{mod } 3)} y_i + y_n\Big)"
    )

    datos = _ui_entrada_datos_lab6("simp")
    x_values, y_values = datos["x_values"], datos["y_values"]
    a_val, b_val, n_sub, h_val = datos["a_val"], datos["b_val"], datos["n_sub"], datos["h_val"]
    f_fn, d4_fn, integral_exacta = datos["f_fn"], datos["d4_fn"], datos["integral_exacta"]

    x_list = list(x_values)
    y_list = list(y_values)

    cv1, cv2 = st.columns(2)
    with cv1:
        if n_sub % 2 == 0:
            st.success(f"✅ **Condición Simpson 1/3 cumplida:** $n = {n_sub}$ es **par** ({len(x_values)} puntos).")
        else:
            st.warning(f"⚠️ **Restricción Simpson 1/3 puro:** $n = {n_sub}$ es **impar**. Se activará automáticamente **Simpson Combinado**.")
    with cv2:
        if n_sub % 3 == 0:
            st.success(f"✅ **Condición Simpson 3/8 cumplida:** $n = {n_sub}$ es **múltiplo de 3** ({n_sub // 3} bloques de 3 subintervalos).")
        else:
            st.warning(f"⚠️ **Restricción Simpson 3/8 puro:** $n = {n_sub}$ no es múltiplo de 3.")

    cota_s13 = None
    cota_s38 = None
    if d4_fn is not None:
        xs_dense = np.linspace(a_val, b_val, 500)
        max_d4 = float(np.max(np.abs([float(d4_fn(float(pt))) for pt in xs_dense])))
        cota_s13 = calcular_cota_error_simpson_1_3(x_values, max_d4)
        cota_s38 = calcular_cota_error_simpson_3_8(x_values, max_d4)

    area_s13, det_s13 = (calcular_simpson_1_3(x_list, y_list) if n_sub % 2 == 0 else (None, None))
    area_s38, det_s38 = (calcular_simpson_3_8(x_list, y_list) if n_sub % 3 == 0 else (None, None))
    try:
        area_scomb, det_scomb = calcular_simpson_combinado(x_list, y_list)
    except Exception:
        area_scomb, det_scomb = None, None

    filas_s = []
    for nom, val, cota, cond in [
        ("Regla de Simpson 1/3", area_s13, cota_s13, f"n = {n_sub} par" if n_sub % 2 == 0 else "No aplicable (n impar)"),
        ("Regla de Simpson 3/8", area_s38, cota_s38, f"n = {n_sub} múltiplo de 3" if n_sub % 3 == 0 else "No aplicable (n no es múltiplo de 3)"),
        (f"Simpson Combinado ({det_scomb['metodo'] if det_scomb else 'Auto'})", area_scomb, cota_s13, "Adapta 1/3 y 3/8 para cualquier n ≥ 2"),
    ]:
        f_row = {
            "Variante de Simpson": nom,
            "Valor Aproximado": f"{val:.10f}" if val is not None else "No aplicable",
            "Valor Exacto": f"{integral_exacta:.10f}" if integral_exacta is not None else "N/A (Tabla)",
            "Error Absoluto": f"{abs(val - integral_exacta):.4e}" if (val is not None and integral_exacta is not None) else "—",
            "Cota Teórica O(h⁴)": f"≤ {cota:.4e}" if cota is not None else "—",
            "Condición de Paridad": cond,
        }
        filas_s.append(f_row)

    st.subheader("2. Comparativa de las Variantes de Simpson")
    st.dataframe(pd.DataFrame(filas_s), use_container_width=True)

    c_d1, c_d2 = st.columns(2)
    with c_d1:
        st.markdown("**Desglose Algebraico de Simpson 1/3:**")
        if det_s13 is not None:
            st.write(
                f"- **Paso:** $h = {det_s13['h']:.6f}$\n"
                f"- **Extremos ($E = y_0 + y_n$):** `{det_s13['E']:.6f}`\n"
                f"- **Pares Interiores ($P$, peso 2):** `{det_s13['P']:.6f}`\n"
                f"- **Impares ($I$, peso 4):** `{det_s13['I']:.6f}`\n"
                f"- **Fórmula Evaluada:** `{det_s13['formula']} = {area_s13:.10f}`"
            )
        else:
            st.info("Ingrese un $n$ par (por ejemplo $n=4, 6, 8$) para ver el desglose puro de Simpson 1/3.")
    with c_d2:
        st.markdown("**Desglose por Bloques de Simpson 3/8:**")
        if det_s38 is not None:
            for idx_g, g in enumerate(det_s38["grupos"], 1):
                idxs = g["indices"]
                st.write(
                    rf"- **Grupo #{idx_g}** (nodos `{idxs}`, $x \in [{x_values[idxs[0]]:.3f}, {x_values[idxs[-1]]:.3f}]$): "
                    f"Área parcial = `{g['area']:.8f}`"
                )
        else:
            st.info("Ingrese un $n$ múltiplo de 3 (por ejemplo $n=3, 6, 9$) para ver los bloques cúbicos de Simpson 3/8.")

    st.subheader("3. Interpretación Geométrica: Arcos Parabólicos cada 3 Nodos")
    fig_s = go.Figure()
    if f_fn is not None:
        xs_smooth = np.linspace(a_val, b_val, 400)
        ys_smooth = np.array([float(f_fn(float(pt))) for pt in xs_smooth])
        fig_s.add_trace(go.Scatter(
            x=xs_smooth, y=ys_smooth, mode="lines",
            name="Función Real f(x)",
            line=dict(color="#1f77b4", width=3),
        ))

    colores_arco = ["rgba(44, 160, 44, 0.25)", "rgba(148, 103, 189, 0.25)"]
    line_colores = ["#2CA02C", "#9467BD"]
    num_pares = n_sub // 2
    for k in range(num_pares):
        i0 = 2 * k
        xs_arc, ys_arc = construir_arco_parabolico(
            x_values[i0], x_values[i0 + 1], x_values[i0 + 2],
            y_values[i0], y_values[i0 + 1], y_values[i0 + 2],
        )
        fig_s.add_trace(go.Scatter(
            x=xs_arc, y=ys_arc, mode="lines",
            name=f"Parábola Simpson [{x_values[i0]:.2f}, {x_values[i0+2]:.2f}]",
            line=dict(color=line_colores[k % 2], width=2.5),
            fill="tozeroy",
            fillcolor=colores_arco[k % 2],
        ))

    for xv, yv in zip(x_values, y_values):
        fig_s.add_trace(go.Scatter(
            x=[xv, xv], y=[0.0, yv], mode="lines",
            line=dict(color="rgba(120,120,120,0.45)", width=1, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
    fig_s.add_trace(go.Scatter(
        x=x_values, y=y_values, mode="markers",
        name="Nodos (x_i, y_i)",
        marker=dict(size=9, color="#D62728", line=dict(width=1.5, color="white")),
    ))
    fig_s.update_layout(
        title="Aproximación Mediante Arcos Parabólicos de Simpson 1/3",
        xaxis_title="x",
        yaxis_title="f(x)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_s, use_container_width=True)


def vista_comparativa_lab6():
    st.header("📊 Vista Comparativa: Integración y Diferenciación Numérica (Lab 6)")
    st.markdown(
        "Compare simultáneamente la **Regla del Trapecio**, **Simpson (1/3, 3/8 y Combinado)** y la **Cuadratura de Gregory** sobre el mismo conjunto de datos."
    )

    datos = _ui_entrada_datos_lab6("comp6")
    x_values, y_values = datos["x_values"], datos["y_values"]
    a_val, b_val, n_sub, h_val = datos["a_val"], datos["b_val"], datos["n_sub"], datos["h_val"]
    f_fn, d2_fn, d4_fn, integral_exacta = datos["f_fn"], datos["d2_fn"], datos["d4_fn"], datos["integral_exacta"]

    cota_trap = None
    cota_s13 = None
    cota_s38 = None
    if d2_fn is not None and d4_fn is not None:
        xs_dense = np.linspace(a_val, b_val, 500)
        max_d2 = float(np.max(np.abs([float(d2_fn(float(pt))) for pt in xs_dense])))
        max_d4 = float(np.max(np.abs([float(d4_fn(float(pt))) for pt in xs_dense])))
        cota_trap = calcular_error_trapecios(list(x_values), max_d2)
        cota_s13 = calcular_cota_error_simpson_1_3(x_values, max_d4)
        cota_s38 = calcular_cota_error_simpson_3_8(x_values, max_d4)

    x_list = list(x_values)
    y_list = list(y_values)
    resultados_int = []

    area_trap, det_trap = calcular_integral_trapecios(x_list, y_list)
    resultados_int.append(("Regla del Trapecio Compuesta", area_trap, cota_trap, "Aplicable para cualquier n ≥ 1"))

    if n_sub % 2 == 0:
        area_s13, det_s13 = calcular_simpson_1_3(x_list, y_list)
        resultados_int.append(("Regla de Simpson 1/3", area_s13, cota_s13, f"n = {n_sub} par (Exacto hasta grado 3)"))
    else:
        resultados_int.append(("Regla de Simpson 1/3", None, cota_s13, f"No aplicable: n = {n_sub} es impar"))

    if n_sub % 3 == 0:
        area_s38, det_s38 = calcular_simpson_3_8(x_list, y_list)
        resultados_int.append(("Regla de Simpson 3/8", area_s38, cota_s38, f"n = {n_sub} múltiplo de 3"))
    else:
        resultados_int.append(("Regla de Simpson 3/8", None, cota_s38, f"No aplicable: n = {n_sub} no es múltiplo de 3"))

    try:
        area_scomb, det_scomb = calcular_simpson_combinado(x_list, y_list)
        resultados_int.append((f"Simpson Automático ({det_scomb['metodo']})", area_scomb, cota_s13, "Combina 3/8 y 1/3 según paridad de n"))
    except Exception as e_comb:
        resultados_int.append(("Simpson Automático", None, None, str(e_comb)))

    area_greg, _ = calcular_integral_gregory(x_list, y_list)
    resultados_int.append(("Cuadratura de Gregory (Asc-Desc)", area_greg, None, "Trapecio + corrección de extremos Δy₀ y ∇yₙ"))

    filas_tabla_int = []
    for nombre_m, val_aprox, cota_m, obs_m in resultados_int:
        fila = {
            "Método": nombre_m,
            "Valor Aproximado": f"{val_aprox:.10f}" if val_aprox is not None else "No aplicable",
            "Valor Exacto Analítico": f"{integral_exacta:.10f}" if integral_exacta is not None else "N/A (Tabla)",
        }
        if val_aprox is not None and integral_exacta is not None:
            err_abs = abs(val_aprox - integral_exacta)
            err_rel = (err_abs / abs(integral_exacta) * 100.0) if abs(integral_exacta) > 1e-14 else 0.0
            fila["Error Absoluto"] = f"{err_abs:.4e}"
            fila["Error Relativo (%)"] = f"{err_rel:.6f}%"
        else:
            fila["Error Absoluto"] = "—"
            fila["Error Relativo (%)"] = "—"

        fila["Cota de Error Teórica"] = f"≤ {cota_m:.4e}" if cota_m is not None else "—"
        fila["Condición / Detalle"] = obs_m
        filas_tabla_int.append(fila)

    st.subheader("2. Tabla Resumen Comparativa")
    st.dataframe(pd.DataFrame(filas_tabla_int), use_container_width=True)

    st.subheader("3. Superposición Geométrica: Trapecios vs. Parábolas de Simpson")
    fig_geom = go.Figure()
    if f_fn is not None:
        xs_smooth = np.linspace(a_val, b_val, 400)
        ys_smooth = np.array([float(f_fn(float(pt))) for pt in xs_smooth])
        fig_geom.add_trace(go.Scatter(x=xs_smooth, y=ys_smooth, mode="lines", name="Función Real f(x)", line=dict(color="#1f77b4", width=3)))

    fig_geom.add_trace(go.Scatter(
        x=x_values, y=y_values, mode="lines",
        name="Techos Rectilíneos (Trapecios)",
        line=dict(color="#FF7F0E", width=2.2, dash="dash"),
    ))
    colores_arco = ["rgba(44, 160, 44, 0.22)", "rgba(148, 103, 189, 0.22)"]
    line_colores = ["#2CA02C", "#9467BD"]
    for k in range(n_sub // 2):
        i0 = 2 * k
        xs_arc, ys_arc = construir_arco_parabolico(
            x_values[i0], x_values[i0 + 1], x_values[i0 + 2],
            y_values[i0], y_values[i0 + 1], y_values[i0 + 2],
        )
        fig_geom.add_trace(go.Scatter(
            x=xs_arc, y=ys_arc, mode="lines",
            name=f"Parábola Simpson [{x_values[i0]:.2f}, {x_values[i0+2]:.2f}]",
            line=dict(color=line_colores[k % 2], width=2.5),
            fill="tozeroy",
            fillcolor=colores_arco[k % 2],
        ))
    fig_geom.add_trace(go.Scatter(
        x=x_values, y=y_values, mode="markers",
        name="Nodos (x_i, y_i)",
        marker=dict(size=9, color="#D62728"),
    ))
    fig_geom.update_layout(
        title="Comparación Geométrica: Cuerdas de Trapecio vs. Parábolas de Simpson",
        xaxis_title="x",
        yaxis_title="f(x)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_geom, use_container_width=True)


METODOS_LAB6 = {
    "Diferenciación Numérica (Gregory Ascendente-Descendente)": vista_diferenciacion_gregory,
    "Regla del Trapecio": vista_trapecio,
    "Regla de Simpson (1/3, 3/8 y Combinado)": vista_simpson,
    "📊 Vista Comparativa del Laboratorio": vista_comparativa_lab6,
}


def render_lab6(metodo_seleccionado=None):
    """Renderiza únicamente el método solicitado de Lab 6, o un selector si se ejecuta autónomamente."""
    if metodo_seleccionado is None:
        st.title("📐 Laboratorio 6: Integración y Diferenciación Numérica")
        metodo_seleccionado = st.selectbox(
            "Seleccione el método que desea estudiar:",
            list(METODOS_LAB6.keys()),
            key="lab6_standalone_sel",
        )
        st.markdown("---")

    funcion_vista = METODOS_LAB6.get(metodo_seleccionado, vista_comparativa_lab6)
    funcion_vista()


if __name__ == "__main__":
    try:
        st.set_page_config(layout="wide", page_title="Lab 6: Integración y Diferenciación Numérica")
    except Exception:
        pass
    render_lab6()
