#en este ejercicio reutilizamos la mayor parte del codigo del ejercicio2 
import math
#Representa un numero en punto flotante normalizado con truncamiento a k=3 digitos.
def fl_trunc(val, k=3):
  if val == 0:
    return 0.0, 0
  sign = 1 if val > 0 else -1
  val_abs = abs(val)
  exp = math.floor(math.log10(val_abs)) + 1
  mantissa = val_abs / (10**exp)
  # Truncamiento estricto sobre la mantisa a k digitos
  # Se usa factor 10^k para cortar sin redondeo
  mantissa_t = math.floor(mantissa * (10**k) + 1e-12) / (10**k)
  val_fl = sign * mantissa_t * (10**exp)
  return val_fl, exp

#Representa un numero en punto flotante normalizado
def fl_round(val, k=3):
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
#Retorna el string en notacion normalizada 
def format_norm(val, k=3):
  if val == 0:
    return "0." + "0" * k + " x 10^0"
  sign = "-" if val < 0 else ""
  val_abs = abs(val)
  exp = math.floor(math.log10(val_abs)) + 1
  mantissa = val_abs / (10**exp)
  mantissa_t = round(mantissa, k)
  if mantissa_t >= 1.0:
    mantissa_t /= 10.0
    exp += 1
  return f"{sign}{mantissa_t:.{k}f} x 10^{exp}"

def main():
  # Operandos de entrada truncados
  fl_133, _ = fl_trunc(133.0, 3)  
  fl_0921, _ = fl_trunc(0.921, 3)  
  fl_0499, _ = fl_trunc(0.499, 3)  
  fl_121, _ = fl_trunc(121.0, 3)  
  fl_119, _ = fl_trunc(119.0, 3)  
  fl_0327, _ = fl_trunc(0.327, 3) 
  casos = []
  # a. 133 + 0.921
  p_a = 133.0 + 0.921
  p_star_a, _ = fl_trunc(fl_133 + fl_0921, 3)
  casos.append(("a", "133 + 0.921", p_a, p_star_a))
  # b. 133 - 0.499
  p_b = 133.0 - 0.499
  p_star_b, _ = fl_trunc(fl_133 - fl_0499, 3)
  casos.append(("b", "133 - 0.499", p_b, p_star_b))
  # c. (121 - 119) - 0.327
  p_c = (121.0 - 119.0) - 0.327
  step1_c, _ = fl_trunc(fl_121 - fl_119, 3)
  p_star_c, _ = fl_trunc(
      step1_c - fl_0327, 3
  ) 
  casos.append(("c", "(121 - 119) - 0.327", p_c, p_star_c))
  # d. (121 - 0.327) - 119
  p_d = (121.0 - 0.327) - 119.0
  step1_d, _ = fl_trunc(
      fl_121 - fl_0327, 3
  ) 
  p_star_d, _ = fl_trunc(step1_d - fl_119, 3)  # fl(120 - 119) = 1.00
  casos.append(("d", "(121 - 0.327) - 119", p_d, p_star_d))
  # e. (2/9) * (9/7)
  p_e = 2.0 / 7.0
  fl_2_9, _ = fl_trunc(2.0 / 9.0, 3)  # 0.222 x 10^0
  fl_9_7, _ = fl_trunc(9.0 / 7.0, 3)  # 0.128 x 10^1 (1.28)
  p_star_e, _ = fl_trunc(
      fl_2_9 * fl_9_7, 3
  )  
  casos.append(("e", "(2/9) * (9/7)", p_e, p_star_e))
  print("=" * 115)
  print(
      f"{'Ítem':<5} | {'Operación':<23} | {'p (Exacto)':<16} | {'p*'
      ' (Normalizado)':<18} | {'E_a (Norm)':<16} | {'E_r (Norm)':<16} | {'E_r'
      ' (%)'}"
  )
  print("=" * 115)

  for item, op, p, p_star in casos:
    ea = abs(p - p_star)
    er = ea / abs(p)
    print(
        f"{item:<5} | {op:<23} | {format_norm(p, 5):<16} |"
        f" {format_norm(p_star, 3):<18} | {format_norm(ea, 3):<16} |"
        f" {format_norm(er, 3):<16} | {er * 100:.4f}%"
    )
  print("=" * 115)


if __name__ == "__main__":
  main()