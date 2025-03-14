// Variável para controlar o contador de serviços
let contadorServicos = 1;

// Variável para controlar atualizações simultâneas de preço
let atualizandoPreco = {};

// Função para mostrar campos adicionais quando PGR for selecionado
function mostrarCamposAdicionais(id) {
    console.log(`Mostrando campos adicionais para o serviço ${id}`);
    
    const servicoSelect = document.getElementById(`servico-${id}-nome`);
    const servicoSelecionado = servicoSelect ? servicoSelect.value : '';
    
    // Elementos que podem ser exibidos ou ocultados
    const parametrosPgr = document.getElementById(`parametros-pgr-${id}`);
    const grauRiscoContainer = document.getElementById(`grau-risco-container-${id}`);
    const numTrabalhadoresContainer = document.getElementById(`num-trabalhadores-container-${id}`);
    const gesGheContainer = document.getElementById(`ges-container-${id}`);
    const avaliacaoAdicionalContainer = document.getElementById(`avaliacao-adicional-container-${id}`);
    const multiplasColetasContainer = document.getElementById(`multiplas-coletas-container-${id}`);
    const custosLaboratoriaisContainer = document.getElementById(`custos-laboratoriais-container-${id}`);
    const variavelContainer = document.getElementById(`variavel-container-${id}`);
    
    // Ocultar todos os campos específicos inicialmente
    if (parametrosPgr) parametrosPgr.style.display = 'none';
    if (grauRiscoContainer) grauRiscoContainer.style.display = 'none';
    if (numTrabalhadoresContainer) numTrabalhadoresContainer.style.display = 'none';
    if (gesGheContainer) gesGheContainer.style.display = 'none';
    if (avaliacaoAdicionalContainer) avaliacaoAdicionalContainer.style.display = 'none';
    if (multiplasColetasContainer) multiplasColetasContainer.style.display = 'none';
    if (custosLaboratoriaisContainer) custosLaboratoriaisContainer.style.display = 'none';
    
    // Se não houver serviço selecionado, não mostrar nenhum campo adicional
    if (!servicoSelecionado) {
        if (variavelContainer) variavelContainer.style.display = 'none';
        return;
    }
    
    // Verificar qual serviço foi selecionado e mostrar os campos apropriados
    if (servicoSelecionado.includes('PGR')) {
        console.log("Serviço PGR selecionado, mostrando campos específicos");
        if (parametrosPgr) parametrosPgr.style.display = 'block';
        if (grauRiscoContainer) grauRiscoContainer.style.display = 'block';
        if (numTrabalhadoresContainer) numTrabalhadoresContainer.style.display = 'block';
        // Para serviços PGR, esconder o campo de variável
        if (variavelContainer) variavelContainer.style.display = 'none';
    } else {
        // Para todos os serviços não-PGR, mostrar o campo de variável
        console.log("Serviço não-PGR selecionado, mostrando campo de variável");
        if (variavelContainer) {
            variavelContainer.style.display = 'block';
            console.log("Campo de variável exibido");
        } else {
            console.error("Campo de variável não encontrado");
        }
    }
    
    if (servicoSelecionado.includes('Coleta para Avaliação Ambiental')) {
        if (gesGheContainer) gesGheContainer.style.display = 'block';
        if (avaliacaoAdicionalContainer) avaliacaoAdicionalContainer.style.display = 'block';
        if (multiplasColetasContainer) multiplasColetasContainer.style.display = 'block';
        if (custosLaboratoriaisContainer) custosLaboratoriaisContainer.style.display = 'block';
    }
    
    if (servicoSelecionado.includes('LTCAT') || servicoSelecionado.includes('Laudo de Insalubridade')) {
        if (gesGheContainer) gesGheContainer.style.display = 'block';
        if (avaliacaoAdicionalContainer) avaliacaoAdicionalContainer.style.display = 'block';
    }
    
    // Verificar se o serviço selecionado requer avaliação adicional
    const variavelSelect = document.getElementById(`variavel-${id}`);
    const variavelSelecionada = variavelSelect ? variavelSelect.value : '';
    
    if (variavelSelecionada && (
        variavelSelecionada.includes('Ruído') || 
        variavelSelecionada.includes('Calor') || 
        variavelSelecionada.includes('Vibração') || 
        variavelSelecionada.includes('Químico')
    )) {
        if (avaliacaoAdicionalContainer) avaliacaoAdicionalContainer.style.display = 'block';
    }
    
    // Atualizar visibilidade dos campos de quantidade de avaliações
    toggleQuantidadeAvaliacoes(id);
    
    // Atualizar dias de coleta
    toggleDiasColeta(id);
}

// Função para obter opções de serviços
async function obterOpcoesServicos() {
    console.log('Obtendo opções de serviços...');
    try {
        const response = await fetch('/api/servicos', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        if (!response.ok) {
            throw new Error(`Erro ao obter serviços: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Serviços obtidos:', data);
        
        if (data.servicos && Array.isArray(data.servicos)) {
            return data.servicos;
        } else {
            console.error('Formato de resposta inválido:', data);
            return [];
        }
    } catch (error) {
        console.error('Erro ao obter serviços:', error);
        return [];
    }
}

// Função para remover um serviço específico
function removerServico(id) {
    console.log(`Removendo serviço ${id}`);
    
    // Confirmar com o usuário antes de remover
    if (confirm('Tem certeza que deseja remover este serviço?')) {
        // Remover o card do serviço
        const servicoCard = document.getElementById(`servico-card-${id}`);
        if (servicoCard) {
            servicoCard.remove();
            
            // Atualizar o total do orçamento
            atualizarTotalOrcamento();
            
            console.log(`Serviço ${id} removido com sucesso`);
        } else {
            console.error(`Serviço ${id} não encontrado`);
        }
    }
}

// Função para inicializar os eventos apenas uma vez
function inicializarEventos() {
    // Adicionar evento para o botão de adicionar serviço
    const btnAdicionarServico = document.getElementById('adicionarServico');
    if (btnAdicionarServico) {
        btnAdicionarServico.addEventListener('click', adicionarServico);
    }
    
    // Adicionar eventos para o primeiro serviço
    adicionarEventosAoNovoServico(1);
    
    // Carregar opções de serviços para o primeiro serviço
    obterOpcoesServicos().then(servicos => {
        const servicoSelect = document.getElementById('servico-1-nome');
        if (servicoSelect && servicos.length > 0) {
            // Limpar opções existentes
            servicoSelect.innerHTML = '<option value="">Selecione um serviço</option>';
            
            // Adicionar novas opções
            servicos.forEach(servico => {
                const option = document.createElement('option');
                option.value = servico;
                option.textContent = servico;
                servicoSelect.appendChild(option);
            });
        }
    });
    
    // Inicializar o total do orçamento
    atualizarTotalOrcamento();
    
    // Prevenir envio do formulário ao pressionar ENTER
    document.addEventListener('keydown', function(event) {
        // Verificar se a tecla pressionada é ENTER
        if (event.key === 'Enter') {
            // Verificar se o elemento ativo não é um textarea
            if (document.activeElement.tagName !== 'TEXTAREA') {
                // Prevenir o comportamento padrão (envio do formulário)
                event.preventDefault();
                
                // Log para depuração
                console.log('Tecla ENTER pressionada em:', document.activeElement.tagName, document.activeElement.id);
                
                // Se estiver em um campo de entrada, mover para o próximo campo
                if (document.activeElement.tagName === 'INPUT' || 
                    document.activeElement.tagName === 'SELECT') {
                    
                    // Encontrar o próximo elemento focável
                    const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
                    const focusable = Array.prototype.filter.call(
                        document.querySelectorAll(focusableElements),
                        function (element) {
                            return element.offsetWidth > 0 || element.offsetHeight > 0 || element === document.activeElement;
                        }
                    );
                    
                    const index = focusable.indexOf(document.activeElement);
                    if (index > -1 && index < focusable.length - 1) {
                        focusable[index + 1].focus();
                    }
                }
            }
        }
    });
}

// Adicionar evento para inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', inicializarEventos);

// Adicionar um event listener para o select de variáveis
function adicionarEventosAoNovoServico(id) {
    console.log(`Adicionando eventos ao serviço ${id}`);
    
    // Adicionar evento para atualizar preço quando o serviço for selecionado
    const servicoSelect = document.getElementById(`servico-${id}-nome`);
    if (servicoSelect) {
        servicoSelect.addEventListener('change', function() {
            mostrarCamposAdicionais(id);
            carregarRegioes(id);
            atualizarPreco(id);
        });
    }
    
    // Adicionar evento para atualizar preço quando a região for selecionada
    const regiaoSelect = document.getElementById(`regiao-${id}`);
    if (regiaoSelect) {
        regiaoSelect.addEventListener('change', function() {
            carregarVariaveis(id);
            atualizarPreco(id);
        });
    }
    
    // Adicionar evento para atualizar preço quando a variável for selecionada
    const variavelSelect = document.getElementById(`variavel-${id}`);
    if (variavelSelect) {
        variavelSelect.addEventListener('change', function() {
            mostrarCamposAdicionais(id);
            atualizarPreco(id);
        });
    }
    
    // Adicionar evento para toggle de avaliações adicionais
    const avaliacaoAdicionalSelect = document.getElementById(`avaliacao-adicional-${id}`);
    if (avaliacaoAdicionalSelect) {
        avaliacaoAdicionalSelect.addEventListener('change', function() {
            toggleQuantidadeAvaliacoes(id);
            atualizarPreco(id);
        });
    }
    
    // Adicionar evento para toggle de dias de coleta
    const multiplasColetasSelect = document.getElementById(`multiplas-coletas-${id}`);
    if (multiplasColetasSelect) {
        multiplasColetasSelect.addEventListener('change', function() {
            toggleDiasColeta(id);
            atualizarPreco(id);
        });
    }
    
    // Adicionar evento para atualizar preço quando a quantidade mudar
    const quantidadeInput = document.getElementById(`quantidade-${id}`);
    if (quantidadeInput) {
        quantidadeInput.addEventListener('change', function() {
            atualizarPrecoTotal(id);
        });
        quantidadeInput.addEventListener('keyup', function() {
            atualizarPrecoTotal(id);
        });
    }
    
    // Adicionar evento para atualizar preço quando os custos logísticos mudarem
    const custosLogisticosInput = document.getElementById(`custos-logisticos-${id}`);
    if (custosLogisticosInput) {
        custosLogisticosInput.addEventListener('change', function() {
            validarCustosLogisticos(this);
            atualizarPrecoTotal(id);
        });
        custosLogisticosInput.addEventListener('keyup', function() {
            validarCustosLogisticos(this);
            atualizarPrecoTotal(id);
        });
    }
    
    // Adicionar evento para atualizar preço quando o número de GES/GHE mudar
    const numGesGheInput = document.getElementById(`ges-${id}`);
    if (numGesGheInput) {
        numGesGheInput.addEventListener('change', function() {
            atualizarPreco(id);
        });
        numGesGheInput.addEventListener('keyup', function() {
            atualizarPreco(id);
        });
    }
    
    // Adicionar eventos para os campos de custos laboratoriais
    const tipoAmostradorSelect = document.getElementById(`tipo-amostrador-${id}`);
    const quantidadeAmostrasInput = document.getElementById(`quantidade-amostras-${id}`);
    const tipoAnaliseSelect = document.getElementById(`tipo-analise-${id}`);
    const necessitaArtCheckbox = document.getElementById(`necessita-art-${id}`);
    const metodoEnvioSelect = document.getElementById(`metodo-envio-${id}`);
    
    if (tipoAmostradorSelect) {
        tipoAmostradorSelect.addEventListener('change', function() {
            calcularCustosLaboratoriais(id);
        });
    }
    
    if (quantidadeAmostrasInput) {
        quantidadeAmostrasInput.addEventListener('change', function() {
            calcularCustosLaboratoriais(id);
        });
        quantidadeAmostrasInput.addEventListener('keyup', function() {
            calcularCustosLaboratoriais(id);
        });
    }
    
    if (tipoAnaliseSelect) {
        tipoAnaliseSelect.addEventListener('change', function() {
            calcularCustosLaboratoriais(id);
        });
    }
    
    if (necessitaArtCheckbox) {
        necessitaArtCheckbox.addEventListener('change', function() {
            calcularCustosLaboratoriais(id);
        });
    }
    
    if (metodoEnvioSelect) {
        metodoEnvioSelect.addEventListener('change', function() {
            calcularCustosLaboratoriais(id);
        });
    }
    
    console.log(`Eventos adicionados ao serviço ${id}`);
}

// Função para calcular o preço com base no número de avaliações adicionais
function atualizarPrecoAvaliacoesAdicionais(id) {
    // Apenas chama a função atualizarPreco que já deve lidar com isso
    atualizarPreco(id);
}

// Função para mostrar/ocultar o campo de quantidade de avaliações
function toggleQuantidadeAvaliacoes(id) {
    const avaliacaoAdicionalSelect = document.getElementById(`avaliacao-adicional-${id}`);
    const quantidadeAvaliacoesContainer = document.getElementById(`quantidade-avaliacoes-container-${id}`);
    
    if (avaliacaoAdicionalSelect && quantidadeAvaliacoesContainer) {
        if (avaliacaoAdicionalSelect.value === 'sim') {
            console.log(`Mostrando campo de quantidade de avaliações adicionais para serviço ${id}`);
            quantidadeAvaliacoesContainer.style.display = 'block';
            
            // Garantir que o campo tenha um valor válido
            const quantidadeAvaliacoes = document.getElementById(`quantidade-avaliacoes-${id}`);
            if (quantidadeAvaliacoes && (!quantidadeAvaliacoes.value || parseInt(quantidadeAvaliacoes.value) < 1)) {
                quantidadeAvaliacoes.value = 1;
            }
        } else {
            console.log(`Ocultando campo de quantidade de avaliações adicionais para serviço ${id}`);
            quantidadeAvaliacoesContainer.style.display = 'none';
            
            // Resetar o valor para 1 quando ocultar
            const quantidadeAvaliacoes = document.getElementById(`quantidade-avaliacoes-${id}`);
            if (quantidadeAvaliacoes) {
                quantidadeAvaliacoes.value = 1;
            }
        }
        
        // Atualizar o preço após a alteração
        atualizarPreco(id);
    }
}

function atualizarDiasColeta(servicoId) {
    const quantidadeDiasInput = document.getElementById(`quantidade-dias-${servicoId}`);
    const detalhesDiasColetaContainer = document.getElementById(`detalhes-dias-coleta-${servicoId}`);
    
    if (!quantidadeDiasInput || !detalhesDiasColetaContainer) {
        console.error(`Elementos para dias de coleta do serviço ${servicoId} não encontrados`);
        return;
    }
    
    const quantidadeDias = parseInt(quantidadeDiasInput.value) || 1;
    
    // Limpar o container de detalhes
    detalhesDiasColetaContainer.innerHTML = '';
    
    // Adicionar campos para cada dia de coleta
    for (let i = 1; i <= quantidadeDias; i++) {
        const diaColetaDiv = document.createElement('div');
        diaColetaDiv.className = 'card mb-3 p-3 bg-dark';
        diaColetaDiv.innerHTML = `
            <h5 class="text-white">Dia de Coleta ${i}</h5>
            <div class="mb-3">
                <label for="data-coleta-${servicoId}-${i}" class="form-label text-white">Data:</label>
                <input type="date" class="form-control" id="data-coleta-${servicoId}-${i}" name="servicos[${servicoId-1}][dias_coleta][${i-1}][data]" required>
            </div>
            <div class="mb-3">
                <label for="hora-coleta-${servicoId}-${i}" class="form-label text-white">Hora:</label>
                <input type="time" class="form-control" id="hora-coleta-${servicoId}-${i}" name="servicos[${servicoId-1}][dias_coleta][${i-1}][hora]" required>
            </div>
            <div class="mb-3">
                <label for="local-coleta-${servicoId}-${i}" class="form-label text-white">Local:</label>
                <input type="text" class="form-control" id="local-coleta-${servicoId}-${i}" name="servicos[${servicoId-1}][dias_coleta][${i-1}][local]" placeholder="Informe o local da coleta" required>
            </div>
            <div class="mb-3">
                <label for="observacoes-coleta-${servicoId}-${i}" class="form-label text-white">Observações:</label>
                <textarea class="form-control" id="observacoes-coleta-${servicoId}-${i}" name="servicos[${servicoId-1}][dias_coleta][${i-1}][observacoes]" rows="2" placeholder="Observações adicionais sobre esta coleta"></textarea>
            </div>
        `;
        
        detalhesDiasColetaContainer.appendChild(diaColetaDiv);
    }
    
    // Atualizar o preço após modificar os dias de coleta
    atualizarPreco(servicoId);
}

function toggleDiasColeta(servicoId) {
    const multiplasColetasSelect = document.getElementById(`multiplas-coletas-${servicoId}`);
    const diasColetaContainer = document.getElementById(`dias-coleta-container-${servicoId}`);
    
    if (!multiplasColetasSelect || !diasColetaContainer) {
        console.error(`Elementos para toggle de dias de coleta do serviço ${servicoId} não encontrados`);
        return;
    }
    
    if (multiplasColetasSelect.value === "sim") {
        diasColetaContainer.style.display = 'block';
        atualizarDiasColeta(servicoId);
    } else {
        diasColetaContainer.style.display = 'none';
    }
    
    // Atualizar o preço após modificar a visibilidade dos dias de coleta
    atualizarPreco(servicoId);
}

// Função para carregar regiões disponíveis com base no serviço selecionado
function carregarRegioes(id) {
    try {
        const servicoSelect = document.getElementById(`servico-${id}-nome`);
        const regiaoSelect = document.getElementById(`regiao-${id}`);
        
        if (!servicoSelect || !regiaoSelect) {
            console.error(`Elementos não encontrados para o serviço ${id}`);
            return;
        }
        
        const servico = servicoSelect.value;
        
        // Limpar o dropdown de regiões
        regiaoSelect.innerHTML = '<option value="">Selecione a região</option>';
        
        // Se não houver serviço selecionado, não fazer nada
        if (!servico) {
            return;
        }
        
        // Mostrar indicador de carregamento
        regiaoSelect.disabled = true;
        regiaoSelect.innerHTML = '<option value="">Carregando...</option>';
        
        console.log(`Carregando regiões para o serviço: ${servico}`);
        
        // Fazer requisição para obter regiões disponíveis
        fetch(`/api/regioes_disponiveis?servico=${encodeURIComponent(servico)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Resposta recebida para regiões: ${JSON.stringify(data)}`);
            
            // Limpar o dropdown
            regiaoSelect.innerHTML = '<option value="">Selecione a região</option>';
            
            // Adicionar as regiões disponíveis
            if (data.regioes && data.regioes.length > 0) {
                data.regioes.forEach(regiao => {
                    const option = document.createElement('option');
                    option.value = regiao;
                    option.textContent = regiao;
                    regiaoSelect.appendChild(option);
                });
                console.log(`Carregadas ${data.regioes.length} regiões para o serviço ${servico}`);
            } else {
                console.log(`Nenhuma região disponível para o serviço ${servico}`);
                
                // Adicionar opções padrão se não houver regiões disponíveis
                const regioesDefault = ["Instituto", "Central", "Norte", "Oeste", "Sudoeste", "Sul e Extremo Sul"];
                regioesDefault.forEach(regiao => {
                    const option = document.createElement('option');
                    option.value = regiao;
                    option.textContent = regiao;
                    regiaoSelect.appendChild(option);
                });
                console.log("Adicionadas regiões padrão");
            }
            
            // Habilitar o dropdown
            regiaoSelect.disabled = false;
            
            // Adicionar evento de change para atualizar o preço quando a região for alterada
            regiaoSelect.addEventListener('change', function() {
                if (servico.includes("PGR")) {
                    // Para serviços PGR, atualizar o preço diretamente
                    atualizarPreco(id);
                } else {
                    // Para outros serviços, carregar as variáveis primeiro
                    carregarVariaveis(id);
                    // A função carregarVariaveis já chama atualizarPreco
                }
            });
        })
        .catch(error => {
            console.error('Erro ao carregar regiões:', error);
            regiaoSelect.innerHTML = '<option value="">Erro ao carregar regiões</option>';
            regiaoSelect.disabled = false;
            
            // Adicionar opções padrão em caso de erro
            const regioesDefault = ["Instituto", "Central", "Norte", "Oeste", "Sudoeste", "Sul e Extremo Sul"];
            regioesDefault.forEach(regiao => {
                const option = document.createElement('option');
                option.value = regiao;
                option.textContent = regiao;
                regiaoSelect.appendChild(option);
            });
            console.log("Adicionadas regiões padrão após erro");
        });
    } catch (error) {
        console.error('Erro na função carregarRegioes:', error);
    }
}

// Função para carregar variáveis disponíveis com base no serviço e região selecionados
function carregarVariaveis(id) {
    try {
        const servicoSelect = document.getElementById(`servico-${id}-nome`);
        const regiaoSelect = document.getElementById(`regiao-${id}`);
        const variavelSelect = document.getElementById(`variavel-${id}`);
        const variavelContainer = document.getElementById(`variavel-container-${id}`);
        
        if (!servicoSelect || !regiaoSelect || !variavelSelect) {
            console.error(`Elementos não encontrados para o serviço ${id}`);
            return;
        }
        
        const servico = servicoSelect.value;
        const regiao = regiaoSelect.value;
        
        // Limpar o dropdown de variáveis
        variavelSelect.innerHTML = '<option value="">Selecione uma variável</option>';
        
        // Se não houver serviço ou região selecionados, não fazer nada
        if (!servico || !regiao) {
            if (variavelContainer) variavelContainer.style.display = 'none';
            return;
        }
        
        // Se for um serviço PGR, não precisa carregar variáveis
        if (servico.includes("PGR")) {
            if (variavelContainer) variavelContainer.style.display = 'none';
            return;
        } else {
            // Para serviços não-PGR, mostrar o campo de variável
            if (variavelContainer) {
                variavelContainer.style.display = 'block';
                console.log("Campo de variável exibido em carregarVariaveis");
            }
        }
        
        console.log(`Carregando variáveis para o serviço: ${servico}, região: ${regiao}`);
        
        // Mostrar indicador de carregamento
        variavelSelect.disabled = true;
        variavelSelect.innerHTML = '<option value="">Carregando...</option>';
        
        // Fazer requisição para obter variáveis disponíveis
        fetch(`/api/variaveis_disponiveis?servico=${encodeURIComponent(servico)}&regiao=${encodeURIComponent(regiao)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Resposta recebida para variáveis: ${JSON.stringify(data)}`);
            
            // Limpar o dropdown
            variavelSelect.innerHTML = '<option value="">Selecione uma variável</option>';
            
            // Adicionar as variáveis disponíveis
            if (data.variaveis && data.variaveis.length > 0) {
                data.variaveis.forEach(variavel => {
                    const option = document.createElement('option');
                    option.value = variavel;
                    option.textContent = variavel;
                    variavelSelect.appendChild(option);
                });
                console.log(`Carregadas ${data.variaveis.length} variáveis para o serviço ${servico} na região ${regiao}`);
            } else {
                console.log(`Nenhuma variável disponível para o serviço ${servico} na região ${regiao}`);
                
                // Adicionar opções padrão se não houver variáveis disponíveis
                const variaveisDefault = ["Pacote (1 a 4 avaliações)", "Por Avaliação Adicional", "Por Relatório Unitário"];
                variaveisDefault.forEach(variavel => {
                    const option = document.createElement('option');
                    option.value = variavel;
                    option.textContent = variavel;
                    variavelSelect.appendChild(option);
                });
                console.log("Adicionadas variáveis padrão");
            }
            
            // Habilitar o dropdown
            variavelSelect.disabled = false;
            
            // Atualizar o preço após carregar as variáveis
            setTimeout(() => {
                atualizarPreco(id);
            }, 100);
        })
        .catch(error => {
            console.error('Erro ao carregar variáveis:', error);
            variavelSelect.innerHTML = '<option value="">Erro ao carregar variáveis</option>';
            variavelSelect.disabled = false;
            
            // Adicionar opções padrão em caso de erro
            const variaveisDefault = ["Pacote (1 a 4 avaliações)", "Por Avaliação Adicional", "Por Relatório Unitário"];
            variaveisDefault.forEach(variavel => {
                const option = document.createElement('option');
                option.value = variavel;
                option.textContent = variavel;
                variavelSelect.appendChild(option);
            });
            console.log("Adicionadas variáveis padrão após erro");
        });
    } catch (error) {
        console.error('Erro na função carregarVariaveis:', error);
    }
}

// Adicionar evento para carregar variáveis quando a região for selecionada
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar evento para o primeiro serviço
    const regiaoSelect = document.getElementById('regiao-1');
    if (regiaoSelect) {
        regiaoSelect.addEventListener('change', function() {
            carregarVariaveis(1);
            atualizarPreco(1);
        });
    }
    
    // Adicionar evento para o primeiro serviço
    const servicoSelect = document.getElementById('servico-1-nome');
    if (servicoSelect) {
        servicoSelect.addEventListener('change', function() {
            mostrarCamposAdicionais(1);
        });
    }
});

// Adicionar tratamento de erros global
window.addEventListener('error', function(event) {
    console.error('Erro global capturado:', event.error);
});

// Adicionar tratamento de erros para promessas não tratadas
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promessa não tratada:', event.reason);
});

// Função para validar e calcular os custos laboratoriais
function calcularCustosLaboratoriais(id) {
    // Verificar se os elementos existem
    const tipoAmostradorSelect = document.getElementById(`tipo-amostrador-${id}`);
    const quantidadeAmostrasInput = document.getElementById(`quantidade-amostras-${id}`);
    const tipoAnaliseSelect = document.getElementById(`tipo-analise-${id}`);
    const necessitaArtCheckbox = document.getElementById(`necessita-art-${id}`);
    const metodoEnvioSelect = document.getElementById(`metodo-envio-${id}`);
    
    if (!tipoAmostradorSelect || !quantidadeAmostrasInput || !tipoAnaliseSelect || !necessitaArtCheckbox || !metodoEnvioSelect) {
        console.log("Elementos de custos laboratoriais não encontrados");
        return 0;
    }
    
    // Obter valores dos campos
    const tipoAmostrador = tipoAmostradorSelect.value;
    const quantidadeAmostras = parseInt(quantidadeAmostrasInput.value || 1);
    const tipoAnalise = tipoAnaliseSelect.value;
    const necessitaArt = necessitaArtCheckbox.checked;
    const metodoEnvio = metodoEnvioSelect.value;
    
    // Verificar se os campos obrigatórios estão preenchidos
    if (!tipoAmostrador || !tipoAnalise) {
        console.log("Campos obrigatórios de custos laboratoriais não preenchidos");
        return 0;
    }
    
    // Preços base por tipo de amostrador
    const precosAmostradores = {
        'bomba': 150.0,
        'dosimetro': 180.0,
        'cassete': 120.0,
        'impinger': 200.0,
        'outro': 100.0
    };
    
    // Preços base por tipo de análise
    const precosAnalises = {
        'quimica': 250.0,
        'biologica': 300.0,
        'fisica': 200.0
    };
    
    // Multiplicadores por método de envio
    const multiplicadoresEnvio = {
        'padrao': 1.0,
        'expresso': 1.5,
        'urgente': 2.0
    };
    
    // Custo da ART
    const custoArt = necessitaArt ? 88.78 : 0.0;
    
    // Calcular custo base do amostrador
    const custoAmostrador = precosAmostradores[tipoAmostrador] || 100.0;
    
    // Calcular custo da análise
    const custoAnalise = precosAnalises[tipoAnalise] || 200.0;
    
    // Aplicar multiplicador de envio
    const multiplicador = multiplicadoresEnvio[metodoEnvio] || 1.0;
    
    // Calcular custo total
    const custoTotal = ((custoAmostrador + custoAnalise) * quantidadeAmostras * multiplicador) + custoArt;
    
    // Atualizar o campo de custos laboratoriais (se existir)
    const custosLaboratoriaisInput = document.getElementById(`custos-laboratoriais-${id}`);
    if (custosLaboratoriaisInput) {
        custosLaboratoriaisInput.value = custoTotal.toFixed(2);
    }
    
    console.log(`Custos laboratoriais calculados para o serviço ${id}: R$ ${custoTotal.toFixed(2)}`);
    
    // Atualizar o preço total
    atualizarPrecoTotal(id);
    
    return custoTotal;
}

// Função para atualizar o preço unitário com base nos parâmetros selecionados
async function atualizarPreco(id) {
    try {
        console.log(`Atualizando preço para o serviço ${id}`);
        
        // Evitar múltiplas chamadas simultâneas para o mesmo serviço
        if (atualizandoPreco[id]) {
            console.log(`Atualização de preço para o serviço ${id} já em andamento, ignorando chamada`);
            return;
        }
        
        atualizandoPreco[id] = true;
        
        // Verificar se os elementos existem
        const servicoSelect = document.getElementById(`servico-${id}-nome`);
        const regiaoSelect = document.getElementById(`regiao-${id}`);
        const variavelSelect = document.getElementById(`variavel-${id}`);
        const variavelContainer = document.getElementById(`variavel-container-${id}`);
        const precoUnitarioElement = document.getElementById(`precoUnitario-${id}`);
        const precoUnitarioHiddenInput = document.getElementById(`precoUnitarioHidden-${id}`);
        
        if (!servicoSelect || !regiaoSelect || !precoUnitarioElement || !precoUnitarioHiddenInput) {
            console.error(`Elementos necessários não encontrados para o serviço ${id}`);
            console.error(`servicoSelect: ${servicoSelect ? 'encontrado' : 'não encontrado'}`);
            console.error(`regiaoSelect: ${regiaoSelect ? 'encontrado' : 'não encontrado'}`);
            console.error(`precoUnitarioElement: ${precoUnitarioElement ? 'encontrado' : 'não encontrado'}`);
            console.error(`precoUnitarioHiddenInput: ${precoUnitarioHiddenInput ? 'encontrado' : 'não encontrado'}`);
            atualizandoPreco[id] = false;
            return;
        }
        
        // Obter valores dos campos
        const servico = servicoSelect.value;
        const regiao = regiaoSelect.value;
        
        // Verificar se os campos obrigatórios estão preenchidos
        if (!servico || !regiao) {
            console.log(`Serviço ou região não selecionados para o serviço ${id}`);
            precoUnitarioElement.textContent = 'R$ 0,00';
            precoUnitarioHiddenInput.value = '0';
            atualizarPrecoTotal(id);
            atualizandoPreco[id] = false;
            return;
        }
        
        // Verificar se é um serviço PGR ou não
        const isPGR = servico.includes('PGR');
        
        // Parâmetros específicos para PGR
        let grauRisco = null;
        let numTrabalhadores = null;
        
        if (isPGR) {
            // Para serviços PGR, verificar grau de risco e número de trabalhadores
            const grauRiscoSelect = document.getElementById(`grau-risco-${id}`);
            const numTrabalhadoresSelect = document.getElementById(`numTrabalhadores-${id}`);
            
            if (grauRiscoSelect) {
                grauRisco = grauRiscoSelect.value;
            }
            
            if (numTrabalhadoresSelect) {
                numTrabalhadores = numTrabalhadoresSelect.value;
            }
            
            if (!grauRisco || !numTrabalhadores) {
                console.log(`Grau de risco ou número de trabalhadores não selecionados para o serviço PGR ${id}`);
                precoUnitarioElement.textContent = 'Selecione todos os campos';
                precoUnitarioHiddenInput.value = '0';
                atualizarPrecoTotal(id);
                atualizandoPreco[id] = false;
                return;
            }
            
            console.log(`Serviço PGR: ${servico}, Grau de Risco: ${grauRisco}, Número de Trabalhadores: ${numTrabalhadores}`);
        } else {
            // Para serviços não-PGR, verificar se a variável está selecionada
            if (variavelContainer && variavelContainer.style.display !== 'none' && 
                (!variavelSelect || !variavelSelect.value)) {
                console.log(`Variável não selecionada para o serviço não-PGR ${id}`);
                precoUnitarioElement.textContent = 'Selecione a variável';
                precoUnitarioHiddenInput.value = '0';
                atualizarPrecoTotal(id);
                atualizandoPreco[id] = false;
                return;
            }
        }
        
        // Obter número de GES/GHE
        let numGesGhe = 1;
        const gesContainer = document.getElementById(`ges-container-${id}`);
        const numGesGheInput = document.getElementById(`ges-${id}`);
        
        if (gesContainer && gesContainer.style.display !== 'none' && numGesGheInput) {
            numGesGhe = parseInt(numGesGheInput.value) || 1;
        }
        
        // Verificar se há avaliações adicionais
        let numAvaliacoesAdicionais = 0;
        const avaliacaoAdicionalSelect = document.getElementById(`avaliacao-adicional-${id}`);
        const quantidadeAvaliacoesInput = document.getElementById(`quantidade-avaliacoes-${id}`);
        
        if (avaliacaoAdicionalSelect && avaliacaoAdicionalSelect.value === 'sim' && quantidadeAvaliacoesInput) {
            numAvaliacoesAdicionais = parseInt(quantidadeAvaliacoesInput.value) || 0;
        }
        
        // Obter variável (se não for PGR)
        let variavel = null;
        if (!isPGR && variavelSelect) {
            variavel = variavelSelect.value;
        }
        
        // Mostrar indicador de carregamento
        precoUnitarioElement.textContent = 'Calculando...';
        
        // Construir URL para a requisição
        let url = `/calcular_preco?servico=${encodeURIComponent(servico)}&regiao=${encodeURIComponent(regiao)}`;
        
        if (isPGR) {
            // Para serviços PGR, sempre incluir grau de risco e número de trabalhadores
            if (grauRisco) {
                url += `&grau_risco=${encodeURIComponent(grauRisco)}`;
            }
            
            if (numTrabalhadores) {
                url += `&num_trabalhadores=${encodeURIComponent(numTrabalhadores)}`;
            }
        } else if (variavel) {
            // Para serviços não-PGR, incluir variável
            url += `&variavel=${encodeURIComponent(variavel)}`;
        }
        
        if (numGesGhe > 1) {
            url += `&num_ges_ghe=${numGesGhe}`;
        }
        
        if (numAvaliacoesAdicionais > 0) {
            url += `&num_avaliacoes_adicionais=${numAvaliacoesAdicionais}`;
        }
        
        console.log(`Fazendo requisição para: ${url}`);
        
        try {
            // Fazer requisição para obter o preço
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            console.log(`Status da resposta: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`Erro HTTP: ${response.status} - ${response.statusText}. Detalhes: ${errorText}`);
                throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            console.log(`Tipo de conteúdo da resposta: ${contentType}`);
            
            if (!contentType || !contentType.includes('application/json')) {
                console.error(`Resposta não é JSON: ${contentType}`);
                const text = await response.text();
                console.error(`Conteúdo da resposta: ${text}`);
                throw new Error('Resposta não é JSON');
            }
            
            const data = await response.json();
            console.log(`Resposta recebida: ${JSON.stringify(data)}`);
            
            if (data.success) {
                // Atualizar o preço unitário
                const preco = data.preco;
                const precoFormatado = data.preco_formatado || `R$ ${preco.toFixed(2).replace('.', ',')}`;
                
                precoUnitarioElement.textContent = precoFormatado;
                precoUnitarioHiddenInput.value = preco;
                
                // Atualizar o preço total
                atualizarPrecoTotal(id);
            } else {
                // Exibir mensagem de erro
                precoUnitarioElement.textContent = 'Erro ao calcular preço';
                precoUnitarioHiddenInput.value = '0';
                atualizarPrecoTotal(id);
                console.error(`Erro retornado pelo servidor: ${data.erro}`);
            }
        } catch (error) {
            console.error(`Erro ao obter preço: ${error.message}`);
            precoUnitarioElement.textContent = 'Erro ao calcular preço';
            precoUnitarioHiddenInput.value = '0';
            atualizarPrecoTotal(id);
        } finally {
            atualizandoPreco[id] = false;
        }
    } catch (error) {
        console.error(`Erro na função atualizarPreco: ${error.message}`);
        atualizandoPreco[id] = false;
    }
}

// Função para atualizar o preço total com base no preço unitário e quantidade
function atualizarPrecoTotal(id) {
    try {
        console.log(`Atualizando preço total para o serviço ${id}`);
        
        // Verificar se os elementos existem
        const precoUnitarioHiddenInput = document.getElementById(`precoUnitarioHidden-${id}`);
        const quantidadeInput = document.getElementById(`quantidade-${id}`);
        const precoTotalElement = document.getElementById(`precoTotal-${id}`);
        const precoTotalHiddenInput = document.getElementById(`precoTotalHidden-${id}`);
        const custosLogisticosInput = document.getElementById(`custos-logisticos-${id}`);
        const custosMultiplosDiasInput = document.getElementById(`custos-multiplos-dias-${id}`);
        const custosLaboratoriaisInput = document.getElementById(`custos-laboratoriais-${id}`);
        
        if (!precoUnitarioHiddenInput || !quantidadeInput || !precoTotalElement || !precoTotalHiddenInput) {
            console.error(`Elementos necessários não encontrados para o serviço ${id}`);
            return;
        }
        
        // Obter valores dos campos
        let precoUnitario = parseFloat(precoUnitarioHiddenInput.value) || 0;
        let quantidade = parseInt(quantidadeInput.value) || 1;
        
        // Obter custos logísticos
        let custosLogisticos = 0;
        if (custosLogisticosInput) {
            let valorCustosLogisticos = custosLogisticosInput.value.replace(',', '.');
            custosLogisticos = parseFloat(valorCustosLogisticos) || 0;
        }
        
        // Obter custos de múltiplos dias
        let custosMultiplosDias = 0;
        if (custosMultiplosDiasInput) {
            custosMultiplosDias = parseFloat(custosMultiplosDiasInput.value) || 0;
        }
        
        // Obter custos laboratoriais
        let custosLaboratoriais = 0;
        if (custosLaboratoriaisInput) {
            custosLaboratoriais = parseFloat(custosLaboratoriaisInput.value) || 0;
        }
        
        // Calcular preço total
        const precoTotal = (precoUnitario * quantidade) + custosLogisticos + custosMultiplosDias + custosLaboratoriais;
        
        console.log(`Preço unitário: ${precoUnitario}, Quantidade: ${quantidade}, Custos logísticos: ${custosLogisticos}, Custos múltiplos dias: ${custosMultiplosDias}, Custos laboratoriais: ${custosLaboratoriais}`);
        console.log(`Preço total calculado: ${precoTotal}`);
        
        // Atualizar o preço total
        precoTotalElement.textContent = `R$ ${precoTotal.toFixed(2).replace('.', ',')}`;
        precoTotalHiddenInput.value = precoTotal.toFixed(2);
        
        // Atualizar o total do orçamento
        atualizarTotalOrcamento();
    } catch (error) {
        console.error(`Erro ao atualizar preço total para o serviço ${id}:`, error);
    }
}

// Função para atualizar o total do orçamento
function atualizarTotalOrcamento() {
    try {
        console.log('Atualizando total do orçamento');
        
        // Verificar se os elementos existem
        const subtotalOrcamentoElement = document.getElementById('subtotalOrcamento');
        const valorSESIElement = document.getElementById('valorSESI');
        const totalOrcamentoElement = document.getElementById('totalOrcamento');
        const totalOrcamentoHiddenInput = document.getElementById('totalOrcamentoHidden');
        
        if (!subtotalOrcamentoElement || !valorSESIElement || !totalOrcamentoElement || !totalOrcamentoHiddenInput) {
            console.log('Elementos de total do orçamento não encontrados');
            return;
        }
        
        // Obter todos os preços totais
        const precosTotaisInputs = document.querySelectorAll('input[id^="precoTotalHidden-"]');
        let subtotalOrcamento = 0;
        
        // Somar todos os preços totais
        precosTotaisInputs.forEach(input => {
            const precoTotal = parseFloat(input.value) || 0;
            subtotalOrcamento += precoTotal;
        });
        
        console.log(`Subtotal do orçamento calculado: ${subtotalOrcamento}`);
        
        // Atualizar o subtotal do orçamento
        subtotalOrcamentoElement.textContent = `R$ ${subtotalOrcamento.toFixed(2).replace('.', ',')}`;
        
        // Calcular e atualizar o valor do SESI (30%)
        const percentualSESI = 0.30; // 30%
        const valorSESI = subtotalOrcamento * percentualSESI;
        valorSESIElement.textContent = `R$ ${valorSESI.toFixed(2).replace('.', ',')}`;
        
        // Calcular e atualizar o total (subtotal + SESI)
        const totalOrcamento = subtotalOrcamento + valorSESI;
        totalOrcamentoElement.textContent = `R$ ${totalOrcamento.toFixed(2).replace('.', ',')}`;
        totalOrcamentoHiddenInput.value = totalOrcamento.toFixed(2);
        
        console.log(`Subtotal: ${subtotalOrcamento}, Valor SESI: ${valorSESI}, Total: ${totalOrcamento}`);
    } catch (error) {
        console.error('Erro ao atualizar total do orçamento:', error);
    }
}

function adicionarServico() {
    contadorServicos++;
    
    const servicosContainer = document.getElementById('servicos-container');
    
    // Criar um novo card para o serviço
    const servicoCard = document.createElement('div');
    servicoCard.id = `servico-card-${contadorServicos}`;
    servicoCard.className = 'card mb-4 servico-card';
    servicoCard.style.backgroundColor = '#1a202c';
    servicoCard.style.border = 'none';
    
    // Obter as opções de serviços do primeiro serviço
    const servicoOptions = document.getElementById('servico-1-nome').innerHTML;
    
    // Obter as opções de regiões do primeiro serviço
    const regiaoOptions = document.getElementById('regiao-1').innerHTML;
    
    // HTML para o novo serviço
    servicoCard.innerHTML = `
        <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h3 class="mb-0">Serviço (${contadorServicos}):</h3>
            <button type="button" class="btn btn-danger" onclick="removerServico(${contadorServicos})">Remover</button>
        </div>
        <div class="card-body" style="background-color: #1a202c;">
            <!-- Etapa 1: Seleção do Serviço -->
            <div class="mb-3">
                <label for="servico-${contadorServicos}-nome" class="form-label text-white">Serviço:</label>
                <select class="form-select servico-select" id="servico-${contadorServicos}-nome" name="servicos[${contadorServicos-1}][nome]" required onchange="mostrarCamposAdicionais(${contadorServicos}); atualizarPreco(${contadorServicos})">
                    ${servicoOptions}
                </select>
                <small class="form-text text-light">Selecione o tipo de serviço a ser incluído no orçamento.</small>
            </div>
            
            <!-- Etapa 2: Parâmetros Específicos para PGR -->
            <div id="parametros-pgr-${contadorServicos}" class="parametros-pgr" style="display: none;">
                <div class="mb-3 campo-adicional campo-pgr" id="grau-risco-container-${contadorServicos}" style="display: none;">
                    <label for="grau-risco-${contadorServicos}" class="form-label text-white">Grau de Risco:</label>
                    <select class="form-select" id="grau-risco-${contadorServicos}" name="servicos[${contadorServicos-1}][grau_risco]" onchange="atualizarPreco(${contadorServicos})">
                        <option value="1e2">1 e 2</option>
                        <option value="3e4">3 e 4</option>
                    </select>
                    <small class="form-text text-light">Selecione o grau de risco da empresa conforme NR-4.</small>
                </div>
                
                <div class="mb-3 campo-adicional campo-pgr" id="num-trabalhadores-container-${contadorServicos}" style="display: none;">
                    <label for="numTrabalhadores-${contadorServicos}" class="form-label text-white">Número de Trabalhadores:</label>
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
                    <small class="form-text text-light">Selecione a faixa de quantidade de trabalhadores da empresa.</small>
                </div>
            </div>
            
            <!-- Etapa 2: Seleção da Região -->
            <div class="mb-3">
                <label for="regiao-${contadorServicos}" class="form-label text-white">Região:</label>
                <select class="form-select regiao-select" id="regiao-${contadorServicos}" name="servicos[${contadorServicos-1}][regiao]" required onchange="atualizarPreco(${contadorServicos})">
                    ${regiaoOptions}
                </select>
                <small class="form-text text-light">Selecione a região onde o serviço será realizado.</small>
            </div>

            <!-- Novo campo para Variável -->
            <div class="mb-3 campo-adicional campo-variavel" id="variavel-container-${contadorServicos}" style="display: none;">
                <label for="variavel-${contadorServicos}" class="form-label text-white">Variável:</label>
                <select class="form-select variavel-select" id="variavel-${contadorServicos}" name="servicos[${contadorServicos-1}][variavel]" onchange="mostrarCamposAdicionais(${contadorServicos}); atualizarPreco(${contadorServicos})">
                    <option value="">Selecione uma variável</option>
                    <!-- As opções serão carregadas dinamicamente via JavaScript -->
                </select>
                <small class="form-text text-light">Selecione a variável específica para este tipo de serviço.</small>
            </div>

            <!-- Após o campo de variável -->
            <div class="mb-3 campo-adicional campo-avaliacao" id="avaliacao-adicional-container-${contadorServicos}" style="display: none;">
                <label for="avaliacao-adicional-${contadorServicos}" class="form-label text-white">Avaliação Adicional:</label>
                <select class="form-select" id="avaliacao-adicional-${contadorServicos}" name="servicos[${contadorServicos-1}][avaliacao_adicional]" onchange="toggleQuantidadeAvaliacoes(${contadorServicos})">
                    <option value="nao">Não</option>
                    <option value="sim">Sim</option>
                </select>
                <small class="form-text text-light">Indique se serão necessárias avaliações adicionais.</small>
            </div>

            <div class="mb-3" id="quantidade-avaliacoes-container-${contadorServicos}" style="display: none;">
                <label for="quantidade-avaliacoes-${contadorServicos}" class="form-label text-white">Quantidade de Avaliações Adicionais:</label>
                <input type="number" class="form-control" id="quantidade-avaliacoes-${contadorServicos}" name="servicos[${contadorServicos-1}][quantidade_avaliacoes]" value="1" min="1" max="10" onchange="atualizarPreco(${contadorServicos})" onkeyup="atualizarPreco(${contadorServicos})">
                <small class="form-text text-light">Informe quantas avaliações adicionais serão necessárias.</small>
            </div>

            <div class="mb-3 campo-adicional campo-ges" id="ges-container-${contadorServicos}" style="display: none;">
                <label for="ges-${contadorServicos}" class="form-label text-white">Número de GES/GHE:</label>
                <input type="number" class="form-control" id="ges-${contadorServicos}" name="servicos[${contadorServicos-1}][ges]" value="1" min="1" onchange="atualizarPreco(${contadorServicos})">
                <small class="form-text text-light">Informe o número de Grupos de Exposição Similar/Grupos Homogêneos de Exposição.</small>
            </div>

            <!-- Após o campo de variável e antes do campo de quantidade -->
            <div class="mb-3 campo-adicional campo-coleta" id="multiplas-coletas-container-${contadorServicos}" style="display: none;">
                <label for="multiplas-coletas-${contadorServicos}" class="form-label text-white">Coletas em dias diferentes:</label>
                <select class="form-select" id="multiplas-coletas-${contadorServicos}" name="servicos[${contadorServicos-1}][multiplas_coletas]" onchange="toggleDiasColeta(${contadorServicos})">
                    <option value="nao">Não</option>
                    <option value="sim">Sim</option>
                </select>
                <small class="form-text text-light">Indique se as coletas serão realizadas em dias diferentes.</small>
            </div>

            <div class="mb-3 campo-adicional" id="dias-coleta-container-${contadorServicos}" style="display: none;">
                <label class="form-label text-white">Quantidade de dias de coleta:</label>
                <input type="number" class="form-control" id="quantidade-dias-${contadorServicos}" name="servicos[${contadorServicos-1}][quantidade_dias]" value="1" min="1" max="30" onchange="atualizarDiasColeta(${contadorServicos})">
                <small class="form-text text-light">Informe em quantos dias diferentes serão realizadas as coletas.</small>
                
                <!-- Container para os detalhes dos dias de coleta -->
                <div id="detalhes-dias-coleta-${contadorServicos}" class="mt-3">
                    <!-- Aqui serão adicionados os campos para cada dia de coleta -->
                </div>
                
                <!-- Campo oculto para armazenar os custos de múltiplos dias -->
                <input type="hidden" id="custos-multiplos-dias-${contadorServicos}" name="servicos[${contadorServicos-1}][custos_multiplos_dias]" value="0">
            </div>

            <div class="mb-3">
                <label for="quantidade-${contadorServicos}" class="form-label text-white">Quantidade:</label>
                <input type="number" class="form-control quantidade-input" id="quantidade-${contadorServicos}" name="servicos[${contadorServicos-1}][quantidade]" value="1" min="1" onchange="atualizarPrecoTotal(${contadorServicos})">
                <small class="form-text text-light">Adicione a quantidade de vezes que o serviço será executado.</small>
            </div>
            
            <!-- Após os campos de região -->
            <div class="mb-3">
                <label for="custos-logisticos-${contadorServicos}" class="form-label text-white">Custos Logísticos:</label>
                <div class="input-group">
                    <span class="input-group-text">R$</span>
                    <input type="number" class="form-control" id="custos-logisticos-${contadorServicos}" name="servicos[${contadorServicos-1}][custos_logisticos]" value="0.00" min="0" step="0.01" onchange="atualizarPrecoTotal(${contadorServicos})">
                </div>
                <small class="form-text text-light">Adicione custos de deslocamento, pedágios, etc.</small>
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

            <!-- Após os campos de GES/GHE -->
            <div class="mb-3 campo-adicional campo-laboratorial" id="custos-laboratoriais-container-${contadorServicos}" style="display: none;">
                <h5 class="text-white">Custos Laboratoriais</h5>
                
                <div class="mb-3">
                    <label for="tipo-amostrador-${contadorServicos}" class="form-label text-white">Tipo de Amostrador:</label>
                    <select class="form-select" id="tipo-amostrador-${contadorServicos}" name="servicos[${contadorServicos-1}][tipo_amostrador]" onchange="calcularCustosLaboratoriais(${contadorServicos})">
                        <option value="">Selecione o tipo de amostrador</option>
                        <option value="bomba">Bomba de Amostragem</option>
                        <option value="dosimetro">Dosímetro</option>
                        <option value="cassete">Cassete</option>
                        <option value="impinger">Impinger</option>
                        <option value="outro">Outro</option>
                    </select>
                    <small class="form-text text-light">Selecione o tipo de equipamento utilizado para coleta de amostras.</small>
                </div>
                
                <div class="mb-3">
                    <label for="quantidade-amostras-${contadorServicos}" class="form-label text-white">Quantidade de Amostras:</label>
                    <input type="number" class="form-control" id="quantidade-amostras-${contadorServicos}" name="servicos[${contadorServicos-1}][quantidade_amostras]" value="1" min="1" onchange="calcularCustosLaboratoriais(${contadorServicos})">
                    <small class="form-text text-light">Informe o número de amostras que serão coletadas.</small>
                </div>
                
                <div class="mb-3">
                    <label for="tipo-analise-${contadorServicos}" class="form-label text-white">Tipo de Análise:</label>
                    <select class="form-select" id="tipo-analise-${contadorServicos}" name="servicos[${contadorServicos-1}][tipo_analise]" onchange="calcularCustosLaboratoriais(${contadorServicos})">
                        <option value="">Selecione o tipo de análise</option>
                        <option value="quimica">Química</option>
                        <option value="biologica">Biológica</option>
                        <option value="fisica">Física</option>
                    </select>
                    <small class="form-text text-light">Selecione o tipo de análise laboratorial a ser realizada.</small>
                </div>
                
                <div class="mb-3">
                    <label for="necessita-art-${contadorServicos}" class="form-label text-white">Necessita ART:</label>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" id="necessita-art-${contadorServicos}" name="servicos[${contadorServicos-1}][necessita_art]" onchange="calcularCustosLaboratoriais(${contadorServicos})">
                        <label class="form-check-label text-white" for="necessita-art-${contadorServicos}">Sim</label>
                    </div>
                    <small class="form-text text-light">Indique se é necessária Anotação de Responsabilidade Técnica.</small>
                </div>
                
                <div class="mb-3">
                    <label for="metodo-envio-${contadorServicos}" class="form-label text-white">Método de Envio:</label>
                    <select class="form-select" id="metodo-envio-${contadorServicos}" name="servicos[${contadorServicos-1}][metodo_envio]" onchange="calcularCustosLaboratoriais(${contadorServicos})">
                        <option value="">Selecione o método de envio</option>
                        <option value="sedex">SEDEX</option>
                        <option value="pac">PAC</option>
                        <option value="transportadora">Transportadora</option>
                        <option value="entrega_pessoal">Entrega Pessoal</option>
                    </select>
                    <small class="form-text text-light">Selecione o método de envio das amostras para o laboratório.</small>
                </div>
                
                <div class="mb-3">
                    <label for="custos-laboratoriais-${contadorServicos}" class="form-label text-white">Custos Laboratoriais:</label>
                    <div class="input-group">
                        <span class="input-group-text">R$</span>
                        <input type="text" class="form-control" id="custos-laboratoriais-valor-${contadorServicos}" name="servicos[${contadorServicos-1}][custos_laboratoriais]" value="0.00" readonly>
                    </div>
                    <small class="form-text text-light">Custos laboratoriais calculados automaticamente.</small>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar o novo card ao container
    servicosContainer.appendChild(servicoCard);
    
    // Adicionar eventos ao novo serviço
    adicionarEventosAoNovoServico(contadorServicos);
    
    // Mostrar o botão de remover para todos os serviços se houver mais de um
    if (contadorServicos > 1) {
        document.querySelectorAll('.servico-card .btn-danger').forEach(btn => {
            btn.style.display = 'block';
        });
    }
    
    // Atualizar o total do orçamento
    atualizarTotalOrcamento();
    
    // Rolar para o novo serviço
    servicoCard.scrollIntoView({ behavior: 'smooth' });
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}