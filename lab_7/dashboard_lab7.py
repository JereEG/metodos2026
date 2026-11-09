# streamlit run "lab_7/dashboard_lab7.py"
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

LAB7_DIR = Path(__file__).resolve().parent
if str(LAB7_DIR) not in sys.path:
    sys.path.insert(0, str(LAB7_DIR))

from metodo_euler_y_mod_euler import (
    calcular_error_local,
    crear_funcion_desde_expresion,
    metodo_euler,
    metodo_euler_modificado,
)
from milner import metodo_milne, metodo_runge_kutta_4_inicial
from rungge_kutta import metodo_runge_kutta_2, metodo_runge_kutta_2_punto_medio


# --- FUNCIONES AUXILIARES Y WRAPPERS (_history) ---

def resolver_pvi_simbolico(expr_str, x0_val, y0_val):
    """
    Intenta resolver analíticamente el PVI y' = f(x, y), y(x0) = y0 usando sympy.dsolve.
    Retorna (latex_sol, callable_fn, exito).
    """
    x_s = sp.Symbol("x", real=True)
    y_s = sp.Symbol("y", real=True)
    y_func = sp.Function("y")(x_s)

    try:
        expr_sym = sp.sympify(expr_str, locals={"x": x_s, "y": y_s})
        expr_ode = expr_sym.subs(y_s, y_func)
        ode_eq = sp.Eq(sp.diff(y_func, x_s), expr_ode)

        sol = sp.dsolve(
            ode_eq,
            y_func,
            ics={y_func.subs(x_s, sp.Rational(str(round(x0_val, 8)))): sp.Rational(str(round(y0_val, 8)))},
        )
        if isinstance(sol, list):
            sol = sol[0]
        rhs_simpl = sp.simplify(sol.rhs)
        fn_exacta = sp.lambdify(x_s, rhs_simpl, "numpy")
        test_val = complex(fn_exacta(float(x0_val)))
        if abs(test_val.imag) > 1e-7 or np.isnan(test_val.real) or np.isinf(test_val.real):
            return None, None, False
        return sp.latex(rhs_simpl), lambda xv: float(np.real(fn_exacta(float(xv)))), True
    except Exception:
        return None, None, False


def referencia_numerica_alta_precision(f_callable, x0, y0, x_grid, subpasos=50):
    """Fallback numérico RK4 con malla ultrafina cuando la EDO no tiene solución simbólica cerrada."""
    y_ref = [float(y0)]
    x_act = float(x0)
    y_act = float(y0)
    for i in range(1, len(x_grid)):
        x_dest = float(x_grid[i])
        h_fino = (x_dest - x_act) / subpasos
        _, ys_sub = metodo_runge_kutta_4_inicial(f_callable, x_act, y_act, h_fino, n=subpasos)
        y_act = float(ys_sub[-1])
        x_act = x_dest
        y_ref.append(y_act)
    return y_ref


def euler_detallado_history(f_callable, x0, y0, h, n):
    """Wrapper sobre metodo_euler que registra las pendientes y pasos intermedios."""
    t0 = time.perf_counter()
    xs, ys = metodo_euler(f_callable, x0, y0, h, n)
    t_total = time.perf_counter() - t0
    pasos = []
    for i in range(n):
        pend = f_callable(xs[i], ys[i])
        pasos.append({
            "Paso (i)": i,
            "x_i": xs[i],
            "y_i": ys[i],
            "Pendiente f(x_i, y_i)": pend,
            "Incremento h·f": h * pend,
            "y_{i+1}": ys[i + 1],
        })
    return xs, ys, pasos, t_total


def _ui_entrada_pvi_lab7(key_prefix):
    """Panel común para plantear el PVI y' = f(x, y), y(x0) = y0."""
    st.subheader("1. Planteo del Problema de Valor Inicial (PVI)")

    caso = st.selectbox(
        "Seleccione un Caso de Estudio Físico/Matemático o ingrese su propia EDO:",
        [
            "Caso A: Crecimiento con Aceleración Exponencial -> y' = x + y, y(0) = 1 en [0, 2] (Euler se desvía drásticamente)",
            "Caso B: Enfriamiento / Amortiguación Gaussiana -> y' = -2*x*y, y(0) = 1 en [0, 2] (Curva campana e^(-x²))",
            "Caso C: Circuito RL / Relajación con Fuente -> y' = x - y, y(0) = 2 en [0, 3] (Estabilidad frente al paso h)",
            "Caso D: EDO No Lineal sin Solución Elemental -> y' = sin(x) - 0.3*y**2, y(0) = 1 en [0, 4]",
            "Personalizado: Ingresar libremente cualquier ecuación y' = f(x, y)",
        ],
        key=f"{key_prefix}_caso",
    )

    if "Caso A" in caso:
        eq_def, x0_def, y0_def, xf_def, h_def = "x + y", 0.0, 1.0, 2.0, 0.25
        contexto = (
            r"🚀 **Caso A ($y' = x + y, \; y(0)=1$):** La solución exacta es $y(x) = 2e^x - x - 1$. "
            r"Como la pendiente crece exponencialmente ($y'' = 2e^x > 0$), **el Método de Euler subestima sistemáticamente la curva** "
            r"en cada paso al usar únicamente la tangente inicial, acumulando un gran error global. En cambio, **Runge-Kutta 4** y **Milne** permanecen prácticamente superpuestos a la solución exacta."
        )
    elif "Caso B" in caso:
        eq_def, x0_def, y0_def, xf_def, h_def = "-2*x*y", 0.0, 1.0, 2.0, 0.25
        contexto = (
            r"🔔 **Caso B ($y' = -2xy, \; y(0)=1$):** La solución analítica es la campana gaussiana $y(x) = e^{-x^2}$. "
            r"Presenta un punto de inflexión en $x = 1/\sqrt{2} \approx 0.707$, pasando de cóncava hacia abajo a cóncava hacia arriba. "
            r"Ideal para observar cómo **Euler Modificado** y **RK2** corrigen el cambio de curvatura promediando pendientes."
        )
    elif "Caso C" in caso:
        eq_def, x0_def, y0_def, xf_def, h_def = "x - y", 0.0, 2.0, 3.0, 0.30
        contexto = (
            r"⚡ **Caso C ($y' = x - y, \; y(0)=2$):** Modelo de relajación hacia una asíntota oblicua ($y(x) = x - 1 + 3e^{-x}$). "
            r"Permite estudiar cómo varía el error local y global al modificar el tamaño del paso $h$."
        )
    elif "Caso D" in caso:
        eq_def, x0_def, y0_def, xf_def, h_def = "sin(x) - 0.3*y**2", 0.0, 1.0, 4.0, 0.40
        contexto = (
            r"🔬 **Caso D (EDO de Riccati No Lineal $y' = \sin(x) - 0.3y^2$):** No posee solución cerrada elemental. "
            r"El dashboard utiliza automáticamente una integración numérica ultrafina como referencia para contrastar el desempeño de los métodos."
        )
    else:
        eq_def, x0_def, y0_def, xf_def, h_def = "x**2 - y", 0.0, 1.0, 2.0, 0.25
        contexto = "✏️ **Modo Personalizado:** Ingrese cualquier expresión en términos de `x` e `y`."

    c1, c2, c3, c4, c5 = st.columns([2.2, 1, 1, 1, 1.2])
    with c1:
        expr_str = st.text_input("Ecuación diferencial y' = f(x, y):", value=eq_def, key=f"{key_prefix}_expr")
    with c2:
        x0_val = st.number_input("x₀ inicial:", value=x0_def, format="%.4f", key=f"{key_prefix}_x0")
    with c3:
        y0_val = st.number_input("y₀ = y(x₀):", value=y0_def, format="%.4f", key=f"{key_prefix}_y0")
    with c4:
        xf_val = st.number_input("x_f final:", value=xf_def, format="%.4f", key=f"{key_prefix}_xf")
    with c5:
        h_val = st.number_input("Paso (h):", min_value=0.005, max_value=2.0, value=h_def, step=0.05, format="%.4f", key=f"{key_prefix}_h")

    if xf_val <= x0_val:
        st.error("El límite final x_f debe ser estrictamente mayor que x₀.")
        st.stop()

    n_pasos = int(round((xf_val - x0_val) / h_val))
    if n_pasos < 1:
        st.error("El paso h es mayor que la longitud del intervalo [x₀, x_f]. Reduzca h.")
        st.stop()

    h_efectivo = (xf_val - x0_val) / n_pasos
    if abs(h_efectivo - h_val) > 1e-6:
        st.caption(f"ℹ️ Se ajustó ligeramente $h = {h_efectivo:.6f}$ para cubrir exactamente $n = {n_pasos}$ pasos entre $x_0={x0_val}$ y $x_f={xf_val}$.")
        h_val = h_efectivo

    try:
        f_callable = crear_funcion_desde_expresion(expr_str)
        _ = f_callable(x0_val, y0_val)
        f_sym_disp = sp.sympify(expr_str)
    except Exception as e:
        st.error(f"Error al interpretar f(x, y): {e}")
        st.stop()

    sol_latex, fn_exacta, tiene_exacta_simbolica = resolver_pvi_simbolico(expr_str, x0_val, y0_val)

    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.markdown("**Problema de Valor Inicial Planteado:**")
        st.latex(
            rf"\begin{{cases}} \dfrac{{dy}}{{dx}} = {sp.latex(f_sym_disp)} \\[6pt] y({x0_val:.4g}) = {y0_val:.4g} \end{{cases}}, \qquad x \in [{x0_val:.4g}, \; {xf_val:.4g}], \quad h = {h_val:.4g} \; ({n_pasos}\text{{ pasos}})"
        )
    with col_eq2:
        if tiene_exacta_simbolica:
            st.markdown("**Solución Analítica Exacta (obtenida con `sympy.dsolve`):**")
            st.latex(rf"y(x) = {sol_latex}")
        else:
            st.markdown("**Referencia de Alta Precisión:**")
            st.warning("La EDO no posee primitiva simbólica elemental cerrada en `sympy.dsolve`. Se utiliza RK4 con malla ultrafina ($h/50$) como curva exacta de referencia.")

    st.info(contexto)

    x_grid = [x0_val + i * h_val for i in range(n_pasos + 1)]
    x_dense = np.linspace(x0_val, xf_val, 300)
    if tiene_exacta_simbolica:
        y_exacta_nodos = [fn_exacta(xv) for xv in x_grid]
        y_exacta_dense = [fn_exacta(xv) for xv in x_dense]
    else:
        y_exacta_nodos = referencia_numerica_alta_precision(f_callable, x0_val, y0_val, x_grid, subpasos=50)
        y_exacta_dense = referencia_numerica_alta_precision(f_callable, x0_val, y0_val, x_dense, subpasos=10)

    return {
        "f_callable": f_callable,
        "x0_val": x0_val,
        "y0_val": y0_val,
        "xf_val": xf_val,
        "h_val": h_val,
        "n_pasos": n_pasos,
        "x_grid": x_grid,
        "x_dense": x_dense,
        "y_exacta_nodos": y_exacta_nodos,
        "y_exacta_dense": y_exacta_dense,
        "fn_exacta": fn_exacta,
        "tiene_exacta_simbolica": tiene_exacta_simbolica,
    }


# ==============================================================================
# VISTAS INDIVIDUALES POR MÉTODO (1 CLIC)
# ==============================================================================

def vista_euler():
    st.header("📐 Método de Euler y Euler Modificado (Heun)")
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        st.markdown("**Método de Euler Explícito — Orden $O(h)$:**")
        st.latex(r"y_{n+1} = y_n + h \cdot f(x_n, y_n)")
        st.write(
            "Avanza a lo largo de la **recta tangente inicial** del subintervalo. "
            "Cuando la solución tiene concavidad pronunciada, se desvía sistemáticamente en cada paso."
        )
    with c_t2:
        st.markdown("**Método de Euler Modificado (Heun) — Orden $O(h^2)$:**")
        st.latex(r"y_{n+1}^* = y_n + h f(x_n, y_n), \quad y_{n+1} = y_n + \frac{h}{2}\Big[f(x_n, y_n) + f(x_{n+1}, y_{n+1}^*)\Big]")
        st.write(
            "Predice un punto auxiliar con Euler y luego **promedia la pendiente inicial y la pendiente al final del paso**, "
            "reduciendo drásticamente el error de truncamiento."
        )

    datos = _ui_entrada_pvi_lab7("euler")
    f_callable = datos["f_callable"]
    x0_val, y0_val, h_val, n_pasos = datos["x0_val"], datos["y0_val"], datos["h_val"], datos["n_pasos"]
    x_grid, x_dense = datos["x_grid"], datos["x_dense"]
    y_exacta_nodos, y_exacta_dense = datos["y_exacta_nodos"], datos["y_exacta_dense"]

    _, y_euler, _, t_euler = euler_detallado_history(f_callable, x0_val, y0_val, h_val, n_pasos)
    t0 = time.perf_counter()
    _, y_emod = metodo_euler_modificado(f_callable, x0_val, y0_val, h_val, n_pasos)
    t_emod = time.perf_counter() - t0

    err_euler = [abs(ye - yex) for ye, yex in zip(y_euler, y_exacta_nodos)]
    err_emod = [abs(yem - yex) for yem, yex in zip(y_emod, y_exacta_nodos)]

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Valor Exacto en x_f", f"{y_exacta_nodos[-1]:.7f}", f"x_f = {x_grid[-1]:.4f}")
    m2.metric("Euler Explícito en x_f", f"{y_euler[-1]:.7f}", f"Error final: {err_euler[-1]:.3e}")
    m3.metric("Euler Modificado en x_f", f"{y_emod[-1]:.7f}", f"Error final: {err_emod[-1]:.3e}")

    st.subheader("2. Comparación Gráfica: Euler vs. Euler Modificado vs. Solución Exacta")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_dense, y=y_exacta_dense, mode="lines", name="Solución Exacta y(x)", line=dict(color="#00CC96", width=3.5)))
    fig.add_trace(go.Scatter(
        x=x_grid, y=y_euler, mode="lines+markers",
        name="Euler Explícito O(h)",
        line=dict(color="#EF553B", width=2.2, dash="dot"),
        marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=x_grid, y=y_emod, mode="lines+markers",
        name="Euler Modificado (Heun) O(h²)",
        line=dict(color="#FFA15A", width=2.5, dash="dash"),
        marker=dict(size=8, symbol="diamond"),
    ))
    fig.update_layout(title="Trayectorias: Euler Explícito vs. Euler Modificado", xaxis_title="x", yaxis_title="y(x)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("3. Tabla Paso a Paso (Pendientes, Predicción y Error)")
    filas = []
    for i in range(len(x_grid)):
        pend_ini = f_callable(x_grid[i], y_euler[i])
        dif_e_em, _ = calcular_error_local(y_euler[i], y_emod[i])
        filas.append({
            "Paso i": i,
            "x_i": x_grid[i],
            "y_Exacta": y_exacta_nodos[i],
            "y_Euler": y_euler[i],
            "Pendiente Euler f(x_i, y_i)": pend_ini,
            "Error Global Euler": err_euler[i],
            "y_Euler_Modificado": y_emod[i],
            "Error Global Euler Mod.": err_emod[i],
            "Dif. |Euler - EulerMod|": dif_e_em,
        })
    st.dataframe(pd.DataFrame(filas).style.format(precision=7), use_container_width=True)


def vista_runge_kutta():
    st.header("🚀 Método de Runge-Kutta (2° Orden Estándar, Punto Medio y 4° Orden)")
    st.markdown(
        """
        Los **Métodos de Runge-Kutta** alcanzan la precisión de un desarrollo de Taylor de orden superior **sin necesidad de calcular derivadas analíticas** de $f(x, y)$, 
        evaluando estratégicamente la pendiente en puntos intermedios del subintervalo $[x_n, x_{n+1}]$:
        """
    )
    c_rk1, c_rk2, c_rk3 = st.columns(3)
    with c_rk1:
        st.markdown("**RK2 Estándar (Heun) — $O(h^2)$:**")
        st.latex(r"k_1 = h f(x_n, y_n)")
        st.latex(r"k_2 = h f(x_n+h, y_n+k_1)")
        st.latex(r"y_{n+1} = y_n + \frac{k_1 + k_2}{2}")
    with c_rk2:
        st.markdown("**RK2 Punto Medio — $O(h^2)$:**")
        st.latex(r"k_1 = h f(x_n, y_n)")
        st.latex(r"k_2 = h f\!\left(x_n+\frac{h}{2}, y_n+\frac{k_1}{2}\right)")
        st.latex(r"y_{n+1} = y_n + k_2")
    with c_rk3:
        st.markdown("**Runge-Kutta 4 (RK4) — $O(h^4)$:**")
        st.latex(r"k_1 = h f(x_n, y_n), \; k_2 = h f(x_n+\tfrac{h}{2}, y_n+\tfrac{k_1}{2})")
        st.latex(r"k_3 = h f(x_n+\tfrac{h}{2}, y_n+\tfrac{k_2}{2}), \; k_4 = h f(x_n+h, y_n+k_3)")
        st.latex(r"y_{n+1} = y_n + \frac{1}{6}(k_1 + 2k_2 + 2k_3 + k_4)")

    datos = _ui_entrada_pvi_lab7("rk")
    f_callable = datos["f_callable"]
    x0_val, y0_val, h_val, n_pasos = datos["x0_val"], datos["y0_val"], datos["h_val"], datos["n_pasos"]
    x_grid, x_dense = datos["x_grid"], datos["x_dense"]
    y_exacta_nodos, y_exacta_dense = datos["y_exacta_nodos"], datos["y_exacta_dense"]

    _, y_rk2_est, det_rk2_est = metodo_runge_kutta_2(f_callable, x0_val, y0_val, h_val, n_pasos)
    _, y_rk2_pm, det_rk2_pm = metodo_runge_kutta_2_punto_medio(f_callable, x0_val, y0_val, h_val, n_pasos)
    _, y_rk4 = metodo_runge_kutta_4_inicial(f_callable, x0_val, y0_val, h_val, n=n_pasos)

    err_rk2_est = [abs(y - yex) for y, yex in zip(y_rk2_est, y_exacta_nodos)]
    err_rk2_pm = [abs(y - yex) for y, yex in zip(y_rk2_pm, y_exacta_nodos)]
    err_rk4 = [abs(y - yex) for y, yex in zip(y_rk4, y_exacta_nodos)]

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Valor Exacto en x_f", f"{y_exacta_nodos[-1]:.7f}", f"x_f = {x_grid[-1]:.4f}")
    m2.metric("RK2 Estándar en x_f", f"{y_rk2_est[-1]:.7f}", f"Error: {err_rk2_est[-1]:.3e}")
    m3.metric("RK2 Punto Medio en x_f", f"{y_rk2_pm[-1]:.7f}", f"Error: {err_rk2_pm[-1]:.3e}")
    m4.metric("RK4 (4° Orden) en x_f", f"{y_rk4[-1]:.7f}", f"Error: {err_rk4[-1]:.3e}")

    st.subheader("2. Trayectorias de Runge-Kutta vs. Solución Exacta")
    fig_rk = go.Figure()
    fig_rk.add_trace(go.Scatter(x=x_dense, y=y_exacta_dense, mode="lines", name="Solución Exacta y(x)", line=dict(color="#00CC96", width=3.5)))
    fig_rk.add_trace(go.Scatter(x=x_grid, y=y_rk2_est, mode="lines+markers", name="RK2 Estándar O(h²)", line=dict(color="#FFA15A", width=2.2, dash="dash")))
    fig_rk.add_trace(go.Scatter(x=x_grid, y=y_rk2_pm, mode="lines+markers", name="RK2 Punto Medio O(h²)", line=dict(color="#19D3F3", width=2.2, dash="dashdot")))
    fig_rk.add_trace(go.Scatter(x=x_grid, y=y_rk4, mode="lines+markers", name="Runge-Kutta 4 (RK4) O(h⁴)", line=dict(color="#636EFA", width=2.5)))
    fig_rk.update_layout(title="Comparación de Familia Runge-Kutta (RK2 vs. RK4)", xaxis_title="x", yaxis_title="y(x)", hovermode="x unified")
    st.plotly_chart(fig_rk, use_container_width=True)

    st.subheader("3. Tablas Detalladas de Incrementos $k_1, k_2$ y Punto Medio")
    t_est, t_pm, t_rk4 = st.tabs([
        "📋 RK2 Estándar (k₁, k₂)",
        "📋 RK2 Punto Medio (x_m, y_m, k₁, k₂)",
        "📋 Comparativa con RK4 y Errores",
    ])
    with t_est:
        df_rk2_est = pd.DataFrame(det_rk2_est)
        df_rk2_est.columns = ["Paso i", "x_n", "y_n", "k₁ = h·f(x_n, y_n)", "k₂ = h·f(x_n+h, y_n+k₁)", "x_{n+1}", "y_{n+1} = y_n + (k₁+k₂)/2"]
        st.dataframe(df_rk2_est.style.format(precision=7), use_container_width=True)
    with t_pm:
        df_rk2_pm = pd.DataFrame(det_rk2_pm)
        df_rk2_pm.columns = ["Paso i", "x_n", "y_n", "k₁ = h·f(x_n, y_n)", "k₂ = h·f(x_m, y_m)", "x_medio", "y_medio", "x_{n+1}", "y_{n+1} = y_n + k₂"]
        st.dataframe(df_rk2_pm.style.format(precision=7), use_container_width=True)
    with t_rk4:
        df_c_rk = pd.DataFrame({
            "Paso i": list(range(len(x_grid))),
            "x_i": x_grid,
            "y_Exacta": y_exacta_nodos,
            "y_RK2_Estándar": y_rk2_est,
            "y_RK2_PuntoMedio": y_rk2_pm,
            "y_RK4": y_rk4,
            "Error RK2 Est.": err_rk2_est,
            "Error RK2 P.Medio": err_rk2_pm,
            "Error RK4": err_rk4,
        })
        st.dataframe(df_c_rk.style.format(precision=7), use_container_width=True)


def vista_milne():
    st.header("🔮 Método de Milne (Predictor-Corrector Multipaso)")
    st.markdown(
        """
        > 💡 **¿Por qué Milne no puede arrancar solo desde $(x_0, y_0)$?**  
        > A diferencia de Euler o Runge-Kutta (que son **métodos de un paso**), el **Método de Milne** es un **método multipaso de 4 pasos** que necesita conocer 4 puntos iniciales $(y_0, y_1, y_2, y_3)$ para predecir $y_4$:
        """
    )
    st.latex(
        r"\textbf{1. Fase de Arranque (Índices } i = 0, 1, 2, 3\textbf{):} \quad \text{Se calculan } (y_1, y_2, y_3) \text{ usando Runge-Kutta de 4° Orden (RK4).}"
    )
    st.latex(
        r"\textbf{2. Predictor de Milne (Abierto):} \quad y_{n+1}^{(P)} = y_{n-3} + \frac{4h}{3}\Big(2 f_n - f_{n-1} + 2 f_{n-2}\Big)"
    )
    st.latex(
        r"\textbf{3. Corrector de Simpson (Cerrado):} \quad y_{n+1}^{(C)} = y_{n-1} + \frac{h}{3}\Big(f(x_{n+1}, y_{n+1}^{(P)}) + 4 f_n + f_{n-1}\Big)"
    )

    datos = _ui_entrada_pvi_lab7("milne")
    f_callable = datos["f_callable"]
    x0_val, y0_val, h_val, n_pasos = datos["x0_val"], datos["y0_val"], datos["h_val"], datos["n_pasos"]
    x_grid, x_dense = datos["x_grid"], datos["x_dense"]
    y_exacta_nodos, y_exacta_dense = datos["y_exacta_nodos"], datos["y_exacta_dense"]

    if n_pasos < 4:
        st.error(
            rf"🚨 **Cantidad de pasos insuficiente ($n = {n_pasos} < 4$):** "
            "El Método de Milne requiere al menos 4 pasos en el intervalo (los primeros 3 se calculan con RK4 y a partir del 4° paso actúa el Predictor-Corrector). "
            "Disminuya el paso $h$ o aumente $x_f$."
        )
        return

    x_ini_m, y_ini_m = metodo_runge_kutta_4_inicial(f_callable, x0_val, y0_val, h_val, n=3)
    _, y_milne, det_milne = metodo_milne(f_callable, x_ini_m, y_ini_m, h_val, n_pasos - 3)

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Puntos de Arranque (RK4)", "4 nodos (i = 0, 1, 2, 3)", f"x ∈ [{x_grid[0]:.3f}, {x_grid[3]:.3f}]")
    m2.metric("Pasos Predictor-Corrector Milne", f"{len(det_milne)} pasos", f"i = 4 hasta i = {n_pasos}")
    m3.metric("Error Final de Milne en x_f", f"{abs(y_milne[-1] - y_exacta_nodos[-1]):.3e}", f"y_Milne(x_f) = {y_milne[-1]:.7f}")

    st.subheader("2. Trayectoria de Milne: Fase de Arranque RK4 vs. Fase Predictor-Corrector")
    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(x=x_dense, y=y_exacta_dense, mode="lines", name="Solución Exacta y(x)", line=dict(color="#00CC96", width=3.5)))
    fig_m.add_trace(go.Scatter(
        x=x_grid[:4], y=y_milne[:4], mode="lines+markers",
        name="Fase 1: Arranque con RK4 (i = 0, 1, 2, 3)",
        line=dict(color="#636EFA", width=3),
        marker=dict(size=10, symbol="square"),
    ))
    fig_m.add_trace(go.Scatter(
        x=x_grid[3:], y=y_milne[3:], mode="lines+markers",
        name="Fase 2: Predictor-Corrector de Milne (i ≥ 4)",
        line=dict(color="#AB63FA", width=3, dash="dash"),
        marker=dict(size=11, symbol="star"),
    ))
    fig_m.update_layout(
        title="Distinción Visual entre los 4 Nodos de Arranque (RK4) y los Pasos Multipaso de Milne",
        xaxis_title="x",
        yaxis_title="y(x)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_m, use_container_width=True)

    st.subheader("3. Tabla Detallada de Arranque RK4 y Pasos Predictor-Corrector")
    filas_milne = []
    for i in range(4):
        f_val_i = f_callable(x_grid[i], y_milne[i])
        filas_milne.append({
            "Índice (i)": i,
            "x_i": x_grid[i],
            "Etapa / Origen": "🚀 Condición Inicial (i=0)" if i == 0 else "🔹 Arranque con RK4 (Un Paso)",
            "Predictor y_i^(P)": np.nan,
            "f(x_i, y_i^(P))": np.nan,
            "Corrector y_i^(C) Final": y_milne[i],
            "f(x_i, y_i^(C))": f_val_i,
            "Diferencia |y^(C) - y^(P)|": np.nan,
            "Iteraciones Corrector": 0,
            "y_Exacta": y_exacta_nodos[i],
            "Error Global |y_Exacta - y_Milne|": abs(y_exacta_nodos[i] - y_milne[i]),
        })

    for det in det_milne:
        idx_real = det["paso"] + 4
        filas_milne.append({
            "Índice (i)": idx_real,
            "x_i": det["x"],
            "Etapa / Origen": "🔮 Predictor-Corrector de Milne",
            "Predictor y_i^(P)": det["y_predicho"],
            "f(x_i, y_i^(P))": det["f_predicho"],
            "Corrector y_i^(C) Final": det["y_corregido"],
            "f(x_i, y_i^(C))": det["f_corregido"],
            "Diferencia |y^(C) - y^(P)|": det["error_pc"],
            "Iteraciones Corrector": det["iteraciones"],
            "y_Exacta": y_exacta_nodos[idx_real],
            "Error Global |y_Exacta - y_Milne|": abs(y_exacta_nodos[idx_real] - det["y_corregido"]),
        })

    df_milne = pd.DataFrame(filas_milne)
    st.dataframe(df_milne.style.format(precision=8, na_rep="— (Arranque)"), use_container_width=True)

    fig_pc = go.Figure()
    err_pc = [d["error_pc"] for d in det_milne]
    fig_pc.add_trace(go.Bar(
        x=[f"i={d['paso']+4} (x={d['x']:.2f})" for d in det_milne],
        y=err_pc,
        name="Corrección |y^(C) - y^(P)|",
        marker_color="#AB63FA",
    ))
    fig_pc.update_layout(
        title="Magnitud del Ajuste entre Predictor y Corrector |y_{n+1}^(C) - y_{n+1}^(P)| en cada Paso de Milne",
        xaxis_title="Paso Multipaso",
        yaxis_title="|y^(C) - y^(P)|",
        hovermode="x unified",
    )
    st.plotly_chart(fig_pc, use_container_width=True)


def vista_comparativa_lab7():
    st.header("📊 Vista Comparativa: Todos los Métodos de EDO - PVI (Lab 7)")
    st.markdown(
        "Comparación simultánea de **Euler Explícito**, **Euler Modificado (Heun)**, **Runge-Kutta 2 (Punto Medio)**, **Runge-Kutta 4 (RK4)** y **Milne (Predictor-Corrector)**."
    )

    datos = _ui_entrada_pvi_lab7("comp7")
    f_callable = datos["f_callable"]
    x0_val, y0_val, h_val, n_pasos = datos["x0_val"], datos["y0_val"], datos["h_val"], datos["n_pasos"]
    x_grid, x_dense = datos["x_grid"], datos["x_dense"]
    y_exacta_nodos, y_exacta_dense = datos["y_exacta_nodos"], datos["y_exacta_dense"]

    _, y_euler, _, _ = euler_detallado_history(f_callable, x0_val, y0_val, h_val, n_pasos)
    _, y_euler_mod = metodo_euler_modificado(f_callable, x0_val, y0_val, h_val, n_pasos)
    _, y_rk2_pm, _ = metodo_runge_kutta_2_punto_medio(f_callable, x0_val, y0_val, h_val, n_pasos)
    _, y_rk4 = metodo_runge_kutta_4_inicial(f_callable, x0_val, y0_val, h_val, n=n_pasos)

    if n_pasos >= 4:
        x_ini_m, y_ini_m = metodo_runge_kutta_4_inicial(f_callable, x0_val, y0_val, h_val, n=3)
        _, y_milne, _ = metodo_milne(f_callable, x_ini_m, y_ini_m, h_val, n_pasos - 3)
        milne_disponible = True
    else:
        y_milne = [np.nan] * (n_pasos + 1)
        milne_disponible = False

    err_euler_arr = [abs(ye - yex) for ye, yex in zip(y_euler, y_exacta_nodos)]
    err_emod_arr = [abs(yem - yex) for yem, yex in zip(y_euler_mod, y_exacta_nodos)]
    err_rk2pm_arr = [abs(yrk2 - yex) for yrk2, yex in zip(y_rk2_pm, y_exacta_nodos)]
    err_rk4_arr = [abs(yrk4 - yex) for yrk4, yex in zip(y_rk4, y_exacta_nodos)]
    err_milne_arr = [abs(ym - yex) for ym, yex in zip(y_milne, y_exacta_nodos)] if milne_disponible else []

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    mc1.metric("Error Final Euler O(h)", f"{err_euler_arr[-1]:.3e}", f"y(x_f)={y_euler[-1]:.5f}")
    mc2.metric("Error Final Euler Mod O(h²)", f"{err_emod_arr[-1]:.3e}", f"y(x_f)={y_euler_mod[-1]:.5f}")
    mc3.metric("Error Final RK2 P.Medio O(h²)", f"{err_rk2pm_arr[-1]:.3e}", f"y(x_f)={y_rk2_pm[-1]:.5f}")
    mc4.metric("Error Final RK4 O(h⁴)", f"{err_rk4_arr[-1]:.3e}", f"y(x_f)={y_rk4[-1]:.5f}")
    mc5.metric(
        "Error Final Milne O(h⁴)",
        f"{err_milne_arr[-1]:.3e}" if milne_disponible else "Requiere n ≥ 4",
        f"y(x_f)={y_milne[-1]:.5f}" if milne_disponible else "—",
    )

    fig_tray = go.Figure()
    fig_tray.add_trace(go.Scatter(x=x_dense, y=y_exacta_dense, mode="lines", name="Solución Exacta y(x)", line=dict(color="#00CC96", width=3.5)))
    fig_tray.add_trace(go.Scatter(x=x_grid, y=y_euler, mode="lines+markers", name="Euler Explícito O(h)", line=dict(color="#EF553B", width=2, dash="dot")))
    fig_tray.add_trace(go.Scatter(x=x_grid, y=y_euler_mod, mode="lines+markers", name="Euler Modificado O(h²)", line=dict(color="#FFA15A", width=2, dash="dash")))
    fig_tray.add_trace(go.Scatter(x=x_grid, y=y_rk2_pm, mode="lines+markers", name="RK2 Punto Medio O(h²)", line=dict(color="#19D3F3", width=1.8, dash="dashdot")))
    fig_tray.add_trace(go.Scatter(x=x_grid, y=y_rk4, mode="lines+markers", name="Runge-Kutta 4 (RK4) O(h⁴)", line=dict(color="#636EFA", width=2.2)))
    if milne_disponible:
        fig_tray.add_trace(go.Scatter(x=x_grid, y=y_milne, mode="lines+markers", name="Milne Predictor-Corrector O(h⁴)", line=dict(color="#AB63FA", width=2.2, dash="longdash")))
    fig_tray.update_layout(title="Comparación de Trayectorias Numéricas vs. Solución Exacta y(x)", xaxis_title="x", yaxis_title="y(x)", hovermode="x unified")
    st.plotly_chart(fig_tray, use_container_width=True)

    escala_log_err = st.checkbox("Visualizar gráfico de error global en escala logarítmica", value=False, key="comp7_log")
    fig_err_edo = go.Figure()
    fig_err_edo.add_trace(go.Scatter(x=x_grid, y=err_euler_arr, mode="lines+markers", name="Error Euler", line=dict(color="#EF553B", width=2.5)))
    fig_err_edo.add_trace(go.Scatter(x=x_grid, y=err_emod_arr, mode="lines+markers", name="Error Euler Modificado", line=dict(color="#FFA15A", width=2.2)))
    fig_err_edo.add_trace(go.Scatter(x=x_grid, y=err_rk2pm_arr, mode="lines+markers", name="Error RK2 Punto Medio", line=dict(color="#19D3F3", width=2, dash="dash")))
    fig_err_edo.add_trace(go.Scatter(x=x_grid, y=err_rk4_arr, mode="lines+markers", name="Error RK4", line=dict(color="#636EFA", width=2.2)))
    if milne_disponible:
        fig_err_edo.add_trace(go.Scatter(x=x_grid, y=err_milne_arr, mode="lines+markers", name="Error Milne (P-C)", line=dict(color="#AB63FA", width=2.2, dash="dot")))
    fig_err_edo.update_layout(
        title="Acumulación del Error Global |y(x_i) - y_i| a lo largo de x",
        xaxis_title="x",
        yaxis_title="Error Absoluto |y(x_i) - y_i|",
        yaxis_type="log" if escala_log_err else "linear",
        hovermode="x unified",
    )
    st.plotly_chart(fig_err_edo, use_container_width=True)

    st.subheader("3. Tabla Comparativa Paso a Paso")
    filas_comp_edo = []
    for i in range(len(x_grid)):
        filas_comp_edo.append({
            "Paso i": i,
            "x_i": x_grid[i],
            "y_Exacta": y_exacta_nodos[i],
            "y_Euler": y_euler[i],
            "y_EulerMod": y_euler_mod[i],
            "y_RK2 (P.Medio)": y_rk2_pm[i],
            "y_RK4": y_rk4[i],
            "y_Milne": y_milne[i] if milne_disponible else np.nan,
            "Error Euler": err_euler_arr[i],
            "Error EulerMod": err_emod_arr[i],
            "Error RK2": err_rk2pm_arr[i],
            "Error RK4": err_rk4_arr[i],
            "Error Milne": err_milne_arr[i] if milne_disponible else np.nan,
        })
    st.dataframe(pd.DataFrame(filas_comp_edo).style.format(precision=7, na_rep="—"), use_container_width=True)


METODOS_LAB7 = {
    "Método de Euler y Euler Modificado": vista_euler,
    "Método de Runge-Kutta": vista_runge_kutta,
    "Método de Milne (Predictor-Corrector)": vista_milne,
    "📊 Vista Comparativa del Laboratorio": vista_comparativa_lab7,
}


def render_lab7(metodo_seleccionado=None):
    """Renderiza únicamente el método solicitado de Lab 7, o un selector si se ejecuta autónomamente."""
    if metodo_seleccionado is None:
        st.title("🚀 Laboratorio 7: Ecuaciones Diferenciales Ordinarias (PVI)")
        metodo_seleccionado = st.selectbox(
            "Seleccione el método que desea estudiar:",
            list(METODOS_LAB7.keys()),
            key="lab7_standalone_sel",
        )
        st.markdown("---")

    funcion_vista = METODOS_LAB7.get(metodo_seleccionado, vista_comparativa_lab7)
    funcion_vista()


if __name__ == "__main__":
    try:
        st.set_page_config(layout="wide", page_title="Lab 7: Ecuaciones Diferenciales Ordinarias (PVI)")
    except Exception:
        pass
    render_lab7()
