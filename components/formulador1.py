from fasthtml.common import *
import json

def register_routes(rt):
    # Página principal do formulador
    @rt('/formulador1')
    def formulador1():
        return Html(
            Head(
                Title('Formulador 1 - Teores Conhecidos'),
                Link(rel="stylesheet", href="/static/style.css"),
                Script(src="/static/script.js")
            ),
            Body(
                Div(
                    Div(
                        H1("Formulador 1", cls="logo"),
                        A("Voltar", href="/", cls="button"),
                        cls="header"
                    ),
                    Div(
                        H2("Informe a quantidade (kg) nos nutrientes disponíveis:", cls="section-title"),
                        Div(id="nutrientList", cls="nutrient-list"),
                        Div(
                            H3("Faltam: ", Span(id="remainingKg", cls="remaining-kg"), " KG para completar 1000 kg.", cls="remaining-info"),
                            cls="calculation-info"
                        ),
                        Div(
                            H2("", cls="section-title"),
                            Div(id="summaryCard", cls="summary-card")
                        )

                    ),
                    Div(id="resultContainer", cls="results-container"),
                    cls="container"
                )
            )
        )


