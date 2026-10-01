import math

# son las misma fucniones del 2 se podria importar a llamar a ambas directamente 
def fl_round(val, k=4):
  if val == 0:
    return 0.0, 0
  sign = 1 if val > 0 else -1
  val_abs = abs(val)
  exp = math.floor(math.log10(val_abs)) + 1
  mantissa = val_abs / (10**exp)
  mantissa_r = round(mantissa, k)
  if mantissa_r >= 1.0:
    mantissa_r /= 10.0
    exp += 1
  val_fl = sign * mantissa_r * (10**exp)
  return val_fl, exp

def format_norm(val, k=4):
  if val == 0:
    return "0." + "0" * k + " x 10^0"
  sign = "-" if val < 0 else ""
  val_abs = abs(val)
  exp = math.floor(math.log10(val_abs)) + 1
  mantissa = val_abs / (10**exp)
  mantissa_r = round(mantissa, k)
  if mantissa_r >= 1.0:
    mantissa_r /= 10.0
    exp += 1
  return f"{sign}{mantissa_r:.{k}f} x 10^{exp}"

def main():
  # Coeficientes exactos dados
  x1_exact = -0.01610723
  x2_exact = -62.08390
  # Normalización de coeficientes de entrada a 4 dígitos
  fl_a, _ = fl_round(1.0, 4) 
  fl_b, _ = fl_round(62.10, 4) 
  fl_c, _ = fl_round(1.0, 4) 
  # Cómputo del discriminante paso a paso en máquina (k = 4)
  # b^2:
  b_sq_exact = fl_b**2  
  fl_b_sq, _ = fl_round(b_sq_exact, 4) 
  # 4ac:
  four_ac_exact = 4.0 * fl_a * fl_c 
  fl_four_ac, _ = fl_round(four_ac_exact, 4)  
  # b^2 - 4ac:
  disc_exact = fl_b_sq - fl_four_ac  
  fl_disc, _ = fl_round(disc_exact, 4)  
  # sqrt(b^2 - 4ac):
  sqrt_disc_exact = math.sqrt(fl_disc) 
  fl_sqrt_disc, _ = fl_round(sqrt_disc_exact, 4)  

  fl_2a, _ = fl_round(2.0 * fl_a, 4) 
  fl_neg_2c, _ = fl_round(-2.0 * fl_c, 4) 

  # itema A tradicional
  # x1 = (-b + sqrt(disc)) / (2a)
  num1_a, _ = fl_round(-fl_b + fl_sqrt_disc, 4) 
  x1_trad, _ = fl_round(num1_a / fl_2a, 4)  
  # x2 = (-b - sqrt(disc)) / (2a)
  num2_a, _ = fl_round(-fl_b - fl_sqrt_disc, 4)  
  x2_trad, _ = fl_round(num2_a / fl_2a, 4)  

  # item B racionalizar  
  # x1 = -2c / (b + sqrt(disc))
  den1_b, _ = fl_round(fl_b + fl_sqrt_disc, 4)  
  x1_rat, _ = fl_round(fl_neg_2c / den1_b, 4)
  # x2 = -2c / (b - sqrt(disc))
  den2_b, _ = fl_round(fl_b - fl_sqrt_disc, 4) 
  x2_rat, _ = fl_round(fl_neg_2c / den2_b, 4) 

  # Cálculo de errores
  resultados = [
      ("x1 (Tradicional)", x1_exact, x1_trad),
      ("x1 (Racionalizada)", x1_exact, x1_rat),
      ("x2 (Tradicional)", x2_exact, x2_trad),
      ("x2 (Racionalizada)", x2_exact, x2_rat),
  ]

  print("=" * 115)
  print(
      f"{'Aproximación evaluada':<22} | {'Valor Exacto':<15} |"
      f" {'p* (Normalizado)':<18} | {'E_a (Norm)':<15} | {'E_r (Norm)':<15} |"
      " {'E_r (%)'}"
  )
  print("=" * 115)

  for nombre, exacto, aprox in resultados:
    ea = abs(exacto - aprox)
    er = ea / abs(exacto)
    print(
        f"{nombre:<22} | {exacto:<15.7f} | {format_norm(aprox, 4):<18} |"
        f" {format_norm(ea, 4):<15} | {format_norm(er, 4):<15} |"
        f" {er * 100:.4f}%"
    )
  print("=" * 115)

if __name__ == "__main__":
  main()