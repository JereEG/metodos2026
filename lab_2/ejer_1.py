import math#importamos la libreria math para poder usar las instrucciones matematicas

import time

#obtiene el error absoluto,relativo y porcentual de los casos definidos
def calcular_errores(p, p_aprox):
    t_ini = time.perf_counter()
    
    e_a = abs(p - p_aprox)
    e_r = e_a / abs(p)
    e_p = e_r * 100
    
    tiempo = time.perf_counter() - t_ini
    return e_a, e_r, e_p, tiempo

def main():
    casos = [
        ("a", "p = π, p* = 22/7", math.pi, 22 / 7),
        ("b", "p = π, p* = 3.1416", math.pi, 3.1416),
        ("c", "p = e, p* = 2.718", math.e, 2.718),
        ("d", "p = √2, p* = 1.414", math.sqrt(2), 1.414),
        ("e", "p = e^10, p* = 22000", math.exp(10), 22000),
        ("f", "p = 8!, p* = 39900", math.factorial(8), 39900),
    ]

    print(f"{'Caso':<5} | {'p (Exacto)':<15} | {'p* (Aprox)':<15} | {'Error Absoluto':<16} | {'Error Relativo':<16} | {'Error Porcentual (%)':<20} | {'Tiempo (s)'}")
    print("-" * 115)

    for item, desc, p, p_aprox in casos:
        ea, er, ep, t_ejec = calcular_errores(p, p_aprox)
        print(f"{item:<5} | {p:<15.7g} | {p_aprox:<15.7g} | {ea:<16.6e} | {er:<16.6e} | {ep:<20.4f}% | {t_ejec:<.8f}")

    print("-" * 115)

if __name__ == "__main__":
    main()