from fasthtml.common import *
from components import menu, nutrientes, formulador1, formulador2, formulador3, formulador4

# Inicialização do app e rotas
app, rt = fast_app()

# Configurar rota para servir arquivos estáticos
app.mount('/static', StaticFiles(directory='static'), name='static')

# Importa e registra os componentes
menu.register_routes(rt)
nutrientes.register_routes(rt)
formulador1.register_routes(rt)
formulador2.register_routes(rt)
formulador3.register_routes(rt)
formulador4.register_routes(rt)

# Inicializar o servidor
serve()
