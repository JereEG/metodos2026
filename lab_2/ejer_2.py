import math

#Representa un numero en punto flotante normalizado con redondeo a k=3 digitos.
def fl_round(val, k=3):
  if val == 0:
    return 0.0, 0
  sign = 1 if val > 0 else -1
  val_abs = abs(val)
  exp = math.floor(math.log10(val_abs)) + 1
  mantissa = val_abs / (10**exp)

  # Redondeo simetrico sobre la mantisa a k decimales
  mantissa_r = round(mantissa, k)

  # Si por redondeo la mantisa llega a 1.0 (ej. 0.9996 -> 1.000)
  if mantissa_r >= 1.0:
    mantissa_r /= 10.0
    exp += 1

  val_fl = sign * mantissa_r * (10**exp)
  return val_fl, exp

#Retorna el string en notacion normalizada
def format_norm(val, k=3):
  if val == 0:
    return "0.000 x 10^0"
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
    casos = []

    # a. 133 + 0.921
    p_a = 133.0 + 0.921
    fl_133, _ = fl_round(133.0, 3)
    fl_0921, _ = fl_round(0.921, 3)
    p_star_a, _ = fl_round(fl_133 + fl_0921, 3)
    casos.append(("a", "133 + 0.921", p_a, p_star_a))

    # b. 133 - 0.499
    p_b = 133.0 - 0.499
    fl_0499, _ = fl_round(0.499, 3)
    p_star_b, _ = fl_round(fl_133 - fl_0499, 3)
    casos.append(("b", "133 - 0.499", p_b, p_star_b))

    # c. (121 - 119) - 0.327
    p_c = (121.0 - 119.0) - 0.327
    fl_121, _ = fl_round(121.0, 3)
    fl_119, _ = fl_round(119.0, 3)
    fl_0327, _ = fl_round(0.327, 3)
    step1_c, _ = fl_round(fl_121 - fl_119, 3) 
    p_star_c, _ = fl_round(step1_c - fl_0327, 3)  
    casos.append(("c", "(121 - 119) - 0.327", p_c, p_star_c))

    # d. (121 - 0.327) - 119
    p_d = (121.0 - 0.327) - 119.0
    step1_d, _ = fl_round(
    fl_121 - fl_0327, 3
    )  
    p_star_d, _ = fl_round(step1_d - fl_119, 3) 
    casos.append(("d", "(121 - 0.327) - 119", p_d, p_star_d))

    # e. (2/9) * (9/7)
    p_e = 2.0 / 7.0  
    fl_2_9, _ = fl_round(2.0 / 9.0, 3) 
    fl_9_7, _ = fl_round(9.0 / 7.0, 3)  
    p_star_e, _ = fl_round(fl_2_9 * fl_9_7, 3)  
    casos.append(("e", "(2/9) * (9/7)", p_e, p_star_e))

    # Presentacion en consola
    print(
        f"{'Ítem':<5} | {'Operación':<23} | {'p (Exacto)':<15} | {'p* (Normalizado)':<18} | {'E_a (Norm)':<15} | {'E_r (Norm)':<15} | {'E_r (%)'}"
    )
    print("-" * 115)

    for item, op, p, p_star in casos:
        ea = abs(p - p_star)
        er = ea / abs(p)
        print(
            f"{item:<5} | {op:<23} | {p:<15.6f} | {format_norm(p_star, 3):<18} | {format_norm(ea, 3):<15} | {format_norm(er, 3):<15} | {er * 100:.4f}%"
        )

if __name__ == "__main__":
  main()