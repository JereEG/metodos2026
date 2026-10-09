import sympy as sp
import metodos as mt
import tanteo as tn


def solicitar_parametros():
    """Solicita todos los parámetros necesarios al usuario"""
    print("=== CONFIGURACIÓN DEL MÉTODO DE TANTEO ===")
    
    
    f_str = input("Ingrese la función f(x): ")
    
    try:
        x = sp.Symbol("x")
        f_sympy = sp.sympify(f_str)
        f = sp.lambdify(x, f_sympy, "math")
        print(f"✓ Función procesada: f(x) = {f_str}")
    except Exception as e:
        print(f"⚠ Error al procesar la función: {e}")
        return None, None, None, None, None, None
    
    # Solicitar parámetros del tanteo
    print("\n=== PARÁMETROS DEL TANTEO ===")
    try:
        x_min = float(input("Ingrese el límite inferior del intervalo de tanteo: "))
        x_max = float(input("Ingrese el límite superior del intervalo de tanteo: "))
        paso = float(input("Ingrese el tamaño del paso para el tanteo: "))
        
        if x_min >= x_max:
            print("⚠ El límite inferior debe ser menor que el superior")
            return None, None, None, None, None, None
        
        if paso <= 0:
            print("⚠ El paso debe ser positivo")
            return None, None, None, None, None, None
            
    except ValueError:
        print("⚠ Error en los parámetros del tanteo")
        return None, None, None, None, None, None
    
    # Solicitar parámetros de Bisección (Intervalo Medio)
    print("\n=== PARÁMETROS DE BISECCIÓN (INTERVALO MEDIO) ===")
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
    
    return f, x_min, x_max, paso, tolerancia, max_iter





def verificar_intervalo(func, a, b):
    """
    Verifica que el intervalo cumple la condición de Bolzano
    
    Parámetros:
    - func: función a evaluar
    - a: extremo izquierdo del intervalo
    - b: extremo derecho del intervalo
    
    Retorna:
    - bool: True si cumple la condición, False en caso contrario
    - fa, fb: valores de la función en los extremos
    """
    try:
        fa = func(a)
        fb = func(b)
        
        print(f"  f({a:.2f}) = {fa:.6f}")
        print(f"  f({b:.2f}) = {fb:.6f}")
        
        # Verificar condición de Bolzano
        if fa * fb > 0:
            print(f"  ⚠ No se cumple la condición de Bolzano en [{a:.2f}, {b:.2f}]")
            return False, fa, fb
        
        print(f"  ✓ Condición de Bolzano cumplida en [{a:.2f}, {b:.2f}]")
        return True, fa, fb
        
    except Exception as e:
        print(f"  ⚠ Error al evaluar la función: {e}")
        return False, None, None






def main():
    """Función principal que ejecuta todo el proceso"""
    
    # Solicitar parámetros
    f, x_min, x_max, paso, tolerancia, max_iter = solicitar_parametros()
    
    if f is None:
        print("⚠ Error en la configuración. Terminando programa.")
        return
    
    print(f"\n=== CONFIGURACIÓN FINAL ===")
    print(f"Intervalo de tanteo: [{x_min}, {x_max}]")
    print(f"Paso: {paso}")
    print(f"Tolerancia: {tolerancia}")
    print(f"Máx. iteraciones: {max_iter}")
    
    # Realizar tanteo
    print(f"\n=== MÉTODO DE TANTEO ===")
    intervalos = tn.metodo_tanteo(f, x_min, x_max, paso)
    
    if not intervalos:
        print("\n⚠ No se encontraron intervalos con cambio de signo.")
        return
    
    print(f"\n✓ Se encontraron {len(intervalos)} intervalos con posibles raíces:")
    for i, (a, b) in enumerate(intervalos, 1):
        print(f"  Intervalo {i}: [{a:.2f}, {b:.2f}]")
    
    # Mostrar gráfica
    mostrar_grafico = input("\n¿Desea mostrar la gráfica? (s/n, Enter=sí): ").strip().lower()
    if mostrar_grafico in ['', 's', 'si', 'sí', 'y', 'yes']:
        tn.graficar_funcion_con_intervalos(f, intervalos, x_min, x_max)
        print("📊 Gráfico mostrado. El programa continuará automáticamente...")
    
    # Aplicar Bisección a cada intervalo
    print(f"\n=== APLICANDO BISECCIÓN (INTERVALO MEDIO) ===")
    
    for i, (a, b) in enumerate(intervalos, 1):
        print(f"\n--- Intervalo {i}: [{a:.2f}, {b:.2f}] ---")
        
        # Verificar que el intervalo cumple la condición de Bolzano
        condicion_ok, fa, fb = verificar_intervalo(f, a, b)
        
        if not condicion_ok:
            print("  Saltando este intervalo...")
            continue
        
        try:
            # Ejecutar Bisección
            print(f"\n  === MÉTODO DE BISECCIÓN ===")
            print(f"  Intervalo: [{a:.6f}, {b:.6f}]")
            print(f"  Tolerancia = {tolerancia}")
            print(f"  Máx. iteraciones = {max_iter}")
            print()
            
            raiz, iteraciones, historial = mt.metodo_intervalo_medio(
                f, a, b, 
                tolerancia=tolerancia, 
                max_iter=max_iter
            )
            
            # Resultados finales
            print(f"\n  📊 RESULTADOS FINALES:")
            print(f"     Raíz aproximada: x = {raiz:.8f}")
            print(f"     f(x) = {f(raiz):.8e}")
            print(f"     Iteraciones: {iteraciones}")
            print(f"     Error final: {historial[-1]['error']:.8e}")
                
        except Exception as e:
            print(f"  ⚠ Error durante Bisección: {e}")
            continue

if __name__ == "__main__":
    main()