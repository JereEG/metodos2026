# streamlit run "lab_4/dashboard_lab4.py"
import contextlib
import io
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

LAB4_DIR = Path(__file__).resolve().parent
if str(LAB4_DIR) not in sys.path:
    sys.path.insert(0, str(LAB4_DIR))

from metodo_eliminacion_gauss import (
    eliminacion_gauss,
    sustitucion_atras,
    verificar_solucion as verificar_solucion_gauss,
)
from metodo_factorisacion_lu import (
    resolver_completo as resolver_lu_completo,
    verificar_factorizacion,
    verificar_solucion as verificar_solucion_lu,
)
from metodo_FadeevLeverrier import calcular_autovectores, metodo_faddeev_leverrier
from metodo_gaus_seidel import es_diagonalmente_dominante
from metodo_gauss_jordan import gauss_jordan
from metodo_potencias import MetodoPotencias as PotenciasClasico
from metodo_potencias_mejorado import MetodoPotencias as PotenciasMejorado


# --- FUNCIONES AUXILIARES Y WRAPPERS (_history) ---

def format_latex(eq_str):
    """Formatea la ecuación ingresada en un string compatible con LaTeX de manera limpia."""
    eq = eq_str.replace("**", "^").replace("*", r"\cdot ")
    eq = re.sub(r"\^(\d{2,})", r"^{\1}", eq)
    return eq


def matrix_to_latex(mat, precision=4):
    """Convierte un arreglo 2D o 1D de NumPy a representación LaTeX bmatrix."""
    arr = np.asarray(mat)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    filas = []
    for fila in arr:
        vals = []
        for v in fila:
            if np.iscomplexobj(v) and abs(v.imag) > 1e-10:
                vals.append(f"{v.real:.{precision}f}{v.imag:+.{precision}f}i")
            else:
                vals.append(f"{float(np.real(v)):.{precision}f}")
        filas.append(" & ".join(vals))
    cuerpo = r" \\ ".join(filas)
    return r"\begin{bmatrix} " + cuerpo + r" \end{bmatrix}"


def augmented_to_latex(A, b, precision=4):
    """Convierte la matriz aumentada [A | b] a representación LaTeX con barra divisoria."""
    A_arr = np.asarray(A, dtype=float)
    b_arr = np.asarray(b, dtype=float).flatten()
    n = A_arr.shape[0]
    col_spec = "r" * n + "|r"
    filas = []
    for i in range(n):
        vals_a = " & ".join(f"{A_arr[i, j]:.{precision}f}" for j in range(n))
        val_b = f"{b_arr[i]:.{precision}f}"
        filas.append(f"{vals_a} & {val_b}")
    cuerpo = r" \\ ".join(filas)
    return r"\left[\begin{array}{" + col_spec + r"} " + cuerpo + r" \end{array}\right]"


def format_characteristic_poly_latex(coef_poly, precision=4):
    """Genera el string en LaTeX del polinomio característico P(lambda)."""
    n = len(coef_poly) - 1
    terminos = []
    for i, c in enumerate(coef_poly):
        potencia = n - i
        if abs(c) < 1e-12 and i > 0:
            continue
        signo = "+" if c >= 0 else "-"
        abs_c = abs(c)

        if i == 0:
            prefijo = "" if abs(abs_c - 1.0) < 1e-10 else f"{c:.{precision}f}"
        else:
            if abs(abs_c - 1.0) < 1e-10 and potencia > 0:
                prefijo = f" {signo} "
            else:
                prefijo = f" {signo} {abs_c:.{precision}f}"

        if potencia == 0:
            terminos.append(f"{prefijo}")
        elif potencia == 1:
            terminos.append(f"{prefijo}\\lambda")
        else:
            terminos.append(f"{prefijo}\\lambda^{{{potencia}}}")

    return "".join(terminos).strip()


def gauss_elimination_history(A, b, decimales=4):
    """Wrapper limpio sobre eliminacion_gauss y sustitucion_atras con control de pivotes nulos."""
    t_ini = time.perf_counter()
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float).reshape(-1, 1)
    matriz_aumentada = np.hstack([A_arr, b_arr])

    if abs(np.linalg.det(A_arr)) < 1e-12:
        return None, False, time.perf_counter() - t_ini, "Matriz singular o casi singular (det(A) ≈ 0)."

    for k in range(len(A_arr)):
        if abs(A_arr[k, k]) < 1e-12:
            return None, False, time.perf_counter() - t_ini, f"Pivote nulo en a_{{{k+1},{k+1}}}. Eliminación de Gauss simple requiere pivoteo."

    pasos = eliminacion_gauss(matriz_aumentada, decimales=decimales)
    matriz_escalonada = pasos[-1]["matriz"]

    for k in range(len(A_arr)):
        if abs(matriz_escalonada[k, k]) < 1e-12:
            return None, False, time.perf_counter() - t_ini, f"Pivote nulo tras escalonamiento en fila {k+1}."

    solucion = sustitucion_atras(matriz_escalonada, decimales=decimales)
    verificacion = verificar_solucion_gauss(matriz_aumentada, solucion, decimales=decimales)
    residuo = float(np.linalg.norm(A_arr @ solucion - b_arr.flatten()))
    t_total = time.perf_counter() - t_ini

    return {
        "pasos": pasos,
        "matriz_escalonada": matriz_escalonada,
        "solucion": solucion,
        "verificacion": verificacion,
        "residuo": residuo,
    }, True, t_total, "Convergencia / Resolución Directa Exitosa"


def gauss_jordan_history(A, b, decimales=4):
    """
    Wrapper paso a paso de Gauss-Jordan respetando la lógica exacta de metodo_gauss_jordan.py
    (pivoteo parcial, normalización y reducción completa), extendido con [A | b | I] para
    obtener también la matriz inversa A^{-1}.
    """
    t_ini = time.perf_counter()
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float).reshape(-1, 1)
    n = A_arr.shape[0]

    matriz_amp_simple = np.hstack([A_arr, b_arr])
    with contextlib.redirect_stdout(io.StringIO()):
        _ = gauss_jordan(matriz_amp_simple)

    M = np.hstack([A_arr.copy(), b_arr.copy(), np.eye(n)])
    pasos = [{
        "paso": 0,
        "titulo": "Matriz Ampliada Inicial [A | b | I]",
        "operaciones": ["Estado inicial antes de reducir por filas."],
        "matriz_ab": M[:, :n + 1].copy(),
        "matriz_inv": M[:, n + 1:].copy(),
    }]

    for i in range(n):
        ops_paso = []
        max_row = i
        for k in range(i + 1, n):
            if abs(M[k, i]) > abs(M[max_row, i]):
                max_row = k

        if max_row != i:
            M[[i, max_row]] = M[[max_row, i]]
            ops_paso.append(f"Pivoteo parcial: Intercambio Fila {i+1} ↔ Fila {max_row+1}")

        pivote = M[i, i]
        if abs(pivote) < 1e-10:
            t_total = time.perf_counter() - t_ini
            return None, False, t_total, f"Matriz singular detectada en columna {i+1} (pivote ≈ 0)."

        M[i, :] = M[i, :] / pivote
        ops_paso.append(f"Normalización: F_{i+1} ← F_{i+1} / ({pivote:.{decimales}f})")

        for k in range(n):
            if k == i:
                continue
            factor = M[k, i]
            if abs(factor) > 1e-10:
                M[k, :] = M[k, :] - factor * M[i, :]
                ops_paso.append(f"Eliminación: F_{k+1} ← F_{k+1} - ({factor:.{decimales}f}) · F_{i+1}")

        pasos.append({
            "paso": i + 1,
            "titulo": f"Reducción de Columna {i+1} (Pivote a_{{{i+1},{i+1}}} = 1)",
            "operaciones": ops_paso,
            "matriz_ab": np.round(M[:, :n + 1].copy(), decimales),
            "matriz_inv": np.round(M[:, n + 1:].copy(), decimales),
        })

    solucion = np.round(M[:, n], decimales)
    inversa = np.round(M[:, n + 1:], decimales)
    residuo = float(np.linalg.norm(A_arr @ solucion - b_arr.flatten()))
    t_total = time.perf_counter() - t_ini

    return {
        "pasos": pasos,
        "solucion": solucion,
        "inversa": inversa,
        "rref": np.round(M[:, :n + 1], decimales),
        "residuo": residuo,
    }, True, t_total, "Reducción RREF Exitosa"


def lu_factorization_history(A, b, decimales=4):
    """Wrapper limpio sobre resolver_completo de metodo_factorisacion_lu.py."""
    t_ini = time.perf_counter()
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float).flatten()

    if abs(np.linalg.det(A_arr)) < 1e-12:
        return None, False, time.perf_counter() - t_ini, "Matriz singular (det(A) ≈ 0)."

    try:
        res = resolver_lu_completo(A_arr, b_arr)
        prod_lu = verificar_factorizacion(res["L"], res["U"])
        Ax, err_residuo = verificar_solucion_lu(A_arr, res["x"], b_arr)
        t_total = time.perf_counter() - t_ini
        res["producto_lu"] = prod_lu
        res["Ax"] = Ax
        res["residuo"] = float(err_residuo)
        res["error_lu"] = float(np.linalg.norm(prod_lu - A_arr))
        return res, True, t_total, "Factorización LU Exitosa"
    except Exception as e:
        return None, False, time.perf_counter() - t_ini, f"Error en Factorización LU: {e}"


def analizar_dominancia_diagonal(A):
    """Evalúa fila por fila la condición suficiente de dominancia diagonal estricta."""
    A_arr = np.array(A, dtype=float)
    n = A_arr.shape[0]
    with contextlib.redirect_stdout(io.StringIO()):
        es_dom_global = bool(es_diagonalmente_dominante(A_arr))
    filas_info = []
    for i in range(n):
        diag = abs(A_arr[i, i])
        suma_otros = sum(abs(A_arr[i, j]) for j in range(n) if j != i)
        cumple = diag > suma_otros
        terminos_str = " + ".join(f"|{A_arr[i, j]:.3f}|" for j in range(n) if j != i)
        filas_info.append({
            "Fila": f"Fila {i+1}",
            "|a_ii| (Diagonal)": diag,
            "Σ |a_ij| (Resto)": suma_otros,
            "Desigualdad": f"|{A_arr[i, i]:.3f}| {' > ' if cumple else ' ≤ '} {terminos_str}",
            "Cumple": "✅ Sí" if cumple else "❌ No",
        })

    try:
        D = np.diag(np.diag(A_arr))
        L_est = np.tril(A_arr, -1)
        U_est = np.triu(A_arr, 1)
        T_gs = -np.linalg.inv(D + L_est) @ U_est
        radio_espectral = float(np.max(np.abs(np.linalg.eigvals(T_gs))))
    except Exception:
        radio_espectral = float("nan")

    return es_dom_global, filas_info, radio_espectral


def gauss_seidel_history(A, b, x0=None, tol=1e-5, max_iter=100):
    """
    Wrapper con historial paso a paso que respeta la lógica algorítmica de metodo_gaus_seidel.py
    sin bloquear por input() de consola cuando la matriz no es diagonalmente dominante.
    """
    t_ini = time.perf_counter()
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float).flatten()
    n = len(b_arr)

    for i in range(n):
        if abs(A_arr[i, i]) < 1e-14:
            return [], False, time.perf_counter() - t_ini, f"Elemento diagonal nulo en a_{{{i+1},{i+1}}}. No se puede despejar x_{i+1}."

    x = np.ones(n, dtype=float) if x0 is None else np.array(x0, dtype=float).flatten()
    history = []

    for k in range(1, max_iter + 1):
        x_ant = x.copy()
        for i in range(n):
            suma = b_arr[i]
            for j in range(n):
                if i != j:
                    suma -= A_arr[i, j] * x[j]
            x[i] = suma / A_arr[i, i]

        if np.any(np.isnan(x)) or np.any(np.isinf(x)) or np.max(np.abs(x)) > 1e12:
            t_total = time.perf_counter() - t_ini
            return history, False, t_total, "Divergencia numérica detectada (valores tienden a infinito)."

        errores_comp = np.abs(x - x_ant)
        err_max = float(np.max(errores_comp))
        residuo = float(np.linalg.norm(A_arr @ x - b_arr))

        fila_hist = {"Iteración (k)": k}
        for i in range(n):
            fila_hist[f"x_{i+1}^(k)"] = float(x[i])
        for i in range(n):
            fila_hist[f"Error x_{i+1}"] = float(errores_comp[i])
        fila_hist["Error Máx ||Δx||_∞"] = err_max
        fila_hist["Residuo ||Ax - b||_2"] = residuo
        history.append(fila_hist)

        if err_max < tol:
            t_total = time.perf_counter() - t_ini
            return history, True, t_total, "Convergencia Exitosa"

    t_total = time.perf_counter() - t_ini
    return history, False, t_total, f"Límite de iteraciones alcanzado ({max_iter})"


def potencias_comparativa_history(A, x0, tol_pct=0.01, max_iter=100, usar_rayleigh_en_mejorado=True):
    """
    Ejecuta el Método de las Potencias Clásico (metodo_potencias.py) y el
    Método de la Potencia Mejorado (metodo_potencias_mejorado.py + Cociente de Rayleigh / x0 personalizado)
    midiendo tiempos e iteraciones lado a lado.
    """
    A_arr = np.array(A, dtype=float)

    t0 = time.perf_counter()
    lam_clas, vec_clas, info_clas = PotenciasClasico.calcular_autovalor_maximo(A_arr, tol_pct, max_iter)
    t_clas = time.perf_counter() - t0

    hist_clas = []
    for item in info_clas:
        fila = {
            "Iteración (k)": item["iteracion"],
            "λ^(k) Estimado": float(item["lambda"]),
            "Error Relativo (%)": float(item["error"]) if item["error"] is not None else None,
        }
        for idx, val in enumerate(item["x_normalizado"]):
            fila[f"v_{idx+1}^(k)"] = float(val)
        hist_clas.append(fila)

    conv_clas = len(hist_clas) > 1 and hist_clas[-1]["Error Relativo (%)"] is not None and hist_clas[-1]["Error Relativo (%)"] < tol_pct

    t1 = time.perf_counter()
    lam_mej_base, vec_mej_base, info_mej_base = PotenciasMejorado.calcular_autovalor_maximo(
        A_arr, np.array(x0, dtype=float), tol_pct, max_iter
    )

    if not usar_rayleigh_en_mejorado:
        t_mej = time.perf_counter() - t1
        hist_mej = []
        for item in info_mej_base:
            fila = {
                "Iteración (k)": item["iteracion"],
                "λ^(k) Estimado": float(item["lambda"]),
                "Error Relativo (%)": float(item["error"]) if item["error"] is not None else None,
            }
            for idx, val in enumerate(item["x_normalizado"]):
                fila[f"v_{idx+1}^(k)"] = float(val)
            hist_mej.append(fila)
        lam_mej, vec_mej = float(lam_mej_base), vec_mej_base
    else:
        x = np.array(x0, dtype=float).copy()
        lam_old = 0.0
        hist_mej = []
        for k in range(max_iter):
            y = np.dot(A_arr, x)
            idx_max = int(np.argmax(np.abs(y)))
            escala = y[idx_max]
            if abs(escala) < 1e-14:
                hist_mej.append({
                    "Iteración (k)": k + 1,
                    "λ^(k) Estimado": 0.0,
                    "Error Relativo (%)": 0.0,
                })
                lam_mej, vec_mej = 0.0, x
                break

            x_norm = y / escala
            num_rayleigh = float(np.dot(x_norm, np.dot(A_arr, x_norm)))
            den_rayleigh = float(np.dot(x_norm, x_norm))
            lam_new = num_rayleigh / den_rayleigh if abs(den_rayleigh) > 1e-14 else float(escala)

            err = None
            if k > 0:
                err = 0.0 if abs(lam_new) < 1e-12 else abs(lam_new - lam_old) / abs(lam_new) * 100.0

            fila = {
                "Iteración (k)": k + 1,
                "λ^(k) Estimado": float(lam_new),
                "Norma Inf (y)": float(escala),
                "Error Relativo (%)": float(err) if err is not None else None,
            }
            for idx, val in enumerate(x_norm):
                fila[f"v_{idx+1}^(k)"] = float(val)
            hist_mej.append(fila)

            lam_old = lam_new
            x = x_norm
            if k > 0 and err is not None and err < tol_pct:
                break
        lam_mej, vec_mej = float(lam_old), x
        t_mej = time.perf_counter() - t1

    conv_mej = len(hist_mej) > 1 and hist_mej[-1]["Error Relativo (%)"] is not None and hist_mej[-1]["Error Relativo (%)"] < tol_pct

    return {
        "clasico": {
            "lambda": float(lam_clas),
            "vector": vec_clas,
            "historial": hist_clas,
            "tiempo": t_clas,
            "convergio": conv_clas,
        },
        "mejorado": {
            "lambda": float(lam_mej),
            "vector": vec_mej,
            "historial": hist_mej,
            "tiempo": t_mej,
            "convergio": conv_mej,
        },
    }


# --- COMPONENTES DE ENTRADA Y VISTAS INDIVIDUALES ---

def _render_selector_matriz_sistema(key_prefix, solo_cuadrada=False):
    """Renderiza el selector de casos de estudio y el editor de matriz para Lab 4."""
    st.subheader("1. Selección de Caso de Estudio o Entrada de Matriz")
    caso = st.selectbox(
        "Seleccione una Matriz de Prueba o ingrese una personalizada:",
        [
            "Caso A: Sistema de la Guía de Laboratorio (3×3 Diagonalmente Dominante — Ideal para Gauss-Seidel y Directos)",
            "Caso B: Matriz sin Dominancia Diagonal (Divergencia en Gauss-Seidel vs. Éxito en Métodos Directos)",
            "Caso C: Tensor Simétrico Definido Positivo (3×3 — Ideal para Autovalores y Faddeev-Leverrier)",
            "Caso D: Sistema 4×4 de Redes Eléctricas (Acoplamiento de Mallas)",
            "Personalizado: Editar libremente dimensión y elementos",
        ],
        key=f"sel_caso_{key_prefix}",
    )

    if "Caso A" in caso:
        A_default = np.array([
            [18.72, 8.20, 8.76],
            [6.40, 15.90, 7.18],
            [5.22, 6.40, 14.31],
        ], dtype=float)
        b_default = np.array([121.280, 126.321, 118.522], dtype=float)
        contexto = (
            "📌 **Caso A (Guía Lab 4):** Sistema $3 \\times 3$ con **dominancia diagonal estricta** "
            "($|a_{ii}| > \\sum_{j \\neq i} |a_{ij}|$). Converge rápidamente tanto en métodos directos como iterativos."
        )
    elif "Caso B" in caso:
        A_default = np.array([
            [1.0, 4.0, 2.0],
            [3.0, 1.0, 5.0],
            [2.0, 3.0, 1.0],
        ], dtype=float)
        b_default = np.array([13.0, 20.0, 11.0], dtype=float)
        contexto = (
            "⚠️ **Caso B (Sin Dominancia Diagonal):** Los elementos de mayor magnitud están fuera de la diagonal principal. "
            "Permite observar cómo **Gauss-Seidel diverge**, mientras los **Métodos Directos** hallan la solución exacta $x = [1, 2, 3]^T$."
        )
    elif "Caso C" in caso:
        A_default = np.array([
            [4.0, 1.0, 1.0],
            [1.0, 3.0, 2.0],
            [1.0, 2.0, 5.0],
        ], dtype=float)
        b_default = np.array([6.0, 6.0, 8.0], dtype=float)
        contexto = (
            "🔬 **Caso C (Matriz Simétrica):** Posee autovalores reales bien separados. "
            "Ideal para estudiar el **Método de las Potencias**, **Potencia Mejorado** y el polinomio característico de **Faddeev-Leverrier**."
        )
    elif "Caso D" in caso:
        A_default = np.array([
            [10.0, -1.0, 2.0, 0.0],
            [-1.0, 11.0, -1.0, 3.0],
            [2.0, -1.0, 10.0, -1.0],
            [0.0, 3.0, -1.0, 8.0],
        ], dtype=float)
        b_default = np.array([6.0, 25.0, -11.0, 15.0], dtype=float)
        contexto = "⚡ **Caso D (Sistema 4×4 de Mallas Eléctricas):** Solución exacta $x = [1, 2, -1, 1]^T$."
    else:
        n_custom = st.slider("Dimensión de la matriz (n × n):", min_value=2, max_value=6, value=3, key=f"sl_n_{key_prefix}")
        A_default = np.eye(n_custom) * 5.0 + np.ones((n_custom, n_custom))
        b_default = np.sum(A_default, axis=1)
        contexto = "✏️ **Modo Personalizado:** Haga clic en cualquier celda de la tabla inferior para modificar sus valores."

    st.info(contexto)

    n_dim = A_default.shape[0]
    cols_a = [f"a_{j+1}" for j in range(n_dim)]
    df_init = pd.DataFrame(A_default, columns=cols_a)
    if not solo_cuadrada:
        df_init["b"] = b_default
    df_init.index = [f"Fila {i+1}" for i in range(n_dim)]

    label_ed = "**Edición interactiva de la matriz $A$:**" if solo_cuadrada else "**Edición interactiva de la matriz aumentada $[A \\mid b]$:**"
    st.markdown(label_ed)
    df_editado = st.data_editor(df_init, use_container_width=True, key=f"ed_l4_{key_prefix}_{caso[:6]}_{n_dim}")

    A_mat = df_editado[cols_a].to_numpy(dtype=float)
    b_vec = df_editado["b"].to_numpy(dtype=float) if not solo_cuadrada else b_default

    col_eq, col_diag = st.columns([3, 2])
    with col_eq:
        if solo_cuadrada:
            st.markdown("**Matriz Cuadrada $A$:**")
            st.latex(r"A = " + matrix_to_latex(A_mat, 3))
        else:
            st.markdown("**Sistema Lineal Aumentado $[A \\mid b]$:**")
            st.latex(augmented_to_latex(A_mat, b_vec, 3))

    with col_diag:
        det_val = float(np.linalg.det(A_mat))
        cond_val = float(np.linalg.cond(A_mat)) if abs(det_val) > 1e-14 else float("inf")
        es_dom, filas_dom, rho_gs = analizar_dominancia_diagonal(A_mat)
        m1, m2 = st.columns(2)
        m1.metric("Determinante det(A)", f"{det_val:.4f}")
        m2.metric("N° de Condición κ(A)", f"{cond_val:.2f}" if cond_val < 1e8 else "∞ (Singular)")
        m3, m4 = st.columns(2)
        m3.metric("Dominancia Diagonal", "Sí ✅" if es_dom else "No ⚠️")
        m4.metric("Radio Espectral ρ(T_GS)", f"{rho_gs:.4f}" if not np.isnan(rho_gs) else "N/A")

    if abs(det_val) < 1e-12:
        st.error("🚨 **Matriz Singular Detectada:** $\\det(A) \\approx 0$. El sistema no tiene solución única ni matriz inversa.")

    return A_mat, b_vec, n_dim, es_dom, filas_dom, rho_gs


def vista_eliminacion_gauss(key_prefix="gauss"):
    st.header("📐 Método de Eliminación de Gauss")
    st.markdown(
        """
        > **Fundamento Teórico:**  
        > El método de **Eliminación de Gauss** transforma el sistema original $Ax = b$ en un sistema equivalente con **matriz triangular superior** aplicando operaciones elementales por fila debajo de cada elemento pivote $a_{kk}$:
        """
    )
    st.latex(
        r"F_i \leftarrow F_i - m_{ik} F_k \quad \text{donde} \quad m_{ik} = \frac{a_{ik}^{(k)}}{a_{kk}^{(k)}} \quad (i = k+1, \dots, n)"
    )
    st.markdown("Una vez escalonada la matriz, las incógnitas se despejan desde la última ecuación hacia la primera mediante **sustitución hacia atrás**:")
    st.latex(
        r"x_i = \frac{1}{a_{ii}} \left( b_i - \sum_{j=i+1}^{n} a_{ij} x_j \right)"
    )

    A_mat, b_vec, n_dim, _, _, _ = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=False)
    st.markdown("---")
    st.subheader("2. Evolución Matricial Paso a Paso y Solución")
    dec = st.slider("Decimales de redondeo en cada operación:", 2, 8, 4, key=f"dec_{key_prefix}")

    res_gauss, ok_g, t_g, msg_g = gauss_elimination_history(A_mat, b_vec, decimales=dec)
    if not ok_g:
        st.error(msg_g)
        return

    c1, c2 = st.columns(2)
    c1.success(f"✅ **{msg_g}**")
    c2.info(f"⏱️ **Tiempo de Ejecución:** {t_g:.6f} s  |  **Residuo $\\|Ax - b\\|_2$:** `{res_gauss['residuo']:.3e}`")

    for paso in res_gauss["pasos"]:
        with st.expander(f"Paso {paso['paso']}: {paso['descripcion']}", expanded=True):
            if paso["operaciones"]:
                st.markdown("**Operaciones elementales aplicadas en esta columna:**")
                for op in paso["operaciones"]:
                    st.code(op)
            mat_p = paso["matriz"]
            st.latex(augmented_to_latex(mat_p[:, :-1], mat_p[:, -1], dec))

    st.subheader("3. Resultado por Sustitución hacia Atrás y Verificación")
    st.latex(r"x = " + matrix_to_latex(res_gauss["solucion"], dec))
    df_ver = pd.DataFrame(res_gauss["verificacion"])
    df_ver.columns = ["Ecuación", "Valor Calculado (Ax)_i", "Término Independiente Original b_i"]
    df_ver["Error Absoluto |(Ax)_i - b_i|"] = np.abs(df_ver["Valor Calculado (Ax)_i"] - df_ver["Término Independiente Original b_i"])
    st.dataframe(df_ver.style.format(precision=dec + 2), use_container_width=True)


def vista_gauss_jordan(key_prefix="gj"):
    st.header("📐 Método de Gauss-Jordan (Forma Escalonada Reducida e Inversa)")
    st.markdown(
        """
        > **Fundamento Teórico:**  
        > El método de **Gauss-Jordan** extiende la eliminación de Gauss normalizando cada fila pivote para que su diagonal valga $1$ ($F_i \\leftarrow F_i / a_{ii}$) y anulando los coeficientes **tanto por debajo como por encima** de cada pivote hasta llegar a la matriz identidad $[A \\mid b] \\longrightarrow [I \\mid x]$.  
        > Al adosar la matriz identidad $[A \\mid b \\mid I]$, las mismas operaciones de fila producen simultáneamente la **matriz inversa $A^{-1}$**.
        """
    )
    st.latex(r"\left[ A \;\middle|\; b \;\middle|\; I \right] \;\xrightarrow{\text{Operaciones Elementales de Fila}}\; \left[ I \;\middle|\; x \;\middle|\; A^{-1} \right]")

    A_mat, b_vec, n_dim, _, _, _ = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=False)
    st.markdown("---")
    st.subheader("2. Reducción Paso a Paso hacia la Matriz Identidad (RREF)")
    dec = st.slider("Decimales de redondeo:", 2, 8, 4, key=f"dec_{key_prefix}")

    res_gj, ok_gj, t_gj, msg_gj = gauss_jordan_history(A_mat, b_vec, decimales=dec)
    if not ok_gj:
        st.error(msg_gj)
        return

    c1, c2 = st.columns(2)
    c1.success(f"✅ **{msg_gj}**")
    c2.info(f"⏱️ **Tiempo de Ejecución:** {t_gj:.6f} s  |  **Residuo $\\|Ax - b\\|_2$:** `{res_gj['residuo']:.3e}`")

    for paso in res_gj["pasos"]:
        with st.expander(f"Paso {paso['paso']}: {paso['titulo']}", expanded=(paso["paso"] in (0, len(res_gj["pasos"]) - 1))):
            for op in paso["operaciones"]:
                st.markdown(f"- `{op}`")
            c_ab, c_inv = st.columns(2)
            with c_ab:
                st.markdown("**Sistema $[A \\mid b]$:**")
                mat_ab = paso["matriz_ab"]
                st.latex(augmented_to_latex(mat_ab[:, :-1], mat_ab[:, -1], dec))
            with c_inv:
                st.markdown("**Bloque de Inversa $A^{-1}$:**")
                st.latex(matrix_to_latex(paso["matriz_inv"], dec))

    st.subheader("3. Solución Directa $x$ y Matriz Inversa $A^{-1}$")
    cs1, cs2 = st.columns(2)
    with cs1:
        st.success("**Vector Solución $x$ (sin necesidad de sustitución regresiva):**")
        st.latex(r"x = " + matrix_to_latex(res_gj["solucion"], dec))
    with cs2:
        st.info("**Matriz Inversa $A^{-1}$:**")
        st.latex(r"A^{-1} = " + matrix_to_latex(res_gj["inversa"], dec))


def vista_factorizacion_lu(key_prefix="lu"):
    st.header("📐 Método de Factorización LU")
    st.markdown(
        """
        > **Fundamento Teórico:**  
        > Descompone la matriz de coeficientes como el producto $A = L \\cdot U$, donde $L$ es **triangular inferior unitaria** (con $1$ en la diagonal y los multiplicadores de Gauss $m_{ik}$ debajo de ella) y $U$ es **triangular superior**.  
        > El sistema $L(Ux) = b$ se resuelve en dos etapas triangulares muy rápidas:
        """
    )
    st.latex(r"\text{Etapa 1 (Sustitución hacia adelante): } L \cdot y = b \qquad \Longrightarrow \qquad \text{Etapa 2 (Sustitución hacia atrás): } U \cdot x = y")

    A_mat, b_vec, n_dim, _, _, _ = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=False)
    st.markdown("---")
    st.subheader("2. Descomposición $A = L \\cdot U$ y Resolución en Dos Etapas")
    dec = st.slider("Decimales de visualización:", 2, 8, 4, key=f"dec_{key_prefix}")

    res_lu, ok_lu, t_lu, msg_lu = lu_factorization_history(A_mat, b_vec, decimales=dec)
    if not ok_lu:
        st.error(msg_lu)
        return

    c1, c2 = st.columns(2)
    c1.success(f"✅ **{msg_lu}**")
    c2.info(f"⏱️ **Tiempo de Ejecución:** {t_lu:.6f} s  |  **Residuo $\\|Ax - b\\|_2$:** `{res_lu['residuo']:.3e}`")

    col_l, col_u, col_ver = st.columns(3)
    with col_l:
        st.markdown("**Matriz $L$ (Triangular Inferior Unitaria):**")
        st.latex(r"L = " + matrix_to_latex(res_lu["L"], dec))
    with col_u:
        st.markdown("**Matriz $U$ (Triangular Superior):**")
        st.latex(r"U = " + matrix_to_latex(res_lu["U"], dec))
    with col_ver:
        st.markdown("**Verificación $L \\cdot U = A$:**")
        st.latex(r"L \cdot U = " + matrix_to_latex(res_lu["producto_lu"], dec))
        st.caption(f"Error de factorización $\\|L\\cdot U - A\\|_F = {res_lu['error_lu']:.2e}$")

    c_ly, c_ux = st.columns(2)
    with c_ly:
        st.subheader("Etapa 1: $L \\cdot y = b$ (Sustitución hacia adelante)")
        for p_ad in res_lu["pasos_sustitucion_adelante"]:
            st.code(p_ad["ecuacion"] + f" = {p_ad['resultado']:.{dec}f}")
        st.latex(r"y = " + matrix_to_latex(res_lu["y"], dec))
    with c_ux:
        st.subheader("Etapa 2: $U \\cdot x = y$ (Sustitución hacia atrás)")
        for p_at in reversed(res_lu["pasos_sustitucion_atras"]):
            st.code(p_at["ecuacion"] + f" = {p_at['resultado']:.{dec}f}")
        st.latex(r"x = " + matrix_to_latex(res_lu["x"], dec))


def vista_gauss_seidel(key_prefix="gs"):
    st.header("🔄 Método Iterativo de Gauss-Seidel")
    st.markdown(
        """
        > **Fundamento Teórico:**  
        > El método de **Gauss-Seidel** despeja cada incógnita $x_i$ de la $i$-ésima fila utilizando **inmediatamente** los valores ya actualizados en la misma iteración $k+1$:
        """
    )
    st.latex(
        r"x_i^{(k+1)} = \frac{1}{a_{ii}} \left( b_i - \sum_{j=1}^{i-1} a_{ij} x_j^{(k+1)} - \sum_{j=i+1}^{n} a_{ij} x_j^{(k)} \right)"
    )

    A_mat, b_vec, n_dim, es_dom, filas_dom, rho_gs = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=False)
    st.markdown("---")
    st.subheader("2. Verificación de Condición Suficiente de Convergencia (Dominancia Diagonal)")
    st.dataframe(pd.DataFrame(filas_dom), use_container_width=True)

    if es_dom:
        st.success(
            f"✅ **Condición Suficiente Cumplida:** La matriz $A$ es estrictamente diagonalmente dominante "
            f"($|a_{{ii}}| > \\sum_{{j \\neq i}} |a_{{ij}}|$ en todas las filas). La convergencia está garantizada "
            f"(Radio espectral $\\rho(T_{{GS}}) = {rho_gs:.4f} < 1$)."
        )
    else:
        st.warning(
            f"⚠️ **Alerta Pedagógica — No cumple Dominancia Diagonal Estricta:** Al menos una fila incumple $|a_{{ii}}| > \\sum_{{j \\neq i}} |a_{{ij}}|$. "
            f"El radio espectral es $\\rho(T_{{GS}}) = {rho_gs:.4f}$. "
            + (
                "Como $\\rho(T_{GS}) \\ge 1$, **el método divergirá** salvo que se permuten las filas."
                if rho_gs >= 1.0
                else "Como $\\rho(T_{GS}) < 1$, el método convergerá a pesar de no ser diagonalmente dominante."
            )
        )

    col_gs1, col_gs2, col_gs3 = st.columns(3)
    with col_gs1:
        x0_str = st.text_input("Vector inicial x^(0) (separado por comas):", ", ".join(["1.0"] * n_dim), key=f"x0_{key_prefix}")
    with col_gs2:
        tol_gs = st.number_input("Tolerancia (Cota de Error ||Δx||_∞):", value=1e-4, format="%e", key=f"tol_{key_prefix}")
    with col_gs3:
        max_iter_gs = int(st.number_input("Máximo de iteraciones:", min_value=5, max_value=500, value=50, step=5, key=f"max_{key_prefix}"))

    try:
        x0_gs = [float(v.strip()) for v in x0_str.split(",") if v.strip()]
        if len(x0_gs) != n_dim:
            x0_gs = np.ones(n_dim)
    except ValueError:
        x0_gs = np.ones(n_dim)

    with st.expander("📖 Ver ecuaciones de iteración despejadas para este sistema", expanded=True):
        for i in range(n_dim):
            if abs(A_mat[i, i]) > 1e-14:
                otros = " ".join(
                    f"{'-' if A_mat[i, j] >= 0 else '+'} {abs(A_mat[i, j]):.3f} x_{{{j+1}}}"
                    for j in range(n_dim) if j != i
                )
                st.latex(rf"x_{{{i+1}}}^{{(k+1)}} = \frac{{{b_vec[i]:.3f} {otros}}}{{{A_mat[i, i]:.3f}}}")

    hist_gs, ok_gs, t_gs, msg_gs = gauss_seidel_history(A_mat, b_vec, x0=x0_gs, tol=tol_gs, max_iter=max_iter_gs)

    c_res1, c_res2 = st.columns([2, 1])
    with c_res1:
        if ok_gs:
            st.success(f"**{msg_gs}** en {len(hist_gs)} iteraciones.")
        else:
            st.error(f"**{msg_gs}**")
    with c_res2:
        st.info(f"⏱️ **Tiempo de Cómputo:** {t_gs:.6f} s")

    if hist_gs:
        df_gs = pd.DataFrame(hist_gs)
        st.dataframe(df_gs.style.format(precision=6), use_container_width=True)

        fig_gs = go.Figure()
        fig_gs.add_trace(go.Scatter(
            x=df_gs["Iteración (k)"],
            y=df_gs["Error Máx ||Δx||_∞"],
            mode="lines+markers",
            name="Error ||x^(k) - x^(k-1)||_∞",
            line=dict(color="#00CC96", width=2.5),
            marker=dict(size=7),
        ))
        fig_gs.add_trace(go.Scatter(
            x=df_gs["Iteración (k)"],
            y=df_gs["Residuo ||Ax - b||_2"],
            mode="lines+markers",
            name="Residuo ||Ax^(k) - b||_2",
            line=dict(color="#FFA15A", width=2, dash="dash"),
            marker=dict(size=6, symbol="diamond"),
        ))
        fig_gs.add_hline(y=tol_gs, line_dash="dot", line_color="red", annotation_text=f"Tolerancia ({tol_gs:.1e})")
        fig_gs.update_layout(
            title="Caída del Error y del Residuo por Iteración (Escala Logarítmica)",
            xaxis_title="Iteración (k)",
            yaxis_title="Magnitud del Error (escala log)",
            yaxis_type="log",
            hovermode="x unified",
        )
        st.plotly_chart(fig_gs, use_container_width=True)


def vista_metodo_potencias(key_prefix="pot_clasico", modo="clasico"):
    if modo == "clasico":
        st.header("⚡ Método de las Potencias (Autovalor Dominante y Mínimo)")
        st.markdown(
            """
            > **Fundamento Teórico:**  
            > El **Método de las Potencias** halla el autovalor dominante $\\lambda_1$ (el de mayor valor absoluto $|\\lambda_1| > |\\lambda_2| \\ge \\dots$) partiendo de un vector inicial $x^{(0)} = [1, 1, \\dots, 1]^T$ y multiplicando sucesivamente por $A$:
            """
        )
        st.latex(r"y^{(k)} = A x^{(k-1)}, \qquad \lambda^{(k)} = \|y^{(k)}\|_\infty, \qquad x^{(k)} = \frac{y^{(k)}}{\lambda^{(k)}}")
    else:
        st.header("🚀 Método de la Potencia Mejorado")
        st.markdown(
            """
            > **Fundamento Teórico:**  
            > El **Método de la Potencia Mejorado** (`metodo_potencias_mejorado.py`) perfecciona al método clásico incorporando:  
            > 1. **Elección libre del vector inicial $x^{(0)}$** y protección contra divisiones por cero si converge al núcleo.  
            > 2. **Aceleración por Cociente de Rayleigh**, que estima el autovalor mediante $\\lambda^{(k)} = \\frac{(x^{(k)})^T A x^{(k)}}{(x^{(k)})^T x^{(k)}}$, logrando convergencia cuadrática en matrices simétricas y reduciendo drásticamente el número de iteraciones.
            """
        )
        st.latex(r"\lambda_{\text{Mejorado}}^{(k)} = \frac{(x^{(k)})^T A x^{(k)}}{(x^{(k)})^T x^{(k)}} \quad \text{vs.} \quad \lambda_{\text{Clásico}}^{(k)} = \|A x^{(k-1)}\|_\infty")

    A_mat, _, n_dim, _, _, _ = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=True)
    st.markdown("---")
    st.subheader("2. Configuración y Convergencia Iterativa")

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        x0_pot_str = st.text_input(
            "Vector inicial x^(0):",
            ", ".join(["1.0"] * n_dim),
            disabled=(modo == "clasico"),
            key=f"x0_{key_prefix}",
        )
    with col_p2:
        tol_pot = st.number_input("Tolerancia Error Relativo (%):", min_value=1e-7, max_value=10.0, value=0.01, format="%.5f", key=f"tol_{key_prefix}")
    with col_p3:
        max_iter_pot = int(st.number_input("Máximo de iteraciones:", min_value=5, max_value=500, value=100, step=10, key=f"max_{key_prefix}"))
    with col_p4:
        usar_rayleigh = st.checkbox("Aceleración Cociente de Rayleigh", value=(modo != "clasico"), disabled=(modo == "clasico"), key=f"ray_{key_prefix}")
        calc_inverso = st.checkbox("Calcular Autovalor Mínimo (Potencia Inversa)", value=False, key=f"inv_{key_prefix}")

    try:
        x0_pot = [float(v.strip()) for v in x0_pot_str.split(",") if v.strip()]
        if len(x0_pot) != n_dim or np.allclose(x0_pot, 0):
            x0_pot = np.ones(n_dim)
    except ValueError:
        x0_pot = np.ones(n_dim)

    res_pot = potencias_comparativa_history(A_mat, x0_pot, tol_pct=tol_pot, max_iter=max_iter_pot, usar_rayleigh_en_mejorado=usar_rayleigh)
    datos_clas = res_pot["clasico"]
    datos_mej = res_pot["mejorado"]

    if modo == "clasico":
        st.subheader("Resultados del Método de las Potencias")
        c1, c2 = st.columns(2)
        c1.success(f"**Autovalor Dominante:** $\\lambda_1 \\approx {datos_clas['lambda']:.6f}$ en **{len(datos_clas['historial'])} iteraciones**")
        c2.info(f"⏱️ **Tiempo de Cómputo:** {datos_clas['tiempo']:.6f} s")
        st.markdown("**Autovector dominante normalizado $v_1$:**")
        st.latex(r"v_1 = " + matrix_to_latex(datos_clas["vector"], 5))
        st.dataframe(pd.DataFrame(datos_clas["historial"]).style.format(precision=6), use_container_width=True)
    else:
        st.subheader("Comparativa Lado a Lado: Potencia Mejorado vs. Potencias Clásico")
        c_pm, c_pc = st.columns(2)
        with c_pm:
            st.markdown("#### 🚀 Método de la Potencia Mejorado")
            st.success(f"$\\lambda_1 \\approx {datos_mej['lambda']:.6f}$ en **{len(datos_mej['historial'])} iteraciones**")
            st.info(f"⏱️ **Tiempo:** {datos_mej['tiempo']:.6f} s")
            st.dataframe(pd.DataFrame(datos_mej["historial"]).style.format(precision=6), use_container_width=True)
        with c_pc:
            st.markdown("#### 🔹 Referencia: Potencias Clásico")
            st.warning(f"$\\lambda_1 \\approx {datos_clas['lambda']:.6f}$ en **{len(datos_clas['historial'])} iteraciones**")
            st.info(f"⏱️ **Tiempo:** {datos_clas['tiempo']:.6f} s")
            st.dataframe(pd.DataFrame(datos_clas["historial"]).style.format(precision=6), use_container_width=True)

    # Gráfico de evolución de lambda_1
    fig_pot = go.Figure()
    df_c = pd.DataFrame(datos_clas["historial"])
    df_m = pd.DataFrame(datos_mej["historial"])

    if modo == "clasico":
        fig_pot.add_trace(go.Scatter(
            x=df_c["Iteración (k)"],
            y=df_c["λ^(k) Estimado"],
            mode="lines+markers",
            name="λ^(k) Método de las Potencias",
            line=dict(color="#636EFA", width=2.5),
        ))
    else:
        fig_pot.add_trace(go.Scatter(
            x=df_m["Iteración (k)"],
            y=df_m["λ^(k) Estimado"],
            mode="lines+markers",
            name="λ^(k) Potencia Mejorado",
            line=dict(color="#EF553B", width=2.5),
        ))
        fig_pot.add_trace(go.Scatter(
            x=df_c["Iteración (k)"],
            y=df_c["λ^(k) Estimado"],
            mode="lines+markers",
            name="λ^(k) Potencias Clásico",
            line=dict(color="#636EFA", width=2, dash="dash"),
        ))

    eigs_exactos = np.linalg.eigvals(A_mat)
    lam_dom_exacto = eigs_exactos[np.argmax(np.abs(eigs_exactos))]
    if np.isreal(lam_dom_exacto):
        fig_pot.add_hline(
            y=float(np.real(lam_dom_exacto)),
            line_dash="dot",
            line_color="green",
            annotation_text=f"λ_1 Exacto = {float(np.real(lam_dom_exacto)):.6f}",
        )

    fig_pot.update_layout(
        title="Evolución del Autovalor Dominante Estimado λ₁^(k) por Iteración",
        xaxis_title="Iteración (k)",
        yaxis_title="Estimación de λ₁",
        hovermode="x unified",
    )
    st.plotly_chart(fig_pot, use_container_width=True)

    if calc_inverso:
        st.subheader("🔎 Método de las Potencias Inverso (Autovalor de Menor Módulo $\\lambda_{\\min}$)")
        lam_min, vec_min, iter_min, _ = PotenciasMejorado.calcular_autovalor_minimo(
            A_mat, np.array(x0_pot, dtype=float), tol_pot, max_iter_pot
        )
        if lam_min is None:
            st.error("La matriz es singular ($\\det(A)=0$), no existe $A^{-1}$ para aplicar el Método Inverso.")
        else:
            st.success(f"**Autovalor mínimo estimado:** $\\lambda_{{\\min}} \\approx {lam_min:.6f}$ en {len(iter_min)} iteraciones.")
            df_min = pd.DataFrame([
                {
                    "Iteración (k)": it["iteracion"],
                    "1 / λ^(k) (en A⁻¹)": it["lambda_inv"],
                    "λ_min^(k) Estimado": it["lambda_min"],
                    "Error Relativo (%)": it["error"],
                }
                for it in iter_min
            ])
            st.dataframe(df_min.style.format(precision=6), use_container_width=True)


def vista_faddeev_leverrier(key_prefix="fl"):
    st.header("📜 Método de Faddeev-Leverrier (Polinomio Característico, Autovalores e Inversa)")
    st.markdown(
        """
        > **Fundamento Teórico:**  
        > El **Método de Faddeev-Leverrier** construye el Polinomio Característico $P(\\lambda) = \\det(\\lambda I - A) = \\lambda^n - b_1 \\lambda^{n-1} - b_2 \\lambda^{n-2} - \\dots - b_n$ mediante trazas de matrices auxiliares $B_k$, y obtiene como subproducto algebraico la **matriz inversa $A^{-1}$**:
        """
    )
    st.latex(
        r"B_1 = A, \quad b_1 = \text{tr}(B_1) \qquad ; \qquad B_k = A (B_{k-1} - b_{k-1} I), \quad b_k = \frac{\text{tr}(B_k)}{k} \quad (k = 2, \dots, n)"
    )

    A_mat, _, n_dim, _, _, _ = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=True)
    st.markdown("---")

    with contextlib.redirect_stdout(io.StringIO()):
        res_fl = metodo_faddeev_leverrier(A_mat)
        autovectores_fl = calcular_autovectores(A_mat, res_fl["autovalores"])

    st.subheader("2. Evolución Paso a Paso de las Matrices Intermedias $B_k$ y Coeficientes")
    for idx_k in range(n_dim):
        k_num = idx_k + 1
        Bk_mat = res_fl["B_matrices"][idx_k]
        bk_val = res_fl["b_coeficientes"][idx_k]
        pk_val = res_fl["coeficientes"][k_num]
        with st.expander(
            f"Iteración k = {k_num}:  b_{k_num} = tr(B_{k_num})/{k_num} = {bk_val:.4f}   (Coeficiente en P(λ): p_{k_num} = {pk_val:+.4f})",
            expanded=True,
        ):
            c_b1, c_b2 = st.columns([2, 1])
            with c_b1:
                if k_num == 1:
                    st.latex(r"B_1 = A = " + matrix_to_latex(Bk_mat, 4))
                else:
                    st.latex(rf"B_{{{k_num}}} = A(B_{{{k_num-1}}} - b_{{{k_num-1}}} I) = " + matrix_to_latex(Bk_mat, 4))
            with c_b2:
                st.metric(f"Traza tr(B_{k_num})", f"{np.trace(Bk_mat):.4f}")
                st.metric(f"Coeficiente b_{k_num}", f"{bk_val:.4f}")
                if k_num == n_dim:
                    st.caption("Por el Teorema de Cayley-Hamilton, $B_n - b_n I = 0$.")

    st.subheader("3. Polinomio Característico Resultante $P(\\lambda) = 0$")
    poly_latex = format_characteristic_poly_latex(res_fl["coeficientes"], precision=4)
    st.latex(r"P(\lambda) = \det(\lambda I - A) = " + poly_latex + r" = 0")

    col_eig, col_inv = st.columns(2)
    with col_eig:
        st.markdown("**Raíces del Polinomio Característico (Autovalores $\\lambda_i$ y Autovectores $v_i$):**")
        filas_eigs = []
        for i, ev in enumerate(res_fl["autovalores"]):
            es_real = abs(np.imag(ev)) < 1e-8
            ev_str = f"{np.real(ev):.6f}" if es_real else f"{np.real(ev):.4f} {np.imag(ev):+.4f}i"
            vec_i = autovectores_fl[i]
            if vec_i is not None:
                vec_str = "[" + ", ".join(
                    f"{np.real(c):.4f}" if abs(np.imag(c)) < 1e-8 else f"{np.real(c):.3f}{np.imag(c):+.3f}i"
                    for c in vec_i
                ) + "]"
                err_av = float(np.linalg.norm(A_mat.astype(complex) @ vec_i - ev * vec_i))
            else:
                vec_str = "N/A"
                err_av = float("nan")
            filas_eigs.append({
                "Autovalor": f"λ_{i+1}",
                "Valor": ev_str,
                "Tipo": "Real" if es_real else "Complejo",
                "Autovector Normalizado v_i": vec_str,
                "Residuo ||Av - λv||": f"{err_av:.2e}",
            })
        st.dataframe(pd.DataFrame(filas_eigs), use_container_width=True)

    with col_inv:
        st.markdown("**Matriz Inversa obtenida por Faddeev-Leverrier:**")
        st.latex(r"A^{-1} = \frac{1}{\det(A)} (B_{n-1} - b_{n-1} I), \quad \det(A) = " + f"{res_fl['determinante']:.4f}")
        if res_fl["inversa"] is not None:
            st.latex(r"A^{-1} = " + matrix_to_latex(res_fl["inversa"], 4))
            err_inv = float(np.linalg.norm(A_mat @ res_fl["inversa"] - np.eye(n_dim)))
            st.success(f"Verificación: $\\|A \\cdot A^{{-1}} - I\\|_F = {err_inv:.2e}$")
        else:
            st.error("La matriz es singular ($\\det(A) \\approx 0$), no posee inversa.")

    st.subheader("4. Gráfico del Polinomio Característico $P(\\lambda)$ y sus Raíces Reales")
    reales = [float(np.real(ev)) for ev in res_fl["autovalores"] if abs(np.imag(ev)) < 1e-7]
    if reales:
        min_l, max_l = min(reales), max(reales)
        span = max(abs(max_l - min_l), 2.0)
        l_min_plot, l_max_plot = min_l - 0.35 * span, max_l + 0.35 * span
    else:
        tr_media = np.trace(A_mat) / n_dim
        l_min_plot, l_max_plot = tr_media - 5.0, tr_media + 5.0

    lam_grid = np.linspace(l_min_plot, l_max_plot, 500)
    p_vals = np.polyval(res_fl["coeficientes"], lam_grid)

    fig_fl = go.Figure()
    fig_fl.add_trace(go.Scatter(
        x=lam_grid,
        y=p_vals,
        mode="lines",
        name="P(λ) = det(λI - A)",
        line=dict(color="#AB63FA", width=2.5),
    ))
    fig_fl.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="P(λ) = 0")

    if reales:
        fig_fl.add_trace(go.Scatter(
            x=reales,
            y=[0.0] * len(reales),
            mode="markers+text",
            name="Raíces Reales (Autovalores λ_i)",
            text=[f"λ = {r:.4f}" for r in reales],
            textposition="top center",
            marker=dict(symbol="star", size=13, color="#00CC96", line=dict(width=1.5, color="black")),
        ))

    fig_fl.update_layout(
        title="Polinomio Característico P(λ) e Intersecciones con el Eje Horizontal (Autovalores)",
        xaxis_title="λ",
        yaxis_title="P(λ)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_fl, use_container_width=True)


def vista_comparativa_lab4(key_prefix="comp_l4"):
    st.header("📊 Vista Comparativa Integral — Laboratorio 4 (Sistemas Lineales y Autovalores)")
    A_mat, b_vec, n_dim, es_dom, filas_dom, rho_gs = _render_selector_matriz_sistema(key_prefix, solo_cuadrada=False)
    st.markdown("---")

    dec_directos = st.slider("Precisión de redondeo (decimales) para métodos directos:", 2, 8, 4, key=f"dec_{key_prefix}")
    res_gauss, ok_g, t_g, msg_g = gauss_elimination_history(A_mat, b_vec, decimales=dec_directos)
    res_gj, ok_gj, t_gj, msg_gj = gauss_jordan_history(A_mat, b_vec, decimales=dec_directos)
    res_lu, ok_lu, t_lu, msg_lu = lu_factorization_history(A_mat, b_vec, decimales=dec_directos)
    hist_gs, ok_gs, t_gs, msg_gs = gauss_seidel_history(A_mat, b_vec, tol=1e-4, max_iter=50)

    st.subheader("Resumen Comparativo de Resolución del Sistema $Ax = b$")
    filas_comp = []
    for nombre_m, tipo_m, ok_m, sol_m, res_m, t_m, msg_m in [
        ("Eliminación de Gauss", "Directo", ok_g, res_gauss["solucion"] if ok_g else None, res_gauss["residuo"] if ok_g else None, t_g, msg_g),
        ("Gauss-Jordan (RREF)", "Directo", ok_gj, res_gj["solucion"] if ok_gj else None, res_gj["residuo"] if ok_gj else None, t_gj, msg_gj),
        ("Factorización LU", "Directo", ok_lu, res_lu["x"] if ok_lu else None, res_lu["residuo"] if ok_lu else None, t_lu, msg_lu),
        (
            f"Gauss-Seidel ({len(hist_gs)} iter.)",
            "Iterativo",
            ok_gs,
            [hist_gs[-1][f"x_{i+1}^(k)"] for i in range(n_dim)] if hist_gs else None,
            hist_gs[-1]["Residuo ||Ax - b||_2"] if hist_gs else None,
            t_gs,
            msg_gs,
        ),
    ]:
        fila_d = {
            "Método": nombre_m,
            "Clasificación": tipo_m,
            "Estado": ("✅ " if ok_m else "❌ ") + msg_m,
            "Tiempo (s)": f"{t_m:.6f}",
            "Residuo ||Ax - b||_2": f"{res_m:.3e}" if res_m is not None else "N/A",
        }
        if sol_m is not None:
            for i_x, val_x in enumerate(sol_m):
                fila_d[f"x_{i_x+1}"] = f"{val_x:.{dec_directos}f}"
        filas_comp.append(fila_d)

    st.dataframe(pd.DataFrame(filas_comp), use_container_width=True)


def render_lab4(metodo_seleccionado=None):
    """Punto de entrada modular para renderizar un método aislado o el selector del Lab 4."""
    opciones = [
        "Eliminación de Gauss",
        "Método de Gauss-Jordan",
        "Factorización LU",
        "Método Iterativo de Gauss-Seidel",
        "Método de las Potencias",
        "Método de la Potencia Mejorado",
        "Método de Faddeev-Leverrier",
        "📊 Vista Comparativa del Laboratorio",
    ]
    if metodo_seleccionado is None:
        st.title("🧮 Laboratorio 4: Sistemas de Ecuaciones Lineales y Autovalores")
        metodo_seleccionado = st.Radio(
            "Seleccione el método que desea estudiar:",
            opciones,
            horizontal=True,
        ) if hasattr(st, "Radio") else st.radio(
            "Seleccione el método que desea estudiar:",
            opciones,
            horizontal=True,
        )
        st.markdown("---")

    if metodo_seleccionado == "Eliminación de Gauss":
        vista_eliminacion_gauss("iso_gauss")
    elif metodo_seleccionado == "Método de Gauss-Jordan":
        vista_gauss_jordan("iso_gj")
    elif metodo_seleccionado == "Factorización LU":
        vista_factorizacion_lu("iso_lu")
    elif metodo_seleccionado == "Método Iterativo de Gauss-Seidel":
        vista_gauss_seidel("iso_gs")
    elif metodo_seleccionado == "Método de las Potencias":
        vista_metodo_potencias("iso_pot_c", modo="clasico")
    elif metodo_seleccionado == "Método de la Potencia Mejorado":
        vista_metodo_potencias("iso_pot_m", modo="mejorado")
    elif metodo_seleccionado == "Método de Faddeev-Leverrier":
        vista_faddeev_leverrier("iso_fl")
    else:
        vista_comparativa_lab4("iso_comp4")


if __name__ == "__main__":
    try:
        st.set_page_config(layout="wide", page_title="Lab 4: Sistemas Lineales y Autovalores")
    except Exception:
        pass
    render_lab4(None)
