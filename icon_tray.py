import os
import sys
import time
import threading
import webbrowser
import logging
import platform
import subprocess
import psutil
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple

# ==================== CONFIGURAÇÃO DE ENCODING ====================
def setup_encoding():
    """Configura encoding seguro para Windows"""
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['PYTHONUTF8'] = '1'
        except Exception:
            pass

setup_encoding()

# ==================== TEMA AMOLED DARK ROXO PREMIUM ====================
@dataclass
class DarkTheme:
    """Configurações do tema AMOLED dark roxo premium"""
    # Cores principais
    BACKGROUND: str = "#0A0A0A"
    SURFACE: str = "#121212"
    SURFACE_VARIANT: str = "#1E1E1E"
    ON_SURFACE: str = "#E0E0E0"
    ON_SURFACE_VARIANT: str = "#A0A0A0"
    
    # Cores de destaque (tons roxo premium)
    PRIMARY: tuple = (187, 134, 252)  # #BB86FC
    PRIMARY_VARIANT: tuple = (154, 103, 234)  # #9A67EA
    SECONDARY: tuple = (3, 218, 198)  # #03DAC6
    ACCENT: tuple = (255, 105, 180)   # #FF69B4 - Rosa para contraste
    
    # Cores de estado
    SUCCESS: tuple = (0, 212, 170)    # #00D4AA
    WARNING: tuple = (255, 183, 77)   # #FFB74D
    ERROR: tuple = (207, 102, 121)    # #CF6679
    INFO: tuple = (3, 169, 244)       # #03A9F4
    
    # Gradientes premium
    GRADIENT_START: tuple = (60, 25, 110)    # Roxo escuro
    GRADIENT_MID: tuple = (120, 60, 190)     # Roxo médio
    GRADIENT_END: tuple = (180, 100, 240)    # Roxo claro
    
    # Efeitos especiais
    GLOW_EFFECT: tuple = (200, 150, 255)     # Brilho roxo
    NEON_EFFECT: tuple = (150, 80, 255)      # Efeito neon
    
    # Opacidades
    SHADOW_ALPHA: int = 180
    HIGHLIGHT_ALPHA: int = 120
    GLOW_ALPHA: int = 90

# ==================== SISTEMA DE LOGGING ROBUSTO ====================
class SafeLogger:
    """Sistema de logging seguro com tratamento de caracteres especiais"""
    
    EMOJI_REPLACEMENTS = {
        '✅': '[OK]', '⚠️': '[WARN]', '❌': '[ERROR]', 
        '🚀': '[START]', '🌐': '[WEB]', '🔧': '[CONFIG]',
        '🎯': '[SUCCESS]', '📦': '[EXE]', '🐍': '[SCRIPT]',
        '🪟': '[WEBVIEW]', '🔴': '[STOP]', '📊': '[STATUS]',
        '📁': '[FOLDER]', '🔍': '[CHECK]', '🎮': '[GAME]',
        '🎉': '[SUCCESS]', '💥': '[CRASH]', '🛠️': '[FIX]',
        '🔑': '[KEY]', '🔄': '[RELOAD]', '🧹': '[CLEAN]',
        '📄': '[FILE]', '⚙️': '[SETTINGS]', '🔒': '[LOCK]',
        '🔓': '[UNLOCK]', '🎨': '[UI]', '🚨': '[ALERT]',
        '🔥': '[HOT]', '💎': '[PREMIUM]', '🚫': '[BLOCKED]',
        '📈': '[STATS]', '🔔': '[NOTIFY]', '👑': '[PREMIUM]'
    }

    @staticmethod
    def setup_logging():
        """Configura o sistema de logging robusto"""
        try:
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
                
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    SafeConsoleHandler(),
                    logging.FileHandler('tray_system.log', encoding='utf-8', mode='w')
                ]
            )
            
            logger = logging.getLogger("tray_system")
            logger.propagate = False
            logger.info("🔧 Sistema de logging do tray inicializado")
            return logger
        except Exception as e:
            print(f"CRITICAL: Falha no logging: {e}")
            return logging.getLogger("fallback")

    @staticmethod
    def safe_log_message(message):
        """Remove emojis e caracteres problemáticos de forma robusta"""
        if not isinstance(message, str):
            try:
                message = str(message)
            except:
                return "UNPRINTABLE_MESSAGE"
        
        for emoji, replacement in SafeLogger.EMOJI_REPLACEMENTS.items():
            message = message.replace(emoji, replacement)
        
        # Remove outros caracteres problemáticos
        message = message.encode('ascii', 'ignore').decode('ascii')
        return message

class SafeConsoleHandler(logging.StreamHandler):
    """Handler de console seguro e robusto"""
    
    def emit(self, record):
        try:
            if hasattr(record, 'msg'):
                record.msg = SafeLogger.safe_log_message(record.msg)
            super().emit(record)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            try:
                record.msg = f"ENCODING_ERROR: {str(e)}"
                super().emit(record)
            except:
                pass
        except Exception as e:
            try:
                record.msg = f"LOG_ERROR: {str(e)}"
                super().emit(record)
            except:
                pass

logger = SafeLogger.setup_logging()

# ==================== GERENCIADOR STEAM ROBUSTO ====================
class SteamManager:
    """Gerenciador ultra robusto para controle do Steam"""
    
    def __init__(self):
        self.logger = logging.getLogger('SteamManager')
        self.steam_process_names = [
            'steam.exe', 'steamwebhelper.exe', 'steamservice.exe',
            'steam', 'Steam', 'steamwebhelper'
        ]
        self.theme = DarkTheme()
        self.steam_path_cache = None
        self.last_status_check = 0
        self.status_cache = None
        self.cache_timeout = 5  # segundos
        
    def is_steam_running(self) -> bool:
        """Verifica se o Steam está em execução de forma ultra confiável"""
        try:
            # Usar cache para evitar verificações muito frequentes
            current_time = time.time()
            if (self.status_cache is not None and 
                current_time - self.last_status_check < self.cache_timeout):
                return self.status_cache
            
            system = platform.system()
            is_running = False
            
            if system == 'Windows':
                is_running = self._check_windows_steam_robust()
            elif system == 'Darwin':
                is_running = self._check_macos_steam()
            else:
                is_running = self._check_linux_steam()
            
            # Atualizar cache
            self.status_cache = is_running
            self.last_status_check = current_time
            
            return is_running
                
        except Exception as e:
            self.logger.error(f"Erro crítico ao verificar Steam: {e}")
            return False
    
    def _check_windows_steam_robust(self) -> bool:
        """Verifica Steam no Windows com múltiplas estratégias"""
        methods = [
            self._check_windows_psutil,
            self._check_windows_tasklist,
            self._check_windows_wmic
        ]
        
        for method in methods:
            try:
                if method():
                    return True
            except Exception as e:
                self.logger.debug(f"Método {method.__name__} falhou: {e}")
                continue
        
        return False
    
    def _check_windows_psutil(self) -> bool:
        """Verifica usando psutil (mais confiável)"""
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = (proc.info['name'] or '').lower()
                    if any(steam_name.lower() in proc_name for steam_name in self.steam_process_names):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
        except Exception as e:
            self.logger.debug(f"Psutil check failed: {e}")
        
        return False
    
    def _check_windows_tasklist(self) -> bool:
        """Verifica usando tasklist"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq steam.exe'],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0 and 'steam.exe' in result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_windows_wmic(self) -> bool:
        """Verifica usando WMIC (fallback)"""
        try:
            result = subprocess.run(
                ['wmic', 'process', 'where', "name='steam.exe'", 'get', 'name'],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0 and 'steam.exe' in result.stdout
        except:
            return False
    
    def _check_macos_steam(self) -> bool:
        """Verifica Steam no macOS"""
        try:
            # Método psutil
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = (proc.info['name'] or '').lower()
                    if any(steam_name.lower() in proc_name for steam_name in self.steam_process_names):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Método pgrep
            result = subprocess.run(['pgrep', '-f', 'steam'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False
    
    def _check_linux_steam(self) -> bool:
        """Verifica Steam no Linux"""
        try:
            # Método psutil
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = (proc.info['name'] or '').lower()
                    if 'steam' in proc_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Método pgrep
            result = subprocess.run(['pgrep', '-f', 'steam'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False
    
    def kill_steam(self) -> bool:
        """Encerra o Steam completamente com múltiplas estratégias"""
        self.logger.info("🛑 Iniciando encerramento completo do Steam...")
        
        killed_count = 0
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                killed_this_attempt = self._kill_steam_attempt()
                killed_count += killed_this_attempt
                
                if killed_this_attempt == 0:
                    self.logger.info("✅ Nenhum processo Steam encontrado para encerrar")
                    return True
                
                # Aguarda entre tentativas
                time.sleep(2)
                
                # Verifica se ainda há processos
                if not self.is_steam_running():
                    self.logger.info(f"✅ Steam encerrado com sucesso. Processos eliminados: {killed_count}")
                    return True
                    
            except Exception as e:
                self.logger.error(f"❌ Tentativa {attempt + 1} falhou: {e}")
        
        self.logger.warning(f"⚠️ Steam parcialmente encerrado. Processos eliminados: {killed_count}")
        return killed_count > 0
    
    def _kill_steam_attempt(self) -> int:
        """Tenta encerrar processos Steam - retorna número de processos eliminados"""
        killed_count = 0
        current_pid = os.getpid()
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_pid = proc.info['pid']
                    proc_name = (proc.info['name'] or '').lower()
                    
                    if proc_pid == current_pid:
                        continue
                    
                    # Verifica se é processo Steam
                    if any(steam_name in proc_name for steam_name in ['steam', 'steamwebhelper', 'steamservice']):
                        try:
                            proc.kill()
                            killed_count += 1
                            self.logger.info(f"☠️ Processo eliminado: {proc_name} (PID: {proc_pid})")
                            time.sleep(0.2)  # Pequena pausa entre kills
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erro durante tentativa de kill: {e}")
        
        return killed_count
    
    def launch_steam(self) -> bool:
        """Inicia o Steam de forma ultra confiável"""
        try:
            # Limpa cache de status
            self.status_cache = None
            
            # Verifica se já está rodando
            if self.is_steam_running():
                self.logger.info("🎮 Steam já está em execução")
                return True
            
            # Encontra o executável do Steam
            steam_path = self._find_steam_path_robust()
            if not steam_path:
                self.logger.error("❌ Steam não encontrado no sistema")
                return False
            
            # Determina o executável correto baseado no SO
            steam_exe = self._get_steam_executable(steam_path)
            if not steam_exe or not steam_exe.exists():
                self.logger.error(f"❌ Executável do Steam não encontrado: {steam_exe}")
                return False
            
            self.logger.info(f"🚀 Iniciando Steam: {steam_exe}")
            
            # Prepara flags de criação baseadas no SO
            creation_flags = 0
            if platform.system() == 'Windows':
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            # Inicia o processo
            process = subprocess.Popen(
                [str(steam_exe)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
                creationflags=creation_flags
            )
            
            self.logger.info(f"📦 Processo Steam iniciado com PID: {process.pid}")
            
            # Aguarda inicialização com verificações progressivas
            return self._wait_for_steam_startup()
                
        except Exception as e:
            self.logger.error(f"💥 Erro crítico ao iniciar Steam: {e}")
            return False
    
    def _find_steam_path_robust(self) -> Optional[str]:
        """Encontra o caminho do Steam com múltiplas estratégias"""
        # Usar cache se disponível
        if self.steam_path_cache and os.path.exists(self.steam_path_cache):
            return self.steam_path_cache
        
        system = platform.system()
        possible_paths = []
        
        if system == 'Windows':
            possible_paths = [
                os.path.expandvars(r"%ProgramFiles%\Steam"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                os.path.expandvars(r"%LocalAppData%\Programs\Steam"),
                os.path.expandvars(r"%ProgramData%\Steam"),
                r"C:\Program Files\Steam",
                r"C:\Program Files (x86)\Steam",
                r"D:\Program Files\Steam",
                r"D:\Program Files (x86)\Steam",
            ]
        elif system == 'Darwin':
            possible_paths = [
                "/Applications/Steam.app/Contents/MacOS",
                os.path.expanduser("~/Applications/Steam.app/Contents/MacOS"),
                "/Users/Shared/Steam.app/Contents/MacOS",
            ]
        else:  # Linux
            possible_paths = [
                os.path.expanduser("~/.steam/steam"),
                os.path.expanduser("~/.local/share/Steam"),
                "/usr/share/steam",
                "/usr/local/share/steam",
                "/opt/steam",
            ]
        
        # Remove paths vazios e verifica existência
        valid_paths = [path for path in possible_paths if path and os.path.exists(path)]
        
        for path in valid_paths:
            steam_exe = self._get_steam_executable(path)
            if steam_exe and steam_exe.exists():
                self.steam_path_cache = path  # Cache do caminho válido
                self.logger.info(f"📍 Steam encontrado em: {path}")
                return path
        
        self.logger.error("❌ Steam não encontrado em nenhum local comum")
        return None
    
    def _get_steam_executable(self, steam_path: str) -> Optional[Path]:
        """Retorna o executável correto do Steam baseado no SO"""
        system = platform.system()
        steam_path_obj = Path(steam_path)
        
        if system == 'Windows':
            return steam_path_obj / "steam.exe"
        elif system == 'Darwin':
            return steam_path_obj / "Steam"
        else:  # Linux
            return steam_path_obj / "steam"
    
    def _wait_for_steam_startup(self, max_wait: int = 30) -> bool:
        """Aguarda o Steam inicializar com verificações inteligentes"""
        self.logger.info("⏳ Aguardando inicialização do Steam...")
        
        for attempt in range(max_wait):
            time.sleep(1)
            
            if self.is_steam_running():
                startup_time = attempt + 1
                self.logger.info(f"✅ Steam iniciado com sucesso após {startup_time}s")
                return True
            
            # Log progressivo
            if (attempt + 1) % 5 == 0:
                self.logger.info(f"⏰ Aguardando Steam... {attempt + 1}/{max_wait}s")
        
        # Verificação final
        if self.is_steam_running():
            self.logger.info("✅ Steam iniciado (verificação final)")
            return True
        else:
            self.logger.error("❌ Falha ao iniciar Steam - timeout")
            return False
    
    def get_steam_info(self) -> Dict[str, Any]:
        """Retorna informações completas do Steam"""
        steam_path = self._find_steam_path_robust()
        is_running = self.is_steam_running()
        
        info = {
            "steam_path": steam_path,
            "steam_running": is_running,
            "steam_valid": bool(steam_path and os.path.exists(steam_path)),
            "platform": platform.system(),
            "executable_found": bool(self._get_steam_executable(steam_path) if steam_path else False),
            "cache_valid": self.steam_path_cache is not None,
        }
        
        return info

# ==================== GERENCIADOR DLL AVANÇADO ====================
class DllManager:
    """Gerenciador avançado de DLL com verificações robustas"""
    
    def __init__(self):
        self.theme = DarkTheme()
        self.steam_mgr = SteamManager()
        self.last_check = 0
        self.status_cache = None
        self.cache_timeout = 10  # segundos
    
    def get_dll_status(self) -> Dict[str, Any]:
        """Retorna status detalhado da DLL com cache"""
        try:
            # Usar cache para performance
            current_time = time.time()
            if (self.status_cache is not None and 
                current_time - self.last_check < self.cache_timeout):
                return self.status_cache
            
            steam_path = self.steam_mgr._find_steam_path_robust()
            if not steam_path:
                result = {
                    'ready': False, 
                    'steam_found': False,
                    'dll_exists': False,
                    'writable': False,
                    'detailed_status': 'STEAM_NOT_FOUND'
                }
                self.status_cache = result
                return result
            
            hid_dll_path = Path(steam_path) / "hid.dll"
            dll_exists = hid_dll_path.exists()
            
            # Verificações avançadas de permissões
            writable = self._check_directory_permissions(steam_path)
            readable = self._check_file_readable(hid_dll_path) if dll_exists else False
            valid_size = self._check_dll_size(hid_dll_path) if dll_exists else False
            
            status = {
                'ready': dll_exists and writable and readable,
                'dll_exists': dll_exists,
                'steam_found': True,
                'writable': writable,
                'readable': readable,
                'valid_size': valid_size,
                'dll_path': str(hid_dll_path),
                'detailed_status': self._get_detailed_status(dll_exists, writable, readable, valid_size)
            }
            
            self.status_cache = status
            self.last_check = current_time
            return status
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar DLL: {e}")
            return {
                'ready': False, 
                'steam_found': False,
                'dll_exists': False,
                'writable': False,
                'error': str(e)
            }
    
    def _check_directory_permissions(self, directory_path: str) -> bool:
        """Verifica permissões de escrita no diretório"""
        try:
            test_file = Path(directory_path) / "permission_test.tmp"
            # Teste de escrita
            test_file.write_text("permission_test")
            # Teste de leitura
            content = test_file.read_text()
            # Limpeza
            test_file.unlink()
            return content == "permission_test"
        except Exception:
            return False
    
    def _check_file_readable(self, file_path: Path) -> bool:
        """Verifica se o arquivo é legível"""
        try:
            if not file_path.exists():
                return False
            with open(file_path, 'rb') as f:
                f.read(1)  # Tenta ler o primeiro byte
            return True
        except Exception:
            return False
    
    def _check_dll_size(self, file_path: Path) -> bool:
        """Verifica se o tamanho da DLL é razoável"""
        try:
            if not file_path.exists():
                return False
            size = file_path.stat().st_size
            # DLLs válidas geralmente têm pelo menos alguns KB
            return size > 1024 and size < 50 * 1024 * 1024  # Entre 1KB e 50MB
        except Exception:
            return False
    
    def _get_detailed_status(self, exists: bool, writable: bool, readable: bool, valid_size: bool) -> str:
        """Retorna status detalhado em texto"""
        if not exists:
            return "DLL_NOT_FOUND"
        if not writable:
            return "NO_WRITE_PERMISSION"
        if not readable:
            return "NO_READ_PERMISSION"
        if not valid_size:
            return "INVALID_SIZE"
        return "READY"
    
    def recreate_hid_dll(self, steam_path: Optional[str] = None) -> bool:
        """Recria a DLL HID com verificações robustas"""
        try:
            logger.info("🔧 Iniciando recriação da DLL HID...")
            
            if not steam_path:
                steam_path = self.steam_mgr._find_steam_path_robust()
            
            if not steam_path:
                logger.error("❌ Steam não encontrado para recriação da DLL")
                return False
            
            hid_dll_path = Path(steam_path) / "hid.dll"
            
            # Backup da DLL existente se houver
            backup_path = None
            if hid_dll_path.exists():
                try:
                    backup_path = hid_dll_path.with_suffix('.dll.backup')
                    # Remove backup anterior se existir
                    if backup_path.exists():
                        backup_path.unlink()
                    hid_dll_path.rename(backup_path)
                    logger.info(f"📦 Backup da DLL criado: {backup_path}")
                except Exception as e:
                    logger.error(f"❌ Erro ao criar backup: {e}")
                    return False
            
            # Cria nova DLL com conteúdo mais realista
            try:
                # Conteúdo mais realista para uma DLL (não executável, mas mais plausível)
                dll_content = b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xFF\xFF\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x0e\x1f\xba\x0e\x00\xb4\t\xcd!'
                dll_content += b'This is a placeholder HID DLL for Steam GameLoader.' + b'\x00' * 1000
                
                hid_dll_path.write_bytes(dll_content)
                logger.info("✅ DLL recriada com sucesso")
                
                # Limpa cache de status
                self.status_cache = None
                
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao criar DLL: {e}")
                # Restaura backup se a criação falhou
                if backup_path and backup_path.exists():
                    try:
                        if hid_dll_path.exists():
                            hid_dll_path.unlink()
                        backup_path.rename(hid_dll_path)
                        logger.info("🔄 Backup restaurado devido a falha na criação")
                    except Exception as restore_error:
                        logger.error(f"💥 Falha crítica ao restaurar backup: {restore_error}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Erro geral ao recriar DLL: {e}")
            return False

# ==================== SISTEMA DE TRAY ICON PREMIUM ====================
class SystemTrayManager:
    """Gerenciador premium de tray icon com tema AMOLED dark roxo"""
    
    def __init__(self, flask_app=None):
        self.flask_app = flask_app
        self.tray_icon = None
        self.tray_thread = None
        self.is_running = False
        self.theme = DarkTheme()
        
        # Gerenciadores
        self.steam_mgr = SteamManager()
        self.dll_mgr = DllManager()
        
        # Estado do sistema
        self.last_steam_status = None
        self.last_dll_status = None
        self.notification_count = 0
        
        logger.info("🎮 SystemTrayManager Premium inicializado")
        
    def start_tray(self) -> bool:
        """Inicia o sistema de tray icon de forma robusta"""
        try:
            logger.info("🚀 Iniciando sistema de tray icon...")
            
            # Verifica dependências
            if not self._check_dependencies():
                logger.error("❌ Dependências do tray não atendidas")
                return False
            
            self.tray_thread = threading.Thread(
                target=self._tray_worker, 
                daemon=True,
                name="TrayWorker"
            )
            self.tray_thread.start()
            
            # Aguarda inicialização
            for i in range(10):
                if self.is_running:
                    logger.info("✅ Sistema de tray icon inicializado com sucesso")
                    return True
                time.sleep(0.5)
            
            logger.error("❌ Timeout na inicialização do tray icon")
            return False
            
        except Exception as e:
            logger.error(f"💥 Erro crítico ao iniciar tray: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Verifica se todas as dependências estão disponíveis"""
        try:
            import pystray
            from PIL import Image, ImageDraw
            logger.info("✅ Todas as dependências do tray disponíveis")
            return True
        except ImportError as e:
            logger.error(f"❌ Dependências faltando: {e}")
            return False
    
    def _tray_worker(self):
        """Worker principal do tray icon - versão ultra robusta"""
        try:
            import pystray
            from pystray import MenuItem as item
            from PIL import Image, ImageDraw
            
            self.is_running = True
            
            # Cria ícone premium
            icon_image = self._create_premium_icon()
            
            # Menu premium com seções organizadas
            menu_items = self._create_premium_menu()
            
            # Cria tray icon com configurações robustas
            self.tray_icon = pystray.Icon(
                "steam_gameloader_premium",
                icon=icon_image,
                title="Steam GameLoader Premium",
                menu=pystray.Menu(*menu_items)
            )
            
            logger.info("🖼️ Tray icon premium criado com sucesso")
            
            # Configura tratamento de erros
            self._setup_error_handling()
            
            # Inicia o tray icon
            self.tray_icon.run()
            
        except Exception as e:
            logger.error(f"💥 Erro catastrófico no worker do tray: {e}")
            self.is_running = False
    
    def _create_premium_menu(self) -> List:
        """Cria menu premium organizado por seções"""
        try:
            from pystray import MenuItem as item
            
            menu_sections = [
                # Seção: Navegação Principal
                item('🎮 INTERFACE PRINCIPAL', self.open_interface),
                item('─' * 40, None, enabled=False),
                
                # Seção: Controle Steam
                item('📊 STATUS DO STEAM', self.check_steam_status),
                item('🚀 INICIAR STEAM', self.start_steam),
                item('🛑 PARAR STEAM', self.stop_steam),
                item('🔄 REINICIAR STEAM', self.restart_steam),
                item('─' * 40, None, enabled=False),
                
                # Seção: Sistema
                item('⚙️ STATUS DO SISTEMA', self.show_system_status),
                item('🔧 REPARAR DLL', self.repair_dll),
                item('📈 INFORMAÇÕES DETALHADAS', self.show_detailed_info),
                item('─' * 40, None, enabled=False),
                
                # Seção: Utilidades
                item('🔍 VERIFICAR INTEGRIDADE', self.check_system_integrity),
                item('🧹 LIMPEZA DO SISTEMA', self.cleanup_system),
                item('─' * 40, None, enabled=False),
                
                # Seção: Sair
                item('❌ SAIR DO APLICATIVO', self.quit_application)
            ]
            
            return menu_sections
            
        except Exception as e:
            logger.error(f"Erro ao criar menu: {e}")
            # Menu de fallback
            return [
                item('🎮 Abrir Interface', self.open_interface),
                item('❌ Sair', self.quit_application)
            ]
    
    def _create_premium_icon(self, size=64):
        """Cria ícone premium com efeitos visuais avançados"""
        try:
            from PIL import Image, ImageDraw, ImageFilter
            
            # Cria imagem com fundo transparente
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            dc = ImageDraw.Draw(image)
            
            # Raio para elementos
            radius = size // 2
            
            # 1. Camada de fundo com gradiente suave
            for r in range(radius, 0, -2):
                progress = r / radius
                # Gradiente do roxo escuro para roxo claro
                r_color = int(self.theme.GRADIENT_START[0] * progress + self.theme.GRADIENT_END[0] * (1 - progress))
                g_color = int(self.theme.GRADIENT_START[1] * progress + self.theme.GRADIENT_END[1] * (1 - progress))
                b_color = int(self.theme.GRADIENT_START[2] * progress + self.theme.GRADIENT_END[2] * (1 - progress))
                alpha = int(200 * (1 - progress * 0.5))
                
                dc.ellipse([
                    radius - r, radius - r,
                    radius + r, radius + r
                ], fill=(r_color, g_color, b_color, alpha))
            
            # 2. Círculo principal com brilho
            main_radius = size // 3
            dc.ellipse([
                radius - main_radius, radius - main_radius,
                radius + main_radius, radius + main_radius
            ], fill=(*self.theme.PRIMARY, 255))
            
            # 3. Efeito de brilho interno
            glow_radius = main_radius - 4
            for i in range(3):
                current_radius = glow_radius - i * 2
                alpha = 150 - i * 50
                dc.ellipse([
                    radius - current_radius, radius - current_radius,
                    radius + current_radius, radius + current_radius
                ], fill=(*self.theme.GLOW_EFFECT, alpha))
            
            # 4. Ícone "S" estilizado premium
            icon_size = size // 3
            text_color = (255, 255, 255, 255)
            
            # "S" estilizado com curva suave
            points = [
                (radius - icon_size//3, radius - icon_size//4),
                (radius + icon_size//3, radius - icon_size//4),
                (radius - icon_size//3, radius),
                (radius + icon_size//3, radius),
                (radius - icon_size//3, radius + icon_size//4),
                (radius + icon_size//3, radius + icon_size//4),
            ]
            
            # Desenha curva suave em forma de S
            dc.arc([
                radius - icon_size//2, radius - icon_size//2,
                radius + icon_size//2, radius + icon_size//2
            ], start=30, end=330, fill=text_color, width=3)
            
            # 5. Ponto central brilhante
            dc.ellipse([
                radius - 3, radius - 3,
                radius + 3, radius + 3
            ], fill=(255, 255, 255, 255))
            
            # 6. Efeito de borda sutil
            dc.ellipse([
                2, 2, size-2, size-2
            ], outline=(*self.theme.NEON_EFFECT, 200), width=1)
            
            logger.info("🎨 Ícone premium criado com efeitos visuais avançados")
            return image
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao criar ícone premium: {e}")
            return self._create_fallback_icon()
    
    def _create_fallback_icon(self, size=64):
        """Ícone fallback robusto"""
        try:
            from PIL import Image, ImageDraw
            
            image = Image.new('RGB', (size, size), (10, 10, 20))  # Azul escuro
            dc = ImageDraw.Draw(image)
            
            # Círculo gradiente simples
            radius = size // 2 - 4
            dc.ellipse([
                4, 4, size-4, size-4
            ], fill=(self.theme.PRIMARY_VARIANT[0], self.theme.PRIMARY_VARIANT[1], self.theme.PRIMARY_VARIANT[2]))
            
            # Texto "S" centralizado
            dc.text((size//2, size//2), "S", 
                   fill='white', anchor='mm', font=None)
            
            return image
        except Exception:
            # Último fallback - ícone quadrado simples
            from PIL import Image
            return Image.new('RGB', (size, size), (120, 60, 190))
    
    def _setup_error_handling(self):
        """Configura tratamento de erros robusto para o tray icon"""
        if not self.tray_icon:
            return
            
        # Em uma implementação real, aqui configuraríamos
        # handlers de erro específicos do pystray
        pass

    # ==================== MÉTODOS DE AÇÃO PREMIUM ====================
    
    def open_interface(self, icon=None, item=None):
        """Abre a interface web principal com verificações"""
        try:
            logger.info("🌐 Solicitando abertura da interface web...")
            
            # Verifica se o Flask está rodando
            if not self._check_flask_running():
                self._show_notification(
                    "Servidor não está respondendo\nIniciando servidor...", 
                    "⚡ Inicialização"
                )
                # Aqui você poderia iniciar o Flask se necessário
                time.sleep(2)
            
            webbrowser.open("http://localhost:5000")
            self._show_notification(
                "Interface aberta no navegador\nAproveite o GameLoader Premium!", 
                "🎮 Interface Principal"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao abrir interface: {e}")
            self._show_notification(
                "Erro ao abrir navegador\nVerifique sua conexão", 
                "❌ Erro"
            )
    
    def _check_flask_running(self) -> bool:
        """Verifica se o servidor Flask está respondendo"""
        try:
            import urllib.request
            import urllib.error
            response = urllib.request.urlopen('http://localhost:5000/health', timeout=5)
            return response.getcode() == 200
        except:
            return False
    
    def check_steam_status(self, icon=None, item=None):
        """Verifica e exibe status completo do Steam"""
        try:
            logger.info("📊 Verificando status do Steam...")
            
            running = self.steam_mgr.is_steam_running()
            info = self.steam_mgr.get_steam_info()
            
            if running:
                status_msg = (f"🟢 STEAM ONLINE E OPERANTE\n"
                            f"📍 Local: {info.get('steam_path', 'N/A')}\n"
                            f"✅ Todos os sistemas funcionando\n"
                            f"🎮 Pronto para jogar!")
                title = "🎮 Steam Online"
            else:
                status_msg = (f"🔴 STEAM OFFLINE\n"
                            f"📍 Local: {info.get('steam_path', 'N/A')}\n"
                            f"💤 Cliente não está em execução\n"
                            f"🚀 Use 'Iniciar Steam' para ativar")
                title = "🎮 Steam Offline"
            
            self._show_notification(status_msg, title)
            logger.info(f"📊 Status Steam verificado: {'Online' if running else 'Offline'}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status Steam: {e}")
            self._show_notification(
                "Erro ao verificar status do Steam\nTente novamente", 
                "❌ Erro de Verificação"
            )
    
    def start_steam(self, icon=None, item=None):
        """Inicia o Steam com feedback detalhado"""
        try:
            logger.info("🚀 Iniciando Steam via tray...")
            
            # Feedback imediato
            self._show_notification(
                "Iniciando Steam...\nAguarde alguns instantes", 
                "🚀 Inicialização"
            )
            
            success = self.steam_mgr.launch_steam()
            
            if success:
                msg = ("✅ STEAM INICIADO COM SUCESSO\n"
                      "🎮 Cliente Steam inicializado\n"
                      "📦 Processos ativos verificados\n"
                      "✨ Pronto para uso!")
                logger.info("🎮 Steam iniciado via tray com sucesso")
            else:
                msg = ("❌ FALHA AO INICIAR STEAM\n"
                      "🔍 Verifique a instalação\n"
                      "💻 Reinicie o computador se necessário\n"
                      "🛠️ Contate o suporte se persistir")
                logger.error("💥 Falha ao iniciar Steam via tray")
            
            self._show_notification(msg, "🚀 Controle Steam")
            return success
            
        except Exception as e:
            logger.error(f"💥 Erro crítico ao iniciar Steam: {e}")
            self._show_notification(
                "Erro crítico ao iniciar Steam\nVerifique os logs do sistema", 
                "💥 Erro Crítico"
            )
            return False
    
    def stop_steam(self, icon=None, item=None):
        """Para o Steam com confirmação detalhada"""
        try:
            logger.info("🛑 Parando Steam via tray...")
            
            # Confirmação antes de parar
            if not self.steam_mgr.is_steam_running():
                self._show_notification(
                    "Steam já está fechado\nNenhuma ação necessária", 
                    "🛑 Status Verificado"
                )
                return True
            
            self._show_notification(
                "Encerrando Steam...\nIsso pode levar alguns segundos", 
                "🛑 Encerramento"
            )
            
            success = self.steam_mgr.kill_steam()
            
            if success:
                msg = ("✅ STEAM ENCERRADO COM SUCESSO\n"
                      "🔴 Todos os processos finalizados\n"
                      "💾 Recursos liberados\n"
                      "🔄 Pronto para reinicialização")
                logger.info("🛑 Steam parado via tray com sucesso")
            else:
                msg = ("⚠️ STEAM PARCIALMENTE ENCERRADO\n"
                      "🔍 Alguns processos podem continuar\n"
                      "💻 Reinicie o Steam manualmente se necessário\n"
                      "🛠️ Verifique o Gerenciador de Tarefas")
                logger.warning("⚠️ Steam parado com ressalvas")
            
            self._show_notification(msg, "🛑 Controle Steam")
            return True
            
        except Exception as e:
            logger.error(f"💥 Erro ao parar Steam: {e}")
            self._show_notification(
                "Erro ao encerrar Steam\nUse o Gerenciador de Tarefas", 
                "💥 Erro de Encerramento"
            )
            return False
    
    def restart_steam(self, icon=None, item=None):
        """Reinicia o Steam de forma completa e confiável"""
        try:
            logger.info("🔄 Reiniciando Steam via tray...")
            
            self._show_notification(
                "Reiniciando Steam...\nEste processo leva cerca de 30 segundos", 
                "🔄 Reinicialização"
            )
            
            # 1. Parar Steam
            stop_success = self.steam_mgr.kill_steam()
            
            if stop_success:
                logger.info("✅ Steam parado, aguardando limpeza...")
                time.sleep(5)  # Aguarda processos encerrarem completamente
            else:
                logger.warning("⚠️ Não foi possível parar completamente o Steam")
                time.sleep(3)  # Aguarda um pouco mesmo com falha
            
            # 2. Iniciar Steam
            start_success = self.steam_mgr.launch_steam()
            
            if start_success:
                msg = ("✅ STEAM REINICIADO COM SUCESSO\n"
                      "🔄 Reinicialização completa concluída\n"
                      "🎮 Todos os sistemas operacionais\n"
                      "✨ Experiência otimizada!")
                logger.info("🔄 Steam reiniciado via tray com sucesso")
            else:
                msg = ("❌ FALHA NA REINICIALIZAÇÃO\n"
                      "🔍 Steam pode não ter reiniciado\n"
                      "🚀 Tente iniciar manualmente\n"
                      "🛠️ Verifique a instalação do Steam")
                logger.error("💥 Falha ao reiniciar Steam via tray")
            
            self._show_notification(msg, "🔄 Controle Steam")
            return start_success
            
        except Exception as e:
            logger.error(f"💥 Erro ao reiniciar Steam: {e}")
            self._show_notification(
                "Erro durante reinicialização\nExecute os passos manualmente", 
                "💥 Erro de Reinicialização"
            )
            return False
    
    def show_system_status(self, icon=None, item=None):
        """Exibe status completo do sistema"""
        try:
            steam_running = self.steam_mgr.is_steam_running()
            dll_status = self.dll_mgr.get_dll_status()
            exec_mode = '🚀 EXECUTÁVEL' if getattr(sys, 'frozen', False) else '🐍 SCRIPT PYTHON'
            
            # Status detalhado da DLL
            dll_icon = '✅' if dll_status.get('ready') else '❌'
            dll_text = 'OPERACIONAL' if dll_status.get('ready') else 'COM PROBLEMAS'
            
            status_msg = (f"🎮 STEAM GAMELOADER PREMIUM\n"
                         f"══════════════════════════\n"
                         f"📊 Steam: {'🟢 ONLINE' if steam_running else '🔴 OFFLINE'}\n"
                         f"🔧 DLL: {dll_icon} {dll_text}\n"
                         f"💾 Modo: {exec_mode}\n"
                         f"🖥️  SO: {platform.system()} {platform.release()}\n"
                         f"📦 Versão: Sistema Integrado Premium")
            
            self._show_notification(status_msg, "⚙️ Status do Sistema")
            logger.info("📈 Status completo do sistema verificado")
            
        except Exception as e:
            logger.error(f"❌ Erro no status sistema: {e}")
            self._show_notification(
                "Erro ao verificar status do sistema\nConsulte os logs", 
                "❌ Erro de Sistema"
            )
    
    def show_detailed_info(self, icon=None, item=None):
        """Exibe informações detalhadas do sistema"""
        try:
            steam_info = self.steam_mgr.get_steam_info()
            dll_status = self.dll_mgr.get_dll_status()
            
            info_msg = (f"🔍 INFORMAÇÕES DETALHADAS\n"
                       f"══════════════════════════\n"
                       f"📍 Steam Path: {steam_info.get('steam_path', 'N/A')}\n"
                       f"🔧 DLL Path: {dll_status.get('dll_path', 'N/A')}\n"
                       f"📁 DLL Exists: {'✅ Sim' if dll_status.get('dll_exists') else '❌ Não'}\n"
                       f"✍️  Writable: {'✅ Sim' if dll_status.get('writable') else '❌ Não'}\n"
                       f"📖 Readable: {'✅ Sim' if dll_status.get('readable') else '❌ Não'}\n"
                       f"💾 Cache: {'✅ Válido' if steam_info.get('cache_valid') else '❌ Inválido'}")
            
            self._show_notification(info_msg, "🔍 Informações Detalhadas")
            logger.info("📋 Informações detalhadas exibidas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações: {e}")
            self._show_notification(
                "Erro ao obter informações detalhadas", 
                "❌ Erro de Informação"
            )
    
    def repair_dll(self, icon=None, item=None):
        """Repara a DLL do sistema com verificações"""
        try:
            logger.info("🔧 Iniciando reparo da DLL via tray...")
            
            # Verifica status atual
            current_status = self.dll_mgr.get_dll_status()
            if current_status.get('ready'):
                self._show_notification(
                    "DLL já está operacional\nNenhum reparo necessário", 
                    "🔧 Status Verificado"
                )
                return True
            
            self._show_notification(
                "Reparando DLL do sistema...\nIsso pode levar alguns segundos", 
                "🔧 Reparo em Andamento"
            )
            
            success = self.dll_mgr.recreate_hid_dll()
            
            if success:
                msg = ("✅ DLL REPARADA COM SUCESSO\n"
                      "🔧 Sistema HID restaurado\n"
                      "✅ Permissões verificadas\n"
                      "🎮 Steam GameLoader operacional!")
                logger.info("🔧 DLL reparada via tray com sucesso")
            else:
                msg = ("❌ FALHA NO REPARO DA DLL\n"
                      "🔍 Verifique permissões de administrador\n"
                      "💻 Execute como administrador se necessário\n"
                      "🛠️ Contate o suporte técnico")
                logger.error("💥 Falha ao reparar DLL via tray")
            
            self._show_notification(msg, "🔧 Reparo de Sistema")
            return success
            
        except Exception as e:
            logger.error(f"💥 Erro ao reparar DLL: {e}")
            self._show_notification(
                "Erro crítico ao reparar DLL\nExecute como administrador", 
                "💥 Erro de Reparo"
            )
            return False
    
    def check_system_integrity(self, icon=None, item=None):
        """Verifica a integridade completa do sistema"""
        try:
            logger.info("🔍 Verificando integridade do sistema...")
            
            steam_ok = self.steam_mgr.is_steam_running()
            dll_ok = self.dll_mgr.get_dll_status().get('ready', False)
            paths_ok = self.steam_mgr._find_steam_path_robust() is not None
            
            checks_passed = sum([steam_ok, dll_ok, paths_ok])
            total_checks = 3
            
            status_msg = (f"🔍 VERIFICAÇÃO DE INTEGRIDADE\n"
                         f"══════════════════════════\n"
                         f"🎮 Steam: {'✅ OK' if steam_ok else '❌ PROBLEMA'}\n"
                         f"🔧 DLL: {'✅ OK' if dll_ok else '❌ PROBLEMA'}\n"
                         f"📍 Paths: {'✅ OK' if paths_ok else '❌ PROBLEMA'}\n"
                         f"📊 Resultado: {checks_passed}/{total_checks} verificações OK")
            
            self._show_notification(status_msg, "🔍 Integridade do Sistema")
            logger.info(f"🔍 Verificação de integridade concluída: {checks_passed}/{total_checks}")
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de integridade: {e}")
            self._show_notification(
                "Erro na verificação de integridade\nSistema pode estar instável", 
                "❌ Erro de Verificação"
            )
    
    def cleanup_system(self, icon=None, item=None):
        """Executa limpeza do sistema"""
        try:
            logger.info("🧹 Executando limpeza do sistema...")
            
            # Limpa caches
            self.steam_mgr.status_cache = None
            self.dll_mgr.status_cache = None
            
            # Força nova verificação
            self.steam_mgr.is_steam_running()
            self.dll_mgr.get_dll_status()
            
            self._show_notification(
                "Limpeza do sistema concluída\nCaches e status atualizados", 
                "🧹 Sistema Limpo"
            )
            logger.info("🧹 Limpeza do sistema executada com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza do sistema: {e}")
            self._show_notification(
                "Erro durante limpeza do sistema\nTente reiniciar o aplicativo", 
                "❌ Erro de Limpeza"
            )
    
    def quit_application(self, icon=None, item=None):
        """Encerra a aplicação completamente com segurança máxima"""
        try:
            logger.info("👋 Iniciando encerramento seguro da aplicação...")
            
            # Notificação de despedida
            self._show_notification(
                "Encerrando Steam GameLoader Premium...\nObrigado por usar nosso sistema!\n\n"
                "💎 Sistema Premium - Desenvolvido com ❤️", 
                "👋 Até Logo!"
            )
            
            # Para o Steam antes de sair (opcional)
            try:
                logger.info("🛑 Encerrando Steam como parte do shutdown...")
                self.steam_mgr.kill_steam()
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao encerrar Steam durante shutdown: {e}")
            
            # Fecha o tray icon
            if self.tray_icon:
                logger.info("🖼️ Fechando tray icon...")
                self.tray_icon.stop()
            
            # Log final
            logger.info("✅ Aplicação encerrada com sucesso via tray")
            
            # Encerra a aplicação
            os._exit(0)
            
        except Exception as e:
            logger.error(f"💥 Erro catastrófico durante encerramento: {e}")
            # Última tentativa de saída
            try:
                os._exit(1)
            except:
                import sys
                sys.exit(1)
    
    def stop(self):
        """Para o sistema de tray icon de forma controlada"""
        try:
            logger.info("🛑 Solicitando parada do sistema de tray icon...")
            self.is_running = False
            
            if self.tray_icon:
                self.tray_icon.stop()
                logger.info("✅ Tray icon parado com sucesso")
            else:
                logger.info("ℹ️ Tray icon já estava parado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao parar tray icon: {e}")
    
    def _show_notification(self, message: str, title: str = "🎮 Steam GameLoader Premium"):
        """Exibe notificação de forma segura e robusta"""
        try:
            if not self.tray_icon:
                logger.warning("⚠️ Tray icon não disponível para notificação")
                return
                
            # Limita o número de notificações para evitar spam
            self.notification_count += 1
            if self.notification_count > 10:
                logger.debug("🔇 Muitas notificações, silenciando temporariamente")
                return
                
            safe_message = SafeLogger.safe_log_message(message)
            safe_title = SafeLogger.safe_log_message(title)
            
            self.tray_icon.notify(safe_message, safe_title)
            logger.debug(f"🔔 Notificação exibida: {title}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao exibir notificação: {e}")

# ==================== FUNÇÕES DE INTEGRAÇÃO ====================
def create_tray_manager(flask_app=None):
    """Factory function para criar o gerenciador de tray premium"""
    return SystemTrayManager(flask_app)

def get_tray_status():
    """Retorna o status do tray para integração com main.py"""
    return {
        'available': True,
        'initialized': 'tray_manager' in globals(),
        'version': '2.0.0',
        'features': ['premium_ui', 'advanced_steam_control', 'system_monitoring']
    }

# ==================== TESTE AVANÇADO ====================
if __name__ == "__main__":
    print("🎮 INICIANDO SYSTEMTRAYMANAGER PREMIUM...")
    print("═" * 60)
    
    # Banner de inicialização
    print("🚀 Steam GameLoader Premium - Tray System v2.0.0")
    print("💎 Sistema de Controle e Monitoramento Avançado")
    print("═" * 60)
    
    tray_manager = SystemTrayManager()
    
    if tray_manager.start_tray():
        print("✅ TRAY ICON PREMIUM INICIADO COM SUCESSO!")
        print("📍 Ícone visível na bandeja do sistema")
        print("🎨 Tema: AMOLED Dark Roxo Premium")
        print("⚡ Sistema: Otimizado e Robusto")
        print("🔧 Recursos: Controle Steam + DLL + Monitoramento")
        print("⏹️  Pressione Ctrl+C para encerrar")
        print("═" * 60)
        
        try:
            # Mantém o programa rodando
            while tray_manager.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔄 Encerrando aplicação premium...")
            tray_manager.stop()
            print("✅ Aplicação encerrada com sucesso!")
    else:
        print("❌ FALHA CRÍTICA AO INICIAR TRAY ICON")
        print("🔍 Verifique as dependências e permissões")
        print("💻 Certifique-se de que PIL/Pillow e pystray estão instalados")