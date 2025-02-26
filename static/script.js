// Variável para controlar o contador de serviços
let servicoCounter = 1;

// Adicionar serviço dinamicamente
function adicionarOutroServico() {
    servicoCounter++;
    const div = document.createElement('div');
    div.className = 'servico';
    div.innerHTML = `
        <div class="row">
            <div class="column">
                <label for="servico_${servicoCounter}">Serviço (1):</label><br>
                <select name="nome" id="servico_${servicoCounter}" required>
                    <option value="">Selecione um serviço</option>
                    ${getServicoOptions()}
                </select>
            </div>
            <div class="column">
                <label for="detalhes_${servicoCounter}">Detalhes:</label><br>
                <input type="text" name="detalhes" id="detalhes_${servicoCounter}" required placeholder="Ex.: 8 horas diárias, 200 empregados">
            </div>
        </div>
        <div class="row">
            <div class="column">
                <label for="quantidade_${servicoCounter}">Quantidade (2):</label><br>
                <select name="quantidade" id="quantidade_${servicoCounter}" required>
                    <option value="">Selecione a quantidade</option>
                    ${getQuantidadeOptions()}
                </select>
            </div>
            <div class="column">
                <label for="unidade_${servicoCounter}">Unidade:</label><br>
                <select name="unidade" id="unidade_${servicoCounter}" required>
                    <option value="">Selecione a unidade</option>
                    <option value="contrato">Contrato</option>
                    <option value="unidade">Unidade</option>
                    <option value="horas">Horas</option>
                    <option value="dias">Dias</option>
                </select>
            </div>
            <div class="column">
                <label for="regiao_${servicoCounter}">Região:</label><br>
                <select name="regiao" id="regiao_${servicoCounter}">
                    <option value="Central">Central</option>
                    <option value="Norte">Norte</option>
                    <option value="Sul">Sul</option>
                    <option value="Oeste">Oeste</option>
                    <option value="Sudoeste">Sudoeste</option>
                    <option value="Extremo Sul">Extremo Sul</option>
                </select>
            </div>
        </div>
        <div class="row">
            <div class="column">
                <label for="nome_empresa_${servicoCounter}">Nome da Empresa:</label><br>
                <input type="text" name="nome_empresa" id="nome_empresa_${servicoCounter}" placeholder="Digite o nome da sua empresa" required>
            </div>
        </div>
        <button type="button" onclick="removerServico(this)">Remover</button><br><br>
    `;
    div.style.opacity = '0'; // Animação de fade
    document.getElementById('servicos').appendChild(div);
    setTimeout(() => div.style.opacity = '1', 100); // Efeito fade-in
    
    // Adiciona o evento de change ao novo select de serviço
    adicionarEventoServicoChange(div.querySelector(`select[id="servico_${servicoCounter}"]`));
}

// Remover serviço dinamicamente
function removerServico(botao) {
    botao.parentElement.remove();
}

// Função para adicionar evento de change aos selects de serviço
function adicionarEventoServicoChange(select) {
    select.addEventListener('change', function() {
        const servicoContainer = this.closest('.servico');
        const detalhesInput = servicoContainer.querySelector('input[name="detalhes"]');
        const servicoSelecionado = this.value;
        
        if (servicoSelecionado.includes('PGR')) {
            detalhesInput.placeholder = "Ex.: 200 empregados, 12 meses";
        } else if (servicoSelecionado.includes('Higiene Ocupacional')) {
            detalhesInput.placeholder = "Ex.: 8 horas diárias, 50 empregados";
        } else if (servicoSelecionado.includes('Laudo')) {
            detalhesInput.placeholder = "Ex.: Avaliação de insalubridade para 10 funções";
        } else if (servicoSelecionado.includes('Coleta')) {
            detalhesInput.placeholder = "Ex.: Coleta de amostras para 5 pontos";
        } else {
            detalhesInput.placeholder = "Ex.: 8 horas diárias, 200 empregados";
        }
    });
}

// Função auxiliar para obter as opções de serviço do primeiro select
function getServicoOptions() {
    const opcoesOriginais = document.getElementById('servico_1').innerHTML;
    return opcoesOriginais;
}

// Função auxiliar para obter as opções de quantidade do primeiro select
function getQuantidadeOptions() {
    const opcoesOriginais = document.getElementById('quantidade_1').innerHTML;
    return opcoesOriginais;
}

// Carrega os eventos quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Adiciona eventos aos selects de serviço existentes na página
    document.querySelectorAll('select[name="nome"]').forEach(select => {
        adicionarEventoServicoChange(select);
    });
});

// Tabela de preços para PGR
const tabelaPrecosPGR = {
    "1 e 2": {
        "ate19": {
            "Central": 700.00,
            "Norte": 600.00,
            "Oeste": 1180.00,
            "Sudoeste": 550.00,
            "Sul": 640.00,
            "Extremo Sul": 631.00
        },
        "20a50": {
            "Central": 850.00,
            "Norte": 675.00,
            "Oeste": 1450.00,
            "Sudoeste": 700.00,
            "Sul": 775.00,
            "Extremo Sul": 671.00
        },
        "51a100": {
            "Central": 1100.00,
            "Norte": 750.00,
            "Oeste": 1900.00,
            "Sudoeste": 960.00,
            "Sul": 1000.00,
            "Extremo Sul": 719.00
        },
        "101a160": {
            "Central": 1900.00,
            "Norte": 900.00,
            "Oeste": 3205.00,
            "Sudoeste": 1330.00,
            "Sul": 1307.50,
            "Extremo Sul": 1066.00
        },
        "161a250": {
            "Central": 2100.00,
            "Norte": 974.00,
            "Oeste": 3430.00,
            "Sudoeste": 1440.00,
            "Sul": 1395.00,
            "Extremo Sul": 1151.00
        },
        "251a300": {
            "Central": 2300.00,
            "Norte": 1050.00,
            "Oeste": 3655.00,
            "Sudoeste": 1490.00,
            "Sul": 1482.50,
            "Extremo Sul": 1194.00
        }
    },
    "3 e 4": {
        "301a350": {
            "Central": 2500.00,
            "Norte": 1050.00,
            "Oeste": 3880.00,
            "Sudoeste": 1490.00,
            "Sul": 1570.00,
            "Extremo Sul": 1322.00
        },
        "351a400": {
            "Central": 2550.00,
            "Norte": 1124.00,
            "Oeste": 4105.00,
            "Sudoeste": 1650.00,
            "Sul": 1657.50,
            "Extremo Sul": 1322.00
        },
        "401a450": {
            "Central": 2550.00,
            "Norte": 1124.00,
            "Oeste": 4510.00,
            "Sudoeste": 1650.00,
            "Sul": 1815.00,
            "Extremo Sul": 1487.00
        },
        "451a500": {
            "Central": 2675.00,
            "Norte": 1310.00,
            "Oeste": 4735.00,
            "Sudoeste": 1780.00,
            "Sul": 1902.50,
            "Extremo Sul": 1602.00
        },
        "501a550": {
            "Central": 3000.00,
            "Norte": 1310.00,
            "Oeste": 5500.00,
            "Sudoeste": 1780.00,
            "Sul": 2200.00,
            "Extremo Sul": 1602.00
        },
        "551a600": {
            "Central": 3225.00,
            "Norte": 1386.00,
            "Oeste": 5725.00,
            "Sudoeste": 1990.00,
            "Sul": 2287.50,
            "Extremo Sul": 1794.00
        },
        "601a650": {
            "Central": 3350.00,
            "Norte": 1386.00,
            "Oeste": 5950.00,
            "Sudoeste": 2200.00,
            "Sul": 2375.00,
            "Extremo Sul": 1960.00
        },
        "651a700": {
            "Central": 3425.00,
            "Norte": 1460.00,
            "Oeste": 6085.00,
            "Sudoeste": 2420.00,
            "Sul": 2427.50,
            "Extremo Sul": 2130.00
        },
        "701a750": {
            "Central": 3500.00,
            "Norte": 1500.00,
            "Oeste": 6220.00,
            "Sudoeste": 2650.00,
            "Sul": 2530.00,
            "Extremo Sul": 2370.00
        },
        "751a800": {
            "Central": 3575.00,
            "Norte": 1575.00,
            "Oeste": 6355.00,
            "Sudoeste": 2840.00,
            "Sul": 2532.50,
            "Extremo Sul": 2562.00
        }
    }
};

// Tabela de preços para outros serviços
const tabelaOutrosServicos = {
    "Coleta para Avaliação Ambiental": {
        "Central": 300.00,
        "Norte": 300.00,
        "Oeste": 300.00,
        "Sudoeste": 300.00,
        "Sul": 300.00,
        "Extremo Sul": 300.00
    },
    "Ruído Limítrofe (NBR 10151)": {
        "Central": 200.00,
        "Norte": 200.00,
        "Oeste": 200.00,
        "Sudoeste": 200.00,
        "Sul": 200.00,
        "Extremo Sul": 200.00
    },
    "Relatório Técnico por Agente Ambiental": {
        "Central": 800.00,
        "Norte": 800.00,
        "Oeste": 600.00,
        "Sudoeste": 600.00,
        "Sul": 600.00,
        "Extremo Sul": 600.00
    },
    "Revisão de Relatório Técnico (após 90 dias)": {
        "Central": 160.00,
        "Norte": 120.00,
        "Oeste": 120.00,
        "Sudoeste": 120.00,
        "Sul": 120.00,
        "Extremo Sul": 120.00
    },
    "Laudo de Insalubridade": {
        "Central": 800.00,
        "Norte": 500.00,
        "Oeste": 500.00,
        "Sudoeste": 500.00,
        "Sul": 500.00,
        "Extremo Sul": 500.00
    },
    "Revisão de Laudo de Insalubridade (após 90 dias)": {
        "Central": 160.00,
        "Norte": 100.00,
        "Oeste": 100.00,
        "Sudoeste": 100.00,
        "Sul": 100.00,
        "Extremo Sul": 100.00
    },
    "LTCAT - Condições Ambientais de Trabalho": {
        "Central": 800.00,
        "Norte": 500.00,
        "Oeste": 500.00,
        "Sudoeste": 500.00,
        "Sul": 500.00,
        "Extremo Sul": 500.00
    },
    "Revisão de LTCAT (após 90 dias)": {
        "Central": 160.00,
        "Norte": 100.00,
        "Oeste": 100.00,
        "Sudoeste": 100.00,
        "Sul": 100.00,
        "Extremo Sul": 100.00
    },
    "Laudo de Periculosidade": {
        "Central": 1000.00,
        "Norte": 900.00,
        "Oeste": 800.00,
        "Sudoeste": 700.00,
        "Sul": 700.00,
        "Extremo Sul": 700.00
    },
    "Revisão de Laudo de Periculosidade (após 90 dias)": {
        "Central": 200.00,
        "Norte": 180.00,
        "Oeste": 160.00,
        "Sudoeste": 140.00,
        "Sul": 140.00,
        "Extremo Sul": 140.00
    }
};

// Contador de serviços
let contadorServicos = 1;

// Função para mostrar campos adicionais quando PGR for selecionado
function mostrarCamposAdicionais(id) {
    const servico = document.getElementById(`servico-${id}-nome`).value;
    const parametrosPGR = document.getElementById(`parametros-pgr-${id}`);
    
    if (servico === 'Elaboração e acompanhamento do PGR') {
        parametrosPGR.style.display = 'block';
        atualizarPreco(id); // Atualiza o preço com base nos valores padrão
    } else {
        parametrosPGR.style.display = 'none';
        // Para outros serviços, usamos o preço fixo
        let precoUnitario = 0;
        
        // Preços fixos para outros serviços
        if (servico === 'Coleta para Avaliação Ambiental') {
            precoUnitario = 300.00;
        } else if (servico === 'Laudo de Insalubridade') {
            precoUnitario = 800.00;
        } else if (servico === 'Revisão de Laudo de Insalubridade (após 90 dias)') {
            precoUnitario = 400.00;
        } else if (servico === 'LTCAT - Condições Ambientais de Trabalho') {
            precoUnitario = 1200.00;
        } else if (servico === 'Revisão de LTCAT (após 90 dias)') {
            precoUnitario = 600.00;
        } else if (servico === 'Laudo de Periculosidade') {
            precoUnitario = 1000.00;
        } else if (servico === 'Revisão de Laudo de Periculosidade (após 90 dias)') {
            precoUnitario = 500.00;
        }
        
        // Atualizar o display de preço
        document.getElementById(`precoUnitario-${id}`).textContent = `R$ ${precoUnitario.toFixed(2)}`;
        document.getElementById(`precoUnitarioHidden-${id}`).value = precoUnitario;
        
        // Atualizar o preço total
        atualizarPrecoTotal(id);
    }
}

// Função para atualizar o preço unitário com base nas seleções para o PGR
function atualizarPreco(id) {
    const servico = document.getElementById(`servico-${id}-nome`).value;
    
    if (servico === 'Elaboração e acompanhamento do PGR') {
        const grauRisco = document.querySelector(`input[name="servicos[${id-1}][grau_risco]"]:checked`).value;
        const numTrabalhadores = document.getElementById(`numTrabalhadores-${id}`).value;
        const regiao = document.getElementById(`regiao-${id}`).value;
        
        // Verificar se todos os campos foram preenchidos
        if (numTrabalhadores && regiao) {
            // Buscar o preço na tabela
            try {
                const preco = tabelaPrecosPGR[grauRisco][numTrabalhadores][regiao];
                
                // Atualizar o display de preço
                document.getElementById(`precoUnitario-${id}`).textContent = `R$ ${preco.toFixed(2)}`;
                document.getElementById(`precoUnitarioHidden-${id}`).value = preco;
                
                // Atualizar o preço total
                atualizarPrecoTotal(id);
            } catch (error) {
                console.error("Erro ao buscar preço:", error);
                // Em caso de erro, definir preço como 0
                document.getElementById(`precoUnitario-${id}`).textContent = "R$ 0,00";
                document.getElementById(`precoUnitarioHidden-${id}`).value = 0;
            }
        }
    }
}

// Função para atualizar o preço total com base na quantidade
function atualizarPrecoTotal(id) {
    const precoUnitarioText = document.getElementById(`precoUnitario-${id}`).textContent;
    const precoUnitario = parseFloat(precoUnitarioText.replace('R$ ', '').replace(',', '.'));
    const quantidade = parseInt(document.getElementById(`quantidade-${id}`).value);
    
    const precoTotal = precoUnitario * quantidade;
    document.getElementById(`precoTotal-${id}`).textContent = `R$ ${precoTotal.toFixed(2)}`;
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
        const preco = parseFloat(precoText.replace('R$ ', '').replace(',', '.'));
        total += preco;
    });
    
    document.getElementById('totalOrcamento').textContent = `R$ ${total.toFixed(2)}`;
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
                <select class="form-select servico-select" id="servico-${contadorServicos}-nome" name="servicos[${contadorServicos-1}][nome]" required onchange="mostrarCamposAdicionais(${contadorServicos})">
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
                <label for="regiao-${contadorServicos}" class="form-label">Região:</label>
                <select class="form-select regiao-select" id="regiao-${contadorServicos}" name="servicos[${contadorServicos-1}][regiao]" required onchange="atualizarPreco(${contadorServicos})">
                    <option value="">Selecione a região</option>
                    <option value="Central">Central</option>
                    <option value="Norte">Norte</option>
                    <option value="Oeste">Oeste</option>
                    <option value="Sudoeste">Sudoeste</option>
                    <option value="Sul">Sul</option>
                    <option value="Extremo Sul">Extremo Sul</option>
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
});