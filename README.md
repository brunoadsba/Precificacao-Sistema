# Sistema de Precificação Automática

Sistema web desenvolvido para automatizar a geração de orçamentos de serviços de saúde e segurança ocupacional, com suporte a múltiplos tipos de serviços e cálculos complexos de precificação.

![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Status](https://img.shields.io/badge/status-produção-green)

## 🚀 Funcionalidades

- Geração automática de orçamentos
- Suporte a múltiplos serviços por orçamento
- Cálculo dinâmico de preços baseado em diversos parâmetros
- Envio automático de orçamentos por e-mail
- Interface responsiva e intuitiva
- Modo escuro/claro

### Tipos de Serviços Suportados

#### Serviços Ambientais
- Coleta para Avaliação Ambiental
- Ruído Limítrofe (NBR 10151)
- Relatório Técnico por Agente Ambiental
- Laudo de Insalubridade
- LTCAT - Condições Ambientais de Trabalho
- Laudo de Periculosidade

#### Programa de Gerenciamento de Riscos (PGR)
- Elaboração e acompanhamento do PGR
- Suporte a diferentes graus de risco
- Cálculo baseado no número de trabalhadores

## 💻 Tecnologias Utilizadas

- **Backend**: Python 3.x com Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: CSV para armazenamento de dados
- **E-mail**: SMTP com suporte Gmail
- **Estilização**: Bootstrap 5
- **Deploy**: Vercel

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta Gmail para envio de e-mails (configuração SMTP)

## 🔧 Instalação

1. Clone o repositório:
\`\`\`bash
git clone https://github.com/seu-usuario/precificacao-sistema.git
cd precificacao-sistema
\`\`\`

2. Crie e ative um ambiente virtual:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
\`\`\`

3. Instale as dependências:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Configure as variáveis de ambiente:
Crie um arquivo \`.env\` na raiz do projeto com as seguintes variáveis:
\`\`\`
EMAIL_REMETENTE=seu-email@gmail.com
EMAIL_SENHA=sua-senha-de-app
SECRET_KEY=sua-chave-secreta
\`\`\`

5. Execute a aplicação:
\`\`\`bash
python app.py
\`\`\`

## 📝 Exemplos de Uso

### Exemplo 1: Criando um orçamento para Avaliação Ambiental

1. Acesse a página inicial do sistema
2. Preencha os dados do cliente (empresa, e-mail, telefone)
3. Selecione o serviço "Coleta para Avaliação Ambiental"
4. Escolha a região "Central"
5. Selecione a variável "Pacote (1 a 4 avaliações)"
6. Defina a quantidade como "1"
7. O sistema calculará automaticamente o preço (R$ 300,00)
8. Clique em "Gerar Orçamento"
9. Revise os dados na tela de resumo
10. Confirme para gerar o orçamento final
11. Envie por e-mail ou salve para uso posterior

### Exemplo 2: Orçamento de PGR com múltiplos serviços

1. Preencha os dados do cliente
2. Selecione o serviço "Elaboração e acompanhamento do PGR"
3. Escolha o grau de risco "3 e 4"
4. Selecione a faixa de trabalhadores "20 a 50 Trab."
5. Escolha a região "Norte"
6. Clique em "Adicionar Serviço" para incluir um segundo serviço
7. No novo serviço, selecione "Laudo de Insalubridade"
8. Defina o número de GES/GHE como "2"
9. Escolha a região "Norte"
10. O sistema calculará o valor total do orçamento combinando ambos os serviços
11. Prossiga com a geração do orçamento

## 🖥️ Interface

### Formulário Principal
![Formulário de Orçamento](https://github.com/user-attachments/assets/4a791681-8c47-45f2-aa6e-ced70bc45ab3)

### Seleção de Serviços
![Seleção de Serviços](https://github.com/user-attachments/assets/cf490b7f-f683-4258-90af-52dce301c57d)

### Resumo do Orçamento
![Resumo do Orçamento](https://github.com/user-attachments/assets/3addf805-f13e-4ef0-9691-43a0e362c236)

### E-mail de Orçamento
![E-mail de Orçamento](https://github.com/user-attachments/assets/d5d613f3-3463-4bd7-8b2e-1dd914d58b13)

## 📱 Responsividade

O sistema é totalmente responsivo, adaptando-se a diferentes tamanhos de tela:

- Desktop
- Tablet
- Smartphone

## 🔒 Segurança

- Proteção CSRF em todos os formulários
- Validação de dados no frontend e backend
- Sanitização de inputs
- Variáveis sensíveis em arquivo .env
- Senhas e chaves protegidas

## 📧 Configuração de E-mail

O sistema utiliza SMTP do Gmail para envio de orçamentos. É necessário:
1. Habilitar autenticação de duas etapas no Gmail
2. Gerar senha de aplicativo
3. Configurar as variáveis de ambiente

## ❓ Troubleshooting

### Problemas comuns e soluções

1. **Erro ao enviar e-mail**
   - Verifique se as credenciais no arquivo `.env` estão corretas
   - Confirme se a autenticação de duas etapas está ativada no Gmail
   - Verifique se a senha de aplicativo foi gerada corretamente

2. **Preços não aparecem corretamente**
   - Verifique se os arquivos CSV de preços estão no formato correto
   - Confirme se todos os parâmetros necessários foram selecionados
   - Reinicie a aplicação para recarregar os dados de preços

3. **Erro ao adicionar múltiplos serviços**
   - Limite máximo de 10 serviços por orçamento
   - Verifique se o JavaScript está habilitado no navegador
   - Tente usar um navegador diferente se o problema persistir

4. **Problemas de visualização em dispositivos móveis**
   - Certifique-se de usar um navegador atualizado
   - Limpe o cache do navegador
   - Verifique se o zoom está configurado para 100%

## 🔮 Roadmap

### Próximas atualizações planejadas

#### Versão 1.1.0 (Prevista para Julho/2025)
- Integração com sistema de pagamento online
- Exportação de orçamentos em formato PDF
- Histórico de orçamentos por cliente

#### Versão 1.2.0 (Prevista para Outubro/2025)
- Área de cliente com login
- Dashboard administrativo com estatísticas
- Notificações automáticas de acompanhamento

#### Versão 2.0.0 (Prevista para 2026)
- Aplicativo móvel para Android e iOS
- Integração com sistemas ERP
- Módulo de assinatura digital de contratos

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte ou dúvidas:
- WhatsApp: (71) 9 8707-5563
- E-mail: brunotstba@gmail.com

## 🌐 Demo

Acesse a demonstração do sistema em: [https://precificacao-sistema.vercel.app/](https://precificacao-sistema.vercel.app/)

![Captura de tela 2025-02-28 153610](https://github.com/user-attachments/assets/4a791681-8c47-45f2-aa6e-ced70bc45ab3)

![Captura de tela 2025-02-28 153715](https://github.com/user-attachments/assets/cf490b7f-f683-4258-90af-52dce301c57d)

![Captura de tela 2025-02-28 153732](https://github.com/user-attachments/assets/3addf805-f13e-4ef0-9691-43a0e362c236)

![Captura de tela 2025-02-28 153748](https://github.com/user-attachments/assets/d5d613f3-3463-4bd7-8b2e-1dd914d58b13)

![image](https://github.com/user-attachments/assets/7124a0a5-838a-4be0-98cd-9bb1e2daca51)

![image](https://github.com/user-attachments/assets/141a7894-aa09-4bc8-bfc3-663c98aea26b)

![image](https://github.com/user-attachments/assets/1a2b5e48-711d-4880-bfa8-6489ffa26e3c)



