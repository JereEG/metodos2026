# streamlit run "lab_1/dashboard_lab1.py"
import contextlib
import io
import math
import random
import sys
import time
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

LAB1_DIR = Path(__file__).resolve().parent
if str(LAB1_DIR) not in sys.path:
    sys.path.insert(0, str(LAB1_DIR))


# --- LÓGICA MATEMÁTICA Y ALGORÍTMICA DEL LABORATORIO 1 ---

def sumar_n_positivos(numeros: list[float]) -> tuple[float, float, float]:
    """
    Calcula la suma de una lista de números positivos y mide tiempos de Reloj y CPU.
    Respeta exactamente la lógica del Ejercicio 1 de Laboratorio_1.ipynb.
    """
    t_ini_clock = time.perf_counter()
    t_ini_cpu = time.process_time()

    total = 0.0
    for x in numeros:
        if x <= 0:
            raise ValueError(f"Valor no positivo detectado: {x}")
        total += x

    t_cpu = time.process_time() - t_ini_cpu
    t_clock = time.perf_counter() - t_ini_clock
    return total, t_clock, t_cpu


def sumar_pares(numeros: list[int]) -> tuple[int, int, float, float]:
    """
    Suma únicamente los valores pares de una lista de enteros positivos y mide tiempos.
    Respeta exactamente la lógica del Ejercicio 2 de Laboratorio_1.ipynb.
    """
    t_ini_clock = time.perf_counter()
    t_ini_cpu = time.process_time()

    suma_pares = 0
    cant_pares = 0
    for x in numeros:
        if x % 2 == 0:
            suma_pares += x
            cant_pares += 1

    t_clock = time.perf_counter() - t_ini_clock
    t_cpu = time.process_time() - t_ini_cpu
    return suma_pares, cant_pares, t_clock, t_cpu


def generar_fibonacci(n: int) -> tuple[list[int], float, float]:
    """
    Genera los primeros N números de la sucesión de Fibonacci (0, 1, 1, 2, 3, 5, ...).
    Respeta la lógica del Ejercicio 3 de Laboratorio_1.ipynb.
    """
    t_ini_clock = time.perf_counter()
    t_ini_cpu = time.process_time()

    if n <= 0:
        fib = []
    elif n == 1:
        fib = [0]
    elif n == 2:
        fib = [0, 1]
    else:
        fib = [0, 1]
        for _ in range(2, n):
            fib.append(fib[-1] + fib[-2])

    t_clock = time.perf_counter() - t_ini_clock
    t_cpu = time.process_time() - t_ini_cpu
    return fib, t_clock, t_cpu


def resolver_cuadratica_analitica(a: float, b: float, c: float):
    """
    Resuelve analíticamente ax^2 + bx + c = 0 midiendo el tiempo de ejecución.
    Respeta la lógica del Ejercicio 4 de Laboratorio_1.ipynb.
    """
    if abs(a) < 1e-15:
        return None, None, 0.0, "El coeficiente cuadrático 'a' no puede ser cero."

    t_ini = time.perf_counter()
    disc = b**2 - 4.0 * a * c

    if disc < 0:
        parte_real = -b / (2.0 * a)
        parte_imag = math.sqrt(-disc) / (2.0 * a)
        raices = (complex(parte_real, parte_imag), complex(parte_real, -parte_imag))
        estado = "Raíces Complejas Conjugadas (Δ < 0)"
    elif abs(disc) < 1e-15:
        x_unica = -b / (2.0 * a)
        raices = (x_unica, x_unica)
        estado = "Raíz Real Doble Única (Δ = 0)"
    else:
        x1 = (-b + math.sqrt(disc)) / (2.0 * a)
        x2 = (-b - math.sqrt(disc)) / (2.0 * a)
        raices = (x1, x2)
        estado = "Dos Raíces Reales Distintas (Δ > 0)"

    duracion = time.perf_counter() - t_ini
    return raices, disc, duracion, estado


def calcular_serie_euler_historial(n_max: int, x_val: float = 1.0, precision_dec: int = 50):
    """
    Calcula la aproximación de e^x = sum_{k=0}^{N} x^k / k! paso a paso
    en punto flotante estándar y con alta precisión Decimal (Ejercicio 5 y compl_ejer_2.py).
    """
    getcontext().prec = precision_dec
    t_ini_clock = time.perf_counter()
    t_ini_cpu = time.process_time()

    val_real = math.exp(x_val)
    suma_float = 1.0
    fact_float = 1.0

    suma_dec = Decimal(1)
    fact_dec = Decimal(1)
    x_dec = Decimal(str(x_val))

    filas = [{
        "Término (k)": 0,
        "Expresión": "1 / 0!",
        "Valor del Término": 1.0,
        "Suma Parcial S_k (float)": suma_float,
        "Valor Exacto": val_real,
        "Error Absoluto |e^x - S_k|": abs(val_real - suma_float),
        "Error Relativo (%)": abs(val_real - suma_float) / abs(val_real) * 100.0 if val_real != 0 else 0.0,
    }]

    for k in range(1, n_max + 1):
        fact_float *= k
        termino_f = (x_val ** k) / fact_float
        suma_float += termino_f

        fact_dec *= Decimal(k)
        suma_dec += (x_dec ** k) / fact_dec

        err_abs = abs(val_real - suma_float)
        err_rel = (err_abs / abs(val_real) * 100.0) if val_real != 0 else 0.0
        filas.append({
            "Término (k)": k,
            "Expresión": f"{x_val:g}^{k} / {k}!" if x_val != 1.0 else f"1 / {k}!",
            "Valor del Término": termino_f,
            "Suma Parcial S_k (float)": suma_float,
            "Valor Exacto": val_real,
            "Error Absoluto |e^x - S_k|": err_abs,
            "Error Relativo (%)": err_rel,
        })

    t_clock = time.perf_counter() - t_ini_clock
    t_cpu = time.process_time() - t_ini_cpu
    return filas, suma_float, str(suma_dec), t_clock, t_cpu


def calcular_pi_leibniz_por_tolerancia(decimales: int, max_iter_seguridad: int = 500000):
    """
    Calcula Pi mediante la serie de Gregory-Leibniz 4 * sum (-1)^k / (2k+1)
    hasta cumplir el criterio de Scarborough: tol = 0.5 * 10^(-decimales) (Ejercicio 6).
    """
    tol = 0.5 * (10 ** (-decimales))
    pi_ref = math.pi

    pi_aprox = 0.0
    signo = 1.0
    k = 0
    error = 1.0

    t_ini_clock = time.perf_counter()
    t_ini_cpu = time.process_time()

    while error >= tol and k < max_iter_seguridad:
        termino = signo * (4.0 / (2 * k + 1))
        pi_aprox += termino
        signo = -signo
        k += 1
        error = abs(pi_ref - pi_aprox)

    t_clock = time.perf_counter() - t_ini_clock
    t_cpu = time.process_time() - t_ini_cpu
    return k, pi_aprox, tol, error, t_clock, t_cpu


def calcular_pi_leibniz_historial(n_terminos: int):
    """Genera la evolución término a término de la serie de Gregory-Leibniz para graficar convergencia."""
    pi_ref = math.pi
    pi_aprox = 0.0
    signo = 1.0
    historial = []
    paso_muestreo = max(1, n_terminos // 200)

    t_ini = time.perf_counter()
    for k in range(n_terminos):
        termino = signo * (4.0 / (2 * k + 1))
        pi_aprox += termino
        signo = -signo
        err = abs(pi_ref - pi_aprox)
        if k < 25 or (k + 1) % paso_muestreo == 0 or k == n_terminos - 1:
            historial.append({
                "Término (k+1)": k + 1,
                "Fracción agregada": f"{'+' if k % 2 == 0 else '-'} 4/{2*k + 1}",
                "Término numérico": termino,
                "π Aproximado (S_k)": pi_aprox,
                "π Exacto": pi_ref,
                "Error Absoluto |π - S_k|": err,
                "Error Relativo (%)": (err / pi_ref) * 100.0,
            })
    t_clock = time.perf_counter() - t_ini
    return historial, pi_aprox, abs(pi_ref - pi_aprox), t_clock


# ==============================================================================
# VISTAS INDIVIDUALES POR EJERCICIO / TEMA (ACCESO EN 1 CLIC)
# ==============================================================================

def vista_sumas_rendimiento(key_prefix="lab1_sumas"):
    st.header("🧮 Ejercicios 1 y 2: Suma de $N$ Números Positivos y Suma de Pares")
    st.markdown(
        """
        Estudio de **Algoritmos Directos e Iterativos** de acumulación numérica y medición experimental del **Tiempo de Reloj** (*Wall-Clock Time*) 
        frente al **Tiempo de Procesador (CPU)** en función del volumen de datos $N$.
        """
    )

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Modelo Matemático — Ejercicio 1 (Suma de $N$ reales positivos):**")
        st.latex(r"S = \sum_{i=1}^{N} X_i \quad \text{con } X_i > 0, \; \forall i \in \{1, 2, \dots, N\}")
        st.caption("Clasificación: **Algoritmo Directo** — alcanza el resultado en un número finito y predeterminado de $N$ sumas.")
    with col_t2:
        st.markdown("**Modelo Matemático — Ejercicio 2 (Suma de pares sobre $N=200$ enteros):**")
        st.latex(r"S_{\text{pares}} = \sum_{i=1}^{200} f(X_i), \quad f(X_i) = \begin{cases} X_i & \text{si } X_i \bmod 2 = 0 \\ 0 & \text{si } X_i \bmod 2 \neq 0 \end{cases}")
        st.caption("Clasificación: **Algoritmo Directo con selección condicional** de paridad.")

    st.markdown("---")

    modalidad_ej = st.radio(
        "Seleccione el experimento del práctico que desea ejecutar:",
        [
            "🔹 Ejercicio 1: Suma de N números reales positivos (Rango corto [1 - 255] vs. Rango amplio hasta 10.000)",
            "🔸 Ejercicio 2: Suma de números pares sobre un conjunto de N = 200 enteros positivos",
        ],
        key=f"{key_prefix}_mod",
    )

    if "Ejercicio 1" in modalidad_ej:
        c1, c2, c3 = st.columns(3)
        with c1:
            rango_tipo = st.selectbox(
                "Rango de prueba para N:",
                ["Rango Corto [1 - 255]", "Rango Amplio [1 - 10.000]"],
                key=f"{key_prefix}_rango",
            )
        with c2:
            limite_max = 255 if "Corto" in rango_tipo else 10000
            val_def = 50 if "Corto" in rango_tipo else 10000
            n_val = int(st.number_input(
                f"Cantidad de números a sumar N (1 a {limite_max}):",
                min_value=1,
                max_value=limite_max,
                value=val_def,
                step=10 if limite_max == 255 else 500,
                key=f"{key_prefix}_n",
            ))
        with c3:
            modo_carga = st.selectbox(
                "Modo de carga de los datos X_i:",
                ["Generador Aleatorio Automático (0.10 a 100.00)", "Ingreso / Edición Manual de Números"],
                key=f"{key_prefix}_carga",
            )

        if "Aleatorio" in modo_carga:
            semilla = int(st.number_input("Semilla aleatoria (para reproducibilidad):", value=42, step=1, key=f"{key_prefix}_seed"))
            rng = random.Random(semilla)
            numeros = [round(rng.uniform(0.1, 100.0), 4) for _ in range(n_val)]
        else:
            st.info("✏️ Ingrese los números positivos separados por coma (o edite los valores de ejemplo):")
            ejemplo_str = ", ".join([str(round(i * 1.5, 2)) for i in range(1, min(n_val, 25) + 1)])
            texto_manual = st.text_area("Listado de números positivos (X_i > 0):", value=ejemplo_str, key=f"{key_prefix}_txt")
            try:
                numeros = [float(x.strip()) for x in texto_manual.split(",") if x.strip()]
                if not numeros or any(x <= 0 for x in numeros):
                    st.error("Todos los números ingresados deben ser estrictamente positivos (X_i > 0).")
                    return
                n_val = len(numeros)
            except ValueError:
                st.error("Formato inválido. Ingrese valores numéricos separados por coma.")
                return

        total_suma, t_clock, t_cpu = sumar_n_positivos(numeros)

        # Comparativa automática N corto vs N = 10.000
        rng_bench = random.Random(42)
        datos_255 = [round(rng_bench.uniform(0.1, 100.0), 4) for _ in range(255)]
        datos_10k = [round(rng_bench.uniform(0.1, 100.0), 4) for _ in range(10000)]
        _, t_clock_255, t_cpu_255 = sumar_n_positivos(datos_255)
        _, t_clock_10k, t_cpu_10k = sumar_n_positivos(datos_10k)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Elementos Sumados (N)", f"{n_val:,}")
        m2.metric("Suma Total S", f"{total_suma:,.4f}")
        m3.metric("Tiempo de Reloj (Wall-Clock)", f"{t_clock * 1e6:.2f} µs", f"{t_clock:.8f} s")
        m4.metric("Tiempo de CPU", f"{t_cpu * 1e6:.2f} µs", f"{t_cpu:.8f} s")

        st.subheader("Comparación de Tiempos de Cómputo según el Tamaño de Entrada $N$")
        df_tiempos = pd.DataFrame([
            {"Experimento": f"Selección Actual (N = {n_val})", "N": n_val, "Tiempo Reloj (µs)": t_clock * 1e6, "Tiempo Reloj (s)": f"{t_clock:.8f}"},
            {"Experimento": "Tope Rango Corto (N = 255)", "N": 255, "Tiempo Reloj (µs)": t_clock_255 * 1e6, "Tiempo Reloj (s)": f"{t_clock_255:.8f}"},
            {"Experimento": "Tope Rango Amplio (N = 10.000)", "N": 10000, "Tiempo Reloj (µs)": t_clock_10k * 1e6, "Tiempo Reloj (s)": f"{t_clock_10k:.8f}"},
        ])
        st.dataframe(df_tiempos, use_container_width=True)

        with st.expander(f"📋 Inspeccionar muestra de los sumandos generados (mostrando primeros {min(100, len(numeros))} de {len(numeros)})"):
            df_muestra = pd.DataFrame({
                "Índice i": list(range(1, min(100, len(numeros)) + 1)),
                "Valor X_i": numeros[:100],
                "Suma Acumulada Parcial": np.cumsum(numeros[:100]),
            })
            st.dataframe(df_muestra.style.format({"Valor X_i": "{:.4f}", "Suma Acumulada Parcial": "{:,.4f}"}), use_container_width=True)

    else:
        c1, c2 = st.columns(2)
        with c1:
            n_pares_total = int(st.number_input("Cantidad total de números enteros a evaluar (N):", min_value=10, max_value=1000, value=200, step=10, key=f"{key_prefix}_np"))
        with c2:
            semilla_p = int(st.number_input("Semilla del generador de enteros [1, 500]:", value=42, step=1, key=f"{key_prefix}_seedp"))

        rng_p = random.Random(semilla_p)
        numeros_ent = [rng_p.randint(1, 500) for _ in range(n_pares_total)]
        suma_p, cant_p, t_clock_p, t_cpu_p = sumar_pares(numeros_ent)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Datos Evaluados (N)", f"{n_pares_total}")
        m2.metric("Cantidad de Números Pares", f"{cant_p} pares", f"{cant_pares_pct := (cant_p / n_pares_total * 100):.1f}% del total")
        m3.metric("Suma Total de Pares", f"{suma_p:,}")
        m4.metric("Tiempo de Reloj", f"{t_clock_p * 1e6:.2f} µs", f"{t_clock_p:.8f} s")

        df_pares = pd.DataFrame({
            "Índice i": list(range(1, len(numeros_ent) + 1)),
            "Valor X_i": numeros_ent,
            "Paridad": ["✅ Par (Se suma)" if x % 2 == 0 else "➖ Impar (Se omite)" for x in numeros_ent],
            "Aporte a la Suma": [x if x % 2 == 0 else 0 for x in numeros_ent],
        })
        st.subheader("Tabla de Clasificación de Paridad y Acumulación")
        st.dataframe(df_pares, use_container_width=True)


def vista_fibonacci(key_prefix="lab1_fib"):
    st.header("🌱 Ejercicio 3: Sucesión de Fibonacci ($N = 200$) y Razón Áurea")
    st.markdown(
        """
        La **Sucesión de Fibonacci** se define por recurrencia lineal de segundo orden: cada término (a partir del tercero) 
        es la suma de los dos términos inmediatos anteriores. Además, el cociente entre términos consecutivos converge al **Número Áureo** $\\varphi$:
        """
    )
    st.latex(
        r"F_n = \begin{cases} 0 & \text{si } n = 1 \\ 1 & \text{si } n = 2 \\ F_{n-1} + F_{n-2} & \text{si } n \ge 3 \end{cases}, \qquad \lim_{n \to \infty} \frac{F_n}{F_{n-1}} = \varphi = \frac{1 + \sqrt{5}}{2} \approx 1.6180339887\dots"
    )

    c1, c2 = st.columns([1.5, 2.5])
    with c1:
        n_fib = int(st.slider("Cantidad de términos N a generar:", min_value=5, max_value=200, value=200, step=5, key=f"{key_prefix}_n"))
    with c2:
        st.info(
            f"💡 **Crecimiento Exponencial:** Para $N = 200$, el término $F_{{200}}$ alcanza **42 dígitos enteros**. "
            "Python gestiona enteros de precisión arbitraria sin desbordamiento (*overflow*)."
        )

    fib_lista, t_clock, t_cpu = generar_fibonacci(n_fib)
    phi_exacto = (1.0 + math.sqrt(5.0)) / 2.0

    m1, m2, m3 = st.columns(3)
    m1.metric("Cantidad de Términos Generados", f"{len(fib_lista)}")
    m2.metric(f"Cantidad de Dígitos de F_{n_fib}", f"{len(str(fib_lista[-1]))} dígitos")
    m3.metric("Tiempo de Cómputo (Reloj)", f"{t_clock * 1e6:.2f} µs", f"{t_clock:.8f} s")

    st.markdown(f"**Último término calculado ($F_{{{n_fib}}}$):**")
    st.code(f"F_{n_fib} = {fib_lista[-1]:,}".replace(",", "."), language="text")

    filas_fib = []
    for i, val in enumerate(fib_lista):
        cociente = (fib_lista[i] / fib_lista[i - 1]) if (i >= 2 and fib_lista[i - 1] != 0) else np.nan
        err_phi = abs(cociente - phi_exacto) if not np.isnan(cociente) else np.nan
        filas_fib.append({
            "Orden (n)": i + 1,
            "Valor Exacto F_n": str(val),
            "Cantidad de Cifras": len(str(val)),
            "Cociente F_n / F_{n-1}": f"{cociente:.10f}" if not np.isnan(cociente) else "—",
            "Distancia a φ |F_n/F_{n-1} - φ|": f"{err_phi:.4e}" if not np.isnan(err_phi) else "—",
        })

    st.subheader(f"Tabla de los Primeros {n_fib} Términos de Fibonacci")
    st.dataframe(pd.DataFrame(filas_fib), use_container_width=True)

    # Gráfico de convergencia del cociente al número áureo en los primeros 30 términos
    n_plot = min(n_fib, 30)
    if n_plot >= 4:
        ns_q = list(range(3, n_plot + 1))
        qs = [fib_lista[k - 1] / fib_lista[k - 2] for k in ns_q]
        fig_fib = go.Figure()
        fig_fib.add_trace(go.Scatter(
            x=ns_q, y=qs, mode="lines+markers",
            name="Cociente F_n / F_{n-1}",
            line=dict(color="#636EFA", width=2.5),
            marker=dict(size=8),
        ))
        fig_fib.add_hline(
            y=phi_exacto, line_dash="dash", line_color="#00CC96",
            annotation_text=f"Número Áureo φ ≈ {phi_exacto:.8f}",
        )
        fig_fib.update_layout(
            title="Convergencia Oscilante del Cociente F_n / F_{n-1} hacia la Razón Áurea φ",
            xaxis_title="Índice n",
            yaxis_title="F_n / F_{n-1}",
            hovermode="x unified",
        )
        st.plotly_chart(fig_fib, use_container_width=True)


def vista_cuadratica_lab1(key_prefix="lab1_cuad"):
    st.header("📐 Ejercicio 4: Modelado y Resolución Analítica de Ecuación Cuadrática")
    st.markdown(
        """
        **Enunciado del problema del Laboratorio 1:**  
        *«Al quíntuple de un número ($5x$) se le suma el triple de su cuadrado ($3x^2$), obteniéndose el triple del mismo ($3x$) más 1»*:
        """
    )
    st.latex(
        r"5x + 3x^2 = 3x + 1 \implies 3x^2 + 2x - 1 = 0 \implies x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \implies x_1 = \frac{1}{3}, \quad x_2 = -1"
    )

    caso_c = st.selectbox(
        "Seleccione el caso a resolver:",
        [
            "Caso del Práctico (Ejercicio 4): 3x² + 2x - 1 = 0  (a = 3, b = 2, c = -1)",
            "Caso Raíz Doble (Δ = 0): x² - 4x + 4 = 0  (a = 1, b = -4, c = 4)",
            "Caso Raíces Complejas (Δ < 0): x² + 2x + 5 = 0  (a = 1, b = 2, c = 5)",
            "Personalizado: Modificar libremente a, b y c",
        ],
        key=f"{key_prefix}_caso",
    )

    if "Ejercicio 4" in caso_c:
        a_d, b_d, c_d = 3.0, 2.0, -1.0
    elif "Raíz Doble" in caso_c:
        a_d, b_d, c_d = 1.0, -4.0, 4.0
    elif "Complejas" in caso_c:
        a_d, b_d, c_d = 1.0, 2.0, 5.0
    else:
        a_d, b_d, c_d = 2.0, -5.0, 2.0

    col1, col2, col3 = st.columns(3)
    with col1:
        a_val = st.number_input("Coeficiente cuadrático (a):", value=a_d, format="%.4f", key=f"{key_prefix}_a")
    with col2:
        b_val = st.number_input("Coeficiente lineal (b):", value=b_d, format="%.4f", key=f"{key_prefix}_b")
    with col3:
        c_val = st.number_input("Término independiente (c):", value=c_d, format="%.4f", key=f"{key_prefix}_c")

    raices, disc, duracion, estado = resolver_cuadratica_analitica(a_val, b_val, c_val)
    if raices is None:
        st.error(estado)
        return

    st.info(f"📌 **Naturaleza de las raíces:** {estado}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Discriminante Δ = b² - 4ac", f"{disc:.6f}")
    if disc >= 0:
        m2.metric("Raíz x₁", f"{raices[0]:.6f}")
        m3.metric("Raíz x₂", f"{raices[1]:.6f}")
    else:
        m2.metric("Raíz Compleja x₁", f"{raices[0].real:.4f} + {abs(raices[0].imag):.4f}i")
        m3.metric("Raíz Compleja x₂", f"{raices[1].real:.4f} - {abs(raices[1].imag):.4f}i")
    m4.metric("Tiempo de Ejecución", f"{duracion * 1e6:.2f} µs")

    # Gráfico de la parábola
    xv_vertice = -b_val / (2.0 * a_val)
    amplitud = max(abs(raices[0].real - xv_vertice) * 2.2, 2.5) if disc >= 0 else 4.0
    xs = np.linspace(xv_vertice - amplitud, xv_vertice + amplitud, 300)
    ys = a_val * (xs ** 2) + b_val * xs + c_val

    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"P(x) = {a_val:g}x² + {b_val:+g}x {c_val:+g}", line=dict(color="#1f77b4", width=3)))
    fig_p.add_hline(y=0, line_color="black", line_width=1.2)
    if disc >= 0:
        fig_p.add_trace(go.Scatter(
            x=[ float(raices[0]), float(raices[1]) ],
            y=[0.0, 0.0],
            mode="markers",
            name="Raíces Reales (P(x) = 0)",
            marker=dict(size=12, color="#D62728", symbol="diamond"),
        ))
    fig_p.update_layout(title="Interpretación Geométrica de la Parábola y sus Intersecciones con el Eje Horizontal", xaxis_title="x", yaxis_title="P(x)", hovermode="x unified")
    st.plotly_chart(fig_p, use_container_width=True)


def vista_series_e_pi(key_prefix="lab1_series"):
    st.header("♾️ Ejercicios 5, 6 y Complementarios: Aproximación de $e$, $e^x$ y $\\pi$ por Series")
    st.markdown(
        """
        Estudio de **Algoritmos Iterativos Convergentes** mediante sumas parciales de series de Taylor / Maclaurin. 
        Permite contrastar la **rápida convergencia factorial** de la serie exponencial frente a la **lenta convergencia algebraica** de la serie de Gregory-Leibniz para $\\pi$.
        """
    )

    sub_e, sub_pi, sub_compl = st.tabs([
        "📈 1. Ejercicio 5: Número e y Función Exponencial e^x por Serie",
        "🥧 2. Ejercicio 6: Número π por Serie de Gregory-Leibniz y Tolerancia",
        "🧩 3. Ejercicios Complementarios (Conteo de Términos de Serie)",
    ])

    with sub_e:
        st.latex(r"e = \sum_{k=0}^{N} \frac{1}{k!} = 1 + \frac{1}{1!} + \frac{1}{2!} + \frac{1}{3!} + \dots + \frac{1}{N!}, \qquad e^x = \sum_{k=0}^{N} \frac{x^k}{k!}")
        ce1, ce2 = st.columns(2)
        with ce1:
            n_term_e = int(st.slider("Cantidad de términos N de la serie de Euler:", min_value=1, max_value=30, value=15, key=f"{key_prefix}_ne"))
        with ce2:
            x_exp = float(st.number_input("Exponente x para evaluar e^x (use x = 1 para el número e):", value=1.0, step=0.5, format="%.4f", key=f"{key_prefix}_xe"))

        filas_e, aprox_f, aprox_dec, t_cl_e, t_cpu_e = calcular_serie_euler_historial(n_term_e, x_exp)
        val_ex_e = math.exp(x_exp)
        err_final_e = abs(val_ex_e - aprox_f)

        me1, me2, me3, me4 = st.columns(4)
        me1.metric(f"Aproximación S_{n_term_e} (float)", f"{aprox_f:.15f}")
        me2.metric("Valor Exacto (math.exp)", f"{val_ex_e:.15f}")
        me3.metric("Error Absoluto Final", f"{err_final_e:.4e}")
        me4.metric("Tiempo de Ejecución", f"{t_cl_e * 1e6:.2f} µs")

        st.caption(f"🔬 **Cálculo en Alta Precisión (`Decimal`, 50 cifras):** `{aprox_dec}`")

        df_e = pd.DataFrame(filas_e)
        st.dataframe(
            df_e.style.format({
                "Valor del Término": "{:.6e}",
                "Suma Parcial S_k (float)": "{:.15f}",
                "Valor Exacto": "{:.15f}",
                "Error Absoluto |e^x - S_k|": "{:.4e}",
                "Error Relativo (%)": "{:.6e}%",
            }),
            use_container_width=True,
        )

        fig_e = go.Figure()
        fig_e.add_trace(go.Scatter(
            x=df_e["Término (k)"],
            y=np.maximum(df_e["Error Absoluto |e^x - S_k|"], 1e-17),
            mode="lines+markers",
            name="Error Absoluto |e^x - S_k|",
            line=dict(color="#00CC96", width=2.5),
        ))
        fig_e.update_layout(
            title="Caída Exponencial del Error de Truncamiento en la Serie de Taylor de e^x (Escala Logarítmica)",
            xaxis_title="Cantidad de Términos Acumulados (k)",
            yaxis_title="Error Absoluto (Escala Log)",
            yaxis_type="log",
            hovermode="x unified",
        )
        st.plotly_chart(fig_e, use_container_width=True)

    with sub_pi:
        st.latex(
            r"\pi = 4 \sum_{k=0}^{\infty} \frac{(-1)^k}{2k + 1} = 4\left(1 - \frac{1}{3} + \frac{1}{5} - \frac{1}{7} + \frac{1}{9} - \dots\right), \qquad \text{Criterio de Scarborough: } E_a < 0.5 \times 10^{-n}"
        )

        st.subheader("Tabla del Práctico: Términos Requeridos según Cifras Decimales Exactas ($n = 3, 4, 5$)")
        filas_pi_ref = []
        for n_cif in [2, 3, 4, 5]:
            k_req, pi_ap, tol_c, err_c, t_c, _ = calcular_pi_leibniz_por_tolerancia(n_cif)
            filas_pi_ref.append({
                "Cifras Decimales Exactas (n)": n_cif,
                "Tolerancia (0.5 × 10⁻ⁿ)": f"{tol_c:.6f}",
                "Términos Necesarios (N)": f"{k_req:,}",
                "π Aproximado": f"{pi_ap:.8f}",
                "π Exacto (math.pi)": f"{math.pi:.8f}",
                "Error Absoluto Final": f"{err_c:.4e}",
                "Tiempo de Reloj (s)": f"{t_c:.6f} s",
            })
        st.dataframe(pd.DataFrame(filas_pi_ref), use_container_width=True)

        st.subheader("Simulador Interactivo de la Serie de Gregory-Leibniz por N° de Términos")
        n_pi_sim = int(st.slider("Seleccione la cantidad de términos N a sumar:", min_value=10, max_value=5000, value=200, step=10, key=f"{key_prefix}_npi"))
        hist_pi, pi_val_sim, err_pi_sim, t_pi_sim = calcular_pi_leibniz_historial(n_pi_sim)

        mp1, mp2, mp3, mp4 = st.columns(4)
        mp1.metric(f"π Aproximado ({n_pi_sim} términos)", f"{pi_val_sim:.8f}")
        mp2.metric("π Exacto (math.pi)", f"{math.pi:.8f}")
        mp3.metric("Error Absoluto", f"{err_pi_sim:.4e}")
        mp4.metric("Tiempo de Ejecución", f"{t_pi_sim * 1e6:.1f} µs")

        df_pi_h = pd.DataFrame(hist_pi)
        fig_pi = go.Figure()
        fig_pi.add_trace(go.Scatter(
            x=df_pi_h["Término (k+1)"],
            y=df_pi_h["π Aproximado (S_k)"],
            mode="lines",
            name="Suma Parcial de Leibniz S_k",
            line=dict(color="#AB63FA", width=2.2),
        ))
        fig_pi.add_hline(y=math.pi, line_dash="dash", line_color="#00CC96", annotation_text=f"π Exacto = {math.pi:.6f}")
        fig_pi.update_layout(
            title="Oscilación Amortiguada de las Sumas Parciales de Gregory-Leibniz alrededor de π",
            xaxis_title="Número de Términos (k)",
            yaxis_title="Aproximación de π",
            hovermode="x unified",
        )
        st.plotly_chart(fig_pi, use_container_width=True)
        st.dataframe(df_pi_h, use_container_width=True)

    with sub_compl:
        st.subheader("Ejercicio Complementario 1 (`compl_ejer_1.py`): Conteo de términos en serie de impares")
        st.markdown(
            "Dada la serie de fracciones con denominadores impares sucesivos $1 + \\frac{1}{3} + \\frac{1}{5} + \\dots + \\frac{1}{2i+1}$, "
            "determinar cuántos términos componen la suma conociendo el denominador del último término:"
        )
        st.latex(r"a_i = \frac{1}{2i + 1} \implies i = \frac{\text{Denominador} - 1}{2}, \qquad N_{\text{términos}} = i + 1")
        denom_imp = int(st.number_input("Denominador impar del último término (ej. 17 en el práctico):", min_value=1, max_value=9999, value=17, step=2, key=f"{key_prefix}_den"))
        if denom_imp % 2 == 0:
            st.warning("El denominador de la serie $1/(2i+1)$ debe ser un número impar.")
        indice_i = (denom_imp - 1) // 2
        n_terminos_c1 = indice_i + 1
        st.success(f"✅ Para el último término $1/{denom_imp}$, el índice final es $i = {indice_i}$ y la serie posee exactamente **$N = {n_terminos_c1}$ términos**.")


def vista_comparativa_lab1():
    st.header("📊 Vista Completa del Laboratorio 1: Modelos, Algoritmos y Series")
    t1, t2, t3, t4 = st.tabs([
        "🧮 1. Sumas y Rendimiento (Ej. 1 y 2)",
        "🌱 2. Sucesión de Fibonacci (Ej. 3)",
        "📐 3. Ecuación Cuadrática (Ej. 4)",
        "♾️ 4. Aproximación de e y π (Ej. 5 y 6)",
    ])
    with t1:
        vista_sumas_rendimiento("tab_sumas")
    with t2:
        vista_fibonacci("tab_fib")
    with t3:
        vista_cuadratica_lab1("tab_cuad")
    with t4:
        vista_series_e_pi("tab_series")


METODOS_LAB1 = {
    "Suma de N Números y Suma de Pares": vista_sumas_rendimiento,
    "Sucesión de Fibonacci (N = 200)": vista_fibonacci,
    "Ecuación Cuadrática Analítica": vista_cuadratica_lab1,
    "Aproximación de e y π por Series": vista_series_e_pi,
    "📊 Vista Comparativa del Laboratorio": vista_comparativa_lab1,
}


def render_lab1(metodo_seleccionado=None):
    """Renderiza el ejercicio seleccionado del Laboratorio 1 o su vista completa por pestañas."""
    if metodo_seleccionado is None:
        st.title("🧮 Laboratorio 1: Modelos Algorítmicos, Tiempos y Series Numéricas")
        vista_comparativa_lab1()
        return

    fn = METODOS_LAB1.get(metodo_seleccionado, vista_comparativa_lab1)
    fn()


if __name__ == "__main__":
    try:
        st.set_page_config(layout="wide", page_title="Lab 1: Modelos Algorítmicos y Series")
    except Exception:
        pass
    render_lab1()

