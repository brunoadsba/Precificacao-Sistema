import os
from app import app, verificar_precos_csv

# Definir variável de ambiente para Vercel
os.environ["VERCEL_ENV"] = "production"

# Executar verificações necessárias
verificar_precos_csv()

# Aplicação para a Vercel
app.logger.info("Aplicação inicializada na Vercel") 

# Exportar para a Vercel
app = app 