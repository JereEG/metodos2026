import sympy as sp
from metodos_lab3 import (
    regla_descartes,
    barrido_tanteo,
    chequear_condiciones_raphson, 
    metodo_newton_raphson, 
    graficar_curva
)

x = sp.Symbol('x') #defino la incognita
entrada = input("\nIngrese f(x) (ej: x**3 - 6*x**2 + 11*x - 6.1): ").strip()
try:
    f_simb = sp.sympify(entrada)
    d1_simb = sp.diff(f_simb, x)
    d2_simb = sp.diff(f_simb, x, 2)

    # creamos las funciones para evaluar rapido
    fn = sp.lambdify(x, f_simb, "math")
    d1 = sp.lambdify(x, d1_simb, "math")
    d2 = sp.lambdify(x, d2_simb, "math")
except Exception as e:
    raise ValueError("Error con la funcion ingresada:", e)

# analisis previo con descartes pedimos lso parametros para la busqueda
max_p, max_n = regla_descartes(f_simb, x)

print("\n--- CONFIGURACION DE LA BUSQUEDA ---")
tipo = input("Buscar raices positivas o negativas? [p/n] (defecto 'p'): ").strip().lower()
sentido = "negativa" if tipo == 'n' else "positiva"
lim_raices = max_n if sentido == "negativa" else max_p

val_ini = input("Punto de inicio del tanteo (defecto 0.0): ").strip()
x_inicio = float(val_ini) if val_ini != "" else 0.0

val_lim = input("Limite maximo a recorrer (defecto 50): ").strip()
x_limite = float(val_lim) if val_lim != "" else 50.0

val_paso = input("Paso deltax para el tanteo (defecto 0.5): ").strip()
paso = float(val_paso) if val_paso != "" else 0.5

val_tol = input("Tolerancia o cota de error (defecto 1e-5): ").strip()
tol = float(val_tol) if val_tol != "" else 1e-5

#TANTEO
print(f"\nBuscando intervalos en sentido {sentido} desde x = {x_inicio}...")
intervalos = barrido_tanteo(fn, x_inicio, sentido, lim_raices, paso, x_limite)

if len(intervalos) == 0:
    print("No se encontraron cambios de signo en ese rango.")

print("\nIntervalos encontrados:")
for i, (a, b) in enumerate(intervalos, 1):
    print(f"  Intervalo {i}: [{round(a, 4)} ; {round(b, 4)}]")
    
#Aplicación de Newton-Raphson sobre cada intervalo
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

    # Chequeo de condiciones de convergencia y selección de x0
    x0 = chequear_condiciones_raphson(fn, d1, d2, d1_simb, x, a, b)
    if x0 is None:
        print(f"Saltando intervalo {i} por no cumplir condiciones.")
        continue

    r, k, err, ok, t_ejec = metodo_newton_raphson(fn, d1, x0, tol=tol)
    if ok:
        raices_halladas.append(r)
        puntos_x.append(r)
        print(f"La Raíz num {i} aproximada es : x = {round(r, 6)} (Tiempo: {t_ejec:.6f} s)")
        print(f"Su imagen : f({round(r, 6)}) = {format(fn(r), '.4e')}")

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
        titulo=f"Newton-Raphson: f(x) = {entrada}",
    )