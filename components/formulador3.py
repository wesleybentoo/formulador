from fasthtml.common import *

def register_routes(rt):
    @rt('/formulador3')
    def formulador3():
        return Div(
            H1('Formulador com Nutrientes Não Desejados'),
            P('Funcionalidade em construção...')
        )
