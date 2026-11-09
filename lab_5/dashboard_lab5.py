# streamlit run "lab_5/dashboard_lab5.py"
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

LAB5_DIR = Path(__file__).resolve().parent
if str(LAB5_DIR) not in sys.path:
    sys.path.insert(0, str(LAB5_DIR))

from interpolacion_cuadratica_inversa import (
    AlgoritmoInterpolacion as InterpolacionCuadraticaInversa,
)
from interpolacion_lineal import AlgoritmoInterpolacion as InterpolacionLinealInversa
from metodo_lagrange import (
    evaluar_polinomio_lagrange_completo,
    interpolar_lagrange,
    obtener_formula_polinomio_lagrange,
)
from newton_gregory_descendente import (
    calcular_diferencias_finitas_retrogradas,
    interpolar_newton_gregory_descendente,
)
from newton_grgegory_ascendente import (
    calcular_diferencias_finitas,
    interpolar_newton_gregory,
)


# --- FUNCIONES AUXILIARES ---

def format_latex(eq_str):
    """Formatea una ecuación en string compatible con LaTeX."""
    eq = eq_str.replace("**", "^").replace("*", r"\cdot ")
    eq = re.sub(r"\^(\d{2,})", r"^{\1}", eq)
    return eq


def verificar_equiespaciamiento(x_arr, tol=1e-7):
    """Verifica si los nodos x_i tienen paso h constante."""
    diffs = np.diff(x_arr)
    es_equi = bool(np.allclose(diffs, diffs[0], rtol=tol, atol=tol))
    h_prom = float(diffs[0]) if es_equi else float(np.mean(diffs))
    return es_equi, h_prom, diffs


def interpolacion_lineal_directa(x_arr, y_arr, x_p):
    """Interpolación lineal directa por tramos para evaluar y(x_p)."""
    n = len(x_arr)
    idx = 0
    for i in range(n - 1):
        if (x_arr[i] <= x_p <= x_arr[i + 1]) or (x_arr[i] >= x_p >= x_arr[i + 1]):
            idx = i
            break
    else:
        idx = 0 if abs(x_p - x_arr[0]) < abs(x_p - x_arr[-1]) else n - 2

    x0, x1 = float(x_arr[idx]), float(x_arr[idx + 1])
    y0, y1 = float(y_arr[idx]), float(y_arr[idx + 1])
    if abs(x1 - x0) < 1e-14:
        raise ZeroDivisionError("Dos nodos consecutivos tienen el mismo valor de x.")
    pendiente = (y1 - y0) / (x1 - x0)
    y_interp = y0 + pendiente * (x_p - x0)
    return {
        "indice": idx,
        "x0": x0,
        "x1": x1,
        "y0": y0,
        "y1": y1,
        "pendiente": pendiente,
        "valor": y_interp,
    }


def construir_polinomio_simbolico_latex(x_arr, y_arr, max_nodos=8):
    """Construye y simplifica simbólicamente el polinomio interpolador P(x) en LaTeX."""
    if len(x_arr) > max_nodos:
        return None
    x_sym = sp.Symbol("x")
    n = len(x_arr)
    poly_expr = 0
    for i in range(n):
        termino = float(y_arr[i])
        for j in range(n):
            if i != j:
                termino *= (x_sym - float(x_arr[j])) / float(x_arr[i] - x_arr[j])
        poly_expr += termino
    poly_simpl = sp.expand(poly_expr)
    poly_clean = poly_simpl.xreplace({
        num: round(float(num), 5)
        for num in poly_simpl.atoms(sp.Float)
    })
    return sp.latex(poly_clean)


def formatear_tabla_diferencias_progresivas(x_arr, tabla_diff):
    """Convierte la matriz de diferencias finitas progresivas (Delta^k y) en DataFrame legible."""
    n = len(x_arr)
    filas = []
    for i in range(n):
        fila = {"i": i, "x_i": x_arr[i], "y_i = Δ⁰y_i": tabla_diff[i, 0]}
        for j in range(1, n):
            if i < n - j:
                fila[f"Δ^{j}y_i"] = tabla_diff[i, j]
            else:
                fila[f"Δ^{j}y_i"] = np.nan
        filas.append(fila)
    return pd.DataFrame(filas)


def formatear_tabla_diferencias_retrogradas(x_arr, tabla_diff):
    """Convierte la matriz de diferencias finitas retrógradas (Nabla^k y) en DataFrame legible."""
    n = len(x_arr)
    filas = []
    for i in range(n):
        fila = {"i": i, "x_i": x_arr[i], "y_i = ∇⁰y_i": tabla_diff[i, 0]}
        for j in range(1, n):
            if i >= j:
                fila[f"∇^{j}y_i"] = tabla_diff[i, j]
            else:
                fila[f"∇^{j}y_i"] = np.nan
        filas.append(fila)
    return pd.DataFrame(filas)


# --- COMPONENTE DE ENTRADA COMPARTIDO (DOBLE MODALIDAD) ---

def _render_input_datos_lab5(key_prefix, requiere_equi=False):
    st.subheader("1. Definición de Datos: Tabla de Puntos $(x_i, y_i)$ o Función Simbólica $f(x)$")
    modalidad = st.radio(
        "Seleccione cómo desea ingresar los datos:",
        [
            "📊 Modalidad 1: Desde Tabla de Puntos (x_i, y_i) Editable",
            "🧮 Modalidad 2: Desde Función Simbólica f(x) (Análisis de Error y Fenómeno de Runge)",
        ],
        horizontal=True,
        key=f"mod_{key_prefix}",
    )

    f_real_fn = None

    if "Modalidad 1" in modalidad:
        caso_tabla = st.selectbox(
            "Seleccione un Caso de Estudio o edite la tabla:",
            [
                "Caso A: Viscosidad Dinámica del Agua vs. Temperatura (Nodos Equiespaciados h = 5 — Ideal para Newton-Gregory)",
                "Caso B: Mediciones de Sensor con Muestreo Irregular (Nodos NO Equiespaciados — Ideal para Lagrange)",
                "Caso C: Tabla Cúbica Exacta y = x³ + 1 (Diferencias Finitas de 3° Orden Constantes)",
                "Personalizado: Editar o agregar filas libremente en la tabla",
            ],
            key=f"caso_t_{key_prefix}",
        )

        if "Caso A" in caso_tabla:
            df_base = pd.DataFrame({
                "x": [0.0, 5.0, 10.0, 15.0, 20.0],
                "y": [1.792, 1.519, 1.308, 1.140, 1.002],
            })
            xp_default = 7.5
            yq_default = 1.400
            st.info(
                "📌 **Caso A (Guía Lab 5 — Viscosidad del Agua):** Nodos equiespaciados cada $h = 5^\\circ\\text{C}$. "
                "Apto para todos los métodos de interpolación."
            )
        elif "Caso B" in caso_tabla:
            df_base = pd.DataFrame({
                "x": [1.0, 2.0, 4.5, 6.0, 9.5],
                "y": [2.10, 3.85, 8.90, 14.20, 29.80],
            })
            xp_default = 5.0
            yq_default = 10.0
            st.info(
                "⚠️ **Caso B (Muestreo No Equiespaciado):** Los pasos entre nodos varían ($\\Delta x_i \\in \\{1.0, 2.5, 1.5, 3.5\\}$). "
                "Permite observar por qué **Newton-Gregory no es teóricamente aplicable** cuando $h \\neq \\text{cte}$ y cómo **Lagrange** lo resuelve exactamente."
            )
        elif "Caso C" in caso_tabla:
            df_base = pd.DataFrame({
                "x": [0.0, 1.0, 2.0, 3.0, 4.0],
                "y": [1.0, 2.0, 9.0, 28.0, 65.0],
            })
            xp_default = 2.5
            yq_default = 15.0
            st.info("🔬 **Caso C ($y = x^3 + 1$):** Las diferencias de 3° orden $\\Delta^3 y_i$ son constantes y $\\Delta^4 y_i = 0$.")
        else:
            df_base = pd.DataFrame({
                "x": [0.0, 2.0, 4.0, 6.0],
                "y": [1.0, 4.0, 2.0, 5.0],
            })
            xp_default = 3.0
            yq_default = 3.0
            st.info("✏️ **Tabla Personalizada:** Modifique, agregue o elimine filas directamente en la tabla.")

        df_puntos = st.data_editor(
            df_base,
            num_rows="dynamic",
            use_container_width=True,
            key=f"ed_t_{key_prefix}_{caso_tabla[:8]}",
        )
    else:
        caso_fn = st.selectbox(
            "Seleccione una función de estudio o ingrese una expresión simbólica:",
            [
                "Caso Runge: Fenómeno de Runge -> f(x) = 1 / (1 + 25*x**2) en [-1, 1]",
                "Caso Oscilatorio: Onda Amortiguada -> f(x) = exp(-0.4*x) * cos(2*x) en [0, 4]",
                "Caso Logarítmico: Crecimiento Suave -> f(x) = log(x + 2) + 0.2*x**2 en [0, 4]",
                "Personalizado: Ingresar cualquier f(x) con SymPy",
            ],
            key=f"caso_f_{key_prefix}",
        )

        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        if "Runge" in caso_fn:
            eq_def, a_def, b_def, n_def = "1 / (1 + 25*x**2)", -1.0, 1.0, 7
            contexto_fn = (
                "🚨 **Fenómeno de Runge:** Al interpolar $f(x) = \\frac{1}{1+25x^2}$ con nodos equiespaciados de grado alto, "
                "surgen oscilaciones severas cerca de los extremos $[-1, 1]$."
            )
        elif "Oscilatorio" in caso_fn:
            eq_def, a_def, b_def, n_def = "exp(-0.4*x)*cos(2*x)", 0.0, 4.0, 6
            contexto_fn = "🌊 **Onda Amortiguada:** Permite contrastar la precisión de aproximación cerca de $x_0$ vs. $x_n$."
        elif "Logarítmico" in caso_fn:
            eq_def, a_def, b_def, n_def = "log(x + 2) + 0.2*x**2", 0.0, 4.0, 5
            contexto_fn = "📐 **Función Suave:** El polinomio interpolador converge con error mínimo."
        else:
            eq_def, a_def, b_def, n_def = "sin(x) + 0.5*x", 0.0, 3.1416, 5
            contexto_fn = "✏️ **Función Simbólica Personalizada:** Evaluada con SymPy para medir el error $|f(x) - P(x)|$."

        with c_f1:
            f_real_str = st.text_input("Función simbólica f(x):", value=eq_def, key=f"fstr_{key_prefix}")
        with c_f2:
            a_nod = st.number_input("Extremo izquierdo a:", value=a_def, key=f"a_{key_prefix}")
        with c_f3:
            b_nod = st.number_input("Extremo derecho b:", value=b_def, key=f"b_{key_prefix}")
        with c_f4:
            n_nod = int(st.number_input("Cantidad de nodos (n):", min_value=3, max_value=15, value=n_def, key=f"n_{key_prefix}"))

        tipo_malla = st.radio(
            "Distribución de los nodos en [a, b]:",
            ["Equiespaciados (h constante)", "No Equiespaciados (Nodos de Chebyshev — Ideal para Lagrange)"],
            horizontal=True,
            key=f"malla_{key_prefix}",
        )

        x_sym = sp.Symbol("x")
        try:
            f_simb = sp.sympify(f_real_str)
            f_real_fn = sp.lambdify(x_sym, f_simb, "numpy")
            st.latex(r"f(x) = " + sp.latex(f_simb))
            st.info(contexto_fn)
        except Exception as e:
            st.error(f"Error al interpretar f(x) con SymPy: {e}")
            st.stop()

        if a_nod >= b_nod:
            st.error("El extremo izquierdo 'a' debe ser menor que 'b'.")
            st.stop()

        if "Equiespaciados" in tipo_malla:
            xs_gen = np.linspace(a_nod, b_nod, n_nod)
        else:
            k_idx = np.arange(1, n_nod + 1)
            cheb = np.cos((2 * k_idx - 1) * np.pi / (2 * n_nod))
            xs_gen = np.sort(0.5 * (a_nod + b_nod) + 0.5 * (b_nod - a_nod) * cheb)

        ys_gen = np.array([float(f_real_fn(float(val))) for val in xs_gen])
        df_puntos = st.data_editor(
            pd.DataFrame({"x": np.round(xs_gen, 6), "y": np.round(ys_gen, 6)}),
            use_container_width=True,
            key=f"ed_fn_{key_prefix}_{caso_fn[:8]}_{n_nod}_{tipo_malla[:4]}",
        )
        xp_default = float(0.35 * a_nod + 0.65 * b_nod)
        yq_default = float(np.mean(ys_gen))

    df_puntos = df_puntos.dropna().sort_values(by="x").reset_index(drop=True)
    x_vals = df_puntos["x"].to_numpy(dtype=float)
    y_vals = df_puntos["y"].to_numpy(dtype=float)

    if len(x_vals) < 2:
        st.error("Se requieren al menos 2 nodos (x_i, y_i) para interpolar.")
        st.stop()

    if len(np.unique(x_vals)) != len(x_vals):
        st.error("Los valores de los nodos x_i deben ser todos distintos.")
        st.stop()

    es_equi, h_paso, diffs_x = verificar_equiespaciamiento(x_vals)
    if es_equi:
        st.success(f"✅ **Validación Teórica — Nodos Equiespaciados:** Paso constante $h = {h_paso:.6f}$.")
    else:
        st.warning(
            f"⚠️ **Validación Teórica — Nodos NO Equiespaciados ($\\Delta x_i = {np.round(diffs_x, 4).tolist()}$):** "
            "Los métodos de **Newton-Gregory (Ascendente y Descendente)** y la **Interpolación Cuadrática Inversa por diferencias finitas** "
            "asumen un paso constante $h$ y **no son teóricamente aplicables** aquí. En cambio, el **Método de Lagrange** soporta cualquier espaciamiento sin pérdida de exactitud."
        )

    return x_vals, y_vals, es_equi, h_paso, xp_default, yq_default, f_real_fn


def _graficar_curva_individual(x_vals, y_vals, x_p, y_p, nombre_metodo, fn_eval_vector, f_real_fn, color_curva="#636EFA"):
    """Grafica en Plotly los nodos, el polinomio del método seleccionado, el punto interpolado y el error."""
    margen = max((x_vals[-1] - x_vals[0]) * 0.08, 0.25)
    x_min_g = min(x_vals[0], x_p) - margen
    x_max_g = max(x_vals[-1], x_p) + margen
    x_grid = np.linspace(x_min_g, x_max_g, 350)
    y_poly_grid = fn_eval_vector(x_grid)

    fig = go.Figure()
    if f_real_fn is not None:
        y_real_grid = np.array([float(f_real_fn(float(xv))) for xv in x_grid])
        fig.add_trace(go.Scatter(
            x=x_grid, y=y_real_grid, mode="lines",
            name="Función Real f(x)",
            line=dict(color="#00CC96", width=3),
        ))

    fig.add_trace(go.Scatter(
        x=x_grid, y=y_poly_grid, mode="lines",
        name=nombre_metodo,
        line=dict(color=color_curva, width=2.6),
    ))
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals, mode="markers",
        name="Nodos Originales (x_i, y_i)",
        marker=dict(size=10, color="#EF553B", symbol="circle", line=dict(width=1.5, color="white")),
    ))
    fig.add_trace(go.Scatter(
        x=[x_p], y=[y_p], mode="markers+text",
        name=f"Punto Interpolado ({x_p:.3f}, {y_p:.4f})",
        text=[f"P({x_p:.2f}) = {y_p:.4f}"],
        textposition="top center",
        marker=dict(size=14, color="gold", symbol="star", line=dict(width=1.5, color="black")),
    ))
    fig.update_layout(
        title=f"Curva Interpoladora — {nombre_metodo}",
        xaxis_title="x",
        yaxis_title="y",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    if f_real_fn is not None:
        fig_err = go.Figure()
        fig_err.add_trace(go.Scatter(
            x=x_grid, y=np.abs(y_real_grid - y_poly_grid),
            mode="lines", name=f"|f(x) - P(x)| ({nombre_metodo})",
            line=dict(color="#EF553B", width=2.2),
            fill="tozeroy",
        ))
        fig_err.update_layout(
            title="Curva del Error de Truncamiento |f(x) - P(x)|",
            xaxis_title="x",
            yaxis_title="Error Absoluto |f(x) - P(x)|",
            hovermode="x unified",
        )
        st.plotly_chart(fig_err, use_container_width=True)


# --- VISTAS INDIVIDUALES POR MÉTODO ---

def vista_interpolacion_lineal(key_prefix="ilin"):
    st.header("📏 Método de Interpolación Lineal (Directa e Inversa)")
    st.markdown(
        """
        > **Fundamento Teórico:**  
        > Conecta dos puntos consecutivos $(x_0, y_0)$ y $(x_1, y_1)$ mediante una recta secante de primer grado.  
        > - **Interpolación Lineal Directa (hallar $y$ dado $x$):** $y(x) = y_0 + \\frac{y_1 - y_0}{x_1 - x_0}(x - x_0)$  
        > - **Interpolación Lineal Inversa (hallar $x$ dado $y$, `interpolacion_lineal.py`):** $x(y) = x_0 + \\frac{y - y_0}{y_1 - y_0} h$
        """
    )

    x_vals, y_vals, _, _, xp_def, yq_def, f_real_fn = _render_input_datos_lab5(key_prefix)
    st.markdown("---")

    c_dir, c_inv = st.columns(2)
    with c_dir:
        st.subheader("2A. Interpolación Lineal Directa $y(x_p)$")
        x_p = st.number_input("Valor de x_p a interpolar:", value=float(xp_def), format="%.6f", key=f"xp_{key_prefix}")
        res_dir = interpolacion_lineal_directa(x_vals, y_vals, x_p)
        st.success(f"**Valor Interpolado:** $P_1({x_p:.4f}) = {res_dir['valor']:.6f}$")
        st.markdown(
            f"- **Tramo usado:** $[{res_dir['x0']:.4f}, {res_dir['x1']:.4f}]$\n"
            f"- **Ordenadas:** $y_0 = {res_dir['y0']:.6f}, \\; y_1 = {res_dir['y1']:.6f}$\n"
            f"- **Pendiente del tramo:** $m = {res_dir['pendiente']:.6f}$"
        )
        st.latex(
            rf"P_1({x_p:.4f}) = {res_dir['y0']:.4f} + {res_dir['pendiente']:.4f}\cdot({x_p:.4f} - {res_dir['x0']:.4f}) = {res_dir['valor']:.6f}"
        )

    with c_inv:
        st.subheader("2B. Interpolación Lineal Inversa $x(y_{\\text{buscado}})$")
        y_q = st.number_input("Valor de y_buscado para despejar x:", value=float(yq_def), format="%.6f", key=f"yq_{key_prefix}")
        try:
            datos_lin_inv = InterpolacionLinealInversa.calcular_interpolacion(list(x_vals), list(y_vals), y_q)
            st.success(f"**Abscisa despejada:** $x = {datos_lin_inv['x_resultado']:.6f}$")
            st.markdown(
                f"- **Tramo seleccionado (índice {datos_lin_inv['indice']}):** "
                f"$P_0({datos_lin_inv['x0']:.4f}, {datos_lin_inv['y0']:.4f})$ a $P_1({datos_lin_inv['x1']:.4f}, {datos_lin_inv['y1']:.4f})$\n"
                f"- **Parámetros:** $h = {datos_lin_inv['h']:.4f}$, $\\Delta y = {datos_lin_inv['delta_y']:.6f}$, $y - y_0 = {datos_lin_inv['diferencia_y']:.6f}$"
            )
            st.latex(
                rf"x = {datos_lin_inv['x0']:.4f} + \frac{{{datos_lin_inv['diferencia_y']:.4f} \cdot {datos_lin_inv['h']:.4f}}}{{{datos_lin_inv['delta_y']:.4f}}} = {datos_lin_inv['x_resultado']:.6f}"
            )
        except Exception as e:
            st.error(f"Error en Interpolación Lineal Inversa: {e}")

    st.subheader("3. Representación Gráfica en Plotly")
    _graficar_curva_individual(
        x_vals, y_vals, x_p, res_dir["valor"],
        "Interpolación Lineal por Tramos P₁(x)",
        lambda grid: np.array([interpolacion_lineal_directa(x_vals, y_vals, float(xv))["valor"] for xv in grid]),
        f_real_fn,
        color_curva="#19D3F3",
    )


def vista_interpolacion_cuadratica_inversa(key_prefix="icuad"):
    st.header("🔄 Método de Interpolación Cuadrática Inversa")
    st.markdown(
        """
        > **Fundamento Teórico (`interpolacion_cuadratica_inversa.py`):**  
        > Cuando conocemos un valor objetivo $y_{\\text{buscado}}$ y necesitamos hallar $x = g(y)$ (o una raíz haciendo $y_{\\text{buscado}} = 0$), tomamos **3 puntos consecutivos** $(x_0, y_0), (x_1, y_1), (x_2, y_2)$ en el polinomio de 2° grado de Newton-Gregory en función de $u = x - x_0$, y resolvemos la ecuación cuadrática resultante:
        """
    )
    st.latex(
        r"y = y_0 + \frac{\Delta y_0}{h} u + \frac{\Delta^2 y_0}{2 h^2} u(u - h) \implies \underbrace{\left(\frac{\Delta^2 y_0}{2 h^2}\right)}_{a} u^2 + \underbrace{\left(\frac{\Delta y_0}{h} - \frac{\Delta^2 y_0}{2h}\right)}_{b} u + \underbrace{(y_0 - y_{\text{buscado}})}_{c} = 0"
    )

    x_vals, y_vals, _, _, _, yq_def, _ = _render_input_datos_lab5(key_prefix)
    st.markdown("---")

    if len(x_vals) < 3:
        st.error("Se requieren al menos 3 puntos en la tabla para aplicar Interpolación Cuadrática Inversa.")
        return

    st.subheader("2. Cálculo Paso a Paso de $a u^2 + b u + c = 0$")
    y_buscado = st.number_input(
        "Ingrese el valor de ordenada y_buscado para hallar x (use y = 0 para buscar raíces):",
        value=float(yq_def),
        format="%.6f",
        key=f"yb_{key_prefix}",
    )

    try:
        datos = InterpolacionCuadraticaInversa.calcular_interpolacion(list(x_vals), list(y_vals), y_buscado)
    except Exception as e:
        st.error(f"No se pudo completar la Interpolación Cuadrática Inversa: {e}")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. Nodos Seleccionados y Diferencias:**")
        st.write(
            f"- **Índice de inicio:** `{datos['indice']}`\n"
            f"- $P_0 = ({datos['x0']:.4f}, \\; {datos['y0']:.6f})$\n"
            f"- $P_1 = ({datos['x1']:.4f}, \\; {datos['y1']:.6f})$\n"
            f"- $P_2 = ({datos['x2']:.4f}, \\; {datos['y2']:.6f})$\n"
            f"- **Paso:** $h = {datos['h']:.6f}$\n"
            f"- $\\Delta y_0 = {datos['delta_y0']:.6f}$\n"
            f"- $\\Delta^2 y_0 = {datos['delta2_y0']:.6f}$"
        )
    with c2:
        st.markdown("**2. Coeficientes de $a u^2 + b u + c = 0$:**")
        st.write(
            f"- $a = \\frac{{\\Delta^2 y_0}}{{2h^2}} = {datos['coef_a']:.8f}$\n"
            f"- $b = \\frac{{\\Delta y_0}}{{h}} - \\frac{{\\Delta^2 y_0}}{{2h}} = {datos['coef_b']:.8f}$\n"
            f"- $c = -(y - y_0) = {datos['coef_c']:.8f}$\n"
            f"- **Discriminante:** $D = b^2 - 4ac = {datos['discriminante']:.8f}$"
        )
    with c3:
        st.markdown("**3. Raíces de la Parábola y Selección:**")
        st.write(
            f"- **Raíz 1:** $x_1 = x_0 + u_1 = {datos['x_sol1']:.8f}$\n"
            f"- **Raíz 2:** $x_2 = x_0 + u_2 = {datos['x_sol2']:.8f}$"
        )
        st.success(f"🎯 **Valor $x$ Seleccionado en el Intervalo:**\n### $x = {datos['x_resultado']:.8f}$")

    with st.expander("📄 Ver Reporte Completo Paso a Paso (formato de la cátedra)"):
        st.code(InterpolacionCuadraticaInversa.generar_reporte(datos))

    st.subheader("3. Visualización de la Parábola en el Plano Directo $(x, y)$ e Inverso $(y, x)$")
    x0_c, x1_c, x2_c = datos["x0"], datos["x1"], datos["x2"]
    y0_c, y1_c, y2_c = datos["y0"], datos["y1"], datos["y2"]
    a_c, b_c = datos["coef_a"], datos["coef_b"]

    span_x = max(abs(x2_c - x0_c), 1.0)
    xs_parab = np.linspace(min(x0_c, x2_c) - 0.35 * span_x, max(x0_c, x2_c) + 0.35 * span_x, 300)
    us_parab = xs_parab - x0_c
    ys_parab = y0_c + b_c * us_parab + a_c * (us_parab ** 2)

    c_g1, c_g2 = st.columns(2)
    with c_g1:
        fig_inv1 = go.Figure()
        fig_inv1.add_trace(go.Scatter(x=xs_parab, y=ys_parab, mode="lines", name="Parábola Interpoladora y(x)", line=dict(color="#636EFA", width=2.5)))
        fig_inv1.add_trace(go.Scatter(
            x=[x0_c, x1_c, x2_c], y=[y0_c, y1_c, y2_c],
            mode="markers+text", name="3 Nodos del Tramo",
            text=["P0", "P1", "P2"], textposition="top left",
            marker=dict(size=10, color="#EF553B"),
        ))
        fig_inv1.add_hline(y=y_buscado, line_dash="dash", line_color="green", annotation_text=f"y_buscado = {y_buscado:.4f}")
        fig_inv1.add_trace(go.Scatter(
            x=[datos["x_resultado"]], y=[y_buscado],
            mode="markers+text", name=f"x = {datos['x_resultado']:.4f}",
            text=[f"x = {datos['x_resultado']:.4f}"], textposition="bottom right",
            marker=dict(size=14, color="gold", symbol="star", line=dict(width=1.5, color="black")),
        ))
        fig_inv1.update_layout(title="Plano Directo (x, y): Corte con y = y_buscado", xaxis_title="x", yaxis_title="y", hovermode="x unified")
        st.plotly_chart(fig_inv1, use_container_width=True)

    with c_g2:
        fig_inv2 = go.Figure()
        fig_inv2.add_trace(go.Scatter(x=ys_parab, y=xs_parab, mode="lines", name="Parábola Horizontal x = g(y)", line=dict(color="#AB63FA", width=2.5)))
        fig_inv2.add_trace(go.Scatter(
            x=[y0_c, y1_c, y2_c], y=[x0_c, x1_c, x2_c],
            mode="markers+text", name="Nodos Invertidos (y_i, x_i)",
            text=["P0", "P1", "P2"], textposition="top left",
            marker=dict(size=10, color="#EF553B"),
        ))
        fig_inv2.add_vline(x=y_buscado, line_dash="dash", line_color="green", annotation_text=f"y = {y_buscado:.4f}")
        fig_inv2.add_trace(go.Scatter(
            x=[y_buscado], y=[datos["x_resultado"]],
            mode="markers+text", name=f"x(y) = {datos['x_resultado']:.4f}",
            text=[f"x = {datos['x_resultado']:.4f}"], textposition="top right",
            marker=dict(size=14, color="gold", symbol="star", line=dict(width=1.5, color="black")),
        ))
        fig_inv2.update_layout(title="Plano Inverso (y, x): Cambio de Rol x = g(y)", xaxis_title="y (Variable Conocida)", yaxis_title="x = g(y)", hovermode="x unified")
        st.plotly_chart(fig_inv2, use_container_width=True)


def vista_lagrange(key_prefix="lag"):
    st.header("📐 Método de Interpolación de Lagrange")
    st.markdown(
        """
        > **Fundamento Teórico (`metodo_lagrange.py`):**  
        > Construye el polinomio interpolador único de grado $\\le n-1$ como combinación lineal de los **Polinomios Base de Lagrange** $L_i(x)$ (donde $L_i(x_i)=1$ y $L_i(x_j)=0$ para $j \\neq i$).  
        > **Ventaja fundamental:** **No requiere que los nodos $x_i$ estén equiespaciados.**
        """
    )
    st.latex(
        r"P(x) = \sum_{i=0}^{n-1} y_i \cdot L_i(x), \qquad \text{donde} \qquad L_i(x) = \prod_{\substack{j=0 \\ j \neq i}}^{n-1} \frac{x - x_j}{x_i - x_j}"
    )

    x_vals, y_vals, _, _, xp_def, _, f_real_fn = _render_input_datos_lab5(key_prefix)
    st.markdown("---")

    poly_latex = construir_polinomio_simbolico_latex(x_vals, y_vals, max_nodos=8)
    if poly_latex is not None:
        st.markdown("**Expresión Simbólica Simplificada del Polinomio Interpolador $P(x)$:**")
        st.latex(r"P(x) = " + poly_latex)

    st.subheader("2. Evaluación en $x_p$ y Polinomios Base $L_i(x_p)$")
    x_p = st.number_input("Punto x_p donde evaluar el Polinomio de Lagrange:", value=float(xp_def), format="%.6f", key=f"xp_{key_prefix}")

    t0 = time.perf_counter()
    res_lag = interpolar_lagrange(x_vals, y_vals, x_p)
    t_lag = time.perf_counter() - t0

    c1, c2 = st.columns(2)
    c1.success(f"🎯 **Valor Interpolado:** $P({x_p:.4f}) = {res_lag['valor']:.8f}$ (Grado $\\le {res_lag['puntos'] - 1}$)")
    c2.info(f"⏱️ **Tiempo de Ejecución:** {t_lag:.6f} s")

    formulas_lag = obtener_formula_polinomio_lagrange(x_vals, y_vals)
    df_lag_terms = pd.DataFrame([
        {
            "Nodo i": i,
            "x_i": x_vals[i],
            "y_i": y_i,
            "Polinomio Base L_i(x_p)": L_i,
            "Término y_i · L_i(x_p)": term_i,
            "Estructura Simbólica de y_i · L_i(x)": formulas_lag[i],
        }
        for i, (L_i, y_i, term_i) in enumerate(res_lag["terminos"])
    ])
    df_lag_terms["Suma Acumulada"] = df_lag_terms["Término y_i · L_i(x_p)"].cumsum()
    st.dataframe(df_lag_terms.style.format(precision=6), use_container_width=True)

    st.subheader("3. Gráfico del Polinomio de Lagrange en Plotly")
    _graficar_curva_individual(
        x_vals, y_vals, x_p, res_lag["valor"],
        "Polinomio de Lagrange P(x)",
        lambda grid: evaluar_polinomio_lagrange_completo(x_vals, y_vals, grid),
        f_real_fn,
        color_curva="#636EFA",
    )


def vista_newton_gregory(key_prefix="nga", modo="ascendente"):
    if modo == "ascendente":
        st.header("📈 Método de Newton-Gregory Ascendente (Diferencias Progresivas)")
        st.markdown(
            """
            > **Fundamento Teórico (`newton_grgegory_ascendente.py`):**  
            > Utiliza las **diferencias finitas progresivas** $\\Delta^k y_0$ apoyadas en el **primer nodo $x_0$**, con el parámetro normalizado $u = \\frac{x - x_0}{h}$. Es ideal para interpolar puntos cercanos al **inicio de la tabla** y requiere paso constante $h$.
            """
        )
        st.latex(
            r"P(x) = y_0 + u\Delta y_0 + \frac{u(u-1)}{2!}\Delta^2 y_0 + \frac{u(u-1)(u-2)}{3!}\Delta^3 y_0 + \dots + \binom{u}{n}\Delta^n y_0, \qquad u = \frac{x - x_0}{h}"
        )
    else:
        st.header("📉 Método de Newton-Gregory Descendente (Diferencias Retrógradas)")
        st.markdown(
            """
            > **Fundamento Teórico (`newton_gregory_descendente.py`):**  
            > Utiliza las **diferencias finitas retrógradas** $\\nabla^k y_n$ apoyadas en el **último nodo $x_n$**, con el parámetro normalizado $v = \\frac{x - x_n}{h}$. Es ideal para interpolar puntos cercanos al **final de la tabla** y requiere paso constante $h$.
            """
        )
        st.latex(
            r"P(x) = y_n + v\nabla y_n + \frac{v(v+1)}{2!}\nabla^2 y_n + \frac{v(v+1)(v+2)}{3!}\nabla^3 y_n + \dots, \qquad v = \frac{x - x_n}{h}"
        )

    x_vals, y_vals, es_equi, h_paso, xp_def, _, f_real_fn = _render_input_datos_lab5(key_prefix, requiere_equi=True)
    st.markdown("---")

    poly_latex = construir_polinomio_simbolico_latex(x_vals, y_vals, max_nodos=8)
    if poly_latex is not None and es_equi:
        st.markdown("**Expresión Simbólica Simplificada del Polinomio $P(x)$:**")
        st.latex(r"P(x) = " + poly_latex)

    x_p = st.number_input("Punto x_p a interpolar:", value=float(xp_def), format="%.6f", key=f"xp_{key_prefix}")

    if modo == "ascendente":
        res = interpolar_newton_gregory(x_vals, y_vals, x_p)
        st.success(
            f"🎯 **Valor Interpolado:** $P({x_p:.4f}) = {res['valor']:.8f}$  |  "
            f"Nodo inicial $x_0 = {res['x0']:.4f}$, Paso $h = {res['h']:.4f}$, Parámetro $u = {res['u']:.6f}$"
        )
        st.subheader("2. Tabla de Diferencias Finitas Progresivas ($\\Delta^k y_i$)")
        df_diff = formatear_tabla_diferencias_progresivas(x_vals, res["tabla_diferencias"])
        st.dataframe(df_diff.style.format(precision=6, na_rep="—"), use_container_width=True)

        st.subheader("3. Desarrollo Término a Término de la Serie Ascendente")
        df_terms = pd.DataFrame([
            {
                "Orden (k)": k,
                "Coeficiente Binomial C(u, k)": coef,
                "Diferencia Progresiva Δ^k y_0": diff_val,
                "Valor del Término": term_val,
            }
            for k, (coef, diff_val, term_val) in enumerate(res["terminos"])
        ])
        df_terms["Suma Acumulada P(x_p)"] = df_terms["Valor del Término"].cumsum()
        st.dataframe(df_terms.style.format(precision=6), use_container_width=True)

        st.subheader("4. Gráfico del Polinomio en Plotly")
        _graficar_curva_individual(
            x_vals, y_vals, x_p, res["valor"],
            "Newton-Gregory Ascendente P(x)",
            lambda grid: np.array([interpolar_newton_gregory(x_vals, y_vals, float(xv))["valor"] for xv in grid]),
            f_real_fn,
            color_curva="#FFA15A",
        )
    else:
        res = interpolar_newton_gregory_descendente(x_vals, y_vals, x_p)
        st.success(
            f"🎯 **Valor Interpolado:** $P({x_p:.4f}) = {res['valor']:.8f}$  |  "
            f"Último nodo $x_n = {res['xn']:.4f}$, Paso $h = {res['h']:.4f}$, Parámetro $v = {res['v']:.6f}$"
        )
        st.subheader("2. Tabla de Diferencias Finitas Retrógradas ($\\nabla^k y_i$)")
        df_diff = formatear_tabla_diferencias_retrogradas(x_vals, res["tabla_diferencias"])
        st.dataframe(df_diff.style.format(precision=6, na_rep="—"), use_container_width=True)

        st.subheader("3. Desarrollo Término a Término de la Serie Descendente")
        df_terms = pd.DataFrame([
            {
                "Orden (k)": k,
                "Coeficiente Binomial C(v+k-1, k)": coef,
                "Diferencia Retrógrada ∇^k y_n": diff_val,
                "Valor del Término": term_val,
            }
            for k, (coef, diff_val, term_val) in enumerate(res["terminos"])
        ])
        df_terms["Suma Acumulada P(x_p)"] = df_terms["Valor del Término"].cumsum()
        st.dataframe(df_terms.style.format(precision=6), use_container_width=True)

        st.subheader("4. Gráfico del Polinomio en Plotly")
        _graficar_curva_individual(
            x_vals, y_vals, x_p, res["valor"],
            "Newton-Gregory Descendente P(x)",
            lambda grid: np.array([interpolar_newton_gregory_descendente(x_vals, y_vals, float(xv))["valor"] for xv in grid]),
            f_real_fn,
            color_curva="#AB63FA",
        )


def vista_comparativa_lab5(key_prefix="comp5"):
    st.header("📊 Vista Comparativa Integral — Laboratorio 5 (Interpolación Polinomial)")
    x_vals, y_vals, es_equi, h_paso, xp_def, _, f_real_fn = _render_input_datos_lab5(key_prefix)
    st.markdown("---")

    x_p = st.number_input("Punto x_p a interpolar y comparar:", value=float(xp_def), format="%.6f", key=f"xp_{key_prefix}")

    t0 = time.perf_counter()
    res_lin = interpolacion_lineal_directa(x_vals, y_vals, x_p)
    t_lin = time.perf_counter() - t0

    t0 = time.perf_counter()
    res_lag = interpolar_lagrange(x_vals, y_vals, x_p)
    t_lag = time.perf_counter() - t0

    t0 = time.perf_counter()
    res_nga = interpolar_newton_gregory(x_vals, y_vals, x_p)
    t_nga = time.perf_counter() - t0

    t0 = time.perf_counter()
    res_ngd = interpolar_newton_gregory_descendente(x_vals, y_vals, x_p)
    t_ngd = time.perf_counter() - t0

    y_ex = float(f_real_fn(x_p)) if f_real_fn is not None else None

    filas = []
    for nom, val, tm, obs in [
        ("Interpolación Lineal (por tramos)", res_lin["valor"], t_lin, f"Tramo [{res_lin['x0']:.3f}, {res_lin['x1']:.3f}]"),
        ("Método de Lagrange", res_lag["valor"], t_lag, "Apto para cualquier espaciamiento"),
        ("Newton-Gregory Ascendente", res_nga["valor"], t_nga, f"u = {res_nga['u']:.4f}" if es_equi else "⚠️ Inválido (h ≠ cte)"),
        ("Newton-Gregory Descendente", res_ngd["valor"], t_ngd, f"v = {res_ngd['v']:.4f}" if es_equi else "⚠️ Inválido (h ≠ cte)"),
    ]:
        f_d = {"Método": nom, "Valor P(x_p)": val, "Tiempo (s)": f"{tm:.6f}", "Observación": obs}
        if y_ex is not None:
            f_d["f(x_p) Exacto"] = y_ex
            f_d["Error Absoluto |f - P|"] = abs(val - y_ex)
        filas.append(f_d)

    st.dataframe(pd.DataFrame(filas).style.format(precision=7), use_container_width=True)

    margen = max((x_vals[-1] - x_vals[0]) * 0.08, 0.25)
    x_grid = np.linspace(min(x_vals[0], x_p) - margen, max(x_vals[-1], x_p) + margen, 300)
    y_lag_g = evaluar_polinomio_lagrange_completo(x_vals, y_vals, x_grid)
    y_nga_g = np.array([interpolar_newton_gregory(x_vals, y_vals, float(xv))["valor"] for xv in x_grid])
    y_ngd_g = np.array([interpolar_newton_gregory_descendente(x_vals, y_vals, float(xv))["valor"] for xv in x_grid])

    fig = go.Figure()
    if f_real_fn is not None:
        y_real_g = np.array([float(f_real_fn(float(xv))) for xv in x_grid])
        fig.add_trace(go.Scatter(x=x_grid, y=y_real_g, mode="lines", name="f(x) Exacta", line=dict(color="#00CC96", width=3)))
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="lines", name="Interpolación Lineal (Tramos)", line=dict(color="#19D3F3", width=1.8, dash="longdash")))
    fig.add_trace(go.Scatter(x=x_grid, y=y_lag_g, mode="lines", name="Polinomio de Lagrange", line=dict(color="#636EFA", width=2.5)))
    fig.add_trace(go.Scatter(x=x_grid, y=y_nga_g, mode="lines", name="Newton-Gregory Ascendente", line=dict(color="#FFA15A", width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=x_grid, y=y_ngd_g, mode="lines", name="Newton-Gregory Descendente", line=dict(color="#AB63FA", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="markers", name="Nodos (x_i, y_i)", marker=dict(size=10, color="#EF553B")))
    fig.add_trace(go.Scatter(x=[x_p], y=[res_lag["valor"]], mode="markers", name=f"P({x_p:.2f})", marker=dict(size=14, color="gold", symbol="star")))
    fig.update_layout(title="Superposición de Polinomios Interpoladores", xaxis_title="x", yaxis_title="y", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def render_lab5(metodo_seleccionado=None):
    """Punto de entrada modular para renderizar un método aislado o el selector del Lab 5."""
    opciones = [
        "Interpolación Lineal",
        "Interpolación Cuadrática Inversa",
        "Método de Lagrange",
        "Newton-Gregory Ascendente",
        "Newton-Gregory Descendente",
        "📊 Vista Comparativa del Laboratorio",
    ]
    if metodo_seleccionado is None:
        st.title("📈 Laboratorio 5: Interpolación y Aproximación Polinomial")
        metodo_seleccionado = st.radio(
            "Seleccione el método que desea estudiar:",
            opciones,
            horizontal=True,
        )
        st.markdown("---")

    if metodo_seleccionado == "Interpolación Lineal":
        vista_interpolacion_lineal("iso_ilin")
    elif metodo_seleccionado == "Interpolación Cuadrática Inversa":
        vista_interpolacion_cuadratica_inversa("iso_icuad")
    elif metodo_seleccionado == "Método de Lagrange":
        vista_lagrange("iso_lag")
    elif metodo_seleccionado == "Newton-Gregory Ascendente":
        vista_newton_gregory("iso_nga", modo="ascendente")
    elif metodo_seleccionado == "Newton-Gregory Descendente":
        vista_newton_gregory("iso_ngd", modo="descendente")
    else:
        vista_comparativa_lab5("iso_comp5")


if __name__ == "__main__":
    try:
        st.set_page_config(layout="wide", page_title="Lab 5: Interpolación y Aproximación Polinomial")
    except Exception:
        pass
    render_lab5(None)
