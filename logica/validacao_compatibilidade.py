import json
import os

def carregar_restricoes_compatibilidade():
    """
    Carrega os dados de compatibilidade do arquivo JSON.

    Returns:
        list: Lista de regras de compatibilidade.
    """
    caminho_arquivo = os.path.join(os.path.dirname(__file__), "../static/restricoes_compatibilidade.json")

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados.get("data", [])
    except Exception as e:
        print(f"⚠️ Erro ao carregar restrições de compatibilidade: {e}")
        return []


def validar_compatibilidade(materiais):
    """
    Valida a compatibilidade dos materiais na mistura, verificando incompatibilidades e limitações.

    Args:
        materiais (list): Lista de materiais selecionados na combinação.

    Returns:
        dict: Resultado da validação com status e mensagem.
    """
    # 🔹 Carregar as regras de compatibilidade
    compatibility_data = carregar_restricoes_compatibilidade()

    # 🔹 Criar um conjunto com os nomes das matérias-primas fornecidas
    materiais_nomes = {mat["name"] for mat in materiais}

    incompatibilidades = set()
    limitacoes = set()

    for material in materiais_nomes:
        # Buscar a regra de compatibilidade para o material atual
        regra = next((item for item in compatibility_data if item["name"] == material), None)
        if not regra:
            continue  # Se não encontrar a regra, ignora

        # 🔹 Verificar incompatibilidades
        for item_incompativel in regra["incompatible"]:
            if item_incompativel in materiais_nomes:
                incompatibilidades.add((material, item_incompativel))

        # 🔹 Verificar limitações
        for item_limitado in regra["limited"]:
            if item_limitado in materiais_nomes:
                limitacoes.add((material, item_limitado))

    # 🔹 Construir a resposta
    if incompatibilidades:
        return {
            "compatibility": False,
            "limited": bool(limitacoes),
            "incompatible": True,
            "message": f"Incompatibilidade detectada entre: {', '.join([f'{a} ↔ {b}' for a, b in incompatibilidades])}"
        }
    elif limitacoes:
        return {
            "compatibility": True,
            "limited": True,
            "incompatible": False,
            "message": f"Limitações detectadas entre: {', '.join([f'{a} ↔ {b}' for a, b in limitacoes])}"
        }
    else:
        return {
            "compatibility": True,
            "limited": False,
            "incompatible": False,
            "message": "Todos os materiais são compatíveis."
        }


def carregar_restricoes_compatibilidade_2():
    """Carrega as restrições de compatibilidade do arquivo JSON."""
    caminho_arquivo = os.path.join(os.path.dirname(__file__), "../static/restricoes_compatibilidade.json")

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return {item["name"]: item for item in dados.get("data", [])}
    except FileNotFoundError:
        print("⚠️ Arquivo de compatibilidade não encontrado. Continuando sem validação...")
        return {}
    except json.JSONDecodeError:
        print("⚠️ Erro ao carregar o arquivo de compatibilidade. Verifique o JSON.")
        return {}


def validar_compatibilidade_2(materiais):
    """
    Verifica se os materiais selecionados possuem restrições de compatibilidade.

    Args:
        materiais (list): Lista de dicionários contendo os materiais escolhidos.

    Returns:
        dict: Contendo status de compatibilidade, mensagens e tipos de restrições.
    """
    materiais_nomes = [m["name"] for m in materiais]

    incompatibilidade_encontrada = set()
    limitacoes_encontradas = set()

    for material in materiais_nomes:
        if material in RESTRICOES_COMPATIBILIDADE:
            restricoes = RESTRICOES_COMPATIBILIDADE[material]

            # Verificar incompatíveis
            for incompativel in restricoes.get("incompatible", []):
                if incompativel in materiais_nomes:
                    incompatibilidade_encontrada.add((material, incompativel))

            # Verificar limitados
            for limitado in restricoes.get("limited", []):
                if limitado in materiais_nomes:
                    limitacoes_encontradas.add((material, limitado))

    # Se houver incompatibilidade, a combinação deve ser descartada
    if incompatibilidade_encontrada:
        return {
            "compatibility": False,
            "limited": False,
            "incompatible": True,
            "message": f"Incompatibilidade entre: {list(incompatibilidade_encontrada)}"
        }

    # Se houver apenas limitações, a combinação pode ser mantida, mas com alerta
    if limitacoes_encontradas:
        return {
            "compatibility": True,
            "limited": True,
            "incompatible": False,
            "message": f"Combinação contém restrições limitadas entre: {list(limitacoes_encontradas)}"
        }

    # Se passou por tudo, é compatível
    return {
        "compatibility": True,
        "limited": False,
        "incompatible": False,
        "message": "Combinação válida!"
    }

# Carregar a lista de restrições uma única vez para otimizar performance
RESTRICOES_COMPATIBILIDADE = carregar_restricoes_compatibilidade_2()