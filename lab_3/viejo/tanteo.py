import numpy as np
import matplotlib.pyplot as plt

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
    
    try:
        f_anterior = func(x)
    except:
        print(f"Error al evaluar la función en x = {x}")
        return intervalos
    
    print(f"{'x':>8} | {'f(x)':>12} | {'Cambio de signo':>15}")
    print("-" * 40)
    print(f"{x:8.2f} | {f_anterior:12.4f} |")
    
    x += paso
    
    while x <= x_max:
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
    
    try:
        y = [func(xi) for xi in x]
    except:
        print("Error al generar la gráfica")
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
    plt.savefig("tanteo.png")
