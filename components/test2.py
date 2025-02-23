from logica.logica_formulacao_2 import (
    gerar_combinacoes_new_,
    calcular_fornecimento_new_
)

materias_primas = [
    {"name": "Ureia", "isNutrient": "true", "nutrients": [{"name": "N", "percent": "45"}]},
    {"name": "Superfosfato simples (SFS)", "isNutrient": "true", "nutrients": [{"name": "P₂O₅", "percent": "18"}]},
    {"name": "Superfosfato triplo (SFT)", "isNutrient": "true", "nutrients": [{"name": "P₂O₅", "percent": "46"}]},
    {"name": "Cloreto de Potássio (KCl)", "isNutrient": "true", "nutrients": [{"name": "K₂O", "percent": "60"}]},
    {"name": "Sulfato de Potássio (K2SO4)", "isNutrient": "true", "nutrients": [{"name": "K₂O", "percent": "50"}]},
    {"name": "Monoamônio fosfato (MAP)", "isNutrient": "true", "nutrients": [{"name": "N", "percent": "10"}, {"name": "P", "percent": "50"}]},
    {"name": "Diamônio fosfato (DAP)", "isNutrient": "true", "nutrients": [{"name": "N", "percent": "18"}, {"name": "P", "percent": "43"}]},
    {"name": "Granilhas", "isNutrient": "false", "nutrients": [{"name": "Inerte", "percent": "100"}]},
    {"name": "Calcário granulado", "isNutrient": "false", "nutrients": [{"name": "Inerte", "percent": "100"}]},
    {"name": "Carbonato de Cálcio", "isNutrient": "false", "nutrients": [{"name": "Inerte", "percent": "100"}]},
]
materia_prima_completo = [
    {'name': 'Amônia Anidra', 'nutrients': [{'name': 'N', 'percent': '82'}], 'isNutrient': True},
    {'name': 'Calcário Granulado', 'nutrients': [{'name': 'CaCO₃', 'percent': '59.8'}, {'name': 'MgCO₃', 'percent': '39.7'}], 'isNutrient': False},
    {'name': 'Carbonato de Cálcio', 'nutrients': [{'name': 'CaO', 'percent': '56'}, {'name': 'ECaCO₃', 'percent': '100'}], 'isNutrient': False},
    {'name': 'Carbonato de Magnésio', 'nutrients': [{'name': 'MgO', 'percent': '48'}, {'name': 'ECaCO₃', 'percent': '119'}], 'isNutrient': False},
    {'name': 'Cloreto de Potássio', 'nutrients': [{'name': 'K₂O', 'percent': '61'}, {'name': 'Cl', 'percent': '47'}], 'isNutrient': True},
    {'name': 'Escória de Thomas', 'nutrients': [{'name': 'P₂O₅', 'percent': '19'}, {'name': 'CaO', 'percent': '25'}], 'isNutrient': True},
    {'name': 'Esterco de Curral', 'nutrients': [{'name': 'N', 'percent': '1'}, {'name': 'P₂O₅', 'percent': '1.5'}, {'name': 'K₂O', 'percent': '1'}], 'isNutrient': True},
    {'name': 'Farinha de Ossos', 'nutrients': [{'name': 'P₂O₅', 'percent': '30'}, {'name': 'CaO', 'percent': '36'}], 'isNutrient': True},
    {'name': 'Fosfato Bicálcico', 'nutrients': [{'name': 'P₂O₅', 'percent': '40'}, {'name': 'CaO', 'percent': '30'}], 'isNutrient': True},
    {'name': 'Fosfato Diamônico', 'nutrients': [{'name': 'P₂O₅', 'percent': '45'}, {'name': 'N', 'percent': '18'}], 'isNutrient': True},
    {'name': 'Fosfato Monoamônico', 'nutrients': [{'name': 'P₂O₅', 'percent': '52'}, {'name': 'N', 'percent': '10'}, {'name': 'S', 'percent': '1'}], 'isNutrient': True},
    {'name': 'Granilhas', 'nutrients': [], 'isNutrient': False},
    {'name': 'Hiperfosfato', 'nutrients': [{'name': 'P₂O₅', 'percent': '27'}, {'name': 'CaO', 'percent': '40'}], 'isNutrient': True},
    {'name': 'Nitrato de Amônio', 'nutrients': [{'name': 'N', 'percent': '32'}], 'isNutrient': True},
    {'name': 'Nitrato de Cálcio', 'nutrients': [{'name': 'N', 'percent': '14'}, {'name': 'CaO', 'percent': '18'}], 'isNutrient': True},
    {'name': 'Nitrato de Potássio', 'nutrients': [{'name': 'K₂O', 'percent': '44'}, {'name': 'N', 'percent': '13'}], 'isNutrient': True},
    {'name': 'Nitrocalcio', 'nutrients': [{'name': 'N', 'percent': '27'}], 'isNutrient': True},
    {'name': 'Nitrofosfato', 'nutrients': [{'name': 'P₂O₅', 'percent': '20'}, {'name': 'N', 'percent': '18'}, {'name': 'CaO', 'percent': '12'}], 'isNutrient': True},
    {'name': 'Olinda', 'nutrients': [{'name': 'P₂O₅', 'percent': '26'}, {'name': 'CaO', 'percent': '43'}], 'isNutrient': True},
    {'name': 'Salitre do Chile', 'nutrients': [{'name': 'N', 'percent': '16'}], 'isNutrient': True},
    {'name': 'Salitre Potássico', 'nutrients': [{'name': 'K₂O', 'percent': '14'}, {'name': 'N', 'percent': '15'}], 'isNutrient': True},
    {'name': 'Solução Amoniacal', 'nutrients': [{'name': 'N', 'percent': '20'}], 'isNutrient': True},
    {'name': 'Soluções Nitrogenadas', 'nutrients': [{'name': 'N', 'percent': '35'}], 'isNutrient': True},
    {'name': 'Sulfato de Amônio', 'nutrients': [{'name': 'N', 'percent': '20'}, {'name': 'S', 'percent': '23'}], 'isNutrient': True},
    {'name': 'Sulfato de K e Mg', 'nutrients': [{'name': 'K₂O', 'percent': '22'}, {'name': 'MgO', 'percent': '18'}, {'name': 'S', 'percent': '22'}], 'isNutrient': True},
    {'name': 'Sulfato de Potássio', 'nutrients': [{'name': 'K₂O', 'percent': '50'}, {'name': 'S', 'percent': '18'}], 'isNutrient': True},
    {'name': 'Sulfonitrato de Amônio', 'nutrients': [{'name': 'N', 'percent': '26'}, {'name': 'S', 'percent': '15'}], 'isNutrient': True},
    {'name': 'Superfosfato Simples', 'nutrients': [{'name': 'P₂O₅', 'percent': '21'}, {'name': 'CaO', 'percent': '26'}, {'name': 'S', 'percent': '12'}], 'isNutrient': True},
    {'name': 'Superfosfato Triplo', 'nutrients': [{'name': 'P₂O₅', 'percent': '45'}, {'name': 'CaO', 'percent': '15'}, {'name': 'S', 'percent': '1.5'}], 'isNutrient': True},
    {'name': 'Termofosfato', 'nutrients': [{'name': 'P₂O₅', 'percent': '17'}, {'name': 'CaO', 'percent': '24'}, {'name': 'MgO', 'percent': '7'}], 'isNutrient': True},
    {'name': 'Ureia', 'nutrients': [{'name': 'N', 'percent': '44'}], 'isNutrient': True}
]
materia_prima_selected = [
    {'name': 'Calcário Granulado', 'nutrients': [{'name': 'CaCO₃', 'percent': '59.8'}, {'name': 'MgCO₃', 'percent': '39.7'}], 'isNutrient': False},
    {'name': 'Carbonato de Cálcio', 'nutrients': [{'name': 'CaO', 'percent': '56'}, {'name': 'ECaCO₃', 'percent': '100'}], 'isNutrient': False},
    {'name': 'Carbonato de Magnésio', 'nutrients': [{'name': 'MgO', 'percent': '48'}, {'name': 'ECaCO₃', 'percent': '119'}], 'isNutrient': False},
    {'name': 'Granilhas', 'nutrients': [], 'isNutrient': False},
    {'name': 'Fosfato Diamônico', 'nutrients': [{'name': 'P₂O₅', 'percent': '45'}, {'name': 'N', 'percent': '18'}], 'isNutrient': True},
    {'name': 'Fosfato Monoamônico', 'nutrients': [{'name': 'P₂O₅', 'percent': '52'}, {'name': 'N', 'percent': '10'}, {'name': 'S', 'percent': '1'}], 'isNutrient': True},
    {'name': 'Sulfato de Potássio', 'nutrients': [{'name': 'K₂O', 'percent': '50'}, {'name': 'S', 'percent': '18'}], 'isNutrient': True},
    {'name': 'Cloreto de Potássio', 'nutrients': [{'name': 'K₂O', 'percent': '61'}, {'name': 'Cl', 'percent': '47'}], 'isNutrient': True},
    {'name': 'Sulfato de Amônio', 'nutrients': [{'name': 'N', 'percent': '20'}, {'name': 'S', 'percent': '23'}], 'isNutrient': True},
    {'name': 'Superfosfato Simples', 'nutrients': [{'name': 'P₂O₅', 'percent': '21'}, {'name': 'CaO', 'percent': '26'}, {'name': 'S', 'percent': '12'}], 'isNutrient': True},
    {'name': 'Superfosfato Triplo', 'nutrients': [{'name': 'P₂O₅', 'percent': '45'}, {'name': 'CaO', 'percent': '15'}, {'name': 'S', 'percent': '1.5'}], 'isNutrient': True},
    {'name': 'Ureia', 'nutrients': [{'name': 'N', 'percent': '44'}], 'isNutrient': True}
]

data_use = materia_prima_completo
formulado = "04-30-20"  # Desejo atingir N=10, P=20, K=20
print(f"Formulado: {formulado}")
print(f"Matérias-Primas: {len(data_use)}")
combinacao = gerar_combinacoes_new_(formulado, data_use, step=10)
#combinacao = gerar_combinacoes_sem_step(formulado, materias_primas)
print(f"Total de Enchimentos: {len(combinacao['enchimentos'])}")
print(f"Total de combinações: {combinacao['total']}")

#print("Primeira combinação:")
#print(combinacao['combinations'][-1] if combinacao['combinations'] else "Nenhuma combinação encontrada")

#print(f"Enchimentos: {len(combinacao['enchimentos'])}")
#print(combinacao['enchimentos'] if combinacao['enchimentos'] else "Nenhum enchimento encontrada")

# formulado, combinacoes, enchimentos, target_total=1000
resultados = calcular_fornecimento_new_(
    formulado,
    combinacao['combinations'],
    combinacao['enchimentos'],
    1000,
500)
#print(resultados['aceitos'])
#resultados = {"tempo_processamento": None, "formulado_exigido": formulado, "descartados": 0, "aceitos": []}
print(f"Tempo necessário: {resultados['tempo_processamento']}")
#print(f"Formulado Exigido: {resultados['formulado_exigido']}")
print(f"Descartados: {resultados['descartados']}")
print(f"Formulados Incompativeis: {resultados['formulados_incompativeis']}")
print(f"Enchimentos Incompativeis: {resultados['enchimentos_incompativeis']}")
print(f"Total Enchimentos: {resultados['total_enchimentos']}")
print(f"Limite Enchimentos: {resultados['limite_enchimentos']}kg")
print(f"Aceitos:{len(resultados['aceitos'])}")

#print("Primeira Formulação:")
#print(resultados['aceitos'][0] if resultados['aceitos'] else "Nenhuma formulação encontrada")

print("Última Formulação:")
print(resultados['aceitos'][0] if resultados['aceitos'] else "Nenhuma formulação encontrada")
#print("Primeira combinação:")
#print(combinacao['combinations'][0] if combinacao['combinations'] else "Nenhuma combinação encontrada")

#print("Última combinação:")
#print(combinacao['combinations'][20] if combinacao['combinations'] else "Nenhuma combinação encontrada")

