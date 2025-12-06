# webview_config.py - Configurações específicas para WebView no EXE - VERSÃO COM ZOOM E MAXIMIZADO
import os
import sys
import tempfile
import logging
import time
import traceback
import webbrowser

def setup_webview_logging():
    """Configura logging seguro para WebView"""
    logger = logging.getLogger('WebViewConfig')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def safe_log_message(message):
    """Remove emojis para logging seguro"""
    if not isinstance(message, str):
        return str(message)
    
    replacements = {
        '✅': '[OK]', '⚠️': '[WARN]', '❌': '[ERROR]', 
        '🚀': '[START]', '🔧': '[CONFIG]', '🎯': '[SUCCESS]',
        '📦': '[EXE]', '🔴': '[STOP]', '📊': '[STATUS]',
        '📁': '[FOLDER]', '🔍': '[CHECK]', '🔎': '[ZOOM]'
    }
    
    for emoji, replacement in replacements.items():
        message = message.replace(emoji, replacement)
    
    return message

def setup_webview_for_exe():
    """
    Configura o WebView para funcionar corretamente no EXE - VERSÃO ROBUSTA
    """
    logger = setup_webview_logging()
    
    try:
        # Configura o diretório temporário para o WebView
        if getattr(sys, 'frozen', False):
            # Está rodando como EXE
            base_path = sys._MEIPASS
            temp_dir = os.path.join(tempfile.gettempdir(), 'steam_gameloader_webview')
            
            # Cria diretório temporário se não existir
            os.makedirs(temp_dir, exist_ok=True)
            
            # Configura variáveis de ambiente para WebView
            os.environ['WEBVIEW_TEMP'] = temp_dir
            os.environ['WEBVIEW_BASE_PATH'] = base_path
            os.environ['WEBVIEW_ALLOW_FILE_ACCESS'] = '1'
            
            log_once(logger, "WebView configurado para EXE", key="webview_exe_config")
            log_once(logger, f"Base path: {base_path}", key="webview_base_path")
            log_once(logger, f"Temp dir: {temp_dir}", key="webview_temp_dir")
            
            return base_path, temp_dir
        else:
            # Está rodando como script
            base_path = os.path.dirname(os.path.abspath(__file__))
            log_once(logger, "WebView configurado para modo script", key="webview_script_config")
            return base_path, None
            
    except Exception as e:
        log_once(logger, f"Erro na configuracao WebView: {e}", level=logging.ERROR, key="webview_config_error")
        return None, None

def get_webview_settings():
    """
    Retorna configurações otimizadas para WebView no EXE - VERSÃO COM ZOOM
    """
    return {
        'debug': False,
        'http_server': False,
        'user_agent': 'SteamGameLoader/2.0',
        'private_mode': True,
        'focus': True,
        'on_top': False,
        'background_color': '#070307',
        'frameless': False,
        'easy_drag': True,
        'confirm_close': False,
    }

def get_webview_window_params():
    """
    Retorna parâmetros separados para a criação da janela - VERSÃO COM ZOOM
    """
    return {
        'width': 1200,
        'height': 800,
        'min_size': (800, 600),
        'resizable': True,
        'fullscreen': False,
        'frameless': False,
        'easy_drag': True,
        'focus': True,
        'on_top': False,
        'background_color': '#070307',
        'text_select': False,
        'confirm_close': True
    }

def get_webview_compatibility_settings():
    """
    Retorna configurações de compatibilidade para diferentes versões do pywebview
    """
    return {
        'debug': False,
        'http_server': False,
        'user_agent': 'SteamGameLoader/2.0 (Windows NT 10.0; Win64; x64)',
        'private_mode': True
    }

# ✅ CONFIGURAÇÕES DE ZOOM E RESOLUÇÃO
def get_zoom_settings():
    """
    Retorna configurações de zoom ajustáveis
    Valores possíveis: 0.5 (50%) a 2.0 (200%)
    """
    return {
        'default_zoom': 0.95,      
        'min_zoom': 0.5,          # 50% - zoom mínimo
        'max_zoom': 2.0,          # 200% - zoom máximo
        'zoom_step': 0.1,         # Incremento/decremento do zoom
        'remember_zoom': True,    # Lembrar configuração de zoom
    }

def get_resolution_settings():
    """
    Retorna configurações de resolução e tamanho da janela
    """
    return {
        'start_maximized': True,      # ✅ SEMPRE INICIAR MAXIMIZADO
        'default_width': 1400,        # Largura padrão se não maximizado
        'default_height': 900,        # Altura padrão se não maximizado
        'min_width': 1000,
        'min_height': 700,
        'max_width': 3840,           # Suporte a 4K
        'max_height': 2160,
        'auto_adjust_to_screen': True, # Ajustar automaticamente ao tamanho da tela
    }

# ✅ NOVAS FUNÇÕES PARA LAUNCHER ESPECÍFICO COM ZOOM
def get_launcher_settings():
    """
    Configurações específicas para o modo Launcher - VERSÃO COM ZOOM
    """
    zoom_config = get_zoom_settings()
    
    return {
        'debug': False,
        'http_server': False,
        'user_agent': 'SteamGameLoader-Launcher/2.0',
        'private_mode': True,
        'focus': True,
        'on_top': False,
        'background_color': '#070307',
        'frameless': False,
        'easy_drag': True,
        'confirm_close': True,
        'zoom': zoom_config['default_zoom'],  # ✅ ZOOM APLICADO
    }

def get_launcher_window_params():
    """
    Parâmetros otimizados para a janela do Launcher - VERSÃO COM MAXIMIZADO E ZOOM
    """
    resolution_config = get_resolution_settings()
    zoom_config = get_zoom_settings()
    
    return {
        'width': resolution_config['default_width'],
        'height': resolution_config['default_height'],
        'min_size': (resolution_config['min_width'], resolution_config['min_height']),
        'resizable': True,
        'fullscreen': False,
        'frameless': False,
        'easy_drag': True,
        'focus': True,
        'on_top': False,
        'background_color': '#070307',
        'text_select': False,
        'confirm_close': True,
        'zoom': zoom_config['default_zoom'],  # ✅ ZOOM APLICADO
    }

def apply_zoom_to_window(window, zoom_level=None):
    """
    Aplica zoom à janela WebView - FUNÇÃO CRÍTICA
    """
    logger = setup_webview_logging()
    
    try:
        if zoom_level is None:
            zoom_config = get_zoom_settings()
            zoom_level = zoom_config['default_zoom']
        
        # Garante que o zoom está dentro dos limites
        zoom_config = get_zoom_settings()
        zoom_level = max(zoom_config['min_zoom'], min(zoom_config['max_zoom'], zoom_level))
        
        # Aplica zoom usando a API do pywebview
        if hasattr(window, 'evaluate_js'):
            js_zoom_code = f"""
                document.body.style.zoom = '{zoom_level}';
                document.documentElement.style.zoom = '{zoom_level}';
            """
            window.evaluate_js(js_zoom_code)
            log_once(logger, f"🔎 Zoom aplicado: {zoom_level*100}%", key="zoom_applied")
            return True
        else:
            log_once(logger, "⚠️ evaluate_js não disponível para aplicar zoom", key="zoom_not_available")
            return False
            
    except Exception as e:
        log_once(logger, f"❌ Erro ao aplicar zoom: {e}", level=logging.ERROR, key="zoom_error")
        return False

def setup_zoom_controls(window):
    """
    Configura controles de zoom (teclas de atalho) - FUNÇÃO IMPORTANTE
    """
    logger = setup_webview_logging()
    
    try:
        # Configura atalhos de teclado para zoom
        def handle_key_event(event):
            try:
                # Ctrl++ para zoom in
                if event.get('key') == 'Add' and event.get('ctrl'):
                    current_zoom = getattr(window, '_current_zoom', get_zoom_settings()['default_zoom'])
                    zoom_config = get_zoom_settings()
                    new_zoom = min(zoom_config['max_zoom'], current_zoom + zoom_config['zoom_step'])
                    apply_zoom_to_window(window, new_zoom)
                    window._current_zoom = new_zoom
                    
                # Ctrl+- para zoom out
                elif event.get('key') == 'Subtract' and event.get('ctrl'):
                    current_zoom = getattr(window, '_current_zoom', get_zoom_settings()['default_zoom'])
                    zoom_config = get_zoom_settings()
                    new_zoom = max(zoom_config['min_zoom'], current_zoom - zoom_config['zoom_step'])
                    apply_zoom_to_window(window, new_zoom)
                    window._current_zoom = new_zoom
                    
                # Ctrl+0 para reset zoom
                elif event.get('key') == '0' and event.get('ctrl'):
                    zoom_config = get_zoom_settings()
                    apply_zoom_to_window(window, zoom_config['default_zoom'])
                    window._current_zoom = zoom_config['default_zoom']
                    
            except Exception as e:
                logger.warning(f"Erro no controle de zoom: {e}")
        
        # Registra handler de eventos se disponível
        if hasattr(window, 'events'):
            try:
                window.events.shown += lambda: apply_zoom_to_window(window)
                log_once(logger, "🔎 Controles de zoom configurados", key="zoom_controls_setup")
            except Exception as e:
                logger.warning(f"Eventos de zoom não disponíveis: {e}")
                
    except Exception as e:
        logger.warning(f"Configuração de controles de zoom falhou: {e}")

def maximize_window_safe(window):
    """
    Maximiza a janela de forma segura - FUNÇÃO CRÍTICA
    """
    logger = setup_webview_logging()
    
    try:
        resolution_config = get_resolution_settings()
        
        if resolution_config['start_maximized']:
            if hasattr(window, 'maximize'):
                window.maximize()
                log_once(logger, "📊 Janela maximizada automaticamente", key="window_maximized")
                return True
            else:
                log_once(logger, "⚠️ Função maximize não disponível", key="maximize_not_available")
                return False
        return False
        
    except Exception as e:
        log_once(logger, f"❌ Erro ao maximizar janela: {e}", level=logging.ERROR, key="maximize_error")
        return False

def check_webview_availability():
    """
    Verifica se o WebView está disponível e funcionando
    """
    logger = setup_webview_logging()
    
    try:
        import webview
        version = getattr(webview, '__version__', 'Unknown')
        log_once(logger, f"PyWebView disponivel - Versao: {version}", key="webview_version")
        return True, version
    except ImportError as e:
        log_once(logger, f"PyWebView nao disponivel: {e}", level=logging.ERROR, key="webview_not_available")
        return False, None
    except Exception as e:
        log_once(logger, f"Erro ao verificar WebView: {e}", level=logging.ERROR, key="webview_check_error")
        return False, None

def optimize_webview_performance():
    """
    Otimiza performance do WebView com configurações específicas
    """
    # Configurações de performance para WebView
    performance_settings = {
        'disable_accelerated_2d_canvas': False,
        'disable_background_timer_throttling': True,
        'disable_renderer_backgrounding': True,
        'enable_fast_unload': True,
        'enable_webgl': True,
        'javascript_can_access_clipboard': True,
        'allow_file_access_from_files': True,
        'allow_universal_access_from_file_urls': True
    }
    
    # Aplica configurações se possível
    try:
        import webview
        for key, value in performance_settings.items():
            try:
                setattr(webview.settings, key, value)
            except:
                pass  # Ignora atributos não disponíveis
    except:
        pass  # Ignora se não for possível configurar
    
    return performance_settings

# ✅ FUNÇÕES MOVIDAS DO MAIN.PY - ATUALIZADAS COM ZOOM

def get_webview_settings_compat():
    """Configurações WebView compatíveis - VERSÃO COM ZOOM"""
    try:
        return get_webview_settings()
    except:
        return {
            'debug': False,
            'http_server': False,
            'user_agent': 'SteamGameLoader/2.0',
            'private_mode': True
        }

def get_webview_window_params_compat():
    """Parâmetros da janela WebView - VERSÃO COM ZOOM"""
    try:
        return get_webview_window_params()
    except:
        return {
            'width': 1400,
            'height': 900,
            'min_size': (1000, 700),
            'resizable': True,
            'fullscreen': False
        }

def open_webview_launcher():
    """Abre WebView como launcher interno - VERSÃO COM ZOOM E MAXIMIZADO (MAIN THREAD)"""
    logger = setup_webview_logging()
    
    time.sleep(2.5)  # Espera o Flask iniciar
    
    try:
        import webview
        
        logger.info("[LAUNCHER] Iniciando launcher interno WebView...")
        
        # ✅ CONFIGURAÇÕES OTIMIZADAS PARA LAUNCHER COM ZOOM
        try:
            window_params = get_launcher_window_params()
        except:
            logger.warning("[WARN] Função get_launcher_window_params não disponível, usando fallback")
            window_params = {
                'width': 1400,
                'height': 900,
                'min_size': (1000, 700),
                'resizable': True,
                'fullscreen': False,
                'frameless': False,
                'easy_drag': True,
                'focus': True,
                'on_top': False,
                'background_color': '#070307',
                'text_select': False,
                'zoom': 0.9  # ✅ ZOOM PADRÃO 90%
            }
        
        # ✅ CORREÇÃO: Remove parâmetros problemáticos e aplica zoom
        safe_params = {
            'width': window_params.get('width', 1400),
            'height': window_params.get('height', 900),
            'min_size': window_params.get('min_size', (1000, 700)),
            'resizable': window_params.get('resizable', True),
            'fullscreen': window_params.get('fullscreen', False),
            'frameless': window_params.get('frameless', False),
            'easy_drag': window_params.get('easy_drag', True),
            'focus': window_params.get('focus', True),
            'on_top': window_params.get('on_top', False),
            'background_color': window_params.get('background_color', '#070307'),
            'text_select': window_params.get('text_select', False)
        }
        
        logger.info(f"[LAUNCHER] Criando janela com parâmetros: {safe_params}")
        
        # ✅ CRIA JANELA WEBVIEW
        window = webview.create_window(
            title='Steam GameLoader - Launcher',
            url='http://localhost:5000',
            **safe_params
        )
        
        # ✅ CONFIGURA ZOOM INICIAL
        initial_zoom = window_params.get('zoom', 0.9)
        window._current_zoom = initial_zoom
        
        # ✅ EVENTOS PARA CONTROLE DO LAUNCHER
        def on_loaded():
            logger.info("[LAUNCHER] Interface carregada completamente")
            # Aplica zoom após o carregamento
            apply_zoom_to_window(window, initial_zoom)
            
        def on_closing():
            logger.info("[LAUNCHER] Launcher fechando - encerrando aplicação...")
            # Encerra tudo de forma segura
            os._exit(0)
            
        def on_shown():
            logger.info("[LAUNCHER] Launcher visível e pronto para uso")
            # ✅ MAXIMIZA JANELA APÓS SER MOSTRADA
            maximize_window_safe(window)
            # ✅ CONFIGURA CONTROLES DE ZOOM
            setup_zoom_controls(window)
            
        # Configura eventos se disponíveis
        if hasattr(window, 'events'):
            try:
                window.events.loaded += on_loaded
                window.events.closing += on_closing
                window.events.shown += on_shown
                logger.info("[LAUNCHER] Eventos configurados com sucesso")
            except Exception as e:
                logger.warning(f"[LAUNCHER] Eventos não disponíveis: {e}")
        
        # ✅ INICIA WEBVIEW EM MODO SEGURO
        logger.info("[LAUNCHER] Iniciando WebView em modo launcher...")
        
        webview.start(
            debug=False,
            http_server=False,
            user_agent='SteamGameLoader-Launcher/2.0'
        )
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Falha no launcher interno: {str(e)}")
        logger.error(f"[ERROR] Tipo: {type(e).__name__}")
        
        # Log detalhado para debugging
        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        
        # Fallback para navegador
        logger.info("[FALLBACK] Usando navegador padrão como fallback")
        open_browser_safe()
        return False

def open_browser_safe():
    """Abre navegador de forma segura - FALLBACK"""
    time.sleep(3.0)
    try:
        logger = setup_webview_logging()
        logger.info("[FALLBACK] Abrindo navegador padrão")
        webbrowser.open("http://localhost:5000")
    except Exception as e:
        logger.error(f"[ERROR] Fallback também falhou: {e}")

# ✅ CORREÇÃO: Sistema de log_once para evitar logs repetidos
_LAST_WEBVIEW_LOG_MESSAGE = {}
_LAST_WEBVIEW_LOG_TIME = {}

def log_once(logger, message, level=logging.INFO, key=None, cooldown=3.0):
    """Log que evita mensagens repetidas consecutivas"""
    global _LAST_WEBVIEW_LOG_MESSAGE, _LAST_WEBVIEW_LOG_TIME
    
    if key is None:
        key = message
    
    import time
    current_time = time.time()
    
    # Verifica se é a mesma mensagem e se foi logada recentemente
    if (key in _LAST_WEBVIEW_LOG_MESSAGE and 
        _LAST_WEBVIEW_LOG_MESSAGE[key] == message and 
        current_time - _LAST_WEBVIEW_LOG_TIME.get(key, 0) < cooldown):
        return False
    
    # Atualiza registro do último log
    _LAST_WEBVIEW_LOG_MESSAGE[key] = message
    _LAST_WEBVIEW_LOG_TIME[key] = current_time
    
    # Faz o log real
    safe_message = safe_log_message(message)
    if level == logging.INFO:
        logger.info(safe_message)
    elif level == logging.WARNING:
        logger.warning(safe_message)
    elif level == logging.ERROR:
        logger.error(safe_message)
    elif level == logging.DEBUG:
        logger.debug(safe_message)
    
    return True

# Inicialização automática quando o módulo é importado
def initialize_webview_module():
    """
    Inicializa o módulo WebView automaticamente
    """
    logger = setup_webview_logging()
    log_once(logger, "Inicializando modulo WebView...", key="webview_module_init")
    
    # Configura ambiente para EXE
    base_path, temp_dir = setup_webview_for_exe()
    
    # Verifica disponibilidade
    available, version = check_webview_availability()
    
    # Otimiza performance
    perf_settings = optimize_webview_performance()
    
    log_once(logger, f"Modulo WebView inicializado - Disponivel: {available}, Versao: {version}", 
             key="webview_module_ready")
    
    return {
        'available': available,
        'version': version,
        'base_path': base_path,
        'temp_dir': temp_dir,
        'performance_settings': perf_settings,
        'zoom_settings': get_zoom_settings(),
        'resolution_settings': get_resolution_settings()
    }

# Executa inicialização automática
webview_status = initialize_webview_module()

# Teste do módulo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== TESTE WEBVIEW CONFIG ===")
    print(f"Disponível: {webview_status['available']}")
    print(f"Versão: {webview_status['version']}")
    print(f"Base Path: {webview_status['base_path']}")
    print(f"Temp Dir: {webview_status['temp_dir']}")
    print("Configurações Zoom:", get_zoom_settings())
    print("Configurações Resolução:", get_resolution_settings())
    print("Configurações:", get_webview_settings())
    print("Parâmetros Janela:", get_webview_window_params())
    print("Configurações Launcher:", get_launcher_settings())
    print("Parâmetros Launcher:", get_launcher_window_params())
    print("=============================")