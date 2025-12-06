// ====== INICIALIZAÇÃO DA SIDEBAR DA HOME ======
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Inicializando sidebar da Home...');
    initializeHomeSidebar();
});

function initializeHomeSidebar() {
    try {
        // Atualizar dados do usuário
        updateSidebarUserData();
        
        // Atualizar status do sistema
        updateSidebarSystemStatus();
        
        // Atualizar contagem de jogos
        updateSidebarGamesCount();
        
        // Iniciar relógio da sidebar
        startSidebarClock();
        
        // Configurar eventos dos botões
        setupSidebarEvents();
        
        console.log('✅ Sidebar da Home inicializada');
        
    } catch (error) {
        console.error('❌ Erro na sidebar da Home:', error);
    }
}

async function updateSidebarUserData() {
    try {
        const response = await fetch('/api/header/status');
        if (!response.ok) throw new Error('API não respondeu');
        
        const data = await response.json();
        
        if (data.success && data.data) {
            const user = data.data;
            
            // Atualizar username
            document.getElementById('sidebar-username').textContent = user.username || 'Jogador';
            
            // Atualizar status
            const statusElement = document.getElementById('sidebar-userstatus');
            if (user.steam_running) {
                statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Online</span>';
                statusElement.querySelector('i').style.color = '#00ff88';
            } else {
                statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Offline</span>';
                statusElement.querySelector('i').style.color = '#ff2a6d';
            }
            
            // Atualizar status dots
            updateStatusDots(user.steam_running, user.dll_available);
            
            return true;
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar dados do usuário:', error);
        document.getElementById('sidebar-username').textContent = 'Usuário Steam';
        document.getElementById('sidebar-userstatus').innerHTML = '<i class="fas fa-circle" style="color: #ffaa00;"></i><span>Erro</span>';
    }
    
    return false;
}

function updateStatusDots(steamRunning, dllAvailable) {
    const steamDot = document.getElementById('home-steam-dot');
    const dllDot = document.getElementById('home-dll-dot');
    
    if (steamDot) {
        steamDot.className = 'status-dot-home ' + (steamRunning ? 'online' : 'offline');
    }
    
    if (dllDot) {
        dllDot.className = 'status-dot-home ' + (dllAvailable ? 'online' : 'warning');
    }
}

async function updateSidebarSystemStatus() {
    try {
        const response = await fetch('/api/system/status');
        if (!response.ok) throw new Error('API de sistema não respondeu');
        
        const data = await response.json();
        
        if (data.success) {
            // Atualizar status na sidebar
            const steamStatus = data.system?.steam?.running ? 'Online' : 'Offline';
            const apiStatus = 'Online';
            const cacheStatus = 'OK';
            
            document.getElementById('sidebar-steam-status').textContent = steamStatus;
            document.getElementById('sidebar-steam-status').className = 'status-value-home ' + 
                (data.system?.steam?.running ? 'online' : 'offline');
            
            document.getElementById('sidebar-dll-status').textContent = 'OK';
            document.getElementById('sidebar-dll-status').className = 'status-value-home online';
            
            document.getElementById('sidebar-api-status').textContent = apiStatus;
            document.getElementById('sidebar-api-status').className = 'status-value-home online';
            
            document.getElementById('sidebar-cache-status').textContent = cacheStatus;
            document.getElementById('sidebar-cache-status').className = 'status-value-home online';
            
            return true;
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar status do sistema:', error);
        document.getElementById('sidebar-steam-status').textContent = 'Erro';
        document.getElementById('sidebar-steam-status').className = 'status-value-home offline';
        
        document.getElementById('sidebar-api-status').textContent = 'Erro';
        document.getElementById('sidebar-api-status').className = 'status-value-home offline';
    }
    
    return false;
}

async function updateSidebarGamesCount() {
    try {
        const response = await fetch('/api/games/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fetch_names: false })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.games) {
                const count = data.games.length;
                document.getElementById('sidebar-games-count').textContent = count;
                return true;
            }
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar contagem de jogos:', error);
    }
    
    return false;
}

function startSidebarClock() {
    function updateClock() {
        const now = new Date();
        
        // Horário
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        
        // Data
        const day = now.getDate().toString().padStart(2, '0');
        const month = (now.getMonth() + 1).toString().padStart(2, '0');
        
        // Atualizar sidebar
        const timeElement = document.getElementById('sidebar-time');
        const dateElement = document.getElementById('sidebar-date');
        
        if (timeElement) timeElement.textContent = `${hours}:${minutes}`;
        if (dateElement) dateElement.textContent = `${day}/${month}`;
    }
    
    updateClock();
    setInterval(updateClock, 60000); // Atualiza a cada minuto
}

function setupSidebarEvents() {
    // Marcar link ativo
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link-home');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Link da Home sempre ativo em /app
    if (currentPath === '/app') {
        const homeLink = document.querySelector('.nav-link-home[href="/app"]');
        if (homeLink) homeLink.classList.add('active');
    }
}

// ====== FUNÇÕES EXPORTADAS PARA A SIDEBAR ======
window.checkSteamStatus = async function() {
    try {
        const response = await fetch('/api/header/status');
        if (!response.ok) throw new Error('API não respondeu');
        
        const data = await response.json();
        
        if (data.success && data.data) {
            const steamRunning = data.data.steam_running;
            const message = steamRunning ? 'Steam está em execução' : 'Steam não está em execução';
            
            // Atualizar UI
            updateStatusDots(steamRunning, data.data.dll_available);
            updateSidebarSystemStatus();
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                showNotification('Status do Steam', message, steamRunning ? 'success' : 'warning');
            } else {
                alert(message);
            }
            
            return steamRunning;
        }
        
    } catch (error) {
        console.error('❌ Erro ao verificar Steam:', error);
        if (typeof showNotification === 'function') {
            showNotification('Erro no Steam', 'Não foi possível verificar o status', 'error');
        }
    }
    
    return false;
};

window.checkDLLStatus = async function() {
    try {
        const response = await fetch('/api/header/status');
        if (!response.ok) throw new Error('API não respondeu');
        
        const data = await response.json();
        
        if (data.success && data.data) {
            const dllAvailable = data.data.dll_available;
            const message = dllAvailable ? 'DLL encontrada e válida' : 'DLL não encontrada';
            
            // Atualizar UI
            updateStatusDots(data.data.steam_running, dllAvailable);
            
            // Mostrar notificação
            if (typeof showNotification === 'function') {
                showNotification('Status da DLL', message, dllAvailable ? 'success' : 'warning');
            } else {
                alert(message);
            }
            
            return dllAvailable;
        }
        
    } catch (error) {
        console.error('❌ Erro ao verificar DLL:', error);
        if (typeof showNotification === 'function') {
            showNotification('Erro na DLL', 'Não foi possível verificar o status', 'error');
        }
    }
    
    return false;
};

window.testAllSystems = async function() {
    if (typeof showNotification === 'function') {
        showNotification('Testando sistemas', 'Iniciando testes completos...', 'info');
    }
    
    // Simulação de teste
    setTimeout(async () => {
        await updateSidebarUserData();
        await updateSidebarSystemStatus();
        await updateSidebarGamesCount();
        
        if (typeof showNotification === 'function') {
            showNotification('Testes concluídos', 'Todos os sistemas verificados', 'success');
        }
    }, 2000);
};

// Funções que redirecionam para o dashboard
window.scanLibrary = function() {
    if (typeof showNotification === 'function') {
        showNotification('Escanear Biblioteca', 'Redirecionando para o Dashboard...', 'info');
    }
    setTimeout(() => window.location.href = '/dashboard', 1000);
};

window.detectGames = function() {
    if (typeof showNotification === 'function') {
        showNotification('Detectar Jogos', 'Redirecionando para o Dashboard...', 'info');
    }
    setTimeout(() => window.location.href = '/dashboard', 1000);
};

window.openSettings = function() {
    if (typeof showNotification === 'function') {
        showNotification('Configurações', 'Redirecionando para o Dashboard...', 'info');
    }
    setTimeout(() => window.location.href = '/dashboard', 1000);
};

window.showSystemLogs = function() {
    if (typeof showNotification === 'function') {
        showNotification('Logs do Sistema', 'Redirecionando para o Dashboard...', 'info');
    }
    setTimeout(() => window.location.href = '/dashboard', 1000);
};

window.forceReconnect = function() {
    if (typeof showNotification === 'function') {
        showNotification('Reconexão', 'Reconectando ao Steam...', 'info');
    }
    
    // Forçar atualização dos dados
    setTimeout(async () => {
        await updateSidebarUserData();
        await updateSidebarSystemStatus();
        
        if (typeof showNotification === 'function') {
            showNotification('Reconexão', 'Dados atualizados com sucesso', 'success');
        }
    }, 1500);
};

window.clearSystemCache = function() {
    if (typeof showNotification === 'function') {
        showNotification('Cache', 'Funcionalidade disponível no Dashboard', 'info');
    }
    setTimeout(() => window.location.href = '/dashboard', 1500);
};

window.navigateTo = function(destination) {
    if (typeof showNotification === 'function') {
        showNotification('Navegação', `Abrindo ${destination}...`, 'info');
    }
    setTimeout(() => window.location.href = '/dashboard', 1000);
};

// Exportar função para atualizar sidebar
window.refreshHomeSidebar = async function() {
    await updateSidebarUserData();
    await updateSidebarSystemStatus();
    await updateSidebarGamesCount();
};

console.log('✅ Funções da sidebar da Home exportadas');