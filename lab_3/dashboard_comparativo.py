# streamlit run "lab_3/dashboard_comparativo.py"
import streamlit as st
import sympy as sp
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
import re
from metodos_lab3 import barrido_tanteo, regla_descartes

st.set_page_config(layout="wide", page_title="Comparativa: NR vs IL")

# --- FUNCIONES AUXILIARES ---
def format_latex(eq_str):
    """Formatea la ecuación ingresada en un string compatible con LaTeX de manera limpia."""
    eq = eq_str.replace("**", "^").replace("*", r"\cdot ")
    # Encierra exponentes de 2 o más dígitos en llaves para que se rendericen bien (ej. x^{10})
    eq = re.sub(r'\^(\d{2,})', r'^{\1}', eq)
    return eq

def newton_raphson_history(fn, d1, x0, tol=1e-5, max_iter=50):
    t_ini = time.perf_counter()
    x_val = x0
    history = []
    
    for k in range(max_iter):
        fx = fn(x_val)
        dfx = d1(x_val)
        
        if abs(dfx) < 1e-14:
            t_total = time.perf_counter() - t_ini
            history.append({"Iteración (i)": k+1, "x_i": x_val, "f(x_i)": fx, "f'(x_i)": dfx, "x_{i+1}": None, "Error": None})
            return history, False, t_total, "Error: Derivada nula."

        x_sig = x_val - (fx / dfx)
        err = abs(x_sig - x_val)
        
        history.append({"Iteración (i)": k+1, "x_i": x_val, "f(x_i)": fx, "f'(x_i)": dfx, "x_{i+1}": x_sig, "Error": err})
        
        if err < tol or abs(fx) < tol:
            t_total = time.perf_counter() - t_ini
            return history, True, t_total, "Convergencia Exitosa"
            
        x_val = x_sig

    t_total = time.perf_counter() - t_ini
    return history, False, t_total, "Límite de iteraciones alcanzado"

def interpolacion_lineal_history(fn, a, b, tol=1e-5, max_iter=50):
    t_ini = time.perf_counter()
    if fn(a) * fn(b) >= 0:
        return [], False, 0.0, "No cumple Bolzano en el intervalo [a, b]"

    x_ant = a
    history = []
    for k in range(1, max_iter + 1):
        fa = fn(a)
        fb = fn(b)
        x_sig = (a * fb - b * fa) / (fb - fa)
        fx_sig = fn(x_sig)
        err = abs(x_sig - x_ant) if k > 1 else abs(b - a)
        
        history.append({"Iteración (i)": k, "a": a, "b": b, "x_i": x_sig, "f(x_i)": fx_sig, "Error": err})

        if err < tol or abs(fx_sig) < 1e-14:
            t_total = time.perf_counter() - t_ini
            return history, True, t_total, "Convergencia Exitosa"

        if fa * fx_sig < 0:
            b = x_sig
        else:
            a = x_sig
        x_ant = x_sig

    t_total = time.perf_counter() - t_ini
    return history, False, t_total, "Límite de iteraciones alcanzado"

# --- UI PRINCIPAL ---
st.title("Estudio Comparativo: Newton-Raphson vs Interpolación Lineal")
st.markdown("Analiza cómo se comportan ambos métodos frente a diferentes desafíos teóricos o industriales.")

# 1. Definición del Problema
st.header("1. Definición del Problema")
caso = st.selectbox(
    "Seleccione el Caso de Estudio o ingrese uno propio:",
    [
        "Caso A: Diseño de Reactores (Alta Curvatura) -> f(x) = x**10 - 1",
        "Caso B: Ecuación de Fricción Trascendente -> f(x) = exp(x) - 4*x",
        "Personalizado: Ingresar ecuación libremente"
    ]
)

if "Personalizado" in caso:
    ecuacion_str = st.text_input("Ingrese f(x):", "x**3 - 6*x**2 + 11*x - 6.1")
    contexto = "Estudio numérico de una función ingresada por el usuario. El comportamiento dependerá en gran medida de las derivadas y curvaturas propias de la misma."
elif "Caso A" in caso:
    ecuacion_str = "x**10 - 1"
    contexto = "Un reactor químico experimenta una tasa de reacción que crece de forma polinomial extrema en función del tiempo. Para un ingeniero químico que plantea el balance de masa, el modelo matemático resultante posee términos elevados a la décima potencia ($x^{10}$). Esto genera una curva muy pronunciada (casi plana al principio y vertical luego), lo que hace que la Interpolación Lineal avance sumamente lento debido a la geometría del bracket, mientras que Newton aprovecha la recta tangente para cortar camino velozmente."
else:
    ecuacion_str = "exp(x) - 4*x"
    contexto = "Cálculo en dinámica de fluidos usando una ecuación trascendente para el factor de fricción. Si Newton inicia cerca del punto de inflexión o donde la derivada es mínima (x cercano a 1.38), fallará al disparar la tangente hacia el infinito o tardará muchísimas iteraciones. En contraste, la Interpolación Lineal por Bolzano siempre converge de manera segura y estable atrapando la raíz, lo que la hace la favorita en los simuladores hidráulicos."

# Mostrar ecuación y contexto
st.latex(r"f(x) = " + format_latex(ecuacion_str))
st.info(contexto)

# Configuración Matemática global
x = sp.Symbol('x')
try:
    f_simb = sp.sympify(ecuacion_str)
    d1_simb = sp.diff(f_simb, x)
    fn = sp.lambdify(x, f_simb, "math")
    d1 = sp.lambdify(x, d1_simb, "math")
except Exception as e:
    st.error(f"Error al interpretar la función: {e}")
    st.stop()

# Descartes con Fallback
try:
    max_p, max_n = regla_descartes(f_simb, x)
except ValueError:
    st.warning("⚠️ **Nota sobre Ecuaciones:** La función ingresada es trascendente o no puramente polinómica. La Regla de Descartes no aplica aquí, por lo que se buscarán hasta 10 raíces en cada sentido predeterminadamente. Algunos métodos numéricos pueden volverse inestables con estas funciones dependiendo del punto de inicio.")
    max_p, max_n = 10, 10

# 2. Configuración de la Búsqueda (Tanteo)
st.header("2. Configuración de la Búsqueda (Tanteo)")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    sentido_opciones = {"Todas ('t')": "todas", "Positivas ('p')": "positiva", "Negativas ('n')": "negativa"}
    sentido_key = st.selectbox("Sentido de búsqueda", list(sentido_opciones.keys()))
    sentido_real = sentido_opciones[sentido_key]

    if sentido_real == "negativa":
        lim_raices = max_n
    elif sentido_real == "positiva":
        lim_raices = max_p
    else:
        lim_raices = (max_p, max_n)

with col_t2:
    val_ini = st.number_input("Punto de inicio del tanteo", value=0.0)
    val_lim = st.number_input("Límite máximo a recorrer", value=50.0)

with col_t3:
    val_paso = st.number_input("Paso deltax (tanteo)", value=0.5, step=0.1)
    tol_input = st.number_input("Tolerancia (Cota de Error)", value=1e-5, format="%e")
    max_iter = st.number_input("Máximo de Iteraciones", value=50, step=10)

st.write(f"Buscando intervalos en sentido **{sentido_real}** desde x = {val_ini}...")
intervalos = barrido_tanteo(fn, val_ini, sentido_real, lim_raices, val_paso, val_lim)

if not intervalos:
    st.warning("No se encontraron cambios de signo en ese rango. Prueba ajustando el inicio, el límite o el paso.")
    st.stop()

# Opciones de Intervalos
int_strs = ["Todos los intervalos (Max 3)"] + [f"Intervalo {i+1}: [{round(a, 4)} ; {round(b, 4)}]" for i, (a, b) in enumerate(intervalos)]
seleccion_int = st.selectbox("Seleccione el intervalo a analizar:", int_strs)

if seleccion_int.startswith("Todos"):
    intervalos_a_procesar = intervalos[:3]
    if len(intervalos) > 3:
        st.info("💡 Mostrando únicamente los primeros 3 intervalos para mantener la interfaz fluida y legible.")
else:
    idx_int = int_strs.index(seleccion_int) - 1
    intervalos_a_procesar = [intervalos[idx_int]]

# Si es un solo intervalo, permitimos personalizar x0. Si son varios, automatizamos x0 = b
if len(intervalos_a_procesar) == 1:
    x0_val_custom = st.number_input("Punto inicial x0 (Exclusivo de Newton-Raphson)", value=float(intervalos_a_procesar[0][1]))
else:
    x0_val_custom = None

st.markdown("---")
st.header("3. Ejecución Lado a Lado")

historiales_completos_il = []
historiales_completos_nr = []
min_x_graph, max_x_graph = float('inf'), float('-inf')

for num_raiz, (a_val, b_val) in enumerate(intervalos_a_procesar, 1):
    if len(intervalos_a_procesar) > 1:
        st.subheader(f"Raíz {num_raiz}: Intervalo [{a_val}, {b_val}]")
        
    # HACK: Si el tanteo cayó exactamente en la raíz (a == b), ampliamos el intervalo para satisfacer Bolzano y no romper los métodos.
    if a_val == b_val:
        st.info(f"💡 El método de tanteo tuvo la suerte de caer exactamente sobre la raíz en x={a_val}. Hemos ampliado artificialmente el intervalo (±{val_paso/2}) para observar cómo se comportan numéricamente los métodos.")
        a_val -= val_paso / 2.0
        b_val += val_paso / 2.0

    min_x_graph = min(min_x_graph, a_val)
    max_x_graph = max(max_x_graph, b_val)

    x0_val = x0_val_custom if x0_val_custom is not None else b_val

    col_il, col_nr = st.columns(2)

    # --- EJECUCION INTERPOLACION LINEAL ---
    with col_il:
        st.markdown(f"**Interpolación Lineal** | Intervalo Evaluado: [{a_val}, {b_val}]")
        hist_il, ok_il, t_il, msg_il = interpolacion_lineal_history(fn, a_val, b_val, tol_input, max_iter)
        
        if ok_il:
            st.success(f"**{msg_il}** en {len(hist_il)} iteraciones.")
        else:
            st.error(f"**{msg_il}**")
        st.info(f"⏱️ **Tiempo de Ejecución:** {t_il:.6f} s")
        
        if hist_il:
            df_il = pd.DataFrame(hist_il)
            st.dataframe(df_il.style.format(precision=6), use_container_width=True)
            historiales_completos_il.extend(hist_il)

    # --- EJECUCION NEWTON RAPHSOM ---
    with col_nr:
        st.markdown(f"**Newton-Raphson** | Punto Inicial (x0): {x0_val}")
        hist_nr, ok_nr, t_nr, msg_nr = newton_raphson_history(fn, d1, x0_val, tol_input, max_iter)
        
        if ok_nr:
            st.success(f"**{msg_nr}** en {len(hist_nr)} iteraciones.")
        else:
            st.error(f"**{msg_nr}**")
        st.info(f"⏱️ **Tiempo de Ejecución:** {t_nr:.6f} s")
        
        if hist_nr:
            df_nr = pd.DataFrame(hist_nr)
            st.dataframe(df_nr.style.format(precision=6), use_container_width=True)
            historiales_completos_nr.extend(hist_nr)
            
    # --- CONCLUSION INDIVIDUAL ---
    if ok_il and ok_nr:
        if len(hist_nr) < len(hist_il):
            st.write(f"📝 *Para esta raíz, Newton-Raphson fue superior (velocidad cuadrática: {len(hist_nr)} iteraciones).*")
        elif len(hist_il) < len(hist_nr):
            st.write(f"📝 *Para esta raíz, Interpolación Lineal ganó de forma contundente ({len(hist_il)} iteraciones) gracias a la contención de Bolzano.*")
    elif not ok_nr and ok_il:
         st.write(f"📝 *Newton fracasó por inestabilidad de la derivada. Interpolación Lineal encontró la raíz sin problemas.*")
    st.markdown("---")

# --- GRAFICO VISUAL (PLOTLY) ---
st.header("4. Representación Gráfica de la Convergencia")

st.markdown("""
> 💡 **¿Qué estamos viendo?**  
> La curva representa la función matemática $f(x)$. La raíz (solución) es el punto exacto donde la curva cruza la **línea roja punteada** ($y = 0$).  
> Cada marca superpuesta muestra qué valores probó cada método en cada iteración ($x_i$). Así puedes ver gráficamente si el método se acercó a la raíz saltando de un lado a otro (oscilación), acercándose muy lentamente (atasco), o de forma directa y limpia.
""")

margen_x = max(0.5, (max_x_graph - min_x_graph) * 0.2)
xs = np.linspace(min_x_graph - margen_x, max_x_graph + margen_x, 600)
try:
    ys = [fn(pt) for pt in xs]
except Exception as e:
    st.error("Error al graficar la función")
    st.stop()

# Ajuste automático del eje Y buscando el máximo valor en los límites de los intervalos
y_max_val = max(abs(fn(min_x_graph)), abs(fn(max_x_graph))) if not np.isnan(fn(min_x_graph)) else 10.0
y_limit = max(y_max_val * 1.5, 1.0) 

fig = go.Figure()
fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name='f(x)'))
fig.add_hline(y=0, line_dash="dash", line_color="red")

if historiales_completos_il:
    il_xs = [step["x_i"] for step in historiales_completos_il]
    il_ys = [step["f(x_i)"] for step in historiales_completos_il]
    fig.add_trace(go.Scatter(x=il_xs, y=il_ys, mode='markers+lines', name='Iteraciones IL', marker=dict(symbol='circle', size=8, color='cyan')))

if historiales_completos_nr:
    nr_xs = [step["x_i"] for step in historiales_completos_nr]
    nr_ys = [step["f(x_i)"] for step in historiales_completos_nr]
    fig.add_trace(go.Scatter(x=nr_xs, y=nr_ys, mode='markers+lines', name='Iteraciones NR', marker=dict(symbol='cross', size=10, color='yellow')))

fig.update_layout(
    title="Camino hacia las Raíces", 
    xaxis_title="x", 
    yaxis_title="f(x)", 
    hovermode="x unified",
    yaxis=dict(range=[-y_limit, y_limit])
)
st.plotly_chart(fig, use_container_width=True)
