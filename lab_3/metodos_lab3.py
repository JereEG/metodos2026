"""
Módulo de Metodos con funciones,reglas y condiciones para Laboratorio 3
Funciones:Regla de Descartes, Tanteo (Bolzano),graficadora, 
Metodos de raices:Intervalo medio,interpolacion lineal,newton raphson,iteracion / con aitken
"""
#mediciones
import time
#herramientas matematicas
import math
import sympy as sp 
#graficadora 
import numpy as np 
import matplotlib.pyplot as plt 


# regla de signos de descartes y grado del polinomio
def regla_descartes(fx, x):
  
    if not fx.is_polynomial(x) or fx==0:
       raise ValueError("La expresión ingresada debe ser un polinomio para aplicar Descartes.")
   
    polinomio = sp.Poly(fx, x)
    grado = polinomio.degree()
    print("-" * 50)
    print(f"Grado del polinomio: {grado} Por el TFA podremos tener {grado} raices totales como maximo")

    # calculamos la cantidad de variaciones positivas para x > 0 sin ceros
    L_coefi = [c for c in polinomio.all_coeffs() if c != 0] #lista de coeficientes ignorando nulos
    cant_pos = sum(1 for i in range(len(L_coefi) - 1) if L_coefi[i] * L_coefi[i + 1] < 0)
    raices_pos = [cant_pos - 2 * k for k in range((cant_pos // 2) + 1)] #cant de raices teniendo en cuenta conjugadas 

    # Coeficientes para x < 0 evaluando P(-x) para ello convertimos la funcion y obtengo el polneg
    pol_neg = sp.Poly(fx.subs(x, -x), x)
    L_neg = [c for c in pol_neg.all_coeffs() if c != 0]
    #calculamos la cantidad de variaciones negativas
    cant_neg = sum(1 for i in range(len(L_neg) - 1) if L_neg[i] * L_neg[i + 1] < 0)
    raices_neg = [cant_neg - 2 * k for k in range(cant_neg // 2 + 1)]

    print(f"Variaciones signo x > 0: {cant_pos} -> Por la Regla tendremos {raices_pos} posibles raices positivas Reales")
    print(f"Variaciones signo x < 0: {cant_neg} -> Por la Regla tendremos {raices_neg} posibles raices negativas Reales")
    print("-" * 50)

    max_p = max(raices_pos) if raices_pos else 0
    max_n = max(raices_neg) if raices_neg else 0
    return max_p, max_n

#Tanteo nos permite aislar las raices en intervalos a partir de Bolzano: f(a)*f(b) < 0
def barrido_tanteo(fx, x_ini=0.0, sentido="positiva", max_r=1, paso=0.5, x_max=50.0):

    intervalos = []
    dx = abs(paso) if sentido == "positiva" else -abs(paso)
    x_actual = float(x_ini)

    try:
        fx_ant = fx(x_actual)
        #condicion para cuando cae sobre la raiz el tanteo en la primera iteracion
        if abs(fx_ant) < 1e-12:
            intervalos.append((round(x_actual, 4), round(x_actual, 4)))
            fx_ant = 0.0
    except Exception:
        print(f"Error al evaluar f(x) en el inicio: {x_actual } revisar valores ingresados")
        return intervalos

    pasos = 0
    limite = int(x_max / abs(paso)) # calculo la cant de pasos que puedo dar o mi cota de parada

    while len(intervalos) < max_r and pasos < limite:
        x_sig = x_actual + dx
        try:
            fx_sig = fx(x_sig)
            if abs(fx_sig) < 1e-12: #condicion para cuando cae sobre la raiz el tanteo
                intervalos.append((round(x_sig, 4), round(x_sig, 4)))
                fx_sig = 0.0
             #verifico que el termino anterior no sea 0(raiz) par que no de falso pos(no busque en el intervalo ese) y cumpla con bolzano
            elif abs(fx_ant) >= 1e-12 and (fx_ant * fx_sig < 0):
                #[a,b]
                a_min = min(x_actual, x_sig) 
                b_max = max(x_actual, x_sig) 
                intervalos.append((round(a_min, 4), round(b_max, 4)))
            
        except Exception:
            break
        #actualizo info 
        x_actual = x_sig
        fx_ant = fx_sig
        pasos += 1

    return intervalos


def graficar_curva(fn, a_vis, b_vis, intervalos=None, raices=None, titulo="Grafico de la funcion"):
    xs = np.linspace(a_vis, b_vis, 600)
    try:    
        ys = [fn(pt) for pt in xs]
    except:
        print("No se pudo armar el grafico.")
        return

    plt.figure(figsize=(9, 5))
    plt.plot(xs, ys, "b-", label="f(x)")
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8)
    plt.axvline(0, color="black", linestyle="--", linewidth=0.8)

    #grafica los intervalos
    if intervalos:
        for idx, (a, b) in enumerate(intervalos):
            lbl = "Intervalo tanteo" if idx == 0 else ""
            #si el intervalo tiene ancho 0 es decir a==b en tanteo cayo en el punto exacto sobre la raiz
            if abs(b-a) < 1e-6:
                #dibujo una linea vertical 
                plt.axvline(
                    a,color="orange", linestyle="-.", linewidth=1.5, label=lbl
                )
            else:
                #sino sombreo el area del intervalo de tanteo
                plt.axvspan(a, b, color="orange", alpha=0.3, label=lbl)
                
    #grafica las raices
    if raices:
        for idx, r in enumerate(raices):
            lbl = "Raiz aproximada" if idx == 0 else ""
            plt.plot(r, fn(r), "ro", markersize=6, label=lbl)
            plt.text(r, fn(r), f"  r={r:.4f}", color="darkred")

    plt.title(titulo)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True, linestyle=":")
    plt.legend()
    plt.show()
    
###############         METODOS PARA CALCULAR RAICES       ##############


# INTERVALO MEDIO
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



# Condiciones de fourier 
def chequear_condiciones_raphson(fn, d1, d2, d1_simb, x, a, b):
    """
    Esta funcion permite verificar las 3 condiciones de newton para asegurar convergencia
    1. Bolzano: f(a)*f(b) < 0 (suficiente)
    2. Monotonia: f'(x) != 0 en (a, b) (no necesaria)
    3. Fourier: f(x0)*f''(x0) > 0 para elegir x0 (suficiente)
    """
    print(f"\n--- Verificamos condiciones en el intervalo [{a:.4f} ; {b:.4f}] ---")
    fa = fn(a)
    fb = fn(b)

    # 1. Bolzano
    if fa * fb >= 0:
        print(" [X] No cumple T. Bolzano ,NO hay cambio de signo.")
        return None
    print(" [OK] Cumple T. Bolzano (Condicion 1)")

    # 2. Monotonia (derivada no nula)
    try:
        pts = sp.solve(d1_simb, x)
        criticos = [float(p.evalf()) for p in pts if p.is_real and a <= float(p.evalf()) <= b]
        if criticos:
            print(f"[!] No cumple monotonia, Puntos criticos en {criticos}")
        else:
            print(" [OK] Cumple monotonia(Condicion II): f'(x) != 0 en el intervalo.")
    except Exception:
        if d1(a) * d1(b) > 0:
            print(" [OK] Condicion II (Monotonia): La 1ra derivada tiene mismo signo en bordes [a,b].")
        else:
            print(" [!] La 1ra derivada: f' cambia de signo en los bordes")

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
        print(f" [!] Ningun borde cumple f*f''>0. Se toma x0 = {x0:.4f} se toma el valor abs del menor valor")
        return x0

#Metodo NEWTON-RAPHSON 
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
         # corte por tolerancia
        if err < tol or abs(fx) < tol:
            t_total = time.perf_counter() - t_ini
            print(f"Convergencia alcanzada en {k + 1} iteraciones.")
            return x_sig, k + 1, err, True, t_total

        x_val = x_sig

    t_total = time.perf_counter() - t_ini
    return x_val, max_iter, err, False, t_total



# ITERACIÓN Y ACELERACIÓN DE AITKEN
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

