// frontend/js/notification.js - Sistema de Notificação Unificado e Robusto
// Versão 2.0 - Steam GameLoader Ultimate

console.log('🔔 Sistema de Notificação Unificado: Inicializando...');

class UnifiedNotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = new Map(); // Para controle de instâncias
        this.config = {
            MAX_NOTIFICATIONS: 5,
            DEFAULT_DURATION: 7000, // 7 segundos
            ANIMATION_DURATION: 300,
            CONTAINER_ID: 'unified-notification-container'
        };
        
        this.initialize();
    }
    
    initialize() {
        console.log('🎯 Inicializando sistema de notificação unificado...');
        
        // Criar ou obter container
        let container = document.getElementById(this.config.CONTAINER_ID);
        if (!container) {
            container = this.createContainer();
        }
        
        this.container = container;
        
        // Remover qualquer script conflitante
        this.cleanupConflictingSystems();
        
        // Adicionar estilos dinâmicos se necessário
        this.injectStyles();
        
        console.log('✅ Sistema de notificação unificado inicializado');
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.id = this.config.CONTAINER_ID;
        container.className = 'unified-notification-container';
        
        // Posicionamento fixo (não interfere com outros elementos)
        Object.assign(container.style, {
            position: 'fixed',
            top: '90px',
            right: '20px',
            zIndex: '9998',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            maxWidth: '400px',
            pointerEvents: 'none' // Permite cliques através do container
        });
        
        document.body.appendChild(container);
        return container;
    }
    
    injectStyles() {
        // Evitar duplicação de estilos
        if (document.getElementById('unified-notification-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'unified-notification-styles';
        style.textContent = `
            .unified-notification-container {
                position: fixed;
                top: 90px;
                right: 20px;
                z-index: 9998;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
                pointer-events: none;
            }
            
            .unified-notification {
                background: rgba(20, 16, 41, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 12px;
                padding: 20px;
                display: flex;
                align-items: flex-start;
                gap: 15px;
                border: 1px solid;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                animation: unifiedNotificationSlideIn 0.3s ease;
                max-width: 400px;
                pointer-events: auto;
                transform-origin: top right;
            }
            
            @keyframes unifiedNotificationSlideIn {
                from { 
                    transform: translateX(100%) scale(0.9);
                    opacity: 0;
                }
                to { 
                    transform: translateX(0) scale(1);
                    opacity: 1;
                }
            }
            
            .unified-notification.success {
                border-color: #00ff88;
                background: rgba(0, 255, 136, 0.05);
            }
            
            .unified-notification.error {
                border-color: #ff2a6d;
                background: rgba(255, 42, 109, 0.05);
            }
            
            .unified-notification.warning {
                border-color: #ffaa00;
                background: rgba(255, 170, 0, 0.05);
            }
            
            .unified-notification.info {
                border-color: #7a2aff;
                background: rgba(122, 42, 255, 0.05);
            }
            
            .unified-notification-icon {
                font-size: 1.5rem;
                flex-shrink: 0;
                margin-top: 2px;
            }
            
            .unified-notification.success .unified-notification-icon {
                color: #00ff88;
            }
            
            .unified-notification.error .unified-notification-icon {
                color: #ff2a6d;
            }
            
            .unified-notification.warning .unified-notification-icon {
                color: #ffaa00;
            }
            
            .unified-notification.info .unified-notification-icon {
                color: #7a2aff;
            }
            
            .unified-notification-content {
                flex: 1;
                min-width: 0;
            }
            
            .unified-notification-title {
                font-family: 'Orbitron', sans-serif;
                font-weight: 700;
                font-size: 1rem;
                color: white;
                margin-bottom: 5px;
                line-height: 1.2;
            }
            
            .unified-notification-message {
                color: rgba(168, 178, 201, 0.9);
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .unified-notification-close {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                color: rgba(168, 178, 201, 0.5);
                cursor: pointer;
                font-size: 1rem;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s ease;
                flex-shrink: 0;
                margin-left: 5px;
            }
            
            .unified-notification-close:hover {
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }
            
            .unified-notification-fade-out {
                animation: unifiedNotificationFadeOut 0.3s ease forwards;
            }
            
            @keyframes unifiedNotificationFadeOut {
                from { 
                    transform: translateX(0) scale(1);
                    opacity: 1;
                }
                to { 
                    transform: translateX(100%) scale(0.9);
                    opacity: 0;
                }
            }
            
            /* Responsividade */
            @media (max-width: 768px) {
                .unified-notification-container {
                    top: 80px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
                
                .unified-notification {
                    max-width: none;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    cleanupConflictingSystems() {
        // Remover containers de notificação conflitantes
        const conflictingIds = [
            'notificationContainer',
            'home-notification-container',
            'search-notification-container'
        ];
        
        conflictingIds.forEach(id => {
            const element = document.getElementById(id);
            if (element && element !== this.container) {
                element.remove();
                console.log(`🧹 Removido container conflitante: ${id}`);
            }
        });
        
        // Remover event listeners conflitantes
        window.showNotification = this.show.bind(this);
        window.showError = (title, message) => this.show(title, message, 'error');
        window.showSuccess = (title, message) => this.show(title, message, 'success');
        window.showWarning = (title, message) => this.show(title, message, 'warning');
        window.showInfo = (title, message) => this.show(title, message, 'info');
    }
    
    show(title, message, type = 'info', duration = this.config.DEFAULT_DURATION) {
        // Validar entradas
        if (!title && !message) {
            console.warn('⚠️ Notificação ignorada: título e mensagem vazios');
            return null;
        }
        
        // Gerar ID único
        const notificationId = 'unified_notif_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        // Limitar número de notificações (mantém as mais recentes)
        this.limitNotifications();
        
        // Criar elemento da notificação
        const notification = this.createNotificationElement(notificationId, title, message, type);
        
        // Adicionar ao container
        this.container.appendChild(notification);
        
        // Registrar no mapa
        this.notifications.set(notificationId, {
            element: notification,
            timeoutId: null,
            createdAt: Date.now()
        });
        
        // Configurar auto-remoção
        if (duration > 0) {
            const timeoutId = setTimeout(() => {
                this.close(notificationId);
            }, duration);
            
            this.notifications.get(notificationId).timeoutId = timeoutId;
        }
        
        // Configurar evento de fechamento
        const closeBtn = notification.querySelector('.unified-notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close(notificationId));
        }
        
        // Log
        console.log(`🔔 Notificação [${type.toUpperCase()}]: ${title} - ${message.substring(0, 50)}...`);
        
        return notificationId;
    }
    
    createNotificationElement(id, title, message, type) {
        // Ícones por tipo
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const notification = document.createElement('div');
        notification.id = id;
        notification.className = `unified-notification ${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'polite');
        
        notification.innerHTML = `
            <div class="unified-notification-icon">
                <i class="fas ${icons[type] || 'fa-info-circle'}"></i>
            </div>
            <div class="unified-notification-content">
                <div class="unified-notification-title">${this.escapeHtml(title)}</div>
                <div class="unified-notification-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="unified-notification-close" aria-label="Fechar notificação">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return notification;
    }
    
    close(notificationId) {
        const notificationData = this.notifications.get(notificationId);
        if (!notificationData) return;
        
        const { element, timeoutId } = notificationData;
        
        // Limpar timeout se existir
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        
        // Animar saída
        if (element) {
            element.classList.add('unified-notification-fade-out');
            
            // Remover após animação
            setTimeout(() => {
                if (element.parentElement) {
                    element.remove();
                }
                this.notifications.delete(notificationId);
            }, this.config.ANIMATION_DURATION);
        } else {
            this.notifications.delete(notificationId);
        }
    }
    
    closeAll() {
        console.log('🧹 Fechando todas as notificações...');
        Array.from(this.notifications.keys()).forEach(id => {
            this.close(id);
        });
    }
    
    limitNotifications() {
        // Remove as notificações mais antigas se exceder o limite
        const notifications = Array.from(this.notifications.entries());
        
        if (notifications.length >= this.config.MAX_NOTIFICATIONS) {
            // Ordenar por criação (mais antigas primeiro)
            notifications.sort((a, b) => a[1].createdAt - b[1].createdAt);
            
            // Remover o excesso (mantém MAX_NOTIFICATIONS - 1 para adicionar a nova)
            const toRemove = notifications.slice(0, notifications.length - (this.config.MAX_NOTIFICATIONS - 1));
            
            toRemove.forEach(([id]) => {
                this.close(id);
            });
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
    
    // Métodos estáticos para tipos específicos
    success(title, message, duration = this.config.DEFAULT_DURATION) {
        return this.show(title, message, 'success', duration);
    }
    
    error(title, message, duration = this.config.DEFAULT_DURATION) {
        return this.show(title, message, 'error', duration);
    }
    
    warning(title, message, duration = this.config.DEFAULT_DURATION) {
        return this.show(title, message, 'warning', duration);
    }
    
    info(title, message, duration = this.config.DEFAULT_DURATION) {
        return this.show(title, message, 'info', duration);
    }
}

// Criar instância global única
const unifiedNotificationSystem = new UnifiedNotificationSystem();

// Exportar para uso global
window.unifiedNotifications = unifiedNotificationSystem;
window.showNotification = unifiedNotificationSystem.show.bind(unifiedNotificationSystem);
window.showErrorNotification = unifiedNotificationSystem.error.bind(unifiedNotificationSystem);
window.showSuccessNotification = unifiedNotificationSystem.success.bind(unifiedNotificationSystem);
window.showWarningNotification = unifiedNotificationSystem.warning.bind(unifiedNotificationSystem);
window.showInfoNotification = unifiedNotificationSystem.info.bind(unifiedNotificationSystem);

// Inicialização automática quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('✅ Sistema de Notificação Unificado carregado e pronto');
    });
} else {
    console.log('✅ Sistema de Notificação Unificado carregado e pronto');
}

console.log('🔔 Sistema de Notificação Unificado inicializado com sucesso!');