# streamlit run "lab_2/dashboard_lab2.py"
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

LAB2_DIR = Path(__file__).resolve().parent
if str(LAB2_DIR) not in sys.path:
    sys.path.insert(0, str(LAB2_DIR))

from ejer_1 import calcular_errores
from ejer_2 import fl_round, format_norm
from ejer_3 import fl_trunc
from ejer_5 import round3, trunc3


# --- FUNCIONES AUXILIARES DE ARITMÉTICA DE PUNTO FLOTANTE DE k DÍGITOS ---

def format_norm_trunc(val: float, k: int = 3) -> str:
    """Formatea un número en notación punto flotante normalizada truncada a k dígitos."""
    if val == 0:
        return "0." + "0" * k + " x 10^0"
    sign = "-" if val < 0 else ""
    val_abs = abs(val)
    exp = math.floor(math.log10(val_abs)) + 1
    mantissa = val_abs / (10 ** exp)
    mantissa_t = math.floor(mantissa * (10 ** k) + 1e-12) / (10 ** k)
    return f"{sign}{mantissa_t:.{k}f} x 10^{exp}"


def trunc_k(val: float, k: int = 3) -> float:
    """Trunca un número a k cifras significativas."""
    v_fl, _ = fl_trunc(val, k)
    return v_fl


def round_k(val: float, k: int = 3) -> float:
    """Redondea un número a k cifras significativas."""
    v_fl, _ = fl_round(val, k)
    return v_fl


def estimar_cifras_significativas(er: float) -> int:
    """
    Calcula el mayor entero no negativo t para el cual p* aproxima a p
    con t cifras significativas según la definición: E_r <= 0.5 * 10^(1 - t) (o 5 * 10^(-t)).
    """
    if er <= 0:
        return 16
    t = 0
    while er <= 0.5 * (10 ** (1 - (t + 1))) and t < 16:
        t += 1
    return t


# ==============================================================================
# VISTAS INDIVIDUALES POR TEMA / EJERCICIO (ACCESO EN 1 CLIC)
# ==============================================================================

def vista_errores_abs_rel(key_prefix="lab2_err"):
    st.header("📏 Ejercicio 1: Errores Absolutos, Relativos y Cifras Significativas")
    st.markdown(
        """
        En el análisis numérico, si $p$ es el **valor exacto** de una magnitud y $p^*$ es una **aproximación**, se definen:
        """
    )
    st.latex(
        r"\text{Error Absoluto: } E_a = |p - p^*|, \qquad \text{Error Relativo: } E_r = \frac{|p - p^*|}{|p|} \; (p \neq 0), \qquad \text{Error Porcentual: } E_r(\%) = E_r \times 100\%"
    )
    st.info(
        r"💡 **Interpretación Matemática:** El **Error Absoluto ($E_a$)** conserva las unidades de la magnitud pero no indica si la aproximación es buena o mala sin conocer el tamaño de $p$. "
        r"El **Error Relativo ($E_r$)** es adimensional e invariante de escala: se dice que $p^*$ aproxima a $p$ con **$t$ cifras significativas** si $E_r \le 0.5 \times 10^{1-t}$."
    )

    st.subheader("1. Calculadora Interactiva de Errores ($p$ vs. $p^*$)")
    c1, c2 = st.columns(2)
    with c1:
        p_str = st.text_input(
            "Valor Exacto p (admite pi, E, sqrt(2), exp(10), factorial(8) o números):",
            value="pi",
            key=f"{key_prefix}_p",
        )
    with c2:
        p_star_str = st.text_input(
            "Aproximación p* (admite fracciones como 22/7 o decimales):",
            value="22/7",
            key=f"{key_prefix}_pstar",
        )

    try:
        entorno_simb = {"pi": sp.pi, "e": sp.E, "E": sp.E, "sqrt": sp.sqrt, "exp": sp.exp, "factorial": sp.factorial}
        p_val = float(sp.sympify(p_str, locals=entorno_simb).evalf())
        p_star_val = float(sp.sympify(p_star_str, locals=entorno_simb).evalf())
        if abs(p_val) < 1e-15:
            st.error("El valor exacto p debe ser distinto de cero para calcular el error relativo.")
            return
        ea, er, ep, t_ejec = calcular_errores(p_val, p_star_val)
        cifras_sig = estimar_cifras_significativas(er)
    except Exception as e:
        st.error(f"Expresión matemática no válida: {e}")
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Error Absoluto (E_a)", f"{ea:.6e}", f"|{p_val:.6g} - {p_star_val:.6g}|")
    m2.metric("Error Relativo (E_r)", f"{er:.6e}")
    m3.metric("Error Relativo (%)", f"{ep:.5f}%")
    m4.metric("Cifras Significativas (t)", f"{cifras_sig} cifras", "Criterio E_r ≤ 0.5·10^(1-t)")

    st.markdown("---")
    st.subheader("2. Casos de Estudio del Trabajo Práctico (`ejer_1.py`)")
    casos_tp = [
        ("a", "p = π,  p* = 22/7 (Arquímedes)", math.pi, 22.0 / 7.0),
        ("b", "p = π,  p* = 3.1416", math.pi, 3.1416),
        ("c", "p = e,  p* = 2.718", math.e, 2.718),
        ("d", "p = √2, p* = 1.414", math.sqrt(2.0), 1.414),
        ("e", "p = e¹⁰, p* = 22000", math.exp(10.0), 22000.0),
        ("f", "p = 8!, p* = 39900", float(math.factorial(8)), 39900.0),
    ]

    filas_tp = []
    for item, desc, p_c, ps_c in casos_tp:
        ea_c, er_c, ep_c, t_c = calcular_errores(p_c, ps_c)
        filas_tp.append({
            "Ítem": item,
            "Descripción": desc,
            "Valor Exacto (p)": p_c,
            "Aproximación (p*)": ps_c,
            "Error Absoluto (E_a)": ea_c,
            "Error Relativo (E_r)": er_c,
            "Error Porcentual (%)": ep_c,
            "Cifras Significativas": estimar_cifras_significativas(er_c),
        })

    df_tp1 = pd.DataFrame(filas_tp)
    st.dataframe(
        df_tp1.style.format({
            "Valor Exacto (p)": "{:.7g}",
            "Aproximación (p*)": "{:.7g}",
            "Error Absoluto (E_a)": "{:.6e}",
            "Error Relativo (E_r)": "{:.6e}",
            "Error Porcentual (%)": "{:.4f}%",
        }),
        use_container_width=True,
    )

    st.markdown(
        """
        > 🔍 **Observación Pedagógica Clave (Ítems `a` al `d` vs. `e` y `f`):**  
        > Observe que en los ítems **e ($e^{10} \\approx 22000$)** y **f ($8! = 40320 \\approx 39900$)**, los **errores absolutos son enormes** ($E_a \\approx 26.47$ y $E_a = 420$), 
        > pero sus **errores relativos son muy pequeños** ($0.12\\%$ y $1.04\\%$). Esto demuestra por qué en ciencias e ingeniería la calidad de una aproximación se mide con el **error relativo**.
        """
    )


def vista_aritmetica_maquina(key_prefix="lab2_fl"):
    st.header("🖥️ Ejercicios 2 y 3: Aritmética de Máquina — Redondeo vs. Truncamiento")
    st.markdown(
        """
        Una computadora almacena los números reales en **punto flotante decimal normalizado de $k$ dígitos**:
        """
    )
    st.latex(
        r"fl(x) = \pm 0.d_1 d_2 \dots d_k \times 10^n, \qquad d_1 \in \{1, 2, \dots, 9\}, \quad d_i \in \{0, 1, \dots, 9\} \; (i \ge 2)"
    )
    st.markdown(
        r"""
        Al limitar la mantisa a $k$ cifras, existen dos políticas de corte en cada operación aritmética elemental ($x \circledast y = fl(fl(x) * fl(y))$):
        - **Truncamiento (Corte directo):** Se descartan todos los dígitos a partir de la posición $k+1$ ($d_{k+1} d_{k+2} \dots$).
        - **Redondeo Simétrico:** Si $d_{k+1} \ge 5$, se suma $1$ al dígito $d_k$; si $d_{k+1} < 5$, se mantiene $d_k$.
        """
    )

    k_dig = int(st.slider(
        "Seleccione la cantidad de dígitos significativos de mantisa (k) de la máquina:",
        min_value=2,
        max_value=6,
        value=3,
        step=1,
        key=f"{key_prefix}_k",
    ))

    st.subheader(f"1. Comparativa de las Operaciones del Práctico con $k = {k_dig}$ Dígitos (`ejer_2.py` vs. `ejer_3.py`)")

    # Evaluación de los 5 ítems con redondeo y truncamiento a k dígitos
    def evaluar_casos_aritm(fn_fl, k):
        res = []
        # a. 133 + 0.921
        p_a = 133.0 + 0.921
        fl_133, _ = fn_fl(133.0, k)
        fl_0921, _ = fn_fl(0.921, k)
        ps_a, _ = fn_fl(fl_133 + fl_0921, k)
        res.append(("a", "133 + 0.921", p_a, ps_a, f"fl({fl_133:g} + {fl_0921:g})"))

        # b. 133 - 0.499
        p_b = 133.0 - 0.499
        fl_0499, _ = fn_fl(0.499, k)
        ps_b, _ = fn_fl(fl_133 - fl_0499, k)
        res.append(("b", "133 - 0.499", p_b, ps_b, f"fl({fl_133:g} - {fl_0499:g})"))

        # c. (121 - 119) - 0.327
        p_c = (121.0 - 119.0) - 0.327
        fl_121, _ = fn_fl(121.0, k)
        fl_119, _ = fn_fl(119.0, k)
        fl_0327, _ = fn_fl(0.327, k)
        st1_c, _ = fn_fl(fl_121 - fl_119, k)
        ps_c, _ = fn_fl(st1_c - fl_0327, k)
        res.append(("c", "(121 - 119) - 0.327", p_c, ps_c, f"Paso 1: {st1_c:g} → fl({st1_c:g} - {fl_0327:g})"))

        # d. (121 - 0.327) - 119
        p_d = (121.0 - 0.327) - 119.0
        st1_d, _ = fn_fl(fl_121 - fl_0327, k)
        ps_d, _ = fn_fl(st1_d - fl_119, k)
        res.append(("d", "(121 - 0.327) - 119", p_d, ps_d, f"Paso 1: {st1_d:g} → fl({st1_d:g} - {fl_119:g})"))

        # e. (2/9) * (9/7)
        p_e = 2.0 / 7.0
        fl_29, _ = fn_fl(2.0 / 9.0, k)
        fl_97, _ = fn_fl(9.0 / 7.0, k)
        ps_e, _ = fn_fl(fl_29 * fl_97, k)
        res.append(("e", "(2/9) × (9/7)", p_e, ps_e, f"fl({fl_29:g} × {fl_97:g})"))
        return res

    casos_red = evaluar_casos_aritm(fl_round, k_dig)
    casos_trn = evaluar_casos_aritm(fl_trunc, k_dig)

    filas_comp_fl = []
    for (it, op, p_ex, ps_r, paso_r), (_, _, _, ps_t, paso_t) in zip(casos_red, casos_trn):
        ea_r = abs(p_ex - ps_r)
        er_r = (ea_r / abs(p_ex)) * 100.0
        ea_t = abs(p_ex - ps_t)
        er_t = (ea_t / abs(p_ex)) * 100.0
        filas_comp_fl.append({
            "Ítem": it,
            "Operación": op,
            "Valor Exacto (p)": f"{p_ex:.6f}",
            f"Redondeo (k={k_dig}) Normalizado": format_norm(ps_r, k_dig),
            "Error Rel. Redondeo (%)": f"{er_r:.4f}%",
            f"Truncamiento (k={k_dig}) Normalizado": format_norm_trunc(ps_t, k_dig),
            "Error Rel. Truncamiento (%)": f"{er_t:.4f}%",
        })

    st.dataframe(pd.DataFrame(filas_comp_fl), use_container_width=True)

    st.warning(
        r"⚠️ **Pérdida de la Propiedad Asociativa (Comparar Ítems `c` y `d`):**  "
        "\nEn matemática exacta, $(121 - 119) - 0.327 = (121 - 0.327) - 119 = 1.673$. "
        f"Sin embargo, en aritmética de $k={k_dig}$ dígitos:\n"
        f"- Al agrupar **`(121 - 119) - 0.327`** (restando primero los números cercanos), el resultado redondeado es **`{casos_red[2][3]:g}`** (Error = `{abs(1.673 - casos_red[2][3])/1.673*100:.2f}%`).\n"
        f"- Al agrupar **`(121 - 0.327) - 119`**, el número pequeño `0.327` es absorbido al restarse de `121`, arrojando **`{casos_red[3][3]:g}`** en redondeo y **`{casos_trn[3][3]:g}`** en truncamiento (Error de hasta `{abs(1.673 - casos_trn[3][3])/1.673*100:.2f}%`)."
    )

    st.markdown("---")
    st.subheader("2. Laboratorio Interactivo de Punto Flotante Normalizado")
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        val_x = st.number_input("Primer operando x:", value=121.0, format="%.5f", key=f"{key_prefix}_vx")
    with c_s2:
        op_sim = st.selectbox("Operación aritmética:", ["Suma (+)", "Resta (-)", "Multiplicación (×)", "División (÷)"], key=f"{key_prefix}_op")
    with c_s3:
        val_y = st.number_input("Segundo operando y:", value=0.327, format="%.5f", key=f"{key_prefix}_vy")

    if "División" in op_sim and abs(val_y) < 1e-15:
        st.error("No se puede dividir por cero.")
        return

    xr, _ = fl_round(val_x, k_dig)
    yr, _ = fl_round(val_y, k_dig)
    xt, _ = fl_trunc(val_x, k_dig)
    yt, _ = fl_trunc(val_y, k_dig)

    if "+" in op_sim:
        ex_res = val_x + val_y
        res_r, _ = fl_round(xr + yr, k_dig)
        res_t, _ = fl_trunc(xt + yt, k_dig)
    elif "-" in op_sim:
        ex_res = val_x - val_y
        res_r, _ = fl_round(xr - yr, k_dig)
        res_t, _ = fl_trunc(xt - yt, k_dig)
    elif "×" in op_sim:
        ex_res = val_x * val_y
        res_r, _ = fl_round(xr * yr, k_dig)
        res_t, _ = fl_trunc(xt * yt, k_dig)
    else:
        ex_res = val_x / val_y
        res_r, _ = fl_round(xr / yr, k_dig)
        res_t, _ = fl_trunc(xt / yt, k_dig)

    ms1, ms2, ms3 = st.columns(3)
    ms1.metric("Resultado Exacto", f"{ex_res:.7g}", f"Norm: {format_norm(ex_res, 6)}")
    ms2.metric(f"Resultado con Redondeo (k={k_dig})", f"{res_r:.7g}", f"Norm: {format_norm(res_r, k_dig)}")
    ms3.metric(f"Resultado con Truncamiento (k={k_dig})", f"{res_t:.7g}", f"Norm: {format_norm_trunc(res_t, k_dig)}")


def vista_estabilidad_cuadratica(key_prefix="lab2_cuad"):
    st.header("⚠️ Ejercicio 4: Estabilidad Numérica y Cancelación Catastrófica en la Cuadrática")
    st.markdown(
        r"""
        Cuando en la ecuación $ax^2 + bx + c = 0$ se cumple que **$b^2 \gg 4ac$**, resulta $\sqrt{b^2 - 4ac} \approx |b|$. 
        En consecuencia, una de las dos raíces de la fórmula resolvente tradicional resta dos cantidades casi iguales en el numerador, provocando **cancelación catastrófica de cifras significativas**:
        """
    )
    st.latex(
        r"\text{Fórmula Tradicional (Inestable para } x_1 \text{ si } b > 0\text{):} \quad x_1 = \frac{-b + \sqrt{b^2 - 4ac}}{2a}, \qquad x_2 = \frac{-b - \sqrt{b^2 - 4ac}}{2a}"
    )
    st.latex(
        r"\text{Fórmula Racionalizada Alternativa (Evita la resta cuando tienen igual signo):} \quad x_1 = \frac{-2c}{b + \sqrt{b^2 - 4ac}}, \qquad x_2 = \frac{-2c}{b - \sqrt{b^2 - 4ac}}"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        a_c = st.number_input("Coeficiente a:", value=1.0, format="%.4f", key=f"{key_prefix}_a")
    with c2:
        b_c = st.number_input("Coeficiente b (con b² ≫ 4ac):", value=62.10, format="%.4f", key=f"{key_prefix}_b")
    with c3:
        c_c = st.number_input("Coeficiente c:", value=1.0, format="%.4f", key=f"{key_prefix}_c")
    with c4:
        k_c = int(st.slider("Dígitos de máquina (k):", min_value=3, max_value=6, value=4, key=f"{key_prefix}_k"))

    if abs(a_c) < 1e-15 or (b_c ** 2 - 4.0 * a_c * c_c) <= 0:
        st.error("Se requiere a ≠ 0 y discriminante estrictamente positivo (b² - 4ac > 0).")
        return

    # Raíces exactas en doble precisión
    disc_real = b_c ** 2 - 4.0 * a_c * c_c
    # Para máxima exactitud de referencia usamos racionalización en doble precisión
    if b_c >= 0:
        x2_exact = (-b_c - math.sqrt(disc_real)) / (2.0 * a_c)
        x1_exact = (-2.0 * c_c) / (b_c + math.sqrt(disc_real))
    else:
        x1_exact = (-b_c + math.sqrt(disc_real)) / (2.0 * a_c)
        x2_exact = (-2.0 * c_c) / (b_c - math.sqrt(disc_real))

    # Cómputo paso a paso en aritmética de k dígitos (como en ejer_4.py)
    fl_a, _ = fl_round(a_c, k_c)
    fl_b, _ = fl_round(b_c, k_c)
    fl_c, _ = fl_round(c_c, k_c)

    fl_b_sq, _ = fl_round(fl_b ** 2, k_c)
    fl_4ac, _ = fl_round(4.0 * fl_a * fl_c, k_c)
    fl_disc, _ = fl_round(fl_b_sq - fl_4ac, k_c)
    fl_sqrt_disc, _ = fl_round(math.sqrt(fl_disc), k_c)
    fl_2a, _ = fl_round(2.0 * fl_a, k_c)
    fl_neg_2c, _ = fl_round(-2.0 * fl_c, k_c)

    # Tradicional
    num1_trad, _ = fl_round(-fl_b + fl_sqrt_disc, k_c)
    x1_trad, _ = fl_round(num1_trad / fl_2a, k_c)
    num2_trad, _ = fl_round(-fl_b - fl_sqrt_disc, k_c)
    x2_trad, _ = fl_round(num2_trad / fl_2a, k_c)

    # Racionalizada
    den1_rat, _ = fl_round(fl_b + fl_sqrt_disc, k_c)
    x1_rat = fl_round(fl_neg_2c / den1_rat, k_c)[0] if den1_rat != 0 else float("nan")
    den2_rat, _ = fl_round(fl_b - fl_sqrt_disc, k_c)
    x2_rat = fl_round(fl_neg_2c / den2_rat, k_c)[0] if den2_rat != 0 else float("nan")

    st.subheader(f"1. Trazado Paso a Paso de Operaciones en Máquina ($k = {k_c}$ dígitos)")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("**Cálculo del radical $\\sqrt{b^2 - 4ac}$ en máquina:**")
        st.write(
            f"- $fl(b^2) = fl({fl_b}^2) = {fl_b_sq:g}$ (`{format_norm(fl_b_sq, k_c)}`)\n"
            f"- $fl(4ac) = {fl_4ac:g}$ (`{format_norm(fl_4ac, k_c)}`)\n"
            f"- $fl(b^2 - 4ac) = {fl_disc:g}$ (`{format_norm(fl_disc, k_c)}`)\n"
            f"- $fl(\\sqrt{{b^2 - 4ac}}) = {fl_sqrt_disc:g}$ (`{format_norm(fl_sqrt_disc, k_c)}`)"
        )
    with col_p2:
        st.markdown("**¿Dónde ocurre la Cancelación Catastrófica?**")
        st.write(
            f"- En **$x_1$ Tradicional**, el numerador resta: `-{fl_b:g} + {fl_sqrt_disc:g} = {num1_trad:g}` "
            f"(se cancelan los dígitos más significativos y solo queda 1 cifra significativa).\n"
            f"- En **$x_1$ Racionalizada**, el denominador suma: `{fl_b:g} + {fl_sqrt_disc:g} = {den1_rat:g}` "
            f"(conserva las {k_c} cifras significativas intactas)."
        )

    resultados = [
        ("x₁ (Fórmula Tradicional — Con Cancelación)", x1_exact, x1_trad, "⚠️ Inestable: resta -b + √Δ en numerador"),
        ("x₁ (Fórmula Racionalizada — Estable)", x1_exact, x1_rat, "✅ Estable: suma b + √Δ en denominador"),
        ("x₂ (Fórmula Tradicional — Estable)", x2_exact, x2_trad, "✅ Estable: suma -b - √Δ de igual signo"),
        ("x₂ (Fórmula Racionalizada — Con Cancelación)", x2_exact, x2_rat, "⚠️ Inestable: resta b - √Δ en denominador"),
    ]

    filas_res = []
    for nombre, ex, ap, diag in resultados:
        ea = abs(ex - ap)
        er_pct = (ea / abs(ex)) * 100.0
        filas_res.append({
            "Método Evaluado": nombre,
            "Valor Exacto": f"{ex:.8f}",
            f"Aproximación p* (k={k_c})": format_norm(ap, k_c),
            "Valor Decimal p*": f"{ap:.7f}",
            "Error Absoluto (Norm)": format_norm(ea, k_c),
            "Error Relativo (%)": er_pct,
            "Diagnóstico de Estabilidad": diag,
        })

    st.subheader("2. Tabla Comparativa de Errores (`ejer_4.py`)")
    df_c4 = pd.DataFrame(filas_res)
    st.dataframe(df_c4.style.format({"Error Relativo (%)": "{:.4f}%"}), use_container_width=True)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=[r["Método Evaluado"] for r in filas_res],
        y=[r["Error Relativo (%)"] for r in filas_res],
        marker_color=["#EF553B", "#00CC96", "#00CC96", "#EF553B"],
        text=[f"{r['Error Relativo (%)']:.3f}%" for r in filas_res],
        textposition="auto",
    ))
    fig_bar.update_layout(
        title=f"Impacto de la Cancelación Catastrófica en el Error Relativo (%) con k = {k_c} dígitos",
        yaxis_title="Error Relativo (%)",
    )
    st.plotly_chart(fig_bar, use_container_width=True)


def vista_evaluacion_polinomica(key_prefix="lab2_horner"):
    st.header("📉 Ejercicio 5: Evaluación Polinómica — Forma Estándar vs. Forma Anidada (Horner)")
    st.markdown(
        """
        Reorganizar un polinomio mediante la **Forma Anidada de Horner** reduce la cantidad de multiplicaciones necesarias 
        y disminuye drásticamente la **acumulación de errores de redondeo y truncamiento** en aritmética de precisión finita:
        """
    )
    st.latex(
        r"\text{Forma Estándar Directa (5 multiplicaciones): } f(x) = x^3 - 6x^2 + 3x - 0.149"
    )
    st.latex(
        r"\text{Forma Anidada de Horner (2 multiplicaciones): } f(x) = \big((x - 6)x + 3\big)x - 0.149"
    )

    c1, c2 = st.columns(2)
    with c1:
        x_val = st.number_input("Punto de evaluación x (en el práctico x = 4.71):", value=4.71, step=0.01, format="%.4f", key=f"{key_prefix}_x")
    with c2:
        k_h = int(st.slider("Cantidad de cifras significativas (k):", min_value=2, max_value=6, value=3, key=f"{key_prefix}_k"))

    # Cálculo exacto
    x2_ex = x_val ** 2
    x3_ex = x_val ** 3
    t_6x2_ex = 6.0 * x2_ex
    t_3x_ex = 3.0 * x_val
    f_ex = x3_ex - t_6x2_ex + t_3x_ex - 0.149

    # Forma Estándar Truncada a k dígitos
    x2_tr = trunc_k(x_val ** 2, k_h)
    x3_tr = trunc_k(x2_tr * x_val, k_h)
    t_6x2_tr = trunc_k(6.0 * x2_tr, k_h)
    t_3x_tr = trunc_k(3.0 * x_val, k_h)
    f_trad_tr = trunc_k(trunc_k(x3_tr - t_6x2_tr + t_3x_tr, k_h) - 0.149, k_h)

    # Forma Estándar Redondeada a k dígitos
    x2_rd = round_k(x_val ** 2, k_h)
    x3_rd = round_k(x2_rd * x_val, k_h)
    t_6x2_rd = round_k(6.0 * x2_rd, k_h)
    t_3x_rd = round_k(3.0 * x_val, k_h)
    f_trad_rd = round_k(round_k(x3_rd - t_6x2_rd + t_3x_rd, k_h) - 0.149, k_h)

    # Forma Anidada (Horner) Truncada a k dígitos: ((x - 6)x + 3)x - 0.149
    p1_tr = trunc_k(x_val - 6.0, k_h)
    p2_tr = trunc_k(p1_tr * x_val, k_h)
    p3_tr = trunc_k(p2_tr + 3.0, k_h)
    p4_tr = trunc_k(p3_tr * x_val, k_h)
    f_anid_tr = trunc_k(p4_tr - 0.149, k_h)

    # Forma Anidada (Horner) Redondeada a k dígitos
    p1_rd = round_k(x_val - 6.0, k_h)
    p2_rd = round_k(p1_rd * x_val, k_h)
    p3_rd = round_k(p2_rd + 3.0, k_h)
    p4_rd = round_k(p3_rd * x_val, k_h)
    f_anid_rd = round_k(p4_rd - 0.149, k_h)

    st.subheader(f"1. Tabla de Términos de Potencias en la Forma Estándar ($k = {k_h}$ dígitos)")
    df_pot = pd.DataFrame([
        {"Aritmética": "Exacto (Doble Precisión)", "x": x_val, "x²": x2_ex, "x³": x3_ex, "6x²": t_6x2_ex, "3x": t_3x_ex, "f(x) Estándar": f_ex},
        {"Aritmética": f"{k_h} dígitos (Truncamiento)", "x": x_val, "x²": x2_tr, "x³": x3_tr, "6x²": t_6x2_tr, "3x": t_3x_tr, "f(x) Estándar": f_trad_tr},
        {"Aritmética": f"{k_h} dígitos (Redondeo)", "x": x_val, "x²": x2_rd, "x³": x3_rd, "6x²": t_6x2_rd, "3x": t_3x_rd, "f(x) Estándar": f_trad_rd},
    ])
    st.dataframe(df_pot.style.format(precision=6), use_container_width=True)

    st.subheader(f"2. Tabla Paso a Paso de la Forma Anidada de Horner ($k = {k_h}$ dígitos)")
    df_horner = pd.DataFrame([
        {"Aritmética": f"{k_h} dígitos (Truncamiento)", "p₁ = x - 6": p1_tr, "p₂ = p₁·x": p2_tr, "p₃ = p₂ + 3": p3_tr, "p₄ = p₃·x": p4_tr, "f(x) = p₄ - 0.149": f_anid_tr},
        {"Aritmética": f"{k_h} dígitos (Redondeo)", "p₁ = x - 6": p1_rd, "p₂ = p₁·x": p2_rd, "p₃ = p₂ + 3": p3_rd, "p₄ = p₃·x": p4_rd, "f(x) = p₄ - 0.149": f_anid_rd},
    ])
    st.dataframe(df_horner.style.format(precision=6), use_container_width=True)

    st.subheader("3. Comparación Final de Errores Absolutos y Relativos (`ejer_5.py`)")
    comparativa = [
        ("Forma Estándar (Truncado)", f_trad_tr),
        ("Forma Estándar (Redondeado)", f_trad_rd),
        ("Forma Anidada de Horner (Truncado)", f_anid_tr),
        ("Forma Anidada de Horner (Redondeado)", f_anid_rd),
    ]
    filas_f = []
    for nom, p_st in comparativa:
        ea = abs(f_ex - p_st)
        er_pct = (ea / abs(f_ex)) * 100.0 if abs(f_ex) > 1e-15 else 0.0
        filas_f.append({
            "Método / Esquema de Evaluación": nom,
            f"Valor Exacto f({x_val:g})": f_ex,
            "Valor Calculado p*": p_st,
            "Error Absoluto (E_a)": ea,
            "Error Relativo (%)": er_pct,
        })
    df_f = pd.DataFrame(filas_f)
    st.dataframe(
        df_f.style.format({
            f"Valor Exacto f({x_val:g})": "{:.6f}",
            "Valor Calculado p*": "{:.4f}",
            "Error Absoluto (E_a)": "{:.6f}",
            "Error Relativo (%)": "{:.4f}%",
        }),
        use_container_width=True,
    )

    fig_h = go.Figure()
    fig_h.add_trace(go.Bar(
        x=[r["Método / Esquema de Evaluación"] for r in filas_f],
        y=[r["Error Relativo (%)"] for r in filas_f],
        marker_color=["#EF553B", "#FFA15A", "#636EFA", "#00CC96"],
        text=[f"{r['Error Relativo (%)']:.4f}%" for r in filas_f],
        textposition="auto",
    ))
    fig_h.update_layout(
        title=f"Reducción del Error Relativo (%) al Evaluar por Forma Anidada de Horner en x = {x_val:g}",
        yaxis_title="Error Relativo (%)",
    )
    st.plotly_chart(fig_h, use_container_width=True)


def vista_comparativa_lab2():
    st.header("📊 Vista Completa del Laboratorio 2: Teoría de Errores y Estabilidad Numérica")
    t1, t2, t3, t4 = st.tabs([
        "📏 1. Errores Absolutos y Relativos (Ej. 1)",
        "🖥️ 2. Aritmética de Máquina: Redondeo vs. Truncamiento (Ej. 2 y 3)",
        "⚠️ 3. Cancelación Catastrófica en Cuadrática (Ej. 4)",
        "📉 4. Evaluación Polinómica y Método de Horner (Ej. 5)",
    ])
    with t1:
        vista_errores_abs_rel("tab2_err")
    with t2:
        vista_aritmetica_maquina("tab2_fl")
    with t3:
        vista_estabilidad_cuadratica("tab2_cuad")
    with t4:
        vista_evaluacion_polinomica("tab2_horner")


METODOS_LAB2 = {
    "Errores Absolutos y Relativos": vista_errores_abs_rel,
    "Aritmética de Máquina (Redondeo vs. Truncamiento)": vista_aritmetica_maquina,
    "Estabilidad Numérica y Cancelación Catastrófica": vista_estabilidad_cuadratica,
    "Evaluación Polinómica y Forma Anidada (Horner)": vista_evaluacion_polinomica,
    "📊 Vista Comparativa del Laboratorio": vista_comparativa_lab2,
}


def render_lab2(metodo_seleccionado=None):
    """Renderiza el ejercicio seleccionado del Laboratorio 2 o su vista completa por pestañas."""
    if metodo_seleccionado is None:
        st.title("🔬 Laboratorio 2: Errores, Aproximaciones y Estabilidad Numérica")
        vista_comparativa_lab2()
        return

    fn = METODOS_LAB2.get(metodo_seleccionado, vista_comparativa_lab2)
    fn()


if __name__ == "__main__":
    try:
        st.set_page_config(layout="wide", page_title="Lab 2: Errores, Aritmética de Máquina y Estabilidad")
    except Exception:
        pass
    render_lab2()
