from logica.logica_formulacao_2 import calcular_combinacoes, calcular_combinacoes_aperfeicoado, gerar_combinacoes

formulado = "04-20-20"
# Teste para validar
materias_primas = [
    {"name": "Ureia", "nutrients": [{"name": "N", "percent": "45"}]},
    {"name": "Superfosfato simples (SFS)", "nutrients": [{"name": "P₂O₅", "percent": "18"}]},
    {"name": "Superfosfato triplo (SFT)", "nutrients": [{"name": "P₂O₅", "percent": "46"}]},
    {"name": "Cloreto de Potássio (KCl)", "nutrients": [{"name": "K₂O", "percent": "60"}]},
    {"name": "Sulfato de Potássio (K2SO4)", "nutrients": [{"name": "K₂O", "percent": "50"}]},
    {"name": "Monoamônio fosfato (MAP)", "nutrients": [{"name": "N", "percent": "10"}, {"name": "P", "percent": "50"}]},
    {"name": "Diamônio fosfato (DAP)", "nutrients": [{"name": "N", "percent": "18"}, {"name": "P", "percent": "43"}]},
    {"name": "Granilhas", "nutrients": [{"name": "Inerte", "percent": "0"}]},
]

resultados = calcular_combinacoes_aperfeicoado(formulado, materias_primas)
print("To aqui? -- test.py")
# Exibindo as opções
for idx, resultado in enumerate(resultados, 1):
    print("Cadê meu teste?")
    print(f"Opção {idx}")
    print(f"Formulado (NPK): {resultado['formulado']}")
    print("Matérias-Primas:")
    for materia in resultado['materiasPrimas']:
        print(f"• {materia['name']}: {materia['kg']:.2f} kg")
    print("Enchimentos:")
    for enchimento in resultado['enchimentos']:
        print(f"• {enchimento['name']}: {enchimento['kg']:.2f} kg")
    print("Total: 1000 kg\n")