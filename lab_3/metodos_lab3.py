"""
Módulo de Métodos Numéricos para Laboratorio 3
Contiene: Regla de Descartes, Tanteo (Bolzano), Intervalo Medio, 
Interpolación Lineal, Newton-Raphson con Fourier, e Iteración / Aitken.
"""
import time
import math
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt


# regla de signos de descartes y grado del polinomio
def regla_descartes(f_simb, x):
    try:
        pol = sp.Poly(f_simb, x)
    except:
        print("\nLa funcion no es un polinomio, no se puede aplicar descartes.")
        return 1, 1
    
    grado = pol.degree()
    print("-" * 50)
    print(f"Grado del polinomio: {grado} (TFA: {grado} raices totales)")

    # Coeficientes para x > 0 sin ceros
    c_pos = [c for c in pol.all_coeffs() if c != 0]
    var_pos = sum(1 for i in range(len(c_pos) - 1) if c_pos[i] * c_pos[i + 1] < 0)
    raices_pos = [var_pos - 2 * k for k in range(var_pos // 2 + 1)]

    # Coeficientes para x < 0 evaluando P(-x)
    pol_neg = sp.Poly(f_simb.subs(x, -x), x)
    c_neg = [c for c in pol_neg.all_coeffs() if c != 0]
    var_neg = sum(1 for i in range(len(c_neg) - 1) if c_neg[i] * c_neg[i + 1] < 0)
    raices_neg = [var_neg - 2 * k for k in range(var_neg // 2 + 1)]

    print(f"Variaciones signo x > 0: {var_pos} -> Posibles raices pos: {raices_pos}")
    print(f"Variaciones signo x < 0: {var_neg} -> Posibles raices neg: {raices_neg}")
    print("-" * 50)

    max_p = max(raices_pos) if raices_pos else 0
    max_n = max(raices_neg) if raices_neg else 0
    return max_p, max_n


def barrido_tanteo(fn, x_ini=0.0, sentido="positiva", max_r=1, paso=0.5, x_max=100.0):
    """
    Busqueda incremental que aisla raices por Bolzano: f(a)*f(b) < 0.
    """
    intervalos = []
    dx = abs(paso) if sentido == "positiva" else -abs(paso)
    x_act = float(x_ini)

    try:
        f_ant = fn(x_act)
    except Exception:
        return intervalos

    pasos = 0
    limite = int(x_max / abs(paso))

    while len(intervalos) < max_r and pasos < limite:
        x_sig = x_act + dx
        try:
            f_sig = fn(x_sig)
            if f_ant * f_sig < 0:
                a_min = min(x_act, x_sig)
                b_max = max(x_act, x_sig)
                intervalos.append((round(a_min, 4), round(b_max, 4)))
            elif abs(f_sig) < 1e-12:
                intervalos.append((round(x_sig, 4), round(x_sig, 4)))
        except Exception:
            break

        x_act = x_sig
        f_ant = f_sig
        pasos += 1

    return intervalos


# -------------------------------------------------------------
# 2. INTERVALO MEDIO E INTERPOLACIÓN LINEAL
# -------------------------------------------------------------

def metodo_intervalo_medio(fn, a, b, tol=1e-3, max_iter=100):
    """
    Metodo de Biseccion. Informa iteraciones teoricas minimas.
    """
    t_ini = time.perf_counter()
    if fn(a) * fn(b) >= 0:
        raise ValueError("No cumple Bolzano en el intervalo [a, b]")

    # Estimacion previa de iteraciones teoricas
    n_teorico = math.ceil((math.log(b - a) - math.log(tol)) / math.log(2))
    print(f"Iteraciones teoricas estimadas: {n_teorico}")

    c_ant = a
    for k in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = fn(c)
        err = abs(c - c_ant) if k > 1 else abs(b - a)

        if err < tol or abs(fc) < 1e-14:
            t_total = time.perf_counter() - t_ini
            return c, k, err, t_total

        if fn(a) * fc < 0:
            b = c
        else:
            a = c
        c_ant = c

    t_total = time.perf_counter() - t_ini
    return c_ant, max_iter, err, t_total


def metodo_interpolacion_lineal(fn, a, b, tol=1e-3, max_iter=100):
    """
    Metodo de Regula Falsi.
    """
    t_ini = time.perf_counter()
    if fn(a) * fn(b) >= 0:
        raise ValueError("No cumple Bolzano en el intervalo [a, b]")

    x_ant = a
    for k in range(1, max_iter + 1):
        fa = fn(a)
        fb = fn(b)
        x_sig = (a * fb - b * fa) / (fb - fa)
        fx_sig = fn(x_sig)
        err = abs(x_sig - x_ant) if k > 1 else abs(b - a)

        if err < tol or abs(fx_sig) < 1e-14:
            t_total = time.perf_counter() - t_ini
            return x_sig, k, err, t_total

        if fa * fx_sig < 0:
            b = x_sig
        else:
            a = x_sig
        x_ant = x_sig

    t_total = time.perf_counter() - t_ini
    return x_ant, max_iter, err, t_total


# -------------------------------------------------------------
# 3. CONDICIONES DE FOURIER Y NEWTON-RAPHSON
# -------------------------------------------------------------

def chequear_condiciones_fourier(fn, d1, d2, d1_simb, x, a, b):
    """
    Verifica:
    1. Bolzano: f(a)*f(b) < 0
    2. Monotonia: f'(x) != 0 en (a, b)
    3. Fourier: f(x0)*f''(x0) > 0 para elegir x0
    """
    print(f"\n--- Condiciones de Fourier en [{a:.4f} ; {b:.4f}] ---")
    fa, fb = fn(a), fn(b)

    # 1. Bolzano
    if fa * fb >= 0:
        print(" [X] Bolzano: No hay cambio de signo.")
        return None
    print(" [OK] Condicion I (Bolzano): Cumple.")

    # 2. Monotonia (derivada no nula)
    try:
        pts = sp.solve(d1_simb, x)
        criticos = [float(p.evalf()) for p in pts if p.is_real and a <= float(p.evalf()) <= b]
        if criticos:
            print(f" [!] Alerta monotonia: Puntos criticos en {criticos}")
        else:
            print(" [OK] Condicion II (Monotonia): f'(x) != 0 en el intervalo.")
    except Exception:
        if d1(a) * d1(b) > 0:
            print(" [OK] Condicion II (Monotonia): Mismo signo en bordes.")
        else:
            print(" [!] Alerta: f' cambia de signo.")

    # 3. Eleccion de x0 por Fourier
    f2a, f2b = d2(a), d2(b)
    if fa * f2a > 0:
        x0 = a
        print(f" [OK] Condicion III (Fourier): Cumple en x=a -> x0 = {x0:.4f}")
        return x0
    elif fb * f2b > 0:
        x0 = b
        print(f" [OK] Condicion III (Fourier): Cumple en x=b -> x0 = {x0:.4f}")
        return x0
    else:
        x0 = a if abs(fa) < abs(fb) else b
        print(f" [!] Ningun borde cumple f*f''>0. Se toma x0 = {x0:.4f} (menor |f|)")
        return x0


def metodo_newton_raphson(fn, d1, x0, tol=1e-3, max_iter=50):
    """
    Iteraciones de Newton-Raphson mostrando la tabla paso a paso.
    """
    t_ini = time.perf_counter()
    x_val = x0

    print("\n" + "-" * 75)
    print(f"{'k':<5} {'x_k':<15} {'f(x_k)':<15} {'f\'(x_k)':<15} {'x_{k+1}':<15} {'Error':<15}")
    print("-" * 75)

    for k in range(max_iter):
        fx = fn(x_val)
        dfx = d1(x_val)

        if abs(dfx) < 1e-14:
            print("Error: Derivada nula.")
            return x_val, k, abs(fx), False, time.perf_counter() - t_ini

        x_sig = x_val - (fx / dfx)
        err = abs(x_sig - x_val)

        print(f"{k+1:<5} {x_val:<15.6f} {fx:<15.4e} {dfx:<15.6f} {x_sig:<15.6f} {err:<15.4e}")

        if err < tol or abs(fx) < tol:
            t_total = time.perf_counter() - t_ini
            return x_sig, k + 1, err, True, t_total

        x_val = x_sig

    t_total = time.perf_counter() - t_ini
    return x_val, max_iter, err, False, t_total


# -------------------------------------------------------------
# 4. ITERACIÓN Y ACELERACIÓN DE AITKEN
# -------------------------------------------------------------

def metodo_iteracion(g_fn, x0, tol=1e-4, max_iter=100, usar_aitken=False):
    """
    Metodo de iteracion de punto fijo x = g(x), con soporte opcional de Aitken.
    """
    t_ini = time.perf_counter()
    x = x0

    print("\n" + "-" * 60)
    metodo_str = "Iteracion + Aitken" if usar_aitken else "Iteracion Simple"
    print(f"Iniciando {metodo_str} con x0 = {x0}")
    print(f"{'k':<5} {'x_k':<20} {'x_{k+1}':<20} {'Error':<15}")
    print("-" * 60)

    for k in range(1, max_iter + 1):
        if not usar_aitken:
            x_sig = g_fn(x)
            err = abs(x_sig - x)
            print(f"{k:<5} {x:<20.8f} {x_sig:<20.8f} {err:<15.4e}")
            if err < tol:
                t_total = time.perf_counter() - t_ini
                return x_sig, k, err, t_total
            x = x_sig
        else:
            # Aitken requiere x_k, x_{k+1}, x_{k+2}
            x1 = g_fn(x)
            x2 = g_fn(x1)
            den = x2 - 2 * x1 + x
            if abs(den) < 1e-14:
                x_sig = x2
            else:
                x_sig = x - ((x1 - x) ** 2) / den

            err = abs(x_sig - x)
            print(f"{k:<5} {x:<20.8f} {x_sig:<20.8f} {err:<15.4e}")
            if err < tol:
                t_total = time.perf_counter() - t_ini
                return x_sig, k, err, t_total
            x = x_sig

    t_total = time.perf_counter() - t_ini
    return x, max_iter, err, t_total


# -------------------------------------------------------------
# 5. UTILIDADES GRÁFICAS
# -------------------------------------------------------------

def graficar_curva(fn, a_vis, b_vis, intervalos=None, raices=None, titulo="Grafico de la funcion"):
    xs = np.linspace(a_vis, b_vis, 600)
    ys = [fn(pt) for pt in xs]

    plt.figure(figsize=(9, 5))
    plt.plot(xs, ys, "b-", label="f(x)")
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8)
    plt.axvline(0, color="black", linestyle="--", linewidth=0.8)

    if intervalos:
        for idx, (a, b) in enumerate(intervalos):
            lbl = "Intervalo tanteo" if idx == 0 else ""
            plt.axvspan(a, b, color="orange", alpha=0.3, label=lbl)

    if raices:
        for idx, r in enumerate(raices):
            lbl = "Raiz" if idx == 0 else ""
            plt.plot(r, fn(r), "ro", markersize=6, label=lbl)
            plt.text(r, fn(r), f"  r={r:.4f}", color="darkred")

    plt.title(titulo)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True, linestyle=":")
    plt.legend()
    plt.show()