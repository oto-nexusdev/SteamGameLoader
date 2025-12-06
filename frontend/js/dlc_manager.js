// ====== VARIÁVEIS GLOBAIS ======
let gamesData = [];
let selectedDLCs = {}; // {appid: [dlc_id1, dlc_id2, ...]}
let selectedToRemove = {}; // {appid: [dlc_id1, dlc_id2, ...]}
let currentModalAction = null;
let currentModalData = null;
let validationState = {
    validating: false,
    validatedGames: 0,
    totalGames: 0,
    errors: [],
    warnings: []
};
let systemCache = {
    lastUpdate: null,
    version: 'v10.1',
    validated: false
};

// ====== INICIALIZAÇÃO ======
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DLC Manager Pro v10.1 inicializando...');
    
    // Inicializar sistema de cache local
    initLocalCache();
    
    // Carregar Header e Sidebar
    loadHeaderAndSidebar();
    
    // Configurar eventos
    setupEventListeners();
    
    // Verificar atualização automática
    checkAutoUpdate();
    
    // Carregar dados iniciais
    setTimeout(() => {
        loadGames();
        updateStats();
    }, 800);
    
    console.log('✅ DLC Manager Pro pronto');
});

// ====== SISTEMA DE CACHE LOCAL ======
function initLocalCache() {
    try {
        const cache = localStorage.getItem('dlc_manager_cache');
        if (cache) {
            const data = JSON.parse(cache);
            systemCache = { ...systemCache, ...data };
            
            // Verificar se o cache é recente (menos de 1 hora)
            if (systemCache.lastUpdate && (Date.now() - systemCache.lastUpdate) < 3600000) {
                console.log('📦 Cache local encontrado, restaurando...');
                restoreFromCache();
            }
        }
    } catch (error) {
        console.warn('⚠️ Erro ao carregar cache local:', error);
        clearLocalCache();
    }
}

function saveToCache() {
    try {
        systemCache.lastUpdate = Date.now();
        systemCache.version = 'v10.1';
        
        const cacheData = {
            gamesData: gamesData,
            selectedDLCs: selectedDLCs,
            selectedToRemove: selectedToRemove,
            systemCache: systemCache,
            stats: {
                totalGames: document.getElementById('statsTotalGames').textContent,
                gamesWithDLC: document.getElementById('statsGamesWithDLC').textContent,
                availableDLCs: document.getElementById('statsAvailableDLCs').textContent,
                installedDLCs: document.getElementById('statsInstalledDLCs').textContent
            }
        };
        
        localStorage.setItem('dlc_manager_cache', JSON.stringify(cacheData));
        console.log('💾 Cache local salvo');
    } catch (error) {
        console.warn('⚠️ Erro ao salvar cache:', error);
    }
}

function restoreFromCache() {
    try {
        const cache = localStorage.getItem('dlc_manager_cache');
        if (cache) {
            const data = JSON.parse(cache);
            
            // Atualizar estatísticas rapidamente
            if (data.stats) {
                document.getElementById('statsTotalGames').textContent = data.stats.totalGames;
                document.getElementById('statsGamesWithDLC').textContent = data.stats.gamesWithDLC;
                document.getElementById('statsAvailableDLCs').textContent = data.stats.availableDLCs;
                document.getElementById('statsInstalledDLCs').textContent = data.stats.installedDLCs;
            }
            
            showMessage('Dados restaurados do cache local', 'info');
        }
    } catch (error) {
        console.warn('⚠️ Erro ao restaurar cache:', error);
    }
}

function clearLocalCache() {
    try {
        localStorage.removeItem('dlc_manager_cache');
        systemCache = {
            lastUpdate: null,
            version: 'v10.1',
            validated: false
        };
        console.log('🧹 Cache local limpo');
    } catch (error) {
        console.warn('⚠️ Erro ao limpar cache local:', error);
    }
}

// ====== CARREGAMENTO DE COMPONENTES ======
function loadHeaderAndSidebar() {
    // Carregar Header
    fetch('/header.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('header-container').innerHTML = data;
            // Executar scripts do header
            const scripts = document.getElementById('header-container').getElementsByTagName('script');
            for (let script of scripts) {
                try {
                    eval(script.innerHTML);
                } catch (e) {
                    console.error('Erro no script do header:', e);
                }
            }
        })
        .catch(error => console.error('❌ Erro ao carregar header:', error));
    
    // Carregar Sidebar
    fetch('/sidebar.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('sidebar-container').innerHTML = data;
            // Executar scripts da sidebar
            const scripts = document.getElementById('sidebar-container').getElementsByTagName('script');
            for (let script of scripts) {
                try {
                    eval(script.innerHTML);
                } catch (e) {
                    console.error('Erro no script da sidebar:', e);
                }
            }
        })
        .catch(error => console.error('❌ Erro ao carregar sidebar:', error));
}

function setupEventListeners() {
    // Fechar modais ao clicar fora
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                if (this.id === 'confirmationModal') closeModal();
                if (this.id === 'statusModal') closeStatusModal();
                if (this.id === 'gameSummaryModal') closeGameSummaryModal();
                if (this.id === 'validationModal') closeValidationModal();
                if (this.id === 'diagnosticModal') closeDiagnosticModal();
            }
        });
    });
    
    // Fechar modais com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
            closeStatusModal();
            closeGameSummaryModal();
            closeValidationModal();
            closeDiagnosticModal();
        }
    });
    
    // Atualizar cache antes de fechar a página
    window.addEventListener('beforeunload', function() {
        saveToCache();
    });
}

function checkAutoUpdate() {
    // Verificar se precisa atualizar automaticamente (a cada 30 minutos)
    if (systemCache.lastUpdate && (Date.now() - systemCache.lastUpdate) > 1800000) {
        console.log('🔄 Atualização automática necessária');
        showMessage('Atualizando dados automaticamente...', 'info');
        setTimeout(() => loadGames(true), 2000);
    }
}

// ====== FUNÇÕES DE UI ======
function showMessage(message, type = 'info', duration = 5000) {
    const messageDiv = document.getElementById('statusMessage');
    messageDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 15px;">
            <i class="fas fa-${getMessageIcon(type)}" style="font-size: 20px;"></i>
            <span>${message}</span>
        </div>
    `;
    messageDiv.className = `status-message ${type}`;
    messageDiv.style.display = 'block';
    
    // Esconder loader de inicialização
    document.getElementById('initLoader').style.display = 'none';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, duration);
}

function getMessageIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function showLoader(message = 'Carregando...') {
    const loader = document.getElementById('mainLoader');
    loader.querySelector('p').textContent = message;
    loader.style.display = 'block';
    document.getElementById('gamesList').style.display = 'none';
}

function hideLoader() {
    document.getElementById('mainLoader').style.display = 'none';
    document.getElementById('gamesList').style.display = 'block';
}

function showModal(title, message, confirmCallback, confirmText = 'Confirmar', cancelText = 'Cancelar') {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalMessage').textContent = message;
    document.getElementById('modalConfirmBtn').innerHTML = 
        `<i class="fas fa-check"></i><span>${confirmText}</span>`;
    
    currentModalAction = confirmCallback;
    document.getElementById('confirmationModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('confirmationModal').style.display = 'none';
    currentModalAction = null;
    currentModalData = null;
}

function confirmAction() {
    if (currentModalAction) {
        currentModalAction();
    }
    closeModal();
}

function showStatusModal() {
    document.getElementById('statusModal').style.display = 'flex';
}

function closeStatusModal() {
    document.getElementById('statusModal').style.display = 'none';
}

function showGameSummaryModal() {
    document.getElementById('gameSummaryModal').style.display = 'flex';
}

function closeGameSummaryModal() {
    document.getElementById('gameSummaryModal').style.display = 'none';
}

function showValidationModal() {
    document.getElementById('validationModal').style.display = 'flex';
}

function closeValidationModal() {
    document.getElementById('validationModal').style.display = 'none';
    validationState.validating = false;
}

function showDiagnosticModal() {
    document.getElementById('diagnosticModal').style.display = 'flex';
}

function closeDiagnosticModal() {
    document.getElementById('diagnosticModal').style.display = 'none';
}

// ====== FUNÇÕES DE DADOS ======
async function loadGames(forceRefresh = false) {
    showLoader(forceRefresh ? 'Atualizando lista de jogos...' : 'Carregando jogos instalados...');
    showMessage(forceRefresh ? 'Atualizando jogos...' : 'Carregando jogos...', 'info');
    
    // Desativar botão de refresh temporariamente
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Carregando...</span>';
    
    try {
        const url = forceRefresh ? '/api/dlc/games?refresh=true&nocache=' + Date.now() : '/api/dlc/games';
        const response = await fetch(url, {
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            gamesData = data.games || [];
            renderGames();
            updateStats();
            updateGlobalCounts();
            
            const message = forceRefresh ? 
                `${gamesData.length} jogos atualizados com sucesso!` : 
                `${gamesData.length} jogos carregados com sucesso!`;
            
            showMessage(message, 'success');
            systemCache.validated = false;
            
            // Salvar no cache local
            saveToCache();
        } else {
            throw new Error(data.error || 'Erro desconhecido do servidor');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar jogos:', error);
        showMessage(`Erro ao carregar jogos: ${error.message}`, 'error');
        gamesData = [];
        renderGames();
        
        // Tentar restaurar do cache local
        if (!forceRefresh) {
            showMessage('Tentando restaurar do cache...', 'warning');
            setTimeout(() => restoreFromCache(), 1000);
        }
    } finally {
        hideLoader();
        // Reativar botão de refresh
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-redo"></i><span>Atualizar Lista</span>';
    }
}

function renderGames() {
    const gamesList = document.getElementById('gamesList');
    gamesList.innerHTML = '';
    
    if (gamesData.length === 0) {
        gamesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-gamepad"></i>
                <h3>Nenhum jogo encontrado</h3>
                <p>Não foram encontrados jogos Steam instalados no sistema.</p>
                <div style="display: flex; gap: 15px; justify-content: center; margin-top: 25px;">
                    <button class="btn btn-primary" onclick="loadGames(true)">
                        <i class="fas fa-redo"></i> Tentar Novamente
                    </button>
                    <button class="btn btn-secondary" onclick="runSystemDiagnostics()">
                        <i class="fas fa-stethoscope"></i> Diagnóstico
                    </button>
                </div>
            </div>
        `;
        document.getElementById('gamesCount').textContent = '0';
        return;
    }
    
    // Ordenar jogos: com DLC primeiro, depois por nome
    gamesData.sort((a, b) => {
        if (a.has_dlc && !b.has_dlc) return -1;
        if (!a.has_dlc && b.has_dlc) return 1;
        return (a.name || '').localeCompare(b.name || '');
    });
    
    let renderedCount = 0;
    gamesData.forEach(game => {
        const gameCard = createGameCard(game);
        gamesList.appendChild(gameCard);
        
        // Carregar DLCs para este jogo
        loadGameDLCs(game.appid);
        renderedCount++;
    });
    
    document.getElementById('gamesCount').textContent = renderedCount;
    console.log(`✅ ${renderedCount} jogos renderizados`);
}

function createGameCard(game) {
    const card = document.createElement('div');
    card.className = 'game-card';
    card.id = `game-${game.appid}`;
    card.dataset.appid = game.appid;
    
    // Determinar ícone baseado no tipo
    const gameIcon = game.has_dlc ? 'fa-puzzle-piece' : 'fa-gamepad';
    const iconColor = game.has_dlc ? 'var(--accent-color)' : 'var(--text-secondary)';
    
    // Calcular porcentagem de DLCs instaladas (se disponível)
    const dlcPercentage = game.installed_dlc_count && game.total_dlc_count ? 
        Math.round((game.installed_dlc_count / game.total_dlc_count) * 100) : 0;
    
    card.innerHTML = `
        <div class="game-card-header">
            <div class="game-icon" style="background: ${game.has_dlc ? 
                'linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%)' : 
                'linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%)'};">
                <i class="fas ${gameIcon}"></i>
            </div>
            <div class="game-info">
                <h3>${game.name || `AppID: ${game.appid}`}</h3>
                <div class="appid">AppID: ${game.appid}</div>
                <div class="game-stats">
                    <div class="game-stat ${game.has_fix ? 'tooltip' : ''}">
                        <i class="fas ${game.has_fix ? 'fa-wrench' : 'fa-times'}"></i>
                        <span>${game.has_fix ? 'Fix disponível' : 'Sem fix'}</span>
                        ${game.has_fix ? `
                            <span class="tooltiptext">
                                Status: ${game.fix_status || 'unknown'}<br>
                                ${game.fix_version ? `Versão: ${game.fix_version}` : ''}
                            </span>
                        ` : ''}
                    </div>
                    <div class="game-stat">
                        <i class="fas ${game.has_dlc ? 'fa-check' : 'fa-times'}"></i>
                        <span>${game.has_dlc ? 'Tem DLCs' : 'Sem DLCs'}</span>
                    </div>
                    <div class="game-stat tooltip">
                        <i class="fas fa-folder"></i>
                        <span>${(game.install_path || '').split('\\').pop() || 'Caminho'}</span>
                        <span class="tooltiptext">${game.install_path || 'Caminho não disponível'}</span>
                    </div>
                    ${dlcPercentage > 0 ? `
                        <div class="game-stat">
                            <i class="fas fa-percentage"></i>
                            <span>${dlcPercentage}% instalado</span>
                        </div>
                    ` : ''}
                </div>
            </div>
            ${game.data_validated ? `
                <div class="data-validation-badge valid">
                    <i class="fas fa-check-circle"></i> Validado
                </div>
            ` : game.data_invalid ? `
                <div class="data-validation-badge invalid">
                    <i class="fas fa-exclamation-circle"></i> Inválido
                </div>
            ` : ''}
        </div>
        
        <div class="dlc-section">
            <div class="dlc-section-header">
                <h4>
                    <i class="fas fa-puzzle-piece"></i>
                    <span>DLCs Disponíveis</span>
                </h4>
                <div class="dlc-count-badge" id="dlc-count-${game.appid}">
                    <i class="fas fa-spinner fa-spin"></i> Carregando...
                </div>
                <div class="dlc-section-actions">
                    <button class="dlc-toggle-btn" onclick="toggleDlcSection('${game.appid}')">
                        <i class="fas fa-chevron-down"></i>
                        <span>Expandir</span>
                    </button>
                    <button class="btn btn-secondary" onclick="showGameSummary('${game.appid}')" style="padding: 12px 20px;">
                        <i class="fas fa-info-circle"></i>
                        <span>Resumo</span>
                    </button>
                    <button class="btn btn-validation" onclick="validateGameData('${game.appid}')" style="padding: 12px 20px;">
                        <i class="fas fa-check-double"></i>
                        <span>Validar</span>
                    </button>
                </div>
            </div>
            <div class="dlc-list" id="dlc-list-${game.appid}" style="display: none;">
                <!-- DLCs serão inseridas aqui -->
            </div>
            <div id="dlc-loader-${game.appid}" class="loader" style="display: none; padding: 30px;">
                <i class="fas fa-spinner"></i>
                <p>Carregando DLCs...</p>
            </div>
        </div>
        
        <div class="game-controls">
            <button class="game-btn btn-secondary" onclick="refreshGameDLCs('${game.appid}')">
                <i class="fas fa-redo"></i>
                <span>Atualizar DLCs</span>
            </button>
            <button class="game-btn btn-primary" onclick="installSelectedGameDLCs('${game.appid}')">
                <i class="fas fa-download"></i>
                <span>Instalar Selecionadas</span>
                <span class="count-badge" id="selected-count-${game.appid}">0</span>
            </button>
            <button class="game-btn btn-danger" onclick="uninstallSelectedGameDLCs('${game.appid}')">
                <i class="fas fa-trash"></i>
                <span>Remover Selecionadas</span>
                <span class="count-badge" id="selected-remove-count-${game.appid}">0</span>
            </button>
            <button class="game-btn btn-warning" onclick="uninstallAllGameDLCs('${game.appid}')">
                <i class="fas fa-broom"></i>
                <span>Remover Todas</span>
            </button>
        </div>
    `;
    
    return card;
}

async function loadGameDLCs(appid) {
    try {
        // Mostrar loader específico do jogo
        const loader = document.getElementById(`dlc-loader-${appid}`);
        if (loader) loader.style.display = 'block';
        
        const response = await fetch(`/api/dlc/${appid}/list?nocache=${Date.now()}`, {
            headers: {
                'Cache-Control': 'no-cache'
            }
        });
        const data = await response.json();
        
        if (loader) loader.style.display = 'none';
        
        if (data.success) {
            // Validar e processar dados
            const processedData = processDLCData(data, appid);
            renderGameDLCs(appid, processedData);
            
            // Atualizar estatísticas do jogo
            updateGameStats(appid, processedData);
        } else {
            console.error(`❌ ${appid}: ${data.error}`);
            updateDlcCount(appid, 0, 0, 'error');
            showMessage(`Erro ao carregar DLCs para ${appid}: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error(`❌ Erro ao carregar DLCs para ${appid}:`, error);
        updateDlcCount(appid, 0, 0, 'error');
        
        const loader = document.getElementById(`dlc-loader-${appid}`);
        if (loader) loader.style.display = 'none';
    }
}

function processDLCData(data, appid) {
    // Extrair dados brutos
    const rawDLCs = data.dlcs || data.available_dlcs || [];
    const rawInstalled = data.installed_dlc_ids || data.installed_dlcs || [];
    
    // Validar e filtrar DLCs
    const validDLCs = [];
    const seenIds = new Set();
    let invalidCount = 0;
    
    rawDLCs.forEach(dlc => {
        const dlcId = String(dlc.id || dlc.appid || '').trim();
        
        // Validações básicas
        if (!dlcId || !dlcId.match(/^\d+$/)) {
            invalidCount++;
            return;
        }
        
        // Verificar duplicatas
        if (seenIds.has(dlcId)) {
            invalidCount++;
            return;
        }
        
        seenIds.add(dlcId);
        
        // Validar campos obrigatórios
        const validDLC = {
            id: dlcId,
            appid: dlcId,
            name: dlc.name || `DLC ${dlcId}`,
            description: dlc.description || dlc.short_description || 'Sem descrição disponível',
            type: dlc.type || 'dlc',
            price: dlc.price || dlc.final_formatted || 'N/A',
            original_price: dlc.original_price || dlc.initial_formatted || 'N/A',
            discount_percent: dlc.discount_percent || 0,
            is_free: dlc.is_free || false,
            release_date: dlc.release_date || '',
            coming_soon: dlc.coming_soon || false,
            header_image: dlc.header_image || '',
            capsule_image: dlc.capsule_image || '',
            validated: true
        };
        
        // Validação adicional: filtrar conteúdo não-DLC
        if (isValidDLC(validDLC)) {
            validDLCs.push(validDLC);
        } else {
            invalidCount++;
        }
    });
    
    // Validar IDs instalados
    const validInstalled = rawInstalled.filter(id => 
        id && String(id).match(/^\d+$/) && seenIds.has(String(id))
    );
    
    console.log(`🔍 ${appid}: ${validDLCs.length} DLCs válidas, ${invalidCount} inválidas, ${validInstalled.length} instaladas`);
    
    return {
        available_dlcs: validDLCs,
        installed_dlc_ids: validInstalled,
        total_raw: rawDLCs.length,
        total_valid: validDLCs.length,
        invalid_count: invalidCount,
        installed_count: validInstalled.length,
        validated: true
    };
}

function isValidDLC(dlc) {
    // Verificar campos obrigatórios
    if (!dlc.id || !dlc.name) return false;
    
    // Filtrar conteúdo que não são DLCs reais
    const name = dlc.name.toLowerCase();
    const invalidKeywords = [
        'soundtrack', 'ost', 'artbook', 'guide', 'season pass',
        'bundle', 'pack', 'comic', 'art book', 'strategy guide',
        'sound track', 'digital artbook', 'digital soundtrack',
        'pre-order', 'preorder', 'deluxe edition', 'gold edition',
        'ultimate edition', 'collector\'s edition'
    ];
    
    return !invalidKeywords.some(keyword => name.includes(keyword));
}

function renderGameDLCs(appid, dlcData) {
    const dlcList = document.getElementById(`dlc-list-${appid}`);
    if (!dlcList) return;
    
    const availableDLCs = dlcData.available_dlcs || [];
    const installedDLCs = dlcData.installed_dlc_ids || [];
    
    // Inicializar arrays de seleção
    if (!selectedDLCs[appid]) selectedDLCs[appid] = [];
    if (!selectedToRemove[appid]) selectedToRemove[appid] = [];
    
    dlcList.innerHTML = '';
    
    if (availableDLCs.length === 0) {
        dlcList.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1; padding: 40px;">
                <i class="fas fa-puzzle-piece"></i>
                <h3>Nenhuma DLC disponível</h3>
                <p>Este jogo não possui DLCs válidas na Steam ou houve um erro ao carregar.</p>
                ${dlcData.invalid_count > 0 ? `
                    <p style="color: var(--warning-color); margin-top: 10px;">
                        <i class="fas fa-exclamation-triangle"></i>
                        ${dlcData.invalid_count} entradas inválidas foram filtradas
                    </p>
                ` : ''}
            </div>
        `;
        updateDlcCount(appid, 0, 0, dlcData.validated ? 'valid' : 'error');
        return;
    }
    
    // Ordenar DLCs: instaladas primeiro, depois por nome
    const sortedDLCs = [...availableDLCs].sort((a, b) => {
        const aInstalled = installedDLCs.includes(a.id);
        const bInstalled = installedDLCs.includes(b.id);
        
        if (aInstalled && !bInstalled) return -1;
        if (!aInstalled && bInstalled) return 1;
        
        return (a.name || '').localeCompare(b.name || '');
    });
    
    // Renderizar cada DLC
    sortedDLCs.forEach(dlc => {
        const dlcId = dlc.id;
        const isInstalled = installedDLCs.includes(dlcId);
        const isSelected = selectedDLCs[appid].includes(dlcId);
        const isSelectedForRemoval = selectedToRemove[appid].includes(dlcId);
        
        const dlcItem = document.createElement('div');
        dlcItem.className = `dlc-item ${isInstalled ? 'installed' : ''} ${isSelected || isSelectedForRemoval ? 'selected' : ''}`;
        dlcItem.dataset.dlcId = dlcId;
        dlcItem.dataset.appid = appid;
        dlcItem.dataset.installed = isInstalled;
        dlcItem.dataset.validated = dlc.validated || false;
        
        // Formatar preço
        const priceHtml = dlc.is_free ? 
            '<span style="color: var(--success-color); font-weight: 700;">GRÁTIS</span>' :
            `<span>${dlc.price}</span>${dlc.discount_percent > 0 ? 
                `<span style="color: var(--danger-color); margin-left: 5px;">-${dlc.discount_percent}%</span>` : ''}`;
        
        // Formatar data de lançamento
        const releaseDate = dlc.release_date ? 
            new Date(dlc.release_date).toLocaleDateString('pt-BR') : 'N/A';
        
        dlcItem.innerHTML = `
            <div class="dlc-checkbox-container">
                <input type="checkbox" class="dlc-checkbox ${isInstalled ? 'installed' : ''}" 
                       id="dlc-${appid}-${dlcId}"
                       onchange="${isInstalled ? 
                           `toggleDLCRemoval('${appid}', '${dlcId}')` : 
                           `toggleDLCSlection('${appid}', '${dlcId}')`}"
                       ${isInstalled ? (isSelectedForRemoval ? 'checked' : '') : (isSelected ? 'checked' : '')}>
            </div>
            
            <div class="dlc-info">
                <h5>${dlc.name}</h5>
                <div class="dlc-description">${dlc.description}</div>
                <div class="dlc-meta">
                    <div class="dlc-meta-item">
                        <i class="fas fa-tag"></i>
                        <span>${dlc.type.toUpperCase()}</span>
                    </div>
                    <div class="dlc-meta-item">
                        <i class="fas fa-dollar-sign"></i>
                        ${priceHtml}
                    </div>
                    <div class="dlc-meta-item">
                        <i class="fas fa-calendar"></i>
                        <span>${releaseDate}</span>
                    </div>
                    ${dlc.coming_soon ? `
                        <div class="dlc-meta-item" style="color: var(--warning-color);">
                            <i class="fas fa-clock"></i>
                            <span>EM BREVE</span>
                        </div>
                    ` : ''}
                </div>
                <div class="dlc-actions">
                    ${!isInstalled ? `
                        <button class="dlc-action-btn dlc-action-install" onclick="installSingleDLC('${appid}', '${dlcId}')">
                            <i class="fas fa-download"></i>
                            <span>Instalar</span>
                        </button>
                    ` : ''}
                    ${isInstalled ? `
                        <button class="dlc-action-btn dlc-action-remove" onclick="removeSingleDLC('${appid}', '${dlcId}')">
                            <i class="fas fa-trash"></i>
                            <span>Remover</span>
                        </button>
                    ` : ''}
                    <button class="dlc-action-btn" style="background: rgba(122, 42, 255, 0.2); color: var(--primary-color); border-color: rgba(122, 42, 255, 0.3);" 
                            onclick="showDLCInfo('${appid}', '${dlcId}')">
                        <i class="fas fa-info-circle"></i>
                        <span>Detalhes</span>
                    </button>
                </div>
            </div>
            
            <div class="dlc-status ${isInstalled ? 'installed' : 'available'}">
                ${isInstalled ? '<i class="fas fa-check"></i> Instalada' : '<i class="fas fa-box"></i> Disponível'}
            </div>
        `;
        
        dlcList.appendChild(dlcItem);
    });
    
    // Atualizar contagem com dados válidos
    updateDlcCount(appid, availableDLCs.length, installedDLCs.length, 
                 dlcData.validated ? 'valid' : 'warning');
    
    // Atualizar contagens de seleção
    updateSelectedCount(appid);
    updateSelectedRemoveCount(appid);
    
    // Mostrar warning se houver dados inválidos
    if (dlcData.invalid_count > 0) {
        console.warn(`⚠️ ${appid}: ${dlcData.invalid_count} DLCs inválidas filtradas`);
    }
}

function updateDlcCount(appid, total, installed, status = 'loading') {
    const countElement = document.getElementById(`dlc-count-${appid}`);
    if (!countElement) return;
    
    let badgeClass = '';
    let badgeText = '';
    let icon = '';
    
    switch (status) {
        case 'valid':
            badgeClass = installed === total ? 'success' : '';
            badgeText = `${installed}/${total} instaladas`;
            icon = installed === total ? 'fa-check-circle' : 'fa-puzzle-piece';
            break;
        case 'warning':
            badgeClass = '';
            badgeText = `${installed}/${total} (verificar)`;
            icon = 'fa-exclamation-triangle';
            break;
        case 'error':
            badgeClass = '';
            badgeText = 'Erro ao carregar';
            icon = 'fa-times-circle';
            break;
        default:
            badgeClass = '';
            badgeText = 'Carregando...';
            icon = 'fa-spinner fa-spin';
    }
    
    countElement.className = `dlc-count-badge ${badgeClass}`;
    countElement.innerHTML = `<i class="fas ${icon}"></i> ${badgeText}`;
    
    // Atualizar dados do jogo
    const game = gamesData.find(g => g.appid === appid);
    if (game) {
        game.total_dlc_count = total;
        game.installed_dlc_count = installed;
        game.dlc_percentage = total > 0 ? Math.round((installed / total) * 100) : 0;
    }
}

function updateGameStats(appid, dlcData) {
    // Esta função pode ser expandida para atualizar outras estatísticas do jogo
    console.log(`📊 ${appid}: ${dlcData.installed_count}/${dlcData.total_valid} DLCs instaladas`);
}

// ====== FUNÇÕES DE SELEÇÃO ======
function toggleDLCSlection(appid, dlcId) {
    if (!selectedDLCs[appid]) {
        selectedDLCs[appid] = [];
    }
    
    const checkbox = document.getElementById(`dlc-${appid}-${dlcId}`);
    const dlcItem = checkbox?.closest('.dlc-item');
    
    if (!checkbox || !dlcItem) return;
    
    if (checkbox.checked) {
        if (!selectedDLCs[appid].includes(dlcId)) {
            selectedDLCs[appid].push(dlcId);
            dlcItem.classList.add('selected');
        }
    } else {
        selectedDLCs[appid] = selectedDLCs[appid].filter(id => id !== dlcId);
        dlcItem.classList.remove('selected');
    }
    
    updateSelectedCount(appid);
    updateGlobalCounts();
    updateStats();
}

function toggleDLCRemoval(appid, dlcId) {
    if (!selectedToRemove[appid]) {
        selectedToRemove[appid] = [];
    }
    
    const checkbox = document.getElementById(`dlc-${appid}-${dlcId}`);
    const dlcItem = checkbox?.closest('.dlc-item');
    
    if (!checkbox || !dlcItem) return;
    
    if (checkbox.checked) {
        if (!selectedToRemove[appid].includes(dlcId)) {
            selectedToRemove[appid].push(dlcId);
            dlcItem.classList.add('selected');
        }
    } else {
        selectedToRemove[appid] = selectedToRemove[appid].filter(id => id !== dlcId);
        dlcItem.classList.remove('selected');
    }
    
    updateSelectedRemoveCount(appid);
    updateGlobalCounts();
    updateStats();
}

function updateSelectedCount(appid) {
    const count = selectedDLCs[appid] ? selectedDLCs[appid].length : 0;
    const countElement = document.getElementById(`selected-count-${appid}`);
    if (countElement) {
        countElement.textContent = count;
        countElement.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

function updateSelectedRemoveCount(appid) {
    const count = selectedToRemove[appid] ? selectedToRemove[appid].length : 0;
    const countElement = document.getElementById(`selected-remove-count-${appid}`);
    if (countElement) {
        countElement.textContent = count;
        countElement.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

function updateGlobalCounts() {
    let totalSelected = 0;
    let totalToRemove = 0;
    
    for (const appid in selectedDLCs) {
        totalSelected += selectedDLCs[appid].length;
    }
    
    for (const appid in selectedToRemove) {
        totalToRemove += selectedToRemove[appid].length;
    }
    
    document.getElementById('globalSelectedCount').textContent = totalSelected;
    document.getElementById('globalRemoveCount').textContent = totalToRemove;
}

function selectAllDLCs() {
    let totalSelected = 0;
    
    gamesData.forEach(game => {
        const appid = game.appid;
        const dlcList = document.getElementById(`dlc-list-${appid}`);
        if (!dlcList) return;
        
        const checkboxes = dlcList.querySelectorAll('.dlc-checkbox:not(.installed):not(:checked)');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
            const dlcId = checkbox.id.replace(`dlc-${appid}-`, '');
            toggleDLCSlection(appid, dlcId);
            totalSelected++;
        });
    });
    
    if (totalSelected > 0) {
        showMessage(`${totalSelected} DLCs selecionadas!`, 'success');
    } else {
        showMessage('Todas as DLCs já estão selecionadas', 'info');
    }
}

function deselectAllDLCs() {
    let totalDeselected = 0;
    
    gamesData.forEach(game => {
        const appid = game.appid;
        if (selectedDLCs[appid]) {
            totalDeselected += selectedDLCs[appid].length;
            selectedDLCs[appid] = [];
        }
        
        const checkboxes = document.querySelectorAll(`#dlc-list-${appid} .dlc-checkbox:not(.installed)`);
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
            const dlcItem = checkbox.closest('.dlc-item');
            if (dlcItem) {
                dlcItem.classList.remove('selected');
            }
        });
        
        updateSelectedCount(appid);
    });
    
    updateGlobalCounts();
    
    if (totalDeselected > 0) {
        showMessage(`${totalDeselected} DLCs deselecionadas!`, 'info');
    } else {
        showMessage('Nenhuma DLC estava selecionada', 'info');
    }
}

// ====== FUNÇÕES DE INSTALAÇÃO ======
async function installSelectedGameDLCs(appid) {
    const dlcIds = selectedDLCs[appid] || [];
    
    if (dlcIds.length === 0) {
        showMessage('Selecione pelo menos uma DLC para instalar.', 'error');
        return;
    }
    
    showModal(
        'Instalar DLCs',
        `Deseja instalar ${dlcIds.length} DLC(s) para o jogo ${appid}?`,
        async () => {
            try {
                showMessage(`Instalando ${dlcIds.length} DLC(s)...`, 'info');
                
                const response = await fetch(`/api/dlc/${appid}/install`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify({ dlc_ids: dlcIds })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const installedCount = data.installed || 0;
                    const message = installedCount > 0 ? 
                        `${installedCount} DLC(s) instaladas com sucesso!` :
                        'Todas as DLCs selecionadas já estavam instaladas.';
                    
                    showMessage(message, 'success');
                    
                    // Recarregar DLCs
                    await loadGameDLCs(appid);
                    
                    // Limpar selecionadas
                    selectedDLCs[appid] = [];
                    updateSelectedCount(appid);
                    updateGlobalCounts();
                    
                    // Atualizar estatísticas
                    updateStats();
                    
                    // Salvar no cache
                    saveToCache();
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                console.error('❌ Erro ao instalar DLCs:', error);
                showMessage(`Erro ao instalar DLCs: ${error.message}`, 'error');
            }
        },
        'Instalar'
    );
}

async function installSingleDLC(appid, dlcId) {
    showModal(
        'Instalar DLC',
        `Deseja instalar a DLC "${dlcId}" para o jogo ${appid}?`,
        async () => {
            try {
                showMessage(`Instalando DLC ${dlcId}...`, 'info');
                
                const response = await fetch(`/api/dlc/${appid}/install`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify({ dlc_ids: [dlcId] })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(`DLC ${dlcId} instalada com sucesso!`, 'success');
                    
                    // Recarregar DLCs
                    await loadGameDLCs(appid);
                    
                    // Atualizar estatísticas
                    updateStats();
                    
                    // Salvar no cache
                    saveToCache();
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                console.error('❌ Erro ao instalar DLC:', error);
                showMessage(`Erro ao instalar DLC: ${error.message}`, 'error');
            }
        },
        'Instalar'
    );
}

async function installSelectedDLCs() {
    // Coletar todas as DLCs selecionadas
    const installs = [];
    let totalToInstall = 0;
    
    for (const appid in selectedDLCs) {
        const dlcIds = selectedDLCs[appid];
        if (dlcIds.length > 0) {
            installs.push({ appid, dlcIds });
            totalToInstall += dlcIds.length;
        }
    }
    
    if (totalToInstall === 0) {
        showMessage('Nenhuma DLC selecionada para instalação.', 'error');
        return;
    }
    
    showModal(
        'Instalar DLCs em Massa',
        `Deseja instalar ${totalToInstall} DLC(s) em ${installs.length} jogo(s)?`,
        async () => {
            try {
                showMessage(`Instalando ${totalToInstall} DLC(s)...`, 'info');
                
                let totalInstalled = 0;
                const errors = [];
                const success = [];
                
                // Instalar em cada jogo
                for (const install of installs) {
                    try {
                        const response = await fetch(`/api/dlc/${install.appid}/install`, {
                            method: 'POST',
                            headers: { 
                                'Content-Type': 'application/json',
                                'Cache-Control': 'no-cache'
                            },
                            body: JSON.stringify({ dlc_ids: install.dlcIds })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            const installed = data.installed || 0;
                            totalInstalled += installed;
                            success.push(`Jogo ${install.appid}: ${installed} DLC(s) instalada(s)`);
                            
                            // Recarregar DLCs deste jogo
                            await loadGameDLCs(install.appid);
                            
                            // Limpar selecionadas
                            selectedDLCs[install.appid] = [];
                            updateSelectedCount(install.appid);
                        } else {
                            errors.push(`Jogo ${install.appid}: ${data.error}`);
                        }
                    } catch (error) {
                        errors.push(`Jogo ${install.appid}: ${error.message}`);
                    }
                }
                
                updateGlobalCounts();
                updateStats();
                saveToCache();
                
                if (errors.length === 0) {
                    showMessage(`${totalInstalled} DLC(s) instaladas com sucesso!`, 'success');
                } else {
                    const message = `${totalInstalled} DLC(s) instaladas, ${errors.length} erro(s).`;
                    showMessage(message, totalInstalled > 0 ? 'warning' : 'error');
                    console.error('Erros:', errors);
                }
                
            } catch (error) {
                console.error('❌ Erro na instalação em massa:', error);
                showMessage(`Erro na instalação: ${error.message}`, 'error');
            }
        },
        'Instalar Todas'
    );
}

// ====== FUNÇÕES DE REMOÇÃO ======
async function uninstallSelectedGameDLCs(appid) {
    const dlcIds = selectedToRemove[appid] || [];
    
    if (dlcIds.length === 0) {
        showMessage('Selecione pelo menos uma DLC instalada para remover.', 'error');
        return;
    }
    
    showModal(
        'Remover DLCs',
        `Deseja remover ${dlcIds.length} DLC(s) do jogo ${appid}?`,
        async () => {
            try {
                showMessage(`Removendo ${dlcIds.length} DLC(s)...`, 'info');
                
                const response = await fetch(`/api/dlc/${appid}/uninstall`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify({ dlc_ids: dlcIds })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(`${data.removed || 0} DLC(s) removidas com sucesso!`, 'success');
                    
                    // Recarregar DLCs
                    await loadGameDLCs(appid);
                    
                    // Limpar selecionadas para remoção
                    selectedToRemove[appid] = [];
                    updateSelectedRemoveCount(appid);
                    updateGlobalCounts();
                    
                    // Atualizar estatísticas
                    updateStats();
                    
                    // Salvar no cache
                    saveToCache();
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                console.error('❌ Erro ao remover DLCs:', error);
                showMessage(`Erro ao remover DLCs: ${error.message}`, 'error');
            }
        },
        'Remover'
    );
}

async function removeSingleDLC(appid, dlcId) {
    showModal(
        'Remover DLC',
        `Deseja remover a DLC "${dlcId}" do jogo ${appid}?`,
        async () => {
            try {
                showMessage(`Removendo DLC ${dlcId}...`, 'info');
                
                const response = await fetch(`/api/dlc/${appid}/uninstall`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify({ dlc_ids: [dlcId] })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(`DLC ${dlcId} removida com sucesso!`, 'success');
                    
                    // Recarregar DLCs
                    await loadGameDLCs(appid);
                    
                    // Atualizar estatísticas
                    updateStats();
                    
                    // Salvar no cache
                    saveToCache();
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                console.error('❌ Erro ao remover DLC:', error);
                showMessage(`Erro ao remover DLC: ${error.message}`, 'error');
            }
        },
        'Remover'
    );
}

async function uninstallAllGameDLCs(appid) {
    showModal(
        'Remover Todas as DLCs',
        `Deseja remover TODAS as DLCs instaladas do jogo ${appid}?<br><br>
        <span style="color: var(--warning-color); font-weight: 700;">
            <i class="fas fa-exclamation-triangle"></i> Esta ação não pode ser desfeita!
        </span>`,
        async () => {
            try {
                showMessage(`Removendo todas as DLCs do jogo ${appid}...`, 'info');
                
                const response = await fetch(`/api/dlc/${appid}/uninstall`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify({ dlc_ids: [] }) // Array vazio = remover todas
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(`${data.removed || 0} DLC(s) removidas do jogo ${appid}!`, 'success');
                    
                    // Recarregar DLCs
                    await loadGameDLCs(appid);
                    
                    // Limpar selecionadas
                    selectedToRemove[appid] = [];
                    updateSelectedRemoveCount(appid);
                    updateGlobalCounts();
                    
                    // Atualizar estatísticas
                    updateStats();
                    
                    // Salvar no cache
                    saveToCache();
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                console.error('❌ Erro ao remover DLCs:', error);
                showMessage(`Erro ao remover DLCs: ${error.message}`, 'error');
            }
        },
        'Remover Todas'
    );
}

async function uninstallSelectedDLCs() {
    let totalToRemove = 0;
    const removals = [];
    
    // Contar total e preparar remoções
    for (const appid in selectedToRemove) {
        const dlcIds = selectedToRemove[appid];
        if (dlcIds.length > 0) {
            totalToRemove += dlcIds.length;
            removals.push({ appid, dlcIds });
        }
    }
    
    if (totalToRemove === 0) {
        showMessage('Nenhuma DLC selecionada para remoção.', 'error');
        return;
    }
    
    showModal(
        'Remover DLCs Selecionadas',
        `Deseja remover ${totalToRemove} DLC(s) instalada(s) em ${removals.length} jogo(s)?<br><br>
        <span style="color: var(--warning-color); font-weight: 700;">
            <i class="fas fa-exclamation-triangle"></i> Esta ação não pode ser desfeita!
        </span>`,
        async () => {
            try {
                showMessage(`Removendo ${totalToRemove} DLC(s)...`, 'info');
                
                let totalRemoved = 0;
                const errors = [];
                const success = [];
                
                // Remover de cada jogo
                for (const removal of removals) {
                    try {
                        const response = await fetch(`/api/dlc/${removal.appid}/uninstall`, {
                            method: 'POST',
                            headers: { 
                                'Content-Type': 'application/json',
                                'Cache-Control': 'no-cache'
                            },
                            body: JSON.stringify({ dlc_ids: removal.dlcIds })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            const removed = data.removed || 0;
                            totalRemoved += removed;
                            success.push(`Jogo ${removal.appid}: ${removed} DLC(s) removida(s)`);
                            
                            // Recarregar DLCs deste jogo
                            await loadGameDLCs(removal.appid);
                            
                            // Limpar selecionadas para remoção
                            selectedToRemove[removal.appid] = [];
                            updateSelectedRemoveCount(removal.appid);
                        } else {
                            errors.push(`Jogo ${removal.appid}: ${data.error}`);
                        }
                    } catch (error) {
                        errors.push(`Jogo ${removal.appid}: ${error.message}`);
                    }
                }
                
                updateGlobalCounts();
                updateStats();
                saveToCache();
                
                if (errors.length === 0) {
                    showMessage(`${totalRemoved} DLC(s) removidas com sucesso!`, 'success');
                } else {
                    const message = `${totalRemoved} DLC(s) removidas, ${errors.length} erro(s).`;
                    showMessage(message, totalRemoved > 0 ? 'warning' : 'error');
                    console.error('Erros:', errors);
                }
                
            } catch (error) {
                console.error('❌ Erro na remoção em massa:', error);
                showMessage(`Erro na remoção: ${error.message}`, 'error');
            }
        },
        'Remover Todas'
    );
}

// ====== FUNÇÕES DE SISTEMA ======
async function showSystemStatus() {
    try {
        const response = await fetch('/api/dlc/status?nocache=' + Date.now());
        const data = await response.json();
        
        if (data.success) {
            let html = `
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-code-branch"></i> Versão:
                    </span>
                    <span class="status-value">${data.version || 'DLCManager v10.1'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-folder"></i> Steam Path:
                    </span>
                    <span class="status-value">${data.steam_path || 'Não definido'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-plug"></i> stplug-in:
                    </span>
                    <span class="status-value">${data['stplug-in'] || 'Não encontrado'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-gamepad"></i> Total de Jogos:
                    </span>
                    <span class="status-value">${data.total_games || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-puzzle-piece"></i> Jogos com DLC:
                    </span>
                    <span class="status-value">${data.games_with_dlc || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-database"></i> Cache DLC (jogos):
                    </span>
                    <span class="status-value">${data.dlc_cache_size || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-boxes"></i> DLCs em Cache:
                    </span>
                    <span class="status-value">${data.total_dlcs_cached || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-memory"></i> Cache de Jogos:
                    </span>
                    <span class="status-value">
                        ${data.from_cache ? 
                            '<span style="color: var(--success-color);">Ativo</span>' : 
                            '<span style="color: var(--warning-color);">Inativo</span>'}
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-clock"></i> Última Atualização:
                    </span>
                    <span class="status-value">${new Date((data.timestamp || Date.now()/1000) * 1000).toLocaleString()}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-hdd"></i> Cache Local:
                    </span>
                    <span class="status-value">
                        ${systemCache.lastUpdate ? 
                            '<span style="color: var(--success-color);">Ativo</span>' : 
                            '<span style="color: var(--warning-color);">Inativo</span>'}
                    </span>
                </div>
            `;
            
            document.getElementById('statusModalContent').innerHTML = html;
            document.getElementById('statusModal').style.display = 'flex';
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
    } catch (error) {
        console.error('❌ Erro ao obter status do sistema:', error);
        showMessage(`Erro ao obter status: ${error.message}`, 'error');
    }
}

async function refreshSystemStatus() {
    await showSystemStatus();
}

async function showGameSummary(appid) {
    try {
        const response = await fetch(`/api/dlc/${appid}/summary?nocache=${Date.now()}`);
        const data = await response.json();
        
        if (data.success) {
            const game = data.game;
            
            // Calcular porcentagens
            const dlcPercentage = data.available_dlcs > 0 ? 
                Math.round((data.installed_dlcs / data.available_dlcs) * 100) : 0;
            
            let html = `
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-hashtag"></i> AppID:
                    </span>
                    <span class="status-value">${game.appid || appid}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-heading"></i> Nome:
                    </span>
                    <span class="status-value">${game.name || 'Desconhecido'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-folder-open"></i> Caminho:
                    </span>
                    <span class="status-value" style="word-break: break-all;">${game.install_path || 'Não disponível'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-wrench"></i> Fix:
                    </span>
                    <span class="status-value">
                        ${game.has_fix ? 
                            '<span style="color: var(--success-color);">Disponível</span>' : 
                            '<span style="color: var(--warning-color);">Não disponível</span>'}
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-tools"></i> Status Fix:
                    </span>
                    <span class="status-value">${game.fix_status || 'none'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-box-open"></i> DLCs Disponíveis:
                    </span>
                    <span class="status-value">${data.available_dlcs || 0}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-check-circle"></i> DLCs Instaladas:
                    </span>
                    <span class="status-value">
                        ${data.installed_dlcs || 0}
                        ${dlcPercentage > 0 ? `(${dlcPercentage}%)` : ''}
                    </span>
                </div>
                <div class="status-item">
                    <span class="status-label">
                        <i class="fas fa-check-double"></i> Dados Validados:
                    </span>
                    <span class="status-value">
                        ${data.validated_count ? 
                            `<span style="color: var(--success-color);">${data.validated_count} válidas</span>` : 
                            '<span style="color: var(--warning-color);">Não validado</span>'}
                    </span>
                </div>
                ${data.dlcs && data.dlcs.length > 0 ? `
                    <div class="status-item">
                        <span class="status-label">
                            <i class="fas fa-list"></i> Última DLC:
                        </span>
                        <span class="status-value">${data.dlcs[0].name || 'N/A'}</span>
                    </div>
                ` : ''}
            `;
            
            document.getElementById('gameSummaryTitle').textContent = `Resumo: ${game.name || appid}`;
            document.getElementById('gameSummaryContent').innerHTML = html;
            document.getElementById('gameSummaryModal').style.display = 'flex';
            
            // Atualizar botão de validação
            document.getElementById('validateGameBtn').onclick = () => validateGameData(appid);
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
    } catch (error) {
        console.error(`❌ Erro ao obter resumo do jogo ${appid}:`, error);
        showMessage(`Erro ao obter resumo: ${error.message}`, 'error');
    }
}

// ====== FUNÇÕES DE VALIDAÇÃO ======
async function validateAllGamesData() {
    if (validationState.validating) {
        showMessage('Validação já em andamento...', 'warning');
        return;
    }
    
    if (gamesData.length === 0) {
        showMessage('Nenhum jogo para validar. Carregue os jogos primeiro.', 'error');
        return;
    }
    
    validationState = {
        validating: true,
        validatedGames: 0,
        totalGames: gamesData.length,
        errors: [],
        warnings: []
    };
    
    showValidationModal();
    updateValidationProgress(0);
    
    const validationContent = document.getElementById('validationContent');
    validationContent.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <i class="fas fa-check-double" style="font-size: 48px; color: var(--primary-color); margin-bottom: 15px;"></i>
            <h3 style="color: var(--text-primary); margin-bottom: 10px;">Validando Dados dos Jogos</h3>
            <p style="color: var(--text-secondary);">Validando ${validationState.totalGames} jogos...</p>
        </div>
        <div id="validationLog" style="max-height: 300px; overflow-y: auto; background: rgba(0, 0, 0, 0.2); border-radius: 8px; padding: 15px;"></div>
    `;
    
    const validationLog = document.getElementById('validationLog');
    
    // Validar cada jogo sequencialmente
    for (let i = 0; i < gamesData.length; i++) {
        const game = gamesData[i];
        const appid = game.appid;
        
        try {
            // Atualizar progresso
            const progress = Math.round(((i + 1) / gamesData.length) * 100);
            updateValidationProgress(progress);
            
            // Adicionar log
            validationLog.innerHTML += `
                <div style="padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-spinner fa-spin" style="color: var(--accent-color);"></i>
                        <span style="color: var(--text-secondary);">Validando ${game.name || appid}...</span>
                    </div>
                </div>
            `;
            validationLog.scrollTop = validationLog.scrollHeight;
            
            // Chamar API de validação
            const response = await fetch(`/api/dlc/${appid}/validate?nocache=${Date.now()}`);
            const data = await response.json();
            
            if (data.success) {
                validationState.validatedGames++;
                
                // Atualizar log com resultado
                const logEntries = validationLog.children;
                const lastEntry = logEntries[logEntries.length - 1];
                lastEntry.innerHTML = `
                    <div style="padding: 8px 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
                            <span style="color: var(--success-color);">${game.name || appid}: ${data.total_valid} DLCs válidas</span>
                        </div>
                        ${data.total_raw !== data.total_valid ? `
                            <div style="margin-left: 26px; font-size: 12px; color: var(--warning-color);">
                                <i class="fas fa-exclamation-triangle"></i>
                                ${data.total_raw - data.total_valid} entradas inválidas filtradas
                            </div>
                        ` : ''}
                    </div>
                `;
                
                // Atualizar badge do jogo
                updateGameValidationBadge(appid, true);
                
            } else {
                validationState.errors.push(`${appid}: ${data.error}`);
                
                // Atualizar log com erro
                const logEntries = validationLog.children;
                const lastEntry = logEntries[logEntries.length - 1];
                lastEntry.innerHTML = `
                    <div style="padding: 8px 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <i class="fas fa-times-circle" style="color: var(--danger-color);"></i>
                            <span style="color: var(--danger-color);">${game.name || appid}: Erro na validação</span>
                        </div>
                        <div style="margin-left: 26px; font-size: 12px; color: var(--text-muted);">
                            ${data.error || 'Erro desconhecido'}
                        </div>
                    </div>
                `;
                
                updateGameValidationBadge(appid, false);
            }
            
            // Pequena pausa para não sobrecarregar
            await new Promise(resolve => setTimeout(resolve, 100));
            
        } catch (error) {
            validationState.errors.push(`${appid}: ${error.message}`);
            
            // Atualizar log com erro
            validationLog.innerHTML += `
                <div style="padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <i class="fas fa-times-circle" style="color: var(--danger-color);"></i>
                        <span style="color: var(--danger-color);">${game.name || appid}: Erro de conexão</span>
                    </div>
                </div>
            `;
        }
    }
    
    // Finalizar validação
    validationState.validating = false;
    updateValidationProgress(100);
    
    // Mostrar resumo
    const successRate = Math.round((validationState.validatedGames / validationState.totalGames) * 100);
    const summaryHtml = `
        <div style="text-align: center; padding: 20px; background: rgba(0, 0, 0, 0.2); border-radius: 8px; margin-top: 20px;">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">Validação Concluída</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
                <div style="background: rgba(0, 255, 136, 0.1); padding: 12px; border-radius: 6px; border: 1px solid rgba(0, 255, 136, 0.2);">
                    <div style="font-size: 24px; color: var(--success-color); font-weight: 700;">${validationState.validatedGames}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">Jogos Validados</div>
                </div>
                <div style="background: rgba(255, 42, 109, 0.1); padding: 12px; border-radius: 6px; border: 1px solid rgba(255, 42, 109, 0.2);">
                    <div style="font-size: 24px; color: var(--danger-color); font-weight: 700;">${validationState.errors.length}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">Erros</div>
                </div>
            </div>
            <div style="background: rgba(122, 42, 255, 0.1); padding: 12px; border-radius: 6px; border: 1px solid rgba(122, 42, 255, 0.2);">
                <div style="font-size: 28px; color: var(--primary-color); font-weight: 700;">${successRate}%</div>
                <div style="font-size: 12px; color: var(--text-secondary);">Taxa de Sucesso</div>
            </div>
        </div>
    `;
    
    validationContent.innerHTML += summaryHtml;
    systemCache.validated = true;
    saveToCache();
    
    showMessage(`Validação concluída: ${successRate}% de sucesso`, 'success');
}

async function validateGameData(appid) {
    try {
        const response = await fetch(`/api/dlc/${appid}/validate?nocache=${Date.now()}`);
        const data = await response.json();
        
        if (data.success) {
            // Recarregar DLCs com dados validados
            await loadGameDLCs(appid);
            
            // Atualizar badge
            updateGameValidationBadge(appid, true);
            
            showMessage(`Jogo ${appid} validado: ${data.total_valid} DLCs válidas encontradas`, 'success');
        } else {
            updateGameValidationBadge(appid, false);
            showMessage(`Erro ao validar jogo ${appid}: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error(`❌ Erro ao validar jogo ${appid}:`, error);
        showMessage(`Erro ao validar: ${error.message}`, 'error');
    }
}

function updateValidationProgress(percentage) {
    const progressBar = document.getElementById('validationProgress');
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${percentage}%`;
    }
}

function updateGameValidationBadge(appid, isValid) {
    const gameCard = document.getElementById(`game-${appid}`);
    if (!gameCard) return;
    
    // Remover badges existentes
    const existingBadges = gameCard.querySelectorAll('.data-validation-badge');
    existingBadges.forEach(badge => badge.remove());
    
    // Adicionar novo badge
    const badge = document.createElement('div');
    badge.className = `data-validation-badge ${isValid ? 'valid' : 'invalid'}`;
    badge.innerHTML = `<i class="fas fa-${isValid ? 'check-circle' : 'exclamation-circle'}"></i> ${isValid ? 'Validado' : 'Inválido'}`;
    
    const header = gameCard.querySelector('.game-card-header');
    if (header) {
        header.appendChild(badge);
    }
    
    // Atualizar dados do jogo
    const game = gamesData.find(g => g.appid === appid);
    if (game) {
        game.data_validated = isValid;
        game.data_invalid = !isValid;
    }
}

// ====== FUNÇÕES AUXILIARES ======
function toggleDlcSection(appid) {
    const dlcList = document.getElementById(`dlc-list-${appid}`);
    const toggleBtn = dlcList?.previousElementSibling?.querySelector('.dlc-toggle-btn');
    
    if (!dlcList || !toggleBtn) return;
    
    if (dlcList.style.display === 'none' || dlcList.style.display === '') {
        dlcList.style.display = 'grid';
        toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i><span>Recolher</span>';
    } else {
        dlcList.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i><span>Expandir</span>';
    }
}

function toggleAllDlcSections() {
    const allExpanded = Array.from(document.querySelectorAll('.dlc-list')).every(
        list => list.style.display === 'grid'
    );
    
    document.querySelectorAll('.dlc-list').forEach(list => {
        list.style.display = allExpanded ? 'none' : 'grid';
    });
    
    document.querySelectorAll('.dlc-toggle-btn').forEach(btn => {
        btn.innerHTML = allExpanded ? 
            '<i class="fas fa-chevron-down"></i><span>Expandir</span>' :
            '<i class="fas fa-chevron-up"></i><span>Recolher</span>';
    });
}

async function refreshGameDLCs(appid) {
    try {
        showMessage(`Atualizando DLCs para o jogo ${appid}...`, 'info');
        
        const response = await fetch(`/api/dlc/${appid}/list?refresh=true&nocache=${Date.now()}`);
        const data = await response.json();
        
        if (data.success) {
            const processedData = processDLCData(data, appid);
            renderGameDLCs(appid, processedData);
            showMessage(`DLCs atualizadas para o jogo ${appid}!`, 'success');
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
    } catch (error) {
        console.error(`❌ Erro ao atualizar DLCs para ${appid}:`, error);
        showMessage(`Erro ao atualizar DLCs: ${error.message}`, 'error');
    }
}

async function refreshAllDLCs() {
    if (gamesData.length === 0) {
        showMessage('Nenhum jogo para atualizar', 'error');
        return;
    }
    
    showModal(
        'Atualizar Todas as DLCs',
        `Deseja atualizar as DLCs de todos os ${gamesData.length} jogos?<br><br>
        <span style="color: var(--warning-color);">
            <i class="fas fa-exclamation-triangle"></i> Isso pode demorar alguns minutos.
        </span>`,
        async () => {
            try {
                showMessage(`Atualizando DLCs de ${gamesData.length} jogos...`, 'info');
                
                let updatedCount = 0;
                let errorCount = 0;
                
                for (const game of gamesData) {
                    try {
                        await refreshGameDLCs(game.appid);
                        updatedCount++;
                        
                        // Pequena pausa para não sobrecarregar a API
                        await new Promise(resolve => setTimeout(resolve, 500));
                        
                    } catch (error) {
                        errorCount++;
                        console.error(`Erro ao atualizar ${game.appid}:`, error);
                    }
                }
                
                if (errorCount === 0) {
                    showMessage(`${updatedCount} jogos atualizados com sucesso!`, 'success');
                } else {
                    showMessage(`${updatedCount} atualizados, ${errorCount} com erro.`, 
                              updatedCount > 0 ? 'warning' : 'error');
                }
                
                saveToCache();
                
            } catch (error) {
                console.error('❌ Erro na atualização em massa:', error);
                showMessage(`Erro na atualização: ${error.message}`, 'error');
            }
        },
        'Atualizar Tudo'
    );
}

function searchGames() {
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    const searchResults = document.getElementById('searchResults');
    const searchCount = document.getElementById('searchCount');
    
    if (!query) {
        // Mostrar todos os jogos
        document.querySelectorAll('.game-card').forEach(card => {
            card.style.display = 'block';
        });
        searchResults.style.display = 'none';
        document.getElementById('gamesCount').textContent = gamesData.length;
        return;
    }
    
    // Filtrar jogos e DLCs
    let visibleCount = 0;
    document.querySelectorAll('.game-card').forEach(card => {
        const gameId = card.id.replace('game-', '');
        const game = gamesData.find(g => g.appid === gameId);
        
        let matches = false;
        
        if (game) {
            // Buscar no nome do jogo
            if (game.name && game.name.toLowerCase().includes(query)) {
                matches = true;
            }
            // Buscar no AppID
            else if (game.appid.includes(query)) {
                matches = true;
            }
            // Buscar no caminho
            else if (game.install_path && game.install_path.toLowerCase().includes(query)) {
                matches = true;
            }
            // Buscar nas DLCs (se a seção estiver expandida)
            else {
                const dlcList = card.querySelector('.dlc-list');
                if (dlcList && dlcList.style.display === 'grid') {
                    const dlcItems = dlcList.querySelectorAll('.dlc-item');
                    for (const dlcItem of dlcItems) {
                        const dlcName = dlcItem.querySelector('h5')?.textContent?.toLowerCase();
                        const dlcDesc = dlcItem.querySelector('.dlc-description')?.textContent?.toLowerCase();
                        if ((dlcName && dlcName.includes(query)) || (dlcDesc && dlcDesc.includes(query))) {
                            matches = true;
                            break;
                        }
                    }
                }
            }
        }
        
        card.style.display = matches ? 'block' : 'none';
        if (matches) visibleCount++;
    });
    
    // Atualizar contador de resultados
    searchCount.textContent = visibleCount;
    searchResults.style.display = 'block';
    
    // Atualizar contador de jogos
    document.getElementById('gamesCount').textContent = visibleCount;
    
    // Expandir seções que contêm resultados
    if (visibleCount > 0) {
        document.querySelectorAll('.game-card').forEach(card => {
            if (card.style.display === 'block') {
                const appid = card.dataset.appid;
                const dlcList = document.getElementById(`dlc-list-${appid}`);
                if (dlcList && query.length > 2) {
                    dlcList.style.display = 'grid';
                    const toggleBtn = dlcList.previousElementSibling?.querySelector('.dlc-toggle-btn');
                    if (toggleBtn) {
                        toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i><span>Recolher</span>';
                    }
                }
            }
        });
    }
}

async function updateStats() {
    try {
        // Atualizar estatísticas básicas
        document.getElementById('statsTotalGames').textContent = gamesData.length;
        
        // Contar jogos com DLC
        const gamesWithDLC = gamesData.filter(game => game.has_dlc).length;
        document.getElementById('statsGamesWithDLC').textContent = gamesWithDLC;
        
        // Calcular DLCs disponíveis e instaladas
        let totalAvailable = 0;
        let totalInstalled = 0;
        let totalValid = 0;
        let totalInvalid = 0;
        
        // Coletar dados de todos os jogos
        const statsPromises = gamesData.map(async (game) => {
            try {
                const response = await fetch(`/api/dlc/${game.appid}/list?cache=true`);
                const data = await response.json();
                
                if (data.success) {
                    const processed = processDLCData(data, game.appid);
                    return {
                        available: processed.total_valid,
                        installed: processed.installed_count,
                        invalid: processed.invalid_count
                    };
                }
            } catch (error) {
                console.warn(`⚠️ Erro ao coletar stats para ${game.appid}:`, error);
            }
            return { available: 0, installed: 0, invalid: 0 };
        });
        
        // Aguardar todas as promessas
        const statsResults = await Promise.all(statsPromises);
        
        // Somar totais
        statsResults.forEach(stats => {
            totalAvailable += stats.available;
            totalInstalled += stats.installed;
            totalInvalid += stats.invalid;
        });
        
        totalValid = totalAvailable;
        
        // Atualizar interface
        document.getElementById('statsAvailableDLCs').textContent = totalAvailable;
        document.getElementById('statsInstalledDLCs').textContent = totalInstalled;
        
        // Atualizar cache local
        systemCache.stats = {
            totalGames: gamesData.length,
            gamesWithDLC: gamesWithDLC,
            availableDLCs: totalAvailable,
            installedDLCs: totalInstalled,
            validDLCs: totalValid,
            invalidDLCs: totalInvalid,
            lastUpdate: Date.now()
        };
        
        saveToCache();
        
        console.log(`📊 Estatísticas: ${totalAvailable} DLCs disponíveis, ${totalInstalled} instaladas, ${totalInvalid} inválidas`);
        
    } catch (error) {
        console.error('❌ Erro ao atualizar estatísticas:', error);
    }
}

async function clearDlcCache() {
    showModal(
        'Limpar Cache do Sistema',
        `Deseja limpar TODO o cache do DLC Manager?<br><br>
        <span style="color: var(--warning-color);">
            <i class="fas fa-exclamation-triangle"></i> Isso forçará uma nova verificação completa de todos os jogos e DLCs.
        </span>`,
        async () => {
            try {
                showMessage('Limpando cache do sistema...', 'info');
                
                const response = await fetch('/api/dlc/cache/clear', {
                    method: 'POST',
                    headers: {
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Limpar cache local também
                    clearLocalCache();
                    
                    showMessage('✅ Cache limpo! Recarregando dados...', 'success');
                    
                    // Limpar dados locais
                    gamesData = [];
                    selectedDLCs = {};
                    selectedToRemove = {};
                    validationState = {
                        validating: false,
                        validatedGames: 0,
                        totalGames: 0,
                        errors: [],
                        warnings: []
                    };
                    
                    // Forçar recarregamento completo
                    setTimeout(() => {
                        loadGames(true);
                        updateStats();
                        updateGlobalCounts();
                    }, 1500);
                } else {
                    throw new Error(data.error || 'Erro desconhecido');
                }
            } catch (error) {
                console.error('❌ Erro ao limpar cache:', error);
                showMessage(`Erro ao limpar cache: ${error.message}`, 'error');
            }
        },
        'Limpar Tudo'
    );
}

async function runSystemDiagnostics() {
    try {
        showDiagnosticModal();
        
        const diagnostics = [];
        
        // Testar conexão com API
        diagnostics.push({ test: 'API Connection', status: 'running', message: 'Testando conexão...' });
        updateDiagnosticContent(diagnostics);
        
        try {
            const statusResponse = await fetch('/api/dlc/status');
            if (statusResponse.ok) {
                diagnostics[0].status = 'success';
                diagnostics[0].message = 'Conexão com API estabelecida';
            } else {
                diagnostics[0].status = 'error';
                diagnostics[0].message = `Falha na conexão: ${statusResponse.status}`;
            }
        } catch (error) {
            diagnostics[0].status = 'error';
            diagnostics[0].message = `Erro: ${error.message}`;
        }
        
        updateDiagnosticContent(diagnostics);
        
        // Testar cache do sistema
        diagnostics.push({ test: 'System Cache', status: 'running', message: 'Verificando cache...' });
        updateDiagnosticContent(diagnostics);
        
        try {
            const cacheResponse = await fetch('/api/dlc/games?cache=true');
            const cacheData = await cacheResponse.json();
            
            if (cacheData.success) {
                diagnostics[1].status = 'success';
                diagnostics[1].message = `Cache OK: ${cacheData.games?.length || 0} jogos em cache`;
            } else {
                diagnostics[1].status = 'warning';
                diagnostics[1].message = 'Cache disponível, mas com dados antigos';
            }
        } catch (error) {
            diagnostics[1].status = 'error';
            diagnostics[1].message = 'Cache indisponível';
        }
        
        updateDiagnosticContent(diagnostics);
        
        // Testar conexão com Steam API
        diagnostics.push({ test: 'Steam API', status: 'running', message: 'Testando conexão com Steam...' });
        updateDiagnosticContent(diagnostics);
        
        try {
            const steamTest = await fetch('https://store.steampowered.com/api/appdetails?appids=570');
            if (steamTest.ok) {
                const data = await steamTest.json();
                if (data['570']?.success) {
                    diagnostics[2].status = 'success';
                    diagnostics[2].message = 'Conexão com Steam API estabelecida';
                } else {
                    diagnostics[2].status = 'warning';
                    diagnostics[2].message = 'Steam API respondeu, mas com erro';
                }
            } else {
                diagnostics[2].status = 'error';
                diagnostics[2].message = 'Falha na conexão com Steam API';
            }
        } catch (error) {
            diagnostics[2].status = 'error';
            diagnostics[2].message = `Erro: ${error.message}`;
        }
        
        updateDiagnosticContent(diagnostics);
        
        // Verificar stplug-in
        diagnostics.push({ test: 'stplug-in', status: 'running', message: 'Verificando configuração...' });
        updateDiagnosticContent(diagnostics);
        
        try {
            const stplugResponse = await fetch('/api/dlc/status');
            const stplugData = await stplugResponse.json();
            
            if (stplugData.success && stplugData['stplug-in']) {
                diagnostics[3].status = 'success';
                diagnostics[3].message = 'stplug-in configurado corretamente';
            } else {
                diagnostics[3].status = 'error';
                diagnostics[3].message = 'stplug-in não encontrado ou mal configurado';
            }
        } catch (error) {
            diagnostics[3].status = 'error';
            diagnostics[3].message = 'Não foi possível verificar stplug-in';
        }
        
        updateDiagnosticContent(diagnostics);
        
        // Verificar jogos instalados
        diagnostics.push({ test: 'Installed Games', status: 'running', message: 'Verificando jogos...' });
        updateDiagnosticContent(diagnostics);
        
        try {
            const gamesResponse = await fetch('/api/dlc/games');
            const gamesData = await gamesResponse.json();
            
            if (gamesData.success && gamesData.games?.length > 0) {
                diagnostics[4].status = 'success';
                diagnostics[4].message = `${gamesData.games.length} jogos detectados`;
            } else {
                diagnostics[4].status = 'warning';
                diagnostics[4].message = 'Nenhum jogo Steam detectado';
            }
        } catch (error) {
            diagnostics[4].status = 'error';
            diagnostics[4].message = 'Erro ao detectar jogos';
        }
        
        updateDiagnosticContent(diagnostics);
        
        // Calcular score do diagnóstico
        const successCount = diagnostics.filter(d => d.status === 'success').length;
        const errorCount = diagnostics.filter(d => d.status === 'error').length;
        const warningCount = diagnostics.filter(d => d.status === 'warning').length;
        const totalTests = diagnostics.length;
        const score = Math.round((successCount / totalTests) * 100);
        
        // Adicionar resumo
        diagnostics.push({ 
            test: 'Diagnóstico Completo', 
            status: score >= 80 ? 'success' : score >= 50 ? 'warning' : 'error',
            message: `Score: ${score}% (${successCount}✓ ${warningCount}⚠ ${errorCount}✗)`
        });
        
        updateDiagnosticContent(diagnostics);
        
    } catch (error) {
        console.error('❌ Erro no diagnóstico:', error);
        showMessage(`Erro no diagnóstico: ${error.message}`, 'error');
    }
}

function updateDiagnosticContent(diagnostics) {
    const diagnosticContent = document.getElementById('diagnosticContent');
    let html = '';
    
    diagnostics.forEach((diag, index) => {
        let icon = '';
        let color = '';
        
        switch (diag.status) {
            case 'success':
                icon = 'fa-check-circle';
                color = 'var(--success-color)';
                break;
            case 'warning':
                icon = 'fa-exclamation-triangle';
                color = 'var(--warning-color)';
                break;
            case 'error':
                icon = 'fa-times-circle';
                color = 'var(--danger-color)';
                break;
            default:
                icon = 'fa-spinner fa-spin';
                color = 'var(--accent-color)';
        }
        
        html += `
            <div class="status-item">
                <span class="status-label">
                    <i class="fas ${icon}" style="color: ${color};"></i>
                    ${diag.test}:
                </span>
                <span class="status-value" style="color: ${color};">${diag.message}</span>
            </div>
        `;
    });
    
    diagnosticContent.innerHTML = html;
}

async function applyDiagnosticFix() {
    showMessage('Aplicando correções automáticas...', 'info');
    
    try {
        // Limpar cache
        await fetch('/api/dlc/cache/clear', { method: 'POST' });
        
        // Limpar cache local
        clearLocalCache();
        
        // Recarregar tudo
        await loadGames(true);
        
        showMessage('Correções aplicadas com sucesso!', 'success');
        closeDiagnosticModal();
        
    } catch (error) {
        console.error('❌ Erro ao aplicar correções:', error);
        showMessage(`Erro ao aplicar correções: ${error.message}`, 'error');
    }
}

async function showDLCInfo(appid, dlcId) {
    try {
        const response = await fetch(`/api/dlc/${appid}/list?nocache=${Date.now()}`);
        const data = await response.json();
        
        if (data.success && data.dlcs) {
            const dlc = data.dlcs.find(d => d.id === dlcId || d.appid === dlcId);
            if (dlc) {
                showModal(
                    dlc.name || `DLC ${dlcId}`,
                    `
                    <div style="text-align: left; line-height: 1.6;">
                        ${dlc.description ? `<p style="margin-bottom: 15px;">${dlc.description}</p>` : ''}
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 20px;">
                            <div style="background: rgba(0, 0, 0, 0.2); padding: 10px; border-radius: 8px;">
                                <div style="font-size: 12px; color: var(--text-muted);">Tipo</div>
                                <div style="color: var(--text-primary); font-weight: 600;">${dlc.type || 'DLC'}</div>
                            </div>
                            <div style="background: rgba(0, 0, 0, 0.2); padding: 10px; border-radius: 8px;">
                                <div style="font-size: 12px; color: var(--text-muted);">Preço</div>
                                <div style="color: ${dlc.is_free ? 'var(--success-color)' : 'var(--text-primary)'}; font-weight: 600;">
                                    ${dlc.is_free ? 'GRÁTIS' : dlc.price || 'N/A'}
                                </div>
                            </div>
                            ${dlc.release_date ? `
                                <div style="background: rgba(0, 0, 0, 0.2); padding: 10px; border-radius: 8px;">
                                    <div style="font-size: 12px; color: var(--text-muted);">Lançamento</div>
                                    <div style="color: var(--text-primary); font-weight: 600;">${new Date(dlc.release_date).toLocaleDateString('pt-BR')}</div>
                                </div>
                            ` : ''}
                            <div style="background: rgba(0, 0, 0, 0.2); padding: 10px; border-radius: 8px;">
                                <div style="font-size: 12px; color: var(--text-muted);">ID</div>
                                <div style="color: var(--text-primary); font-weight: 600; font-family: monospace;">${dlcId}</div>
                            </div>
                        </div>
                    </div>
                    `,
                    () => {},
                    'Fechar'
                );
                return;
            }
        }
        
        showMessage('Informações da DLC não disponíveis', 'warning');
        
    } catch (error) {
        console.error(`❌ Erro ao obter informações da DLC ${dlcId}:`, error);
        showMessage('Erro ao carregar informações', 'error');
    }
}

// ====== INTEGRAÇÃO COM HEADER/SIDEBAR ======
window.DLCManager = {
    ready: function() {
        console.log('✅ DLCManager Pro integrado com header/sidebar');
        document.getElementById('initLoader').style.display = 'none';
        loadGames();
    },
    
    refresh: function() {
        loadGames(true);
    },
    
    getStatus: function() {
        return {
            totalGames: gamesData.length,
            selectedDLCs: Object.values(selectedDLCs).flat().length,
            selectedToRemove: Object.values(selectedToRemove).flat().length,
            ready: gamesData.length > 0,
            validated: systemCache.validated,
            version: 'v10.1'
        };
    },
    
    runDiagnostics: function() {
        runSystemDiagnostics();
    },
    
    validateData: function() {
        validateAllGamesData();
    }
};

// Expor funções para header/sidebar
window.navigateTo = function(destination) {
    if (destination === 'dlc') {
        loadGames(true);
        if (typeof showNotification === 'function') {
            showNotification('DLC Manager Pro', 'Atualizando lista de jogos...', 'info');
        }
    }
};

console.log('✅ DLC Manager Pro HTML carregado e configurado');