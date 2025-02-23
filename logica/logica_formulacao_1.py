def calcular_formula(materias_primas):
    total_kg = 0
    total_n = 0
    total_p = 0
    total_k = 0

    for mp in materias_primas:
        kg = mp.get('kg', 0)
        teor_n = mp.get('teor_n', 0)
        teor_p = mp.get('teor_p2o5', 0)
        teor_k = mp.get('teor_k2o', 0)

        total_kg += kg
        total_n += (kg * teor_n) / 100
        total_p += (kg * teor_p) / 100
        total_k += (kg * teor_k) / 100

    if total_kg > 1000:
        raise ValueError("A soma total ultrapassa 1000 kg!")

    enchimento = 1000 - total_kg

    formula_final = {
        "N": (total_n / 10),
        "P": (total_p / 10),
        "K": (total_k / 10)
    }

    return {
        "formula": f"{formula_final['N']:.2f}-{formula_final['P']:.2f}-{formula_final['K']:.2f}",
        "total_kg": total_kg,
        "enchimento": enchimento,
        "detalhes": materias_primas
    }
