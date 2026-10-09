import sympy as sp
from metodos_lab3 import (
    chequear_condiciones_raphson, 
    metodo_newton_raphson, 
    graficar_curva
)

x = sp.Symbol('x')
P_simb = 8*x + 0.3*x**2 - 0.0013*x**3 - 372
d1_simb = sp.diff(P_simb, x)
d2_simb = sp.diff(P_simb, x, 2)

fn = sp.lambdify(x, P_simb, "math")
d1 = sp.lambdify(x, d1_simb, "math")
d2 = sp.lambdify(x, d2_simb, "math")

intervalos = [(24.0, 26.0), (250.0, 252.0)]
raices = []

print("--- EJERCICIO 2: PUNTOS DE EQUILIBRIO CON NEWTON-RAPHSON ---")
for idx, (a, b) in enumerate(intervalos, 1):
    x0 = chequear_condiciones_raphson(fn, d1, d2, d1_simb, x, a, b)
    if x0 is not None:
        r, k, err, ok, t = metodo_newton_raphson(fn, d1, x0, tol=1e-3)
        if ok:
            raices.append(r)
            print(f">> Raiz {idx} aproximada: {r:.4f} impresoras (Tiempo: {t:.6f} s)")

graficar_curva(fn, 0, 300, intervalos=intervalos, raices=raices, titulo="Puntos de Equilibrio P(x)")