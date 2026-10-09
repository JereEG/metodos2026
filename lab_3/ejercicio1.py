import math
from metodos_lab3 import (
    barrido_tanteo, 
    metodo_intervalo_medio, 
    metodo_interpolacion_lineal, 
    graficar_curva
)

# Definición del problema
R = 3.0
V = 30.0
fn = lambda h: math.pi * (h**2) * ((3 * R - h) / 3.0) - V

print("--- EJERCICIO 1: TANQUE ESFERICO ---")
# 1. Grafico previo en [0, 2R] (h debe estar entre 0 y el diametro 6m)
graficar_curva(fn, 0, 6, titulo="f(h) - Nivel del Tanque")

# 2. Tanteo
paso = float(input("Ingrese el paso para el tanteo (ej: 0.5): ") or 0.5)
intervalos = barrido_tanteo(fn, x_ini=0.0, sentido="positiva", max_r=1, paso=paso, x_max=6.0)
print("Intervalos hallados:", intervalos)

if intervalos:
    a, b = intervalos[0]
    tol = 0.001

    # 3. Intervalo Medio
    r_im, it_im, err_im, t_im = metodo_intervalo_medio(fn, a, b, tol)
    print(f"\n[Intervalo Medio]      Raiz: {r_im:.4f} m | Iter: {it_im} | Error: {err_im:.2e} | Tiempo: {t_im:.6f} s")

    # 4. Interpolacion Lineal
    r_il, it_il, err_il, t_il = metodo_interpolacion_lineal(fn, a, b, tol)
    print(f"[Interpolacion Lineal] Raiz: {r_il:.4f} m | Iter: {it_il} | Error: {err_il:.2e} | Tiempo: {t_il:.6f} s")