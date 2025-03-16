document.addEventListener('DOMContentLoaded', function() {
    console.log('Script carregado!');
    
    // Elementos do formulário
    const form = document.getElementById('orcamento-form');
    const servicosContainer = document.getElementById('servicos-container');
    const adicionarServicoBtn = document.getElementById('adicionar-servico');
    const subtotalInput = document.getElementById('subtotal');
    const percentualSesiInput = document.getElementById('percentual-sesi');
    const valorSesiInput = document.getElementById('valor-sesi');
    const totalInput = document.getElementById('total');
    const resultadoSection = document.getElementById('resultado-section');
    const numeroOrcamento = document.getElementById('numero-orcamento');
    const resultadoTotal = document.getElementById('resultado-total');
    const downloadPdfBtn = document.getElementById('download-pdf');
    const novoOrcamentoBtn = document.getElementById('novo-orcamento');
    
    // Verificar se os elementos existem
    if (!form || !servicosContainer) {
        console.error('Elementos essenciais do formulário não encontrados');
        return;
    }
    
    // Variáveis globais
    let servicoIndex = 0;
    let servicos = [];
    
    // Inicialização
    inicializarFormulario();
    
    // Event listeners
    if (adicionarServicoBtn) adicionarServicoBtn.addEventListener('click', adicionarServico);
    if (form) form.addEventListener('submit', handleSubmit);
    if (percentualSesiInput) percentualSesiInput.addEventListener('input', calcularTotal);
    if (novoOrcamentoBtn) novoOrcamentoBtn.addEventListener('click', resetarFormulario);
    
    // Funções
    function inicializarFormulario() {
        console.log('Inicializando formulário...');
        // Carregar serviços para o primeiro item
        carregarServicos(0);
        
        // Configurar event listeners para remover serviço
        document.querySelectorAll('.remover-servico').forEach(btn => {
            btn.addEventListener('click', function() {
                removerServico(parseInt(this.dataset.index));
            });
        });
        
        // Inicializar campos de resumo
        if (subtotalInput) subtotalInput.value = 'R$ 0,00';
        if (valorSesiInput) valorSesiInput.value = 'R$ 0,00';
        if (totalInput) totalInput.value = 'R$ 0,00';
    }
    
    function carregarServicos(index) {
        console.log(`Carregando serviços para o índice ${index}...`);
        const servicoSelect = document.getElementById(`servico-${index}`);
        if (!servicoSelect) {
            console.error(`Elemento select para serviço ${index} não encontrado`);
            return;
        }
        
        fetch('/orcamentos/servicos')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao obter serviços: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Serviços recebidos:', data);
                if (data.success && Array.isArray(data.servicos)) {
                    servicoSelect.innerHTML = '<option value="">Selecione um serviço</option>';
                    data.servicos.forEach(servico => {
                        const option = document.createElement('option');
                        option.value = servico;
                        option.textContent = servico;
                        servicoSelect.appendChild(option);
                    });
                    
                    // Adicionar event listener para carregar regiões quando o serviço mudar
                    servicoSelect.addEventListener('change', function() {
                        carregarRegioes(index);
                    });
                } else {
                    console.error('Erro nos dados de serviços:', data.error || 'Formato de resposta inválido');
                    servicoSelect.innerHTML = '<option value="">Erro ao carregar serviços</option>';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar serviços:', error);
                servicoSelect.innerHTML = '<option value="">Erro ao carregar serviços</option>';
            });
    }
    
    function carregarRegioes(index) {
        console.log(`Carregando regiões para o índice ${index}...`);
        const servicoSelect = document.getElementById(`servico-${index}`);
        const regiaoSelect = document.getElementById(`regiao-${index}`);
        
        if (!servicoSelect || !regiaoSelect) {
            console.error(`Elementos para serviço/região ${index} não encontrados`);
            return;
        }
        
        const servico = servicoSelect.value;
        
        if (!servico) {
            regiaoSelect.innerHTML = '<option value="">Selecione uma região</option>';
            regiaoSelect.disabled = true;
            return;
        }
        
        fetch(`/orcamentos/regioes?servico=${encodeURIComponent(servico)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao obter regiões: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Regiões recebidas:', data);
                if (data.success && Array.isArray(data.regioes)) {
                    regiaoSelect.innerHTML = '<option value="">Selecione uma região</option>';
                    data.regioes.forEach(regiao => {
                        const option = document.createElement('option');
                        option.value = regiao;
                        option.textContent = regiao;
                        regiaoSelect.appendChild(option);
                    });
                    regiaoSelect.disabled = false;
                    
                    // Adicionar event listener para carregar variáveis quando a região mudar
                    regiaoSelect.addEventListener('change', function() {
                        carregarVariaveis(index);
                    });
                } else {
                    console.error('Erro nos dados de regiões:', data.error || 'Formato de resposta inválido');
                    regiaoSelect.innerHTML = '<option value="">Erro ao carregar regiões</option>';
                    regiaoSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('Erro ao carregar regiões:', error);
                regiaoSelect.innerHTML = '<option value="">Erro ao carregar regiões</option>';
                regiaoSelect.disabled = true;
            });
    }
    
    function carregarVariaveis(index) {
        console.log(`Carregando variáveis para o índice ${index}...`);
        const servicoSelect = document.getElementById(`servico-${index}`);
        const regiaoSelect = document.getElementById(`regiao-${index}`);
        const variaveisContainer = document.getElementById(`variaveis-${index}`);
        
        if (!servicoSelect || !regiaoSelect || !variaveisContainer) {
            console.error(`Elementos para variáveis ${index} não encontrados`);
            return;
        }
        
        const servico = servicoSelect.value;
        const regiao = regiaoSelect.value;
        
        if (!servico || !regiao) {
            variaveisContainer.innerHTML = '';
            return;
        }
        
        fetch(`/orcamentos/variaveis/${encodeURIComponent(servico)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao obter variáveis: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Variáveis recebidas:', data);
                if (data.success && data.variaveis) {
                    variaveisContainer.innerHTML = '';
                    
                    Object.entries(data.variaveis).forEach(([key, variavel]) => {
                        const div = document.createElement('div');
                        div.className = 'form-field';
                        
                        const label = document.createElement('label');
                        label.setAttribute('for', `var-${index}-${key}`);
                        label.textContent = variavel.nome || key;
                        
                        let input;
                        if (variavel.tipo === 'select' && Array.isArray(variavel.opcoes)) {
                            input = document.createElement('select');
                            input.id = `var-${index}-${key}`;
                            input.name = `servicos[${index}][variaveis][${key}]`;
                            input.className = 'form-control';
                            
                            variavel.opcoes.forEach(opcao => {
                                const option = document.createElement('option');
                                option.value = opcao;
                                option.textContent = opcao;
                                input.appendChild(option);
                            });
                        } else {
                            input = document.createElement('input');
                            input.id = `var-${index}-${key}`;
                            input.name = `servicos[${index}][variaveis][${key}]`;
                            input.className = 'form-control';
                            
                            if (variavel.tipo === 'numero') {
                                input.type = 'number';
                                if (variavel.min !== undefined) input.min = variavel.min;
                                if (variavel.max !== undefined) input.max = variavel.max;
                                input.value = variavel.min || 0;
                            } else {
                                input.type = 'text';
                            }
                        }
                        
                        // Adicionar event listener para calcular preço quando o valor mudar
                        input.addEventListener('change', function() {
                            calcularPreco(index);
                        });
                        
                        div.appendChild(label);
                        div.appendChild(input);
                        variaveisContainer.appendChild(div);
                    });
                    
                    // Calcular preço inicial
                    calcularPreco(index);
                } else {
                    console.error('Erro nos dados de variáveis:', data.error || 'Formato de resposta inválido');
                    variaveisContainer.innerHTML = '<p>Erro ao carregar variáveis</p>';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar variáveis:', error);
                variaveisContainer.innerHTML = '<p>Erro ao carregar variáveis</p>';
            });
    }
    
    function calcularPreco(index) {
        console.log(`Calculando preço para o índice ${index}...`);
        const servicoSelect = document.getElementById(`servico-${index}`);
        const regiaoSelect = document.getElementById(`regiao-${index}`);
        const valorInput = document.getElementById(`valor-${index}`);
        const variaveisContainer = document.getElementById(`variaveis-${index}`);
        
        if (!servicoSelect || !regiaoSelect || !valorInput || !variaveisContainer) {
            console.error(`Elementos para cálculo de preço ${index} não encontrados`);
            return;
        }
        
        const servico = servicoSelect.value;
        const regiao = regiaoSelect.value;
        
        if (!servico || !regiao) {
            valorInput.value = '';
            return;
        }
        
        // Coletar valores das variáveis
        const dados = {
            servico: servico,
            regiao: regiao
        };
        
        // Adicionar todas as variáveis ao objeto de dados
        variaveisContainer.querySelectorAll('input, select').forEach(input => {
            const varId = input.id.split('-')[2];
            dados[varId] = input.value;
        });
        
        console.log('Dados para cálculo de preço:', dados);
        
        // Enviar requisição para calcular preço
        fetch('/orcamentos/calcular_preco', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao calcular preço: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Preço calculado:', data);
                if (data.success) {
                    valorInput.value = data.preco_formatado || `R$ ${data.preco.toFixed(2).replace('.', ',')}`;
                    
                    // Atualizar serviço na lista
                    const servicoExistente = servicos.findIndex(s => s.index === index);
                    if (servicoExistente !== -1) {
                        servicos[servicoExistente] = {
                            index: index,
                            nome: servico,
                            regiao: regiao,
                            variaveis: dados,
                            valor: data.preco
                        };
                    } else {
                        servicos.push({
                            index: index,
                            nome: servico,
                            regiao: regiao,
                            variaveis: dados,
                            valor: data.preco
                        });
                    }
                    
                    // Recalcular total
                    calcularTotal();
                } else {
                    console.error('Erro ao calcular preço:', data.error);
                    valorInput.value = 'Erro';
                }
            })
            .catch(error => {
                console.error('Erro na requisição de cálculo de preço:', error);
                valorInput.value = 'Erro';
            });
    }
    
    function adicionarServico() {
        console.log('Adicionando novo serviço...');
        servicoIndex++;
        
        const novoServico = document.createElement('div');
        novoServico.className = 'servico-item';
        novoServico.dataset.index = servicoIndex;
        
        novoServico.innerHTML = `
            <div class="form-row">
                <div class="form-field">
                    <label for="servico-${servicoIndex}">Serviço</label>
                    <select id="servico-${servicoIndex}" name="servicos[${servicoIndex}][nome]" class="servico-select" required>
                        <option value="">Selecione um serviço</option>
                    </select>
                </div>
                <div class="form-field">
                    <label for="regiao-${servicoIndex}">Região</label>
                    <select id="regiao-${servicoIndex}" name="servicos[${servicoIndex}][regiao]" class="regiao-select" required disabled>
                        <option value="">Selecione uma região</option>
                    </select>
                </div>
            </div>
            <div class="form-row variaveis-container" id="variaveis-${servicoIndex}">
                <!-- Variáveis dinâmicas serão inseridas aqui -->
            </div>
            <div class="form-row">
                <div class="form-field">
                    <label for="valor-${servicoIndex}">Valor</label>
                    <input type="text" id="valor-${servicoIndex}" name="servicos[${servicoIndex}][valor]" readonly>
                </div>
                <div class="form-field">
                    <button type="button" class="btn btn-danger remover-servico" data-index="${servicoIndex}">Remover</button>
                </div>
            </div>
        `;
        
        servicosContainer.appendChild(novoServico);
        
        // Configurar event listener para remover serviço
        novoServico.querySelector('.remover-servico').addEventListener('click', function() {
            removerServico(parseInt(this.dataset.index));
        });
        
        // Carregar serviços para o novo item
        carregarServicos(servicoIndex);
    }
    
    function removerServico(index) {
        console.log(`Removendo serviço com índice ${index}...`);
        const servicoItem = document.querySelector(`.servico-item[data-index="${index}"]`);
        if (servicoItem) {
            servicoItem.remove();
            
            // Remover serviço da lista
            servicos = servicos.filter(s => s.index !== index);
            
            // Recalcular total
            calcularTotal();
        }
    }
    
    function calcularTotal() {
        console.log('Calculando total...');
        if (!subtotalInput || !valorSesiInput || !totalInput || !percentualSesiInput) {
            console.error('Elementos para cálculo de total não encontrados');
            return;
        }
        
        const subtotal = servicos.reduce((sum, servico) => sum + (servico.valor || 0), 0);
        const percentualSesi = parseFloat(percentualSesiInput.value) || 0;
        const valorSesi = subtotal * (percentualSesi / 100);
        const total = subtotal + valorSesi;
        
        subtotalInput.value = `R$ ${subtotal.toFixed(2).replace('.', ',')}`;
        valorSesiInput.value = `R$ ${valorSesi.toFixed(2).replace('.', ',')}`;
        totalInput.value = `R$ ${total.toFixed(2).replace('.', ',')}`;
    }
    
    function handleSubmit(event) {
        event.preventDefault();
        console.log('Enviando formulário...');
        
        if (servicos.length === 0) {
            alert('Adicione pelo menos um serviço ao orçamento.');
            return;
        }
        
        // Coletar dados do formulário
        const formData = new FormData(form);
        const empresa = formData.get('empresa');
        const email = formData.get('email');
        const telefone = formData.get('telefone');
        const contato = formData.get('contato');
        const percentualSesi = parseFloat(formData.get('percentual_sesi')) || 0;
        const enviarEmail = formData.get('enviar_email') === 'on';
        
        if (!empresa || !email) {
            alert('Preencha os campos obrigatórios: Empresa e E-mail.');
            return;
        }
        
        // Calcular valores
        const subtotal = servicos.reduce((sum, servico) => sum + (servico.valor || 0), 0);
        const valorSesi = subtotal * (percentualSesi / 100);
        const total = subtotal + valorSesi;
        
        // Preparar dados para envio
        const dados = {
            empresa: empresa,
            email: email,
            telefone: telefone || '',
            contato: contato || '',
            servicos: servicos.map(s => ({
                nome: s.nome,
                regiao: s.regiao,
                variaveis: s.variaveis,
                valor: s.valor
            })),
            subtotal: subtotal,
            percentual_sesi: percentualSesi,
            valor_sesi: valorSesi,
            total: total,
            enviar_email: enviarEmail
        };
        
        console.log('Dados do orçamento:', dados);
        
        // Enviar requisição para gerar orçamento
        fetch('/orcamentos/gerar_orcamento', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao gerar orçamento: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Resposta do servidor:', data);
                if (data.success) {
                    // Exibir resultado
                    const formSection = document.getElementById('form-section');
                    if (formSection) formSection.style.display = 'none';
                    
                    if (resultadoSection) {
                        resultadoSection.style.display = 'block';
                        
                        if (numeroOrcamento) numeroOrcamento.textContent = data.numero_orcamento;
                        if (resultadoTotal) resultadoTotal.textContent = `R$ ${data.total.toFixed(2).replace('.', ',')}`;
                        if (downloadPdfBtn) downloadPdfBtn.href = `/orcamentos/download_orcamento/${data.numero_orcamento}`;
                    }
                } else {
                    console.error('Erro ao gerar orçamento:', data.error);
                    alert(`Erro ao gerar orçamento: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Erro na requisição de geração de orçamento:', error);
                alert(`Erro ao gerar orçamento: ${error.message}`);
            });
    }
    
    function resetarFormulario() {
        console.log('Resetando formulário...');
        // Exibir formulário e ocultar resultado
        const formSection = document.getElementById('form-section');
        if (formSection) formSection.style.display = 'block';
        if (resultadoSection) resultadoSection.style.display = 'none';
        
        // Limpar campos
        if (form) form.reset();
        
        // Remover todos os serviços exceto o primeiro
        const servicosItems = document.querySelectorAll('.servico-item');
        for (let i = 1; i < servicosItems.length; i++) {
            servicosItems[i].remove();
        }
        
        // Resetar variáveis
        servicoIndex = 0;
        servicos = [];
        
        // Reinicializar formulário
        inicializarFormulario();
    }
}); 