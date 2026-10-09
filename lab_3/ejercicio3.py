import math
import numpy as np
import matplotlib.pyplot as plt
from metodos_lab3 import metodo_iteracion

# 1. Definición analítica del problema
# g(x) para iteración y f(x) = 5x - A - 1000 para verificar residuos
def g(x):
    return 200.0 + 40.0 * math.log(400.0 / (500.0 - x))

def g_prima(x):
    return 40.0 / (500.0 - x)

def f_residuo(x):
    return 5.0 * x - 200.0 * math.log(400.0 / (500.0 - x)) - 1000.0

def main():
    print("=" * 70)
    print("LABORATORIO 3 - EJERCICIO 3: UTILIDAD NETA E ITERACIÓN / AITKEN")
    print("=" * 70)

    x0 = 200.0
    tol = 1e-4

    # 2. Demostración teórica de convergencia
    derivada_x0 = g_prima(x0)
    print(f"\n1. Análisis previo de convergencia en x0 = {x0}:")
    print(f"   g'(x0) = 40 / (500 - {x0}) = {derivada_x0:.6f}")
    if abs(derivada_x0) < 1.0:
        print("   [OK] |g'(x0)| < 1: Cumple la condición de convergencia.")
        tipo_aprox = "Monótona (en Escalera)" if derivada_x0 > 0 else "Oscilatoria (en Espiral)"
        print(f"   Tipo de aproximación geométrica: {tipo_aprox}")
    else:
        print("   [!] |g'(x0)| >= 1: El método diverge. Modifique el despeje.")
        return

    # 3. Inciso a: Método de Iteración Simple (punto fijo)
    print("\n" + "=" * 70)
    print("INCISO A: MÉTODO DE ITERACIÓN SIMPLE (E < 1e-4)")
    r_simple, it_simple, err_simple, t_simple = metodo_iteracion(
        g_fn=g, 
        x0=x0, 
        tol=tol, 
        max_iter=50, 
        usar_aitken=False
    )
    print(f">> Raíz aproximada: x ≈ {r_simple:.6f} unidades")
    print(f">> Iteraciones requeridas: {it_simple}")
    print(f">> Error relativo final: {err_simple:.4e}")
    print(f">> Tiempo de ejecución: {t_simple:.6f} segundos")
    print(f">> Residuo f(raiz): {f_residuo(r_simple):.4e}")

    # 4. Inciso b: Método de Iteración con Aceleración de Aitken
    print("\n" + "=" * 70)
    print("INCISO B: ITERACIÓN CON ACELERACIÓN DE AITKEN (E < 1e-4)")
    r_aitken, it_aitken, err_aitken, t_aitken = metodo_iteracion(
        g_fn=g, 
        x0=x0, 
        tol=tol, 
        max_iter=50, 
        usar_aitken=True
    )
    print(f">> Raíz aproximada: x ≈ {r_aitken:.6f} unidades")
    print(f">> Ciclos/Iteraciones Aitken: {it_aitken}")
    print(f">> Error final estimado: {err_aitken:.4e}")
    print(f">> Tiempo de ejecución: {t_aitken:.6f} segundos")
    print(f">> Residuo f(raiz): {f_residuo(r_aitken):.4e}")

    # 5. Comparación y conclusiones
    print("\n" + "-" * 70)
    print("COMPARACIÓN DE EFICIENCIA:")
    print(f"Iteración Simple : {it_simple} iteraciones | {t_simple:.6f} s")
    print(f"Aceleración Aitken: {it_aitken} iteraciones | {t_aitken:.6f} s")
    print(f"Unidades enteras a comercializar: {math.ceil(r_aitken)} unidades")
    print("-" * 70)

    # 6. Gráfico de Punto Fijo: y = x vs y = g(x)
    xs = np.linspace(190, 230, 400)
    ys_g = [g(val) for val in xs]

    plt.figure(figsize=(9, 5))
    plt.plot(xs, xs, "k--", label="y = x (Bisectriz)")
    plt.plot(xs, ys_g, "b-", label="y = g(x)")
    plt.plot(r_aitken, g(r_aitken), "ro", markersize=7, label=f"Raíz x ≈ {r_aitken:.2f}")
    plt.title("Método de Punto Fijo: Intersección y = x con y = g(x)")
    plt.xlabel("x (unidades)")
    plt.ylabel("y")
    plt.grid(True, linestyle=":")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()