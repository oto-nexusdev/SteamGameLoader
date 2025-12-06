# utils/game_management.py - SISTEMA ESPECIALIZADO EM GERENCIAMENTO DE JOGOS .LUA
# VERSÃO DEFINITIVA CORRIGIDA - APENAS LÓGICA DE NEGÓCIO (SEM ROTAS FLASK)

import os
import json
import logging
import shutil
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import time

# Configuração de logging
logger = logging.getLogger(__name__)

# ================= CONFIGURAÇÕES ESPECIALIZADAS =================
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

GAME_NAMES_CACHE_FILE = CACHE_DIR / "steam_games_cache.json"

# ================= CONSTANTES STEAM =================
STEAM_API_BASE = "https://store.steampowered.com/api"

# ================= FUNÇÕES AUXILIARES ESPECIALIZADAS =================

def ensure_cache_dir():
    """Garante que o diretório de cache existe"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_game_names_cache() -> Dict[str, str]:
    """Carrega cache de nomes de jogos"""
    ensure_cache_dir()
    if GAME_NAMES_CACHE_FILE.exists():
        try:
            with open(GAME_NAMES_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.info(f"📁 Cache de nomes carregado: {len(cache_data)} entradas")
                return cache_data
        except Exception as e:
            logger.error(f"❌ Erro ao carregar cache de nomes: {e}")
    return {}

def save_game_names_cache(cache: Dict[str, str]):
    """Salva cache de nomes de jogos"""
    try:
        ensure_cache_dir()
        with open(GAME_NAMES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Cache de nomes salvo: {len(cache)} entradas")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar cache de nomes: {e}")

def get_game_name_from_steam(appid: str, cache: Dict[str, str]) -> Tuple[str, bool]:
    """Obtém nome do jogo da API Steam - Versão otimizada"""
    # Verificar cache primeiro
    if appid in cache:
        logger.debug(f"📦 Nome do jogo {appid} encontrado no cache")
        return cache[appid], True
    
    try:
        url = f"{STEAM_API_BASE}/appdetails?appids={appid}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        logger.info(f"🌐 Buscando nome do jogo {appid} na API Steam...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            app_data = data.get(str(appid), {})
            
            if app_data.get('success', False):
                game_data = app_data.get('data', {})
                real_name = game_data.get('name')
                
                if real_name:
                    # Limitar tamanho do nome se necessário
                    if len(real_name) > 100:
                        real_name = real_name[:100] + "..."
                    
                    cache[appid] = real_name
                    logger.info(f"✅ Nome encontrado: {real_name} (AppID: {appid})")
                    return real_name, True
                else:
                    logger.warning(f"⚠️ Nome não encontrado para AppID {appid}")
            else:
                logger.warning(f"⚠️ API Steam retornou success=False para AppID {appid}")
        else:
            logger.warning(f"⚠️ HTTP {response.status_code} para AppID {appid}")
            
    except requests.exceptions.Timeout:
        logger.warning(f"⏰ Timeout ao buscar nome para AppID {appid}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"🌐 Erro de conexão ao buscar nome para AppID {appid}")
    except Exception as e:
        logger.error(f"❌ Erro ao buscar nome do jogo {appid}: {e}")
    
    # Fallback
    fallback_name = f"AppID {appid}"
    cache[appid] = fallback_name
    return fallback_name, False

def detect_lua_games(steam_path: str) -> List[Dict]:
    """Detecta jogos baseado APENAS em arquivos .lua - FOCO EXCLUSIVO"""
    games = []
    
    if not steam_path or not Path(steam_path).exists():
        logger.warning(f"⚠️ Caminho do Steam não existe: {steam_path}")
        return games
        
    try:
        stplugin_path = Path(steam_path) / "config" / "stplug-in"
        
        if not stplugin_path.exists():
            logger.warning(f"⚠️ Diretório stplug-in não encontrado: {stplugin_path}")
            return games
        
        logger.info(f"🔍 Procurando arquivos .lua em: {stplugin_path}")
        lua_files = list(stplugin_path.glob("*.lua"))
        logger.info(f"📁 {len(lua_files)} arquivos .lua encontrados")
        
        for lua_file in lua_files:
            try:
                appid = lua_file.stem
                
                # Validar AppID (apenas números, comprimento razoável)
                if not appid.isdigit() or len(appid) < 5 or len(appid) > 10:
                    continue
                
                file_stats = lua_file.stat()
                file_size = file_stats.st_size
                
                # Filtro de tamanho mínimo (100 bytes)
                if file_size < 100:
                    continue
                
                # Formatar datas
                install_date = datetime.fromtimestamp(file_stats.st_mtime)
                created_date = datetime.fromtimestamp(file_stats.st_ctime)
                
                game_data = {
                    'appid': appid,
                    'name': f"AppID {appid}",  # Nome temporário
                    'type': 'lua',
                    'file_path': str(lua_file),
                    'size': file_size,
                    'size_formatted': format_file_size(file_size),
                    'real_name': None,
                    'install_date': install_date.strftime("%d/%m/%Y %H:%M"),
                    'created_date': created_date.strftime("%d/%m/%Y %H:%M"),
                    'file_name': lua_file.name,
                    'is_valid': True,
                    'name_from_cache': False
                }
                
                games.append(game_data)
                logger.debug(f"🎮 Jogo detectado: {appid} ({format_file_size(file_size)})")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar arquivo {lua_file}: {e}")
                continue
                    
    except Exception as e:
        logger.error(f"❌ Erro crítico na detecção de jogos: {e}")
    
    logger.info(f"✅ Detecção concluída: {len(games)} jogos .lua válidos encontrados")
    return games

def format_file_size(bytes_size: int) -> str:
    """Formata tamanho de arquivo de forma legível"""
    if bytes_size == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    
    while bytes_size >= 1024 and unit_index < len(units) - 1:
        bytes_size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:
        return f"{bytes_size:.0f} {units[unit_index]}"
    elif bytes_size < 10:
        return f"{bytes_size:.1f} {units[unit_index]}"
    else:
        return f"{bytes_size:.0f} {units[unit_index]}"

# ================= CLASSE PRINCIPAL DE GERENCIAMENTO =================

class GameManager:
    """Gerenciador especializado em jogos .lua - Backup/Remoção/Estatísticas"""
    
    def __init__(self, steam_path: str = None):
        self.steam_path = steam_path
        self.detected_games = []
        logger.info(f"🎮 GameManager inicializado com Steam path: {steam_path}")
        
    def detect_games(self, fetch_names: bool = True) -> Dict[str, Any]:
        """Detecta jogos .lua e retorna resultado - VERSÃO ESPECIALIZADA"""
        try:
            logger.info("🔍 Iniciando detecção de jogos .lua...")
            start_time = time.time()
            
            # Fase 1: Detecção de arquivos .lua
            games = detect_lua_games(self.steam_path)
            if not games:
                logger.warning("⚠️ Nenhum jogo .lua detectado")
                return {
                    'success': True,
                    'games': [],
                    'total_games': 0,
                    'total_size': 0,
                    'message': 'Nenhum jogo .lua detectado'
                }
            
            # Fase 2: Buscar nomes se solicitado
            if fetch_names:
                name_cache = load_game_names_cache()
                logger.info(f"📝 Buscando nomes para {len(games)} jogos...")
                
                games_with_names = 0
                for i, game in enumerate(games):
                    try:
                        real_name, from_cache = get_game_name_from_steam(game['appid'], name_cache)
                        game['name'] = real_name
                        game['real_name'] = real_name
                        game['name_from_cache'] = from_cache
                        
                        if from_cache:
                            games_with_names += 1
                            
                        # Progresso a cada 10 jogos
                        if (i + 1) % 10 == 0:
                            logger.info(f"📊 Progresso: {i + 1}/{len(games)} jogos processados")
                            
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar jogo {game['appid']}: {e}")
                        continue
                
                # Salvar cache atualizado
                save_game_names_cache(name_cache)
                logger.info(f"📊 Estatísticas: {games_with_names} nomes do cache")
            else:
                # Manter nomes padrão se não buscar
                for game in games:
                    game['name'] = f"AppID {game['appid']}"
                    game['real_name'] = None
                    game['name_from_cache'] = False
            
            self.detected_games = games
            
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Detecção concluída: {len(games)} jogos .lua em {elapsed_time:.2f}s")
            
            return {
                'success': True,
                'games': games,
                'total_games': len(games),
                'total_size': sum(g['size'] for g in games),
                'processing_time': f"{elapsed_time:.2f}s",
                'message': f'Detectados {len(games)} jogos .lua'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na detecção: {e}")
            return {
                'success': False,
                'error': str(e),
                'games': [],
                'total_games': 0,
                'total_size': 0,
                'message': f'Erro na detecção: {str(e)}'
            }
    
    def backup_games(self, games: List[Dict], backup_dir: str = None) -> Dict[str, Any]:
        """Faz backup dos jogos selecionados - VERSÃO ROBUSTA"""
        try:
            if not games:
                return {
                    'success': False,
                    'error': 'Nenhum jogo fornecido para backup',
                    'message': 'Nenhum jogo selecionado'
                }
            
            # Criar diretório de backup
            if backup_dir is None:
                backup_dir = Path.home() / "SteamGameLoader_Backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            else:
                backup_dir = Path(backup_dir) / datetime.now().strftime("%Y%m%d_%H%M%S")
                
            backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"💾 Criando backup em: {backup_dir}")
            
            success_count = 0
            failed_games = []
            total = len(games)
            
            for i, game in enumerate(games):
                game_name = game.get('name', f"AppID {game['appid']}")
                logger.info(f"📦 Backup [{i+1}/{total}]: {game_name}")
                
                try:
                    game_backup_dir = backup_dir / game['appid']
                    game_backup_dir.mkdir(exist_ok=True)
                    
                    file_path = Path(game['file_path'])
                    if file_path.exists():
                        # Copiar arquivo .lua
                        shutil.copy2(file_path, game_backup_dir / file_path.name)
                        
                        # Criar metadata detalhada
                        metadata = {
                            'appid': game['appid'],
                            'name': game['name'],
                            'real_name': game.get('real_name'),
                            'backup_date': datetime.now().isoformat(),
                            'original_path': game['file_path'],
                            'size': game['size'],
                            'size_formatted': game.get('size_formatted'),
                            'install_date': game.get('install_date'),
                            'backup_version': '2.0',
                            'game_manager': 'SteamGameLoader Lua Manager'
                        }
                        
                        with open(game_backup_dir / "metadata.json", 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                        
                        success_count += 1
                        logger.debug(f"✅ Backup concluído: {game_name}")
                    else:
                        logger.warning(f"⚠️ Arquivo não encontrado: {file_path}")
                        failed_games.append({'appid': game['appid'], 'error': 'Arquivo não encontrado'})
                        
                except Exception as e:
                    logger.error(f"❌ Erro no backup {game['appid']}: {e}")
                    failed_games.append({'appid': game['appid'], 'error': str(e)})
            
            # Criar arquivo de relatório do backup
            report = {
                'backup_date': datetime.now().isoformat(),
                'total_games': total,
                'success_count': success_count,
                'failed_count': len(failed_games),
                'failed_games': failed_games,
                'backup_path': str(backup_dir),
                'total_size': sum(g['size'] for g in games)
            }
            
            with open(backup_dir / "backup_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup finalizado: {success_count}/{total} jogos")
            
            return {
                'success': True,
                'message': f"Backup concluído: {success_count}/{total} jogos",
                'backup_path': str(backup_dir),
                'success_count': success_count,
                'total_count': total,
                'failed_count': len(failed_games),
                'failed_games': failed_games,
                'report_file': str(backup_dir / "backup_report.json")
            }
            
        except Exception as e:
            logger.error(f"❌ Erro crítico no backup: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro no backup: {str(e)}"
            }
    
    def remove_games(self, games: List[Dict]) -> Dict[str, Any]:
        """Remove os jogos selecionados - VERSÃO SEGURA"""
        try:
            if not games:
                return {
                    'success': False,
                    'error': 'Nenhum jogo fornecido para remoção',
                    'message': 'Nenhum jogo selecionado'
                }
            
            removed_count = 0
            failed_games = []
            total = len(games)
            
            backup_dir = Path.home() / "SteamGameLoader_Removal_Backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🗑️ Iniciando remoção de {total} jogos...")
            
            for i, game in enumerate(games):
                game_name = game.get('name', f"AppID {game['appid']}")
                logger.info(f"🗑️ Removendo [{i+1}/{total}]: {game_name}")
                
                try:
                    file_path = Path(game['file_path'])
                    if file_path.exists():
                        # Criar backup de segurança antes de remover
                        backup_path = backup_dir / f"{game['appid']}_{file_path.name}.backup"
                        try:
                            shutil.copy2(file_path, backup_path)
                            logger.debug(f"💾 Backup de segurança criado: {backup_path}")
                        except Exception as backup_error:
                            logger.warning(f"⚠️ Não foi possível criar backup: {backup_error}")
                        
                        # Remover arquivo
                        file_path.unlink()
                        
                        # Verificar se foi removido
                        if not file_path.exists():
                            removed_count += 1
                            logger.debug(f"✅ Remoção concluída: {game_name}")
                        else:
                            raise Exception("Arquivo ainda existe após remoção")
                    else:
                        logger.warning(f"⚠️ Arquivo já não existe: {file_path}")
                        removed_count += 1  # Considerar sucesso se já não existir
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao remover {game['appid']}: {e}")
                    failed_games.append({'appid': game['appid'], 'error': str(e)})
            
            logger.info(f"✅ Remoção finalizada: {removed_count}/{total} jogos")
            
            return {
                'success': True,
                'message': f"Remoção concluída: {removed_count}/{total} jogos",
                'removed_count': removed_count,
                'total_count': total,
                'failed_count': len(failed_games),
                'failed_games': failed_games,
                'backup_dir': str(backup_dir)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na remoção: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Erro na remoção: {str(e)}"
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas dos jogos detectados"""
        total_games = len(self.detected_games)
        
        if total_games == 0:
            return {
                'total_games': 0,
                'total_size_bytes': 0,
                'total_size_formatted': '0 B',
                'from_cache_count': 0,
                'from_api_count': 0,
                'size_breakdown': {},
                'message': 'Nenhum jogo detectado'
            }
        
        total_size_bytes = sum(game['size'] for game in self.detected_games)
        from_cache_count = sum(1 for game in self.detected_games if game.get('name_from_cache'))
        from_api_count = total_games - from_cache_count
        
        # Análise de tamanhos
        size_breakdown = {
            'small': sum(1 for g in self.detected_games if g['size'] < 1024),  # < 1KB
            'medium': sum(1 for g in self.detected_games if 1024 <= g['size'] < 10240),  # 1KB - 10KB
            'large': sum(1 for g in self.detected_games if g['size'] >= 10240)  # >= 10KB
        }
        
        return {
            'total_games': total_games,
            'total_size_bytes': total_size_bytes,
            'total_size_formatted': format_file_size(total_size_bytes),
            'from_cache_count': from_cache_count,
            'from_api_count': from_api_count,
            'size_breakdown': size_breakdown,
            'average_size': format_file_size(total_size_bytes / total_games) if total_games > 0 else '0 B',
            'message': f'{total_games} jogos .lua, {format_file_size(total_size_bytes)} total'
        }
    
    def get_game_by_appid(self, appid: str) -> Optional[Dict]:
        """Retorna jogo específico pelo AppID"""
        for game in self.detected_games:
            if game['appid'] == appid:
                return game
        return None
    
    def refresh_game_data(self, appid: str) -> Optional[Dict]:
        """Atualiza dados de um jogo específico"""
        try:
            game = self.get_game_by_appid(appid)
            if not game:
                return None
            
            # Atualizar nome
            name_cache = load_game_names_cache()
            real_name, from_cache = get_game_name_from_steam(appid, name_cache)
            game['name'] = real_name
            game['real_name'] = real_name
            game['name_from_cache'] = from_cache
            save_game_names_cache(name_cache)
            
            return game
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar jogo {appid}: {e}")
            return None

    def get_detected_games(self) -> List[Dict]:
        """Retorna cópia da lista de jogos detectados"""
        return self.detected_games.copy()
    
    def clear_detected_games(self):
        """Limpa lista de jogos detectados"""
        self.detected_games = []
        logger.info("🧹 Lista de jogos detectados limpa")
    
    def validate_game_file(self, appid: str) -> Dict[str, Any]:
        """Valida se o arquivo do jogo ainda existe e é acessível"""
        game = self.get_game_by_appid(appid)
        if not game:
            return {
                'valid': False,
                'error': 'Jogo não encontrado',
                'appid': appid
            }
        
        try:
            file_path = Path(game['file_path'])
            if not file_path.exists():
                return {
                    'valid': False,
                    'error': 'Arquivo não existe',
                    'appid': appid,
                    'file_path': str(file_path)
                }
            
            # Verificar permissões
            file_stats = file_path.stat()
            current_size = file_stats.st_size
            
            return {
                'valid': True,
                'appid': appid,
                'file_path': str(file_path),
                'size': current_size,
                'size_matches': current_size == game['size'],
                'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'appid': appid,
                'file_path': game['file_path']
            }

# ================= FUNÇÃO DE INICIALIZAÇÃO =================

def create_game_manager(steam_path: str = None) -> GameManager:
    """Função factory para criar gerenciador de jogos"""
    return GameManager(steam_path=steam_path)

def get_game_manager(steam_path: str = None) -> GameManager:
    """Obtém instância do gerenciador (alias para create_game_manager)"""
    return create_game_manager(steam_path)

# ================= FUNÇÃO DE INTEGRAÇÃO SIMPLIFICADA =================

def setup_game_management_routes(app, steam_path: str = None):
    """
    Configura integração do gerenciador de jogos - VERSÃO CORRIGIDA
    APENAS inicializa o manager, NÃO configura rotas (já existem no routes.py)
    """
    try:
        game_manager = create_game_manager(steam_path)
        logger.info("🎮 Gerenciador de jogos .lua inicializado para uso pelas rotas principais")
        
        # ✅ APENAS retorne o manager - as rotas já estão definidas no routes.py
        return game_manager
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar gerenciador de jogos: {e}")
        return None

# ================= FUNÇÕES UTILITÁRIAS ADICIONAIS =================

def get_game_manager_version() -> str:
    """Retorna versão do sistema de gerenciamento"""
    return "2.0.0_corrigido_definitivo"

def get_supported_features() -> List[str]:
    """Retorna lista de funcionalidades suportadas"""
    return [
        "detect_lua_games",
        "backup_games", 
        "remove_games",
        "game_statistics",
        "steam_api_integration",
        "cache_management"
    ]

def validate_steam_path_for_games(steam_path: str) -> Dict[str, Any]:
    """Valida se o caminho do Steam é adequado para detecção de jogos .lua"""
    try:
        path = Path(steam_path)
        
        if not path.exists():
            return {
                'valid': False,
                'error': 'Caminho não existe',
                'steam_path': steam_path
            }
        
        stplugin_path = path / "config" / "stplug-in"
        has_stplugin = stplugin_path.exists()
        
        lua_files = []
        if has_stplugin:
            lua_files = list(stplugin_path.glob("*.lua"))
        
        return {
            'valid': True,
            'steam_path': steam_path,
            'has_stplugin_dir': has_stplugin,
            'lua_files_count': len(lua_files),
            'stplugin_path': str(stplugin_path),
            'readable': os.access(stplugin_path, os.R_OK) if has_stplugin else False
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'steam_path': steam_path
        }

# Exemplo de uso direto
if __name__ == "__main__":
    print("🎮 Teste do Sistema de Gerenciamento de Jogos .LUA")
    print(f"🔧 Versão: {get_game_manager_version()}")
    print(f"📋 Funcionalidades: {', '.join(get_supported_features())}")
    
    steam_path = "C:/Program Files (x86)/Steam"
    manager = create_game_manager(steam_path)
    
    # Validar caminho do Steam
    validation = validate_steam_path_for_games(steam_path)
    print(f"🔍 Validação do Steam path: {validation}")
    
    if validation['valid']:
        # Detectar jogos
        print("🔍 Detectando jogos .lua...")
        result = manager.detect_games(fetch_names=True)
        
        if result['success']:
            print(f"✅ {result['total_games']} jogos .lua detectados")
            print(f"💾 Tamanho total: {format_file_size(result['total_size'])}")
            print(f"⏱️  Tempo de processamento: {result['processing_time']}")
            
            # Estatísticas
            stats = manager.get_statistics()
            print(f"📊 Estatísticas: {stats['message']}")
            print(f"   - Cache: {stats['from_cache_count']} jogos")
            print(f"   - API: {stats['from_api_count']} jogos")
            print(f"   - Tamanhos: Pequenos({stats['size_breakdown']['small']}), Médios({stats['size_breakdown']['medium']}), Grandes({stats['size_breakdown']['large']})")
            
            # Listar alguns jogos
            if manager.detected_games:
                print("\n📋 Primeiros 3 jogos detectados:")
                for game in manager.detected_games[:3]:
                    source = "💫 Cache" if game['name_from_cache'] else "🌐 API"
                    print(f"  🎮 {game['name']} (AppID: {game['appid']}) - {game['size_formatted']} - {source}")
        else:
            print(f"❌ Erro na detecção: {result.get('error', 'Erro desconhecido')}")
    else:
        print(f"❌ Caminho do Steam inválido: {validation.get('error', 'Erro desconhecido')}")
    
    print("\n✅ Teste concluído!")