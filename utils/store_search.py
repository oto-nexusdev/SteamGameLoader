import requests
import logging
import time
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# -------------------- CONFIGURAÇÕES GLOBAIS --------------------
STEAM_API_BASE = "https://store.steampowered.com/api"
STEAM_SEARCH_URL = f"{STEAM_API_BASE}/storesearch"
STEAM_APP_DETAILS_URL = f"{STEAM_API_BASE}/appdetails"

# -------------------- IMPORTAÇÕES DO DOWNLOAD MANAGER --------------------
try:
    from .download_manager import baixar_manifesto, _verificar_disponibilidade_appid
    DOWNLOAD_MANAGER_AVAILABLE = True
    logger.info("✅ Download Manager importado com sucesso")
except ImportError as e:
    DOWNLOAD_MANAGER_AVAILABLE = False
    logger.warning(f"⚠️ Download Manager não disponível: {e}")
    
    # Fallback functions para manter compatibilidade
    def baixar_manifesto(appid: str) -> Dict[str, Any]:
        return {
            "success": False, 
            "error": "Sistema de download não disponível",
            "appid": appid
        }
    
    def _verificar_disponibilidade_appid(appid: str) -> List[Dict]:
        return []

# Timeouts / retries (APENAS PARA BUSCA)
API_TIMEOUT = 12
MAX_RETRIES = 3
REQUEST_DELAY = 0.5

# -------------------- CACHE MANAGER (MANTIDO PARA BUSCA) --------------------
class CacheManager:
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "cache"
        self.search_cache_file = self.cache_dir / "search_cache.json"
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cached_search(self, query: str) -> Optional[List[Dict]]:
        try:
            if not self.search_cache_file.exists():
                return None
            with open(self.search_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            key = query.lower().strip()
            data = cache.get(key)
            if not data:
                return None
            # validade 1 hora
            if time.time() - data.get('timestamp', 0) < 3600:
                return data.get('results', [])
        except Exception as e:
            logger.debug(f"Erro ao ler cache de busca: {e}")
        return None

    def save_search_cache(self, query: str, results: List[Dict]):
        try:
            cache = {}
            if self.search_cache_file.exists():
                with open(self.search_cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            key = query.lower().strip()
            cache[key] = {'results': results, 'timestamp': time.time(), 'count': len(results)}
            with open(self.search_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Erro ao salvar cache de busca: {e}")

# -------------------- UTILITÁRIOS (MANTIDOS) --------------------
def safe_int(val: Any, default: int = 0) -> int:
    try:
        if val is None:
            return default
        return int(val)
    except Exception:
        return default

def formatar_preco(preco_info: Dict) -> str:
    try:
        if not preco_info or not isinstance(preco_info, dict):
            return "🎁 Gratuito"
        final = int(preco_info.get("final", 0))
        if final == 0:
            return "🎁 Gratuito"
        valor = final / 100.0
        return f"💰 R$ {valor:.2f}".replace('.', ',')
    except Exception:
        return "💰 Consultar"

def formatar_plataformas(plataformas: Dict) -> str:
    try:
        if not plataformas:
            return "❓ Não especificado"
        icons = []
        if plataformas.get('windows'):
            icons.append("Windows")
        if plataformas.get('mac'):
            icons.append("macOS")
        if plataformas.get('linux'):
            icons.append("Linux")
        return " • ".join(icons) if icons else "❓ Não especificado"
    except Exception:
        return "❓ Não especificado"

# -------------------- VERIFICAÇÃO SILENCIOSA DE DIRETÓRIOS STEAM --------------------
def _verificar_e_criar_diretorios_steam() -> bool:
    """✅ VERIFICA E CRIA DIRETÓRIOS DO STEAM SILENCIOSAMENTE"""
    try:
        # Tentar importar steam_utils silenciosamente
        steam_path = None
        try:
            from utils.steam_utils import get_steam_path_with_fallback
            steam_path = get_steam_path_with_fallback()
        except ImportError:
            # Falha silenciosa - não logar como erro
            pass
        
        # Se não encontrou via steam_utils, tentar caminhos comuns
        if not steam_path:
            possible_paths = [
                os.path.expandvars(r"%ProgramFiles%\Steam"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                r"C:\Program Files\Steam",
                r"C:\Program Files (x86)\Steam",
                os.path.expanduser(r"~/.steam/steam")
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    steam_exe = os.path.join(path, "steam.exe")
                    steamapps_dir = os.path.join(path, "steamapps")
                    if os.path.exists(steam_exe) or os.path.exists(steamapps_dir):
                        steam_path = path
                        break
        
        # Se ainda não encontrou, retornar False silenciosamente
        if not steam_path:
            return False
        
        # Criar diretórios críticos silenciosamente
        diretorios_criticos = [
            os.path.join(steam_path, 'depotcache'),
            os.path.join(steam_path, 'config', 'stplug-in')
        ]
        
        for diretorio in diretorios_criticos:
            try:
                os.makedirs(diretorio, exist_ok=True)
                # Teste silencioso de permissões
                test_file = os.path.join(diretorio, "write_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except (IOError, OSError, Exception):
                # Falha silenciosa
                return False
        
        return True
        
    except Exception:
        # Falha completamente silenciosa
        return False

# -------------------- VALIDAÇÃO DO STEAM NO INÍCIO DO PROGRAMA --------------------
def _validar_steam_inicio() -> Tuple[bool, Optional[str]]:
    """✅ VALIDAÇÃO SILENCIOSA DO STEAM AO INICIAR O PROGRAMA"""
    try:
        steam_path = None
        
        # Método 1: Tentar steam_utils primeiro
        try:
            from utils.steam_utils import get_steam_path_with_fallback
            steam_path = get_steam_path_with_fallback()
        except ImportError:
            pass
        
        # Método 2: Caminhos comuns do Steam
        if not steam_path:
            possible_paths = [
                os.path.expandvars(r"%ProgramFiles%\Steam"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                r"C:\Program Files\Steam", 
                r"C:\Program Files (x86)\Steam",
                os.path.expanduser(r"~/.steam/steam")
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    steam_exe = os.path.join(path, "steam.exe")
                    steamapps_dir = os.path.join(path, "steamapps")
                    if os.path.exists(steam_exe) or os.path.exists(steamapps_dir):
                        steam_path = path
                        break
        
        if not steam_path:
            return False, "Steam não encontrado no sistema"
        
        # Verificar se diretórios críticos existem ou podem ser criados
        diretorios_criticos = [
            os.path.join(steam_path, 'depotcache'),
            os.path.join(steam_path, 'config', 'stplug-in')
        ]
        
        for diretorio in diretorios_criticos:
            try:
                os.makedirs(diretorio, exist_ok=True)
                # Testar escrita
                test_file = os.path.join(diretorio, "write_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except (IOError, OSError, Exception) as e:
                return False, f"Sem permissão em {diretorio}"
        
        return True, steam_path
        
    except Exception as e:
        return False, f"Erro na validação: {str(e)}"

# -------------------- VALIDAÇÃO FINAL DA INSTALAÇÃO --------------------
def _validar_instalacao_final(appid: str) -> Dict[str, Any]:
    """✅ VALIDAÇÃO FINAL DA INSTALAÇÃO"""
    try:
        try:
            from utils.steam_utils import get_steam_path_with_fallback
            steam_path = get_steam_path_with_fallback()
        except ImportError:
            steam_path = None
            
        if not steam_path:
            possible_paths = [
                os.path.expandvars(r"%ProgramFiles%\Steam"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                r"C:\Program Files\Steam",
                r"C:\Program Files (x86)\Steam"
            ]
            for path in possible_paths:
                if path and os.path.exists(path):
                    steam_path = path
                    break
        
        if not steam_path:
            return {"success": False, "error": "Steam não encontrado"}
        
        resultados = {
            "success": False,
            "steam_path": steam_path,
            "depotcache_files": [],
            "stplugin_files": [],
            "total_arquivos": 0,
            "appid_encontrado": False,
            "depotcache_path": "",
            "stplugin_path": ""
        }
        
        depotcache_path = os.path.join(steam_path, 'depotcache')
        resultados["depotcache_path"] = depotcache_path
        
        if os.path.exists(depotcache_path):
            for file in os.listdir(depotcache_path):
                if file.endswith('.manifest') and str(appid) in file:
                    resultados["depotcache_files"].append(file)
                    resultados["total_arquivos"] += 1
                    resultados["appid_encontrado"] = True
                    logger.info(f"✅ Arquivo .manifest encontrado: {file}")
        
        stplugin_path = os.path.join(steam_path, 'config', 'stplug-in')
        resultados["stplugin_path"] = stplugin_path
        
        if os.path.exists(stplugin_path):
            for file in os.listdir(stplugin_path):
                if file.endswith('.lua') and str(appid) in file:
                    resultados["stplugin_files"].append(file)
                    resultados["total_arquivos"] += 1
                    resultados["appid_encontrado"] = True
                    logger.info(f"✅ Arquivo .lua encontrado: {file}")
        
        resultados["success"] = resultados["appid_encontrado"]
        
        logger.info(f"📊 Validação final: {resultados['total_arquivos']} arquivos encontrados para AppID {appid}")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Erro na validação final: {e}")
        return {"success": False, "error": str(e)}

# -------------------- CLIENTE STEAM (MANTIDO PARA BUSCA) --------------------
class SteamAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; SteamGameLoader/1.0)",
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        })
        self.last_request_time = 0
        self.cache_manager = CacheManager()

    def _rate_limit(self):
        now = time.time()
        diff = now - self.last_request_time
        if diff < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - diff)
        self.last_request_time = time.time()

    def make_request(self, url: str, params: Dict = None, timeout: int = API_TIMEOUT) -> Optional[Dict]:
        self._rate_limit()
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Request {url} params={params} attempt={attempt+1}")
                resp = self.session.get(url, params=params, timeout=timeout)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    text = resp.text
                    try:
                        data = json.loads(text)
                    except Exception:
                        raise ValueError("Resposta não é JSON válido")
                return data
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout {attempt+1} for {url}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(1 + attempt)
            except requests.exceptions.HTTPError as e:
                code = getattr(e.response, "status_code", None)
                logger.warning(f"HTTPError {code} {url}")
                if code == 429:
                    time.sleep(2 ** attempt)
                    continue
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(1)
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"ConnectionError attempt {attempt+1} for {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(1)
            except Exception as e:
                logger.debug(f"Erro na request: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(0.5)
        return None

# -------------------- PROCESSAMENTO DOS DADOS (MANTIDO) --------------------
def _processar_dados_jogo(jogo: Dict) -> Optional[Dict]:
    try:
        if not jogo or 'id' not in jogo:
            return None
        appid = safe_int(jogo.get('id'))
        name = (jogo.get('name') or "").strip()
        if not appid or not name:
            return None
        price_info = jogo.get('price') or {}
        preco_final = safe_int(price_info.get('final', 0))
        preco_original = safe_int(price_info.get('original', preco_final))
        desconto = safe_int(price_info.get('discount_percent', 0))
        platforms = jogo.get('platforms') or {}
        release = jogo.get('release_date') or {}
        metacritic = jogo.get('metacritic') or {}
        score = safe_int(metacritic.get('score', 0))
        tiny = jogo.get('tiny_image') or ""
        small_capsule = jogo.get('small_capsule_image') or tiny

        return {
            'id': str(appid),
            'appid': str(appid),
            'name': name,
            'price': {
                'final': preco_final,
                'original': preco_original,
                'discount_percent': desconto,
                'formatted': formatar_preco(price_info),
                'currency': 'BRL'
            },
            'platforms': platforms,
            'platforms_formatted': formatar_plataformas(platforms),
            'release_date': {
                'date': release.get('date', 'Não informada'),
                'coming_soon': bool(release.get('coming_soon', False))
            },
            'metacritic_score': score,
            'short_description': jogo.get('short_description') or "",
            'header_image': small_capsule,
            'tiny_image': tiny,
            'type': jogo.get('type', 'game'),
            'is_free': preco_final == 0,
            'search_timestamp': datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.debug(f"Erro processando jogo: {e}")
        return None

# -------------------- FUNÇÃO PRINCIPAL DE BUSCA (MANTIDA) --------------------
def buscar_jogos_steam(nome_jogo: str, max_results: int = 50) -> List[Dict]:
    """
    Busca única e definitiva. Retorna lista de dicionários padronizados.
    Usa cache (1h) e faz request à Steam Store API /storesearch.
    """
    client = SteamAPIClient()
    cache = client.cache_manager

    if not nome_jogo or len(nome_jogo.strip()) < 2:
        logger.warning("Query muito curta para buscar_jogos_steam")
        return []

    query = nome_jogo.strip()
    try:
        cached = cache.get_cached_search(query)
        if cached is not None:
            logger.info(f"Usando cache para '{query}' ({len(cached)} resultados)")
            return cached
    except Exception:
        logger.debug("Falha ao verificar cache")

    params = {
        "term": query,
        "l": "brazilian",
        "cc": "BR",
        "max_results": max_results
    }

    try:
        data = client.make_request(STEAM_SEARCH_URL, params=params, timeout=API_TIMEOUT)
        if not data:
            logger.warning("Resposta vazia da API Steam")
            return []
        items = data.get('items') if isinstance(data, dict) else None
        if not items:
            items = data.get('results') if isinstance(data, dict) else None
        if not items:
            logger.info("Nenhum item retornado pela Steam")
            return []

        jogos = []
        for item in items[:max_results]:
            p = _processar_dados_jogo(item)
            if p:
                jogos.append(p)

        try:
            cache.save_search_cache(query, jogos)
        except Exception:
            logger.debug("Falha ao salvar cache, ignorando")

        logger.info(f"buscar_jogos_steam: {len(jogos)} resultados para '{query}'")
        return jogos

    except Exception as e:
        logger.error(f"Erro em buscar_jogos_steam: {e}")
        try:
            stale = cache.get_cached_search(query)
            if stale:
                logger.info(f"Usando cache expirado como fallback para '{query}' ({len(stale)} itens)")
                return stale
        except Exception:
            pass
        return []

# -------------------- DETALHES DO JOGO (MANTIDO) --------------------
def obter_detalhes_jogo(appid: str) -> Optional[Dict]:
    client = SteamAPIClient()
    try:
        params = {"appids": str(appid), "l": "brazilian", "cc": "BR"}
        data = client.make_request(STEAM_APP_DETAILS_URL, params=params, timeout=API_TIMEOUT)
        if not data:
            return None
        entry = data.get(str(appid))
        if not entry or not entry.get('success'):
            return None
        d = entry.get('data', {})
        categories = [c.get('description') for c in d.get('categories', []) if c.get('description')]
        genres = [g.get('description') for g in d.get('genres', []) if g.get('description')]
        screenshots = [s.get('path_full') for s in d.get('screenshots', []) if s.get('path_full')]
        movies = [m.get('webm', {}).get('max') for m in d.get('movies', []) if m.get('webm', {}).get('max')]

        return {
            'detailed_description': d.get('detailed_description', ''),
            'about_the_game': d.get('about_the_game', ''),
            'short_description': d.get('short_description', ''),
            'supported_languages': d.get('supported_languages', ''),
            'categories': categories,
            'genres': genres,
            'recommendations': d.get('recommendations', {}).get('total', 0),
            'achievements': d.get('achievements', {}).get('total', 0),
            'release_date': d.get('release_date', {}),
            'developers': d.get('developers', []),
            'publishers': d.get('publishers', []),
            'metacritic': d.get('metacritic', {}),
            'website': d.get('website', ''),
            'header_image': d.get('header_image', ''),
            'background': d.get('background', ''),
            'pc_requirements': d.get('pc_requirements', {}),
            'mac_requirements': d.get('mac_requirements', {}),
            'linux_requirements': d.get('linux_requirements', {}),
            'screenshots': screenshots,
            'movies': movies
        }
    except Exception as e:
        logger.debug(f"Erro obter_detalhes_jogo({appid}): {e}")
        return None

# -------------------- INICIALIZAÇÃO SILENCIOSA DO PROGRAMA --------------------
def inicializar_programa_silenciosamente():
    """✅ INICIALIZA O PROGRAMA VALIDANDO STEAM SILENCIOSAMENTE"""
    steam_ok, steam_path = _validar_steam_inicio()
    
    if steam_ok:
        logger.info(f"✅ Steam validado silenciosamente: {steam_path}")
    else:
        logger.warning(f"⚠️ Steam não configurado idealmente: {steam_path}")
    
    return steam_ok, steam_path

# Chamar a inicialização silenciosa quando o módulo for carregado
_STEAM_STATUS_INICIAL = inicializar_programa_silenciosamente()

# -------------------- STATUS / UTILIDADES ATUALIZADAS --------------------
def verificar_conectividade() -> bool:
    try:
        client = SteamAPIClient()
        params = {"term": "test", "l": "brazilian", "cc": "BR", "max_results": 1}
        data = client.make_request(STEAM_SEARCH_URL, params=params, timeout=10)
        return bool(data and (data.get('items') or data.get('results')))
    except Exception:
        return False

def get_system_status() -> Dict[str, Any]:
    try:
        steam_online = verificar_conectividade()
        
        # Usar a validação silenciosa já feita no início
        steam_ok, steam_path = _STEAM_STATUS_INICIAL
        
        github_accessible = False
        try:
            r = requests.head("https://github.com", timeout=5)
            github_accessible = r.status_code == 200
        except Exception:
            github_accessible = False
            
        # Verificar status usando download_manager se disponível
        apis_status = {}
        if DOWNLOAD_MANAGER_AVAILABLE:
            try:
                from .download_manager import criar_gerenciador_download
                download_manager = criar_gerenciador_download()
                download_status = download_manager.get_system_status()
                apis_status = download_status.get('external_apis_status', {})
                git_available = download_status.get('git_available', False)
            except Exception as e:
                logger.debug(f"Erro obtendo status do download manager: {e}")
                git_available = False
        else:
            git_available = False
        
        return {
            "steam_api_online": steam_online,
            "steam_installed": steam_ok,
            "steam_path": steam_path if steam_ok else None,
            "github_access": github_accessible,
            "git_available": git_available,
            "steam_directories_ok": steam_ok,
            "external_apis_status": apis_status,
            "cache_enabled": True,
            "version": "24.1_otimizado_modular",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "status": "operacional" if steam_online and steam_ok else "parcial",
            "initialized_silently": True,
            "download_manager_available": DOWNLOAD_MANAGER_AVAILABLE,
            "search_system_available": True
        }
    except Exception as e:
        logger.debug(f"Erro get_system_status: {e}")
        return {"status": "erro", "error": str(e)}

# -------------------- EXECUTABLE TEST --------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    print("🧪 TESTE DO STORE_SEARCH.PY - VERSÃO OTIMIZADA E MODULAR")
    print("=" * 60)
    
    st = get_system_status()
    print("📊 Status do Sistema:")
    for key, value in st.items():
        if key != "external_apis_status":
            print(f"  • {key}: {value}")
    
    print("\n🔍 Status das APIs:")
    for api_name, status in st.get("external_apis_status", {}).items():
        print(f"  • {api_name}: {status}")
    
    try:
        jogos = buscar_jogos_steam("counter strike", 3)
        print(f"\n🎮 Encontrados: {len(jogos)} jogos")
        
        if jogos:
            j = jogos[0]
            print(f"📝 Exemplo: {j.get('name')} (AppID: {j.get('appid')}) - {j.get('price', {}).get('formatted')}")
            
            # Teste de verificação de disponibilidade
            appid_teste = j.get('appid')
            print(f"\n--- VERIFICAÇÃO DE DISPONIBILIDADE PARA {appid_teste} ---")
            apis_disponiveis = _verificar_disponibilidade_appid(appid_teste)
            print(f"✅ APIs disponíveis: {[api['name'] for api in apis_disponiveis]}")
            
            # Teste de download (se disponível)
            if DOWNLOAD_MANAGER_AVAILABLE:
                print(f"\n--- TESTE DE DOWNLOAD (SIMULAÇÃO) ---")
                print("📥 Sistema de download disponível via Download Manager")
            else:
                print(f"\n--- SISTEMA DE DOWNLOAD ---")
                print("❌ Download Manager não disponível")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()