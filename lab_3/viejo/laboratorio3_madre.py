"""
MÉTODOS COMPUTACIONALES - LABORATORIO 3
SCRIPT MADRE: Resolución de Ecuaciones No Lineales
Flujo: Análisis de Descartes -> Tanteo por Bolzano -> Métodos Numéricos
"""

import math
import time
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

# ==============================================================================
# 1. ANÁLISIS PREVIO: TEOREMA FUNDAMENTAL Y REGLA DE DESCARTES
# ==============================================================================
def analizar_descartes(f_sympy, x_sym):
    try:
        poly = sp.Poly(f_sympy, x_sym)
    except (sp.PolynomialError, sp.GeneratorsError):
        print("\n[!] La función ingresada no es puramente polinómica. Omitiendo Descartes.")
        return 1, 1

    grado = poly.degree()
    print("\n" + "=" * 80)
    print(" ANÁLISIS PREVIO: TEOREMA FUNDAMENTAL DEL ÁLGEBRA Y REGLA DE DESCARTES")
    print("=" * 80)
    print(f"• Grado del polinomio: {grado}")
    print(f"• Teorema Fundamental del Álgebra: Posee {grado} raíces en total (reales y/o complejas).")

    # Coeficientes ignorando ceros
    coeffs_pos = [c for c in poly.all_coeffs() if c != 0]
    var_pos = sum(1 for i in range(len(coeffs_pos) - 1) if (coeffs_pos[i] * coeffs_pos[i+1]) < 0)
    posibles_pos = [var_pos - 2*k for k in range(var_pos // 2 + 1)]

    poly_neg = sp.Poly(f_sympy.subs(x_sym, -x_sym), x_sym)
    coeffs_neg = [c for c in poly_neg.all_coeffs() if c != 0]
    var_neg = sum(1 for i in range(len(coeffs_neg) - 1) if (coeffs_neg[i] * coeffs_neg[i+1]) < 0)
    posibles_neg = [var_neg - 2*k for k in range(var_neg // 2 + 1)]

    print(f"\n• Regla de los signos de Descartes:")
    print(f"  - Para x > 0: {var_pos} variaciones de signo -> Posibles raíces positivas: {posibles_pos}")
    print(f"  - Para x < 0: {var_neg} variaciones de signo -> Posibles raíces negativas: {posibles_neg}")

    print("\n• Combinaciones teóricas posibles de raíces:")
    print(f"{'Reales Positivas':<20} {'Reales Negativas':<20} {'Complejas':<15} {'Total':<10}")
    print("-" * 65)
    for p in posibles_pos:
        for n in posibles_neg:
            complejas = grado - (p + n)
            if complejas >= 0:
                print(f"{p:<20} {n:<20} {complejas:<15} {grado:<10}")
    print("=" * 80)
    return max(posibles_pos), max(posibles_neg)

# ==============================================================================
# 2. SEPARACIÓN DE RAÍCES POR MÉTODO DE TANTEO (BOLZANO)
# ==============================================================================
def metodo_tanteo(func, x_inicio=0.0, direccion="positiva", max_raices=1, paso=0.5, limite_seguridad=100.0):
    intervalos = []
    delta = abs(paso) if direccion == "positiva" else -abs(paso)
    x_actual = float(x_inicio)

    try:
        f_ant = func(x_actual)
    except Exception as e:
        print(f"[!] Error al evaluar en x = {x_actual}: {e}")
        return intervalos

    pasos = 0
    max_pasos = int(limite_seguridad / abs(paso))

    print("\n" + "-" * 65)
    print(f"{'x':<12} {'f(x)':<18} {'Signo':<10} {'Teorema de Bolzano':<20}")
    print("-" * 65)
    print(f"{x_actual:<12.4f} {f_ant:<18.4e} {'(-)' if f_ant < 0 else '(+)':<10} {'Inicio':<20}")

    while len(intervalos) < max_raices and pasos < max_pasos:
        x_sig = x_actual + delta
        try:
            f_sig = func(x_sig)
            signo_str = "(-)" if f_sig < 0 else "(+)"

            if f_ant * f_sig < 0:
                a_int = min(x_actual, x_sig)
                b_int = max(x_actual, x_sig)
                intervalos.append((a_int, b_int))
                print(f"{x_sig:<12.4f} {f_sig:<18.4e} {signo_str:<10} {'¡Cambio de signo!':<20}")
            elif f_sig == 0:
                intervalos.append((x_sig, x_sig))
                print(f"{x_sig:<12.4f} {f_sig:<18.4e} {'(0)':<10} {'Raíz exacta hallada':<20}")
            else:
                print(f"{x_sig:<12.4f} {f_sig:<18.4e} {signo_str:<10} {'Mismo signo':<20}")
        except Exception:
            break

        x_actual = x_sig
        f_ant = f_sig
        pasos += 1

    print("-" * 65)
    return intervalos

# ==============================================================================
# 3. MÉTODOS DE APROXIMACIÓN DE RAÍCES
# ==============================================================================

# A. Método de Intervalo Medio (Bisección)
def resolver_intervalo_medio(f, a, b, tol):
    fa, fb = f(a), f(b)
    if fa * fb >= 0:
        print("[!] Error: No se cumple Bolzano en el intervalo seleccionado.")
        return None

    # Cantidad teórica mínima de iteraciones a priori
    n_teorico = math.ceil((math.log(b - a) - math.log(tol)) / math.log(2))
    print(f"\n[*] Cantidad mínima teórica de iteraciones requeridas (a priori): n >= {n_teorico}")

    t_inicio = time.perf_counter()
    k = 1
    xr_ant = None

    print("\n" + "=" * 80)
    print(f"{'k':<4} {'a':<12} {'b':<12} {'xr':<14} {'f(xr)':<16} {'Error |b-a|/2':<14}")
    print("=" * 80)

    while True:
        xr = (a + b) / 2.0
        fxr = f(xr)
        error = (b - a) / 2.0

        print(f"{k:<4} {a:<12.6f} {b:<12.6f} {xr:<14.6f} {fxr:<16.6e} {error:<14.6e}")

        if error < tol or abs(fxr) < 1e-15:
            break

        if fa * fxr < 0:
            b = xr
            fb = fxr
        else:
            a = xr
            fa = fxr

        xr_ant = xr
        k += 1

    t_total = time.perf_counter() - t_inicio
    print("=" * 80)
    print(f"[✓] Raíz hallada: xr = {xr:.8f}")
    print(f"[✓] Iteraciones realizadas: {k}")
    print(f"[✓] Tiempo de ejecución: {t_total:.6f} segundos")
    return xr

# B. Método de Interpolación Lineal (Regula Falsi)
def resolver_interpolacion_lineal(f, a, b, tol):
    fa, fb = f(a), f(b)
    if fa * fb >= 0:
        print("[!] Error: No se cumple Bolzano en el intervalo seleccionado.")
        return None

    t_inicio = time.perf_counter()
    k = 1
    xr_ant = None

    print("\n" + "=" * 80)
    print(f"{'k':<4} {'a':<12} {'b':<12} {'xr':<14} {'f(xr)':<16} {'Error |xr - xr_ant|':<14}")
    print("=" * 80)

    while True:
        # Fórmula de partes proporcionales
        xr = (a * fb - b * fa) / (fb - fa)
        fxr = f(xr)
        error = abs(xr - xr_ant) if xr_ant is not None else abs(b - a)

        err_str = f"{error:.6e}" if xr_ant is not None else "---"
        print(f"{k:<4} {a:<12.6f} {b:<12.6f} {xr:<14.6f} {fxr:<16.6e} {err_str:<14}")

        if xr_ant is not None and error < tol:
            break

        if fa * fxr < 0:
            b = xr
            fb = fxr
        else:
            a = xr
            fa = fxr

        xr_ant = xr
        k += 1

    t_total = time.perf_counter() - t_inicio
    print("=" * 80)
    print(f"[✓] Raíz hallada: xr = {xr:.8f}")
    print(f"[✓] Iteraciones realizadas: {k}")
    print(f"[✓] Tiempo de ejecución: {t_total:.6f} segundos")
    return xr

# C. Método de Newton-Raphson (Verificación de las 3 condiciones y Fourier)
def resolver_newton_raphson(f_num, f1_num, f2_num, f1_sym, x_sym, a, b, tol, max_iter=50):
    print("\n--- COMPROBACIÓN DE CONDICIONES DE CONVERGENCIA ---")
    fa, fb = f_num(a), f_num(b)
    if fa * fb >= 0:
        print("  [x] Condición I (Bolzano) NO satisfecha.")
        return None
    print("  [✓] Condición I (Bolzano) satisfecha: f(a)*f(b) < 0.")

    # Condición II: Monotonía en [a, b]
    try:
        criticos = [r.evalf() for r in sp.solve(f1_sym, x_sym) if r.is_real and a <= r <= b]
        if len(criticos) == 0:
            print(f"  [✓] Condición II (Monotonía) satisfecha: f'(x) != 0 en [{a:.2f}, {b:.2f}].")
        else:
            print(f"  [!] Alerta de punto crítico en el intervalo: {criticos}")
    except Exception:
        if f1_num(a) * f1_num(b) > 0:
            print("  [✓] Condición II (Monotonía) verificada numéricamente.")

    # Condición III: Criterio de Fourier para el punto de arranque x0
    f2a, f2b = f2_num(a), f2_num(b)
    if fa * f2a > 0:
        x0 = a
        print(f"  [✓] Condición III (Fourier) satisfecha en x = a -> x0 = {x0:.4f}")
    elif fb * f2b > 0:
        x0 = b
        print(f"  [✓] Condición III (Fourier) satisfecha en x = b -> x0 = {x0:.4f}")
    else:
        x0 = (a + b) / 2.0
        print(f"  [!] Ningún extremo cumple Fourier en bordes. Fallback: x0 = {x0:.4f}")

    # Iteraciones
    t_inicio = time.perf_counter()
    x = x0
    print("\n" + "=" * 90)
    print(f"{'k':<4} {'x_k':<15} {'f(x_k)':<15} {'f\'(x_k)':<15} {'x_{k+1}':<15} {'Error':<15}")
    print("=" * 90)

    for k in range(max_iter):
        fx = f_num(x)
        fpx = f1_num(x)
        if abs(fpx) < 1e-14:
            print("[!] Error: Derivada nula.")
            return None

        x_sig = x - fx / fpx
        error = abs(x_sig - x)
        print(f"{k:<4} {x:<15.6f} {fx:<15.6e} {fpx:<15.6f} {x_sig:<15.6f} {error:<15.6e}")

        if error < tol or abs(fx) < tol:
            t_total = time.perf_counter() - t_inicio
            print("=" * 90)
            print(f"[✓] Raíz hallada: x = {x_sig:.8f}")
            print(f"[✓] Iteraciones: {k + 1}")
            print(f"[✓] Tiempo de ejecución: {t_total:.6f} segundos")
            return x_sig
        x = x_sig

    return x

# D. Método de Iteración (Punto Fijo) y Aceleración de Aitken
def resolver_iteracion_y_aitken(x0, tol):
    print("\nFormulación canónica del método de iteración: x = g(x)")
    g_str = input("Ingrese la función g(x) despejada (ej: 200 + 40*log(400/(500-x))): ").strip()
    x_sym = sp.Symbol('x')
    g_sym = sp.sympify(g_str)
    g1_sym = sp.diff(g_sym, x_sym)

    g = sp.lambdify(x_sym, g_sym, modules=['numpy', 'math'])
    g1 = sp.lambdify(x_sym, g1_sym, modules=['numpy', 'math'])

    usar_aitken = input("¿Desea aplicar la Aceleración de Aitken? (s/n): ").strip().lower() == 's'

    # Verificación del criterio de Lipschitz / contracción
    dg_val = g1(x0)
    print(f"\n[*] Derivada g'({x0:.2f}) = {dg_val:.4f}")
    if abs(dg_val) < 1.0:
        print("    [✓] Cumple condición de contracción |g'(x0)| < 1 (Convergencia asegurada).")
    else:
        print("    [!] Advertencia: |g'(x0)| >= 1 (El método podría divergir).")

    t_inicio = time.perf_counter()
    x = x0

    if not usar_aitken:
        print("\n" + "=" * 65)
        print(f"{'k':<5} {'x_k':<18} {'x_{k+1} = g(x_k)':<22} {'Error':<15}")
        print("=" * 65)
        k = 0
        while k < 100:
            x_next = g(x)
            error = abs(x_next - x)
            print(f"{k:<5} {x:<18.6f} {x_next:<22.6f} {error:<15.6e}")
            if error < tol:
                k += 1
                x = x_next
                break
            x = x_next
            k += 1
    else:
        print("\n" + "=" * 70)
        print(f"{'Paso/Salto':<12} {'x_calculado':<18} {'Tipo de paso':<22} {'Error':<15}")
        print("=" * 70)
        k = 0
        while k < 50:
            x1 = g(x)
            x2 = g(x1)
            den = x2 - 2 * x1 + x
            if abs(den) < 1e-14:
                x = x2
                break
            x_aitken = x2 - ((x2 - x1) ** 2) / den
            error_salto = abs(x_aitken - x2)
            print(f"{k:<12} {x_aitken:<18.6f} {'Aitken (Salto)':<22} {error_salto:<15.6e}")

            # Confirmación de parada de la cátedra
            x_check = g(x_aitken)
            error_conf = abs(x_check - x_aitken)
            k += 1
            if error_conf < tol:
                x = x_check
                print(f"{k:<12} {x:<18.6f} {'Punto Fijo (Parada)':<22} {error_conf:<15.6e}")
                break
            x = x_aitken

    t_total = time.perf_counter() - t_inicio
    print("=" * 70)
    print(f"[✓] Raíz aproximada: x = {x:.8f}")
    print(f"[✓] Evaluaciones/Pasos: {k}")
    print(f"[✓] Tiempo de ejecución: {t_total:.6f} segundos")

    # Gráfico simultáneo de las dos curvas y = x e y = g(x)
    x_grid = np.linspace(min(x0, x) - 10, max(x0, x) + 10, 400)
    plt.figure(figsize=(8, 6))
    plt.plot(x_grid, x_grid, 'k--', label='y = x (Bisectriz)')
    plt.plot(x_grid, [g(v) for v in x_grid], 'b-', label='y = g(x)')
    plt.plot(x, x, 'ro', markersize=6, label=f'Punto Fijo x ≈ {x:.4f}')
    plt.title("Método de Iteración: Curvas y = x e y = g(x)")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
    return x

# ==============================================================================
# 4. FUNCIÓN GRÁFICA DE f(x) CON INTERVALOS DE BOLZANO
# ==============================================================================
def graficar_funcion_con_intervalos(func, intervalos, x_min, x_max, raiz=None):
    x_vals = np.linspace(x_min, x_max, 600)
    y_vals = [func(v) for v in x_vals]

    plt.figure(figsize=(9, 5))
    plt.plot(x_vals, y_vals, 'b-', label='f(x)')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.axvline(0, color='gray', linestyle=':', linewidth=0.8)

    for i, (a, b) in enumerate(intervalos):
        plt.axvspan(a, b, color='red', alpha=0.25, label=f'Intervalo [{a:.2f}, {b:.2f}]' if i == 0 else "")

    if raiz is not None:
        plt.plot(raiz, func(raiz), 'go', markersize=8, label=f'Raíz ≈ {raiz:.4f}')

    plt.title("Separación de Raíces por Tanteo (Bolzano)")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()

# ==============================================================================
# MENÚ PRINCIPAL Y COORDINADOR DE FLUJO
# ==============================================================================
def main():
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║   MÉTODOS COMPUTACIONALES - SCRIPT MADRE DE RESOLUCIÓN DE ECUACIONES      ║")
    print("║  Descartes -> Tanteo (Bolzano) -> Selección y Ejecución de Métodos        ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")

    x_sym = sp.Symbol('x')
    f_str = input("\nIngrese la ecuación f(x) = 0 (ej: x**3 - 6*x**2 + 11*x - 6.1): ").strip()

    try:
        f_sym = sp.sympify(f_str)
        f1_sym = sp.diff(f_sym, x_sym)
        f2_sym = sp.diff(f_sym, x_sym, 2)

        f_num = sp.lambdify(x_sym, f_sym, modules=['numpy', 'math'])
        f1_num = sp.lambdify(x_sym, f1_sym, modules=['numpy', 'math'])
        f2_num = sp.lambdify(x_sym, f2_sym, modules=['numpy', 'math'])
    except Exception as e:
        print(f"[!] Error procesando la función: {e}")
        return

    # 1. Regla de Descartes
    max_pos, max_neg = analizar_descartes(f_sym, x_sym)

    # 2. Configuración de Tanteo
    print("\n--- CONFIGURACIÓN DE SEPARACIÓN POR TANTEO ---")
    tipo_busqueda = input("¿Desea buscar raíces 'positivas' o 'negativas'? [p/n] (Defecto 'p'): ").strip().lower()
    direccion = "negativa" if tipo_busqueda == 'n' else "positiva"
    max_a_buscar = max_neg if direccion == "negativa" else max_pos

    x_ini_in = input("Ingrese el punto de inicio de tanteo [Defecto 0.0]: ").strip()
    x_inicio = float(x_ini_in) if x_ini_in else 0.0

    limite_in = input("Ingrese la cota máxima de exploración [Defecto 50.0]: ").strip()
    limite_seguridad = float(limite_in) if limite_in else 50.0

    paso_in = input("Ingrese el paso de tanteo Δx [Defecto 0.5]: ").strip()
    paso = float(paso_in) if paso_in else 0.5

    tol_in = input("Ingrese la cota de error E [Defecto 0.001]: ").strip()
    tolerancia = float(tol_in) if tol_in else 0.001

    # 3. Ejecución del Tanteo
    intervalos = metodo_tanteo(f_num, x_inicio, direccion, max_a_buscar, paso, limite_seguridad)

    if not intervalos:
        print("[!] No se aislaron raíces en el rango especificado.")
        return

    print(f"\n[✓] Se aislaron {len(intervalos)} intervalo(s) con cambio de signo:")
    for idx, (a, b) in enumerate(intervalos, 1):
        print(f"    Intervalo {idx}: [{a:.4f} ; {b:.4f}]")

    # Muestra el gráfico con las zonas detectadas
    x_graf_min = min(x_inicio, min(a for a, b in intervalos)) - 1
    x_graf_max = max(x_inicio, max(b for a, b in intervalos)) + 1
    graficar_funcion_con_intervalos(f_num, intervalos, x_graf_min, x_graf_max)

    # 4. Menú de Métodos para resolver sobre un intervalo seleccionado
    print("\n" + "=" * 50)
    print(" SELECCIÓN DE MÉTODO NUMÉRICO PARA LA RAÍZ")
    print("=" * 50)
    print("1. Método de Intervalo Medio (Bisección)")
    print("2. Método de Interpolación Lineal (Regula Falsi)")
    print("3. Método de Newton-Raphson (Condiciones de Fourier)")
    print("4. Método de Iteración (Punto Fijo) y Aceleración de Aitken")

    opc = input("Seleccione el método a aplicar (1-4): ").strip()
    a_sel, b_sel = intervalos[0]
    if len(intervalos) > 1:
        sel_idx = int(input(f"Elija el intervalo a procesar (1 a {len(intervalos)}): ") or "1") - 1
        a_sel, b_sel = intervalos[sel_idx]

    raiz_obtenida = None
    if opc == '1':
        raiz_obtenida = resolver_intervalo_medio(f_num, a_sel, b_sel, tolerancia)
    elif opc == '2':
        raiz_obtenida = resolver_interpolacion_lineal(f_num, a_sel, b_sel, tolerancia)
    elif opc == '3':
        raiz_obtenida = resolver_newton_raphson(f_num, f1_num, f2_num, f1_sym, x_sym, a_sel, b_sel, tolerancia)
    elif opc == '4':
        x0_sug = (a_sel + b_sel) / 2.0
        x0_in = input(f"Ingrese punto inicial x0 [Sugerido {x0_sug:.4f}]: ").strip()
        x0 = float(x0_in) if x0_in else x0_sug
        raiz_obtenida = resolver_iteracion_y_aitken(x0, tolerancia)
    else:
        print("Opción inválida.")

    # Si se halló la raíz, mostramos el gráfico final con el punto exacto marcado
    if raiz_obtenida is not None:
        graficar_funcion_con_intervalos(f_num, [(a_sel, b_sel)], x_graf_min, x_graf_max, raiz=raiz_obtenida)

if __name__ == "__main__":
    main()