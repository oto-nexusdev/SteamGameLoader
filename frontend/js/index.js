// frontend/js/index.js - VERSÃO DEFINITIVA CORRIGIDA 2.0
// Sistema DE APOIO - NÃO SOBRESCREVE, APENAS SUPORTA

console.log('🔧 index.js - Sistema de apoio carregado');

// ==================== SISTEMA DE APOIO ====================
// Este arquivo NÃO substitui scripts das páginas, apenas fornece funções auxiliares

const AppState = {
    user: null,
    lastUpdate: null
};

// ==================== FUNÇÕES DE APOIO ====================

/**
 * Atualiza elementos específicos de forma segura
 */
function updateElementSafely(id, content) {
    const element = document.getElementById(id);
    if (element) {
        if (typeof content === 'string') {
            element.textContent = content;
        } else if (typeof content === 'object' && content.html) {
            element.innerHTML = content.html;
        }
        return true;
    }
    return false;
}

/**
 * Atualiza status visualmente
 */
function updateStatusIndicator(elementId, status, options = {}) {
    const element = document.getElementById(elementId);
    if (!element) return false;
    
    const {
        text = '',
        onlineColor = '#00ff88',
        offlineColor = '#ff2a6d',
        warningColor = '#ffaa00'
    } = options;
    
    if (text && element.querySelector('span')) {
        element.querySelector('span').textContent = text;
    }
    
    if (status === true) {
        element.style.color = onlineColor;
        if (element.classList) {
            element.classList.remove('offline', 'warning');
            element.classList.add('online');
        }
    } else if (status === false) {
        element.style.color = offlineColor;
        if (element.classList) {
            element.classList.remove('online', 'warning');
            element.classList.add('offline');
        }
    } else if (status === 'warning') {
        element.style.color = warningColor;
        if (element.classList) {
            element.classList.remove('online', 'offline');
            element.classList.add('warning');
        }
    }
    
    return true;
}

/**
 * Função auxiliar para verificar e corrigir elementos não atualizados
 */
function checkAndFixMissingElements() {
    console.log('🔍 Verificando elementos não atualizados...');
    
    // Lista de elementos críticos que devem estar preenchidos
    const criticalElements = [
        'username-display',
        'sidebar-username', 
        'user-display-name',
        'hero-steam-status',
        'hero-dll-status'
    ];
    
    let fixedCount = 0;
    
    criticalElements.forEach(id => {
        const element = document.getElementById(id);
        if (element && (!element.textContent || element.textContent.includes('Carregando') || element.textContent.includes('--'))) {
            console.log(`⚠️ Elemento ${id} não foi atualizado:`, element.textContent);
            
            // Tentar obter dados atualizados
            fetchUserDataForFix(id);
            fixedCount++;
        }
    });
    
    if (fixedCount > 0) {
        console.log(`✅ Tentativa de corrigir ${fixedCount} elementos`);
    }
}

/**
 * Busca dados do usuário para corrigir elementos específicos
 */
async function fetchUserDataForFix(elementId) {
    try {
        const response = await fetch('/api/steam/user/full-info', {
            cache: 'no-cache',
            headers: { 'Pragma': 'no-cache' }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.user) {
                applyFixToElement(elementId, data.user);
            }
        }
    } catch (error) {
        console.error(`❌ Erro ao corrigir elemento ${elementId}:`, error);
    }
}

/**
 * Aplica correção a elemento específico
 */
function applyFixToElement(elementId, userData) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    switch(elementId) {
        case 'username-display':
        case 'sidebar-username':
        case 'user-display-name':
            element.textContent = userData.username || 'Jogador';
            break;
            
        case 'hero-steam-status':
            element.textContent = userData.steam_running ? 'ON' : 'OFF';
            element.style.color = userData.steam_running ? '#00ff88' : '#ff2a6d';
            break;
            
        case 'hero-dll-status':
            element.textContent = userData.dll_available ? 'OK' : 'ERR';
            element.style.color = userData.dll_available ? '#00ff88' : '#ff2a6d';
            break;
            
        case 'hero-api-status':
            element.textContent = 'OK';
            element.style.color = '#00ff88';
            break;
    }
    
    console.log(`✅ Elemento ${elementId} corrigido:`, element.textContent);
}

// ==================== SISTEMA DE VERIFICAÇÃO ====================

/**
 * Verifica se o sistema principal está funcionando
 */
function checkMainSystem() {
    // Verifica se há scripts principais em execução
    const hasMainScript = typeof window.showNotification !== 'undefined';
    
    if (!hasMainScript) {
        console.log('⚠️ Sistema principal não detectado, ativando modo de apoio...');
        activateFallbackMode();
    } else {
        console.log('✅ Sistema principal detectado, modo de apoio ativo');
    }
}

/**
 * Modo de fallback - apenas para emergências
 */
async function activateFallbackMode() {
    console.log('🚨 Ativando modo de fallback...');
    
    try {
        // Buscar dados básicos
        const response = await fetch('/api/steam/user/full-info');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.user) {
                AppState.user = data.user;
                updateCriticalElements(data.user);
            }
        }
    } catch (error) {
        console.error('❌ Erro no modo fallback:', error);
    }
}

/**
 * Atualiza apenas elementos críticos
 */
function updateCriticalElements(user) {
    // Elementos MAIS IMPORTANTES - atualizar sempre
    updateElementSafely('username-display', user.username || 'Jogador');
    updateElementSafely('sidebar-username', user.username || 'Jogador');
    updateElementSafely('user-display-name', user.username || 'Jogador');
    
    // Status Steam
    updateElementSafely('steam-status-value', user.steam_running ? 'Online' : 'Offline');
    updateElementSafely('sidebar-steam-status', user.steam_running ? 'Online' : 'Offline');
    updateElementSafely('hero-steam-status', user.steam_running ? 'ON' : 'OFF');
    
    // Status DLL
    updateElementSafely('dll-status-value', user.dll_available ? 'OK' : 'Ausente');
    updateElementSafely('sidebar-dll-status', user.dll_available ? 'OK' : 'Ausente');
    updateElementSafely('hero-dll-status', user.dll_available ? 'OK' : 'ERR');
    
    console.log('✅ Elementos críticos atualizados no fallback');
}

// ==================== RELÓGIO UNIVERSAL ====================

/**
 * Sistema de relógio que NÃO interfere com outros
 */
function startUniversalClock() {
    console.log('⏰ Iniciando relógio universal...');
    
    function updateClock() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('pt-BR', { hour12: false });
        const dateStr = now.toLocaleDateString('pt-BR');
        
        // Atualizar SEMPRE que encontrar elementos não atualizados
        const timeElements = document.querySelectorAll('[id*="time"], [id*="Time"], [id*="clock"], [id*="Clock"]');
        const dateElements = document.querySelectorAll('[id*="date"], [id*="Date"]');
        
        timeElements.forEach(el => {
            if (!el.textContent || el.textContent.includes('--')) {
                el.textContent = timeStr;
            }
        });
        
        dateElements.forEach(el => {
            if (!el.textContent || el.textContent.includes('--')) {
                el.textContent = dateStr;
            }
        });
    }
    
    updateClock();
    setInterval(updateClock, 1000);
}

// ==================== INICIALIZAÇÃO SEGURA ====================

/**
 * Inicialização que NÃO conflita com scripts existentes
 */
function initializeSafeSupport() {
    console.log('🛡️ Inicializando sistema de apoio seguro...');
    
    // 1. Iniciar relógio universal
    startUniversalClock();
    
    // 2. Verificar sistema principal
    setTimeout(checkMainSystem, 1000);
    
    // 3. Verificar elementos após 3 segundos
    setTimeout(checkAndFixMissingElements, 3000);
    
    // 4. Verificação periódica (apenas se necessário)
    setInterval(() => {
        if (AppState.user === null) {
            checkAndFixMissingElements();
        }
    }, 15000);
    
    console.log('✅ Sistema de apoio seguro inicializado');
}

// ==================== FUNÇÕES GLOBAIS DE APOIO ====================

/**
 * Função global para forçar atualização (usada por botões)
 */
window.forceRefreshUniversal = async function() {
    console.log('🔄 Atualização universal solicitada...');
    
    try {
        const response = await fetch('/api/steam/user/full-info', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.user) {
                AppState.user = data.user;
                updateCriticalElements(data.user);
                
                // Disparar evento para outros scripts
                const event = new CustomEvent('userDataUpdated', { 
                    detail: data.user 
                });
                window.dispatchEvent(event);
                
                return true;
            }
        }
    } catch (error) {
        console.error('❌ Erro na atualização universal:', error);
    }
    
    return false;
};

/**
 * Função para verificar status específico
 */
window.checkSteamStatusUniversal = async function() {
    return window.forceRefreshUniversal();
};

// ==================== INICIALIZAÇÃO AUTOMÁTICA SEGURA ====================

// Aguardar completamente a página carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('📄 DOM carregado - Iniciando apoio seguro...');
        setTimeout(initializeSafeSupport, 500);
    });
} else {
    console.log('⚡ DOM já pronto - Iniciando apoio seguro...');
    setTimeout(initializeSafeSupport, 300);
}

// ==================== EXPORTAÇÕES LIMITADAS ====================

// Exportar APENAS funções que não conflitam
window.supportForceRefresh = window.forceRefreshUniversal;
window.supportCheckStatus = window.checkSteamStatusUniversal;

console.log('✅ index.js - Sistema de apoio seguro carregado');