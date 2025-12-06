import os
import platform
import subprocess
import logging
import time
from pathlib import Path
import psutil
import re

# ==================== CONFIGURAÇÃO GLOBAL ====================
# ✅ SISTEMA SIMPLIFICADO: Cache mais curto e controle de logs
_LAST_LOG_MESSAGE = {}
_LAST_LOG_TIME = {}
_LOGGER_INSTANCE = None
_STEAM_PATH_CACHE = None
_STEAM_PATH_CACHE_TIME = 0
_STEAM_STATUS_CACHE = None
_STEAM_STATUS_CACHE_TIME = 0
_HEADER_DATA_CACHE = None
_HEADER_CACHE_TIME = 0
_CACHE_DURATION = 5  # segundos para cache rápido
_HEADER_CACHE_DURATION = 30  # ✅ REDUZIDO: 30 segundos apenas

# ==================== SISTEMA DE LOGGING ====================

def setup_steam_logging():
    """Configura logging específico para Steam utils - SINGLETON"""
    global _LOGGER_INSTANCE
    
    if _LOGGER_INSTANCE is not None:
        return _LOGGER_INSTANCE
    
    logger = logging.getLogger('SteamUtils')
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    
    _LOGGER_INSTANCE = logger
    return logger

def safe_log_message(message):
    """Remove emojis para logging seguro"""
    if not isinstance(message, str):
        return str(message)
    
    replacements = {
        '✅': '[OK]', '⚠️': '[WARN]', '❌': '[ERROR]', 
        '🚀': '[START]', '🔧': '[CONFIG]', '🎯': '[SUCCESS]',
        '📦': '[EXE]', '🔴': '[STOP]', '📊': '[STATUS]',
        '📁': '[FOLDER]', '🔍': '[CHECK]', '🎮': '[GAME]',
        '💥': '[CRASH]', '🛠️': '[FIX]', '🔑': '[KEY]',
        '🔄': '[RELOAD]', '🧹': '[CLEAN]', '📄': '[FILE]',
        '⚙️': '[SETTINGS]', '🔒': '[LOCK]', '🔓': '[UNLOCK]',
        '🧪': '[TEST]'
    }
    
    for emoji, replacement in replacements.items():
        message = message.replace(emoji, replacement)
    
    return message

def log_once(logger, message, level=logging.INFO, key=None, cooldown=3.0):
    """Log que evita mensagens repetidas com cooldown"""
    global _LAST_LOG_MESSAGE, _LAST_LOG_TIME
    
    if key is None:
        key = message
    
    current_time = time.time()
    last_time = _LAST_LOG_TIME.get(key, 0)
    
    if (key in _LAST_LOG_MESSAGE and 
        _LAST_LOG_MESSAGE[key] == message and 
        current_time - last_time < cooldown):
        return False
    
    _LAST_LOG_MESSAGE[key] = message
    _LAST_LOG_TIME[key] = current_time
    
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

# ==================== FUNÇÕES DE CACHE ====================

def clear_steam_cache():
    """Limpa todo o cache do Steam para forçar nova detecção"""
    global _STEAM_PATH_CACHE, _STEAM_PATH_CACHE_TIME, _STEAM_STATUS_CACHE, _STEAM_STATUS_CACHE_TIME, _HEADER_DATA_CACHE, _HEADER_CACHE_TIME
    
    _STEAM_PATH_CACHE = None
    _STEAM_PATH_CACHE_TIME = 0
    _STEAM_STATUS_CACHE = None
    _STEAM_STATUS_CACHE_TIME = 0
    _HEADER_DATA_CACHE = None
    _HEADER_CACHE_TIME = 0
    
    logger = setup_steam_logging()
    log_once(logger, "✅ Cache do Steam limpo", key="cache_cleared")
    return True

# ==================== DETECÇÃO DO STEAM ====================

def get_steam_path():
    """✅ FUNÇÃO PRINCIPAL: Encontra o caminho de instalação do Steam com cache inteligente"""
    global _STEAM_PATH_CACHE, _STEAM_PATH_CACHE_TIME
    
    current_time = time.time()
    
    if (_STEAM_PATH_CACHE is not None and 
        current_time - _STEAM_PATH_CACHE_TIME < _CACHE_DURATION):
        return _STEAM_PATH_CACHE
    
    logger = setup_steam_logging()
    
    system = platform.system()
    possible_paths = []
    
    if system == 'Windows':
        # Tentar registro primeiro
        registry_path = _get_steam_path_from_registry()
        if registry_path:
            possible_paths.append(registry_path)
        
        possible_paths.extend([
            os.path.expandvars(r"%ProgramFiles%\Steam"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
            os.path.expandvars(r"%LocalAppData%\Programs\Steam"),
            r"C:\Program Files\Steam",
            r"C:\Program Files (x86)\Steam",
            os.path.expanduser(r"~\Steam"),
        ])
    elif system == 'Darwin':
        possible_paths = [
            "/Applications/Steam.app/Contents/MacOS",
            os.path.expanduser("~/Applications/Steam.app/Contents/MacOS"),
        ]
    else:
        possible_paths = [
            os.path.expanduser("~/.steam/steam"),
            "/usr/share/steam",
            "/usr/local/share/steam",
            "/opt/steam",
        ]
    
    # Remover duplicados e paths inválidos
    possible_paths = list(set([p for p in possible_paths if p and os.path.exists(p)]))
    
    old_cache = _STEAM_PATH_CACHE
    
    for path in possible_paths:
        if _validate_steam_directory(path):
            if path != old_cache:
                if old_cache is None:
                    log_once(logger, f"Steam encontrado em: {path}", key="steam_path_found")
                else:
                    log_once(logger, f"Steam path atualizado para: {path}", key="steam_path_updated")
            
            _STEAM_PATH_CACHE = path
            _STEAM_PATH_CACHE_TIME = current_time
            return path
    
    if old_cache is not None:
        log_once(logger, "Diretório do Steam não encontrado (cache limpo)", level=logging.ERROR, key="steam_path_lost")
        _STEAM_PATH_CACHE = None
    else:
        log_once(logger, "Diretório do Steam não encontrado", level=logging.ERROR, key="steam_path_not_found")
    
    return None

def _get_steam_path_from_registry():
    """Tenta obter o caminho do Steam do registro do Windows"""
    try:
        if platform.system() != 'Windows':
            return None
            
        import winreg
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam", "SteamPath"),
            (winreg.HKEY_CURRENT_USER, r"Software\Wow6432Node\Valve\Steam", "SteamPath"),
        ]
        
        for hive, key, value_name in registry_paths:
            try:
                with winreg.OpenKey(hive, key) as reg_key:
                    steam_path, _ = winreg.QueryValueEx(reg_key, value_name)
                    if steam_path and os.path.exists(steam_path):
                        return steam_path
            except FileNotFoundError:
                continue
                
    except Exception as e:
        logger = setup_steam_logging()
        logger.debug(f"Não foi possível acessar registro do Windows: {e}")
    
    return None

def _validate_steam_directory(path):
    """Valida se o diretório contém instalação do Steam"""
    required_files = ['steam.exe']
    path_obj = Path(path)
    
    has_required = any((path_obj / file).exists() for file in required_files)
    is_valid = path_obj.exists() and path_obj.is_dir() and has_required
    
    return is_valid

def validate_steam_directory(steam_path):
    """Valida se o diretório do Steam é válido e tem permissões de escrita"""
    if not steam_path or not os.path.exists(steam_path):
        return False
    
    required_dirs = ['steamapps', 'config']
    required_files = ['steam.exe']
    
    path_obj = Path(steam_path)
    
    for dir_name in required_dirs:
        if not (path_obj / dir_name).exists():
            return False
    
    for file_name in required_files:
        if not (path_obj / file_name).exists():
            return False
    
    try:
        test_file = path_obj / "write_test.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (IOError, OSError):
        return False

# ==================== FUNÇÃO DETECT_STEAM_PATH (SIMPLIFICADA) ====================

def detect_steam_path():
    """✅ VERSÃO SIMPLIFICADA: Detecta o caminho do Steam (compatibilidade frontend)"""
    logger = setup_steam_logging()
    log_once(logger, "Iniciando detecção automática do Steam...", key="detect_start")
    
    # Limpa cache para forçar nova detecção
    clear_steam_cache()
    
    path = get_steam_path()
    
    if path:
        log_once(logger, f"✅ Steam detectado em: {path}", key="detect_success")
        return path
    else:
        log_once(logger, "❌ Steam não encontrado na detecção automática", key="detect_fail")
        return None

# ==================== FUNÇÕES DE CONTROLE DO STEAM ====================

def is_steam_running():
    """Verifica se o Steam está em execução com cache inteligente"""
    global _STEAM_STATUS_CACHE, _STEAM_STATUS_CACHE_TIME
    
    current_time = time.time()
    
    if (_STEAM_STATUS_CACHE is not None and 
        current_time - _STEAM_STATUS_CACHE_TIME < _CACHE_DURATION):
        return _STEAM_STATUS_CACHE
    
    logger = setup_steam_logging()
    
    system = platform.system()
    steam_running = False
    
    try:
        if system == 'Windows':
            for proc in psutil.process_iter(['name', 'exe', 'pid', 'status']):
                try:
                    proc_name = (proc.info.get('name') or '').lower()
                    proc_status = (proc.info.get('status') or '').lower()
                    
                    if (proc_name == 'steam.exe' and 
                        proc_status not in ['zombie', 'dead'] and
                        'steamwebhelper' not in (proc.info.get('exe') or '').lower()):
                        steam_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not steam_running:
                try:
                    result = subprocess.run(
                        ['tasklist', '/FI', 'IMAGENAME eq steam.exe', '/FO', 'CSV'],
                        capture_output=True, 
                        text=True,
                        timeout=3,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    steam_running = 'steam.exe' in result.stdout
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    pass
        
        else:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = (proc.info.get('name') or '').lower()
                    proc_exe = (proc.info.get('exe') or '').lower()
                    if 'steam' in proc_name and 'steamwebhelper' not in proc_exe:
                        steam_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        old_status = _STEAM_STATUS_CACHE
        _STEAM_STATUS_CACHE = steam_running
        _STEAM_STATUS_CACHE_TIME = current_time
        
        if old_status != steam_running:
            status_msg = f"Status Steam: {'[OK] Executando' if steam_running else '[ERROR] Parado'}"
            log_once(logger, status_msg, key="steam_status_changed")
        
        return steam_running
        
    except Exception as e:
        log_once(logger, f"[ERROR] Erro ao verificar processo Steam: {e}", 
                level=logging.ERROR, key="steam_check_error")
        return False

def kill_steam():
    """Encerra o Steam de forma segura"""
    logger = setup_steam_logging()
    log_once(logger, "Encerrando Steam de forma segura...", key="kill_steam_start")
    
    current_pid = os.getpid()
    killed_count = 0
    
    try:
        steam_process_names = ['steam.exe', 'steamwebhelper.exe', 'steamservice.exe']
        
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                proc_pid = proc.info.get('pid')
                if proc_pid == current_pid:
                    continue
                
                proc_name = (proc.info.get('name') or '').lower()
                proc_status = (proc.info.get('status') or '').lower()
                
                if proc_name in steam_process_names and proc_status not in ['zombie', 'dead']:
                    try:
                        proc.kill()
                        killed_count += 1
                        logger.debug(f"Processo Steam encerrado: {proc_name} (PID: {proc_pid})")
                        time.sleep(0.2)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        log_once(logger, "Verificando se todos os processos Steam foram encerrados...", 
                key="steam_verify_kill")
        time.sleep(2)
        
        steam_still_running = False
        remaining_processes = []
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = (proc.info.get('name') or '').lower()
                if proc_name in ['steam.exe', 'steamwebhelper.exe']:
                    steam_still_running = True
                    remaining_processes.append(proc_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        global _STEAM_STATUS_CACHE, _STEAM_STATUS_CACHE_TIME
        _STEAM_STATUS_CACHE = False
        _STEAM_STATUS_CACHE_TIME = time.time()
        
        if not steam_still_running:
            success_msg = f"[OK] Steam encerrado com sucesso! Processos encerrados: {killed_count}"
            log_once(logger, success_msg, key="steam_kill_success")
            return True
        else:
            warning_msg = f"[WARN] Alguns processos Steam ainda em execução: {', '.join(remaining_processes)}"
            log_once(logger, warning_msg, level=logging.WARNING, key="steam_kill_partial")
            return True
            
    except Exception as e:
        log_once(logger, f"[ERROR] Erro ao encerrar Steam: {str(e)}", 
                level=logging.ERROR, key="steam_kill_error")
        return False

def launch_steam(steam_path=None):
    """Inicia o Steam de forma robusta"""
    logger = setup_steam_logging()
    
    log_once(logger, "[RELOAD] Limpando processos Steam residuais...", key="steam_cleanup")
    kill_steam()
    time.sleep(2)
    
    if not steam_path:
        steam_path = get_steam_path()
    
    if not steam_path:
        logger.error("Não foi possível encontrar o diretório do Steam")
        return False
    
    try:
        steam_exe = Path(steam_path) / "steam.exe"
        
        if not steam_exe.exists():
            logger.error(f"Steam.exe não encontrado em: {steam_exe}")
            return False
        
        current_status = is_steam_running()
        if current_status:
            log_once(logger, "Steam já está em execução", key="steam_already_running")
            return True
        
        log_once(logger, f"Iniciando Steam: {steam_exe}", key="steam_launch_start")
        
        try:
            creation_flags = 0
            if platform.system() == 'Windows':
                creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            
            process = subprocess.Popen(
                [str(steam_exe)],
                shell=False,
                creationflags=creation_flags
            )
            
            log_once(logger, "Aguardando inicialização do Steam...", key="steam_waiting")
            
            for i in range(45):
                time.sleep(1)
                
                if is_steam_running():
                    success_msg = f"[OK] Steam iniciado com sucesso após {i+1} segundos"
                    log_once(logger, success_msg, key="steam_start_success")
                    return True
                
                if process.poll() is not None:
                    exit_code = process.poll()
                    warning_msg = f"Processo Steam terminou com código: {exit_code}"
                    log_once(logger, warning_msg, level=logging.WARNING, key="steam_process_exit")
                    
                    if exit_code != 0:
                        break
                
                if (i + 1) % 10 == 0:
                    log_once(logger, f"Aguardando Steam... {i+1}s", key="steam_wait_progress")
            
            if not is_steam_running():
                log_once(logger, "Tentando método alternativo...", key="steam_alt_method")
                try:
                    subprocess.Popen(
                        f'"{steam_exe}"',
                        shell=True
                    )
                    
                    for i in range(20):
                        time.sleep(1)
                        if is_steam_running():
                            log_once(logger, "[OK] Steam iniciado com método alternativo", 
                                    key="steam_alt_success")
                            return True
                        if (i + 1) % 5 == 0:
                            log_once(logger, f"Verificando método alternativo... {i+1}s", 
                                    key="steam_alt_progress")
                except Exception as e:
                    log_once(logger, f"Método alternativo falhou: {e}", 
                            level=logging.ERROR, key="steam_alt_error")
        
        except Exception as e:
            log_once(logger, f"Erro no método principal: {e}", 
                    level=logging.ERROR, key="steam_main_error")
        
        log_once(logger, "Realizando verificação final do Steam...", key="steam_final_check")
        time.sleep(2)
        
        final_check = is_steam_running()
        if final_check:
            log_once(logger, "[OK] Steam iniciado (verificação final)", key="steam_final_success")
            return True
        else:
            logger.error("[ERROR] Falha ao iniciar Steam após todas as tentativas")
            return False
            
    except Exception as e:
        logger.error(f"[ERROR] Erro crítico ao iniciar Steam: {e}")
        return False

# ==================== FUNÇÃO GET_STEAM_USERNAME ÚNICA E DEFINITIVA ====================

def get_steam_username():
    """✅ FUNÇÃO ÚNICA E DEFINITIVA: Extrai username do Steam do arquivo loginusers.vdf"""
    logger = setup_steam_logging()
    
    try:
        # 1. Obter caminho do Steam
        steam_path = get_steam_path()
        if not steam_path:
            log_once(logger, "❌ Steam path não encontrado", key="vdf_no_path")
            return None
        
        # 2. Verificar se arquivo VDF existe
        vdf_path = Path(steam_path) / "config" / "loginusers.vdf"
        if not vdf_path.exists():
            log_once(logger, f"❌ VDF não existe: {vdf_path}", key="vdf_not_found")
            return None
        
        # 3. Ler conteúdo com encoding UTF-8-SIG (padrão Steam)
        try:
            with open(vdf_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback para UTF-8 normal
            with open(vdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # 4. PARSER ÚNICO E EFICIENTE
        # Procura pelo usuário mais recente (MostRecent = "1")
        
        # Encontrar todos os PersonaName no arquivo
        persona_pattern = r'"PersonaName"\s+"([^"]+)"'
        all_personas = re.findall(persona_pattern, content)
        
        if all_personas:
            # Retorna o último PersonaName encontrado (normalmente o mais recente)
            username = all_personas[-1].strip()
            if username and len(username) > 1:
                log_once(logger, f"✅ Username extraído: '{username}'", key="vdf_extracted")
                return username
        
        # 5. Se não encontrar PersonaName, procurar MostRecent
        # Procurar por usuário com MostRecent = "1"
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Encontrar linha com MostRecent = "1"
            if '"MostRecent"' in line and '"1"' in line:
                # Procurar PersonaName nas linhas próximas
                for j in range(max(0, i - 5), min(len(lines), i + 5)):
                    persona_line = lines[j].strip()
                    if '"PersonaName"' in persona_line:
                        match = re.search(persona_pattern, persona_line)
                        if match:
                            username = match.group(1).strip()
                            if username and len(username) > 1:
                                log_once(logger, f"✅ Username extraído (MostRecent): '{username}'", key="vdf_extracted_recent")
                                return username
        
        # 6. Nada encontrado
        log_once(logger, "❌ PersonaName não encontrado no VDF", key="vdf_not_found")
        return None
        
    except Exception as e:
        log_once(logger, f"❌ Erro crítico no parser VDF: {e}", level=logging.ERROR, key="vdf_error")
        return None

# ==================== FUNÇÕES AUXILIARES ====================

def get_user_greeting():
    """Retorna saudação baseada no horário"""
    try:
        current_hour = time.localtime().tm_hour
        
        if 5 <= current_hour < 12:
            return "Bom dia"
        elif 12 <= current_hour < 18:
            return "Boa tarde"
        elif 18 <= current_hour < 24:
            return "Boa noite"
        else:
            return "Boa madrugada"
    except:
        return "Olá"

def get_header_data():
    """✅ VERSÃO CORRIGIDA: Retorna dados para header com cache reduzido"""
    global _HEADER_DATA_CACHE, _HEADER_CACHE_TIME
    
    current_time = time.time()
    
    # ✅ CACHE REDUZIDO: Apenas 30 segundos
    if (_HEADER_DATA_CACHE is not None and 
        current_time - _HEADER_CACHE_TIME < _HEADER_CACHE_DURATION):
        
        # Atualiza apenas status do Steam (muda rápido)
        cached_data = _HEADER_DATA_CACHE.copy()
        cached_data['steam_running'] = is_steam_running()
        cached_data['timestamp'] = current_time
        cached_data['cache_used'] = True
        return cached_data
    
    logger = setup_steam_logging()
    log_once(logger, "🔁 Atualização completa dos dados do header...", key="header_full_update")
    
    try:
        # Dados principais
        steam_path = get_steam_path()
        username = get_steam_username()  # ✅ CHAMA FUNÇÃO ÚNICA E DEFINITIVA
        steam_running = is_steam_running()
        greeting = get_user_greeting()
        
        # Verificação DLL SIMPLIFICADA
        dll_available = False
        if steam_path:
            dll_path = Path(steam_path) / "hid.dll"
            if dll_path.exists():
                try:
                    # Verifica apenas se existe e tem tamanho > 0
                    dll_available = dll_path.stat().st_size > 0
                except OSError:
                    dll_available = False
        
        data = {
            "username": username or "Jogador",
            "greeting": greeting,
            "steam_running": steam_running,
            "dll_available": dll_available,
            "steam_path": steam_path,
            "timestamp": current_time,
            "cache_used": False,
            "source": "steam_utils_definitivo"
        }
        
        # Atualiza cache
        _HEADER_DATA_CACHE = data.copy()
        _HEADER_CACHE_TIME = current_time
        
        log_once(logger, f"✅ Header data atualizado - User: '{data['username']}', Steam: {data['steam_running']}, DLL: {data['dll_available']}", 
                key="header_data_updated")
        
        return data
        
    except Exception as e:
        log_once(logger, f"❌ Erro no header: {e}", level=logging.ERROR, key="header_error")
        return {
            "username": "Jogador",
            "greeting": "Olá",
            "steam_running": False,
            "dll_available": False,
            "steam_path": None,
            "timestamp": current_time,
            "error": str(e),
            "source": "error_fallback"
        }

def force_header_refresh():
    """Força atualização completa do cache do header"""
    global _HEADER_DATA_CACHE, _HEADER_CACHE_TIME
    
    _HEADER_DATA_CACHE = None
    _HEADER_CACHE_TIME = 0
    
    logger = setup_steam_logging()
    log_once(logger, "✅ Cache do header forçado a atualizar", key="header_force_refresh")
    
    return get_header_data()

# ==================== FUNÇÕES DE INFORMAÇÃO ====================

def get_steam_info():
    """Retorna informações detalhadas sobre a instalação do Steam"""
    steam_path = get_steam_path()
    
    info = {
        "steam_path": steam_path,
        "steam_running": is_steam_running(),
        "steam_valid": validate_steam_directory(steam_path) if steam_path else False,
        "platform": platform.system(),
        "hid_dll_exists": False,
        "hid_dll_valid": False,
    }
    
    if steam_path:
        hid_dll_path = Path(steam_path) / "hid.dll"
        info["hid_dll_exists"] = hid_dll_path.exists()
        
        if info["hid_dll_exists"]:
            try:
                file_size = hid_dll_path.stat().st_size
                info["hid_dll_valid"] = file_size > 0
                info["hid_dll_size"] = file_size
            except OSError:
                info["hid_dll_valid"] = False
    
    return info

def get_system_info():
    """Retorna informações do sistema para integração"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "steam_utils_version": "definitivo_corrigido"
    }

# ==================== FUNÇÕES DE VALIDAÇÃO MANUAL ====================

def _normalize_manual_path(path):
    """Normaliza caminho manual do usuário"""
    logger = setup_steam_logging()
    
    try:
        if not path or not isinstance(path, str):
            return None
            
        expanded_path = os.path.expanduser(os.path.expandvars(path))
        cleaned_path = expanded_path.replace('"', '').replace("'", "").strip()
        
        if cleaned_path.lower().endswith('steam.exe') and os.path.isfile(cleaned_path):
            normalized = os.path.dirname(cleaned_path)
            log_once(logger, f"Normalizado (arquivo): {cleaned_path} → {normalized}", key="normalize_file")
            return normalized
        
        if os.path.isdir(cleaned_path):
            steam_exe = os.path.join(cleaned_path, 'steam.exe')
            if os.path.isfile(steam_exe):
                log_once(logger, f"Normalizado (diretório): {cleaned_path}", key="normalize_dir")
                return cleaned_path
        
        steam_exe_in_dir = os.path.join(cleaned_path, 'steam.exe')
        if os.path.isfile(steam_exe_in_dir):
            log_once(logger, f"Normalizado (steam.exe no dir): {cleaned_path}", key="normalize_exe_in_dir")
            return cleaned_path
            
        return None
        
    except Exception as e:
        logger.error(f"Erro ao normalizar caminho '{path}': {e}")
        return None

def validate_steam_path_manual(path):
    """Validação manual compatível com frontend"""
    logger = setup_steam_logging()
    
    if not path or not isinstance(path, str):
        return {"valid": False, "normalized_path": None, "error": "Caminho vazio"}
    
    path = path.strip()
    log_once(logger, f"Validando caminho manual: {path}", key="validate_manual")
    
    normalized = _normalize_manual_path(path)
    if not normalized:
        return {"valid": False, "normalized_path": None, "error": "Caminho inválido ou não encontrado"}
    
    is_valid = validate_steam_directory(normalized)
    
    if is_valid:
        log_once(logger, f"✅ Caminho válido: {normalized}", key="validate_success")
        return {
            "valid": True, 
            "normalized_path": normalized,
            "message": "Diretório do Steam válido"
        }
    else:
        log_once(logger, f"❌ Caminho inválido: {normalized}", key="validate_fail")
        return {
            "valid": False, 
            "normalized_path": normalized,
            "error": "Diretório não contém instalação válida do Steam"
        }

# ==================== FUNÇÕES DE CONTROLE AVANÇADO ====================

def force_kill_steam_safe():
    """Encerra Steam de forma segura para inicialização"""
    logger = setup_steam_logging()
    log_once(logger, "Encerramento seguro do Steam na inicialização...", key="force_kill_start")
    
    current_pid = os.getpid()
    killed_count = 0
    
    try:
        steam_process_names = ['steam.exe', 'steamwebhelper.exe', 'steamservice.exe']
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_pid = proc.info.get('pid')
                if proc_pid == current_pid:
                    continue
                    
                proc_name = (proc.info.get('name') or '').lower()
                if proc_name in steam_process_names:
                    try:
                        proc.kill()
                        killed_count += 1
                        logger.debug(f"Processo {proc_name} (PID: {proc_pid}) encerrado com segurança")
                        time.sleep(0.2)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        time.sleep(1)
        
        still_running = False
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = (proc.info.get('name') or '').lower()
                proc_pid = proc.info.get('pid')
                if proc_name in ['steam.exe'] and proc_pid != current_pid:
                    still_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not still_running:
            success_msg = f"[OK] {killed_count} processos Steam encerrados com segurança"
            log_once(logger, success_msg, key="force_kill_success")
            return True
        else:
            log_once(logger, "[WARN] Alguns processos Steam podem ainda estar ativos", 
                    level=logging.WARNING, key="force_kill_partial")
            return True
            
    except Exception as e:
        log_once(logger, f"[ERROR] Erro no encerramento seguro: {str(e)}", 
                level=logging.ERROR, key="force_kill_error")
        return False

def wait_for_steam_shutdown(timeout=30):
    """Aguarda o Steam encerrar completamente"""
    logger = setup_steam_logging()
    log_once(logger, f"Aguardando encerramento do Steam (timeout: {timeout}s)...", key="wait_shutdown")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_steam_running():
            log_once(logger, "[OK] Steam encerrado completamente", key="steam_shutdown_complete")
            return True
        time.sleep(1)
    
    log_once(logger, "[WARN] Timeout aguardando encerramento do Steam", level=logging.WARNING, key="shutdown_timeout")
    return False

def restart_steam():
    """Reinicia o Steam completamente"""
    logger = setup_steam_logging()
    log_once(logger, "Reiniciando Steam...", key="restart_steam")
    
    if kill_steam():
        if wait_for_steam_shutdown():
            time.sleep(2)
            return launch_steam()
    
    return False

# ==================== FUNÇÕES DE DETECÇÃO E TESTE ====================

def get_steam_detection_report():
    """Retorna relatório completo da detecção do Steam"""
    steam_path = detect_steam_path()
    is_running = is_steam_running()
    is_valid = validate_steam_directory(steam_path) if steam_path else False
    
    return {
        "detected": steam_path is not None,
        "path": steam_path,
        "running": is_running,
        "valid": is_valid,
        "platform": platform.system(),
        "cache_age": time.time() - _STEAM_PATH_CACHE_TIME if _STEAM_PATH_CACHE else None,
        "detection_method": "registry" if _get_steam_path_from_registry() == steam_path else "filesystem"
    }

def test_steam_integration():
    """Testa a integração completa com o Steam"""
    logger = setup_steam_logging()
    log_once(logger, "🧪 Iniciando teste de integração Steam...", key="integration_test")
    
    results = {
        "steam_detection": False,
        "steam_validation": False,
        "steam_running": False,
        "steam_control": False,
        "username_detection": False,
        "details": {}
    }
    
    steam_path = detect_steam_path()
    results["steam_detection"] = steam_path is not None
    results["details"]["detected_path"] = steam_path
    
    if steam_path:
        results["steam_validation"] = validate_steam_directory(steam_path)
        results["details"]["validation"] = "Valid" if results["steam_validation"] else "Invalid"
    
    results["steam_running"] = is_steam_running()
    results["details"]["running_status"] = "Running" if results["steam_running"] else "Stopped"
    
    username = get_steam_username()
    results["username_detection"] = username is not None and username != "Jogador"
    results["details"]["username"] = username
    
    if not results["steam_running"] and results["steam_validation"]:
        test_launch = launch_steam(steam_path)
        time.sleep(5)
        results["steam_control"] = is_steam_running()
        if results["steam_control"]:
            kill_steam()
        results["details"]["control_test"] = "Passed" if results["steam_control"] else "Failed"
    else:
        results["details"]["control_test"] = "Skipped"
    
    log_once(logger, f"🧪 Teste integração concluído: {results}", key="integration_test_complete")
    return results

# ==================== FUNÇÃO DE DEBUG PARA USERNAME ====================

def debug_steam_username():
    """Função de debug para testar extração de username"""
    logger = setup_steam_logging()
    log_once(logger, "🧪 DEBUG: Testando extração de username do Steam...", key="debug_username")
    
    try:
        steam_path = get_steam_path()
        if not steam_path:
            return {"success": False, "error": "Steam path não encontrado"}
        
        vdf_path = Path(steam_path) / "config" / "loginusers.vdf"
        if not vdf_path.exists():
            return {"success": False, "error": f"Arquivo não existe: {vdf_path}"}
        
        # Ler conteúdo
        content = None
        try:
            with open(vdf_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(vdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        if not content:
            return {"success": False, "error": "Não foi possível ler arquivo VDF"}
        
        # Chamar função principal
        username = get_steam_username()
        
        return {
            "success": True,
            "username": username,
            "found": username is not None,
            "steam_path": steam_path,
            "vdf_exists": True,
            "vdf_size": os.path.getsize(vdf_path),
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

# ==================== COMPATIBILIDADE ====================

def check_hid_dll_status(steam_path=None):
    """Verifica status da hid.dll - versão simplificada"""
    if not steam_path:
        steam_path = get_steam_path()
    
    if not steam_path:
        return {"valid": False, "exists": False, "steam_found": False}
    
    dll_path = Path(steam_path) / "hid.dll"
    exists = dll_path.exists()
    valid = False
    
    if exists:
        try:
            file_size = dll_path.stat().st_size
            valid = file_size > 0
        except:
            valid = False
    
    return {
        "valid": valid,
        "exists": exists,
        "steam_found": True,
        "path": str(dll_path)
    }

# ==================== TESTE E EXECUÇÃO ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🧪 Steam Utils - VERSÃO DEFINITIVA CORRIGIDA")
    print("=" * 60)
    
    print("1. Testando detecção automática...")
    detected_path = get_steam_path()
    print(f"   ✅ Detectado: {detected_path}")
    print(f"   ✅ Existe: {os.path.exists(detected_path) if detected_path else False}")
    
    print("\n2. Testando extração de username...")
    debug_result = debug_steam_username()
    if debug_result.get("success"):
        print(f"   ✅ Username: '{debug_result['username']}'")
        print(f"   ✅ Encontrado: {debug_result['found']}")
        print(f"   ✅ VDF size: {debug_result.get('vdf_size', 'N/A')} bytes")
    else:
        print(f"   ❌ Erro: {debug_result.get('error', 'Desconhecido')}")
    
    print("\n3. Testando dados do header...")
    for i in range(2):
        header_data = get_header_data()
        print(f"   Tentativa {i+1}: User='{header_data['username']}', Steam={header_data['steam_running']}, DLL={header_data['dll_available']}")
        time.sleep(1)
    
    print("\n4. Teste de status Steam...")
    status = is_steam_running()
    print(f"   ✅ Steam executando: {status}")
    
    print("\n5. Relatório de detecção...")
    report = get_steam_detection_report()
    for key, value in report.items():
        print(f"   {key}: {value}")