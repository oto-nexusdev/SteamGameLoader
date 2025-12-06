// frontend/js/game_management.js - SISTEMA PREMIUM DE GERENCIAMENTO DE JOGOS UNIFICADO V2

class GameManagementSystem {
    constructor() {
        this.detectedGames = [];
        this.selectedGames = [];
        this.steamPath = null;
        this.isInitialized = false;
        this.operationsLog = [];
        this.steamCoverManager = new SteamCoverManager();
        
        this.init();
    }

    async init() {
        try {
            // Inicialização imediata - não depende mais do appLoaded
            this.setupEventListeners();
            await this.loadSteamPath();
            this.isInitialized = true;
            this.logOperation('✅ Sistema de gerenciamento inicializado com sucesso');
            
            // Disparar evento de pronto
            window.dispatchEvent(new CustomEvent('gameManagementReady'));
            
        } catch (error) {
            console.error('Erro na inicialização do Game Management:', error);
            this.logOperation('❌ Erro na inicialização do sistema');
        }
    }

    setupEventListeners() {
        // Usar event delegation para elementos carregados dinamicamente
        document.addEventListener('click', (event) => {
            const target = event.target;
            
            // Ações principais
            if (target.id === 'gmDetectGames') {
                this.detectGames();
            } else if (target.id === 'gmCheckFixes') {
                this.checkFixesBatch();
            }
            
            // Gerenciamento
            else if (target.id === 'gmBackupSelected') {
                this.backupSelectedGames();
            } else if (target.id === 'gmBackupAll') {
                this.backupAllGames();
            } else if (target.id === 'gmRemoveSelected') {
                this.removeSelectedGames();
            } else if (target.id === 'gmRemoveAll') {
                this.removeAllGames();
            }
            
            // Controles de seleção
            else if (target.id === 'gmSelectAll') {
                this.selectAllGames();
            } else if (target.id === 'gmDeselectAll') {
                this.deselectAllGames();
            }
            
            // Logs
            else if (target.id === 'gmClearLog') {
                this.clearOperationsLog();
            } else if (target.id === 'gmExportLog') {
                this.exportOperationsLog();
            }
            
            // Configurações
            else if (target.classList.contains('setting-checkbox')) {
                this.toggleSetting(target);
            }
            
            // Seleção individual de jogos
            else if (target.closest('.game-item')) {
                const gameItem = target.closest('.game-item');
                const appid = gameItem.getAttribute('data-appid');
                if (appid) {
                    this.toggleGameSelection(appid);
                }
            }
        });

        // Eventos de teclado para melhor acessibilidade
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch(event.key) {
                    case 'a':
                        event.preventDefault();
                        this.selectAllGames();
                        break;
                    case 'd':
                        event.preventDefault();
                        this.deselectAllGames();
                        break;
                }
            }
        });
    }

    async loadSteamPath() {
        try {
            const response = await fetch('/api/steam/status');
            const data = await response.json();
            
            if (data.success && data.steam_info && data.steam_info.steam_path) {
                this.steamPath = data.steam_info.steam_path;
                this.logOperation(`📍 Caminho do Steam detectado: ${this.steamPath}`);
                
                // Detecção automática se configurado
                if (this.getSetting('autoDetect')) {
                    setTimeout(() => this.detectGames(), 1500);
                }
            } else {
                this.logOperation('⚠️ Caminho do Steam não detectado - configure nas configurações');
            }
        } catch (error) {
            this.logOperation('❌ Erro ao carregar caminho do Steam');
            console.error('Erro ao carregar Steam path:', error);
        }
    }

    // ==================== DETECÇÃO DE JOGOS ====================
    async detectGames() {
        if (!this.steamPath) {
            this.showMessage('Configure o caminho do Steam primeiro', 'error');
            return;
        }

        this.showProgress('🔍 Detectando jogos na biblioteca Steam...');
        
        try {
            const response = await fetch('/api/games/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    check_fixes: this.getSetting('autoFixes')
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.detectedGames = result.games || [];
                await this.renderGamesList(); // Agora é assíncrono
                this.updateStatistics();
                this.updateControlStates();
                
                this.logOperation(`🎮 ${result.total_games} jogos detectados com sucesso`);
                
                if (result.fixes_count > 0) {
                    this.logOperation(`🔧 ${result.fixes_count} jogos com fixes disponíveis`);
                }
                
                // Disparar evento global
                window.dispatchEvent(new CustomEvent('gamesDetected', {
                    detail: { 
                        count: result.total_games, 
                        games: this.detectedGames,
                        total_size: result.total_size 
                    }
                }));
            } else {
                throw new Error(result.error || 'Falha na detecção de jogos');
            }
        } catch (error) {
            console.error('Erro na detecção:', error);
            this.logOperation(`❌ Erro na detecção: ${error.message}`);
            this.showMessage('Falha na detecção de jogos - verifique o console', 'error');
        } finally {
            this.hideProgress();
        }
    }

    // ==================== RENDERIZAÇÃO DA LISTA PREMIUM ====================
    async renderGamesList() {
        const gamesList = document.getElementById('gamesList');
        const statsContainer = document.getElementById('gamesStats');
        
        if (!gamesList) return;
        
        if (!this.detectedGames.length) {
            gamesList.innerHTML = this.createEmptyState();
            if (statsContainer) statsContainer.style.display = 'none';
            return;
        }

        if (statsContainer) statsContainer.style.display = 'grid';
        
        // Renderizar jogos com carregamento assíncrono de capas
        const gamesHTML = await Promise.all(
            this.detectedGames.map(async (game) => await this.createGameItemHTML(game))
        );
        
        gamesList.innerHTML = gamesHTML.join('');
    }

    async createGameItemHTML(game) {
        const coverContent = await this.steamCoverManager.getGameCover(game.appid);
        const isSelected = this.isGameSelected(game.appid);
        const hasFixes = game.has_fixes;
        const fromCache = game.name_from_cache;
        
        return `
            <div class="game-item ${isSelected ? 'selected' : ''}" 
                 data-appid="${game.appid}"
                 role="button"
                 aria-label="${this.escapeHtml(game.name)} - ${hasFixes ? 'Com fixes disponíveis' : 'Sem fixes'}">
                <div class="game-cover ${coverContent.includes('//') ? '' : 'fallback'}">
                    ${coverContent.includes('//') 
                        ? `<img src="${coverContent}" alt="${this.escapeHtml(game.name)}" loading="lazy" onerror="this.style.display='none'; this.parentElement.classList.add('fallback'); this.parentElement.innerHTML='${this.getFallbackIcon(game.appid)}'">`
                        : `<span>${coverContent}</span>`
                    }
                </div>
                <div class="game-info">
                    <div class="game-name" title="${this.escapeHtml(game.name)}">
                        ${this.escapeHtml(game.name)}
                    </div>
                    <div class="game-details">
                        <div class="game-detail" title="ID do jogo">🆔 ${game.appid}</div>
                        <div class="game-detail" title="Tamanho do arquivo">💾 ${game.size_formatted || 'N/A'}</div>
                        <div class="game-detail" title="Data de instalação">📅 ${game.install_date || 'N/A'}</div>
                        ${fromCache ? '<div class="game-detail" title="Nome do cache">💫 Cache</div>' : ''}
                    </div>
                </div>
                <div class="game-status">
                    ${hasFixes ? '<div class="status-badge status-fixes" title="Fixes disponíveis">🔧 Fixes</div>' : ''}
                    <div class="status-badge ${fromCache ? 'status-cache' : 'status-api'}" title="${fromCache ? 'Nome do cache' : 'Nome da API Steam'}">
                        ${fromCache ? '💫' : '🌐'}
                    </div>
                </div>
            </div>
        `;
    }

    createEmptyState() {
        return `
            <div class="empty-state">
                <div class="icon">🎮</div>
                <div class="message">
                    <h3>Nenhum jogo detectado</h3>
                    <p>Clique em "Detectar Jogos" para explorar sua biblioteca Steam</p>
                </div>
            </div>
        `;
    }

    getFallbackIcon(appid) {
        const icons = ['🎮', '👾', '🕹️', '🎯', '🎪', '🏆', '⚽', '🏀', '🎲', '🎳'];
        const index = parseInt(appid) % icons.length;
        return icons[index];
    }

    // ==================== SELEÇÃO DE JOGOS ====================
    toggleGameSelection(appid) {
        const index = this.selectedGames.indexOf(appid);
        
        if (index > -1) {
            this.selectedGames.splice(index, 1);
        } else {
            this.selectedGames.push(appid);
        }
        
        this.renderGamesList();
        this.updateControlStates();
        this.updateStatistics();
        
        // Feedback visual
        const gameItem = document.querySelector(`[data-appid="${appid}"]`);
        if (gameItem) {
            gameItem.style.transform = 'scale(0.98)';
            setTimeout(() => {
                gameItem.style.transform = '';
            }, 150);
        }
    }

    selectAllGames() {
        this.selectedGames = this.detectedGames.map(game => game.appid);
        this.renderGamesList();
        this.updateControlStates();
        this.updateStatistics();
        this.logOperation('✅ Todos os jogos selecionados');
    }

    deselectAllGames() {
        this.selectedGames = [];
        this.renderGamesList();
        this.updateControlStates();
        this.updateStatistics();
        this.logOperation('❌ Seleção de jogos limpa');
    }

    isGameSelected(appid) {
        return this.selectedGames.includes(appid);
    }

    // ==================== ATUALIZAÇÃO DE CONTROLES ====================
    updateControlStates() {
        const hasGames = this.detectedGames.length > 0;
        const hasSelection = this.selectedGames.length > 0;
        
        // Atualizar estados dos botões de forma segura
        const updateButtonState = (id, disabled, tooltip = '') => {
            const button = document.getElementById(id);
            if (button) {
                button.disabled = disabled;
                button.title = tooltip || '';
                if (disabled) {
                    button.setAttribute('aria-disabled', 'true');
                } else {
                    button.removeAttribute('aria-disabled');
                }
            }
        };
        
        updateButtonState('gmCheckFixes', !hasGames, 
            hasGames ? 'Verificar fixes para todos os jogos' : 'Nenhum jogo detectado');
        updateButtonState('gmBackupAll', !hasGames, 
            hasGames ? 'Fazer backup de todos os jogos' : 'Nenhum jogo detectado');
        updateButtonState('gmRemoveAll', !hasGames, 
            hasGames ? 'Remover todos os jogos' : 'Nenhum jogo detectado');
        updateButtonState('gmBackupSelected', !hasSelection, 
            hasSelection ? `Fazer backup de ${this.selectedGames.length} jogo(s) selecionado(s)` : 'Nenhum jogo selecionado');
        updateButtonState('gmRemoveSelected', !hasSelection, 
            hasSelection ? `Remover ${this.selectedGames.length} jogo(s) selecionado(s)` : 'Nenhum jogo selecionado');
    }

    // ==================== ESTATÍSTICAS AVANÇADAS ====================
    updateStatistics() {
        const updateStat = (id, value, tooltip = '') => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                if (tooltip) {
                    element.title = tooltip;
                }
            }
        };
        
        if (!this.detectedGames.length) {
            updateStat('statTotal', '0', 'Total de jogos detectados');
            updateStat('statFixes', '0', 'Jogos com fixes disponíveis');
            updateStat('statSize', '0 MB', 'Tamanho total dos arquivos');
            updateStat('statSelected', '0', 'Jogos selecionados');
            return;
        }
        
        const totalGames = this.detectedGames.length;
        const fixesCount = this.detectedGames.filter(game => game.has_fixes).length;
        const totalSizeBytes = this.detectedGames.reduce((sum, game) => sum + (game.size || 0), 0);
        const selectedCount = this.selectedGames.length;
        
        // Formatar tamanho de forma inteligente
        let sizeText, sizeTooltip;
        if (totalSizeBytes >= 1024 * 1024 * 1024) {
            const sizeGB = (totalSizeBytes / (1024 * 1024 * 1024)).toFixed(2);
            sizeText = `${sizeGB} GB`;
            sizeTooltip = `${totalSizeBytes.toLocaleString()} bytes`;
        } else if (totalSizeBytes >= 1024 * 1024) {
            const sizeMB = (totalSizeBytes / (1024 * 1024)).toFixed(1);
            sizeText = `${sizeMB} MB`;
            sizeTooltip = `${totalSizeBytes.toLocaleString()} bytes`;
        } else {
            const sizeKB = (totalSizeBytes / 1024).toFixed(1);
            sizeText = `${sizeKB} KB`;
            sizeTooltip = `${totalSizeBytes.toLocaleString()} bytes`;
        }
        
        updateStat('statTotal', totalGames.toLocaleString(), `${totalGames} jogos detectados`);
        updateStat('statFixes', fixesCount.toLocaleString(), 
            `${fixesCount} jogos com fixes disponíveis`);
        updateStat('statSize', sizeText, sizeTooltip);
        updateStat('statSelected', selectedCount.toLocaleString(), 
            `${selectedCount} jogos selecionados de ${totalGames}`);
    }

    // ==================== OPERAÇÕES DE BACKUP ====================
    async backupSelectedGames() {
        if (!this.selectedGames.length) {
            this.showMessage('Selecione pelo menos um jogo para fazer backup', 'error');
            return;
        }
        
        const gamesToBackup = this.detectedGames.filter(game => 
            this.selectedGames.includes(game.appid)
        );
        
        await this.executeBackup(gamesToBackup, 'selecionados');
    }

    async backupAllGames() {
        if (!this.detectedGames.length) {
            this.showMessage('Nenhum jogo detectado para backup', 'error');
            return;
        }
        
        await this.executeBackup(this.detectedGames, 'todos');
    }

    async executeBackup(games, type) {
        const appids = games.map(game => game.appid);
        const gameNames = games.map(game => game.name).join(', ');
        
        this.showProgress(`💾 Criando backup de ${games.length} jogos...`);
        this.updateProgressBar(0);
        
        try {
            const response = await fetch('/api/games/backup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    appids: appids,
                    include_lua: this.getSetting('backupLua')
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateProgressBar(100);
                this.logOperation(`✅ Backup concluído: ${games.length} jogos salvos`);
                if (result.backup_path) {
                    this.logOperation(`📁 Backup salvo em: ${result.backup_path}`);
                }
                if (result.success_count !== undefined) {
                    this.logOperation(`📊 ${result.success_count}/${games.length} jogos processados com sucesso`);
                }
                this.showMessage(`Backup concluído! ${games.length} jogos salvos.`, 'success');
            } else {
                throw new Error(result.error || 'Falha no processo de backup');
            }
        } catch (error) {
            console.error('Erro no backup:', error);
            this.logOperation(`❌ Erro no backup: ${error.message}`);
            this.showMessage('Falha no backup dos jogos', 'error');
        } finally {
            setTimeout(() => this.hideProgress(), 1000);
        }
    }

    // ==================== REMOÇÃO DE JOGOS ====================
    async removeSelectedGames() {
        if (!this.selectedGames.length) {
            this.showMessage('Selecione pelo menos um jogo para remover', 'error');
            return;
        }
        
        const gamesToRemove = this.detectedGames.filter(game => 
            this.selectedGames.includes(game.appid)
        );
        
        await this.executeRemoval(gamesToRemove, 'selecionados');
    }

    async removeAllGames() {
        if (!this.detectedGames.length) {
            this.showMessage('Nenhum jogo detectado para remoção', 'error');
            return;
        }
        
        await this.executeRemoval(this.detectedGames, 'todos');
    }

    async executeRemoval(games, type) {
        const appids = games.map(game => game.appid);
        const gameNames = games.map(game => game.name).slice(0, 3).join(', ');
        const remainingCount = Math.max(0, games.length - 3);
        const namesDisplay = remainingCount > 0 ? 
            `${gameNames} e mais ${remainingCount} jogo(s)` : 
            gameNames;
        
        // Confirmação mais detalhada e segura
        const confirmation = await this.showConfirmationDialog(
            `Remover ${games.length} Jogos`,
            `Tem certeza que deseja remover permanentemente ${games.length} jogos?\n\n📋 Jogos: ${namesDisplay}\n\n⚠️ ATENÇÃO: Esta ação não pode ser desfeita!`,
            'removal'
        );
        
        if (!confirmation) {
            this.logOperation('⚠️ Remoção de jogos cancelada pelo usuário');
            return;
        }
        
        this.showProgress(`🗑️ Removendo ${games.length} jogos...`);
        this.updateProgressBar(0);
        
        try {
            const response = await fetch('/api/games/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    appids: appids
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateProgressBar(100);
                this.logOperation(`✅ ${games.length} jogos removidos com sucesso`);
                this.showMessage(`Remoção concluída! ${games.length} jogos removidos.`, 'success');
                
                // Recarregar lista após um breve delay
                setTimeout(() => {
                    this.detectGames();
                }, 1500);
            } else {
                throw new Error(result.error || 'Falha no processo de remoção');
            }
        } catch (error) {
            console.error('Erro na remoção:', error);
            this.logOperation(`❌ Erro na remoção: ${error.message}`);
            this.showMessage('Falha na remoção dos jogos', 'error');
        } finally {
            setTimeout(() => this.hideProgress(), 1000);
        }
    }

    // ==================== VERIFICAÇÃO DE FIXES ====================
    async checkFixesBatch() {
        if (!this.detectedGames.length) {
            this.showMessage('Nenhum jogo detectado para verificação', 'error');
            return;
        }
        
        this.showProgress('🔧 Verificando fixes disponíveis...');
        this.updateProgressBar(0);
        
        try {
            const response = await fetch('/api/games/fixes/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    appids: this.detectedGames.map(game => game.appid)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateProgressBar(100);
                const fixesCount = result.fixes_count || 0;
                const totalChecked = result.total_checked || this.detectedGames.length;
                
                this.logOperation(`✅ Verificação de fixes concluída: ${fixesCount} de ${totalChecked} jogos com fixes`);
                
                if (fixesCount > 0) {
                    this.showMessage(`🎉 ${fixesCount} jogos com fixes disponíveis!`, 'success');
                } else {
                    this.showMessage('ℹ️ Nenhum fix adicional encontrado', 'info');
                }
                
                // Atualizar estatísticas e lista
                this.updateStatistics();
                this.renderGamesList();
            } else {
                throw new Error(result.error || 'Falha na verificação de fixes');
            }
        } catch (error) {
            console.error('Erro na verificação:', error);
            this.logOperation(`❌ Erro na verificação de fixes: ${error.message}`);
            this.showMessage('Falha na verificação de fixes', 'error');
        } finally {
            setTimeout(() => this.hideProgress(), 1000);
        }
    }

    // ==================== SISTEMA DE CONFIGURAÇÕES ====================
    toggleSetting(checkbox) {
        const wasChecked = checkbox.classList.contains('checked');
        checkbox.classList.toggle('checked');
        const setting = checkbox.getAttribute('data-setting');
        const isEnabled = checkbox.classList.contains('checked');
        
        // Feedback visual
        checkbox.style.transform = 'scale(0.9)';
        setTimeout(() => {
            checkbox.style.transform = '';
        }, 150);
        
        this.logOperation(`⚙️ ${setting.replace(/([A-Z])/g, ' $1')} ${isEnabled ? '✅ ativado' : '❌ desativado'}`);
        
        // Ações específicas por configuração
        if (setting === 'autoDetect' && isEnabled && this.steamPath) {
            setTimeout(() => this.detectGames(), 1000);
        }
    }

    getSetting(settingName) {
        const checkbox = document.querySelector(`[data-setting="${settingName}"]`);
        return checkbox ? checkbox.classList.contains('checked') : true;
    }

    // ==================== SISTEMA DE LOGS PREMIUM ====================
    logOperation(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = { 
            timestamp, 
            message,
            type: this.getLogType(message)
        };
        
        this.operationsLog.push(logEntry);
        this.updateOperationsLog();
        
        // Log sempre ativo para desenvolvimento
        console.log(`[Game Management] ${message}`);
    }

    getLogType(message) {
        if (message.includes('✅') || message.includes('🎉')) return 'success';
        if (message.includes('❌') || message.includes('⚠️')) return 'error';
        if (message.includes('🔧') || message.includes('⚙️')) return 'warning';
        if (message.includes('📁') || message.includes('📊')) return 'info';
        return 'info';
    }

    updateOperationsLog() {
        const logContainer = document.getElementById('gmOperationsLog');
        if (!logContainer) return;
        
        const lastEntries = this.operationsLog.slice(-15); // Aumentado para 15 registros
        
        logContainer.innerHTML = lastEntries.map(entry => `
            <div class="log-entry log-${entry.type}">
                <span class="log-timestamp">[${entry.timestamp}]</span>
                <span class="log-message">${entry.message}</span>
            </div>
        `).join('');
        
        // Auto-scroll para o final
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    clearOperationsLog() {
        this.operationsLog = [];
        this.updateOperationsLog();
        this.logOperation('🧹 Log de operações limpo');
        this.showMessage('Log limpo com sucesso', 'info');
    }

    exportOperationsLog() {
        const logText = this.operationsLog.map(entry => 
            `[${entry.timestamp}] ${entry.message}`
        ).join('\n');
        
        const blob = new Blob([logText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `steam_gameloader_log_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.logOperation('📤 Log exportado com sucesso');
        this.showMessage('Log exportado para downloads', 'success');
    }

    // ==================== SISTEMA DE UI PREMIUM ====================
    showProgress(message, progress = 0) {
        const overlay = document.getElementById('gmProgressOverlay');
        const progressText = document.getElementById('gmProgressText');
        const progressBar = document.getElementById('gmProgressBar');
        
        if (overlay && progressText) {
            progressText.textContent = message;
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            overlay.classList.remove('hidden');
        }
    }

    updateProgressBar(progress) {
        const progressBar = document.getElementById('gmProgressBar');
        if (progressBar) {
            progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
        }
    }

    hideProgress() {
        const overlay = document.getElementById('gmProgressOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }

    showMessage(message, type = 'info', duration = 4000) {
        // Sistema de toast premium
        const toast = document.createElement('div');
        toast.className = `message-toast message-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${icons[type] || icons.info}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" aria-label="Fechar mensagem">×</button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animação de entrada
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Fechar ao clicar no botão
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
        
        // Auto-remover
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    async showConfirmationDialog(title, message, type = 'default') {
        return new Promise((resolve) => {
            const dialog = document.createElement('div');
            dialog.className = 'confirmation-dialog';
            dialog.innerHTML = `
                <div class="dialog-overlay">
                    <div class="dialog-content">
                        <div class="dialog-header">
                            <h3>${title}</h3>
                        </div>
                        <div class="dialog-body">
                            <p>${message.replace(/\n/g, '<br>')}</p>
                        </div>
                        <div class="dialog-footer">
                            <button class="btn secondary dialog-cancel">Cancelar</button>
                            <button class="btn ${type === 'removal' ? 'danger' : 'primary'} dialog-confirm">
                                ${type === 'removal' ? '🗑️ Remover' : 'Confirmar'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(dialog);
            
            const confirmBtn = dialog.querySelector('.dialog-confirm');
            const cancelBtn = dialog.querySelector('.dialog-cancel');
            
            const cleanup = () => {
                dialog.remove();
                document.removeEventListener('keydown', handleKeydown);
            };
            
            const handleKeydown = (e) => {
                if (e.key === 'Escape') {
                    resolve(false);
                    cleanup();
                } else if (e.key === 'Enter') {
                    resolve(true);
                    cleanup();
                }
            };
            
            confirmBtn.addEventListener('click', () => {
                resolve(true);
                cleanup();
            });
            
            cancelBtn.addEventListener('click', () => {
                resolve(false);
                cleanup();
            });
            
            document.addEventListener('keydown', handleKeydown);
            
            // Focar no botão de cancelar por segurança
            cancelBtn.focus();
        });
    }

    // ==================== UTILITÁRIOS AVANÇADOS ====================
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatFileSize(bytes) {
        if (bytes === 0 || bytes === undefined) return '0 B';
        
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    // ==================== MÉTODOS PÚBLICOS ====================
    getDetectedGames() {
        return [...this.detectedGames]; // Retorna cópia para evitar mutação
    }

    getSelectedGames() {
        return [...this.selectedGames];
    }

    getGameByAppId(appid) {
        return this.detectedGames.find(game => game.appid === appid);
    }

    isReady() {
        return this.isInitialized;
    }

    getStats() {
        return {
            totalGames: this.detectedGames.length,
            selectedGames: this.selectedGames.length,
            gamesWithFixes: this.detectedGames.filter(game => game.has_fixes).length,
            totalSize: this.detectedGames.reduce((sum, game) => sum + (game.size || 0), 0)
        };
    }
}

// ==================== GERENCIADOR DE CAPAS STEAM ====================
class SteamCoverManager {
    constructor() {
        this.coversCache = new Map();
        this.failedLoads = new Set();
        this.cacheDir = 'cache/covers/';
    }

    async getGameCover(appid, size = 'capsule') {
        const cacheKey = `${appid}_${size}`;
        
        // Retornar do cache se disponível
        if (this.coversCache.has(cacheKey)) {
            return this.coversCache.get(cacheKey);
        }
        
        // Pular se já falhou antes
        if (this.failedLoads.has(cacheKey)) {
            return this.getFallbackIcon(appid);
        }

        try {
            const coverUrl = this.buildCoverUrl(appid, size);
            const isValid = await this.validateImage(coverUrl);
            
            if (isValid) {
                this.coversCache.set(cacheKey, coverUrl);
                return coverUrl;
            } else {
                throw new Error('Imagem inválida ou não encontrada');
            }
        } catch (error) {
            console.warn(`Não foi possível carregar capa para ${appid}:`, error);
            this.failedLoads.add(cacheKey);
            return this.getFallbackIcon(appid);
        }
    }

    buildCoverUrl(appid, size = 'capsule') {
        const sizes = {
            'capsule': `https://cdn.cloudflare.steamstatic.com/steam/apps/${appid}/capsule_231x87.jpg`,
            'header': `https://cdn.cloudflare.steamstatic.com/steam/apps/${appid}/header.jpg`,
            'library': `https://cdn.cloudflare.steamstatic.com/steam/apps/${appid}/library_600x900.jpg`,
            'library_hero': `https://cdn.cloudflare.steamstatic.com/steam/apps/${appid}/library_hero.jpg`
        };
        
        return sizes[size] || sizes.capsule;
    }

    async validateImage(url) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;
            
            // Timeout para imagens que nunca carregam
            setTimeout(() => resolve(false), 3000);
        });
    }

    getFallbackIcon(appid) {
        const icons = ['🎮', '👾', '🕹️', '🎯', '🎪', '🏆', '⚽', '🏀', '🎲', '🎳'];
        const index = parseInt(appid) % icons.length;
        return icons[index];
    }

    clearCache() {
        this.coversCache.clear();
        this.failedLoads.clear();
    }
}

// ==================== INICIALIZAÇÃO E EXPORTAÇÃO ====================
let gameManagement = null;

function initializeGameManagement() {
    if (!gameManagement) {
        gameManagement = new GameManagementSystem();
        window.gameManagement = gameManagement;
        
        // Expor utilitários globais para debug (sempre disponíveis)
        window._gameManagementUtils = {
            clearCache: () => gameManagement.steamCoverManager.clearCache(),
            getStats: () => gameManagement.getStats(),
            forceDetect: () => gameManagement.detectGames()
        };
    }
    return gameManagement;
}

// Auto-inicialização melhorada
function autoInitializeGameManagement() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeGameManagement);
    } else {
        // Delay para garantir que outros sistemas estejam inicializados
        setTimeout(initializeGameManagement, 500);
    }
}

// Inicializar automaticamente
autoInitializeGameManagement();

// Exportar para uso global
window.GameManagementSystem = GameManagementSystem;
window.SteamCoverManager = SteamCoverManager;
window.initializeGameManagement = initializeGameManagement;

// Eventos globais para integração com outros sistemas
window.addEventListener('steamPathUpdated', (event) => {
    if (gameManagement) {
        gameManagement.steamPath = event.detail.path;
        gameManagement.logOperation('📍 Caminho do Steam atualizado via evento');
        if (gameManagement.getSetting('autoDetect')) {
            setTimeout(() => gameManagement.detectGames(), 1000);
        }
    }
});

console.log('🎮 Sistema de Gerenciamento de Jogos Premium carregado');