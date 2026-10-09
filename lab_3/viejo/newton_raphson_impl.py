import sympy as sp
import time
import numpy as np
import matplotlib.pyplot as plt

def metodo_newton_raphson(func, derivada, x0, tolerancia=1e-6, max_iter=100):
    """
    Método de Newton-Raphson
    
    Parámetros:
    - func: función a evaluar
    - derivada: derivada de la función
    - x0: estimación inicial
    - tolerancia: precisión deseada
    - max_iter: número máximo de iteraciones
    """
    tiempo_inicio = time.time()  # Inicia medición de tiempo
    historial = []               # Guarda el progreso de las iteraciones
    x = x0
    
    # Imprimir encabezado de la tabla
    print("\n" + "="*90)
    print(f"{'Iteración':<10} {'x':<15} {'f(x)':<15} {'f\'(x)':<15} {'x_nuevo':<15} {'Error':<15}")
    print("="*90)
    
    for i in range(max_iter):
        fx = func(x)
        fpx = derivada(x)
        
        # Verifica que la derivada no sea demasiado pequeña (evita división por cero)
        if abs(fpx) < 1e-14:
            tiempo_total = time.time() - tiempo_inicio
            print(f"Tiempo de ejecución: {tiempo_total:.6f} segundos")
            raise ValueError(f"Derivada muy pequeña en x = {x}. El método puede no converger.")
        
        # Fórmula principal del método de Newton-Raphson
        x_nuevo = x - fx / fpx
        error = abs(x_nuevo - x)
        
        # Guarda los valores actuales de la iteración
        historial.append({
            'iteracion': i + 1,
            'x': x,
            'fx': fx,
            'fpx': fpx,
            'x_nuevo': x_nuevo,
            'error': error
        })
        
        # Mostrar fila de la tabla
        print(f"{i+1:<10} {x:<15.8f} {fx:<15.8f} {fpx:<15.8f} {x_nuevo:<15.8f} {error:<15.8e}")
        
        # Condición de convergencia
        if error < tolerancia or abs(fx) < tolerancia:
            tiempo_total = time.time() - tiempo_inicio
            print("="*90)
            print(f"\nConvergencia alcanzada en {i+1} iteraciones")
            print(f"Tiempo de ejecución: {tiempo_total:.6f} segundos")
            return x_nuevo, i + 1, historial
        
        x = x_nuevo  # Actualiza el valor de x
    
    # Si no converge en el número máximo de iteraciones
    tiempo_total = time.time() - tiempo_inicio
    print("="*90)
    print(f"\nMáximo de iteraciones alcanzado")
    print(f"Tiempo de ejecución: {tiempo_total:.6f} segundos")
    return x, max_iter, historial




def seleccionar_x0_fourier(func, f_second, a, b):
    """
    Selecciona x0 basado en la condición suficiente (a veces llamada condición de Fourier)
    usada en Newton-Raphson: elegir el extremo que cumple f(x0) * f''(x0) > 0.

    Parámetros:
    - func: función a evaluar (numérica)
    - f_second: segunda derivada de la función (numérica)
    - a: extremo izquierdo del intervalo
    - b: extremo derecho del intervalo

    Retorna:
    - x0: punto inicial seleccionado (o None si no se puede elegir)
    - fa, fb: valores de la función en los extremos
    """
    try:
        fa = func(a)
        fb = func(b)
        f2a = f_second(a)
        f2b = f_second(b)

        # Verifica si existe cambio de signo entre los extremos (condición de Bolzano)
        if fa * fb > 0:
            print(f"  ⚠ No se cumple la condición de Bolzano en [{a:.2f}, {b:.2f}]")
            return None, fa, fb

        # Condición suficiente para convergencia local de Newton: f(x0)*f''(x0) > 0
        if fa * f2a > 0:
            x0 = a
            print(f"  ✓ Seleccionado x0 = {x0:.2f} (cumple f(x0)*f''(x0) > 0)")
            return x0, fa, fb
        elif fb * f2b > 0:
            x0 = b
            print(f"  ✓ Seleccionado x0 = {x0:.2f} (cumple f(x0)*f''(x0) > 0)")
            return x0, fa, fb

        # Si ninguno cumple la condición suficiente, elegir el extremo con menor |f| y avisar
        x0 = a if abs(fa) < abs(fb) else b
        print(f"  ⚠ Ningún extremo cumple f(x)*f''(x)>0. Seleccionado x0 = {x0:.2f} (menor |f(x)|) como fallback")
        return x0, fa, fb

    except Exception as e:
        print(f"  ⚠ Error al evaluar la función o su segunda derivada: {e}")
        return None, None, None


def metodo_tanteo(func, x_min=-10, x_max=10, paso=0.5):
    """
    Encuentra intervalos donde se encuentran las raíces de una función usando el método de tanteo.
    
    Parámetros:
    - func: función matemática a evaluar
    - x_min: límite inferior del rango de búsqueda
    - x_max: límite superior del rango de búsqueda 
    - paso: tamaño del paso para el tanteo
    
    Retorna:
    - Lista de tuplas con los intervalos [a, b] donde hay cambio de signo
    """
    intervalos = []
    x = x_min
    
    # Evalúa el primer punto
    try:
        f_anterior = func(x)
    except:
        print(f"Error al evaluar la función en x = {x}")
        return intervalos
    
    x += paso
    
    # Recorre el rango buscando cambios de signo
    while x <= x_max:
        try:
            f_actual = func(x)
            
            # Si hay cambio de signo, guarda el intervalo
            if f_anterior * f_actual < 0:
                intervalos.append((x - paso, x))
            
            f_anterior = f_actual
            x += paso
            
        except:
            print(f"Error al evaluar la función en x = {x}")
            x += paso
            continue
    
    return intervalos



def graficar_funcion_con_intervalos(func, intervalos, x_min=-10, x_max=10):
    """
    Grafica la función y marca los intervalos donde se encuentran las raíces.
    """
    x = np.linspace(x_min, x_max, 1000)
    
    # Evalúa la función en el rango de valores
    try:
        y = [func(xi) for xi in x]
    except:
        print("Error al generar la gráfica")
        return
    
    plt.figure(figsize=(12, 8))
    plt.plot(x, y, 'b-', linewidth=2, label='f(x)')
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.axvline(x=0, color='k', linestyle='--', alpha=0.5)
    
    # Marca visualmente los intervalos donde se detectaron raíces
    for i, (a, b) in enumerate(intervalos):
        plt.axvspan(a, b, alpha=0.3, color='red', 
                   label=f'Intervalo {i+1}: [{a:.2f}, {b:.2f}]' if i == 0 else "")
    
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Función con intervalos que contienen raíces')
    plt.legend()
    plt.show(block=False)


def solicitar_parametros():
    """Solicita todos los parámetros necesarios al usuario"""
    print("=== CONFIGURACIÓN DEL MÉTODO DE TANTEO ===")
    
    # Solicita la función al usuario y genera su versión simbólica y derivada
    f_str = input("Ingrese la función f(x): ")
    
    try:
        x = sp.Symbol("x")
        f_sympy = sp.sympify(f_str)
        
        # Calcula automáticamente la derivada
        f_deriv_sympy = sp.diff(f_sympy, x)
        # Calcula la segunda derivada
        f_second_sympy = sp.diff(f_sympy, x, 2)
        
        # Crea funciones evaluables numéricamente
        f = sp.lambdify(x, f_sympy, "math")
        f_deriv = sp.lambdify(x, f_deriv_sympy, "math")
        f_second = sp.lambdify(x, f_second_sympy, "math")
    except Exception as e:
        print(f"⚠ Error al procesar la función: {e}")
        return None, None, None, None, None, None, None, None
    
    # Solicita los parámetros de búsqueda y precisión
    try:
        x_min = float(input("Ingrese el límite inferior del intervalo de tanteo: "))
        x_max = float(input("Ingrese el límite superior del intervalo de tanteo: "))
        paso = float(input("Ingrese el tamaño del paso para el tanteo: "))
    except ValueError:
        print("⚠ Error en los parámetros del tanteo")
        return None, None, None, None, None, None, None
    
    tolerancia = float(input("Ingrese la tolerancia (por defecto 1e-6): ") or 1e-6)
    max_iter = int(input("Ingrese el máximo de iteraciones (por defecto 100): ") or 100)
    
    return f, f_deriv, f_second, x_min, x_max, paso, tolerancia, max_iter



def main():
    """Función principal que ejecuta todo el proceso"""
    
    # Se obtiene toda la configuración inicial
    f, f_deriv, f_second, x_min, x_max, paso, tolerancia, max_iter = solicitar_parametros()
    if f is None:
        print("⚠ Error en la configuración. Terminando programa.")
        return
    
    # 1. Localiza los intervalos con posibles raíces
    intervalos = metodo_tanteo(f, x_min, x_max, paso)
    if not intervalos:
        print("\n⚠ No se encontraron intervalos con cambio de signo.")
        return
    
    # 2. Muestra la gráfica de la función con los intervalos detectados
    graficar_funcion_con_intervalos(f, intervalos, x_min, x_max)
    
    # 3. Aplica el método de Newton-Raphson en cada intervalo hallado
    for i, (a, b) in enumerate(intervalos, 1):
        print(f"\n--- Intervalo {i}: [{a:.2f}, {b:.2f}] ---")
        
        x0, _, _ = seleccionar_x0_fourier(f, f_second, a, b)
        if x0 is None:
            continue
        
        # Ejecuta Newton-Raphson y muestra resultados
        raiz, iteraciones, historial = metodo_newton_raphson(
            f, f_deriv, x0, tolerancia, max_iter
        )
        
        print(f"\n  📊 RESULTADOS FINALES:")
        print(f"     Raíz aproximada: x = {raiz:.8f}")
        print(f"     f(x) = {f(raiz):.8e}")
        print(f"     Iteraciones: {iteraciones}")
        print(f"     Error final: {historial[-1]['error']:.8e}")


if __name__ == "__main__":
    main()
    input("Presioná Enter para salir...")
