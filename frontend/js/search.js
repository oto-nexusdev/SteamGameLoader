// frontend/js/search.js - Sistema de busca modularizado e otimizado
// VERSÃO 2.0 - COM SISTEMA DE NOTIFICAÇÃO UNIFICADO

// ====== CONFIGURAÇÕES GLOBAIS UNIFICADAS ======
const SearchConfig = {
    API_BASE: '/api',
    INSTALLATION_CACHE_KEY: 'steam_gameloader_installed_games',
    SEARCH_MIN_CHARS: 2,
    MAX_NOTIFICATIONS: 4
};

// ====== ESTADO GLOBAL ======
const SearchState = {
    user: null,
    results: [],
    installedGames: new Set(),
    currentSearchQuery: '',
    isSystemReady: false,
    activeInstallations: new Set(),
    isDarkMode: localStorage.getItem('darkMode') === 'true'
};

// ====== SISTEMA DE BUSCA ======
class SearchSystem {
    constructor() {
        this.searchTimeout = null;
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.elements = {
            searchInput: document.getElementById('searchInput'),
            btnSearch: document.getElementById('btnSearch'),
            btnInstallZip: document.getElementById('btnInstallZip'),
            btnClearResults: document.getElementById('btnClearResults'),
            zipFileInput: document.getElementById('zipFileInput'),
            zipUploadArea: document.getElementById('zipUploadArea'),
            resultsGrid: document.getElementById('resultsGrid'),
            loadingState: document.getElementById('loadingState'),
            systemStatusText: document.getElementById('systemStatusText'),
            resultsCount: document.getElementById('resultsCount')
        };
    }
    
    setupEventListeners() {
        const { searchInput, btnSearch, btnInstallZip, zipFileInput, zipUploadArea, btnClearResults } = this.elements;
        
        // Busca com Enter
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch();
                }
            });
            
            // Busca automática com debounce
            searchInput.addEventListener('input', () => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    if (searchInput.value.length >= SearchConfig.SEARCH_MIN_CHARS) {
                        this.performSearch();
                    }
                }, 800);
            });
        }
        
        // Botão de busca
        if (btnSearch) {
            btnSearch.addEventListener('click', () => this.performSearch());
        }
        
        // Upload ZIP
        if (btnInstallZip) {
            btnInstallZip.addEventListener('click', () => {
                if (SearchState.isSystemReady) {
                    zipFileInput.click();
                } else {
                    this.showNotification('Sistema não pronto', 
                        'Aguarde o sistema carregar completamente', 'warning');
                }
            });
        }
        
        if (zipFileInput) {
            zipFileInput.addEventListener('change', (e) => this.handleZipUpload(e));
        }
        
        // Drag and drop
        if (zipUploadArea) {
            zipUploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (SearchState.isSystemReady) {
                    zipUploadArea.classList.add('dragover');
                }
            });
            
            zipUploadArea.addEventListener('dragleave', () => {
                zipUploadArea.classList.remove('dragover');
            });
            
            zipUploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                zipUploadArea.classList.remove('dragover');
                
                if (!SearchState.isSystemReady) {
                    this.showNotification('Sistema não pronto', 
                        'Aguarde o sistema carregar completamente', 'warning');
                    return;
                }
                
                if (e.dataTransfer.files.length > 0) {
                    const file = e.dataTransfer.files[0];
                    if (file.name.toLowerCase().endsWith('.zip')) {
                        this.handleZipFile(file);
                    } else {
                        this.showNotification('Arquivo inválido', 
                            'Por favor, selecione um arquivo ZIP válido', 'error');
                    }
                }
            });
            
            zipUploadArea.addEventListener('click', () => {
                if (SearchState.isSystemReady) {
                    zipFileInput.click();
                }
            });
        }
        
        // Limpar resultados
        if (btnClearResults) {
            btnClearResults.addEventListener('click', () => {
                if (SearchState.results.length > 0) {
                    if (confirm('Tem certeza que deseja limpar todos os resultados?')) {
                        this.clearResults();
                    }
                }
            });
        }
        
        // Modo escuro
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', this.toggleDarkMode);
        }
    }
    
    async performSearch() {
        const { searchInput, btnSearch } = this.elements;
        const query = searchInput ? searchInput.value.trim() : '';
        
        if (!query || query.length < SearchConfig.SEARCH_MIN_CHARS) {
            this.showNotification('Busca', 
                `Digite pelo menos ${SearchConfig.SEARCH_MIN_CHARS} caracteres para buscar`, 'warning');
            return;
        }
        
        if (!SearchState.isSystemReady) {
            this.showNotification('Sistema carregando', 
                'Aguarde o sistema estar completamente pronto', 'warning');
            return;
        }
        
        // Atualizar estado
        SearchState.currentSearchQuery = query;
        
        // Atualizar URL
        const newUrl = window.location.pathname + '?q=' + encodeURIComponent(query);
        window.history.pushState({ path: newUrl }, '', newUrl);
        
        // Mostrar loading
        this.showLoading(true);
        
        // Desabilitar botão
        if (btnSearch) {
            btnSearch.disabled = true;
            btnSearch.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Buscando...</span>';
        }
        
        try {
            console.log(`🔍 Buscando jogos para: "${query}"`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000);
            
            const response = await fetch(`${SearchConfig.API_BASE}/search/games?q=${encodeURIComponent(query)}`, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`API retornou ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.results && data.results.length > 0) {
                SearchState.results = data.results;
                
                // Verificar instalações
                await this.verifyInstallationsForResults(data.results);
                
                this.displayResults(data.results);
                this.updateStatistics(data.results);
                
                this.showNotification('✅ Busca Concluída', 
                    `Encontrados ${data.results.length} jogos para "${query}"`, 'success');
                    
            } else {
                const errorMsg = data.error || data.message || 'Nenhum resultado encontrado';
                this.showNotification('🔍 Sem Resultados', errorMsg, 'info');
                
                this.showEmptyState('Nenhum resultado encontrado', 
                    `Tente buscar por outro termo: "${query}"`);
                this.updateStatistics([]);
            }
            
            // Atualizar status do sistema
            if (data.download_system_ready !== undefined) {
                this.updateSystemStatusText(data.download_system_ready);
            }
            
        } catch (error) {
            console.error('❌ Erro na busca:', error);
            
            let errorMessage = 'Não foi possível conectar ao servidor de busca';
            if (error.name === 'AbortError') {
                errorMessage = 'A busca demorou muito tempo. Tente novamente.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Erro de rede. Verifique sua conexão com a internet.';
            }
            
            this.showNotification('🌐 Erro de Conexão', errorMessage, 'error');
            
            this.showEmptyState('Erro de conexão', 
                'Verifique sua conexão com a internet e tente novamente');
            this.updateStatistics([]);
            
        } finally {
            this.showLoading(false);
            
            // Reabilitar botão
            const { btnSearch } = this.elements;
            if (btnSearch) {
                btnSearch.disabled = false;
                btnSearch.innerHTML = '<i class="fas fa-search"></i><span>Buscar Jogos</span>';
            }
        }
    }
    
    async verifyInstallationsForResults(results) {
        if (!results || results.length === 0) return;
        
        console.log(`🔍 Verificando instalações para ${results.length} jogos...`);
        
        const cachedInstallations = this.getCachedInstallations();
        
        for (const game of results) {
            const appid = game.appid?.toString();
            if (!appid) continue;
            
            // Verificar cache primeiro
            if (cachedInstallations.has(appid)) {
                game.installed = true;
                game.installation_verified = true;
                SearchState.installedGames.add(appid);
                continue;
            }
            
            // Verificar via API
            try {
                const response = await fetch(`${SearchConfig.API_BASE}/game/${appid}/install-status`);
                if (response.ok) {
                    const data = await response.json();
                    if (data.installed) {
                        game.installed = true;
                        game.installation_verified = true;
                        SearchState.installedGames.add(appid);
                        this.saveToInstallationCache(appid);
                    } else {
                        game.installed = false;
                        game.installation_verified = true;
                    }
                }
            } catch (error) {
                console.warn(`⚠️ Erro verificando instalação ${appid}:`, error);
                game.installed = false;
                game.installation_verified = false;
            }
        }
        
        // Atualizar estatísticas
        document.getElementById('stat-installed').textContent = SearchState.installedGames.size;
    }
    
    displayResults(results) {
        const { resultsGrid, btnClearResults } = this.elements;
        
        if (!results || results.length === 0) {
            this.showEmptyState('Nenhum resultado encontrado', 'Tente buscar por outro nome ou termo');
            if (btnClearResults) btnClearResults.style.display = 'none';
            return;
        }
        
        // Mostrar botão de limpar
        if (btnClearResults) btnClearResults.style.display = 'inline-flex';
        
        // Atualizar contador
        if (this.elements.resultsCount) {
            this.elements.resultsCount.textContent = `${results.length} ${results.length === 1 ? 'jogo' : 'jogos'}`;
        }
        
        // Limpar grid
        resultsGrid.innerHTML = '';
        
        // Renderizar resultados
        results.forEach((game, index) => {
            const gameCard = this.createGameCard(game, index);
            resultsGrid.appendChild(gameCard);
        });
    }
    
    createGameCard(game, index) {
        const isInstalled = game.installed === true;
        const isFree = game.is_free || false;
        const hasImage = game.header_image || game.image;
        const appid = game.appid?.toString() || '';
        
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card-search';
        gameCard.dataset.appid = appid;
        gameCard.dataset.index = index;
        
        // Imagem
        const imageHtml = hasImage ? 
            `<div class="game-image">
                <img src="${this.escapeHtml(game.header_image || game.image)}" 
                     alt="${this.escapeHtml(game.name)}"
                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjE4MCIgdmlld0JveD0iMCAwIDMyMCAxODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjMyMCIgaGVpZ2h0PSIxODAiIGZpbGw9InJnYmEoMjAsMTUsMzUsMC45KSIvPjx0ZXh0IHg9IjE2MCIgeT0iOTAiIGZvbnQtZmFtaWx5PSJJbnRlciIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPiR7dGhpcy5lc2NhcGVIdG1sKGdhbWUubmFtZSl9PC90ZXh0Pjwvc3ZnPmc='">
            </div>` : '';
        
        // Botão de instalação
        const installButtonHtml = isInstalled ? 
            '<i class="fas fa-check"></i><span>Instalado</span>' : 
            '<i class="fas fa-download"></i><span>Instalar Agora</span>';
        
        const installButtonClass = isInstalled ? 'installed' : '';
        const installButtonDisabled = isInstalled ? 'disabled' : '';
        
        gameCard.innerHTML = `
            ${imageHtml}
            <div class="game-header">
                <div class="game-title">
                    <div class="game-title-text" title="${this.escapeHtml(game.name)}">
                        ${this.escapeHtml(game.name)}
                    </div>
                    ${isFree ? '<span class="free-badge-search">GRÁTIS</span>' : ''}
                </div>
                <div class="game-meta">
                    <span>AppID: ${game.appid || 'N/A'}</span>
                    <span>•</span>
                    <span>${this.escapeHtml(game.platforms_formatted || game.platforms || 'Windows')}</span>
                    ${game.developer ? `<span>•</span><span>${this.escapeHtml(game.developer)}</span>` : ''}
                </div>
            </div>
            <div class="game-body">
                ${game.short_description ? 
                    `<div class="game-description">
                        ${this.escapeHtml(game.short_description.substring(0, 120))}${game.short_description.length > 120 ? '...' : ''}
                    </div>` : ''}
                
                <div class="game-price">
                    ${isFree ? 'GRATUITO' : (game.price?.formatted || game.price || 'Consultar')}
                </div>
                <div class="game-actions">
                    <button class="install-btn-search ${installButtonClass}" 
                            data-appid="${appid}"
                            ${installButtonDisabled}
                            onclick="window.searchSystem.installGame('${appid}', this)">
                        ${installButtonHtml}
                    </button>
                    <button class="details-btn" onclick="window.searchSystem.showGameDetailsModal('${appid}')">
                        <i class="fas fa-info-circle"></i>
                        <span>Detalhes</span>
                    </button>
                </div>
            </div>
        `;
        
        return gameCard;
    }
    
    async installGame(appid, button) {
        if (!appid || !button) return;
        
        // Verificar se já está instalando
        if (SearchState.activeInstallations.has(appid)) {
            this.showNotification('⏳ Instalação em andamento', 
                'Este jogo já está sendo instalado', 'warning');
            return;
        }
        
        // Adicionar à lista de instalações ativas
        SearchState.activeInstallations.add(appid);
        
        // Atualizar estado do botão
        const originalText = button.innerHTML;
        const originalClass = button.className;
        button.disabled = true;
        button.classList.add('installing');
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Instalando...</span>';
        
        // Encontrar o jogo
        const game = SearchState.results.find(g => g.appid == appid);
        const gameName = game?.name || `Jogo ${appid}`;
        
        try {
            this.showNotification('🚀 Iniciando Instalação', 
                `Preparando instalação de ${this.escapeHtml(gameName)}...`, 'info');
            
            const response = await fetch(`${SearchConfig.API_BASE}/game/${appid}/download`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ 
                    appid: appid,
                    force_download: true,
                    timestamp: new Date().toISOString()
                })
            });
            
            const data = await response.json();
            console.log('📥 Resposta do download:', data);
            
            if (data.success) {
                if (data.download_completed === true) {
                    button.classList.remove('installing');
                    button.classList.add('installed');
                    button.innerHTML = '<i class="fas fa-check"></i><span>Instalado</span>';
                    button.disabled = true;
                    
                    // Atualizar cache
                    this.saveToInstallationCache(appid);
                    SearchState.installedGames.add(appid.toString());
                    document.getElementById('stat-installed').textContent = SearchState.installedGames.size;
                    
                    // Atualizar objeto do jogo
                    const gameIndex = SearchState.results.findIndex(g => g.appid == appid);
                    if (gameIndex !== -1) {
                        SearchState.results[gameIndex].installed = true;
                        SearchState.results[gameIndex].installation_verified = true;
                    }
                    
                    this.showNotification('✅ Download Concluído', 
                        `${this.escapeHtml(gameName)} instalado com sucesso!`, 'success');
                    
                    this.updateStatistics(SearchState.results);
                    
                } else if (data.already_installed === true) {
                    button.classList.remove('installing');
                    button.classList.add('installed');
                    button.innerHTML = '<i class="fas fa-check"></i><span>Instalado</span>';
                    button.disabled = true;
                    
                    this.saveToInstallationCache(appid);
                    SearchState.installedGames.add(appid.toString());
                    document.getElementById('stat-installed').textContent = SearchState.installedGames.size;
                    
                    this.showNotification('✅ Jogo já instalado', 
                        `${this.escapeHtml(gameName)} já estava instalado no sistema`, 'info');
                    
                } else {
                    button.disabled = false;
                    button.classList.remove('installing');
                    button.className = originalClass;
                    button.innerHTML = originalText;
                    
                    this.showNotification('⚠️ Download Iniciado', 
                        `${this.escapeHtml(gameName)} - Download em processamento`, 'warning');
                    
                    setTimeout(() => {
                        this.verifySingleInstallation(appid);
                    }, 5000);
                }
                
            } else {
                button.disabled = false;
                button.classList.remove('installing');
                button.className = originalClass;
                button.innerHTML = originalText;
                
                const errorMessage = data.error || data.message || 'Falha ao instalar o jogo';
                this.showNotification('❌ Erro na Instalação', 
                    `${this.escapeHtml(gameName)} - ${errorMessage}`, 'error');
            }
            
        } catch (error) {
            console.error('❌ Erro na instalação:', error);
            
            button.disabled = false;
            button.classList.remove('installing');
            button.className = originalClass;
            button.innerHTML = originalText;
            
            this.showNotification('🌐 Erro de Rede', 
                `Não foi possível conectar ao servidor para instalar ${this.escapeHtml(gameName)}`, 'error');
            
        } finally {
            SearchState.activeInstallations.delete(appid);
        }
    }
    
    async verifySingleInstallation(appid) {
        try {
            const response = await fetch(`${SearchConfig.API_BASE}/game/${appid}/install-status`);
            if (response.ok) {
                const data = await response.json();
                if (data.installed) {
                    console.log(`✅ Verificação: Jogo ${appid} está instalado`);
                    
                    this.saveToInstallationCache(appid);
                    SearchState.installedGames.add(appid.toString());
                    document.getElementById('stat-installed').textContent = SearchState.installedGames.size;
                    
                    const button = document.querySelector(`.install-btn-search[data-appid="${appid}"]`);
                    if (button && !button.classList.contains('installed')) {
                        button.classList.remove('installing');
                        button.classList.add('installed');
                        button.innerHTML = '<i class="fas fa-check"></i><span>Instalado</span>';
                        button.disabled = true;
                    }
                    
                    const gameIndex = SearchState.results.findIndex(g => g.appid == appid);
                    if (gameIndex !== -1) {
                        SearchState.results[gameIndex].installed = true;
                        SearchState.results[gameIndex].installation_verified = true;
                    }
                    
                    const game = SearchState.results.find(g => g.appid == appid);
                    const gameName = game?.name || `Jogo ${appid}`;
                    
                    this.showNotification('✅ Instalação Verificada', 
                        `${this.escapeHtml(gameName)} foi instalado com sucesso!`, 'success');
                }
            }
        } catch (error) {
            console.warn(`⚠️ Erro verificando instalação ${appid}:`, error);
        }
    }
    
    // ====== MANIPULAÇÃO ZIP ======
    async handleZipUpload(event) {
        const file = event.target.files[0];
        if (file) {
            await this.handleZipFile(file);
        }
        event.target.value = '';
    }
    
    async handleZipFile(file) {
        if (!file.name.toLowerCase().endsWith('.zip')) {
            this.showNotification('❌ Arquivo inválido', 
                'Por favor, selecione um arquivo ZIP válido', 'error');
            return;
        }
        
        if (file.size > 500 * 1024 * 1024) {
            this.showNotification('📦 Arquivo muito grande', 
                'O arquivo ZIP deve ter menos de 500MB', 'warning');
            return;
        }
        
        const formData = new FormData();
        formData.append('zip_file', file);
        
        const zipProgress = document.getElementById('zipProgress');
        const zipProgressBar = document.getElementById('zipProgressBar');
        const zipStatus = document.getElementById('zipStatus');
        const zipUploadArea = document.getElementById('zipUploadArea');
        
        // Desabilitar área de upload
        if (zipUploadArea) {
            zipUploadArea.style.cursor = 'wait';
            zipUploadArea.style.opacity = '0.7';
        }
        
        if (zipProgress) zipProgress.style.display = 'block';
        if (zipProgressBar) zipProgressBar.style.width = '10%';
        if (zipStatus) zipStatus.textContent = 'Preparando upload...';
        
        try {
            const progressInterval = setInterval(() => {
                if (zipProgressBar) {
                    const currentWidth = parseInt(zipProgressBar.style.width);
                    if (currentWidth < 70) {
                        zipProgressBar.style.width = (currentWidth + 10) + '%';
                    }
                }
            }, 300);
            
            const response = await fetch(`${SearchConfig.API_BASE}/upload/zip`, {
                method: 'POST',
                body: formData
            });
            
            clearInterval(progressInterval);
            
            if (zipProgressBar) zipProgressBar.style.width = '80%';
            if (zipStatus) zipStatus.textContent = 'Processando arquivo...';
            
            const data = await response.json();
            
            if (zipProgressBar) zipProgressBar.style.width = '100%';
            
            if (data.success) {
                if (zipStatus) {
                    zipStatus.innerHTML = `
                        <span style="color: #00ff88;">✅ Instalação via ZIP concluída!</span>
                        <div style="margin-top: 10px; font-size: 13px;">
                            <strong>Arquivo:</strong> ${this.escapeHtml(data.filename || file.name)}<br>
                            <strong>Arquivos processados:</strong> ${data.valid_files_found || data.files_processed || 0}
                        </div>
                    `;
                }
                
                this.showNotification('📦 ZIP Instalado', 
                    `${data.valid_files_found || data.files_processed || 0} arquivos processados com sucesso!`, 'success');
                
                setTimeout(() => {
                    this.loadInstallationCache();
                    if (SearchState.currentSearchQuery && SearchState.results.length > 0) {
                        setTimeout(() => this.verifyInstallationsForResults(SearchState.results), 2000);
                    }
                }, 2000);
                
            } else {
                if (zipStatus) {
                    zipStatus.innerHTML = `<span style="color: #ff2a6d;">❌ Erro: ${this.escapeHtml(data.error || 'Falha desconhecida')}</span>`;
                }
                this.showNotification('❌ Erro no ZIP', 
                    data.error || 'Falha ao processar o arquivo', 'error');
            }
            
            setTimeout(() => {
                if (zipProgress) zipProgress.style.display = 'none';
                if (zipProgressBar) zipProgressBar.style.width = '0%';
                if (zipStatus) zipStatus.textContent = '';
            }, 5000);
            
        } catch (error) {
            console.error('❌ Erro no upload ZIP:', error);
            
            if (zipStatus) {
                zipStatus.innerHTML = `<span style="color: #ff2a6d;">❌ Erro de rede: ${this.escapeHtml(error.message)}</span>`;
            }
            
            this.showNotification('🌐 Erro de Rede', 'Não foi possível enviar o arquivo', 'error');
            
        } finally {
            if (zipUploadArea) {
                zipUploadArea.style.cursor = 'pointer';
                zipUploadArea.style.opacity = '1';
            }
        }
    }
    
    // ====== MODAL DE DETALHES ======
    showGameDetailsModal(appid) {
        const game = SearchState.results.find(g => g.appid == appid);
        if (!game) {
            this.showNotification('❌ Jogo não encontrado', 
                'Os detalhes deste jogo não estão disponíveis', 'error');
            return;
        }
        
        this.closeGameDetailsModal();
        
        const modalContent = document.getElementById('gameDetailsContent');
        const isInstalled = game.installed === true;
        const isFree = game.is_free || false;
        const gameName = game.name || `Jogo ${appid}`;
        
        modalContent.innerHTML = `
            <button class="game-details-close" onclick="window.searchSystem.closeGameDetailsModal()" id="modalCloseBtn">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="game-details-main">
                ${game.header_image ? 
                    `<div class="game-details-image">
                        <img src="${this.escapeHtml(game.header_image)}" 
                             alt="${this.escapeHtml(gameName)}"
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIwIiBoZWlnaHQ9IjE4MCIgdmlld0JveD0iMCAwIDMyMCAxODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjMyMCIgaGVpZ2h0PSIxODAiIGZpbGw9InJnYmEoMjAsMTUsMzUsMC45KSIvPjx0ZXh0IHg9IjE2MCIgeT0iOTAiIGZvbnQtZmFtaWx5PSJJbnRlciIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPiR7dGhpcy5lc2NhcGVIdG1sKGdhbWVOYW1lKX08L3RleHQ+PC9zdmc+Zmc='">
                    </div>` : ''}
                
                <div class="game-details-info">
                    <h2>${this.escapeHtml(gameName)}</h2>
                    
                    <div class="game-details-badges">
                        <div class="badge appid-badge">
                            <i class="fas fa-hashtag"></i>
                            <span>AppID: ${appid}</span>
                        </div>
                        
                        ${isFree ? 
                            `<div class="badge free-badge">
                                <i class="fas fa-gift"></i>
                                <span>GRÁTIS</span>
                            </div>` : 
                            `<div class="badge price-badge">
                                <i class="fas fa-tag"></i>
                                <span>${game.price?.formatted || game.price || 'Consultar'}</span>
                            </div>`}
                        
                        <div class="badge ${isInstalled ? 'installed-badge' : 'not-installed-badge'}">
                            <i class="fas fa-${isInstalled ? 'check' : 'times'}"></i>
                            <span>${isInstalled ? 'Instalado' : 'Não instalado'}</span>
                        </div>
                    </div>
                    
                    <div class="game-details-meta">
                        <div class="meta-item">
                            <i class="fas fa-desktop"></i>
                            <span>${this.escapeHtml(game.platforms_formatted || game.platforms || 'Windows')}</span>
                        </div>
                        
                        ${game.developer ? `
                            <div class="meta-item">
                                <i class="fas fa-code"></i>
                                <span>${this.escapeHtml(game.developer)}</span>
                            </div>` : ''}
                        
                        ${game.publisher ? `
                            <div class="meta-item">
                                <i class="fas fa-building"></i>
                                <span>${this.escapeHtml(game.publisher)}</span>
                            </div>` : ''}
                        
                        ${game.release_date ? `
                            <div class="meta-item">
                                <i class="fas fa-calendar-alt"></i>
                                <span>${this.escapeHtml(game.release_date.date || game.release_date)}</span>
                            </div>` : ''}
                    </div>
                </div>
            </div>
            
            ${game.short_description ? `
                <div class="game-details-description">
                    <h3><i class="fas fa-align-left"></i> Descrição</h3>
                    <p>${this.escapeHtml(game.short_description)}</p>
                </div>` : ''}
            
            <div class="game-details-actions">
                <button onclick="window.searchSystem.installGameFromModal('${appid}')" 
                        class="install-btn-modal ${isInstalled ? 'installed' : ''}"
                        ${isInstalled ? 'disabled' : ''}
                        id="modalInstallBtn">
                    <i class="fas fa-${isInstalled ? 'check' : 'download'}"></i>
                    ${isInstalled ? 'Jogo Instalado' : 'Instalar Agora'}
                </button>
                
                <button onclick="window.open('https://store.steampowered.com/app/${appid}', '_blank')"
                        class="steam-btn">
                    <i class="fas fa-external-link-alt"></i>
                    <span>Ver na Steam</span>
                </button>
                
                <button onclick="window.searchSystem.closeGameDetailsModal()"
                        class="close-btn">
                    <i class="fas fa-times"></i>
                    <span>Fechar</span>
                </button>
            </div>
        `;
        
        setTimeout(() => {
            const modal = document.getElementById('gameDetailsModal');
            const modalContent = document.getElementById('gameDetailsContent');
            
            if (modal && modalContent) {
                modal.addEventListener('click', function(e) {
                    if (e.target === this) {
                        window.searchSystem.closeGameDetailsModal();
                    }
                });
                
                modalContent.addEventListener('click', function(e) {
                    e.stopPropagation();
                });
            }
        }, 10);
        
        document.getElementById('gameDetailsModal').style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    installGameFromModal(appid) {
        const installBtn = document.getElementById('modalInstallBtn');
        if (installBtn && !installBtn.disabled) {
            this.installGame(appid, installBtn);
        }
    }
    
    closeGameDetailsModal() {
        const modal = document.getElementById('gameDetailsModal');
        if (modal) {
            modal.style.display = 'none';
            const newModal = modal.cloneNode(true);
            modal.parentNode.replaceChild(newModal, modal);
        }
        
        document.body.style.overflow = 'auto';
    }
    
    // ====== UTILITÁRIOS ======
    showEmptyState(message, title = 'Nenhuma busca realizada') {
        const { resultsGrid, btnClearResults } = this.elements;
        
        resultsGrid.innerHTML = `
            <div class="search-empty">
                <i class="fas fa-search"></i>
                <h3>${this.escapeHtml(title)}</h3>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
        
        if (btnClearResults) btnClearResults.style.display = 'none';
        
        if (this.elements.resultsCount) {
            this.elements.resultsCount.textContent = '0 jogos';
        }
    }
    
    updateStatistics(results) {
        const gamesFound = results.length || 0;
        const freeGames = results.filter(g => g.is_free).length || 0;
        
        document.getElementById('stat-games-found').textContent = gamesFound;
        document.getElementById('stat-free-games').textContent = freeGames;
        document.getElementById('stat-installed').textContent = SearchState.installedGames.size;
        
        const totalSize = results.reduce((acc, game) => {
            if (game.is_free) return acc + 3;
            if (game.name?.toLowerCase().includes('detroit')) return acc + 60;
            if (game.name?.toLowerCase().includes('cyberpunk')) return acc + 70;
            return acc + 20;
        }, 0);
        
        document.getElementById('stat-total-size').textContent = `${Math.round(totalSize)} GB`;
    }
    
    showLoading(show) {
        const { loadingState, resultsGrid } = this.elements;
        
        if (show) {
            if (loadingState) loadingState.style.display = 'block';
            if (resultsGrid) resultsGrid.innerHTML = '';
        } else {
            if (loadingState) loadingState.style.display = 'none';
        }
    }
    
    clearResults() {
        SearchState.results = [];
        this.showEmptyState('Digite o nome de um jogo acima para começar', 'Nenhuma busca realizada');
        this.updateStatistics([]);
        
        const { searchInput } = this.elements;
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
        }
        
        window.history.pushState({ path: '/search' }, '', '/search');
        
        this.showNotification('🧹 Resultados Limpos', 
            'Todos os resultados foram removidos', 'info');
    }
    
    updateSystemStatusText(isAvailable) {
        const { systemStatusText } = this.elements;
        if (systemStatusText) {
            if (isAvailable === undefined) {
                systemStatusText.innerHTML = '<i class="fas fa-sync fa-spin"></i> Verificando sistema...';
            } else if (isAvailable) {
                systemStatusText.innerHTML = '<i class="fas fa-check-circle"></i> Sistema de busca online e pronto';
                SearchState.isSystemReady = true;
            } else {
                systemStatusText.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Sistema de busca offline';
                SearchState.isSystemReady = false;
            }
        }
    }
    
    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        SearchState.isDarkMode = !SearchState.isDarkMode;
        localStorage.setItem('darkMode', SearchState.isDarkMode);
        
        const icon = document.querySelector('#darkModeToggle i');
        if (icon) {
            icon.className = SearchState.isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        this.showNotification('🎨 Tema', 
            `Modo ${SearchState.isDarkMode ? 'claro' : 'escuro'} ativado`, 'info');
    }
    
    showNotification(title, message, type = 'info', duration = 7000) {
        // Usar o sistema unificado de notificações
        if (window.unifiedNotifications && typeof window.unifiedNotifications.show === 'function') {
            return window.unifiedNotifications.show(title, message, type, duration);
        } else {
            // Fallback: usar alert simples
            console.log(`🔔 [${type.toUpperCase()}] ${title}: ${message}`);
            alert(`${title}: ${message}`);
            return null;
        }
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    }
    
    // ====== CACHE DE INSTALAÇÃO ======
    loadInstallationCache() {
        try {
            const cached = localStorage.getItem(SearchConfig.INSTALLATION_CACHE_KEY);
            if (cached) {
                const parsed = JSON.parse(cached);
                if (Array.isArray(parsed)) {
                    parsed.forEach(appid => SearchState.installedGames.add(appid));
                    document.getElementById('stat-installed').textContent = SearchState.installedGames.size;
                    console.log(`✅ Cache carregado: ${SearchState.installedGames.size} jogos instalados`);
                }
            }
        } catch (error) {
            console.warn('⚠️ Erro carregando cache:', error);
            SearchState.installedGames.clear();
        }
    }
    
    saveToInstallationCache(appid) {
        try {
            const cached = localStorage.getItem(SearchConfig.INSTALLATION_CACHE_KEY);
            let installations = cached ? JSON.parse(cached) : [];
            
            if (!installations.includes(appid)) {
                installations.push(appid);
                localStorage.setItem(SearchConfig.INSTALLATION_CACHE_KEY, JSON.stringify(installations));
                console.log(`✅ AppID ${appid} salvo no cache`);
            }
        } catch (error) {
            console.warn('⚠️ Erro salvando no cache:', error);
        }
    }
    
    getCachedInstallations() {
        try {
            const cached = localStorage.getItem(SearchConfig.INSTALLATION_CACHE_KEY);
            if (cached) {
                const parsed = JSON.parse(cached);
                return new Set(parsed);
            }
        } catch (error) {
            console.warn('⚠️ Erro obtendo cache:', error);
        }
        return new Set();
    }
    
    clearInstallationCache() {
        if (confirm('Tem certeza que deseja limpar o cache de instalação? Isso resetará o status de todos os jogos.')) {
            localStorage.removeItem(SearchConfig.INSTALLATION_CACHE_KEY);
            SearchState.installedGames.clear();
            document.getElementById('stat-installed').textContent = '0';
            
            document.querySelectorAll('.install-btn-search.installed').forEach(button => {
                button.classList.remove('installed');
                button.innerHTML = '<i class="fas fa-download"></i><span>Instalar Agora</span>';
                button.disabled = false;
            });
            
            SearchState.results.forEach(game => {
                game.installed = false;
                game.installation_verified = false;
            });
            
            this.showNotification('🧹 Cache Limpo', 
                'Status de instalação resetado. Os botões foram reativados.', 'info');
        }
    }
}

// ====== INICIALIZAÇÃO ======
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🎮 Sistema de busca inicializando...');
    
    // Inicializar sistema de busca (SEM sistema de notificação interno)
    window.searchSystem = new SearchSystem();
    
    // Configurar modo escuro inicial
    if (SearchState.isDarkMode) {
        document.body.classList.add('dark-mode');
        const icon = document.querySelector('#darkModeToggle i');
        if (icon) icon.className = 'fas fa-sun';
    }
    
    // Carregar componentes
    await loadComponents();
    
    // Verificar status do sistema
    await checkSystemStatus();
    
    // Carregar cache de instalações
    window.searchSystem.loadInstallationCache();
    
    // Verificar parâmetro de busca na URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('q');
    if (searchQuery && searchQuery.length >= SearchConfig.SEARCH_MIN_CHARS) {
        const { searchInput } = window.searchSystem.elements;
        if (searchInput) {
            searchInput.value = searchQuery;
            SearchState.currentSearchQuery = searchQuery;
            setTimeout(() => window.searchSystem.performSearch(), 500);
        }
    } else {
        window.searchSystem.showEmptyState('Digite o nome de um jogo acima para começar', 'Nenhuma busca realizada');
    }
    
    console.log('✅ Sistema de busca inicializado');
});

// ====== CARREGAMENTO DE COMPONENTES ======
async function loadComponents() {
    try {
        console.log('🔧 Carregando componentes...');
        
        // Carregar Header
        await loadHeader();
        
        // Carregar Sidebar
        try {
            const sidebarResponse = await fetch('/sidebar.html');
            if (sidebarResponse.ok) {
                document.getElementById('sidebar-container').innerHTML = await sidebarResponse.text();
                console.log('✅ Sidebar carregado');
                setTimeout(() => {
                    if (typeof initializeSidebar === 'function') initializeSidebar();
                }, 100);
            }
        } catch (e) {
            console.warn('Sidebar não carregado:', e);
            createFallbackSidebar();
        }
        
        // Carregar Footer
        try {
            const footerResponse = await fetch('/footer.html');
            if (footerResponse.ok) {
                document.getElementById('footer-container').innerHTML = await footerResponse.text();
                console.log('✅ Footer carregado');
            }
        } catch (e) {
            console.log('Footer error:', e);
            createFallbackFooter();
        }
        
        // Configurar menu mobile
        setupMobileMenu();
        
    } catch (error) {
        console.error('❌ Erro ao carregar componentes:', error);
        createFallbackSidebar();
        createFallbackFooter();
    }
}

async function loadHeader() {
    console.log('📥 Carregando header...');
    try {
        const headerResponse = await fetch('/header.html');
        if (headerResponse.ok) {
            const headerHtml = await headerResponse.text();
            const headerWithScript = processHeaderHtml(headerHtml);
            
            document.getElementById('header-container').innerHTML = headerWithScript.html;
            
            if (headerWithScript.script) {
                console.log('🚀 Executando script do header...');
                executeHeaderScript(headerWithScript.script);
            }
            
            console.log('✅ Header carregado e inicializado');
            
            setTimeout(checkAndInitializeHeader, 500);
        } else {
            console.error('❌ Header não encontrado');
            throw new Error('Header não encontrado');
        }
    } catch (e) {
        console.error('❌ ERRO CRÍTICO: Header não carregado:', e);
        throw new Error('Header é obrigatório - sistema não pode continuar');
    }
}

function processHeaderHtml(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    const scriptTags = doc.querySelectorAll('script');
    let headerScript = '';
    
    scriptTags.forEach(script => {
        if (script.textContent.includes('Steam GameLoader Header')) {
            headerScript = script.textContent;
            script.remove();
        }
    });
    
    return {
        html: doc.body.innerHTML,
        script: headerScript
    };
}

function executeHeaderScript(scriptContent) {
    try {
        const headerInitFunction = new Function(scriptContent);
        headerInitFunction();
        console.log('✅ Script do header executado com sucesso');
        
        setTimeout(() => {
            if (typeof window.initializeHeader === 'function') {
                window.initializeHeader();
            }
        }, 300);
        
    } catch (error) {
        console.error('❌ Erro executando script do header:', error);
    }
}

function checkAndInitializeHeader() {
    const steamStatus = document.getElementById('steam-status-value');
    if (!steamStatus || steamStatus.textContent === '--') {
        console.log('⚠️ Header não inicializado automaticamente - forçando...');
        forceHeaderInitialization();
    }
}

function forceHeaderInitialization() {
    if (typeof window.refreshSteamStatus === 'function') {
        window.refreshSteamStatus();
    }
    
    if (typeof window.refreshDLLStatus === 'function') {
        window.refreshDLLStatus();
    }
    
    setTimeout(() => updateHeaderManually(), 1000);
}

async function updateHeaderManually() {
    try {
        const userResponse = await fetch('/api/steam/user/full-info');
        if (userResponse.ok) {
            const userData = await userResponse.json();
            if (userData.success && userData.user) {
                const usernameEl = document.getElementById('username-display');
                const greetingEl = document.getElementById('greeting-text');
                
                if (usernameEl) {
                    const span = usernameEl.querySelector('span');
                    if (span) span.textContent = userData.user.username || 'Jogador';
                }
                
                if (greetingEl) {
                    const hour = new Date().getHours();
                    let greeting = '';
                    if (hour >= 5 && hour < 12) greeting = 'Bom dia';
                    else if (hour >= 12 && hour < 18) greeting = 'Boa tarde';
                    else greeting = 'Boa noite';
                    greetingEl.textContent = `${greeting},`;
                }
            }
        }
        
    } catch (error) {
        console.error('❌ Erro atualizando header manualmente:', error);
    }
}

async function checkSystemStatus() {
    try {
        const response = await fetch(`${SearchConfig.API_BASE}/download/system-status`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                SearchState.isSystemReady = data.overall_status === 'operational';
                window.searchSystem.updateSystemStatusText(data.systems?.store_search?.available);
                updateHeaderStatusFromSystem(data);
                console.log('✅ Sistema verificado e pronto');
            }
        }
    } catch (error) {
        console.error('❌ Erro verificando status do sistema:', error);
        window.searchSystem.updateSystemStatusText(false);
    }
}

function updateHeaderStatusFromSystem(systemData) {
    const steamStatusEl = document.getElementById('steam-status-value');
    const dllStatusEl = document.getElementById('dll-status-value');
    
    if (steamStatusEl) {
        const isSteamOnline = systemData.systems?.store_search?.available || false;
        steamStatusEl.textContent = isSteamOnline ? 'ONLINE' : 'OFFLINE';
    }
    
    if (dllStatusEl) {
        const isDllAvailable = systemData.download_system_ready || false;
        dllStatusEl.textContent = isDllAvailable ? 'DISPONÍVEL' : 'INDISPONÍVEL';
    }
}

// ====== FALLBACKS ======
function createFallbackSidebar() {
    document.getElementById('sidebar-container').innerHTML = `
        <nav style="padding: 25px; height: 100%;">
            <div style="margin-bottom: 30px;">
                <div style="color: rgba(168, 178, 201, 0.8); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; padding-left: 10px;">
                    Navegação Principal
                </div>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin-bottom: 10px;">
                        <a href="/dashboard" style="display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: rgba(168, 178, 201, 0.9); text-decoration: none; border-radius: 10px; transition: all 0.3s ease;">
                            <i class="fas fa-home" style="color: #7a2aff;"></i>
                            <span>Dashboard</span>
                        </a>
                    </li>
                    <li style="margin-bottom: 10px;">
                        <a href="/search" style="display: flex; align-items: center; gap: 12px; padding: 12px 15px; color: white; text-decoration: none; border-radius: 10px; transition: all 0.3s ease; background: rgba(122, 42, 255, 0.2);">
                            <i class="fas fa-search" style="color: #7a2aff;"></i>
                            <span>Buscar Jogos</span>
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
    `;
}

function createFallbackFooter() {
    document.getElementById('footer-container').innerHTML = `
        <footer style="padding: 20px; text-align: center; background: linear-gradient(135deg, #0a0814 0%, #151225 100%); color: rgba(168, 178, 201, 0.7); border-top: 1px solid rgba(122, 42, 255, 0.2);">
            <div style="max-width: 1200px; margin: 0 auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                    <div style="text-align: left;">
                        <div style="font-size: 14px; font-weight: 600; color: white; margin-bottom: 5px;">
                            Steam GameLoader Ultimate
                        </div>
                        <div style="font-size: 12px;">
                            Sistema completo de gerenciamento Steam
                        </div>
                    </div>
                    <div style="font-size: 12px;">
                        <span id="currentYear">${new Date().getFullYear()}</span> | Busca Funcional
                    </div>
                </div>
            </div>
        </footer>
    `;
}

function setupMobileMenu() {
    const toggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar-container');
    
    if (toggle && sidebar) {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
            toggle.querySelector('i').className = 
                sidebar.classList.contains('active') ? 'fas fa-times' : 'fas fa-bars';
        });
        
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && !toggle.contains(e.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                toggle.querySelector('i').className = 'fas fa-bars';
            }
        });
    }
}

// ====== EXPORTAR FUNÇÕES ======
window.clearInstallationCache = () => window.searchSystem.clearInstallationCache();
window.performSearch = () => window.searchSystem.performSearch();
window.toggleDarkMode = () => window.searchSystem.toggleDarkMode();

// Inicializar ano atual
document.addEventListener('DOMContentLoaded', function() {
    const currentYear = document.getElementById('currentYear');
    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }
});

console.log('🎮 Sistema de busca carregado!');