import os
import sys
import time
import json
import threading
import traceback
import webbrowser
import logging
from pathlib import Path
from datetime import datetime, date

# ------------------ CONFIGURAÇÃO DE ENCODING ------------------
def setup_encoding():
    """Configura encoding seguro para Windows"""
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['PYTHONUTF8'] = '1'
        except:
            pass

setup_encoding()

# ------------------ CONFIGURAÇÃO DE LOGGING ------------------
class SafeLogger:
    @staticmethod
    def setup_logging():
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log', encoding='utf-8')
            ]
        )
        
        logger = logging.getLogger("main")
        return logger

logger = SafeLogger.setup_logging()

# ------------------ CONFIGURAÇÃO DE PATHS ------------------
def setup_exe_environment():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        current_dir = os.path.dirname(sys.executable)
        
        logger.info("[EXE] Modo EXE detectado")
        logger.info("[EXE] Base path: " + str(base_path))
        logger.info("[EXE] Current dir: " + str(current_dir))
        
        frontend_path_exe = os.path.join(base_path, 'frontend')
        
        if not os.path.exists(frontend_path_exe):
            logger.warning("[EXE] Frontend não encontrado em MEIPASS, usando current_dir")
            frontend_path_exe = os.path.join(current_dir, 'frontend')
        
        logger.info("[EXE] Frontend path final: " + str(frontend_path_exe))
        return frontend_path_exe, current_dir, base_path
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_path_script = os.path.join(current_dir, "frontend")
        logger.info("[SCRIPT] Modo script detectado")
        logger.info("[SCRIPT] Frontend path: " + str(frontend_path_script))
        return frontend_path_script, current_dir, current_dir

frontend_path, current_dir, base_path = setup_exe_environment()
parent_dir = os.path.dirname(current_dir)

sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "utils"))
sys.path.insert(0, os.path.join(current_dir, "config"))
sys.path.insert(0, parent_dir)

# ✅ VARIÁVEL GLOBAL CRÍTICA: Instância única do DownloadManager
DOWNLOAD_MANAGER_INSTANCE = None

# ------------------ IMPORTAÇÃO DIRETA SEM FALLBACKS ------------------
def import_module(module_name, function_names=None):
    """Importa módulos diretamente - SEM FALLBACKS"""
    try:
        module = __import__(module_name, fromlist=['*'])
        logger.info(f"[IMPORT] Importado: {module_name}")
        
        if function_names:
            functions = {}
            for func_name in function_names:
                try:
                    func = getattr(module, func_name)
                    functions[func_name] = func
                    logger.debug(f"[IMPORT] ✓ Função {func_name} carregada")
                except AttributeError as e:
                    logger.error(f"[IMPORT] ❌ Função {func_name} não encontrada em {module_name}: {e}")
                    # Não quebra o sistema, apenas registra o erro
                    functions[func_name] = None
            return functions
        return module
    except Exception as e:
        logger.error(f"[IMPORT] ❌ Erro ao importar {module_name}: {e}")
        return None

# ✅ CRÍTICO: Importação do download_logger.py (NOVO SISTEMA)
download_logger_funcs = import_module("utils.download_logger", [
    "download_logger"
])

# ✅ Importação do download_routes.py
download_routes_funcs = import_module("download_routes", [
    "setup_download_routes"
])
DOWNLOAD_ROUTES_AVAILABLE = bool(download_routes_funcs)

# ✅ CORREÇÃO: Importação COMPLETA do download_manager com todas as funções necessárias
download_manager_funcs = import_module("utils.download_manager", [
    "baixar_manifesto", "criar_gerenciador_download", "_verificar_disponibilidade_appid",
    "reset_download_cache"  # ✅ ADICIONADA para limpeza de cache
])
DOWNLOAD_MANAGER_AVAILABLE = bool(download_manager_funcs)

# ✅ CORREÇÃO: Importação correta do DLC Manager
dlc_manager_funcs = import_module("utils.dlc_manager", [
    "get_dlc_manager", "initialize_dlc_system"
])
DLC_MANAGER_AVAILABLE = bool(dlc_manager_funcs)

# ✅ CORREÇÃO: Importação do Fix Manager
fix_manager_funcs = import_module("utils.fix_manager", [
    "get_fix_manager", "initialize_fix_system"
])
FIX_MANAGER_AVAILABLE = bool(fix_manager_funcs)

# ✅ Steam Routes
steam_routes_funcs = import_module("steam_routes", [
    "setup_steam_routes", "make_json_safe", "safe_jsonify"
])
STEAM_ROUTES_AVAILABLE = bool(steam_routes_funcs)

# ✅ IMPORTANTE: Game Routes (NOVO - substitui as rotas duplicadas)
game_routes_funcs = import_module("game_routes", [
    "setup_game_routes", "detect_lua_games", "format_file_size"
])
GAME_ROUTES_AVAILABLE = bool(game_routes_funcs)

# ✅ Store Search
store_search_funcs = import_module("utils.store_search", [
    "buscar_jogos_steam", "obter_detalhes_jogo", "get_system_status"
])
STORE_SEARCH_AVAILABLE = bool(store_search_funcs)

# ✅ Steam Utils
steam_utils_funcs = import_module("utils.steam_utils", [
    "is_steam_running", "get_steam_info", "launch_steam", "kill_steam", 
    "get_steam_path", "force_kill_steam_safe", "validate_steam_directory",
    "get_steam_path_with_fallback", "clear_steam_cache", "detect_steam_path",
    "validate_steam_path_manual", "get_header_data", "force_header_refresh", 
    "get_steam_username"
])

# ✅ File Processing
file_processing_funcs = import_module("utils.file_processing", [
    "create_steam_backend", "process_downloaded_game_files",
    "create_zip_processor", "process_zip_upload"
])
FILE_PROCESSING_AVAILABLE = bool(file_processing_funcs)

# ✅ WebView Config
webview_config_funcs = import_module("webview_config", [
    "get_webview_settings", "get_webview_window_params",
    "get_webview_compatibility_settings", "check_webview_availability",
    "get_launcher_settings", "get_launcher_window_params",
    "open_webview_launcher", "open_browser_safe"
])
WEBVIEW_CONFIG_AVAILABLE = bool(webview_config_funcs)

# ✅ Game Management (removido - agora está em game_routes.py)
game_management_funcs = None  # ❌ REMOVIDO - substituído por game_routes.py

# ✅ DLL Manager
dll_manager_funcs = import_module("config.dll_manager", [
    "initialize_dll_system", "check_hid_dll_status", "get_detailed_dll_report",
    "recreate_hid_dll", "get_dll_simple_status", "ensure_hid_dll_initialized"
])

# Importar tray manager
try:
    from icon_tray import create_tray_manager
    TRAY_AVAILABLE = True
    logger.info("[TRAY] Tray Manager importado com sucesso")
except Exception as e:
    logger.error(f"[TRAY] ❌ Erro ao importar Tray Manager: {e}")
    TRAY_AVAILABLE = False

# ------------------ ATRIBUIÇÃO DAS FUNÇÕES COM VERIFICAÇÃO ------------------
def safe_get(funcs_dict, func_name, default=None):
    """Obtém função de forma segura com fallback"""
    if funcs_dict and func_name in funcs_dict and funcs_dict[func_name] is not None:
        return funcs_dict[func_name]
    logger.warning(f"[FUNC] ⚠️ Função {func_name} não disponível, usando fallback")
    return default

# ✅ NOVO: Download Logger
download_logger = safe_get(download_logger_funcs, "download_logger", None)

# ✅ Download Routes
setup_download_routes = safe_get(download_routes_funcs, "setup_download_routes", lambda x, y: None)

# ✅ IMPORTANTE: Game Routes (NOVO)
setup_game_routes = safe_get(game_routes_funcs, "setup_game_routes", lambda x, y: None)
detect_lua_games = safe_get(game_routes_funcs, "detect_lua_games", lambda x, y=True: {"success": False, "error": "Sistema não disponível"})
format_file_size = safe_get(game_routes_funcs, "format_file_size", lambda x: "0 B")

# ✅ Store Search
buscar_jogos_steam = safe_get(store_search_funcs, "buscar_jogos_steam", lambda x, y=20: {"success": False, "error": "Sistema não disponível"})
obter_detalhes_jogo = safe_get(store_search_funcs, "obter_detalhes_jogo", lambda x: {"success": False, "error": "Sistema não disponível"})
get_system_status = safe_get(store_search_funcs, "get_system_status", lambda: {"success": False, "error": "Sistema não disponível"})

# ✅ Download Manager - CORREÇÃO CRÍTICA
def get_download_manager_instance():
    """Obtém instância ÚNICA do DownloadManager (SINGLETON)"""
    global DOWNLOAD_MANAGER_INSTANCE
    
    if DOWNLOAD_MANAGER_INSTANCE is None:
        try:
            if callable(criar_gerenciador_download):
                DOWNLOAD_MANAGER_INSTANCE = criar_gerenciador_download()
                logger.info("[DM] ✅ Instância única do DownloadManager criada")
            else:
                logger.error("[DM] ❌ Função criar_gerenciador_download não disponível")
                return None
        except Exception as e:
            logger.error(f"[DM] ❌ Erro ao criar DownloadManager: {e}")
            return None
    
    return DOWNLOAD_MANAGER_INSTANCE

# ✅ Função wrapper para baixar_manifesto que usa singleton
def baixar_manifesto_safe(appid: str):
    """Função segura de download usando singleton"""
    try:
        manager = get_download_manager_instance()
        if manager and hasattr(manager, 'baixar_manifesto'):
            return manager.baixar_manifesto(appid)
        elif callable(baixar_manifesto):
            # Fallback para função direta
            return baixar_manifesto(appid)
        else:
            return {
                "success": False,
                "error": "DownloadManager não disponível",
                "appid": appid
            }
    except Exception as e:
        logger.error(f"[DM] ❌ Erro em baixar_manifesto_safe: {e}")
        return {
            "success": False,
            "error": f"Erro interno: {str(e)}",
            "appid": appid
        }

# ✅ Inicializar funções do Download Manager
baixar_manifesto = safe_get(download_manager_funcs, "baixar_manifesto", lambda x: {"success": False, "error": "Sistema não disponível"})
criar_gerenciador_download = safe_get(download_manager_funcs, "criar_gerenciador_download", lambda: None)
_verificar_disponibilidade_appid = safe_get(download_manager_funcs, "_verificar_disponibilidade_appid", lambda x: [])
reset_download_cache = safe_get(download_manager_funcs, "reset_download_cache", lambda: None)

# ✅ CORREÇÃO: DLC Manager
get_dlc_manager = safe_get(dlc_manager_funcs, "get_dlc_manager", lambda x=None: None)
initialize_dlc_system = safe_get(dlc_manager_funcs, "initialize_dlc_system", lambda x=None: None)

# ✅ Fix Manager
get_fix_manager = safe_get(fix_manager_funcs, "get_fix_manager", lambda x=None: None)
initialize_fix_system = safe_get(fix_manager_funcs, "initialize_fix_system", lambda x=None: None)

# ✅ Steam Utils
is_steam_running = safe_get(steam_utils_funcs, "is_steam_running", lambda: False)
get_steam_info = safe_get(steam_utils_funcs, "get_steam_info", lambda: {})
launch_steam = safe_get(steam_utils_funcs, "launch_steam", lambda: False)
kill_steam = safe_get(steam_utils_funcs, "kill_steam", lambda: False)
get_steam_path = safe_get(steam_utils_funcs, "get_steam_path", lambda: None)
force_kill_steam_safe = safe_get(steam_utils_funcs, "force_kill_steam_safe", lambda: False)
validate_steam_directory = safe_get(steam_utils_funcs, "validate_steam_directory", lambda x: False)
get_steam_path_with_fallback = safe_get(steam_utils_funcs, "get_steam_path_with_fallback", lambda: None)
clear_steam_cache = safe_get(steam_utils_funcs, "clear_steam_cache", lambda: False)
detect_steam_path = safe_get(steam_utils_funcs, "detect_steam_path", lambda: None)
validate_steam_path_manual = safe_get(steam_utils_funcs, "validate_steam_path_manual", lambda x: {"valid": False})
get_header_data = safe_get(steam_utils_funcs, "get_header_data", lambda: {})
force_header_refresh = safe_get(steam_utils_funcs, "force_header_refresh", lambda: {})
get_steam_username = safe_get(steam_utils_funcs, "get_steam_username", lambda: None)

# ✅ File Processing
create_zip_processor = safe_get(file_processing_funcs, "create_zip_processor", lambda: None)
process_zip_upload = safe_get(file_processing_funcs, "process_zip_upload", lambda x: {"success": False, "error": "Sistema não disponível"})

# ✅ WebView Config
get_webview_settings = safe_get(webview_config_funcs, "get_webview_settings", lambda: {})
get_webview_window_params = safe_get(webview_config_funcs, "get_webview_window_params", lambda: {})
get_webview_compatibility_settings = safe_get(webview_config_funcs, "get_webview_compatibility_settings", lambda: {})
check_webview_availability = safe_get(webview_config_funcs, "check_webview_availability", lambda: (False, "0.0"))
get_launcher_settings = safe_get(webview_config_funcs, "get_launcher_settings", lambda: {})
get_launcher_window_params = safe_get(webview_config_funcs, "get_launcher_window_params", lambda: {})
open_webview_launcher = safe_get(webview_config_funcs, "open_webview_launcher", lambda: False)
open_browser_safe = safe_get(webview_config_funcs, "open_browser_safe", lambda: None)

# ✅ IMPORTANTE: Game Management (removido - substituído)
create_game_manager = None  # ❌ REMOVIDO
setup_game_management_routes = None  # ❌ REMOVIDO

# ✅ DLL Manager
initialize_dll_system = safe_get(dll_manager_funcs, "initialize_dll_system", lambda: {"success": False})
check_hid_dll_status = safe_get(dll_manager_funcs, "check_hid_dll_status", lambda x=None: {"valid": False})
get_detailed_dll_report = safe_get(dll_manager_funcs, "get_detailed_dll_report", lambda: {"success": False})
recreate_hid_dll = safe_get(dll_manager_funcs, "recreate_hid_dll", lambda x=None: False)
get_dll_simple_status = safe_get(dll_manager_funcs, "get_dll_simple_status", lambda: {"success": False})
ensure_hid_dll_initialized = safe_get(dll_manager_funcs, "ensure_hid_dll_initialized", lambda: {"success": False})

# ------------------ IMPORTAÇÕES CONDICIONAIS ------------------
try:
    import webview
    PYWEBVIEW_AVAILABLE = True
    webview_available, webview_version = check_webview_availability()
    logger.info(f"[WEBVIEW] PyWebView importado - Versão: {webview_version}")
except ImportError:
    PYWEBVIEW_AVAILABLE = False
    logger.warning("[WEBVIEW] ❌ PyWebView não disponível")

try:
    from flask_cors import CORS
    FLASK_CORS_AVAILABLE = True
    logger.info("[CORS] Flask-CORS importado com sucesso")
except ImportError:
    FLASK_CORS_AVAILABLE = False
    logger.warning("[CORS] ❌ Flask-CORS não disponível")

from flask import Flask

# ------------------ FLASK APP ------------------
app = Flask(__name__, template_folder=frontend_path, static_folder=frontend_path)

if FLASK_CORS_AVAILABLE:
    CORS(app)
    logger.info("[FLASK] Aplicação Flask configurada com CORS")
else:
    logger.info("[FLASK] Aplicação Flask configurada SEM CORS")

# ------------------ ENCERRAMENTO DO STEAM ------------------
def force_kill_steam_processes():
    """Encerra processos Steam de forma segura"""
    logger.info("[STEAM] Encerrando processos Steam...")
    result = force_kill_steam_safe()
    if result:
        logger.info("[STEAM] Processos Steam encerrados com segurança")
    else:
        logger.warning("[STEAM] Não foi possível encerrar todos os processos Steam")
    return result

# ------------------ INICIALIZAÇÃO DO TRAY MANAGER ------------------
tray_manager = None
tray_started = False

def initialize_tray_system():
    """Inicializa o sistema de tray icon"""
    global tray_manager, tray_started
    
    if not TRAY_AVAILABLE:
        logger.warning("[TRAY] Sistema de tray não disponível")
        return False
        
    try:
        tray_manager = create_tray_manager()
        logger.info("[TRAY] Tray Manager criado")
        
        tray_started = tray_manager.start_tray()
        if tray_started:
            logger.info("[TRAY] Sistema de tray icon inicializado")
        else:
            logger.warning("[TRAY] Sistema de tray icon não iniciado")
            
        return tray_started
    except Exception as e:
        logger.error(f"[TRAY] ❌ Erro ao inicializar tray: {e}")
        return False

# ------------------ CONFIGURAÇÃO DAS ROTAS (VERSÃO DEFINITIVA) ------------------
def setup_routes():
    """Configura todas as rotas - VERSÃO DEFINITIVA CORRIGIDA"""
    try:
        from routes import setup_all_routes
        
        # ✅ CRIAÇÃO DEFINITIVA DO getattr_funcs
        getattr_funcs = {
            # ✅ SISTEMA DE BUSCA
            "buscar_jogos_steam": buscar_jogos_steam,
            "obter_detalhes_jogo": obter_detalhes_jogo,
            "get_system_status": get_system_status,
            
            # ✅ SISTEMA DE DOWNLOAD (CORRIGIDO)
            "baixar_manifesto": baixar_manifesto_safe,  # ✅ USA SINGLETON
            "_verificar_disponibilidade_appid": _verificar_disponibilidade_appid,
            "criar_gerenciador_download": criar_gerenciador_download,
            "reset_download_cache": reset_download_cache,
            "get_download_manager_instance": get_download_manager_instance,  # ✅ NOVA
            
            # ✅ SISTEMA DE LOG DE DOWNLOADS (NOVO)
            "download_logger": download_logger,
            
            # ✅ SISTEMA STEAM
            "is_steam_running": is_steam_running,
            "get_steam_info": get_steam_info,
            "launch_steam": launch_steam,
            "kill_steam": kill_steam,
            "get_steam_path": get_steam_path,
            "force_kill_steam_safe": force_kill_steam_safe,
            "validate_steam_directory": validate_steam_directory,
            "get_steam_path_with_fallback": get_steam_path_with_fallback,
            "clear_steam_cache": clear_steam_cache,
            "detect_steam_path": detect_steam_path,
            "validate_steam_path_manual": validate_steam_path_manual,
            "get_header_data": get_header_data,
            "force_header_refresh": force_header_refresh,
            "get_steam_username": get_steam_username,
            
            # ✅ SISTEMA DLL
            "check_hid_dll_status": check_hid_dll_status,
            "get_detailed_dll_report": get_detailed_dll_report,
            "get_dll_simple_status": get_dll_simple_status,
            "recreate_hid_dll": recreate_hid_dll,
            
            # ✅ SISTEMA DE ARQUIVOS
            "process_zip_upload": process_zip_upload,
            "create_zip_processor": create_zip_processor,
            "create_steam_backend": file_processing_funcs.get("create_steam_backend") if file_processing_funcs else None,
            
            # ✅ IMPORTANTE: Game Routes (NOVO - substitui game_management)
            "setup_game_routes": setup_game_routes,
            "detect_lua_games": detect_lua_games,
            "format_file_size": format_file_size,
            
            # ✅ SISTEMA DLC
            "get_dlc_manager": get_dlc_manager,
            
            # ✅ SISTEMA FIX
            "get_fix_manager": get_fix_manager,
            
            # ✅ VARIÁVEIS DE STATUS
            "GAME_ROUTES_AVAILABLE": GAME_ROUTES_AVAILABLE,  # ✅ NOVA
            "PYWEBVIEW_AVAILABLE": PYWEBVIEW_AVAILABLE,
            "WEBVIEW_CONFIG_AVAILABLE": WEBVIEW_CONFIG_AVAILABLE,
            "FLASK_CORS_AVAILABLE": FLASK_CORS_AVAILABLE,
            "DOWNLOAD_MANAGER_AVAILABLE": DOWNLOAD_MANAGER_AVAILABLE,
            "DOWNLOAD_ROUTES_AVAILABLE": DOWNLOAD_ROUTES_AVAILABLE,
            "DLC_MANAGER_AVAILABLE": DLC_MANAGER_AVAILABLE,
            "FIX_MANAGER_AVAILABLE": FIX_MANAGER_AVAILABLE,
            "STORE_SEARCH_AVAILABLE": STORE_SEARCH_AVAILABLE,
            "FILE_PROCESSING_AVAILABLE": FILE_PROCESSING_AVAILABLE,
            "DOWNLOAD_LOGGER_AVAILABLE": bool(download_logger),  # ✅ NOVA
            
            # ✅ VARIÁVEIS CRÍTICAS
            "DOWNLOAD_MANAGER_INSTANCE": DOWNLOAD_MANAGER_INSTANCE,  # ✅ INSTÂNCIA ÚNICA
            "current_dir": current_dir,
            "frontend_path": frontend_path,
            "tray_started": tray_started,
        }
        
        logger.info("[ROUTES] 🔧 Configurando sistema de rotas DEFINITIVO...")
        
        # ✅ 1. Configurar rotas principais
        setup_all_routes(app, frontend_path, base_path, getattr_funcs)
        logger.info("[ROUTES] ✅ Rotas principais configuradas")

        # ✅ 2. Configurar rotas Steam
        if STEAM_ROUTES_AVAILABLE:
            setup_steam_routes_func = steam_routes_funcs["setup_steam_routes"]
            setup_steam_routes_func(app, getattr_funcs)
            logger.info("[ROUTES] ✅ Rotas Steam configuradas")
        else:
            logger.warning("[ROUTES] ⚠️ Rotas Steam não disponíveis")
        
        # ✅ 3. CONFIGURAÇÃO CRÍTICA: Configurar rotas de download
        if DOWNLOAD_ROUTES_AVAILABLE and callable(setup_download_routes):
            try:
                setup_download_routes(app, getattr_funcs)
                logger.info("[ROUTES] ✅ Rotas de Download configuradas (SISTEMA CORRIGIDO)")
            except Exception as e:
                logger.error(f"[ROUTES] ❌ Erro ao configurar rotas de download: {e}")
                traceback.print_exc()
        else:
            logger.error("[ROUTES] ❌ Rotas de Download NÃO DISPONÍVEIS - Sistema crítico!")
        
        # ✅ 4. IMPORTANTE: Configurar rotas de gerenciamento de jogos (agora de game_routes.py)
        if GAME_ROUTES_AVAILABLE and callable(setup_game_routes):
            try:
                setup_game_routes(app, getattr_funcs)
                logger.info("[ROUTES] ✅ Rotas de Gerenciamento de Jogos configuradas (game_routes.py)")
            except Exception as e:
                logger.error(f"[ROUTES] ❌ Erro ao configurar game routes: {e}")
                traceback.print_exc()
        else:
            logger.warning("[ROUTES] ⚠️ Rotas de Gerenciamento de Jogos (game_routes.py) não disponíveis")
        
        logger.info("[ROUTES] ✅ Todas as rotas configuradas com sucesso")
        logger.info(f"[ROUTES] 📊 Status Final:")
        logger.info(f"[ROUTES]   • Download Manager: {DOWNLOAD_MANAGER_AVAILABLE}")
        logger.info(f"[ROUTES]   • Download Routes: {DOWNLOAD_ROUTES_AVAILABLE}")
        logger.info(f"[ROUTES]   • Download Logger: {bool(download_logger)}")
        logger.info(f"[ROUTES]   • Store Search: {STORE_SEARCH_AVAILABLE}")
        logger.info(f"[ROUTES]   • Game Routes: {GAME_ROUTES_AVAILABLE}")  # ✅ NOVA
        return True
        
    except Exception as e:
        logger.error(f"[ROUTES] ❌ Erro ao configurar rotas: {e}")
        traceback.print_exc()
        return False

# ------------------ INICIALIZAÇÃO DOS SISTEMAS UNIFICADOS ------------------
def initialize_dlc_system_robust():
    """Inicializa o sistema DLC unificado"""
    try:
        steam_path = get_steam_path()
        if initialize_dlc_system:
            result = initialize_dlc_system(steam_path)
            logger.info(f"[DLC] ✅ Sistema DLC inicializado: {steam_path}")
            return {'success': True, 'steam_path': steam_path}
        else:
            logger.warning("[DLC] ⚠️ Sistema DLC não disponível")
            return {'success': False, 'error': 'Sistema DLC não disponível'}
    except Exception as e:
        logger.error(f"[DLC] ❌ Erro ao inicializar DLC: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def initialize_fix_system_robust():
    """Inicializa o sistema Fix unificado"""
    try:
        steam_path = get_steam_path()
        if initialize_fix_system:
            result = initialize_fix_system(steam_path)
            logger.info(f"[FIX] ✅ Sistema Fix inicializado: {steam_path}")
            return {'success': True, 'steam_path': steam_path}
        else:
            logger.warning("[FIX] ⚠️ Sistema Fix não disponível")
            return {'success': False, 'error': 'Sistema Fix não disponível'}
    except Exception as e:
        logger.error(f"[FIX] ❌ Erro ao inicializar Fix: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def initialize_dll_system_robust():
    """Inicializa o sistema DLL"""
    try:
        logger.info("[DLL] Inicializando sistema DLL...")
        result = initialize_dll_system()
        if result.get('success'):
            logger.info("[DLL] ✅ Sistema DLL inicializado")
        else:
            logger.warning(f"[DLL] ⚠️ Sistema DLL com problemas: {result.get('error')}")
        return result
    except Exception as e:
        logger.error(f"[DLL] ❌ Erro ao inicializar DLL: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def initialize_download_logger():
    """Inicializa o sistema de log de downloads"""
    try:
        if download_logger:
            # Criar diretório de logs de download
            downloads_dir = Path(current_dir) / "downloads"
            downloads_dir.mkdir(exist_ok=True)
            logger.info(f"[DLOG] ✅ Sistema de log de downloads inicializado: {downloads_dir}")
            return True
        else:
            logger.warning("[DLOG] ⚠️ Sistema de log de downloads não disponível")
            return False
    except Exception as e:
        logger.error(f"[DLOG] ❌ Erro ao inicializar log de downloads: {e}")
        return False

def shutdown_application():
    """Função de encerramento"""
    logger.info("[SHUTDOWN] Encerrando aplicação...")
    if tray_manager and hasattr(tray_manager, 'stop'):
        tray_manager.stop()
        logger.info("[SHUTDOWN] Tray Manager encerrado")
    
    force_kill_steam_processes()
    logger.info("[SHUTDOWN] Processos Steam encerrados")
    sys.exit(0)

def initialize_application():
    """Inicialização principal da aplicação - VERSÃO DEFINITIVA CORRIGIDA"""
    logger.info("=" * 60)
    logger.info("🚀 STEAM GAMELOADER ULTIMATE - SISTEMA DEFINITIVO CORRIGIDO")
    logger.info("=" * 60)
    
    # Encerrar Steam na inicialização
    steam_killed = force_kill_steam_processes()
    if steam_killed:
        logger.info("[INIT] Steam encerrado na inicialização")
    
    # Inicializar tray
    tray_success = initialize_tray_system()
    if tray_success:
        logger.info("[INIT] Tray icon inicializado")
    
    # Log do modo de execução
    if getattr(sys, 'frozen', False):
        logger.info("[INIT] Executando como EXE")
    else:
        logger.info("[INIT] Executando como script Python")
    
    # Status dos sistemas - VERSÃO DEFINITIVA
    logger.info("-" * 50)
    logger.info("[SYSTEMS] 📊 STATUS DOS SISTEMAS (DEFINITIVO):")
    logger.info("-" * 50)
    logger.info(f"[SYSTEMS] • Download Logger: {'✅' if download_logger else '❌'}")
    logger.info(f"[SYSTEMS] • Download Routes: {'✅' if DOWNLOAD_ROUTES_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • Download Manager: {'✅' if DOWNLOAD_MANAGER_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • Store Search: {'✅' if STORE_SEARCH_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • Steam Routes: {'✅' if STEAM_ROUTES_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • Game Routes: {'✅' if GAME_ROUTES_AVAILABLE else '❌'}")  # ✅ NOVA
    logger.info(f"[SYSTEMS] • WebView: {'✅' if PYWEBVIEW_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • DLC Manager: {'✅' if DLC_MANAGER_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • Fix Manager: {'✅' if FIX_MANAGER_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • ZIP Upload: {'✅' if FILE_PROCESSING_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • Tray System: {'✅' if TRAY_AVAILABLE else '❌'}")
    logger.info(f"[SYSTEMS] • File Processing: {'✅' if FILE_PROCESSING_AVAILABLE else '❌'}")
    logger.info("-" * 50)
    
    # Verificar sistemas críticos
    critical_errors = []
    
    if not DOWNLOAD_ROUTES_AVAILABLE:
        critical_errors.append("❌ SISTEMA DE DOWNLOAD ROUTES NÃO DISPONÍVEL")
    
    if not DOWNLOAD_MANAGER_AVAILABLE:
        critical_errors.append("❌ SISTEMA DE DOWNLOAD MANAGER NÃO DISPONÍVEL")
    
    if not STORE_SEARCH_AVAILABLE:
        logger.warning("[WARNING] ⚠️ Sistema de busca não disponível - usando fallback")
    
    if critical_errors:
        for error in critical_errors:
            logger.error(f"[ERROR] {error}")
        logger.error("[ERROR] Sistemas críticos faltando. O aplicativo pode não funcionar corretamente.")
    
    # Verificar frontend
    if not os.path.exists(frontend_path):
        logger.error(f"[ERROR] ❌ Frontend não encontrado: {frontend_path}")
        return False
    else:
        logger.info(f"[INIT] ✅ Frontend encontrado: {frontend_path}")
    
    # Inicializar sistemas unificados
    logger.info("[INIT] 🔧 Inicializando sistemas DEFINITIVOS...")
    
    logger.info("[INIT] Inicializando sistema de log de downloads...")
    dlog_init = initialize_download_logger()
    
    logger.info("[INIT] Inicializando sistema DLL...")
    dll_init_result = initialize_dll_system_robust()
    
    logger.info("[INIT] Inicializando sistema DLC...")
    dlc_init_result = initialize_dlc_system_robust()
    
    logger.info("[INIT] Inicializando sistema Fix...")
    fix_init_result = initialize_fix_system_robust()
    
    # Configurar rotas
    logger.info("[INIT] 🌐 Configurando rotas DEFINITIVAS...")
    routes_success = setup_routes()
    if not routes_success:
        logger.error("[ERROR] ❌ Falha ao configurar rotas")
        return False
    
    # ✅ TESTAR DOWNLOAD MANAGER (VERIFICAÇÃO CRÍTICA)
    logger.info("[INIT] 🔍 Testando Download Manager...")
    try:
        test_manager = get_download_manager_instance()
        if test_manager:
            logger.info("[INIT] ✅ Download Manager testado e funcionando")
        else:
            logger.warning("[INIT] ⚠️ Download Manager não pôde ser instanciado")
    except Exception as e:
        logger.error(f"[INIT] ❌ Erro testando Download Manager: {e}")
    
    logger.info("=" * 60)
    logger.info("✅ APLICAÇÃO INICIALIZADA COM SUCESSO! - SISTEMA DEFINITIVO")
    logger.info(f"✅ Busca de Jogos: {'ATIVA' if STORE_SEARCH_AVAILABLE else 'FALLBACK'}")
    logger.info(f"✅ Download Manager: {'ATIVO' if DOWNLOAD_MANAGER_AVAILABLE else 'INATIVO'}")
    logger.info(f"✅ Sistema de Log: {'ATIVO' if dlog_init else 'INATIVO'}")
    logger.info(f"✅ Game Routes: {'ATIVO' if GAME_ROUTES_AVAILABLE else 'INATIVO'}")
    logger.info("=" * 60)
    return True

# ------------------ INICIALIZAÇÃO DO FLASK EM THREAD ------------------
def start_flask_in_thread():
    """Inicia o Flask em thread separada"""
    logger.info("[FLASK] 🌐 Iniciando servidor Flask em thread...")
    
    def run_flask():
        try:
            app.run(debug=False, host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
        except Exception as e:
            logger.error(f"[FLASK] ❌ Erro no servidor Flask: {e}")
            traceback.print_exc()
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Dar tempo suficiente para o Flask iniciar
    time.sleep(3.5)
    logger.info("[FLASK] ✅ Servidor Flask iniciado em http://localhost:5000")
    return True

# ------------------ MAIN ------------------
if __name__ == "__main__":
    try:
        ok = initialize_application()
        if not ok:
            logger.error("[ERROR] ❌ Falha na inicialização - Encerrando")
            sys.exit(1)

        logger.info("[MAIN] ✅ Sistema pronto para uso - VERSÃO DEFINITIVA")
        logger.info("[MAIN] 📍 Acesse: http://localhost:5000")
        logger.info("[MAIN] 📍 Busca de jogos: http://localhost:5000/search")
        logger.info("[MAIN] 📍 API de busca: http://localhost:5000/api/search/games?q=teste")
        logger.info("[MAIN] 📍 API de download: http://localhost:5000/api/game/570/download (POST)")
        logger.info("[MAIN] 📍 Status do sistema: http://localhost:5000/api/download/system-status")
        logger.info("[MAIN] 📍 Game Management: http://localhost:5000/game_management.html")  # ✅ NOVA
        
        if PYWEBVIEW_AVAILABLE and webview_available:
            logger.info("[MAIN] 🖥️ Iniciando launcher WebView...")
            flask_started = start_flask_in_thread()
            
            if flask_started:
                launcher_success = open_webview_launcher()
                if not launcher_success:
                    logger.error("[MAIN] ❌ Launcher falhou")
                    shutdown_application()
        else:
            logger.info("[MAIN] 🌐 Iniciando modo navegador...")
            threading.Thread(target=open_browser_safe, daemon=True).start()
            app.run(debug=False, host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
        
    except KeyboardInterrupt:
        logger.info("[MAIN] ⏹️ Aplicação interrompida pelo usuário")
        shutdown_application()
        
    except Exception as e:
        logger.error(f"[MAIN] ❌ Erro crítico no sistema: {e}")
        traceback.print_exc()
        shutdown_application()