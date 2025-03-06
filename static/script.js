// Variável para controlar o contador de serviços
let contadorServicos = 1;

// Função para mostrar campos adicionais quando PGR for selecionado
function mostrarCamposAdicionais(id) {
    const servicoSelect = document.getElementById(`servico-${id}-nome`);
    const servicoSelecionado = servicoSelect.value;
    const parametrosPgr = document.getElementById(`parametros-pgr-${id}`);
    const variavelContainer = document.getElementById(`variavel-${id}`).parentElement;
    const gesGheContainer = document.getElementById(`ges-ghe-container-${id}`);
    const avaliacoesAdicionaisContainer = document.getElementById(`avaliacoes-adicionais-container-${id}`);
    
    // Esconder campos específicos inicialmente
    parametrosPgr.style.display = "none";
    gesGheContainer.style.display = "none";
    avaliacoesAdicionaisContainer.style.display = "none";
    
    if (!servicoSelecionado) return;
    
    // Se for um serviço de PGR, mostrar os campos específicos de PGR
    if (servicoSelecionado.includes("PGR") || servicoSelecionado.includes("Elaboração e acompanhamento do PGR")) {
        parametrosPgr.style.display = "block";
        variavelContainer.style.display = "none"; // Esconder variáveis apenas para PGR
    } else {
        // Para outros serviços, mostrar o campo de variáveis e atualizar as opções
        parametrosPgr.style.display = "none";
        variavelContainer.style.display = "block"; // Mostrar variáveis para outros serviços
        atualizarVariaveisDisponiveis(id, servicoSelecionado);
        
        // Verificar se o serviço requer campo GES/GHE
        const servicosComGesGhe = [
            "Laudo de Insalubridade",
            "Revisão de Laudo de Insalubridade (após 90 dias)",
            "LTCAT - Condições Ambientais de Trabalho",
            "Revisão de LTCAT (após 90 dias)"
        ];
        
        if (servicosComGesGhe.some(s => servicoSelecionado.includes(s))) {
            gesGheContainer.style.display = "block";
        }
    }
}

// Corrigir a função atualizarVariaveisDisponiveis para evitar duplicatas
function atualizarVariaveisDisponiveis(id, servico) {
    console.log(`Atualizando variáveis para serviço: ${servico}, id: ${id}`);
    
    if (!servico) return;
    
    const variavelSelect = document.getElementById(`variavel-${id}`);
    const variavelContainer = variavelSelect.parentElement;
    const avaliacaoAdicionalContainer = document.getElementById(`avaliacao-adicional-container-${id}`);
    const quantidadeAvaliacoesContainer = document.getElementById(`quantidade-avaliacoes-container-${id}`);
    
    // Limpar e mostrar o select de variáveis
    variavelSelect.innerHTML = '<option value="">Selecione uma variável</option>';
    variavelContainer.style.display = "block";
    
    // Esconder containers adicionais inicialmente
    if (avaliacaoAdicionalContainer) avaliacaoAdicionalContainer.style.display = "none";
    if (quantidadeAvaliacoesContainer) quantidadeAvaliacoesContainer.style.display = "none";
    
    // Serviços que usam o padrão Pacote + Avaliação Adicional
    const servicosPacote = [
        "Coleta para Avaliação Ambiental",
        "Ruído Limítrofe (NBR 10151)"
    ];
    
    // Serviços que usam apenas uma variável única
    const servicosUnitarios = [
        "Relatório Técnico por Agente Ambiental",
        "Revisão de Relatório Técnico (após 90 dias)",
        "Laudo de Periculosidade",
        "Revisão de Laudo de Periculosidade (após 90 dias)"
    ];
    
    // Serviços que usam GES/GHE
    const servicosGesGhe = [
        "Laudo de Insalubridade",
        "Revisão de Laudo de Insalubridade (após 90 dias)",
        "LTCAT - Condições Ambientais de Trabalho",
        "Revisão de LTCAT (após 90 dias)"
    ];
    
    if (servicosPacote.includes(servico)) {
        // Adicionar opção de pacote
        const optionPacote = document.createElement('option');
        optionPacote.value = "Pacote (1 a 4 avaliações)";
        optionPacote.textContent = "Pacote (1 a 4 avaliações)";
        variavelSelect.appendChild(optionPacote);
        
        // Adicionar event listener para mostrar opção de avaliação adicional
        variavelSelect.addEventListener('change', function() {
            if (this.value === "Pacote (1 a 4 avaliações)") {
                avaliacaoAdicionalContainer.style.display = "block";
            } else {
                avaliacaoAdicionalContainer.style.display = "none";
                quantidadeAvaliacoesContainer.style.display = "none";
            }
            atualizarPreco(id);
        });
    } 
    else if (servicosUnitarios.includes(servico)) {
        // Adicionar opção unitária apropriada
        const optionUnitaria = document.createElement('option');
        optionUnitaria.value = "Por Relatório Unitário";
        optionUnitaria.textContent = "Por Relatório Unitário";
        
        if (servico.includes("Periculosidade")) {
            optionUnitaria.value = "Por Laudo Técnico";
            optionUnitaria.textContent = "Por Laudo Técnico";
        }
        
        variavelSelect.appendChild(optionUnitaria);
    }
    else if (servicosGesGhe.includes(servico)) {
        // Adicionar opção GES/GHE apropriada
        const optionGesGhe = document.createElement('option');
        if (servico.includes("Revisão")) {
            optionGesGhe.value = "Adicional por GES/GHE Revisado";
            optionGesGhe.textContent = "Adicional por GES/GHE Revisado";
        } else {
            optionGesGhe.value = "Base + Adicional por GES/GHE";
            optionGesGhe.textContent = "Base + Adicional por GES/GHE";
        }
        variavelSelect.appendChild(optionGesGhe);
    }
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
    const numGesGheInput = document.getElementById(`num-ges-ghe-${id}`);
    
    // Verificar se os campos obrigatórios estão preenchidos
    if (!servicoSelect.value || !regiaoSelect.value || !variavelSelect.value) {
        precoUnitarioElement.textContent = formatarMoeda(0);
        precoUnitarioHidden.value = 0;
        atualizarPrecoTotal(id);
        return;
    }
    
    // Parâmetros para a requisição
    const params = new URLSearchParams({
        servico: servicoSelect.value,
        regiao: regiaoSelect.value,
        variavel: variavelSelect.value
    });
    
    // Verificar se é um serviço com GES/GHE
    const servicosGesGhe = [
        "Laudo de Insalubridade",
        "Revisão de Laudo de Insalubridade (após 90 dias)",
        "LTCAT - Condições Ambientais de Trabalho",
        "Revisão de LTCAT (após 90 dias)"
    ];
    
    // Se for serviço com GES/GHE e tiver o número de GES/GHE preenchido
    if (servicosGesGhe.includes(servicoSelect.value) && numGesGheInput) {
        const numGesGhe = parseInt(numGesGheInput.value) || 0;
        params.append('num_ges_ghe', numGesGhe);
    }
    
    // Verificar se tem avaliações adicionais
    const avaliacaoAdicionalSelect = document.getElementById(`avaliacao-adicional-${id}`);
    const quantidadeAvaliacoesInput = document.getElementById(`quantidade-avaliacoes-${id}`);
    
    if (avaliacaoAdicionalSelect && 
        avaliacaoAdicionalSelect.value === "sim" && 
        quantidadeAvaliacoesInput && 
        quantidadeAvaliacoesInput.style.display !== "none") {
        params.append('quantidade_avaliacoes', quantidadeAvaliacoesInput.value);
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
    try {
        console.log("Função adicionarServico() iniciada");
        
        const servicosContainer = document.getElementById('servicos-container');
        if (!servicosContainer) {
            console.error("Container de serviços não encontrado");
            return;
        }
        
        const servicoCards = document.querySelectorAll('.servico-card');
        const novoId = servicoCards.length + 1;
        const novoIndex = servicoCards.length;
        
        console.log(`Adicionando novo serviço com ID: ${novoId}, index: ${novoIndex}`);
        
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

                <!-- Campo para número de avaliações adicionais -->
                <div class="mb-3 avaliacoes-adicionais-container" id="avaliacoes-adicionais-container-${novoId}" style="display: none;">
                    <label for="num-avaliacoes-adicionais-${novoId}" class="form-label text-white">Número de Avaliações Adicionais:</label>
                    <select class="form-select" id="num-avaliacoes-adicionais-${novoId}" name="servicos[${novoIndex}][num_avaliacoes_adicionais]" onchange="atualizarPrecoAvaliacoesAdicionais(${novoId})">
                        <option value="1">1 avaliação adicional</option>
                        <option value="2">2 avaliações adicionais</option>
                        <option value="3">3 avaliações adicionais</option>
                        <option value="4">4 avaliações adicionais</option>
                        <option value="5">5 avaliações adicionais</option>
                        <option value="6">6 avaliações adicionais</option>
                        <option value="7">7 avaliações adicionais</option>
                        <option value="8">8 avaliações adicionais</option>
                        <option value="9">9 avaliações adicionais</option>
                        <option value="10">10 avaliações adicionais</option>
                    </select>
                </div>

                <!-- Campo para número de GES/GHE -->
                <div class="mb-3 ges-ghe-container" id="ges-ghe-container-${novoId}" style="display: none;">
                    <label for="num-ges-ghe-${novoId}" class="form-label text-white">Número de GES/GHE:</label>
                    <input type="number" class="form-control num-ges-ghe" id="num-ges-ghe-${novoId}" name="servicos[${novoIndex}][num_ges_ghe]" value="1" min="1" onchange="atualizarPreco(${novoId})">
                    <small class="form-text text-muted text-white">Grupos de Exposição Similar/Grupos Homogêneos de Exposição</small>
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
        const removerBtn = document.getElementById('removerServico');
        if (removerBtn) {
            console.log("Exibindo botão de remover serviço");
            removerBtn.style.display = 'block';
        } else {
            console.error("Botão de remover serviço não encontrado");
        }
        
        // Adicionar event listener para o select de variáveis
        adicionarEventListenerVariavel(novoId);
        
        console.log("Serviço adicionado com sucesso");
    } catch (error) {
        console.error("Erro ao adicionar serviço:", error);
        alert(`Erro ao adicionar serviço: ${error.message}`);
    }
}

// Função para remover o último serviço
function removerServico() {
    try {
        console.log("Função removerServico() iniciada");
        
        const servicosContainer = document.getElementById('servicos-container');
        const servicoCards = document.querySelectorAll('.servico-card');
        
        console.log(`Número de cards de serviço encontrados: ${servicoCards.length}`);
        
        if (servicoCards.length <= 1) {
            console.error("Tentativa de remover o único serviço. Operação cancelada.");
            alert("Não é possível remover o único serviço!");
            return;
        }
        
        // Remover o último card
        const ultimoCard = servicoCards[servicoCards.length - 1];
        console.log(`Removendo card de serviço com ID: ${ultimoCard.id || 'ID não encontrado'}`);
        
        servicosContainer.removeChild(ultimoCard);
        
        // Verificar se o botão de remover deve ser escondido
        if (document.querySelectorAll('.servico-card').length <= 1) {
            console.log("Escondendo botão de remover serviço");
            document.getElementById('removerServico').style.display = 'none';
        }
        
        // Atualizar o total do orçamento
        console.log("Atualizando total do orçamento");
        atualizarTotalOrcamento();
        
        console.log("Serviço removido com sucesso");
    } catch (error) {
        console.error("Erro ao remover serviço:", error);
        alert(`Erro ao remover serviço: ${error.message}`);
    }
}

// Função para inicializar os eventos apenas uma vez
function inicializarEventos() {
    console.log("Inicializando eventos dos botões");
    
    // Remover eventos existentes para evitar duplicação
    const removerBtn = document.getElementById('removerServico');
    const adicionarBtn = document.getElementById('adicionarServico');
    
    if (removerBtn) {
        // Remover todos os event listeners existentes
        const novoRemoverBtn = removerBtn.cloneNode(true);
        removerBtn.parentNode.replaceChild(novoRemoverBtn, removerBtn);
        
        // Adicionar novo event listener
        console.log("Adicionando evento de clique ao botão de remover serviço");
        novoRemoverBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevenir comportamento padrão
            console.log("Botão de remover serviço clicado");
            removerServico();
        });
    } else {
        console.error("Botão de remover serviço não encontrado");
    }
    
    if (adicionarBtn) {
        // Remover todos os event listeners existentes
        const novoAdicionarBtn = adicionarBtn.cloneNode(true);
        adicionarBtn.parentNode.replaceChild(novoAdicionarBtn, adicionarBtn);
        
        // Adicionar novo event listener
        console.log("Adicionando evento de clique ao botão de adicionar serviço");
        novoAdicionarBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevenir comportamento padrão
            console.log("Botão de adicionar serviço clicado");
            adicionarServico();
        });
    } else {
        console.error("Botão de adicionar serviço não encontrado");
    }
}

// Inicializar eventos quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado, inicializando...");
    
    // Formatar valores iniciais
    try {
        document.getElementById('precoUnitario-1').textContent = formatarMoeda(0);
        document.getElementById('precoTotal-1').textContent = formatarMoeda(0);
        document.getElementById('totalOrcamento').textContent = formatarMoeda(0);
    } catch (e) {
        console.error("Erro ao formatar valores iniciais:", e);
    }
    
    // Inicializar eventos dos botões
    inicializarEventos();

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

    // Adicionar event listener para o select de variáveis do primeiro serviço
    adicionarEventListenerVariavel(1);

    // Verificar todos os serviços existentes e mostrar campos de variáveis se necessário
    const servicoSelects = document.querySelectorAll('[id^="servico-"][id$="-nome"]');
    servicoSelects.forEach(select => {
        const id = select.id.match(/servico-(\d+)-nome/)[1];
        const servicoSelecionado = select.value;
        
        if (servicoSelecionado && !servicoSelecionado.includes("PGR")) {
            console.log(`Serviço ${id} já selecionado: ${servicoSelecionado}`);
            const variavelContainer = document.getElementById(`variavel-${id}`).parentElement;
            variavelContainer.style.display = "block";
            atualizarVariaveisDisponiveis(id, servicoSelecionado);
        }
    });
});

// Adicionar um event listener para o select de variáveis
function adicionarEventListenerVariavel(id) {
    const variavelSelect = document.getElementById(`variavel-${id}`);
    const avaliacoesAdicionaisContainer = document.getElementById(`avaliacoes-adicionais-container-${id}`);
    
    variavelSelect.addEventListener('change', function() {
        // Se a variável for "Por Avaliação Adicional", mostrar o campo de avaliações adicionais
        if (this.value === "Por Avaliação Adicional") {
            avaliacoesAdicionaisContainer.style.display = "block";
        } else {
            avaliacoesAdicionaisContainer.style.display = "none";
        }
        
        atualizarPreco(id);
    });
}

// Função para calcular o preço com base no número de avaliações adicionais
function atualizarPrecoAvaliacoesAdicionais(id) {
    // Apenas chama a função atualizarPreco que já deve lidar com isso
    atualizarPreco(id);
}

// Função para gerenciar a seleção de avaliação adicional
function toggleQuantidadeAvaliacoes(id) {
    const avaliacaoAdicionalSelect = document.getElementById(`avaliacao-adicional-${id}`);
    const quantidadeAvaliacoesContainer = document.getElementById(`quantidade-avaliacoes-container-${id}`);
    
    if (avaliacaoAdicionalSelect.value === "sim") {
        quantidadeAvaliacoesContainer.style.display = "block";
    } else {
        quantidadeAvaliacoesContainer.style.display = "none";
    }
    
    atualizarPreco(id);
}