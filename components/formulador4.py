from fasthtml.common import *

def register_routes(rt):
    @rt('/formulador4')
    def formulador4():
        return Div(
            H1('Formulador com Nutrientes Incluídos/Excluídos'),
            P('Funcionalidade em construção...')
        )
