# config/dll_manager.py - VERSÃO DEFINITIVA CORRIGIDA - VERIFICAÇÃO ÚNICA
import os
import base64
import logging
import shutil
import sys
import time
from pathlib import Path

# 🔥 CORREÇÃO: Sistema global de controle de logs e cache
_LAST_LOG_MESSAGE = {}
_LAST_LOG_TIME = {}
_LOGGER_INSTANCE = None
_DLL_VERIFICATION_DONE = False
_DLL_VERIFICATION_RESULT = None
_DLL_SYSTEM_INITIALIZED = False
_DLL_SYSTEM_RESULT = None

# 🔥 CORREÇÃO: Configuração de encoding seguro
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

# 🔥 CORREÇÃO: Adicionar o diretório utils ao path do Python
current_dir = Path(__file__).parent
project_root = current_dir.parent
utils_dir = project_root / "utils"

if str(utils_dir) not in sys.path:
    sys.path.insert(0, str(utils_dir))

# 🔥 AGORA importar steam_utils diretamente - SEM FALLBACKS
try:
    from steam_utils import get_steam_path, is_steam_running, kill_steam, validate_steam_directory
    STEAM_UTILS_AVAILABLE = True
except ImportError as e:
    logging.error(f"Falha critica: Nao foi possivel importar steam_utils: {e}")
    logging.error(f"Paths disponiveis: {sys.path}")
    raise ImportError("steam_utils nao disponivel - verifique a estrutura de pastas")

def safe_log_message(message):
    """Remove emojis e caracteres problemáticos para logging seguro"""
    if not isinstance(message, str):
        return str(message)
    
    # Substitui emojis problemáticos
    replacements = {
        '✅': '[OK]', '⚠️': '[WARN]', '❌': '[ERROR]', 
        '🚀': '[START]', '🔧': '[CONFIG]', '🎯': '[SUCCESS]',
        '📦': '[EXE]', '🔴': '[STOP]', '📊': '[STATUS]',
        '📁': '[FOLDER]', '🔍': '[CHECK]', '🎮': '[GAME]',
        '💥': '[CRASH]', '🛠️': '[FIX]', '🔑': '[KEY]',
        '🔄': '[RELOAD]', '🧹': '[CLEAN]', '📄': '[FILE]',
        '⚙️': '[SETTINGS]', '🔒': '[LOCK]', '🔓': '[UNLOCK]',
        '🔥': '[HOTFIX]', '💾': '[BACKUP]', '🔧': '[TOOL]'
    }
    
    for emoji, replacement in replacements.items():
        message = message.replace(emoji, replacement)
    
    return message

def setup_dll_logging():
    """Configura logging seguro - SINGLETON"""
    global _LOGGER_INSTANCE
    
    if _LOGGER_INSTANCE is not None:
        return _LOGGER_INSTANCE
    
    logger = logging.getLogger('DLLManager')
    
    # ✅ CORREÇÃO: Evita múltiplos handlers e propagação duplicada
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # ✅ IMPEDE PROPAGAÇÃO DUPLICADA
    
    _LOGGER_INSTANCE = logger
    return logger

def log_once(logger, message, level=logging.INFO, key=None, cooldown=10.0):
    """✅ CORREÇÃO DEFINITIVA: Log que evita mensagens repetidas com cooldown aumentado"""
    global _LAST_LOG_MESSAGE, _LAST_LOG_TIME
    
    if key is None:
        key = message
    
    current_time = time.time()
    last_time = _LAST_LOG_TIME.get(key, 0)
    
    # ✅ VERIFICAÇÃO ROBUSTA: Mensagem idêntica dentro do cooldown
    if (key in _LAST_LOG_MESSAGE and 
        _LAST_LOG_MESSAGE[key] == message and 
        current_time - last_time < cooldown):
        return False  # Log ignorado
    
    # ✅ VERIFICAÇÃO ADICIONAL: Não logar a mesma mensagem muitas vezes
    if key in _LAST_LOG_MESSAGE:
        repetition_count = _LAST_LOG_MESSAGE.get(f"{key}_count", 0) + 1
        _LAST_LOG_MESSAGE[f"{key}_count"] = repetition_count
        
        # Se a mesma mensagem foi logada mais de 5 vezes em 60 segundos, silenciar
        if repetition_count > 5 and current_time - _LAST_LOG_TIME.get(f"{key}_first", current_time) < 60:
            logger.debug(f"[SILENCIADO] Mensagem repetida: {safe_log_message(message)}")
            return False
    
    # Primeira vez que vemos esta mensagem
    if key not in _LAST_LOG_MESSAGE:
        _LAST_LOG_MESSAGE[f"{key}_first"] = current_time
        _LAST_LOG_MESSAGE[f"{key}_count"] = 1
    
    # Atualiza registro
    _LAST_LOG_MESSAGE[key] = message
    _LAST_LOG_TIME[key] = current_time
    
    # Log real com mensagem segura
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

def get_hid_dll_base64_path():
    """
    Encontra o caminho do arquivo hid_dll_base64.txt de forma robusta
    Retorna: Path object ou None
    """
    logger = setup_dll_logging()
    
    # ✅ CORREÇÃO: Cache local para evitar verificações repetidas
    if hasattr(get_hid_dll_base64_path, '_cached_result'):
        return get_hid_dll_base64_path._cached_result
    
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    possible_locations = [
        # Diretório config atual
        current_dir / "hid_dll_base64.txt",
        # Diretório config no projeto principal
        project_root / "config" / "hid_dll_base64.txt",
        # Diretório atual de trabalho
        Path.cwd() / "config" / "hid_dll_base64.txt",
        Path.cwd() / "hid_dll_base64.txt",
    ]
    
    for location in possible_locations:
        if location.exists() and location.is_file():
            log_once(logger, "Arquivo base64 encontrado: " + str(location), key="base64_found")
            # ✅ SALVAR NO CACHE
            get_hid_dll_base64_path._cached_result = location
            return location
    
    log_once(logger, "Arquivo hid_dll_base64.txt nao encontrado", level=logging.ERROR, key="base64_not_found")
    get_hid_dll_base64_path._cached_result = None
    return None

def verify_hid_dll_integrity(dll_path):
    """
    Verifica a integridade da hid.dll de forma robusta
    Retorna: bool indicando se a DLL é válida
    """
    logger = setup_dll_logging()
    
    if not dll_path or not os.path.exists(dll_path):
        log_once(logger, "DLL nao encontrada: " + str(dll_path), level=logging.WARNING, key="dll_not_found")
        return False
    
    try:
        file_size = os.path.getsize(dll_path)
        
        # Verificações de integridade
        checks = [
            (file_size > 1024, f"Tamanho minimo (1KB) - Atual: {file_size} bytes"),
            (file_size < 50 * 1024 * 1024, f"Tamanho maximo (50MB) - Atual: {file_size} bytes"),
        ]
        
        all_checks_passed = True
        for check_passed, check_description in checks:
            if not check_passed:
                log_once(logger, "Verificacao falhou: " + check_description, level=logging.WARNING, key=f"check_failed_{check_description}")
                all_checks_passed = False
        
        # Verificação adicional: tentar ler o arquivo
        try:
            with open(dll_path, 'rb') as f:
                header = f.read(2)
                # Verifica se é um arquivo PE (DLL) válido (magic number "MZ")
                is_pe_file = (header == b'MZ')
                if not is_pe_file:
                    log_once(logger, "Arquivo nao parece ser uma DLL valida", level=logging.WARNING, key="not_pe_file")
                    all_checks_passed = False
        except Exception as read_error:
            log_once(logger, "Erro ao ler DLL para verificacao: " + str(read_error), level=logging.WARNING, key="dll_read_error")
            all_checks_passed = False
        
        if all_checks_passed:
            log_once(logger, "DLL verificada: " + f"{dll_path} ({file_size} bytes)", key="dll_verified")
        else:
            log_once(logger, "DLL com problemas de integridade: " + str(dll_path), level=logging.WARNING, key="dll_integrity_failed")
            
        return all_checks_passed
        
    except Exception as e:
        log_once(logger, "Erro ao verificar integridade da DLL: " + f"{dll_path}: {e}", level=logging.ERROR, key="dll_integrity_error")
        return False

def create_backup_existing_dll(dll_path):
    """
    Cria backup da DLL existente de forma segura
    Retorna: caminho do backup ou None
    """
    logger = setup_dll_logging()
    
    try:
        if not os.path.exists(dll_path):
            log_once(logger, "Nenhuma DLL existente para backup", key="no_dll_for_backup")
            return None
            
        backup_dir = os.path.join(os.path.dirname(dll_path), "otosteam_backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dll_name = os.path.basename(dll_path)
        backup_filename = f"{timestamp}_{dll_name}.backup"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(dll_path, backup_path)
        log_once(logger, "Backup criado: " + str(backup_path), key="backup_created")
        return backup_path
        
    except Exception as e:
        log_once(logger, "Erro ao criar backup da DLL: " + str(e), level=logging.ERROR, key="backup_error")
        return None

def decode_base64_dll_data(base64_file_path):
    """
    Decodifica dados base64 da DLL de forma robusta
    Retorna: dados binários ou None
    """
    logger = setup_dll_logging()
    
    try:
        if not os.path.exists(base64_file_path):
            log_once(logger, "Arquivo base64 nao encontrado: " + str(base64_file_path), level=logging.ERROR, key="base64_file_not_found")
            return None
            
        with open(base64_file_path, 'r', encoding='utf-8') as file:
            dll_data_base64 = file.read().strip()
        
        if not dll_data_base64:
            log_once(logger, "Arquivo base64 vazio ou invalido", level=logging.ERROR, key="base64_empty")
            return None
        
        # Validação básica do formato base64
        if len(dll_data_base64) % 4 != 0:
            log_once(logger, "Dados base64 podem estar incompletos", level=logging.WARNING, key="base64_incomplete")
            # Tenta corrigir adicionando padding
            dll_data_base64 += '=' * (4 - len(dll_data_base64) % 4)
        
        try:
            dll_data = base64.b64decode(dll_data_base64, validate=True)
            log_once(logger, "Dados base64 decodificados: " + f"{len(dll_data)} bytes", key="base64_decoded")
            return dll_data
        except base64.binascii.Error as e:
            log_once(logger, "Erro na decodificacao base64: " + str(e), level=logging.ERROR, key="base64_decode_error")
            return None
            
    except Exception as e:
        log_once(logger, "Erro ao ler/decodificar arquivo base64: " + str(e), level=logging.ERROR, key="base64_read_error")
        return None

def create_hid_dll(steam_path=None):
    """
    Cria a hid.dll no diretório correto do Steam de forma robusta
    Retorna: bool indicando sucesso
    """
    logger = setup_dll_logging()
    
    if not steam_path:
        steam_path = get_steam_path()
    
    if not steam_path:
        log_once(logger, "Nao foi possivel encontrar o diretorio do Steam", level=logging.ERROR, key="steam_not_found")
        return False

    # Validar diretório Steam
    if not validate_steam_directory(steam_path):
        log_once(logger, "Diretorio do Steam invalido ou sem permissoes de escrita", level=logging.ERROR, key="steam_invalid")
        return False

    dll_name = "hid.dll"
    dll_path = os.path.join(steam_path, dll_name)
    
    log_once(logger, "Iniciando criacao da " + f"{dll_name} em: {steam_path}", key="dll_creation_start")

    # Verificar se a DLL já existe e está íntegra
    if verify_hid_dll_integrity(dll_path):
        log_once(logger, "DLL " + f"{dll_name} ja existe e esta integra", key="dll_already_exists")
        return True

    # Encontrar arquivo base64
    base64_file_path = get_hid_dll_base64_path()
    if not base64_file_path:
        log_once(logger, "Arquivo base64 nao encontrado", level=logging.ERROR, key="base64_not_found_creation")
        return False

    # Decodificar dados da DLL
    dll_data = decode_base64_dll_data(base64_file_path)
    if not dll_data:
        log_once(logger, "Falha ao decodificar dados base64", level=logging.ERROR, key="base64_decode_failed")
        return False

    # Criar DLL no diretório Steam
    try:
        # Criar backup da DLL existente se houver
        create_backup_existing_dll(dll_path)
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(dll_path), exist_ok=True)
        
        # Escrever nova DLL
        with open(dll_path, 'wb') as dll_file:
            dll_file.write(dll_data)
        
        log_once(logger, "DLL escrita em: " + f"{dll_path} ({len(dll_data)} bytes)", key="dll_written")
        
        # Verificar integridade após escrita
        if verify_hid_dll_integrity(dll_path):
            log_once(logger, "DLL criada e verificada com sucesso!", key="dll_creation_success")
            return True
        else:
            log_once(logger, "Falha na verificacao da DLL apos criacao", level=logging.ERROR, key="dll_verification_failed")
            return False
            
    except Exception as e:
        log_once(logger, "Erro critico ao criar DLL: " + str(e), level=logging.ERROR, key="dll_creation_error")
        return False

def recreate_hid_dll(steam_path=None):
    """
    Função específica para criar/reconstruir a hid.dll - compatibilidade com main.py
    Versão robusta com múltiplas tentativas
    """
    logger = setup_dll_logging()
    log_once(logger, "Iniciando verificacao/recriacao da hid.dll...", key="dll_recreation_start")
    
    # Tentativa 1: Verificação simples
    if steam_path:
        dll_path = os.path.join(steam_path, "hid.dll")
        if verify_hid_dll_integrity(dll_path):
            log_once(logger, "hid.dll ja existe e esta integra", key="dll_exists_valid")
            return True
    
    # Tentativa 2: Criação normal
    if create_hid_dll(steam_path):
        return True
    
    # Tentativa 3: Fallback - tentar com novo caminho do Steam
    log_once(logger, "Tentando fallback: rediscover Steam path...", level=logging.WARNING, key="steam_fallback_attempt")
    fallback_steam_path = get_steam_path()
    if fallback_steam_path and fallback_steam_path != steam_path:
        log_once(logger, "Novo caminho Steam descoberto: " + str(fallback_steam_path), key="steam_path_discovered")
        if create_hid_dll(fallback_steam_path):
            return True
    
    log_once(logger, "Todas as tentativas de criar hid.dll falharam", level=logging.ERROR, key="dll_creation_all_failed")
    return False

def check_hid_dll_status(steam_path=None):
    """
    ✅ CORREÇÃO DEFINITIVA: Verifica o status UMA ÚNICA VEZ
    Retorna: dict com status detalhado (cacheado)
    """
    global _DLL_VERIFICATION_DONE, _DLL_VERIFICATION_RESULT
    
    logger = setup_dll_logging()
    
    # ✅ VERIFICAÇÃO ÚNICA - retorna cache sempre após primeira verificação
    if _DLL_VERIFICATION_DONE:
        logger.debug("Retornando cache de verificação DLL (única)")
        return _DLL_VERIFICATION_RESULT
    
    if not steam_path:
        steam_path = get_steam_path()
    
    dll_path = os.path.join(steam_path, "hid.dll") if steam_path else None
    
    status = {
        "exists": False,
        "valid": False,
        "path": dll_path,
        "size": 0,
        "steam_found": bool(steam_path),
        "steam_path": steam_path,
        "writable": False,
        "backup_exists": False,
        "base64_file_found": False,
        "last_verified": time.time()
    }
    
    # ✅ VERIFICAÇÃO BASE64 (usa cache da função)
    status["base64_file_found"] = get_hid_dll_base64_path() is not None
    
    if steam_path and dll_path:
        status["exists"] = os.path.exists(dll_path)
        
        if status["exists"]:
            try:
                status["size"] = os.path.getsize(dll_path)
                status["valid"] = verify_hid_dll_integrity(dll_path)
            except OSError:
                status["size"] = 0
                status["valid"] = False
        
        # ✅ Verificar permissões de escrita (apenas uma vez)
        if not hasattr(check_hid_dll_status, '_writable_cache'):
            check_hid_dll_status._writable_cache = {}
        
        cache_key = f"writable_{steam_path}"
        if cache_key not in check_hid_dll_status._writable_cache:
            try:
                test_file = os.path.join(steam_path, "write_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                check_hid_dll_status._writable_cache[cache_key] = True
            except:
                check_hid_dll_status._writable_cache[cache_key] = False
        
        status["writable"] = check_hid_dll_status._writable_cache[cache_key]
        
        # Verificar se existe backup
        backup_dir = os.path.join(steam_path, "otosteam_backups")
        status["backup_exists"] = os.path.exists(backup_dir) and any(
            f.endswith('.backup') for f in os.listdir(backup_dir)
        )
    
    # ✅ MARCA COMO VERIFICADO UMA ÚNICA VEZ
    _DLL_VERIFICATION_DONE = True
    _DLL_VERIFICATION_RESULT = status
    
    # ✅ LOG APENAS NA PRIMEIRA VEZ
    status_msg = f"Status hid.dll: Existe={status['exists']}, Valida={status['valid']}, Steam={status['steam_found']}"
    logger.info(status_msg)
    
    return status

def get_detailed_dll_report():
    """Gera relatório detalhado do status da DLL"""
    status = check_hid_dll_status()
    
    report = [
        "RELATORIO DETALHADO HID.DLL",
        f"Caminho Steam: {status['steam_path']}",
        f"Steam encontrado: {'SIM' if status['steam_found'] else 'NAO'}",
        f"DLL existe: {'SIM' if status['exists'] else 'NAO'}",
        f"DLL valida: {'SIM' if status['valid'] else 'NAO'}",
        f"Tamanho DLL: {status['size']} bytes",
        f"Gravavel: {'SIM' if status['writable'] else 'NAO'}",
        f"Backup: {'DISPONIVEL' if status['backup_exists'] else 'NAO'}",
        f"Base64: {'ENCONTRADO' if status['base64_file_found'] else 'NAO ENCONTRADO'}",
    ]
    
    return "\n".join(report)

def initialize_dll_system():
    """
    ✅ CORREÇÃO DEFINITIVA: Inicializa o sistema DLL UMA ÚNICA VEZ
    Retorna: dict com status da inicialização (cacheado)
    """
    global _DLL_SYSTEM_INITIALIZED, _DLL_SYSTEM_RESULT
    
    # ✅ SE JÁ FOI INICIALIZADO, RETORNA RESULTADO CACHEADO
    if _DLL_SYSTEM_INITIALIZED:
        logger = setup_dll_logging()
        logger.debug("Sistema DLL já inicializado - retornando cache")
        return _DLL_SYSTEM_RESULT
    
    logger = setup_dll_logging()
    log_once(logger, "INICIANDO SISTEMA DLL (VERIFICAÇÃO ÚNICA)...", key="dll_system_start")
    
    result = {
        "success": False,
        "steam_found": False,
        "dll_created": False,
        "dll_valid": False,
        "errors": []
    }
    
    try:
        # 1. Verificar Steam
        steam_path = get_steam_path()
        if not steam_path:
            result["errors"].append("Steam nao encontrado")
            _DLL_SYSTEM_RESULT = result
            _DLL_SYSTEM_INITIALIZED = True
            return result
        
        result["steam_found"] = True
        
        # 2. Verificar/criar DLL
        if recreate_hid_dll(steam_path):
            result["dll_created"] = True
            
            # 3. Verificar validade final (usa a verificação única)
            dll_status = check_hid_dll_status(steam_path)
            result["dll_valid"] = dll_status["valid"]
            result["success"] = dll_status["valid"]
            
            if result["success"]:
                log_once(logger, "Sistema DLL inicializado com sucesso! (ÚNICA VEZ)", key="dll_system_success")
            else:
                result["errors"].append("DLL criada mas invalida")
                log_once(logger, "DLL criada mas invalida", level=logging.ERROR, key="dll_invalid_after_creation")
        else:
            result["errors"].append("Falha ao criar DLL")
            log_once(logger, "Falha ao criar DLL", level=logging.ERROR, key="dll_creation_failed")
            
    except Exception as e:
        error_msg = f"Erro critico na inicializacao DLL: {str(e)}"
        log_once(logger, error_msg, level=logging.ERROR, key="dll_system_critical_error")
        result["errors"].append(error_msg)
    
    # ✅ SALVAR NO CACHE GLOBAL PARA CHAMADAS FUTURAS
    _DLL_SYSTEM_RESULT = result
    _DLL_SYSTEM_INITIALIZED = True
    
    return result

# 🔥 CORREÇÃO: Adicionar funções de compatibilidade para o main.py
def ensure_hid_dll_initialized():
    """Função de compatibilidade com chamadas antigas"""
    return recreate_hid_dll()

def get_dll_simple_status():
    """Retorna status simplificado da DLL"""
    status = check_hid_dll_status()
    return {
        'dll_available': status.get('valid', False),
        'dll_exists': status.get('exists', False),
        'steam_found': status.get('steam_found', False),
        'writable': status.get('writable', False),
        'ready': status.get('valid', False) and status.get('steam_found', False)
    }

# ✅ CORREÇÃO: Função para resetar cache (se necessário para testes)
def reset_dll_cache():
    """Reseta todo o cache do sistema DLL - útil para testes"""
    global _DLL_VERIFICATION_DONE, _DLL_VERIFICATION_RESULT
    global _DLL_SYSTEM_INITIALIZED, _DLL_SYSTEM_RESULT
    global _LAST_LOG_MESSAGE, _LAST_LOG_TIME
    
    _DLL_VERIFICATION_DONE = False
    _DLL_VERIFICATION_RESULT = None
    _DLL_SYSTEM_INITIALIZED = False
    _DLL_SYSTEM_RESULT = None
    _LAST_LOG_MESSAGE = {}
    _LAST_LOG_TIME = {}
    
    # Resetar caches de funções específicas
    if hasattr(get_hid_dll_base64_path, '_cached_result'):
        delattr(get_hid_dll_base64_path, '_cached_result')
    
    if hasattr(check_hid_dll_status, '_writable_cache'):
        delattr(check_hid_dll_status, '_writable_cache')
    
    logger = setup_dll_logging()
    logger.info("Cache do sistema DLL resetado")

# Teste direto - CORRIGIDO
if __name__ == "__main__":
    # Configura logging para execução direta
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    print(safe_log_message("Teste do DLL Manager - VERSAO DEFINITIVA VERIFICAÇÃO ÚNICA"))
    print("=" * 50)
    
    # Teste de inicialização completa (APENAS UMA VEZ)
    init_result = initialize_dll_system()
    print(f"Inicializacao: {init_result['success']}")
    
    # Teste de status (DEVE USAR CACHE)
    status = check_hid_dll_status()
    print(f"Status: Existe={status['exists']}, Valida={status['valid']}")
    
    # Teste novamente (DEVE USAR CACHE)
    status2 = check_hid_dll_status()
    print(f"Status2 (cache): Existe={status2['exists']}, Valida={status2['valid']}")
    
    print("\n" + "=" * 50)
    print("Relatorio Detalhado:")
    print(get_detailed_dll_report())
    
    # Teste reset de cache
    print("\n" + "=" * 50)
    reset_dll_cache()
    print("Cache resetado - pode testar novamente")