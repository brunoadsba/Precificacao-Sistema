from app import app, verificar_precos_csv

# Executar verificações necessárias
verificar_precos_csv()

if __name__ == "__main__":
    app.run() 