// Variável para controlar o contador de serviços
let contadorServicos = 1;

// Função para mostrar campos adicionais quando PGR for selecionado
function mostrarCamposAdicionais(id) {
    const servico = document.getElementById(`servico-${id}-nome`).value;
    const parametrosPGR = document.getElementById(`parametros-pgr-${id}`);
    
    if (servico === 'Elaboração e acompanhamento do PGR') {
        parametrosPGR.style.display = 'block';
        atualizarPreco(id); // Atualiza o preço imediatamente
    } else {
        parametrosPGR.style.display = 'none';
        atualizarPreco(id); // Atualiza o preço para outros serviços
    }
    
    // Adicionar chamada para atualizar as variáveis disponíveis
    atualizarVariaveisDisponiveis(id, servico);
}

// Adicionar nova função para atualizar as variáveis disponíveis
function atualizarVariaveisDisponiveis(id, servico) {
    // Fazer uma requisição para obter as variáveis disponíveis para o serviço selecionado
    fetch(`/obter_variaveis?servico=${encodeURIComponent(servico)}`)
        .then(response => response.json())
        .then(data => {
            const variavelSelect = document.getElementById(`variavel-${id}`);
            // Limpar opções atuais
            variavelSelect.innerHTML = '<option value="">Selecione uma variável</option>';
            
            // Adicionar novas opções
            if (data.variaveis && data.variaveis.length > 0) {
                data.variaveis.forEach(variavel => {
                    const option = document.createElement('option');
                    option.value = variavel;
                    option.textContent = variavel;
                    variavelSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "Nenhuma variável disponível";
                variavelSelect.appendChild(option);
            }
            
            // Atualizar o preço após carregar as variáveis
            atualizarPreco(id);
        })
        .catch(error => {
            console.error('Erro ao obter variáveis:', error);
        });
}

// Função para atualizar o preço unitário com base nas seleções
function atualizarPreco(id) {
    const servico = document.getElementById(`servico-${id}-nome`).value;
    const regiao = document.getElementById(`regiao-${id}`).value;
    const variavel = document.getElementById(`variavel-${id}`).value;
    const quantidade = parseInt(document.getElementById(`quantidade-${id}`).value) || 1;
    let grauRisco = null, numTrabalhadores = null;

    if (servico === 'Elaboração e acompanhamento do PGR') {
        grauRisco = document.querySelector(`input[name="servicos[${id-1}][grau_risco]"]:checked`)?.value || '1 e 2';
        numTrabalhadores = document.getElementById(`numTrabalhadores-${id}`).value;
    }

    if (servico && regiao) {
        // Construir a URL corretamente, usando '&'
        let url = `/calcular_preco?servico=${encodeURIComponent(servico)}&regiao=${encodeURIComponent(regiao)}&variavel=${encodeURIComponent(variavel || '')}&quantidade=${quantidade}`;
        if (grauRisco) url += `&grau_risco=${encodeURIComponent(grauRisco)}`;
        if (numTrabalhadores) url += `&num_trabalhadores=${encodeURIComponent(numTrabalhadores)}`;

        console.log(`Fazendo requisição para: ${url}`);

        fetch(url, {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.preco_unitario && data.preco_unitario > 0) {
                document.getElementById(`precoUnitario-${id}`).textContent = `R$ ${data.preco_unitario.toFixed(2).replace('.', ',')}`;
                document.getElementById(`precoUnitarioHidden-${id}`).value = data.preco_unitario;
            } else {
                document.getElementById(`precoUnitario-${id}`).textContent = 'R$ 0,00';
                document.getElementById(`precoUnitarioHidden-${id}`).value = 0;
            }
            atualizarPrecoTotal(id);
        })
        .catch(error => {
            console.error('Erro ao calcular preço:', error);
            document.getElementById(`precoUnitario-${id}`).textContent = 'R$ 0,00';
            document.getElementById(`precoUnitarioHidden-${id}`).value = 0;
            atualizarPrecoTotal(id);
        });
    } else {
        document.getElementById(`precoUnitario-${id}`).textContent = 'R$ 0,00';
        document.getElementById(`precoUnitarioHidden-${id}`).value = 0;
        atualizarPrecoTotal(id);
    }
}

// Função para atualizar o preço total com base na quantidade
function atualizarPrecoTotal(id) {
    const precoUnitarioText = document.getElementById(`precoUnitario-${id}`).textContent;
    const precoUnitario = parseFloat(precoUnitarioText.replace('R$ ', '').replace(',', '.')) || 0;
    const quantidade = parseInt(document.getElementById(`quantidade-${id}`).value) || 1;
    
    // Garante que o preço total seja calculado corretamente com base no preço unitário retornado
    const precoTotal = precoUnitario * quantidade;
    document.getElementById(`precoTotal-${id}`).textContent = `R$ ${precoTotal.toFixed(2).replace('.', ',')}`;
    document.getElementById(`precoTotalHidden-${id}`).value = precoTotal;
    
    // Atualizar o total do orçamento
    atualizarTotalOrcamento();
}

// Função para atualizar o total do orçamento
function atualizarTotalOrcamento() {
    let total = 0;
    const precosTotais = document.querySelectorAll('.preco-total');
    
    precosTotais.forEach(function(elemento) {
        const precoText = elemento.textContent;
        const preco = parseFloat(precoText.replace('R$ ', '').replace(',', '.')) || 0;
        total += preco;
    });
    
    document.getElementById('totalOrcamento').textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
    document.getElementById('totalOrcamentoHidden').value = total;
}

// Função para adicionar um novo serviço
function adicionarServico() {
    contadorServicos++;
    
    const servicosContainer = document.getElementById('servicos-container');
    const novoServico = document.createElement('div');
    novoServico.className = 'card mb-4 servico-card';
    novoServico.id = `servico-${contadorServicos}`;
    
    novoServico.innerHTML = `
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h3 class="mb-0">Serviço (${contadorServicos}):</h3>
        </div>
        <div class="card-body">
            <!-- Etapa 1: Seleção do Serviço -->
            <div class="mb-3">
                <label for="servico-${contadorServicos}-nome" class="form-label">Selecione um serviço:</label>
                <select class="form-select servico-select" id="servico-${contadorServicos}-nome" name="servicos[${contadorServicos-1}][nome]" required onchange="mostrarCamposAdicionais(${contadorServicos}); atualizarPreco(${contadorServicos})">
                    <option value="">Selecione um serviço</option>
                    ${Array.from(document.getElementById('servico-1-nome').options).map(option => 
                        `<option value="${option.value}">${option.text}</option>`
                    ).join('')}
                </select>
            </div>
            
            <!-- Etapa 2: Parâmetros Específicos para PGR -->
            <div id="parametros-pgr-${contadorServicos}" class="parametros-pgr" style="display: none;">
                <div class="mb-3">
                    <label class="form-label">Grau de Risco:</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check grau-risco" name="servicos[${contadorServicos-1}][grau_risco]" id="grauRisco1e2-${contadorServicos}" value="1 e 2" checked onchange="atualizarPreco(${contadorServicos})">
                        <label class="btn btn-outline-primary" for="grauRisco1e2-${contadorServicos}">1 e 2</label>
                        
                        <input type="radio" class="btn-check grau-risco" name="servicos[${contadorServicos-1}][grau_risco]" id="grauRisco3e4-${contadorServicos}" value="3 e 4" onchange="atualizarPreco(${contadorServicos})">
                        <label class="btn btn-outline-primary" for="grauRisco3e4-${contadorServicos}">3 e 4</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="numTrabalhadores-${contadorServicos}" class="form-label">Número de Trabalhadores:</label>
                    <select class="form-select num-trabalhadores" id="numTrabalhadores-${contadorServicos}" name="servicos[${contadorServicos-1}][num_trabalhadores]" onchange="atualizarPreco(${contadorServicos})">
                        <option value="">Selecione a faixa</option>
                        <option value="ate19">Até 19 Trabalhadores</option>
                        <option value="20a50">20 a 50 Trabalhadores</option>
                        <option value="51a100">51 a 100 Trabalhadores</option>
                        <option value="101a160">101 a 160 Trabalhadores</option>
                        <option value="161a250">161 a 250 Trabalhadores</option>
                        <option value="251a300">251 a 300 Trabalhadores</option>
                        <option value="301a350">301 a 350 Trabalhadores</option>
                        <option value="351a400">351 a 400 Trabalhadores</option>
                        <option value="401a450">401 a 450 Trabalhadores</option>
                        <option value="451a500">451 a 500 Trabalhadores</option>
                        <option value="501a550">501 a 550 Trabalhadores</option>
                        <option value="551a600">551 a 600 Trabalhadores</option>
                        <option value="601a650">601 a 650 Trabalhadores</option>
                        <option value="651a700">651 a 700 Trabalhadores</option>
                        <option value="701a750">701 a 750 Trabalhadores</option>
                        <option value="751a800">751 a 800 Trabalhadores</option>
                    </select>
                </div>
            </div>
            
            <!-- Campos comuns para todos os serviços -->
            <div class="mb-3">
                <label for="regiao-${contadorServicos}" class="form-label">Região/Instituto:</label>
                <select class="form-select regiao-select" id="regiao-${contadorServicos}" name="servicos[${contadorServicos-1}][regiao]" required onchange="atualizarPreco(${contadorServicos})">
                    <option value="">Selecione a região ou Instituto</option>
                    <option value="Instituto">Instituto</option>
                    <option value="Central">Central</option>
                    <option value="Norte">Norte</option>
                    <option value="Oeste">Oeste</option>
                    <option value="Sudoeste">Sudoeste</option>
                    <option value="Sul">Sul</option>
                    <option value="Extremo Sul">Extremo Sul</option>
                </select>
            </div>

            <!-- Novo campo para Variável -->
            <div class="mb-3">
                <label for="variavel-${contadorServicos}" class="form-label">Selecione a Variável:</label>
                <select class="form-select variavel-select" id="variavel-${contadorServicos}" name="servicos[${contadorServicos-1}][variavel]" onchange="atualizarPreco(${contadorServicos})">
                    <option value="">Selecione uma variável</option>
                    {% for variavel in ['Pacote (1 a 4 avaliações)', 'Por Avaliação Adicional', 'Por Relatório Unitário', 'Base + Adicional por GES/GHE', 'Adicional por GES/GHE Revisado', 'Por Laudo Técnico'] %}
                        <option value="{{ variavel }}">{{ variavel }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="mb-3">
                <label for="quantidade-${contadorServicos}" class="form-label">Quantidade:</label>
                <input type="number" class="form-control quantidade-input" id="quantidade-${contadorServicos}" name="servicos[${contadorServicos-1}][quantidade]" value="1" min="1" onchange="atualizarPrecoTotal(${contadorServicos})">
            </div>
            
            <!-- Etapa 3: Visualização do Preço -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5 class="card-title">Preço Unitário:</h5>
                            <h4 class="card-text preco-unitario" id="precoUnitario-${contadorServicos}">R$ 0,00</h4>
                            <input type="hidden" id="precoUnitarioHidden-${contadorServicos}" name="servicos[${contadorServicos-1}][preco_unitario]" value="0">
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5 class="card-title">Preço Total:</h5>
                            <h4 class="card-text preco-total" id="precoTotal-${contadorServicos}">R$ 0,00</h4>
                            <input type="hidden" id="precoTotalHidden-${contadorServicos}" name="servicos[${contadorServicos-1}][preco_total]" value="0">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    servicosContainer.appendChild(novoServico);
    
    // Adicionar event listener para o novo serviço
    const novoServicoSelect = document.getElementById(`servico-${contadorServicos}-nome`);
    if (novoServicoSelect) {
        novoServicoSelect.addEventListener('change', function() {
            const servico = this.value;
            atualizarVariaveisDisponiveis(contadorServicos, servico);
            mostrarCamposAdicionais(contadorServicos);
        });
    }
    
    // Mostrar o botão de remover serviço
    document.getElementById('removerServico').style.display = 'block';
}

// Função para remover o último serviço
function removerServico() {
    if (contadorServicos > 1) {
        const servicosContainer = document.getElementById('servicos-container');
        const ultimoServico = document.getElementById(`servico-${contadorServicos}`);
        
        servicosContainer.removeChild(ultimoServico);
        contadorServicos--;
        
        // Esconder o botão de remover se só houver um serviço
        if (contadorServicos === 1) {
            document.getElementById('removerServico').style.display = 'none';
        }
        
        // Atualizar o total do orçamento
        atualizarTotalOrcamento();
    }
}

// Inicializar os event listeners quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Event listener para o botão de adicionar serviço
    const btnAdicionarServico = document.getElementById('adicionarServico');
    if (btnAdicionarServico) {
        btnAdicionarServico.addEventListener('click', adicionarServico);
    }
    
    // Event listener para o botão de remover serviço
    const btnRemoverServico = document.getElementById('removerServico');
    if (btnRemoverServico) {
        btnRemoverServico.addEventListener('click', removerServico);
    }

    // Adicionar event listener para atualizar variáveis quando o serviço é alterado
    const servicoSelect = document.getElementById('servico-1-nome');
    if (servicoSelect) {
        servicoSelect.addEventListener('change', function() {
            const servico = this.value;
            atualizarVariaveisDisponiveis(1, servico);
            mostrarCamposAdicionais(1);
        });
    }

    // Inicializar preços para o primeiro serviço
    atualizarPreco(1);

    // Adicionar eventos onchange para todos os campos relevantes
    document.querySelectorAll('.servico-select, .regiao-select, .variavel-select, .grau-risco, .num-trabalhadores, .quantidade-input').forEach(element => {
        element.addEventListener('change', function() {
            const container = this.closest('.servico-card');
            const id = container.id.split('-')[1];
            atualizarPreco(id);
        });
    });
});