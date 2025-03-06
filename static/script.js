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
    if (!servico) return;
    
    // Limpar o select de variáveis
    const variavelSelect = document.getElementById(`variavel-${id}`);
    variavelSelect.innerHTML = '<option value="">Selecione uma variável</option>';
    
    // Se for PGR, esconder o campo de variáveis e mostrar os campos específicos de PGR
    if (servico.includes("PGR")) {
        document.getElementById(`parametros-pgr-${id}`).style.display = "block";
        variavelSelect.parentElement.style.display = "none";
        return;
    }
    
    // Para outros serviços, esconder os campos de PGR e mostrar o campo de variáveis
    document.getElementById(`parametros-pgr-${id}`).style.display = "none";
    variavelSelect.parentElement.style.display = "block";
    
    // Fazer requisição para obter as variáveis disponíveis
    fetch(`/obter_variaveis?servico=${encodeURIComponent(servico)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Erro ao obter variáveis:", data.error);
                return;
            }
            
            const variaveis = data.variaveis || [];
            
            // Se não houver variáveis, esconder o campo
            if (variaveis.length === 0) {
                variavelSelect.parentElement.style.display = "none";
                return;
            }
            
            // Adicionar as variáveis ao select
            variaveis.forEach(variavel => {
                const option = document.createElement('option');
                option.value = variavel;
                option.textContent = variavel;
                variavelSelect.appendChild(option);
            });
            
            // Mostrar o campo de variáveis
            variavelSelect.parentElement.style.display = "block";
        })
        .catch(error => {
            console.error("Erro na requisição:", error);
        });
}

// Função para formatar valores monetários no padrão brasileiro (R$ 2.502,00)
function formatarMoeda(valor) {
    // Converte para número caso seja string
    const numero = typeof valor === 'string' ? parseFloat(valor.replace(',', '.')) : valor;
    
    // Formata o número com separador de milhar e duas casas decimais
    return `R$ ${numero.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

// Função para atualizar o preço unitário com base nas seleções
function atualizarPreco(id) {
    const servicoSelect = document.getElementById(`servico-${id}-nome`);
    const regiaoSelect = document.getElementById(`regiao-${id}`);
    const variavelSelect = document.getElementById(`variavel-${id}`);
    const precoUnitarioElement = document.getElementById(`precoUnitario-${id}`);
    const precoUnitarioHidden = document.getElementById(`precoUnitarioHidden-${id}`);
    
    // Verificar se os campos obrigatórios estão preenchidos
    if (!servicoSelect.value || !regiaoSelect.value) {
        precoUnitarioElement.textContent = formatarMoeda(0);
        precoUnitarioHidden.value = 0;
        atualizarPrecoTotal(id);
        return;
    }
    
    // Parâmetros para a requisição
    const params = new URLSearchParams({
        servico: servicoSelect.value,
        regiao: regiaoSelect.value
    });
    
    // Adicionar variável se estiver disponível e não for um serviço de PGR
    if (!servicoSelect.value.includes("PGR") && !servicoSelect.value.includes("Elaboração e acompanhamento do PGR") && 
        variavelSelect.style.display !== "none" && variavelSelect.value) {
        params.append('variavel', variavelSelect.value);
    }
    
    // Adicionar parâmetros específicos para PGR
    if (servicoSelect.value.includes("PGR") || servicoSelect.value.includes("Elaboração e acompanhamento do PGR")) {
        const grauRiscoElements = document.getElementsByName(`servicos[${id-1}][grau_risco]`);
        let grauRisco = "";
        for (const element of grauRiscoElements) {
            if (element.checked) {
                grauRisco = element.value;
                break;
            }
        }
        
        const numTrabalhadores = document.getElementById(`numTrabalhadores-${id}`).value;
        
        if (!grauRisco || !numTrabalhadores) {
            precoUnitarioElement.textContent = formatarMoeda(0);
            precoUnitarioHidden.value = 0;
            atualizarPrecoTotal(id);
            return;
        }
        
        params.append('grau_risco', grauRisco);
        params.append('num_trabalhadores', numTrabalhadores);
    }
    
    // Fazer requisição para obter o preço
    fetch(`/calcular_preco?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Erro ao calcular preço:", data.error);
                precoUnitarioElement.textContent = "Erro ao calcular preço";
                precoUnitarioHidden.value = 0;
            } else {
                const preco = parseFloat(data.preco);
                precoUnitarioElement.textContent = formatarMoeda(preco);
                precoUnitarioHidden.value = preco;
            }
            atualizarPrecoTotal(id);
        })
        .catch(error => {
            console.error("Erro na requisição:", error);
            precoUnitarioElement.textContent = "Erro na requisição";
            precoUnitarioHidden.value = 0;
            atualizarPrecoTotal(id);
        });
}

// Função para atualizar o preço total com base na quantidade
function atualizarPrecoTotal(id) {
    const precoUnitarioHidden = document.getElementById(`precoUnitarioHidden-${id}`);
    const precoTotalElement = document.getElementById(`precoTotal-${id}`);
    const precoTotalHidden = document.getElementById(`precoTotalHidden-${id}`);
    const quantidadeInput = document.getElementById(`quantidade-${id}`);
    
    const precoUnitario = parseFloat(precoUnitarioHidden.value) || 0;
    const quantidade = parseInt(quantidadeInput.value) || 1;
    
    const precoTotal = precoUnitario * quantidade;
    
    precoTotalElement.textContent = formatarMoeda(precoTotal);
    precoTotalHidden.value = precoTotal;
    
    atualizarTotalOrcamento();
}

// Função para atualizar o total do orçamento
function atualizarTotalOrcamento() {
    const precosTotaisHidden = document.querySelectorAll('[id^="precoTotalHidden-"]');
    const totalOrcamentoElement = document.getElementById('totalOrcamento');
    const totalOrcamentoHidden = document.getElementById('totalOrcamentoHidden');
    
    let total = 0;
    precosTotaisHidden.forEach(input => {
        total += parseFloat(input.value) || 0;
    });
    
    totalOrcamentoElement.textContent = formatarMoeda(total);
    totalOrcamentoHidden.value = total;
}

// Função para adicionar um novo serviço
function adicionarServico() {
    const servicosContainer = document.getElementById('servicos-container');
    const servicoCards = document.querySelectorAll('.servico-card');
    const novoId = servicoCards.length + 1;
    const novoIndex = servicoCards.length;
    
    // Criar novo card de serviço
    const novoCard = document.createElement('div');
    novoCard.className = 'card mb-4 servico-card';
    novoCard.style.backgroundColor = '#1a202c';
    novoCard.style.border = 'none';
    
    // HTML para o novo card
    novoCard.innerHTML = `
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h3 class="mb-0">Serviço (${novoId}):</h3>
        </div>
        <div class="card-body" style="background-color: #1a202c;">
            <!-- Etapa 1: Seleção do Serviço -->
            <div class="mb-3">
                <label for="servico-${novoId}-nome" class="form-label text-white">Selecione um serviço:</label>
                <select class="form-select servico-select" id="servico-${novoId}-nome" name="servicos[${novoIndex}][nome]" required onchange="mostrarCamposAdicionais(${novoId}); atualizarPreco(${novoId})">
                    <option value="">Selecione um serviço</option>
                    ${Array.from(document.getElementById('servico-1-nome').options)
                        .map(option => `<option value="${option.value}">${option.text}</option>`)
                        .join('')}
                </select>
            </div>
            
            <!-- Etapa 2: Parâmetros Específicos para PGR -->
            <div id="parametros-pgr-${novoId}" class="parametros-pgr" style="display: none;">
                <div class="mb-3">
                    <label class="form-label text-white">Grau de Risco:</label>
                    <div class="radio-group">
                        <input type="radio" class="btn-check grau-risco" name="servicos[${novoIndex}][grau_risco]" id="grauRisco1e2-${novoId}" value="1 e 2" checked onchange="atualizarPreco(${novoId})">
                        <label class="btn btn-radio" for="grauRisco1e2-${novoId}">1 e 2</label>
                        
                        <input type="radio" class="btn-check grau-risco" name="servicos[${novoIndex}][grau_risco]" id="grauRisco3e4-${novoId}" value="3 e 4" onchange="atualizarPreco(${novoId})">
                        <label class="btn btn-radio" for="grauRisco3e4-${novoId}">3 e 4</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="numTrabalhadores-${novoId}" class="form-label text-white">Número de Trabalhadores:</label>
                    <select class="form-select num-trabalhadores" id="numTrabalhadores-${novoId}" name="servicos[${novoIndex}][num_trabalhadores]" onchange="atualizarPreco(${novoId})">
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
                <label for="regiao-${novoId}" class="form-label text-white">Região:</label>
                <select class="form-select regiao-select" id="regiao-${novoId}" name="servicos[${novoIndex}][regiao]" required onchange="atualizarPreco(${novoId})">
                    <option value="">Selecione a região</option>
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
                <label for="variavel-${novoId}" class="form-label text-white">Selecione a Variável:</label>
                <select class="form-select variavel-select" id="variavel-${novoId}" name="servicos[${novoIndex}][variavel]" onchange="atualizarPreco(${novoId})">
                    <option value="">Selecione uma variável</option>
                </select>
            </div>

            <div class="mb-3">
                <label for="quantidade-${novoId}" class="form-label text-white">Quantidade:</label>
                <input type="number" class="form-control quantidade-input" id="quantidade-${novoId}" name="servicos[${novoIndex}][quantidade]" value="1" min="1" onchange="atualizarPrecoTotal(${novoId})">
            </div>
            
            <!-- Etapa 3: Visualização do Preço -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5 class="card-title">Preço Unitário:</h5>
                            <h4 class="card-text preco-unitario" id="precoUnitario-${novoId}">${formatarMoeda(0)}</h4>
                            <input type="hidden" id="precoUnitarioHidden-${novoId}" name="servicos[${novoIndex}][preco_unitario]" value="0">
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h5 class="card-title">Preço Total:</h5>
                            <h4 class="card-text preco-total" id="precoTotal-${novoId}">${formatarMoeda(0)}</h4>
                            <input type="hidden" id="precoTotalHidden-${novoId}" name="servicos[${novoIndex}][preco_total]" value="0">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar o novo card ao container
    servicosContainer.appendChild(novoCard);
    
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