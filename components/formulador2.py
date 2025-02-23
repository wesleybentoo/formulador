from fasthtml.common import *
from logica.logica_formulacao_2 import (
    calcular_fornecimento,
    gerar_combinacoes,
    gerar_combinacoes_new_,
    calcular_fornecimento_new_
)

def register_routes(rt):
    def formulador_old():
        return Html(
            Head(
                Title("Formulador 2"),
                Link(rel="stylesheet", href="/static/style.css"),
                Script(src="/static/script.js"),
            ),
            Body(
                Div(
                    H1("Formulador 2 - Fórmulas com Teores Indeterminados", cls="page-title"),

                    # Input para o formulado desejado
                    Div(
                        Label("Informe o formulado desejado (NPK):", For="formulado"),
                        Input(id="formulado", type="text", placeholder="Ex.: 04-20-20", cls="form-input"),
                        cls="form-group"
                    ),

                    # Tabela com checkbox para selecionar as matérias-primas
                    Div(
                        H2("Selecione as Matérias-Primas Disponíveis:", cls="section-title"),
                        Table(
                            Thead(
                                Tr(
                                    Th("Selecionar", cls="table-header"),
                                    Th("Nome", cls="table-header"),
                                    Th("Teores de Nutrientes", cls="table-header")
                                )
                            ),
                            Tbody(id="materiasPrimasTable"),  # JS irá preencher essa tabela
                            cls="table"
                        ),
                        cls="table-container"
                    ),

                    # Botão para calcular
                    Button("Calcular Fórmula", id="calculateButton", cls="calculate-button",
                           onclick="calculateFormula()"),

                    # Container para os resultados
                    Div(id="resultsContainer", cls="results-container"),
                    cls="container"
                )
            )
        )

    @rt('/formulador2')
    def formulador2():
        return Html(
            Head(
                Title("Formulador 2 - Fórmulas com Teores Indeterminados"),
                Link(rel="stylesheet", href="/static/styleFormulador2.css"),
                Script(src="/static/script.js"),
                Script(src="/static/previsaoCombinacoes.js"),
            ),
            Body(
                Div(
                    # Cabeçalho
                    Div(
                        H1("Formulador 2", cls="logo"),
                        A("Voltar", href="/", cls="button"),
                        cls="header"
                    ),

                    # Card 1 - Input do Formulado
                    Div(
                        Div(
                            H2("Informe o Formulado Desejado (NPK):", cls="card-header"),
                            Div(
                                Label("Formulado (XX-XX-XX):", For="formulado"),
                                Input(
                                    id="formulado",
                                    type="text",
                                    placeholder="Ex.: 04-20-20",
                                    cls="form-input",
                                    oninput="aplicarMascaraFormulado(this); atualizarPrevisaoCombinacoes()"
                                ),
                                cls="input-card"
                            ),
                        ),
                        cls="card"
                    ),

                    # Card 2 - Matérias-Primas
                    Div(
                        Div(
                            H2("Selecione as Matérias-Primas Disponíveis:", cls="card-header"),
                            Div(
                                Table(
                                    Thead(
                                        Tr(
                                            Th("Selecionar", cls="table-header"),
                                            Th("Nome", cls="table-header"),
                                            Th("Teores de Nutrientes", cls="table-header")
                                        )
                                    ),
                                    Tbody(id="materiasPrimasTable"),  # JS irá preencher essa tabela
                                    cls="table"
                                ),
                                cls="table-container"
                            ),
                            Div(
                            Button("Selecionar Tudo",
                                   cls="action-button select-all",
                                   onclick="selecionar('tudo')"
                                   ),
                                Button("Selecionar Matérias-Primas",
                                       cls="action-button select-nutrientes",
                                       onclick="selecionar('nutrientes')"
                                       ),
                                Button("Selecionar Enchimentos",
                                       cls="action-button select-fillers",
                                       onclick="selecionar('enchimentos')"
                                       ),
                                Button("Remover Tudo",
                                       cls="action-button remove-all",
                                       onclick="removerTudo()"
                                       ),
                                cls="button-container"
                            ),
                        ),
                        cls="card materias-primas-card"
                    ),

                    # Card 3 - Previsão e Erros
                    Div(
                        Div(
                            H2("Previsão de Combinações e Validações:", cls="card-header"),
                            Div(id="combinacoesPrevisao", cls="previsao-container"),
                            Div(id="erroContainer", cls="error-container"),
                        ),
                        cls="card previsao-card"
                    ),

                    # Card 4 - Input do limite de enchimento
                    Div(
                        Div(
                            H2("Configuração das combinações:", cls="card-header"),
                            Div(
                                Label("Limite de enchimento (kg):", For="limite em kg"),
                                Input(
                                    id="limite_enchimento",
                                    type="number",
                                    placeholder="Ex.: 300.00",
                                    cls="form-input",
                                    value="200"
                                    #oninput="aplicarMascaraFormulado(this);"
                                ),
                                cls="input-card"
                            ),
                            Div(
                                Label("Percentual de margem:", For="percentual"),
                                Input(
                                    id="margem",
                                    type="number",
                                    placeholder="Ex.: 5%",
                                    cls="form-input",
                                    value="5"
                                    # oninput="aplicarMascaraFormulado(this);"
                                ),
                                cls="input-card"
                            ),

                            Div(
                                Label("Intervalo de variação das proporções:", For="percentual"),
                                Input(
                                    id="step",
                                    type="number",
                                    placeholder="Recomendado: 10",
                                    cls="form-input",
                                    value="10",
                                    oninput="atualizarPrevisaoCombinacoes()"
                                ),
                                cls="input-card"
                            ),
                            Div(
                                Label('Mostrar formulações incompátiveis', For='incompatibility', cls="inline-label"),
                                Input(id='incompatibility', name='incompatibility', type='checkbox', checked=False),
                                cls="checkbox-wrapper margin-top"
                            ),

                            Div(
                                Button("Calcular Fórmula",
                                       id="buttonCalculate",
                                       cls="action-button calculate-button",
                                       onclick="calculateFormula()"),
                                cls="button-container"
                            ),
                        ),
                        cls="card"
                    ),

                    # Lista de Cards para Resultados
                    Div(
                        H2("Resultados das Combinações:", cls="card-header"),
                        Div(id="resultsContainer", cls="cards-container"),
                        cls="card",
                        id="cardResults"
                    ),

                    cls="container"
                )
            )
        )

    @rt('/formulador2/calculate')
    async def formulador2_calculate(request):
        try:
            # Obtém os dados enviados como JSON
            data = await request.json()  # Use await para esperar os dados
            formulado = data.get('formulado', '').strip()
            materias_primas = data.get('materiasPrimas', [])
            limite_enchimento = int(data.get('limiteEnchimento', 0))
            margem = int(data.get('margem', 0))
            step = int(data.get('step', 0))
            incompatibility = bool(data.get('incompatibility', 0))

            # Valida os dados recebidos
            if not formulado:
                return {"error": "Por favor, informe o formulado desejado (ex.: 04-20-20)."}
            if not materias_primas:
                return {"error": "Nenhuma matéria-prima selecionada. Por favor, selecione ao menos uma."}

            # Realiza os cálculos com a lógica de combinação
            #combinacao = gerar_combinacoes(formulado, materias_primas, step=10)
            #resultados = calcular_fornecimento(formulado, combinacao['combinations'])

            combinacao = gerar_combinacoes_new_(formulado, materias_primas, step)
            resultados = calcular_fornecimento_new_(
                formulado,
                combinacao['combinations'],
                combinacao['enchimentos'],
                1000,
                limite_enchimento,
                margem,
                incompatibility
            )

            # Se nenhum resultado for encontrado, retorne uma mensagem de erro
            if not resultados:
                return {"error": "Não foi possível encontrar uma combinação com as matérias-primas selecionadas."}

            return {"results": resultados}

        except Exception as e:
            return {"error": f"Ocorreu um erro ao processar a solicitação: {str(e)}"}


