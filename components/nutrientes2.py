from fasthtml.common import *

def register_routes(rt):
    @rt('/nutrientes2')
    def nutrientes():
        return Html(
            Head(
                Title('Nutrientes'),
                Link(rel="stylesheet", href="/static/style.css"),
                Script(src="/static/script.js")
            ),
            Body(
                Div(
                    id="feedback", cls="feedback"
                ),

                Div(
                    Div(
                        H1("Cadastro de Nutrientes", cls="logo"),
                        A("Voltar", href="/", cls="button"),
                        cls="header"
                    ),

                    # Card Geral (Formulário e Informações)
                    Div(
                        H2('Cadastro e Informações', cls="card-header"),
                        Div(
                            # Coluna de cadastro
                            Div(
                                Form(
                                    Label('Nome da Matéria-prima:', For='name'),
                                    Input(id='name', name='name', type='text', required=True),
                                    Div(
                                        Label('É um Nutriente?', For='isNutrient', cls="inline-label"),
                                        Input(id='isNutrient', name='isNutrient', type='checkbox', checked=True),
                                        cls="checkbox-wrapper"
                                    ),
                                    Div(
                                        Label('Nutrientes:', cls="nutrient-label"),
                                        Div(
                                            Div(
                                                Input(name='nutrientName', type='text', placeholder='Ex.: N',
                                                      required=True, cls="nutrient-input"),
                                                Input(name='percent', type='number', placeholder='%', min='0',
                                                      max='100', required=True, cls="percent-input"),
                                                Button('+', type='button', onclick="addNutrientField()",
                                                       cls="add-button"),
                                                cls="nutrient-field"
                                            ),
                                            id="nutrientsContainer"
                                        ),
                                        cls="nutrient-wrapper"
                                    ),
                                    Button('Salvar', type='button', onclick="saveNutrient()", cls="save-button"),
                                    cls="form-container"
                                ),
                                cls="form-column"
                            ),
                            # Coluna de tabela informativa
                            Div(
                                Table(
                                    Thead(
                                        Tr(
                                            Th("Informação", cls="table-header"),
                                            Th("Valor", cls="table-header")
                                        )
                                    ),
                                    Tbody(
                                        Tr(
                                            Td("Total de Nutrientes:", cls="table-data"),
                                            Td(id="totalNutrients", cls="table-data")
                                        ),
                                        Tr(
                                            Td("Total de Enchimentos:", cls="table-data"),
                                            Td(id="totalFillers", cls="table-data")
                                        ),
                                        Tr(
                                            Td("Matérias-primas à Base de N:", cls="table-data"),
                                            Td(id="totalNBase", cls="table-data")
                                        ),
                                        Tr(
                                            Td("Matérias-primas à Base de P:", cls="table-data"),
                                            Td(id="totalPBase", cls="table-data")
                                        ),
                                        Tr(
                                            Td("Matérias-primas à Base de K:", cls="table-data"),
                                            Td(id="totalKBase", cls="table-data")
                                        )
                                    ),
                                    cls="info-table"
                                ),
                                cls="table-column"
                            ),
                            cls="main-wrapper"
                        ),
                        cls="general-card"
                    ),

                    # Card Geral (Pesquisa e Nutrientes/Enchimentos)
                    Div(
                        Div(
                            H2('Nutrientes e Enchimentos', cls="card-header"),
                            Div(
                                Input(id='searchInput', type='text', placeholder='Pesquise aqui...', cls='search-input',
                                      oninput="filterData()"),
                                P("Total de Itens: ", Span(id="totalItems"), cls="search-total"),
                                cls="search-container"
                            ),
                        ),
                        Div(id='nutrientCards', cls="cards-container"),
                        cls="general-card"
                    ),

                    cls="container"
                )
            )
        )
