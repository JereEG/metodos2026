import math

def trunc3(val):
  """Trunca un número a 3 cifras significativas directas."""
  if val == 0:
    return 0.0
  sign = 1 if val > 0 else -1
  v = abs(val)
  exp = math.floor(math.log10(v))
  factor = 10 ** (exp - 2)
  return sign * math.floor(v / factor + 1e-12) * factor

def round3(val):
  """Redondea un número a 3 cifras significativas directas."""
  if val == 0:
    return 0.0
  sign = 1 if val > 0 else -1
  v = abs(val)
  exp = math.floor(math.log10(v))
  factor = 10 ** (exp - 2)
  return sign * round(v / factor) * factor

def main():
  x = 4.71
  # VALOR EXACTO
  x2_ex = x**2  # 22.1841
  x3_ex = x**3  # 104.487111
  t_6x2_ex = 6 * x2_ex  # 133.1046
  t_3x_ex = 3 * x  # 14.13
  f_ex = x3_ex - t_6x2_ex + t_3x_ex - 0.149  # -14.636489

  #forma normal
  # Truncado
  x2_tr = trunc3(x**2)  # 22.1
  x3_tr = trunc3(x2_tr * x)  # 22.1 * 4.71 = 104.091 -> 104
  t_6x2_tr = trunc3(6 * x2_tr)  # 6 * 22.1 = 132.6 -> 132
  t_3x_tr = trunc3(3 * x)  # 14.13 -> 14.1
  f_trad_tr = trunc3(trunc3(x3_tr - t_6x2_tr + t_3x_tr) - 0.149)  # -14.0

  # Redondeado
  x2_rd = round3(x**2)  # 22.2
  x3_rd = round3(x2_rd * x) 
  t_6x2_rd = round3(6 * x2_rd)  
  t_3x_rd = round3(3 * x)  
  f_trad_rd = round3(round3(x3_rd - t_6x2_rd + t_3x_rd) - 0.149) 

  # FORMA ANIDADA: aritmetica en cada operacion f(x) = ((x - 6)x + 3)x - 0.149
  # Truncado en cada operacion:
  p1_tr = trunc3(x - 6)  
  p2_tr = trunc3(p1_tr * x)  
  p3_tr = trunc3(p2_tr + 3)  
  p4_tr = trunc3(p3_tr * x)  
  f_anid_tr = trunc3(p4_tr - 0.149)  

  # Redondeado en cada operacion
  p1_rd = round3(x - 6)  
  p2_rd = round3(p1_rd * x) 
  p3_rd = round3(p2_rd + 3) 
  p4_rd = round3(p3_rd * x)  
  f_anid_rd = round3(p4_rd - 0.149) 

  # Muestra en consola
  print("=" * 85)
  print(
        f"{'Tipo':<25} | {'x':<6} | {'x^2':<10} | {'x^3':<12} | {'6x^2':<10} | {'3x':<6}"
    )
  print("=" * 85)
  print(
    f"{'Exacto':<25} | {x:<6} | {x2_ex:<10.4f} | {x3_ex:<12.6f} |"
    f" {t_6x2_ex:<10.4f} | {t_3x_ex:<6.2f}"
    )
  print(
    f"{'Tres dígitos (truncados)':<25} | {x:<6} | {x2_tr:<10.4g} |"
    f" {x3_tr:<12.4g} | {t_6x2_tr:<10.4g} | {t_3x_tr:<6.4g}"
    )
  print(
    f"{'Tres dígitos (redondeados)':<25} | {x:<6} | {x2_rd:<10.4g} |"
    f" {x3_rd:<12.4g} | {t_6x2_rd:<10.4g} | {t_3x_rd:<6.4g}"
    )
  print("=" * 85)

  casos = [
      ("Tradicional (Truncado)", f_trad_tr),
      ("Tradicional (Redondeado)", f_trad_rd),
      ("Anidado (Truncado)", f_anid_tr),
      ("Anidado (Redondeado)", f_anid_rd),
  ]

  print(
      f"\n{'Método / Forma':<27} | {'f(4.71) p*':<12} | {'E_a':<12} | {'E_r" (%)'}")
  print("-" * 65)
  for nombre, p_star in casos:
    ea = abs(f_ex - p_star)
    er = ea / abs(f_ex)
    print(f"{nombre:<27} | {p_star:<12.3f} | {ea:<12.6f} | {er * 100:.4f}%")
    
if __name__ == "__main__":
  main()