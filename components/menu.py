from fasthtml.common import *

def register_routes(rt):
    @rt('/')
    def menu():
        return Html(
            Head(
                Title('Formulador'),
                Link(rel="stylesheet", href="/static/style.css")
            ),
            Body(
                # HEADER
                Div(
                    Div(
                        H1("Formulador de Fertilizantes", cls="logo"),
                        A("Cadastro de Nutrientes", href="/nutrientes", cls="button"),
                        cls="header"
                    ),
                    # BODY
                    Div(
                        H2("Formulador de fertilizantes básico, inteligente, acessível e 100% gratuito.", cls="title"),
                        P(
                            "Aplicação construída com Python para automatizar cálculos de combinações de formulados. Criado e desenvolvido por Wesley Bento durante a graduação de Engenharia Agronômica - UEL.",
                            cls="description"
                        ),
                        cls="body"
                    ),
                    # FOOTER - Cards
                    Div(
                        Div(
                            H3("FORMULADOR 1", cls="card-title"),
                            P("Simples e direto, calcule fórmulas com teores conhecidos manualmente.", cls="card-description"),
                            A("Acessar", href="/formulador1", cls="card-button"),
                            cls="card"
                        ),
                        Div(
                            H3("FORMULADOR 2", cls="card-title"),
                            P("Permite fórmulas com teores desconhecidos.", cls="card-description"),
                            A("Acessar", href="/formulador2", cls="card-button"),
                            cls="card"
                        ),
                        #Div(
                        #    H3("FORMULADOR 3", cls="card-title"),
                        #    P("Ajuste fórmulas com restrições específicas de nutrientes.", cls="card-description"),
                        #    A("Acessar", href="/formulador3", cls="card-button"),
                        #    cls="card"
                        #),
                        #Div(
                        #    H3("FORMULADOR 4", cls="card-title"),
                        #    P("Funções avançadas para análises e combinações complexas.", cls="card-description"),
                        #    A("Acessar", href="/formulador4", cls="card-button"),
                        #    cls="card"
                        #),
                        cls="cards-container"
                    ),
                    cls="container"
                )
            )
        )
