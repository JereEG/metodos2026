"""
METODOS COMPUTACIONALES - LABORATORIO 3
EJERCICIO 1: Tanque Esferico
Oipuru umi tembiaporape oiva 'laboratorio3_madre.py'-pe
"""

import math
import matplotlib.pyplot as plt
import numpy as np

# Oñeguenohẽ umi función script sýgui (laboratorio3_madre.py)
from laboratorio3_madre import (
    metodo_tanteo,
    resolver_interpolacion_lineal,
    resolver_intervalo_medio,
)

# ==============================================================================
# 1. TEMBIAPORÃ TEKO / PAPAPÝVA (MODELO MATEMÁTICO)
# V = pi * h^2 * (3*R - h) / 3
# R = 3 m, V = 30 m^3
# f(h) = (pi * h^2 * (9 - h) / 3) - 30 = 0
# ==============================================================================

R_VAL = 3.0
V_OBJ = 30.0


def f_tanque(h):
  """Ecuación canónica f(h) = 0"""
  return (math.pi * (h**2) * (3.0 * R_VAL - h) / 3.0) - V_OBJ


# ==============================================================================
# a. TAVYETE REHECHAHÁRA (EVALUACIÓN GRÁFICA PRELIMINAR)
# ==============================================================================
def graficar_tanque(func, h_min=0.0, h_max=6.0, raiz=None):
  """Ohechauka ta'angápe pe función dominio físico ryepýpe [0, 2R]"""
  h_vals = np.linspace(h_min, h_max, 500)
  y_vals = [func(h) for h in h_vals]

  plt.figure(figsize=(8, 5))
  plt.plot(
      h_vals,
      y_vals,
      label=r"$f(h) = \frac{\pi h^2 (9 - h)}{3} - 30$",
      color="navy",
      lw=2,
  )
  plt.axhline(
      0, color="black", linestyle="--", linewidth=1.2, label="Nivel f(h)=0"
  )
  plt.axvline(0, color="gray", linestyle=":", linewidth=0.8)

  if raiz is not None:
    plt.plot(
        raiz,
        func(raiz),
        "ro",
        markersize=8,
        label=f"Hapo (Raíz) ≈ {raiz:.4f} m",
    )

  plt.title("Ejercicio 1: Y rape rechauka (Tanque Esférico)", fontsize=12)
  plt.xlabel("Ypypuku h / Profundidad (m)", fontsize=11)
  plt.ylabel("f(h) (m³)", fontsize=11)
  plt.grid(True, linestyle="--", alpha=0.6)
  plt.legend()
  plt.tight_layout()
  plt.show()


# ==============================================================================
# PROGRAMA RUVICHA (FLUJO PRINCIPAL)
# ==============================================================================
def main():
  print("=" * 75)
  print(" GUÍA 3 - EJERCICIO 1: TANQUE ESFÉRICO (SCRIPT IMPORTADO)")
  print("=" * 75)

  # a. Ta'anga ñepyrũrã
  print("\n[a] Oñembosako'i ta'anga rechauka...")
  graficar_tanque(f_tanque, h_min=0.0, h_max=6.0)

  # b. Tanteo oñemoingéva kuatiáre (teclado rupive)
  print("\n[b] Tanteo rape (Separación de raíces por Bolzano):")
  paso_in = input("Emoinge tanteo mbohapypyre Δh [0.5 por defecto]: ").strip()
  paso = float(paso_in) if paso_in else 0.5

  # Ojeipuru 'metodo_tanteo' script sýgui
  intervalos = metodo_tanteo(
      func=f_tanque,
      x_inicio=0.0,
      direccion="positiva",
      max_raices=1,
      paso=paso,
      limite_seguridad=6.0,  # Dominio físico yvypóra mba'éva: 2R = 6 m
  )

  if not intervalos:
    print("[!] Ndojejuhúi mba'eveichagua cambio de signo.")
    return

  a_sel, b_sel = intervalos[0]
  print(f"\n[✓] Intervalo ojejuhúva: [{a_sel:.4f} ; {b_sel:.4f}] m")

  # c. Mbohapypyre jejuhu (Intervalo Medio ha Interpolación Lineal)
  tol_in = input(
      "\nEmoinge cota de error E [0.001 por defecto]: "
  ).strip()  # E < 0.001
  tol = float(tol_in) if tol_in else 0.001

  print("\n>>> 1. Oñemba'apo Método de Intervalo Medio rupive:")
  raiz_im = resolver_intervalo_medio(f_tanque, a_sel, b_sel, tol)

  print("\n>>> 2. Oñemba'apo Método de Interpolación Lineal rupive:")
  raiz_il = resolver_interpolacion_lineal(f_tanque, a_sel, b_sel, tol)

  # Ta'anga pahague hapo reheve
  if raiz_il is not None:
    graficar_tanque(f_tanque, h_min=0.0, h_max=6.0, raiz=raiz_il)


if __name__ == "__main__":
  main()