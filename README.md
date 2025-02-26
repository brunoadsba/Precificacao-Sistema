# Precificação Automática

Sistema web para geração de orçamentos automáticos com base em serviços preenchidos pelo cliente.

## Estrutura
- `app.py`: Lógica principal do Flask.
- `precificacao.py`: Funções de precificação e geração de planilha.
- `email_sender.py`: Envio de e-mails.
- `static/`: Arquivos CSS e JS.
- `templates/`: Templates HTML.
- `requirements.txt`: Dependências do projeto.
- `.env`: Configuração de credenciais de e-mail.

## Requisitos
- Python 3.8 ou superior
- WSL (Windows Subsystem for Linux)

## Instalação
1. Clone o repositório ou copie os arquivos para um diretório local.
2. Ative o WSL e navegue até o diretório do projeto:
   ```bash
   cd /caminho/para/seu/projeto
   ```
3. Crie e ative o ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Execução
1. Certifique-se de que o ambiente virtual está ativado:
   ```bash
   source venv/bin/activate
   ```
2. Execute o aplicativo Flask:
   ```bash
   python app.py
   ```
3. Abra um navegador e acesse `http://localhost:5000`.

## Configuração de E-mail
- Configure o arquivo `.env` com suas credenciais de e-mail:
  ```
  EMAIL_REMETENTE=seuemail@gmail.com
  EMAIL_SENHA=sua_senha_de_aplicativo
  ```

## Solução de Problemas
- **Localidade `pt_BR.UTF-8` não suportada:** Certifique-se de que a localidade está instalada no WSL:
  ```bash
  sudo locale-gen pt_BR.UTF-8
  sudo update-locale LANG=pt_BR.UTF-8
  ```

Se precisar de mais alguma coisa, estou à disposição!# Precificacao-Sistema
# Precificacao-Sistema
# Precificacao-Sistema
