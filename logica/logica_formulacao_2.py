import time
import itertools
import numpy as np
from itertools import combinations
from itertools import product
from logica.validacao_compatibilidade import validar_compatibilidade, validar_compatibilidade_2
from scipy.optimize import linprog

def gerar_combinacoes_old(formulado, materias_primas, step):
    """
    Gera todas as combinações possíveis de matérias-primas para atender ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        materias_primas (list): Lista de matérias-primas disponíveis.
        step (int): Intervalo de variação das proporções.

    Returns:
        dict: Dicionário contendo o total de combinações e a lista das combinações geradas.
    """

    # Converter formulado de string para dicionário
    formulado_split = formulado.split("-")
    formulado_dict = {
        "N": int(formulado_split[0]),
        "P": int(formulado_split[1]),
        "K": int(formulado_split[2]),
    }

    # Identificar nutrientes que devem ser excluídos
    nutrientes_excluidos = {k for k, v in formulado_dict.items() if v == 0}

    # 1. Separar materiais-primas em arrays
    fornece_N, fornece_P, fornece_K = [], [], []
    fornece_N_P, fornece_N_K, fornece_P_K, fornece_N_P_K = [], [], [], []
    enchimentos = []

    def simplificar_nutriente(nutriente):
        """Simplifica os nomes dos nutrientes para N, P e K."""
        if nutriente.startswith("N"):
            return "N"
        elif nutriente.startswith("P"):
            return "P"
        elif nutriente.startswith("K"):
            return "K"
        return nutriente

    # Separação das matérias-primas por tipo de fornecimento de nutrientes
    for materia in materias_primas:

        is_nutrient = materia.get("isNutrient", True)  # Padrão é True se não estiver presente
        if isinstance(is_nutrient, str):
            is_nutrient = is_nutrient.lower() == "true"  # Converte "true"/"false" para booleano

        if not is_nutrient:
            enchimentos.append(materia)
            continue  # Se não for nutriente, apenas adiciona à lista de enchimentos

        nutrientes = materia["nutrients"]
        nutrient_names = [simplificar_nutriente(n["name"]) for n in nutrientes]

        # Verificar se a matéria-prima contém um nutriente indesejado
        if any(nutriente in nutrientes_excluidos for nutriente in nutrient_names):
            continue  # Ignorar essa matéria-prima

        if len(nutrientes) == 1:
            if "N" in nutrient_names:
                fornece_N.append(materia)
            elif "P" in nutrient_names:
                fornece_P.append(materia)
            elif "K" in nutrient_names:
                fornece_K.append(materia)

        elif len(nutrientes) == 2:
            if "N" in nutrient_names and "P" in nutrient_names:
                fornece_N_P.append(materia)
            elif "N" in nutrient_names and "K" in nutrient_names:
                fornece_N_K.append(materia)
            elif "P" in nutrient_names and "K" in nutrient_names:
                fornece_P_K.append(materia)

        elif len(nutrientes) == 3:
            fornece_N_P_K.append(materia)

    # 2. Gerar combinações com steps
    def gerar_combinacoes_steps(array, step):
        """Gera combinações de proporções para um array com os steps definidos."""
        from itertools import product

        steps = [i for i in range(step, 101, step)]
        combinacoes = []

        for num_itens in range(1, len(array) + 1):
            for combinacao in product(array, repeat=num_itens):
                proporcoes = product(steps, repeat=num_itens)
                for proporcao in proporcoes:
                    if sum(proporcao) == 100:
                        combinacoes.append([
                            {
                                "name": item["name"],
                                "nutrient": {simplificar_nutriente(n["name"]): float(n["percent"]) for n in item["nutrients"]},
                                "proportion": prop,
                                "isNutrient": item["isNutrient"]
                            }
                            for item, prop in zip(combinacao, proporcao)
                        ])

        return combinacoes

    # Gerar combinações para cada grupo
    combinacoes_N = gerar_combinacoes_steps(fornece_N, step)
    combinacoes_P = gerar_combinacoes_steps(fornece_P, step)
    combinacoes_K = gerar_combinacoes_steps(fornece_K, step)
    combinacoes_N_P = gerar_combinacoes_steps(fornece_N_P, step)
    combinacoes_N_K = gerar_combinacoes_steps(fornece_N_K, step)
    combinacoes_P_K = gerar_combinacoes_steps(fornece_P_K, step)
    combinacoes_N_P_K = gerar_combinacoes_steps(fornece_N_P_K, step)

    # 3. Juntar combinações respeitando proporções por nutriente
    def juntar_combinacoes_por_nutriente_separado(combinacoes):
        """Junta combinações separadas por N, P e K."""
        combinacoes_finais = []

        # Iterar por cada combinação base
        for combinacao in combinacoes:
            combinacao_valida = True

            # Verificar proporções dentro de cada nutriente
            for nutriente, materiais in combinacao.items():
                proporcao_total = sum(item["proportion"] for item in materiais)
                if proporcao_total != 100:
                    combinacao_valida = False
                    break

            if combinacao_valida:
                combinacoes_finais.append(combinacao)

        return combinacoes_finais

    # 🔹 Organizar combinações em estrutura separada por nutrientes
    combinacoes_separadas = []

    # **Gerando TODAS as combinações possíveis**
    combinacoes_separadas += [
        {"N": comb_n, "P": comb_p, "K": comb_k}
        for comb_n in (combinacoes_N + combinacoes_N_P + combinacoes_N_K + combinacoes_N_P_K)
        for comb_p in (combinacoes_P + combinacoes_P_K + combinacoes_N_P_K)
        for comb_k in (combinacoes_K + combinacoes_N_K + combinacoes_P_K + combinacoes_N_P_K)
    ]

    # Casos em que um nutriente está zerado
    if formulado_dict["N"] == 0:
        combinacoes_separadas += [
            {"P": comb_p, "K": comb_k}
            for comb_p in (combinacoes_P + combinacoes_P_K)
            for comb_k in (combinacoes_K + combinacoes_P_K)
        ]

    if formulado_dict["P"] == 0:
        combinacoes_separadas += [
            {"N": comb_n, "K": comb_k}
            for comb_n in (combinacoes_N + combinacoes_N_K)
            for comb_k in (combinacoes_K + combinacoes_N_K)
        ]

    if formulado_dict["K"] == 0:
        combinacoes_separadas += [
            {"N": comb_n, "P": comb_p}
            for comb_n in (combinacoes_N + combinacoes_N_P)
            for comb_p in (combinacoes_P + combinacoes_N_P)
        ]

    # Casos individuais (somente um nutriente)
    if formulado_dict["N"] > 0 and formulado_dict["P"] == 0 and formulado_dict["K"] == 0:
        combinacoes_separadas += [{"N": comb_n} for comb_n in combinacoes_N]

    if formulado_dict["P"] > 0 and formulado_dict["N"] == 0 and formulado_dict["K"] == 0:
        combinacoes_separadas += [{"P": comb_p} for comb_p in combinacoes_P]

    if formulado_dict["K"] > 0 and formulado_dict["N"] == 0 and formulado_dict["P"] == 0:
        combinacoes_separadas += [{"K": comb_k} for comb_k in combinacoes_K]

    # 🔹 Filtrar combinações válidas
    combinacoes_finais = juntar_combinacoes_por_nutriente_separado(combinacoes_separadas)

    # 🔹 Adicionar enchimentos às combinações existentes
    if enchimentos:
        novas_combinacoes = []
        for combinacao in combinacoes_finais:
            for enchimento in enchimentos:
                combinacao_com_enchimento = combinacao.copy()
                combinacao_com_enchimento["Enchimento"] = [enchimento]
                novas_combinacoes.append(combinacao_com_enchimento)
        combinacoes_finais.extend(novas_combinacoes)

    return {
        "total": len(combinacoes_finais),
        "combinations": combinacoes_finais
    }

def gerar_combinacoes(formulado, materias_primas, step):
    """
    Gera todas as combinações possíveis de matérias-primas para atender ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        materias_primas (list): Lista de matérias-primas disponíveis.
        step (int): Intervalo de variação das proporções.

    Returns:
        dict: Dicionário contendo o total de combinações e a lista das combinações geradas.
    """

    # Converter formulado de string para dicionário
    formulado_split = formulado.split("-")
    formulado_dict = {
        "N": int(formulado_split[0]),
        "P": int(formulado_split[1]),
        "K": int(formulado_split[2]),
    }

    # Identificar nutrientes que devem ser excluídos
    nutrientes_excluidos = {k for k, v in formulado_dict.items() if v == 0}

    # 1. Separar materiais-primas em arrays
    fornece_N, fornece_P, fornece_K = [], [], []
    fornece_N_P, fornece_N_K, fornece_P_K, fornece_N_P_K = [], [], [], []
    enchimentos = []

    def simplificar_nutriente(nutriente):
        """Simplifica os nomes dos nutrientes para N, P e K."""
        if nutriente.startswith("N"):
            return "N"
        elif nutriente.startswith("P"):
            return "P"
        elif nutriente.startswith("K"):
            return "K"
        return nutriente

    # Separação das matérias-primas por tipo de fornecimento de nutrientes
    for materia in materias_primas:
        is_nutrient = materia.get("isNutrient", True)
        if isinstance(is_nutrient, str):
            is_nutrient = is_nutrient.lower() == "true"

        if not is_nutrient:
            enchimentos.append(materia)
            continue  # Se não for nutriente, adiciona à lista de enchimentos e pula para a próxima matéria-prima

        nutrientes = materia["nutrients"]

        # Filtrar apenas os nutrientes N, P e K para categorização correta
        nutrient_names = [
            simplificar_nutriente(n["name"]) for n in nutrientes if simplificar_nutriente(n["name"]) in {"N", "P", "K"}
        ]

        # Se a matéria-prima contém um nutriente excluído, ignoramos ela
        if any(nutriente in nutrientes_excluidos for nutriente in nutrient_names):
            continue

            # **Classificação correta baseada SOMENTE em N, P e K**
        if len(nutrient_names) == 1:
            if "N" in nutrient_names:
                fornece_N.append(materia)
            elif "P" in nutrient_names:
                fornece_P.append(materia)
            elif "K" in nutrient_names:
                fornece_K.append(materia)

        elif len(nutrient_names) == 2:
            if "N" in nutrient_names and "P" in nutrient_names:
                fornece_N_P.append(materia)
            elif "N" in nutrient_names and "K" in nutrient_names:
                fornece_N_K.append(materia)
            elif "P" in nutrient_names and "K" in nutrient_names:
                fornece_P_K.append(materia)

        elif len(nutrient_names) == 3:
            fornece_N_P_K.append(materia)
    # 2. Gerar combinações com steps
    def gerar_combinacoes_steps(array, step):
        """Gera combinações de proporções para um array com os steps definidos."""
        from itertools import product

        steps = [i for i in range(step, 101, step)]
        combinacoes = []

        for num_itens in range(1, len(array) + 1):
            for combinacao in product(array, repeat=num_itens):
                proporcoes = product(steps, repeat=num_itens)
                for proporcao in proporcoes:
                    if sum(proporcao) == 100:
                        combinacoes.append([
                            {
                                "name": item["name"],
                                "nutrient": {simplificar_nutriente(n["name"]): float(n["percent"]) for n in item["nutrients"]},
                                "proportion": prop,
                                "isNutrient": item["isNutrient"]
                            }
                            for item, prop in zip(combinacao, proporcao)
                        ])

        return combinacoes

    print(f"Fornece N: {len(fornece_N)}")
    print(f"Fornece P: {len(fornece_P)}")
    print(f"Fornece K: {len(fornece_K)}")
    print(f"Fornece N_P: {len(fornece_N_P)}")
    print(f"Fornece N_K: {len(fornece_N_K)}")
    print(f"Fornece P_K: {len(fornece_P_K)}")
    print(f"Fornece N_P_K: {len(fornece_N_P_K)}")
    print(f"Enchimentos: {len(enchimentos)}")

    # Ordenar cada lista de matérias-primas pelo valor do maior nutriente (N, P ou K) que fornece, em ordem decrescente.
    def get_max_nutrient(materia):
        # Pega somente os nutrientes relevantes e converte o percentual para float.
        nutrientes = [
            float(n["percent"])
            for n in materia["nutrients"]
            if simplificar_nutriente(n["name"]) in {"N", "P", "K"}
        ]
        return max(nutrientes) if nutrientes else 0

    fornece_N.sort(key=get_max_nutrient, reverse=True)
    fornece_P.sort(key=get_max_nutrient, reverse=True)
    fornece_K.sort(key=get_max_nutrient, reverse=True)
    fornece_N_P.sort(key=get_max_nutrient, reverse=True)
    fornece_N_K.sort(key=get_max_nutrient, reverse=True)
    fornece_P_K.sort(key=get_max_nutrient, reverse=True)
    fornece_N_P_K.sort(key=get_max_nutrient, reverse=True)

    # Gerar combinações para cada grupo
    combinacoes_N = gerar_combinacoes_steps(fornece_N, step)
    combinacoes_P = gerar_combinacoes_steps(fornece_P, step)
    combinacoes_K = gerar_combinacoes_steps(fornece_K, step)
    combinacoes_N_P = gerar_combinacoes_steps(fornece_N_P, step)
    combinacoes_N_K = gerar_combinacoes_steps(fornece_N_K, step)
    combinacoes_P_K = gerar_combinacoes_steps(fornece_P_K, step)
    combinacoes_N_P_K = gerar_combinacoes_steps(fornece_N_P_K, step)

    # 3. Juntar combinações respeitando proporções por nutriente
    def juntar_combinacoes_por_nutriente_separado(combinacoes):
        """Junta combinações separadas por N, P e K."""
        combinacoes_finais = []

        # Iterar por cada combinação base
        for combinacao in combinacoes:
            combinacao_valida = True

            # Verificar proporções dentro de cada nutriente
            for nutriente, materiais in combinacao.items():
                proporcao_total = sum(item["proportion"] for item in materiais)
                if proporcao_total != 100:
                    combinacao_valida = False
                    break

            if combinacao_valida:
                combinacoes_finais.append(combinacao)

        return combinacoes_finais

    # 🔹 Organizar combinações em estrutura separada por nutrientes
    combinacoes_separadas = []

    # **Gerando TODAS as combinações possíveis**
    combinacoes_separadas += [
        {"N": comb_n, "P": comb_p, "K": comb_k}
        for comb_n in (combinacoes_N + combinacoes_N_P + combinacoes_N_K + combinacoes_N_P_K)
        for comb_p in (combinacoes_P + combinacoes_P_K + combinacoes_N_P_K)
        for comb_k in (combinacoes_K + combinacoes_N_K + combinacoes_P_K + combinacoes_N_P_K)
    ]

    # Casos em que um nutriente está zerado
    if formulado_dict["N"] == 0:
        combinacoes_separadas += [
            {"P": comb_p, "K": comb_k}
            for comb_p in (combinacoes_P + combinacoes_P_K)
            for comb_k in (combinacoes_K + combinacoes_P_K)
        ]

    if formulado_dict["P"] == 0:
        combinacoes_separadas += [
            {"N": comb_n, "K": comb_k}
            for comb_n in (combinacoes_N + combinacoes_N_K)
            for comb_k in (combinacoes_K + combinacoes_N_K)
        ]

    if formulado_dict["K"] == 0:
        combinacoes_separadas += [
            {"N": comb_n, "P": comb_p}
            for comb_n in (combinacoes_N + combinacoes_N_P)
            for comb_p in (combinacoes_P + combinacoes_N_P)
        ]

    # Casos individuais (somente um nutriente)
    if formulado_dict["N"] > 0 and formulado_dict["P"] == 0 and formulado_dict["K"] == 0:
        combinacoes_separadas += [{"N": comb_n} for comb_n in combinacoes_N]

    if formulado_dict["P"] > 0 and formulado_dict["N"] == 0 and formulado_dict["K"] == 0:
        combinacoes_separadas += [{"P": comb_p} for comb_p in combinacoes_P]

    if formulado_dict["K"] > 0 and formulado_dict["N"] == 0 and formulado_dict["P"] == 0:
        combinacoes_separadas += [{"K": comb_k} for comb_k in combinacoes_K]

    # 🔹 Filtrar combinações válidas
    combinacoes_finais = juntar_combinacoes_por_nutriente_separado(combinacoes_separadas)

    # 🔹 Adicionar enchimentos às combinações existentes
    if enchimentos:
        novas_combinacoes = []
        for combinacao in combinacoes_finais:
            for enchimento in enchimentos:
                combinacao_com_enchimento = combinacao.copy()
                combinacao_com_enchimento["Enchimento"] = [enchimento]
                novas_combinacoes.append(combinacao_com_enchimento)
        combinacoes_finais.extend(novas_combinacoes)

    return {
        "total": len(combinacoes_finais),
        "combinations": combinacoes_finais
    }

def calcular_fornecimento(formulado, combinacoes, target_total=1000):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação, verificando se atendem ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        combinacoes (list/dict): Lista de combinações ou dicionário contendo "combinations".
        target_total (int): Total desejado (em kg). Padrão: 1000 kg.

    Returns:
        dict: Resultados com combinações aceitas, descartadas e tempo de processamento.
    """
    start_time = time.time()

    try:
        target_n, target_p, target_k = map(float, formulado.split('-'))
    except ValueError:
        raise ValueError("Erro: O formulado deve estar no formato correto, ex: '10-10-10'.")

    # Converter para kg na tonelada
    target_n = (target_n * target_total) / 100
    target_p = (target_p * target_total) / 100
    target_k = (target_k * target_total) / 100

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    # 🔹 **Garantir que combinacoes seja uma lista válida**
    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])  # Pegar lista dentro do dicionário

    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    for combinacao in combinacoes:
        if not isinstance(combinacao, dict):
            print(f"⚠️ Aviso: Ignorando combinação inválida: {combinacao}")
            continue

        total_kg = 0
        fornecimento_real = {"N": 0, "P": 0, "K": 0}
        materias_selecionadas = []

        for nutriente, itens in combinacao.items():
            if not isinstance(itens, list):
                continue  # Ignorar se não for uma lista válida

            for item in itens:
                if not isinstance(item, dict):
                    print(f"⚠️ Aviso: Item inválido encontrado: {item}")
                    continue

                nome_mp = item.get("name", "Desconhecido")
                proporcao = item.get("proportion", 0) / 100  # Converter para fração decimal
                nutrientes = item.get("nutrient", {})
                isNutrient = item.get("isNutrient", False)

                if not isinstance(nutrientes, dict):
                    print(f"⚠️ Aviso: Nutrientes inválidos para {nome_mp}: {nutrientes}")
                    continue

                for nome_nutriente, teor_percent in nutrientes.items():
                    if not isinstance(teor_percent, (int, float)):
                        print(f"⚠️ Aviso: Teor inválido encontrado para {nome_mp}: {teor_percent}")
                        continue

                    # 🔹 **Calcular a quantidade real necessária de cada matéria-prima**
                    if nome_nutriente.startswith("N"):
                        kg_mp = (target_n * 100) / teor_percent
                        kg_real = kg_mp * proporcao
                        fornecimento_real["N"] += kg_real
                    elif nome_nutriente.startswith("P"):
                        kg_mp = (target_p * 100) / teor_percent
                        kg_real = kg_mp * proporcao
                        fornecimento_real["P"] += kg_real
                    elif nome_nutriente.startswith("K"):
                        kg_mp = (target_k * 100) / teor_percent
                        kg_real = kg_mp * proporcao
                        fornecimento_real["K"] += kg_real

                    total_kg += kg_real

                    nutrientes_calculados = {
                        nome_nutriente: (teor_percent * kg_real) / 100
                        for nome_nutriente, teor_percent in nutrientes.items()
                    }

                    for nome_nutriente, fornecido in nutrientes_calculados.items():
                        if nome_nutriente.startswith("N"):
                            fornecimento_real["N"] += fornecido
                        elif nome_nutriente.startswith("P"):
                            fornecimento_real["P"] += fornecido
                        elif nome_nutriente.startswith("K"):
                            fornecimento_real["K"] += fornecido

                    #materias_selecionadas.append({"materia": nome_mp, "kg": kg_real})
                    materias_selecionadas.append({
                        "name": nome_mp,
                        "kg": kg_real,
                        "nutrients": nutrientes_calculados,
                        "isNutrient": isNutrient
                    })


        # 🔹 **Log detalhado do fornecimento calculado**
        #print(f"Fornecimento calculado para combinação: {fornecimento_real}")

        # 🔹 **Descartar se ultrapassar 1000 kg**
        if total_kg > target_total:
            #print(f"❌ Descartado: Extrapolou o limite de {target_total} kg. Total calculado: {total_kg:.2f} kg")
            resultados["descartados"] += 1
            continue

        # 🔹 **Ajuste para completar 1000kg**
        if total_kg < target_total:
            enchimento = combinacao.get("Enchimento", [])
            if enchimento:
                enchimento = enchimento[0]
                materias_selecionadas.append({
                    "name": enchimento["name"],
                    "kg": round(target_total - total_kg, 2),
                    "nutrients": {},
                    "isNutrient": False
                })
            else:
                resultados["descartados"] += 1
                #print("⚠️ Aviso: Nenhum enchimento encontrado na combinação para completar 1000kg.")


        #print(f"✅ Aceito: Combinação válida com fornecimento: {fornecimento_real}")
        #print(materias_selecionadas)
        materiais_filtrados = combinar_materiais(materias_selecionadas)
        compatibility_result = validar_compatibilidade(materiais_filtrados)

        resultado_final = {
            "materiais": materiais_filtrados,
            "compatibility": compatibility_result["compatibility"],
            "limited": compatibility_result["limited"],
            "incompatible": compatibility_result["incompatible"],
            "message": compatibility_result["message"]
        }
        resultados["aceitos"].append(resultado_final)

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados

def combinar_materiais(materiais):
    """
    Agrupa materiais repetidos, somando seus valores de kg e nutrientes,
    mantendo duas casas decimais para os valores calculados.

    Args:
        materiais (list): Lista de materiais selecionados.

    Returns:
        list: Lista de materiais combinados e ordenados alfabeticamente.
    """
    from collections import defaultdict

    materiais_combinados = defaultdict(lambda: {"kg": 0, "nutrients": defaultdict(float)})
    #print(materiais)
    for material in materiais:
        nome = material["name"]
        kg = round(material["kg"], 2)  # Mantém duas casas decimais
        nutrientes = material["nutrients"]
        materiais_combinados[nome]["isNutrient"] = material['isNutrient']
        materiais_combinados[nome]["kg"] += kg  # Soma os kg
        for nutriente, valor in nutrientes.items():
            materiais_combinados[nome]["nutrients"][nutriente] += round(valor, 2)  # Soma nutrientes

    # Converter defaultdict para lista formatada
    materiais_ordenados = sorted(
        [
            {
                "name": nome,
                "kg": round(dados["kg"], 2),
                "nutrients": {nutriente: round(valor, 2) for nutriente, valor in dados["nutrients"].items()},
                "isNutrient": dados['isNutrient']
            }
            for nome, dados in materiais_combinados.items()
        ],
        key=lambda x: (not x["isNutrient"], x["name"])  # Ordena isNutrient=True primeiro, depois por nome
    )

    return materiais_ordenados


def calcular_fornecimento_old(formulado, combinacoes, target_total=1000, tolerancia=0.05):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação, testando diferentes ordens e
    aplicando uma margem de tolerância.
    """
    start_time = time.time()

    try:
        target_n, target_p, target_k = map(float, formulado.split('-'))
    except ValueError:
        raise ValueError("Erro: O formulado deve estar no formato correto, ex: '10-10-10'.")

    # Converter para kg na tonelada
    target_n = (target_n * target_total) / 100
    target_p = (target_p * target_total) / 100
    target_k = (target_k * target_total) / 100

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])

    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    def calcular_por_ordem(combinacao, ordem):
        """Calcula o fornecimento real com base na ordem especificada."""
        total_kg = 0
        fornecimento_real = {"N": 0, "P": 0, "K": 0}
        materias_selecionadas = []

        for nutriente in ordem:
            itens = combinacao.get(nutriente, [])
            for item in itens:
                nome_mp = item.get("name", "Desconhecido")
                proporcao = item.get("proportion", 0) / 100
                nutrientes = item.get("nutrient", {})
                isNutrient = item.get("isNutrient", False)

                for nome_nutriente, teor_percent in nutrientes.items():
                    if not isinstance(teor_percent, (int, float)) or teor_percent <= 0:
                        continue

                    if nome_nutriente.startswith(nutriente):
                        kg_mp = (eval(f"target_{nutriente.lower()}") * 100) / teor_percent
                        kg_real = kg_mp * proporcao
                        fornecimento_real[nutriente] += kg_real
                        total_kg += kg_real

                        nutrientes_calculados = {
                            nome_nutriente: (teor_percent * kg_real) / 100
                            for nome_nutriente, teor_percent in nutrientes.items()
                        }

                        materias_selecionadas.append({
                            "name": nome_mp,
                            "kg": kg_real,
                            "nutrients": nutrientes_calculados,
                            "isNutrient": isNutrient
                        })

        return fornecimento_real, total_kg, materias_selecionadas

    for combinacao in combinacoes:
        melhor_resultado = None
        melhor_diferenca = float("inf")
        ordens = [("N", "P", "K"), ("P", "K", "N"), ("K", "N", "P")]

        for ordem in ordens:
            fornecimento_real, total_kg, materias_selecionadas = calcular_por_ordem(combinacao, ordem)

            # Verifica se a combinação atende ao formulado dentro da margem de tolerância
            diferenca_total = sum(abs(fornecimento_real[n] - eval(f"target_{n.lower()}") for n in ["N", "P", "K"]))

            if diferenca_total < melhor_diferenca and total_kg <= target_total * (1 + tolerancia):
                melhor_resultado = (fornecimento_real, total_kg, materias_selecionadas)
                melhor_diferenca = diferenca_total

        if melhor_resultado is None:
            resultados["descartados"] += 1
            continue

        fornecimento_real, total_kg, materias_selecionadas = melhor_resultado

        # Ajuste para completar 1000kg
        if total_kg < target_total:
            enchimento = combinacao.get("Enchimento", [])
            if enchimento:
                enchimento = enchimento[0]
                materias_selecionadas.append({
                    "name": enchimento["name"],
                    "kg": round(target_total - total_kg, 2),
                    "nutrients": {},
                    "isNutrient": False
                })
            else:
                resultados["descartados"] += 1
                continue

        materiais_filtrados = combinar_materiais(materias_selecionadas)
        compatibility_result = validar_compatibilidade(materiais_filtrados)

        resultado_final = {
            "materiais": materiais_filtrados,
            "compatibility": compatibility_result["compatibility"],
            "limited": compatibility_result["limited"],
            "incompatible": compatibility_result["incompatible"],
            "message": compatibility_result["message"]
        }
        resultados["aceitos"].append(resultado_final)

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados


def calcular_fornecimento_old_2(formulado, combinacoes, target_total=1000, tolerancia=0.05):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação, verificando se atendem ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        combinacoes (list/dict): Lista de combinações ou dicionário contendo "combinations".
        target_total (int): Total desejado (em kg). Padrão: 1000 kg.
        tolerancia (float): Margem de tolerância na aceitação da combinação.

    Returns:
        dict: Resultados com combinações aceitas, descartadas e tempo de processamento.
    """
    start_time = time.time()

    try:
        target_n, target_p, target_k = map(float, formulado.split('-'))
    except ValueError:
        raise ValueError("Erro: O formulado deve estar no formato correto, ex: '10-10-10'.")

    # Converter para kg na tonelada
    target_n = (target_n * target_total) / 100
    target_p = (target_p * target_total) / 100
    target_k = (target_k * target_total) / 100

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    # Garantir que combinacoes seja uma lista válida
    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])

    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    def calcular_por_ordem(combinacao, ordem, target_n, target_p, target_k):
        """Executa o cálculo seguindo uma ordem específica de nutrientes."""
        fornecimento_real = {"N": 0, "P": 0, "K": 0}
        total_kg = 0
        materias_selecionadas = []

        targets = {"N": target_n, "P": target_p, "K": target_k}

        for nutriente in ordem:
            if nutriente not in combinacao:
                continue

            for item in combinacao[nutriente]:
                nome_mp = item.get("name", "Desconhecido")
                proporcao = item.get("proportion", 0) / 100
                nutrientes = item.get("nutrient", {})
                isNutrient = item.get("isNutrient", False)

                for nome_nutriente, teor_percent in nutrientes.items():
                    if not isinstance(teor_percent, (int, float)) or teor_percent == 0:
                        continue

                    kg_mp = (targets[nutriente] * 100) / teor_percent
                    kg_real = kg_mp * proporcao
                    fornecimento_real[nutriente] += kg_real
                    total_kg += kg_real

                    nutrientes_calculados = {
                        nome_nutriente: (teor_percent * kg_real) / 100
                        for nome_nutriente, teor_percent in nutrientes.items()
                    }

                    materias_selecionadas.append({
                        "name": nome_mp,
                        "kg": kg_real,
                        "nutrients": nutrientes_calculados,
                        "isNutrient": isNutrient
                    })

        return fornecimento_real, total_kg, materias_selecionadas

    ordens_teste = [["N", "P", "K"], ["P", "K", "N"], ["K", "N", "P"]]

    for combinacao in combinacoes:
        for ordem in ordens_teste:
            fornecimento_real, total_kg, materias_selecionadas = calcular_por_ordem(combinacao, ordem, target_n,
                                                                                    target_p, target_k)

            dentro_da_tolerancia = all(
                abs(fornecimento_real[n] - eval(f"target_{n.lower()}")) <= eval(f"target_{n.lower()}") * tolerancia
                for n in ["N", "P", "K"]
            )

            if dentro_da_tolerancia:
                resultado_final = {
                    "materiais": materias_selecionadas,
                    "compatibility": True,  # Validação de compatibilidade pode ser adicionada aqui
                    "limited": False,
                    "incompatible": False,
                    "message": "Dentro da tolerância de 5%"
                }
                resultados["aceitos"].append(resultado_final)
                break  # Se uma ordem foi aceita, não testamos as demais

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados

def calcular_fornecimento_new(formulado, combinacoes, target_total=1000, tolerancia=0.05):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação, verificando se atendem ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        combinacoes (list/dict): Lista de combinações ou dicionário contendo "combinations".
        target_total (int): Total desejado (em kg). Padrão: 1000 kg.
        tolerancia (float): Margem de tolerância na aceitação da combinação (padrão 5%).

    Returns:
        dict: Resultados com combinações aceitas, descartadas e tempo de processamento.
    """
    start_time = time.time()

    try:
        target_n, target_p, target_k = map(float, formulado.split('-'))
    except ValueError:
        raise ValueError("Erro: O formulado deve estar no formato correto, ex: '10-10-10'.")

    # Converter para kg na tonelada
    target_n = (target_n * target_total) / 100
    target_p = (target_p * target_total) / 100
    target_k = (target_k * target_total) / 100

    target_values = {"N": target_n, "P": target_p, "K": target_k}

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])

    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    ordens_de_teste = [
        ["N", "P", "K"],
        ["P", "K", "N"],
        ["K", "N", "P"]
    ]

    def calcular_por_ordem(combinacao, ordem):
        fornecimento_real = {"N": 0, "P": 0, "K": 0}
        total_kg = 0
        materias_selecionadas = []

        for nutriente in ordem:
            if nutriente not in combinacao:
                continue

            for item in combinacao[nutriente]:
                nome_mp = item.get("name", "Desconhecido")
                proporcao = item.get("proportion", 0) / 100
                nutrientes = item.get("nutrient", {})
                isNutrient = item.get("isNutrient", False)

                for nome_nutriente, teor_percent in nutrientes.items():
                    if nome_nutriente.startswith(nutriente):
                        kg_mp = (target_values[nutriente] * 100) / teor_percent
                        kg_real = kg_mp * proporcao
                        fornecimento_real[nutriente] += kg_real
                        total_kg += kg_real

                        nutrientes_calculados = {
                            nome_nutriente: (teor_percent * kg_real) / 100
                            for nome_nutriente, teor_percent in nutrientes.items()
                        }

                        materias_selecionadas.append({
                            "name": nome_mp,
                            "kg": kg_real,
                            "nutrients": nutrientes_calculados,
                            "isNutrient": isNutrient
                        })

        return fornecimento_real, total_kg, materias_selecionadas

    for combinacao in combinacoes:
        if not isinstance(combinacao, dict):
            continue

        for ordem in ordens_de_teste:
            fornecimento_real, total_kg, materias_selecionadas = calcular_por_ordem(combinacao, ordem)

            # Verifica se o fornecimento está dentro da tolerância
            dentro_da_tolerancia = all(
                abs(fornecimento_real[n] - target_values[n]) <= target_values[n] * tolerancia
                for n in ["N", "P", "K"]
            )

            if dentro_da_tolerancia:
                break  # Se encontrar uma ordem válida, sai do loop

        if not dentro_da_tolerancia:
            resultados["descartados"] += 1
            continue

        # Ajuste para completar 1000kg com enchimento da própria combinação
        if total_kg < target_total:
            enchimento = combinacao.get("Enchimento", [])
            if enchimento:
                enchimento = enchimento[0]
                materias_selecionadas.append({
                    "name": enchimento["name"],
                    "kg": round(target_total - total_kg, 2),
                    "nutrients": {},
                    "isNutrient": False
                })
            else:
                resultados["descartados"] += 1
                continue

        materiais_filtrados = combinar_materiais(materias_selecionadas)
        compatibility_result = validar_compatibilidade(materiais_filtrados)

        resultado_final = {
            "materiais": materiais_filtrados,
            "compatibility": compatibility_result["compatibility"],
            "limited": compatibility_result["limited"],
            "incompatible": compatibility_result["incompatible"],
            "message": compatibility_result["message"]
        }
        resultados["aceitos"].append(resultado_final)

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados


def gerar_combinacoes_sem_step(formulado, materias_primas):
    """
    Gera todas as combinações possíveis de matérias-primas para atender ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        materias_primas (list): Lista de matérias-primas disponíveis.

    Returns:
        dict: Dicionário contendo o total de combinações e a lista das combinações geradas.
    """

    print(f"Matéria-Prima: {len(materias_primas)}")
    # Converter formulado para dicionário
    formulado_split = formulado.split("-")
    formulado_dict = {
        "N": int(formulado_split[0]),
        "P": int(formulado_split[1]),
        "K": int(formulado_split[2]),
    }

    # Identificar nutrientes que devem ser excluídos
    nutrientes_excluidos = {k for k, v in formulado_dict.items() if v == 0}

    # Separar matérias-primas
    fornece_N, fornece_P, fornece_K = [], [], []
    fornece_N_P, fornece_N_K, fornece_P_K, fornece_N_P_K = [], [], [], []
    enchimentos = []

    def simplificar_nutriente(nutriente):
        if nutriente.startswith("N"): return "N"
        if nutriente.startswith("P"): return "P"
        if nutriente.startswith("K"): return "K"
        return None

    for materia in materias_primas:
        is_nutrient = materia.get("isNutrient", True)
        if isinstance(is_nutrient, str):
            is_nutrient = is_nutrient.lower() == "true"

        if not is_nutrient:
            enchimentos.append(materia)
            continue

        nutrientes = materia["nutrients"]
        nutrient_names = [simplificar_nutriente(n["name"]) for n in nutrientes if
                          simplificar_nutriente(n["name"]) is not None]

        # Se a matéria-prima fornece um nutriente que deve ser excluído, ignoramos
        if any(nutriente in nutrientes_excluidos for nutriente in nutrient_names):
            continue

        if len(nutrient_names) == 1:
            if "N" in nutrient_names:
                fornece_N.append(materia)
            elif "P" in nutrient_names:
                fornece_P.append(materia)
            elif "K" in nutrient_names:
                fornece_K.append(materia)
        elif len(nutrient_names) == 2:
            if "N" in nutrient_names and "P" in nutrient_names:
                fornece_N_P.append(materia)
            elif "N" in nutrient_names and "K" in nutrient_names:
                fornece_N_K.append(materia)
            elif "P" in nutrient_names and "K" in nutrient_names:
                fornece_P_K.append(materia)
        elif len(nutrient_names) == 3:
            fornece_N_P_K.append(materia)

    # Criar combinações sem step
    combinacoes = []
    categorias = [fornece_N, fornece_P, fornece_K, fornece_N_P, fornece_N_K, fornece_P_K, fornece_N_P_K]
    print(f"Range: {len(categorias) + 1}")
    for n in range(1, len(categorias) + 1):
        for combinacao in combinations(categorias, n):
            combinacao_final = {"N": [], "P": [], "K": []}
            for grupo in combinacao:
                for materia in grupo:
                    for nutriente in materia["nutrients"]:
                        nome_nutriente = simplificar_nutriente(nutriente["name"])
                        if nome_nutriente and nome_nutriente in combinacao_final:
                            combinacao_final[nome_nutriente].append(materia)
            combinacoes.append(combinacao_final)

    return {
        "total": len(combinacoes),
        "combinations": combinacoes
    }


def gerar_combinacoes_compatibilidade(formulado, materias_primas):
    """
    Gera combinações de matérias-primas garantindo compatibilidade.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        materias_primas (list): Lista de matérias-primas disponíveis.

    Returns:
        dict: Total de combinações válidas e a lista de combinações geradas.
    """

    print(f"Materia-Prima: {len(materias_primas)}")
    todas_combinacoes = gerar_combinacoes_sem_step(formulado, materias_primas)  # Gera todas as combinações possíveis
    combinacoes_validas = []

    for combinacao in todas_combinacoes["combinations"]:

        materiais_para_validacao = (
                combinacao.get("N", []) +
                combinacao.get("P", []) +
                combinacao.get("K", [])
        )

        # 🔹 Verifica se a combinação contém materiais válidos
        if not isinstance(materiais_para_validacao, list) or len(materiais_para_validacao) == 0:
            #print(f"⚠️ Combinação sem materiais válidos: {combinacao}")
            continue  # Pula essa combinação

        # 🔹 Valida compatibilidade usando a nova estrutura
        resultado_validacao = validar_compatibilidade(materiais_para_validacao)

        if resultado_validacao["incompatible"]:
            continue  # Descarta combinações que tenham materiais incompatíveis

        # Adiciona um campo de validação na combinação
        combinacao["compatibility_check"] = resultado_validacao
        combinacoes_validas.append(combinacao)

    return {
        "total": len(combinacoes_validas),
        "combinations": combinacoes_validas
    }


def calcular_fornecimento_com_validacao(formulado, combinacoes, target_total=1000):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação e valida compatibilidade.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        combinacoes (list/dict): Lista de combinações validadas.
        target_total (int): Total desejado (em kg). Padrão: 1000 kg.

    Returns:
        dict: Resultados filtrados com combinações aceitas, descartadas e tempo de processamento.
    """
    start_time = time.time()

    # Se combinacoes for um dicionário, extrair a lista
    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    for combinacao in combinacoes:
        if not isinstance(combinacao, dict):
            continue

        # Verifica compatibilidade antes do cálculo
        if combinacao.get("compatibility_check", {}).get("incompatible", False):
            resultados["descartados"] += 1
            continue  # Pula essa combinação

        # Aqui entraria o código para calcular os fornecimentos de N, P e K...
        # ...

        resultados["aceitos"].append(combinacao)

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados


def gerar_combinacoes_(formulado: str, materias_primas: list, step: int) -> dict:
    """
    Gera todas as combinações possíveis de matérias-primas para atender ao formulado desejado.

    Args:
        formulado (str): Fórmula desejada no formato "N-P-K".
        materias_primas (list): Lista de matérias-primas disponíveis.
        step (int): Intervalo de variação das proporções.

    Returns:
        dict: Dicionário contendo o total de combinações e a lista das combinações geradas.
    """
    # Converter formulado para dicionário
    formulado_split = formulado.split("-")
    formulado_dict = {
        "N": int(formulado_split[0]),
        "P": int(formulado_split[1]),
        "K": int(formulado_split[2]),
    }

    # Identificar nutrientes a serem excluídos (valor zero)
    nutrientes_excluidos = {k for k, v in formulado_dict.items() if v == 0}

    # Inicializar arrays para as matérias-primas
    fornece_N, fornece_P, fornece_K = [], [], []
    fornece_N_P, fornece_N_K, fornece_P_K, fornece_N_P_K = [], [], [], []
    enchimentos = []

    def simplificar_nutriente(nutriente: str) -> str:
        """Simplifica os nomes dos nutrientes para N, P e K."""
        if nutriente.startswith("N"):
            return "N"
        elif nutriente.startswith("P"):
            return "P"
        elif nutriente.startswith("K"):
            return "K"
        return nutriente

    # Separar matérias-primas em arrays conforme os nutrientes fornecidos
    for materia in materias_primas:
        is_nutrient = materia.get("isNutrient", True)
        if isinstance(is_nutrient, str):
            is_nutrient = is_nutrient.lower() == "true"

        if not is_nutrient:
            enchimentos.append(materia)
            continue

        nutrientes = materia["nutrients"]
        nutrient_names = [
            simplificar_nutriente(n["name"])
            for n in nutrientes
            if simplificar_nutriente(n["name"]) in {"N", "P", "K"}
        ]

        # Se a matéria contém um nutriente excluído, ignora
        if any(n in nutrientes_excluidos for n in nutrient_names):
            continue

        # Classificação baseada apenas em N, P e K
        if len(nutrient_names) == 1:
            if "N" in nutrient_names:
                fornece_N.append(materia)
            elif "P" in nutrient_names:
                fornece_P.append(materia)
            elif "K" in nutrient_names:
                fornece_K.append(materia)
        elif len(nutrient_names) == 2:
            if "N" in nutrient_names and "P" in nutrient_names:
                fornece_N_P.append(materia)
            elif "N" in nutrient_names and "K" in nutrient_names:
                fornece_N_K.append(materia)
            elif "P" in nutrient_names and "K" in nutrient_names:
                fornece_P_K.append(materia)
        elif len(nutrient_names) == 3:
            fornece_N_P_K.append(materia)

    # Ordenar cada lista pelo maior valor do nutriente fornecido (ordem decrescente)
    def get_max_nutrient(materia):
        valores = [
            float(n["percent"])
            for n in materia["nutrients"]
            if simplificar_nutriente(n["name"]) in {"N", "P", "K"}
        ]
        return max(valores) if valores else 0

    fornece_N.sort(key=get_max_nutrient, reverse=True)
    fornece_P.sort(key=get_max_nutrient, reverse=True)
    fornece_K.sort(key=get_max_nutrient, reverse=True)
    fornece_N_P.sort(key=get_max_nutrient, reverse=True)
    fornece_N_K.sort(key=get_max_nutrient, reverse=True)
    fornece_P_K.sort(key=get_max_nutrient, reverse=True)
    fornece_N_P_K.sort(key=get_max_nutrient, reverse=True)

    # Gerar combinações com steps
    def gerar_combinacoes_steps(array, step):
        steps = [i for i in range(step, 101, step)]
        combinacoes = []
        for num_itens in range(1, len(array) + 1):
            for combinacao in product(array, repeat=num_itens):
                for proporcao in product(steps, repeat=num_itens):
                    if sum(proporcao) == 100:
                        combinacoes.append([
                            {
                                "name": item["name"],
                                "nutrient": {simplificar_nutriente(n["name"]): float(n["percent"]) for n in item["nutrients"]},
                                "proportion": prop,
                                "isNutrient": item["isNutrient"]
                            }
                            for item, prop in zip(combinacao, proporcao)
                        ])
        return combinacoes

    # Debug prints (pode remover depois)
    print(f"Fornece N: {len(fornece_N)}")
    print(f"Fornece P: {len(fornece_P)}")
    print(f"Fornece K: {len(fornece_K)}")
    print(f"Fornece N_P: {len(fornece_N_P)}")
    print(f"Fornece N_K: {len(fornece_N_K)}")
    print(f"Fornece P_K: {len(fornece_P_K)}")
    print(f"Fornece N_P_K: {len(fornece_N_P_K)}")
    print(f"Enchimentos: {len(enchimentos)}")

    # Gerar combinações individuais para cada grupo
    combinacoes_N = gerar_combinacoes_steps(fornece_N, step)
    combinacoes_P = gerar_combinacoes_steps(fornece_P, step)
    combinacoes_K = gerar_combinacoes_steps(fornece_K, step)
    combinacoes_N_P = gerar_combinacoes_steps(fornece_N_P, step)
    combinacoes_N_K = gerar_combinacoes_steps(fornece_N_K, step)
    combinacoes_P_K = gerar_combinacoes_steps(fornece_P_K, step)
    combinacoes_N_P_K = gerar_combinacoes_steps(fornece_N_P_K, step)

    # Juntar as combinações usando o itertools.product com base nos nutrientes ativos
    candidate_combs = {}
    if formulado_dict["N"] > 0:
        candidate_combs["N"] = combinacoes_N + combinacoes_N_P + combinacoes_N_K + combinacoes_N_P_K
    if formulado_dict["P"] > 0:
        candidate_combs["P"] = combinacoes_P + combinacoes_P_K + combinacoes_N_P_K
    if formulado_dict["K"] > 0:
        candidate_combs["K"] = combinacoes_K + combinacoes_N_K + combinacoes_P_K + combinacoes_N_P_K

    combinacoes_separadas = []
    active_nutrients = list(candidate_combs.keys())
    if active_nutrients:
        for comb in itertools.product(*(candidate_combs[nutr] for nutr in active_nutrients)):
            combinacoes_separadas.append(dict(zip(active_nutrients, comb)))
    else:
        combinacoes_separadas = []

    # Validação final: verificar se as combinações têm soma 100 para cada nutriente
    def juntar_combinacoes_por_nutriente_separado(combinacoes):
        combinacoes_finais = []
        for combinacao in combinacoes:
            combinacao_valida = True
            for nutriente, materiais in combinacao.items():
                proporcao_total = sum(item["proportion"] for item in materiais)
                if proporcao_total != 100:
                    combinacao_valida = False
                    break
            if combinacao_valida:
                combinacoes_finais.append(combinacao)
        return combinacoes_finais

    combinacoes_finais = juntar_combinacoes_por_nutriente_separado(combinacoes_separadas)

    # Adicionar enchimentos às combinações, se existirem
    if enchimentos:
        novas_combinacoes = []
        for combinacao in combinacoes_finais:
            for enchimento in enchimentos:
                combinacao_com_enchimento = combinacao.copy()
                combinacao_com_enchimento["Enchimento"] = [enchimento]
                novas_combinacoes.append(combinacao_com_enchimento)
        combinacoes_finais.extend(novas_combinacoes)

    return {
        "total": len(combinacoes_finais),
        "combinations": combinacoes_finais
    }


def gerar_combinacoes_old_(formulado: str, materias_primas: list, step: int) -> dict:
    """
    Gera combinações utilizando no máximo 3 matérias bases para cada nutriente (N, P, K),
    retornando também os enchimentos separadamente.

    Parâmetros:
        formulado (str): Fórmula no formato "N-P-K".
        materias_primas (list): Lista de dicionários com as matérias-primas.
        step (int): Intervalo de variação das proporções (ex: 5, 10, etc).

    Retorna:
        dict: {
            "total": número de combinações geradas,
            "combinations": lista de combinações, onde cada combinação é um dict
                            com chaves 'N', 'P' e/ou 'K' e seus respectivos itens,
            "enchimentos": lista de matérias-primas que não são nutrientes.
        }
    """
    # Converter o formulado para dicionário
    formulado_split = formulado.split("-")
    formulado_dict = {
        "N": int(formulado_split[0]),
        "P": int(formulado_split[1]),
        "K": int(formulado_split[2]),
    }

    # Nutrientes com valor zero serão excluídos das combinações
    nutrientes_excluidos = {nutr for nutr, v in formulado_dict.items() if v == 0}

    # Listas para matérias bases e enchimentos
    candidatos_N = []
    candidatos_P = []
    candidatos_K = []
    enchimentos = []

    def simplificar_nutriente(nutriente: str) -> str:
        """Mapeia o nome para N, P ou K."""
        if nutriente.startswith("N"):
            return "N"
        elif nutriente.startswith("P"):
            return "P"
        elif nutriente.startswith("K"):
            return "K"
        return nutriente

    # Percorre as matérias e separa em candidatos ou enchimentos
    for materia in materias_primas:
        is_nutrient = materia.get("isNutrient", True)
        if isinstance(is_nutrient, str):
            is_nutrient = is_nutrient.lower() == "true"

        if not is_nutrient:
            enchimentos.append(materia)
            continue

        # Extrai os nutrientes relevantes e simplifica os nomes
        nutrient_names = [simplificar_nutriente(n["name"]) for n in materia.get("nutrients", [])
                          if simplificar_nutriente(n["name"]) in {"N", "P", "K"}]

        # Se a matéria fornece um nutriente que está excluído, pula
        if any(n in nutrientes_excluidos for n in nutrient_names):
            continue

        # Se a matéria fornece N, P ou K, adiciona em cada lista correspondente
        if "N" in nutrient_names:
            candidatos_N.append(materia)
        if "P" in nutrient_names:
            candidatos_P.append(materia)
        if "K" in nutrient_names:
            candidatos_K.append(materia)

    # Função para extrair o valor (percentual) específico para um nutriente de uma matéria
    def get_nutrient_value(materia: dict, nutriente: str) -> float:
        for n in materia.get("nutrients", []):
            if simplificar_nutriente(n["name"]) == nutriente:
                return float(n["percent"])
        return 0.0

    # Ordena os candidatos por contribuição específica (descendente) e limita a 3 itens
    candidatos_N = sorted(candidatos_N, key=lambda m: get_nutrient_value(m, "N"), reverse=True)[:3]
    candidatos_P = sorted(candidatos_P, key=lambda m: get_nutrient_value(m, "P"), reverse=True)[:3]
    candidatos_K = sorted(candidatos_K, key=lambda m: get_nutrient_value(m, "K"), reverse=True)[:3]

    # Função para gerar combinações para um nutriente específico
    def gerar_combinacoes_por_nutriente(candidates: list, nutrient_letter: str, step: int) -> list:
        """
        Gera combinações (de 1 até len(candidates) itens) com distribuições de proporções
        que somam 100, utilizando o step definido.
        Cada item na combinação carrega o nome, o valor do nutriente e a proporção atribuída.
        """
        steps = [i for i in range(step, 101, step)]
        combinacoes = []
        n_candidates = len(candidates)

        # Escolhe de 1 até n_candidates itens (sem repetição)
        for num_itens in range(1, n_candidates + 1):
            for comb in itertools.combinations(candidates, num_itens):
                # Para cada combinação de matérias, gera as distribuições de proporção
                for proporcoes in itertools.product(steps, repeat=num_itens):
                    if sum(proporcoes) == 100:
                        combo_itens = []
                        for materia, prop in zip(comb, proporcoes):
                            combo_itens.append({
                                "name": materia["name"],
                                "proportion": prop,
                                "value": get_nutrient_value(materia, nutrient_letter)
                            })
                        combinacoes.append(combo_itens)
        return combinacoes

    # Gera as combinações para cada nutriente ativo no formulado
    combinacoes_por_nutriente = {}
    if formulado_dict["N"] > 0:
        combinacoes_por_nutriente["N"] = gerar_combinacoes_por_nutriente(candidatos_N, "N", step)
    if formulado_dict["P"] > 0:
        combinacoes_por_nutriente["P"] = gerar_combinacoes_por_nutriente(candidatos_P, "P", step)
    if formulado_dict["K"] > 0:
        combinacoes_por_nutriente["K"] = gerar_combinacoes_por_nutriente(candidatos_K, "K", step)

    # Gera a combinação final: produto cartesiano entre os nutrientes ativos
    nutrientes_ativos = list(combinacoes_por_nutriente.keys())
    combinacoes_finais = []
    if nutrientes_ativos:
        # Cada item do produto é uma tupla com combinações para cada nutriente
        for comb in itertools.product(*(combinacoes_por_nutriente[n] for n in nutrientes_ativos)):
            # Monta um dicionário com a combinação de cada nutriente
            combinacao = {nutr: comb[idx] for idx, nutr in enumerate(nutrientes_ativos)}
            combinacoes_finais.append(combinacao)

    return {
        "total": len(combinacoes_finais),
        "combinations": combinacoes_finais,
        "enchimentos": enchimentos
    }


def gerar_combinacoes_new_(formulado: str, materias_primas: list, step: int) -> dict:
    """
    Gera combinações utilizando no máximo 3 matérias bases para cada nutriente (N, P, K),
    retornando também os enchimentos separadamente. Utiliza processamento lazy (yield)
    para reduzir o uso de memória durante a geração das combinações.

    Parâmetros:
        formulado (str): Fórmula no formato "N-P-K".
        materias_primas (list): Lista de dicionários com as matérias-primas.
        step (int): Intervalo de variação das proporções (ex: 5, 10, etc).

    Retorna:
        dict: {
            "total": número de combinações geradas,
            "combinations": lista de combinações (cada combinação é um dict com chaves 'N', 'P' e 'K'),
            "enchimentos": lista de matérias-primas que não são nutrientes.
        }
    """
    # Converter o formulado para dicionário
    formulado_split = formulado.split("-")
    formulado_dict = {
        "N": int(formulado_split[0]),
        "P": int(formulado_split[1]),
        "K": int(formulado_split[2]),
    }

    # Nutrientes com valor zero serão excluídos das combinações
    nutrientes_excluidos = {nutr for nutr, v in formulado_dict.items() if v == 0}

    # Listas para matérias bases e enchimentos
    candidatos_N = []
    candidatos_P = []
    candidatos_K = []
    enchimentos = []

    def simplificar_nutriente(nutriente: str) -> str:
        """Mapeia o nome para N, P ou K."""
        if nutriente.startswith("N"):
            return "N"
        elif nutriente.startswith("P"):
            return "P"
        elif nutriente.startswith("K"):
            return "K"
        return nutriente

    # Percorre as matérias e separa em candidatos ou enchimentos
    for materia in materias_primas:
        is_nutrient = materia.get("isNutrient", True)
        if isinstance(is_nutrient, str):
            is_nutrient = is_nutrient.lower() == "true"

        if not is_nutrient:
            enchimentos.append(materia)
            continue

        # Extrai os nutrientes relevantes e simplifica os nomes
        nutrient_names = [
            simplificar_nutriente(n["name"])
            for n in materia.get("nutrients", [])
            if simplificar_nutriente(n["name"]) in {"N", "P", "K"}
        ]

        # Se a matéria fornece um nutriente que está excluído, pula
        if any(n in nutrientes_excluidos for n in nutrient_names):
            continue

        # Adiciona a matéria em cada grupo que ela fornece
        if "N" in nutrient_names:
            candidatos_N.append(materia)
        if "P" in nutrient_names:
            candidatos_P.append(materia)
        if "K" in nutrient_names:
            candidatos_K.append(materia)

    # Função para extrair o valor (percentual) específico para um nutriente de uma matéria
    def get_nutrient_value(materia: dict, nutriente: str) -> float:
        for n in materia.get("nutrients", []):
            if simplificar_nutriente(n["name"]) == nutriente:
                return float(n["percent"])
        return 0.0

    # Ordena os candidatos por contribuição específica (descendente) e limita a 3 itens
    candidatos_N = sorted(candidatos_N, key=lambda m: get_nutrient_value(m, "N"), reverse=True)[:3]
    candidatos_P = sorted(candidatos_P, key=lambda m: get_nutrient_value(m, "P"), reverse=True)[:3]
    candidatos_K = sorted(candidatos_K, key=lambda m: get_nutrient_value(m, "K"), reverse=True)[:3]
    # Função para gerar combinações para um nutriente específico (usando yield para lazy evaluation)
    def gerar_combinacoes_por_nutriente(candidates: list, nutrient_letter: str, step: int):
        steps = [i for i in range(step, 101, step)]
        n_candidates = len(candidates)
        # Escolhe de 1 até n_candidates itens (sem repetição)
        for num_itens in range(1, n_candidates + 1):
            for comb in itertools.combinations(candidates, num_itens):
                # Para cada combinação de matérias, gera as distribuições de proporção
                for proporcoes in itertools.product(steps, repeat=num_itens):
                    if sum(proporcoes) == 100:
                        combo_itens = []
                        for materia, prop in zip(comb, proporcoes):
                            combo_itens.append({
                                "name": materia["name"],
                                "proportion": prop,
                                "nutrients": materia.get("nutrients", []),
                                "value": get_nutrient_value(materia, nutrient_letter),
                                "isNutrient": materia["isNutrient"]
                            })
                        yield combo_itens

    # Cria generators para cada nutriente ativo no formulado
    combinacoes_por_nutriente = {}
    if formulado_dict["N"] > 0:
        combinacoes_por_nutriente["N"] = gerar_combinacoes_por_nutriente(candidatos_N, "N", step)
    if formulado_dict["P"] > 0:
        combinacoes_por_nutriente["P"] = gerar_combinacoes_por_nutriente(candidatos_P, "P", step)
    if formulado_dict["K"] > 0:
        combinacoes_por_nutriente["K"] = gerar_combinacoes_por_nutriente(candidatos_K, "K", step)

    # Generator para produzir as combinações finais usando o produto cartesiano entre os nutrientes ativos
    def gerar_combinacoes_finais():
        nutrientes_ativos = list(combinacoes_por_nutriente.keys())
        if not nutrientes_ativos:
            return
        iterators = [combinacoes_por_nutriente[n] for n in nutrientes_ativos]
        for comb in itertools.product(*iterators):
            yield {nutr: comb[idx] for idx, nutr in enumerate(nutrientes_ativos)}

    # Consumir o generator final para obter a lista completa e contar o total
    combinacoes_finais_gen = gerar_combinacoes_finais()
    combinacoes_finais = []
    total = 0
    for comb in combinacoes_finais_gen:
        total += 1
        combinacoes_finais.append(comb)

    return {
        "total": total,
        "combinations": combinacoes_finais,
        "enchimentos": enchimentos
    }


def calcular_fornecimento_new_1(formulado, combinacoes, enchimentos, target_total=1000):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação e gera combinações
    adicionais quando for necessário usar um enchimento para completar o target_total.

    Parâmetros:
      formulado (str): Fórmula desejada no formato "N-P-K".
      combinacoes (list ou dict): Lista de combinações ou dicionário contendo a chave "combinations".
      enchimentos (list): Lista de enchimentos (matérias-primas não nutricionais) disponíveis.
      target_total (int): Total desejado em kg (default: 1000 kg).

    Retorna:
      dict: {
         "tempo_processamento": <tempo em segundos>,
         "formulado_exigido": <formulado>,
         "descartados": <número de combinações descartadas>,
         "aceitos": [lista de combinações aceitas, cada uma com seus materiais calculados]
      }

    Observação:
      - Para cada combinação que precisar de enchimento (quando total de fertilizante < target_total),
        uma nova combinação é gerada para cada item presente na lista de enchimentos.
      - Se a combinação ultrapassar o target_total, ela é descartada.
    """
    start_time = time.time()

    # Converter o formulado para metas em kg para cada nutriente
    try:
        target_n_perc, target_p_perc, target_k_perc = map(float, formulado.split('-'))
    except ValueError:
        raise ValueError("Erro: O formulado deve estar no formato 'N-P-K', ex: '10-10-10'.")

    # Converter percentuais para metas em kg
    target_n = (target_n_perc * target_total) / 100
    target_p = (target_p_perc * target_total) / 100
    target_k = (target_k_perc * target_total) / 100
    targets = {'N': target_n, 'P': target_p, 'K': target_k}

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    # Se combinacoes vier como dict, extrair a lista interna
    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])
    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    # Função auxiliar para calcular a quantidade de matéria-prima (kg) para um item
    def calcular_kg_item(nutriente, item):
        """
        Calcula a quantidade de matéria-prima necessária para fornecer o nutriente.
        Fórmula: kg_item = (target_nutriente * proporcao * 100) / teor_percent
        """
        proporcao = item.get("proportion", 0) / 100.0
        teor_percent = item.get("nutrient", {}).get(nutriente, 0)
        if teor_percent == 0:
            return 0
        return (targets[nutriente] * proporcao * 100) / teor_percent

    # Processa cada combinação individualmente
    for combinacao in combinacoes:
        if not isinstance(combinacao, dict):
            print(f"⚠️ Aviso: Combinação inválida ignorada: {combinacao}")
            continue

        total_fertilizer = 0.0  # total de kg de matérias-primas na combinação
        materias_selecionadas = []  # informações calculadas de cada material

        # Para cada nutriente (N, P, K) presente na combinação
        for nutriente in ['N', 'P', 'K']:
            itens = combinacao.get(nutriente, [])
            if not isinstance(itens, list):
                continue
            for item in itens:
                if not isinstance(item, dict):
                    print(f"⚠️ Aviso: Item inválido ignorado: {item}")
                    continue

                kg_item = calcular_kg_item(nutriente, item)
                total_fertilizer += kg_item
                # A quantidade real de nutriente fornecido é: target * proporcao
                proporcao = item.get("proportion", 0) / 100.0
                nutriente_fornecido = targets[nutriente] * proporcao

                materias_selecionadas.append({
                    "name": item.get("name", "Desconhecido"),
                    "kg": round(kg_item, 2),
                    "nutrients": {nutriente: round(nutriente_fornecido, 2)},
                    "isNutrient": item.get("isNutrient", False)
                })

        # Se o total de matéria-prima ultrapassar o target_total, descarta a combinação
        if total_fertilizer > target_total:
            resultados["descartados"] += 1
            continue

        # Se a soma for menor, calcula a diferença e usa enchimentos para completar
        diferenca = round(target_total - total_fertilizer, 2)
        if diferenca > 0:
            # Se houver enchimentos, gera uma combinação para cada um
            if enchimentos and isinstance(enchimentos, list):
                for filler in enchimentos:
                    nova_comb = materias_selecionadas.copy()
                    nova_comb.append({
                        "name": filler.get("name", "Enchimento Desconhecido"),
                        "kg": diferenca,
                        "nutrients": filler.get("nutrients", {}),
                        "isNutrient": filler.get("isNutrient", False)
                    })
                    # Aplica funções externas para combinar e validar os materiais
                    materiais_filtrados = combinar_materiais(nova_comb)
                    compatibility_result = validar_compatibilidade(materiais_filtrados)
                    resultados["aceitos"].append({
                        "materiais": materiais_filtrados,
                        "compatibility": compatibility_result.get("compatibility"),
                        "limited": compatibility_result.get("limited"),
                        "incompatible": compatibility_result.get("incompatible"),
                        "message": compatibility_result.get("message")
                    })
            else:
                # Se não houver enchimentos, descarta a combinação
                resultados["descartados"] += 1
                continue
        else:
            # Se total_fertilizer == target_total, aceita a combinação sem enchimento
            materiais_filtrados = combinar_materiais(materias_selecionadas)
            compatibility_result = validar_compatibilidade(materiais_filtrados)
            resultados["aceitos"].append({
                "materiais": materiais_filtrados,
                "compatibility": compatibility_result.get("compatibility"),
                "limited": compatibility_result.get("limited"),
                "incompatible": compatibility_result.get("incompatible"),
                "message": compatibility_result.get("message")
            })

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados

def calcular_fornecimento_new_2(formulado, combinacoes, enchimentos, target_total=1000):
    """
    Calcula os fornecimentos reais de N, P e K para cada combinação e gera combinações adicionais
    com cada enchimento, se necessário, para completar o target_total.

    Parâmetros:
      formulado (str): Fórmula desejada no formato "N-P-K".
      combinacoes (list ou dict): Lista de combinações ou dicionário contendo a chave "combinations".
      enchimentos (list): Lista de enchimentos disponíveis.
      target_total (int): Total desejado em kg (default: 1000).

    Retorna:
      dict: {
         "tempo_processamento": tempo em segundos,
         "formulado_exigido": formulado,
         "descartados": número de combinações descartadas,
         "aceitos": lista de combinações aceitas,
      }

    Para cada combinação que não atinge target_total, é gerada uma nova combinação para cada enchimento.
    """
    start_time = time.time()

    # Processar o formulado
    try:
        target_n_perc, target_p_perc, target_k_perc = map(float, formulado.split('-'))
    except ValueError:
        raise ValueError("Erro: O formulado deve estar no formato 'N-P-K', ex: '10-10-10'.")

    # Converter percentuais para metas em kg
    target_n = (target_n_perc * target_total) / 100
    target_p = (target_p_perc * target_total) / 100
    target_k = (target_k_perc * target_total) / 100
    targets = {'N': target_n, 'P': target_p, 'K': target_k}

    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "descartados": 0,
        "aceitos": []
    }

    # Se combinacoes vier como dict, extrair a lista interna
    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])
    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    # Função auxiliar para calcular a quantidade de kg de cada item
    def calcular_kg_item(nutriente, item):
        proporcao = item.get("proportion", 0) / 100.0
        teor_percent = item.get("nutrient", {}).get(nutriente, 0)
        if teor_percent == 0:
            return 0
        return (targets[nutriente] * proporcao * 100) / teor_percent

    # Processa cada combinação
    for combinacao in combinacoes:
        if not isinstance(combinacao, dict):
            print(f"⚠️ Aviso: Combinação inválida ignorada: {combinacao}")
            continue

        total_fertilizer = 0.0  # soma dos kg calculados dos itens
        materias_selecionadas = []  # lista dos materiais com seus cálculos

        # Para cada nutriente (N, P, K)
        for nutriente in ['N', 'P', 'K']:
            itens = combinacao.get(nutriente, [])
            if not isinstance(itens, list):
                continue
            for item in itens:
                if not isinstance(item, dict):
                    print(f"⚠️ Aviso: Item inválido ignorado: {item}")
                    continue

                kg_item = calcular_kg_item(nutriente, item)
                total_fertilizer += kg_item
                proporcao = item.get("proportion", 0) / 100.0
                nutriente_fornecido = targets[nutriente] * proporcao

                materias_selecionadas.append({
                    "name": item.get("name", "Desconhecido"),
                    "kg": round(kg_item, 2),
                    "nutrients": {nutriente: round(nutriente_fornecido, 2)},
                    "isNutrient": item.get("isNutrient", False)
                })

        # Se a soma ultrapassar o target_total, descarta a combinação
        if total_fertilizer > target_total:
            resultados["descartados"] += 1
            continue

        diferenca = round(target_total - total_fertilizer, 2)

        if diferenca > 0:
            # Se há necessidade de enchimento, gera uma nova combinação para cada enchimento disponível
            if enchimentos and isinstance(enchimentos, list):
                for filler in enchimentos:
                    nova_comb = materias_selecionadas.copy()
                    # Converter o campo "nutrients" do enchimento para dicionário, se necessário
                    filler_nutrients = filler.get("nutrients", {})
                    if isinstance(filler_nutrients, list):
                        filler_nutrients = {n.get("name", "unknown"): float(n.get("percent", 0))
                                            for n in filler_nutrients}
                    nova_comb.append({
                        "name": filler.get("name", "Enchimento Desconhecido"),
                        "kg": diferenca,
                        "nutrients": filler_nutrients,
                        "isNutrient": filler.get("isNutrient", False)
                    })
                    # Aplicar funções externas de combinação e validação (supondo que existam)
                    materiais_filtrados = combinar_materiais(nova_comb)
                    compatibility_result = validar_compatibilidade(materiais_filtrados)
                    resultados["aceitos"].append({
                        "materiais": materiais_filtrados,
                        "compatibility": compatibility_result.get("compatibility"),
                        "limited": compatibility_result.get("limited"),
                        "incompatible": compatibility_result.get("incompatible"),
                        "message": compatibility_result.get("message")
                    })
            else:
                resultados["descartados"] += 1
                continue
        else:
            # Caso total exato: aceita a combinação sem enchimento
            materiais_filtrados = combinar_materiais(materias_selecionadas)
            compatibility_result = validar_compatibilidade(materiais_filtrados)
            resultados["aceitos"].append({
                "materiais": materiais_filtrados,
                "compatibility": compatibility_result.get("compatibility"),
                "limited": compatibility_result.get("limited"),
                "incompatible": compatibility_result.get("incompatible"),
                "message": compatibility_result.get("message")
            })

    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados

def calcular_fornecimento_por_combinacao_old(formulado, combinacao, target_total):
    """
    Para uma única combinação, calcula os kg necessários de cada composto,
    usando os seguintes passos:
      1. Determina as necessidades de cada nutriente (em kg) a partir do formulado.
      2. Processa os nutrientes em ordem decrescente de necessidade.
      3. Para cada nutriente, para os compostos atribuídos, calcula:
             kg_item = ((remaining * 100) / teor_percent) * proporcao
         e subtrai a contribuição (kg_item * teor_percent/100) da necessidade.
      4. Se um composto fornece outros nutrientes, subtrai sua contribuição desses nutrientes.
      5. Retorna:
             - Uma lista de insumos com os kg calculados.
             - O total de kg dos insumos.
             - O peso de enchimento necessário para atingir target_total.
    """
    # 1. Parse do formulado: exemplo "04-20-20"
    try:
        perc_n, perc_p, perc_k = map(float, formulado.split('-'))
    except Exception as e:
        raise ValueError("Formulado deve estar no formato 'N-P-K', ex: '04-20-20'.")

    # Requisitos (em kg) para cada nutriente
    req = {
        'N': target_total * (perc_n / 100.0),
        'P': target_total * (perc_p / 100.0),
        'K': target_total * (perc_k / 100.0)
    }
    # Copia para atualizar as necessidades remanescentes
    remaining = dict(req)

    # Definimos uma ordem de processamento dos nutrientes – os que têm maior necessidade primeiro
    nutrientes_order = sorted(remaining.items(), key=lambda x: x[1], reverse=True)
    # Ex: para "04-20-20": P e K terão 200 kg cada e N terá 40 kg; assim, P e K virão antes de N.
    # dicionário para acumular o kg calculado para cada composto (chave: nome do composto)
    comp_results = {}
    # Guardamos detalhes do composto (por exemplo, os percentuais e proporção)
    comp_details = {}

    # Processa cada nutriente na ordem definida
    for nutr, req_val in nutrientes_order:

        # Obtemos a lista de compostos para este nutriente na combinação
        comp_list = combinacao.get(nutr, [])

        # Ordena os compostos por seu teor para o nutriente (decrescente)
        comp_list = sorted(comp_list, key=lambda c: float(c.get("nutrients", []).get(nutr, 0)), reverse=True)
        for comp in comp_list:
            comp_name = comp.get("name", "Desconhecido")
            try:
                teor = float(comp.get("nutrients", []).get(nutr, 0))
            except:
                teor = 0
            try:
                proporcao = float(comp.get("proportion", 0)) / 100.0
            except:
                proporcao = 0.0

            if teor <= 0 or proporcao <= 0:
                continue  # ignora se não há teor ou proporção definida

            if remaining[nutr] <= 0:
                continue  # necessidade já satisfeita para este nutriente

            # Cálculo: quanto do composto é necessário para suprir a parte remanescente deste nutriente
            kg_comp = ((remaining[nutr] * 100) / teor) * proporcao

            # A contribuição efetiva deste composto para o nutriente
            contrib = kg_comp * (teor / 100.0)
            # Garante que não subtraímos mais do que o necessário
            if contrib > remaining[nutr]:
                contrib = remaining[nutr]
                # Recalcula kg_comp para essa contribuição exata
                kg_comp = (contrib * 100) / (teor * proporcao)

            # Atualiza a necessidade remanescente para o nutriente atual
            remaining[nutr] -= contrib

            # Se o composto já foi usado (pode vir em mais de uma chave), somamos
            if comp_name in comp_results:
                comp_results[comp_name] += kg_comp
            else:
                comp_results[comp_name] = kg_comp
                # Guarda os detalhes originais (usamos o primeiro encontrado)
                comp_details[comp_name] = comp

            # Como o composto pode fornecer outros nutrientes, atualiza as necessidades remanescentes dos demais
            for outro in ['N', 'P', 'K']:
                if outro == nutr:
                    continue
                try:
                    teor_outro = float(comp.get("nutrients", []).get(outro, 0))
                except:
                    teor_outro = 0
                if teor_outro > 0:
                    # Contribuição para o outro nutriente
                    contrib_outro = kg_comp * (teor_outro / 100.0)
                    # Subtrai dessa necessidade (não pode ser negativa)
                    remaining[outro] = max(0, remaining[outro] - contrib_outro)

    total_compounds = sum(comp_results.values())
    filler = target_total - total_compounds

    # Monta a lista final de insumos calculados
    insumos = []
    for comp_name, kg in comp_results.items():
        detalhes = comp_details.get(comp_name, {})
        insumos.append({
            "name": comp_name,
            "kg": round(kg, 2),
            "nutrients": detalhes.get("nutrients", {}),
            "proportion": detalhes.get("proportion")
        })

    return insumos, round(total_compounds, 2), round(filler, 2)

### Em uso

def calcular_fornecimento_new_(
        formulado,
        combinacoes,
        enchimentos,
        target_total=1000,
        limite_enchimento = 400,
        margem = 0.05,
        show_incompatibility=False
):
    """
    Para cada combinação base (das 'combinacoes'), calcula os insumos necessários segundo o
    algoritmo definido – que opera em ordem de prioridade dos nutrientes – e, se o total dos
    insumos for menor que target_total, gera novas formulações para cada enchimento disponível,
    adicionando o enchimento para completar o total.

    Retorna um dicionário com:
      - tempo de processamento
      - formulado exigido
      - número de combinações descartadas (se houver)
      - lista de combinações aceitas, cada uma com:
             "materiais": lista dos insumos calculados (cada um com kg, etc.)
             "filler": a quantidade de enchimento necessária
    """
    start_time = time.time()
    resultados = {
        "tempo_processamento": None,
        "formulado_exigido": formulado,
        "limite_enchimentos": limite_enchimento,
        "total_enchimentos": len(enchimentos),
        "total_combinacoes": len(combinacoes),
        "combinacoes_descartadas": 0,
        "formulados_incompativeis": 0,
        "enchimentos_incompativeis": 0,
        "descartados": 0,
        "aceitos": []
    }

    # Se 'combinacoes' vier como dict, extrai a lista
    if isinstance(combinacoes, dict):
        combinacoes = combinacoes.get("combinations", [])
    if not isinstance(combinacoes, list):
        print(f"⚠️ Erro: 'combinacoes' deveria ser uma lista, mas recebeu {type(combinacoes)}. Encerrando.")
        return resultados

    # Processa cada combinação base
    for comb in combinacoes:
        if not isinstance(comb, dict):
            continue

        # Calcula os insumos e o total de kg a partir desta combinação
        try:
            insumos, total_insumos, filler_kg = calcular_fornecimento_por_combinacao(
                formulado,
                comb,
                target_total,
                limite_enchimento,
                margem
            )
        except Exception as e:
            print(f"Erro no processamento da combinação: {e}")
            resultados["descartados"] += 1
            continue

        # Se os não existir insumos, descarta
        if len(insumos) == 0:
            resultados["descartados"] += 1
            continue

        # Se os insumos somados ultrapassam o target_total, descartamos
        if total_insumos > target_total:
            #print(f"Erro no processamento da combinação: {total_insumos} {insumos}")
            resultados["descartados"] += 1
            continue

        # Valida a compatibilidade entre as matérias-primas
        compatibilidade = validar_compatibilidade(insumos)
        if not compatibilidade['compatibility'] and show_incompatibility == False:
            resultados["formulados_incompativeis"] += 1
            continue

        # Se houver filler (isto é, total_insumos < target_total), para cada enchimento disponível,
        # gera-se uma formulação que é a combinação dos insumos + o filler do enchimento.
        if 0 < filler_kg <= limite_enchimento and enchimentos and isinstance(enchimentos, list):
            for filler in enchimentos:
                # Se o filler tiver os nutrientes em formato lista, converte para dict (como esperado)
                #filler_nutrients = filler.get("nutrients", {})
                #if isinstance(filler_nutrients, list):
                #    filler_nutrients = {n.get("name", "unknown"): float(n.get("percent", 0)) for n in filler_nutrients}

                formula_final = {
                    "materiais": insumos + [{
                        "name": filler.get("name", "Enchimento Desconhecido"),
                        "kg": filler_kg,
                        #"nutrients": filler_nutrients,
                        "isNutrient": filler.get("isNutrient", False),
                        "nutrients": filler.get("nutrients", {})
                    }],
                    "total_insumos": total_insumos,
                    "filler": filler_kg,
                    "compatibility": False,
                    "limited": False,
                    "message": ''
                }

                # Valida compatibilidade novamente, pois existem enchimentos incompativeis com certos materiais
                compatibilidade = validar_compatibilidade(formula_final['materiais'])
                if compatibilidade['compatibility'] == True or show_incompatibility == True:
                    formula_final['compatibility'] = compatibilidade['compatibility']
                    formula_final['limited'] = compatibilidade['limited']
                    formula_final['message'] = compatibilidade['message']
                    resultados["aceitos"].append(formula_final)

                    if compatibilidade['compatibility'] == False and show_incompatibility == True:
                        resultados["enchimentos_incompativeis"] += 1

                else:
                    resultados["enchimentos_incompativeis"] += 1

        elif filler_kg > limite_enchimento:
            resultados["descartados"] += 1
        else:
            # Caso não precise de filler ou não haja enchimento, aceita a combinação
            formula_final = {
                "materiais": insumos,
                "total_insumos": total_insumos,
                "filler": filler_kg,
                "compatibility": False,
                "limited": False,
                "message": ''
            }
            compatibilidade = validar_compatibilidade(formula_final['materiais'])
            if compatibilidade['compatibility'] == True or show_incompatibility == True:
                formula_final['compatibility'] = compatibilidade['compatibility']
                formula_final['limited'] = compatibilidade['limited']
                formula_final['message'] = compatibilidade['message']
                resultados["aceitos"].append(formula_final)

                if compatibilidade['compatibility'] == False and show_incompatibility == True:
                    resultados["formulados_incompativeis"] += 1
                    print(F"show_incompatibility {show_incompatibility}")

            else:
                resultados["formulados_incompativeis"] += 1

    resultados["descartados"]+= resultados["formulados_incompativeis"]
    resultados["tempo_processamento"] = f"{(time.time() - start_time):.2f} segundos"
    return resultados

def calcular_fornecimento_por_combinacao(
        formulado,
        combinacao,
        target_total,
        limite_enchimento,
        margem = 0.05
):
    """
    Para uma única combinação, calcula os kg necessários de cada composto,
    seguindo os passos:
      1. Determina as necessidades (em kg) de cada nutriente a partir do formulado.
      2. Processa os nutrientes em ordem decrescente de necessidade.
      3. Para cada nutriente, para os compostos atribuídos, calcula:
             kg_item = ((remaining * 100) / teor_percent) * proporcao
         e subtrai a contribuição (kg_item * teor_percent/100) da necessidade.
      4. Se o composto fornece outros nutrientes, subtrai sua contribuição desses nutrientes.
      5. Retorna:
             - Uma lista de insumos com os kg calculados.
             - O total de kg dos insumos.
             - O peso de enchimento necessário para atingir target_total.
    """
    try:
        perc_n, perc_p, perc_k = map(float, formulado.split('-'))
    except Exception as e:
        raise ValueError("Formulado deve estar no formato 'N-P-K', ex: '04-20-20'.")

    # Requisitos (em kg) para cada nutriente
    req = {
        'N': target_total * (perc_n / 100.0),
        'P': target_total * (perc_p / 100.0),
        'K': target_total * (perc_k / 100.0)
    }
    remaining = dict(req)
    # Ordem de processamento: os que têm maior necessidade primeiro
    nutrientes_order = sorted(remaining.items(), key=lambda x: x[1], reverse=True)

    comp_results = {}
    comp_details = {}

    for nutr, req_val in nutrientes_order:
        comp_list = combinacao.get(nutr, [])
        # Ordena os compostos pela taxa (teor) para o nutriente 'nutr'
        comp_list = sorted(comp_list,
                           key=lambda c: extrair_teor_nutriente(c.get("nutrients", []), nutr),
                           reverse=True)
        for comp in comp_list:
            comp_name = comp.get("name", "Desconhecido")
            teor = extrair_teor_nutriente(comp.get("nutrients", []), nutr)
            try:
                proporcao = float(comp.get("proportion", 0)) / 100.0
            except:
                proporcao = 0.0

            if teor <= 0 or proporcao <= 0:
                continue
            if remaining[nutr] <= 0:
                continue

            kg_comp = ((remaining[nutr] * 100) / teor) * proporcao
            contrib = kg_comp * (teor / 100.0)
            if contrib > remaining[nutr]:
                contrib = remaining[nutr]
                kg_comp = (contrib * 100) / (teor * proporcao)

            remaining[nutr] -= contrib

            if comp_name in comp_results:
                comp_results[comp_name] += kg_comp
            else:
                comp_results[comp_name] = kg_comp
                comp_details[comp_name] = comp

            for outro in ['N', 'P', 'K']:
                if outro == nutr:
                    continue
                teor_outro = extrair_teor_nutriente(comp.get("nutrients", []), outro)
                if teor_outro > 0:
                    contrib_outro = kg_comp * (teor_outro / 100.0)
                    remaining[outro] = max(0, remaining[outro] - contrib_outro)

    total_compounds = sum(comp_results.values())
    filler = target_total - total_compounds

    # --- Nova etapa: calcular o fornecimento real de cada nutriente ---
    fornecimento_calculado = {"N": 0.0, "P": 0.0, "K": 0.0}
    for comp_name, kg in comp_results.items():
        # Para cada composto, calcule a contribuição de cada nutriente com base no kg usado
        comp = comp_details[comp_name]
        for nutrient in comp.get("nutrients", []):
            nome_nutriente = nutrient.get("name", "")
            # Utiliza a função simplificar para identificar N, P ou K
            nutr_simpl = simplificar_nutriente(nome_nutriente)
            try:
                teor = float(nutrient.get("percent", 0))
            except:
                teor = 0.0
            if teor > 0 and nutr_simpl in fornecimento_calculado:
                fornecimento_calculado[nutr_simpl] += kg * (teor / 100.0)

    # --- Verificar se algum fornecimento ultrapassa o limite (mais tolerância) ---
    tolerancia = (margem / 100)  # % vem do front-end, transforma em decimal
    excede_limite = False
    for nutr in ['N', 'P', 'K']:
        limite_esperado = req[nutr]
        fornecido = fornecimento_calculado.get(nutr, 0)
        limite_inferior = limite_esperado * (1 - tolerancia)
        limite_superior = limite_esperado * (1 + tolerancia)

        if fornecido < limite_inferior or fornecido > limite_superior:
            #print( f"❌ Descartado: Fornecimento de {nutr} ({fornecido:.2f} kg) ultrapassa o limite esperado ({limite_esperado:.2f} kg) com tolerância.")
            excede_limite = True
            break

    if excede_limite:
        # Descarta a combinação se algum nutriente exceder o limite
        return [], round(total_compounds, 2), round(filler, 2)

    insumos = []
    if filler <= limite_enchimento:
        for comp_name, kg in comp_results.items():
            detalhes = comp_details.get(comp_name, {})
            insumos.append({
                "name": comp_name,
                "kg": round(kg, 2),
                "nutrients": detalhes.get("nutrients", {}),  # mantém a estrutura original
                "proportion": detalhes.get("proportion"),
            })

    return insumos, round(total_compounds, 2), round(filler, 2)

def simplificar_nutriente(nutriente: str) -> str:
    nutriente = nutriente.strip().upper()
    if nutriente.startswith("N"):
        return "N"
    elif nutriente.startswith("P"):
        return "P"
    elif nutriente.startswith("K"):
        return "K"
    return nutriente

def extrair_teor_nutriente(nutrientes_list: list, nutr: str) -> float:
    """
    Dado uma lista de nutrientes (cada item com 'name' e 'percent'),
    retorna o valor (float) para o nutriente desejado (após simplificação).
    Se não encontrar, retorna 0.
    """
    for item in nutrientes_list:
        if isinstance(item, dict):
            nome = item.get("name", "")
            if simplificar_nutriente(nome) == nutr:
                try:
                    return float(item.get("percent", 0))
                except:
                    return 0.0
    return 0.0










