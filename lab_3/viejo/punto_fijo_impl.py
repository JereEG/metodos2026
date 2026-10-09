import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import time


def aceleracion_aitken(x0, x1, x2):
    """
    Aplica la aceleración de Aitken para mejorar la convergencia

    Fórmula: x_acelerado = x0 - (x1 - x0)**2 / (x2 - 2*x1 + x0)
    """
    denominador = x2 - 2*x1 + x0
    # Evitar división por cero
    if abs(denominador) < 1e-14:
        return x2
    return x0 - (x1 - x0)**2 / denominador


def metodo_punto_fijo(func_g, x0, tolerancia=1e-6, max_iter=100, usar_aitken=False):
    """
    Método de Iteración de Punto Fijo con opción de Aceleración de Aitken

    Parámetros:
    - func_g: función g(x) tal que x = g(x) (callable)
    - x0: estimación inicial
    - tolerancia: precisión deseada
    - max_iter: número máximo de iteraciones
    - usar_aitken: True para aplicar aceleración de Aitken
    """
    tiempo_inicio = time.time()

    historial = []
    x = x0

    # Encabezado de la tabla
    if usar_aitken:
        print(f"{'Iter':>4} | {'x':>12} | {'g(x)':>12} | {'x_Aitken':>12} | {'Error':>10}")
        print("-" * 65)
    else:
        print(f"{'Iter':>4} | {'x':>12} | {'g(x)':>12} | {'Error':>10}")
        print("-" * 50)

    # Variables para Aitken (necesitamos 3 puntos consecutivos)
    valores_aitken = []  # Almacena x0, x1, x2 para aplicar Aitken

    for i in range(max_iter):
        try:
            gx = func_g(x)
        except Exception as e:
            print(f"  ⚠ Error al evaluar g(x) en x = {x}: {e}")
            return x, i, historial

        # Aplicar Aitken solo cada 3 iteraciones
        x_aitken = None
        aplicar_aitken = False

        if usar_aitken:
            valores_aitken.append(x)

            # Aplicar Aitken cuando tengamos 3 valores consecutivos
            if len(valores_aitken) == 3:
                x_aitken = aceleracion_aitken(valores_aitken[0], valores_aitken[1], valores_aitken[2])
                aplicar_aitken = True
                # calcular error relativo al último x almacenado
                error = abs(x_aitken - x)
                x_siguiente = x_aitken
                valores_aitken = []  # Reiniciar para próxima aplicación de Aitken
            else:
                error = abs(gx - x)
                x_siguiente = gx
        else:
            error = abs(gx - x)
            x_siguiente = gx

        # Guardar en historial
        historial.append({
            'iteracion': i + 1,
            'x': x,
            'gx': gx,
            'x_aitken': x_aitken,
            'error': error,
            'x_siguiente': x_siguiente
        })

        # Mostrar resultados
        if usar_aitken and aplicar_aitken:
            print(f"{i+1:4} | {x:12.8f} | {gx:12.8f} | {x_aitken:12.8f} | {error:10.8f}")
        elif usar_aitken:
            print(f"{i+1:4} | {x:12.8f} | {gx:12.8f} | {'N/A':>12} | {error:10.8f}")
        else:
            print(f"{i+1:4} | {x:12.8f} | {gx:12.8f} | {error:10.8f}")

        # Verificar convergencia
        if error < tolerancia:
            tiempo_total = time.time() - tiempo_inicio
            print(f"\nConvergencia alcanzada en {i+1} iteraciones")
            metodo = "Punto Fijo con Aitken" if usar_aitken else "Punto Fijo"
            print(f"Método usado: {metodo}")
            print(f"Tiempo de ejecución: {tiempo_total:.6f} segundos")
            return x_siguiente, i + 1, historial

        # Actualizar x para siguiente iteración
        x = x_siguiente

    tiempo_total = time.time() - tiempo_inicio
    print(f"\nMáximo de iteraciones alcanzado")
    metodo = "Punto Fijo con Aitken" if usar_aitken else "Punto Fijo"
    print(f"Método usado: {metodo}")
    print(f"Tiempo de ejecución: {tiempo_total:.6f} segundos")
    return x, max_iter, historial


def metodo_tanteo(func, x_min=-10, x_max=10, paso=0.5):
    """
    Encuentra intervalos donde se encuentran las raíces de una función usando el método de tanteo.
    """
    intervalos = []
    x = x_min

    try:
        f_anterior = func(x)
    except Exception as e:
        print(f"Error al evaluar la función en x = {x}: {e}")
        return intervalos

    print(f"{'x':>8} | {'f(x)':>12} | {'Cambio de signo':>15}")
    print("-" * 40)
    print(f"{x:8.2f} | {f_anterior:12.4f} |")

    x += paso

    while x <= x_max + 1e-12:
        try:
            f_actual = func(x)

            # Verificar cambio de signo (teorema de Bolzano)
            if f_anterior * f_actual < 0:
                intervalos.append((x - paso, x))
                print(f"{x:8.2f} | {f_actual:12.4f} | *** [{x-paso:.2f}, {x:.2f}]")
            else:
                print(f"{x:8.2f} | {f_actual:12.4f} |")

            f_anterior = f_actual
            x += paso

        except Exception as e:
            print(f"Error al evaluar la función en x = {x}: {e}")
            x += paso
            continue

    return intervalos



def graficar_funcion_con_intervalos(func, intervalos, x_min=-10, x_max=10):
    """
    Grafica la función y marca los intervalos donde se encuentran las raíces.
    """
    x = np.linspace(x_min, x_max, 1000)

    try:
        y = [func(xi) for xi in x]
    except Exception as e:
        print(f"Error al generar la gráfica: {e}")
        return

    plt.figure(figsize=(12, 8))
    plt.plot(x, y, 'b-', linewidth=2, label='f(x)')
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.axvline(x=0, color='k', linestyle='--', alpha=0.5)


    for i, (a, b) in enumerate(intervalos):
        plt.axvspan(a, b, alpha=0.3, color='red', 
                   label=f'Intervalo {i+1}: [{a:.2f}, {b:.2f}]' if i == 0 else "")
        if i > 0:
            plt.axvspan(a, b, alpha=0.3, color='red')

    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Función con intervalos que contienen raíces')
    plt.legend()
    plt.show(block=False)



def solicitar_parametros():
    """Solicita todos los parámetros necesarios al usuario y devuelve funciones + objetos sympy.

    Retorna: f_callable, f_sympy, g_callable, g_sympy, f_str, g_str, x_min, x_max, paso, tolerancia, max_iter
    """
    print("=== CONFIGURACIÓN DEL MÉTODO DE TANTEO CON PUNTO FIJO ===")

    # Solicitar función original
    f_str = input("Ingrese la función f(x): ")

    # Convertir a funciones Python y simbólicas
    try:
        x = sp.Symbol("x")
        f_sympy = sp.sympify(f_str)
        f = sp.lambdify(x, f_sympy, "math")

        print(f"Función f(x) = {f_str}")

    except Exception as e:
        print(f"⚠ Error al procesar la función: {e}")
        return None

    # Solicitar función g(x) para punto fijo
    print("\n=== CONFIGURACIÓN DE PUNTO FIJO ===")
    print("Para resolver f(x) = 0 con punto fijo, necesita reescribir como x = g(x)")
    print("Ejemplos de transformaciones:")
    print("  • f(x) = x² - 3 → g(x) = √3 (para x > 0) o g(x) = x - (x² - 3)")
    print("  • f(x) = x - cos(x) → g(x) = cos(x)")
    print("  • f(x) = x² - x - 1 → g(x) = x + 1/x (para x ≠ 0)")

    g_str = input("\nIngrese la función g(x) tal que x = g(x): ")

    try:
        g_sympy = sp.sympify(g_str)
        g = sp.lambdify(x, g_sympy, "math")
        print(f"Función g(x) = {g_str}")

    except Exception as e:
        print(f"⚠ Error al procesar la función g(x): {e}")
        return None

    # Solicitar parámetros del tanteo
    print("\n=== PARÁMETROS DEL TANTEO ===")
    try:
        x_min = float(input("Ingrese el límite inferior del intervalo de tanteo: "))
        x_max = float(input("Ingrese el límite superior del intervalo de tanteo: "))
        paso = float(input("Ingrese el tamaño del paso para el tanteo: "))

        if x_min >= x_max:
            print("⚠ El límite inferior debe ser menor que el superior")
            return None

        if paso <= 0:
            print("⚠ El paso debe ser positivo")
            return None

    except ValueError:
        print("⚠ Error en los parámetros del tanteo")
        return None

    # Solicitar parámetros de Punto Fijo
    print("\n=== PARÁMETROS DE PUNTO FIJO ===")
    tolerancia_input = input("Ingrese la tolerancia (presione Enter para usar 1e-6): ").strip()
    if tolerancia_input == "":
        tolerancia = 1e-6
    else:
        try:
            tolerancia = float(tolerancia_input)
        except ValueError:
            print("⚠ Valor inválido para tolerancia. Usando 1e-6 por defecto.")
            tolerancia = 1e-6

    max_iter_input = input("Ingrese el máximo de iteraciones (presione Enter para usar 100): ").strip()
    if max_iter_input == "":
        max_iter = 100
    else:
        try:
            max_iter = int(max_iter_input)
            if max_iter <= 0:
                print("⚠ El máximo de iteraciones debe ser positivo. Usando 100 por defecto.")
                max_iter = 100
        except ValueError:
            print("⚠ Valor inválido para máximo de iteraciones. Usando 100 por defecto.")
            max_iter = 100

    return f, f_sympy, g, g_sympy, f_str, g_str, x_min, x_max, paso, tolerancia, max_iter


def seleccionar_x0_punto_fijo(func_f, func_g, a, b):
    """
    Selecciona x0 para punto fijo basado en criterios de convergencia
    """
    try:
        fa = func_f(a)
        fb = func_f(b)

        print(f"  f({a:.2f}) = {fa:.6f}")
        print(f"  f({b:.2f}) = {fb:.6f}")

        # Verificar condición de Bolzano para f(x)
        if fa * fb > 0:
            print(f"  ⚠ No se cumple la condición de Bolzano en [{a:.2f}, {b:.2f}]")
            return None, fa, fb

        # Para punto fijo, elegir el punto más cercano al centro del intervalo
        # o el que tenga menor valor absoluto de f(x)
        centro = (a + b) / 2

        # Evaluar g(x) en algunos puntos para verificar que esté bien definida
        try:
            ga = func_g(a)
            gb = func_g(b)
            gc = func_g(centro)

            print(f"  g({a:.2f}) = {ga:.6f}")
            print(f"  g({centro:.2f}) = {gc:.6f}")
            print(f"  g({b:.2f}) = {gb:.6f}")

        except Exception as e:
            print(f"  ⚠ Error al evaluar g(x): {e}")
            return None, fa, fb

        # Seleccionar x0 (preferir el centro o el punto con menor |f(x)|)
        if abs(fa) < abs(fb):
            x0 = a
            print(f"  ✓ Seleccionado x0 = {x0:.2f} (menor |f(x)|)")
        else:
            x0 = b
            print(f"  ✓ Seleccionado x0 = {x0:.2f} (menor |f(x)|)")

        return x0, fa, fb

    except Exception as e:
        print(f"  ⚠ Error al evaluar las funciones: {e}")
        return None, None, None



def graficar_comparacion_metodos(func_g, func_f, x0, tolerancia, max_iter, intervalo):
    """
    Grafica la comparación entre punto fijo simple y con Aitken
    """
    print("\n=== COMPARACIÓN: PUNTO FIJO SIMPLE vs AITKEN ===")

    # Ejecutar ambos métodos
    print("\n--- Método de Punto Fijo Simple ---")
    sol_simple, iter_simple, hist_simple = metodo_punto_fijo(func_g, x0, tolerancia, max_iter, usar_aitken=False)

    print("\n--- Método de Punto Fijo con Aitken ---")
    sol_aitken, iter_aitken, hist_aitken = metodo_punto_fijo(func_g, x0, tolerancia, max_iter, usar_aitken=True)

    # Crear gráfico de comparación
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Gráfico 1: Funciones f(x) y g(x)
        a, b = intervalo
        x_vals = np.linspace(a - 0.5, b + 0.5, 1000)

        try:
            g_vals = [func_g(x) for x in x_vals]
            f_vals = [func_f(x) for x in x_vals]

            ax1.plot(x_vals, g_vals, 'b-', label='g(x)', linewidth=2)
            ax1.plot(x_vals, x_vals, 'r--', label='y = x', linewidth=1)
            ax1.plot(x_vals, f_vals, 'g-', label='f(x)', alpha=0.7)

            # Marcar puntos importantes (si las soluciones existen)
            try:
                ax1.plot(sol_simple, sol_simple, 'ro', markersize=8, label=f'Punto Fijo Simple ({sol_simple:.4f})')
            except:
                pass
            try:
                ax1.plot(sol_aitken, sol_aitken, 'mo', markersize=8, label=f'Punto Fijo + Aitken ({sol_aitken:.4f})')
            except:
                pass
            ax1.plot(x0, func_g(x0), 'ko', markersize=6, label=f'x₀ = {x0:.4f}')

            ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)

            ax1.set_xlabel('x')
            ax1.set_ylabel('y')
            ax1.set_title('Método de Punto Fijo: g(x) vs y = x')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

        except Exception as e:
            ax1.text(0.5, 0.5, f'Error al graficar: {str(e)}', 
                    transform=ax1.transAxes, ha='center', va='center')

        # Gráfico 2: Convergencia
        iter_simple_range = range(1, len(hist_simple) + 1)
        iter_aitken_range = range(1, len(hist_aitken) + 1)

        errores_simple = [h['error'] for h in hist_simple]
        errores_aitken = [h['error'] for h in hist_aitken]

        ax2.semilogy(iter_simple_range, errores_simple, 'b-o', 
                    label=f'Punto Fijo Simple ({len(hist_simple)} iter)', linewidth=2, markersize=4)
        ax2.semilogy(iter_aitken_range, errores_aitken, 'r-s', 
                    label=f'Punto Fijo + Aitken ({len(hist_aitken)} iter)', linewidth=2, markersize=4)

        ax2.axhline(y=tolerancia, color='k', linestyle='--', alpha=0.5, label=f'Tolerancia ({tolerancia})')
        ax2.set_xlabel('Iteración')
        ax2.set_ylabel('Error (escala log)')
        ax2.set_title('Comparación de Convergencia')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        plt.show(block=False)

        # Resumen de resultados
        print(f"\n=== RESUMEN DE RESULTADOS ===")
        if hist_simple:
            print(f"Método Simple:")
            print(f"  - Solución: {sol_simple:.10f}")
            print(f"  - Iteraciones: {len(hist_simple)}")
            print(f"  - Error final: {hist_simple[-1]['error']:.2e}")
            print(f"  - f(x) = {func_f(sol_simple):.2e}")
        if hist_aitken:
            print(f"\nMétodo con Aitken:")
            print(f"  - Solución: {sol_aitken:.10f}")
            print(f"  - Iteraciones: {len(hist_aitken)}")
            print(f"  - Error final: {hist_aitken[-1]['error']:.2e}")
            print(f"  - f(x) = {func_f(sol_aitken):.2e}")

        if len(hist_aitken) and len(hist_simple):
            if len(hist_aitken) < len(hist_simple):
                mejora = ((len(hist_simple) - len(hist_aitken)) / len(hist_simple)) * 100
                print(f"\nAitken mejoró la convergencia en {mejora:.1f}% ({len(hist_simple) - len(hist_aitken)} iteraciones menos)")
            elif len(hist_simple) < len(hist_aitken):
                print(f"\nEl método simple fue más eficiente en este caso")
            else:
                print(f"\nAmbos métodos requirieron el mismo número de iteraciones")

    except Exception as e:
        print(f"Error al crear gráficos: {e}")
        print("Continuando sin visualización...")


def verificar_condicion_fourier(g_sympy, a, b, puntos=200):
    """
    Verifica la condición de Fourier |g'(x)| < 1 en el intervalo [a, b].
    Devuelve (cumple_bool, max_valor) y no lanza excepción si hay problemas.
    """
    x = sp.Symbol('x')
    try:
        # Si recibimos una cadena, convertir
        if isinstance(g_sympy, str):
            g_expr = sp.sympify(g_sympy)
        else:
            g_expr = g_sympy

        g_deriv = sp.diff(g_expr, x)
        gprime = sp.lambdify(x, g_deriv, 'math')

        xs = np.linspace(a, b, puntos)
        vals = []
        for xi in xs:
            try:
                v = gprime(xi)
                if np.isfinite(v):
                    vals.append(abs(v))
            except Exception:
                # si falla en un punto lo ignoramos (ej. raíz par en denom)
                continue

        if not vals:
            return False, None

        max_val = max(vals)
        return (max_val < 1), max_val

    except Exception as e:
        # Ante cualquier error devolvemos False
        return False, None


def main():
    """Función principal que ejecuta todo el proceso"""

    # Solicitar parámetros
    salida = solicitar_parametros()
    if salida is None:
        print("⚠ Error en la configuración. Terminando programa.")
        return

    f, f_sympy, g, g_sympy, f_str, g_str, x_min, x_max, paso, tolerancia, max_iter = salida

    print(f"\n=== CONFIGURACIÓN FINAL ===")
    print(f"Intervalo de tanteo: [{x_min}, {x_max}]")
    print(f"Paso: {paso}")
    print(f"Tolerancia: {tolerancia}")
    print(f"Máx. iteraciones: {max_iter}")

    # Realizar tanteo
    print(f"\n=== MÉTODO DE TANTEO ===")
    intervalos = metodo_tanteo(f, x_min, x_max, paso)

    if not intervalos:
        print("\n⚠ No se encontraron intervalos con cambio de signo.")
        return

    print(f"\n✓ Se encontraron {len(intervalos)} intervalos con posibles raíces:")
    for i, (a, b) in enumerate(intervalos, 1):
        print(f"  Intervalo {i}: [{a:.2f}, {b:.2f}]")

    # Mostrar gráfica del tanteo
    mostrar_grafico = input("\n¿Desea mostrar la gráfica del tanteo? (s/n, Enter=sí): ").strip().lower()
    if mostrar_grafico in ['', 's', 'si', 'sí', 'y', 'yes']:
        graficar_funcion_con_intervalos(f, intervalos, x_min, x_max)
        print("📊 Gráfico del tanteo mostrado.")

    # Aplicar Punto Fijo a cada intervalo
    print(f"\n=== APLICANDO MÉTODO DE PUNTO FIJO ===")

    for i, (a, b) in enumerate(intervalos, 1):
        print(f"\n{'='*50}")
        print(f"INTERVALO {i}: [{a:.2f}, {b:.2f}]")
        print(f"{'='*50}")

        # Verificar condición de Fourier para g en el intervalo
        cumple, max_gprime = verificar_condicion_fourier(g_sympy, a, b)
        if max_gprime is None:
            print("  ⚠ No fue posible evaluar |g'(x)| en el intervalo (posibles singularidades).")
        else:
            print(f"  Máx |g'(x)| aproximado en [{a:.2f}, {b:.2f}] = {max_gprime:.6f}")

        if not cumple:
            print(f"  ❌ ALERTA: g(x) NO cumple la condición de Fourier en [{a:.2f}, {b:.2f}]")
            print("     → El método de punto fijo podría no converger aquí. Saltando intervalo.")
            continue

        # Seleccionar x0
        x0, fa, fb = seleccionar_x0_punto_fijo(f, g, a, b)

        if x0 is None:
            print("  Saltando este intervalo...")
            continue

        try:
            # Preguntar si quiere comparación de métodos
            comparar = input(f"\n¿Desea comparar Punto Fijo simple vs Aitken para este intervalo? (s/n, Enter=sí): ").strip().lower()

            if comparar in ['', 's', 'si', 'sí', 'y', 'yes']:
                graficar_comparacion_metodos(g, f, x0, tolerancia, max_iter, (a, b))
            else:
                # Solo ejecutar punto fijo simple
                print(f"\n=== MÉTODO DE PUNTO FIJO ===")
                print(f"Intervalo: [{a:.6f}, {b:.6f}]")
                print(f"x₀ = {x0:.6f}")
                print(f"Tolerancia = {tolerancia}")
                print(f"Máx. iteraciones = {max_iter}")
                print()

                raiz, iteraciones, historial = metodo_punto_fijo(g, x0, tolerancia, max_iter, usar_aitken=False)

                # Resultados finales (si hay historial)
                if historial:
                    print(f"\n📊 RESULTADOS FINALES:")
                    print(f"   Raíz aproximada: x = {raiz:.8f}")
                    try:
                        print(f"   f(x) = {f(raiz):.8e}")
                    except Exception:
                        pass
                    try:
                        print(f"   g(x) = {g(raiz):.8f}")
                    except Exception:
                        pass
                    print(f"   Iteraciones: {iteraciones}")
                    print(f"   Error final: {historial[-1]['error']:.8e}")
                else:
                    print("   ⚠ No se registraron iteraciones (error en la ejecución).")

        except Exception as e:
            print(f"  ⚠ Error durante Punto Fijo: {e}")
            continue


if __name__ == "__main__":
    main()
    input("Presioná Enter para salir...")
