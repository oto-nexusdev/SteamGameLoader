/* ========================================================================
   DLC_FIXES_INTEGRATION.JS — SISTEMA DE INTEGRAÇÃO DE FIXES v8.0
   Integração completa entre DLCs e Fixes com novo design
   ======================================================================== */

class DLCFixesIntegration {
    constructor() {
        this.currentGame = null;
        this.availableFixes = [];
        this.selectedFix = null;
        this.initialized = false;
    }

    initialize() {
        if (this.initialized) return;
        
        console.log('🎯 Inicializando Sistema de Integração de Fixes...');
        this.setupEventListeners();
        this.initialized = true;
        
        window.dlcLog('✅ Sistema de Fixes integrado com sucesso');
    }

    setupEventListeners() {
        // Botão de verificar fixes
        const checkFixesBtn = document.getElementById('fixCheckAvailable');
        if (checkFixesBtn) {
            checkFixesBtn.addEventListener('click', () => this.checkAvailableFixes());
        }

        // Botão de aplicar fix
        const applyFixBtn = document.getElementById('fixApplySelected');
        if (applyFixBtn) {
            applyFixBtn.addEventListener('click', () => this.applySelectedFix());
        }

        // Botão de atualizar cache
        const refreshCacheBtn = document.getElementById('fixRefreshCache');
        if (refreshCacheBtn) {
            refreshCacheBtn.addEventListener('click', () => this.refreshFixesCache());
        }

        // Listeners para seleção de fixes
        document.addEventListener('click', (e) => {
            const fixItem = e.target.closest('.fix-item');
            if (fixItem) {
                this.selectFix(fixItem);
            }
        });
    }

    onGameSelected(game) {
        this.currentGame = game;
        this.updateFixSelectionInfo(game);
        this.clearFixesList();
        
        window.dlcLog(`🎮 Preparando fixes para: ${game.name}`);
    }

    updateFixSelectionInfo(game) {
        const fixName = document.getElementById('fixSelectedGameName');
        const fixAppid = document.getElementById('fixSelectedGameAppid');
        const fixStatus = document.getElementById('fixSelectedGameStatus');

        if (fixName) fixName.textContent = game.name;
        if (fixAppid) fixAppid.textContent = `AppID: ${game.appid}`;
        if (fixStatus) {
            fixStatus.textContent = 'Clique em "Verificar Fixes"';
            fixStatus.className = 'status-badge';
        }
    }

    async checkAvailableFixes() {
        if (!this.currentGame) {
            this.showNotification('Selecione um jogo primeiro', 'warning');
            return;
        }

        try {
            this.showLoadingState('fixes');
            window.dlcLog(`🔍 Verificando fixes para: ${this.currentGame.name}`);

            const response = await fetch(`/api/fixes/${this.currentGame.appid}`);
            const data = await response.json();

            if (data.success) {
                this.availableFixes = data.fixes || [];
                this.renderFixesList();
                this.updateFixStatus();
                window.dlcLog(`✅ ${this.availableFixes.length} fixes encontrados`);
            } else {
                throw new Error(data.error || 'Erro ao buscar fixes');
            }
        } catch (error) {
            console.error('❌ Erro ao verificar fixes:', error);
            this.showErrorState('fixes', error.message);
            window.dlcLog(`❌ Falha na verificação de fixes: ${error.message}`, 'error');
        }
    }

    renderFixesList() {
        const fixesList = document.getElementById('fixItemsList');
        if (!fixesList) return;

        if (this.availableFixes.length === 0) {
            fixesList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">🔧</div>
                    <h4>Nenhum fix disponível</h4>
                    <p>Este jogo não possui fixes detectados no momento</p>
                </div>
            `;
            return;
        }

        fixesList.innerHTML = this.availableFixes.map(fix => `
            <div class="fix-item" data-fix-id="${fix.id}">
                <div class="fix-type">${fix.type || 'Fix Geral'}</div>
                <div class="fix-description">${fix.description || 'Sem descrição disponível'}</div>
                <div class="fix-details">
                    <span class="fix-status ${fix.available ? 'available' : 'unavailable'}">
                        ${fix.available ? 'Disponível' : 'Indisponível'}
                    </span>
                    <span class="fix-version">v${fix.version || '1.0'}</span>
                    <span class="fix-size">${fix.size || 'N/A'}</span>
                </div>
            </div>
        `).join('');

        this.updateFixControls();
    }

    selectFix(fixElement) {
        // Desselecionar fix anterior
        document.querySelectorAll('.fix-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Selecionar novo fix
        fixElement.classList.add('selected');
        const fixId = fixElement.getAttribute('data-fix-id');
        this.selectedFix = this.availableFixes.find(fix => fix.id == fixId);

        this.updateFixControls();
        window.dlcLog(`🔧 Fix selecionado: ${this.selectedFix.type}`);
    }

    updateFixControls() {
        const applyBtn = document.getElementById('fixApplySelected');
        const hasSelection = this.selectedFix !== null;
        const isAvailable = this.selectedFix?.available;

        if (applyBtn) {
            applyBtn.disabled = !hasSelection || !isAvailable;
            
            if (!hasSelection) {
                applyBtn.innerHTML = '<span class="btn-icon">🔧</span> Aplicar Fix Selecionado';
            } else if (!isAvailable) {
                applyBtn.innerHTML = '<span class="btn-icon">⏸️</span> Fix Indisponível';
            } else {
                applyBtn.innerHTML = '<span class="btn-icon">🔧</span> Aplicar Fix Selecionado';
            }
        }
    }

    updateFixStatus() {
        const fixStatus = document.getElementById('fixSelectedGameStatus');
        if (!fixStatus) return;

        const availableFixes = this.availableFixes.filter(fix => fix.available).length;
        
        if (availableFixes > 0) {
            fixStatus.textContent = `${availableFixes} Fix(es) Disponível(is)`;
            fixStatus.className = 'status-badge available';
        } else {
            fixStatus.textContent = 'Nenhum Fix Disponível';
            fixStatus.className = 'status-badge unavailable';
        }
    }

    async applySelectedFix() {
        if (!this.selectedFix || !this.currentGame) {
            this.showNotification('Selecione um fix para aplicar', 'warning');
            return;
        }

        if (!this.selectedFix.available) {
            this.showNotification('Este fix não está disponível', 'error');
            return;
        }

        try {
            this.showFixProgress('Aplicando fix...', 0);
            window.dlcLog(`🛠️ Aplicando fix: ${this.selectedFix.type}`);

            const applyBtn = document.getElementById('fixApplySelected');
            applyBtn.disabled = true;
            applyBtn.innerHTML = '<span class="btn-icon">⏳</span> Aplicando...';

            // Simular progresso (substituir por chamada real à API)
            for (let i = 0; i <= 100; i += 10) {
                this.showFixProgress(`Aplicando ${this.selectedFix.type}...`, i);
                await this.delay(200);
            }

            this.showFixProgress('Fix aplicado com sucesso!', 100);
            window.dlcLog(`✅ Fix aplicado: ${this.selectedFix.type}`, 'success');

            setTimeout(() => {
                this.hideFixProgress();
                applyBtn.innerHTML = '<span class="btn-icon">🔧</span> Aplicar Fix Selecionado';
                applyBtn.disabled = false;
                this.selectedFix = null;
                document.querySelectorAll('.fix-item').forEach(item => {
                    item.classList.remove('selected');
                });
            }, 2000);

        } catch (error) {
            console.error('❌ Erro ao aplicar fix:', error);
            this.showFixProgress('Erro ao aplicar fix', 100);
            window.dlcLog(`❌ Falha na aplicação do fix: ${error.message}`, 'error');
            
            setTimeout(() => {
                this.hideFixProgress();
                const applyBtn = document.getElementById('fixApplySelected');
                applyBtn.innerHTML = '<span class="btn-icon">🔧</span> Aplicar Fix Selecionado';
                applyBtn.disabled = false;
            }, 3000);
        }
    }

    async refreshFixesCache() {
        try {
            window.dlcLog('🔄 Atualizando cache de fixes...');
            
            const response = await fetch('/api/fixes/cache/refresh', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Cache de fixes atualizado!', 'success');
                window.dlcLog('✅ Cache de fixes atualizado');
                
                // Recarregar fixes se tiver um jogo selecionado
                if (this.currentGame) {
                    setTimeout(() => this.checkAvailableFixes(), 1000);
                }
            } else {
                throw new Error(data.error || 'Erro ao atualizar cache');
            }
        } catch (error) {
            console.error('❌ Erro ao atualizar cache:', error);
            this.showNotification('Erro ao atualizar cache', 'error');
            window.dlcLog(`❌ Falha na atualização do cache: ${error.message}`, 'error');
        }
    }

    showLoadingState(type) {
        const container = type === 'fixes' ? 
            document.getElementById('fixItemsList') : 
            document.getElementById('dlcItemsList');
        
        if (container) {
            container.innerHTML = `
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>${type === 'fixes' ? 'Buscando fixes disponíveis...' : 'Carregando DLCs...'}</p>
                </div>
            `;
        }
    }

    showErrorState(type, message) {
        const container = type === 'fixes' ? 
            document.getElementById('fixItemsList') : 
            document.getElementById('dlcItemsList');
        
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="icon">❌</div>
                    <h4>Erro ao carregar ${type === 'fixes' ? 'fixes' : 'DLCs'}</h4>
                    <p>${message}</p>
                    <button class="action-btn secondary" onclick="window.dlcFixesIntegration.${type === 'fixes' ? 'checkAvailableFixes' : 'loadGameDlcs'}()">
                        <span class="btn-icon">🔄</span>
                        Tentar Novamente
                    </button>
                </div>
            `;
        }
    }

    showFixProgress(message, percent, details = '') {
        const progressArea = document.getElementById('fixProgressArea');
        const progressText = document.getElementById('fixProgressText');
        const progressPercent = document.getElementById('fixProgressPercent');
        const progressBar = document.getElementById('fixProgressBar');
        const progressDetails = document.getElementById('fixProgressDetails');

        if (progressArea && progressText && progressPercent && progressBar) {
            progressText.textContent = message;
            progressPercent.textContent = percent + '%';
            progressBar.style.width = percent + '%';
            if (progressDetails) progressDetails.textContent = details;
            
            progressArea.style.display = 'block';
            progressArea.classList.add('active');
            
            // Atualizar classes de status
            progressBar.className = 'progress-bar';
            if (percent >= 100) progressBar.classList.add('success');
            else if (percent < 30) progressBar.classList.add('warning');
        }
    }

    hideFixProgress() {
        const progressArea = document.getElementById('fixProgressArea');
        if (progressArea) {
            progressArea.classList.remove('active');
            setTimeout(() => {
                progressArea.style.display = 'none';
            }, 500);
        }
    }

    clearFixesList() {
        const fixesList = document.getElementById('fixItemsList');
        if (fixesList) {
            fixesList.innerHTML = `
                <div class="empty-state">
                    <div class="icon">🔧</div>
                    <h4>Verifique os fixes disponíveis</h4>
                    <p>Clique em "Verificar Fixes" para buscar fixes para o jogo selecionado</p>
                </div>
            `;
        }
        
        this.availableFixes = [];
        this.selectedFix = null;
        this.updateFixControls();
    }

    showNotification(message, type = 'info') {
        // Implementar sistema de notificações toast
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Placeholder - implementar UI de notificação
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? 'var(--success)' : 
                        type === 'error' ? 'var(--error)' : 
                        type === 'warning' ? 'var(--warning)' : 'var(--info)'};
            color: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            z-index: var(--z-modal);
            animation: dlcNotificationIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('hiding');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 400);
        }, 3000);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Inicializar globalmente
window.dlcFixesIntegration = new DLCFixesIntegration();