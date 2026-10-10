import sympy as sp
from metodos_lab3 import (
    regla_descartes,
    barrido_tanteo,
    metodo_interpolacion_lineal, 
    graficar_curva
)

x = sp.Symbol('x') # defino la incognita
entrada = input("\nIngrese f(x) (ej: x**3 - 6*x**2 + 11*x - 6.1): ").strip()
try:
    f_simb = sp.sympify(entrada)
    # Creamos la funcion para evaluar rapido
    fn = sp.lambdify(x, f_simb, "math")
except Exception as e:
    raise ValueError("Error con la funcion ingresada:", e)

# verifico que sea un polinomio sino descarte da error 
if not f_simb.is_polynomial(x):
    raise ValueError("\nError: La función ingresada no es un polinomio. El programa solo admite polinomios.")

# Analisis previo con descartes
max_p, max_n = regla_descartes(f_simb, x)

print("\n--- CONFIGURACION DE LA BUSQUEDA ---")
tipo = input("Buscar raices positivas, negativas o todas? [p/n/t] (defecto 't'): ").strip().lower()
if tipo == 'n':
    sentido = "negativa"
    lim_raices = max_n
elif tipo == 'p':
    sentido = "positiva"
    lim_raices = max_p
else:
    sentido = "todas"
    lim_raices = (max_p, max_n)

val_ini = input("Punto de inicio del tanteo (defecto 0.0): ").strip()
x_inicio = float(val_ini) if val_ini != "" else 0.0

val_lim = input("Limite maximo a recorrer (defecto 50): ").strip()
x_limite = float(val_lim) if val_lim != "" else 50.0

val_paso = input("Paso deltax para el tanteo (defecto 0.5): ").strip()
paso = float(val_paso) if val_paso != "" else 0.5

val_tol = input("Tolerancia o cota de error (defecto 1e-5): ").strip()
tol = float(val_tol) if val_tol != "" else 1e-5

# TANTEO
print(f"\nBuscando intervalos en sentido {sentido} desde x = {x_inicio}...")
intervalos = barrido_tanteo(fn, x_inicio, sentido, lim_raices, paso, x_limite)

if not intervalos:
    print("No se encontraron cambios de signo en ese rango.")
else:
    print("\nIntervalos encontrados:")
    for i, (a, b) in enumerate(intervalos, 1):
        print(f"  Intervalo {i}: [{round(a, 4)} ; {round(b, 4)}]")
        
    # Aplicación de Interpolacion Lineal sobre cada intervalo
    raices_halladas = []
    puntos_x = [x_inicio]

    for i, (a, b) in enumerate(intervalos, 1):
        puntos_x.extend([a, b])

        # Si el intervalo es un punto exacto encontrado en tanteo (a == b)
        if abs(b - a) < 1e-6:
            print(f"\n>> Raíz exacta encontrada en tanteo: x = {a:.6f}")
            raices_halladas.append(a)
            puntos_x.append(a)
            continue

        # Llamado al método de interpolación lineal (Regula Falsi)
        # metodo_interpolacion_lineal devuelve x_sig, iteraciones, err, t_total
        try:
            r, k, err, t_ejec = metodo_interpolacion_lineal(fn, a, b, tol=tol)
            raices_halladas.append(r)
            puntos_x.append(r)
            print(f"La Raíz num {i} aproximada es : x = {round(r, 6)} en {k} iteraciones (Tiempo: {t_ejec:.6f} s)")
            print(f"Su imagen : f({round(r, 6)}) = {format(fn(r), '.4e')}")
        except ValueError as ve:
            print(f"Saltando intervalo {i} por error: {ve}")

    # GRAFICO LA FUNCION Y ABRO EL GRAFICO
    if len(raices_halladas) > 0:
        print("\nAbriendo gráfico...")
        # Margen 
        ancho = max(puntos_x) - min(puntos_x)
        margen = max(ancho * 0.15, 1.0)
        a_vis = min(puntos_x) - margen
        b_vis = max(puntos_x) + margen

        graficar_curva(
            fn,
            a_vis,
            b_vis,
            intervalos=intervalos,
            raices=raices_halladas,
            titulo=f"Interpolación Lineal: f(x) = {entrada}",
        )
