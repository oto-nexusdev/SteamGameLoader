// frontend/js/header.js - JS OTIMIZADO PARA HEADER
(function() {
    'use strict';
    
    console.log('🔧 Steam GameLoader Header: Inicializando...');
    
    // ====== ATUALIZAÇÃO DO USUÁRIO ======
    function updateUserInfo() {
        const usernameDisplay = document.getElementById('username-display');
        const greetingText = document.getElementById('greeting-text');
        
        if (!usernameDisplay || !greetingText) return;
        
        try {
            // Já está definido no HTML: "Otto.Nexus" e "Boa noite,"
            // Manter os valores estáticos da imagem
            const usernameSpan = usernameDisplay.querySelector('.username-text');
            if (usernameSpan && usernameSpan.textContent === 'Carregando...') {
                usernameSpan.textContent = 'Otto.Nexus';
            }
            
            greetingText.textContent = 'Boa noite,';
            
        } catch (error) {
            console.log('Usando dados padrão do usuário');
        }
    }
    
    // ====== FUNÇÃO DE ATUALIZAÇÃO FORÇADA ======
    window.forceRefreshAll = function() {
        console.log('🔄 Header: Atualização forçada solicitada');
        const refreshBtn = document.querySelector('.refresh-btn');
        
        if (refreshBtn) {
            refreshBtn.classList.add('rotating');
            refreshBtn.style.pointerEvents = 'none';
            
            // Disparar evento para outros componentes
            document.dispatchEvent(new CustomEvent('header-refresh-requested', {
                detail: { timestamp: new Date().toISOString() }
            }));
            
            // Simular tempo de atualização
            setTimeout(() => {
                refreshBtn.classList.remove('rotating');
                refreshBtn.style.pointerEvents = 'auto';
                
                console.log('✅ Header: Atualização concluída');
            }, 800);
        }
    };
    
    // ====== INJEÇÃO DE ANIMAÇÕES ======
    function injectAnimations() {
        if (document.querySelector('#header-animations')) return;
        
        const style = document.createElement('style');
        style.id = 'header-animations';
        style.textContent = `
            @keyframes spinFull {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .refresh-btn.rotating i {
                animation: spinFull 0.8s linear infinite;
            }
            
            .status-badge.loading {
                opacity: 0.7;
            }
            
            .status-badge.loading .status-pulse {
                animation: pulseFast 0.8s infinite;
                background: #7a2aff !important;
            }
            
            @keyframes pulseFast {
                0%, 100% { 
                    opacity: 0.5;
                    transform: translateY(-50%) scale(0.8);
                }
                50% { 
                    opacity: 1;
                    transform: translateY(-50%) scale(1.2);
                }
            }
            
            .status-badge:active {
                transform: scale(0.98) !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    // ====== ATUALIZAÇÃO DE SAUDAÇÃO BASEADA NO HORÁRIO ======
    function updateGreetingBasedOnTime() {
        const greetingText = document.getElementById('greeting-text');
        if (!greetingText) return;
        
        const hour = new Date().getHours();
        let greeting;
        
        if (hour >= 5 && hour < 12) {
            greeting = 'Bom dia,';
        } else if (hour >= 12 && hour < 18) {
            greeting = 'Boa tarde,';
        } else {
            greeting = 'Boa noite,';
        }
        
        greetingText.textContent = greeting;
    }
    
    // ====== INICIALIZAÇÃO ======
    async function initializeHeader() {
        console.log('🚀 Header: Inicializando...');
        
        injectAnimations();
        updateUserInfo();
        updateGreetingBasedOnTime();
        
        // Atualizar saudação a cada hora
        setInterval(updateGreetingBasedOnTime, 3600000);
        
        // Evento de inicialização
        document.dispatchEvent(new CustomEvent('header-ready', {
            detail: { 
                version: '19.0',
                status: 'funcional',
                timestamp: new Date().toISOString()
            }
        }));
        
        console.log('✅ Header carregado com sucesso');
    }
    
    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeHeader);
    } else {
        setTimeout(initializeHeader, 50);
    }
    
})();