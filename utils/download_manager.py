# utils/download_manager.py - SISTEMA DE DOWNLOAD UNIFICADO - VERIFICAÇÃO ÚNICA
import requests
import logging
import time
import tempfile
import shutil
import subprocess
import os
import sys
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ✅ CORREÇÃO: Controle global de inicialização
_DOWNLOAD_MANAGER_INSTANCE = None
_DOWNLOAD_MANAGER_INITIALIZED = False
_SYSTEM_STATUS_CACHE = None

# -------------------- CONFIGURAÇÕES GLOBAIS (HERDADAS DO STORE_SEARCH) --------------------
PRIMARY_BASE = "https://pub-5b6d3b7c03fd4ac1afb5bd3017850e20.r2.dev"
GITHUB_CODELOAD_TEMPLATE = "https://codeload.github.com/SteamAutoCracks/ManifestHub/zip/refs/heads/"

# REPOSITÓRIOS UNIFICADOS (MESMA LISTA DO STORE_SEARCH)
REPOSITORIOS = [
    "https://github.com/SteamAutoCracks/ManifestHub",
    "https://github.com/OpenSteamLoader/GameFiles",
    "https://github.com/blumenal/luafastdb",
    "https://github.com/SPIN0ZAi/SB_manifest_DB"
]

# APIS EXTERNAS CONSOLIDADAS (MESMA LISTA DO STORE_SEARCH)
EXTERNAL_APIS = [
    {
        "name": "Sadie",
        "url": "http://167.235.229.108/m/<appid>",
        "success_code": 200,
        "unavailable_code": 404,
        "enabled": True,
        "type": "direct"
    },
    {
        "name": "Ryuu", 
        "url": "http://167.235.229.108/<appid>",
        "success_code": 200,
        "unavailable_code": 404,
        "enabled": True,
        "type": "direct"
    },
    {
        "name": "TwentyTwo Cloud",
        "url": "http://masss.pythonanywhere.com/storage?auth=IEOIJE54esfsipoE56GE4&appid=<appid>",
        "success_code": 200,
        "unavailable_code": 404,
        "enabled": True,
        "type": "direct"
    },
    {
        "name": "Sushi",
        "url": "https://raw.githubusercontent.com/sushi-dev55/sushitools-games-repo/refs/heads/main/<appid>.zip",
        "success_code": 200,
        "unavailable_code": 404,
        "enabled": True,
        "type": "direct"
    },
    {
        "name": "Servidor Principal",
        "url": f"{PRIMARY_BASE}/<appid>.zip",
        "success_code": 200,
        "unavailable_code": 404,
        "enabled": True,
        "type": "direct"
    },
    {
        "name": "GitHub Codeload",
        "url": f"{GITHUB_CODELOAD_TEMPLATE}<appid>",
        "success_code": 200,
        "unavailable_code": 404,
        "enabled": True,
        "type": "direct"
    }
]

# Timeouts / retries (MESMAS CONFIGURAÇÕES)
DOWNLOAD_TIMEOUT = 25
GIT_TIMEOUT = 45
API_TIMEOUT = 12
MAX_RETRIES = 3
REQUEST_DELAY = 0.5

# -------------------- CACHE MANAGER (COPIADO DO STORE_SEARCH) --------------------
class CacheManager:
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "cache"
        self.download_cache_file = self.cache_dir / "download_cache.json"
        self.api_check_cache_file = self.cache_dir / "api_check_cache.json"
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cached_download(self, appid: str) -> Optional[str]:
        try:
            if not self.download_cache_file.exists():
                return None
            with open(self.download_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            data = cache.get(str(appid))
            if not data:
                return None
            if time.time() - data.get('timestamp', 0) < 86400:
                return data.get('source')
        except Exception as e:
            logger.debug(f"Erro ao ler cache de download: {e}")
        return None

    def save_download_cache(self, appid: str, source: str):
        try:
            cache = {}
            if self.download_cache_file.exists():
                with open(self.download_cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            cache[str(appid)] = {'source': source, 'timestamp': time.time(), 'appid': str(appid)}
            with open(self.download_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Erro ao salvar cache de download: {e}")

    def get_cached_api_check(self, appid: str) -> Optional[Dict]:
        """Cache para verificação de disponibilidade em APIs"""
        try:
            if not self.api_check_cache_file.exists():
                return None
            with open(self.api_check_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            data = cache.get(str(appid))
            if not data:
                return None
            if time.time() - data.get('timestamp', 0) < 1800:
                return data
        except Exception as e:
            logger.debug(f"Erro ao ler cache de API check: {e}")
        return None

    def save_api_check_cache(self, appid: str, available_apis: List[str]):
        """Salva cache de APIs disponíveis para um appid"""
        try:
            cache = {}
            if self.api_check_cache_file.exists():
                with open(self.api_check_cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            cache[str(appid)] = {
                'available_apis': available_apis,
                'timestamp': time.time(),
                'appid': str(appid)
            }
            with open(self.api_check_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Erro ao salvar cache de API check: {e}")

# -------------------- CLIENTE STEAM (HERDADO DO STORE_SEARCH) --------------------
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

# -------------------- DOWNLOAD MANAGER PRINCIPAL --------------------
class DownloadManager:
    """
    🚀 GERENCIADOR DE DOWNLOAD UNIFICADO - VERSÃO COMPLETA E INTEGRADA
    Com inicialização única e sistema de cache
    """
    
    def __init__(self):
        global _DOWNLOAD_MANAGER_INITIALIZED
        
        # ✅ CORREÇÃO: VERIFICAÇÃO ÚNICA - se já foi inicializado, retorna
        if _DOWNLOAD_MANAGER_INITIALIZED:
            return
            
        self.logger = logger
        self.cache_manager = CacheManager()
        self.steam_client = SteamAPIClient()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SteamGameLoader/2.0",
            "Accept": "*/*"
        })
        
        # ✅ MARCA COMO INICIALIZADO UMA ÚNICA VEZ
        _DOWNLOAD_MANAGER_INITIALIZED = True
        
        # ✅ LOG APENAS NA PRIMEIRA INICIALIZAÇÃO
        self.logger.info("🚀 Download Manager INICIALIZADO (VERIFICAÇÃO ÚNICA)")

    # -------------------- MÉTODOS EXCLUSIVOS DO KEY INSTALLER INTEGRADOS --------------------
    def _baixar_arquivos_individuais_github(self, appid: str) -> Tuple[bool, Optional[str]]:
        """
        🎯 MÉTODO 1 EXCLUSIVO DO KEY INSTALLER: DOWNLOAD DIRETO DE ARQUIVOS INDIVIDUAIS
        Baixa arquivos .lua e .manifest individualmente do GitHub
        """
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"steam_individual_{appid}_")
            
            files_baixados = 0
            
            self.logger.info(f"🎯 INICIANDO DOWNLOAD INDIVIDUAL para AppID {appid}")
            
            # 📄 TENTAR BAIXAR ARQUIVOS .lua
            lua_urls = [
                f"https://raw.githubusercontent.com/SteamAutoCracks/ManifestHub/{appid}/{appid}.lua",
                f"https://raw.githubusercontent.com/OpenSteamLoader/GameFiles/main/{appid}.lua",
                f"https://raw.githubusercontent.com/SPIN0ZAi/SB_manifest_DB/{appid}/{appid}.lua",
                f"https://raw.githubusercontent.com/blumenal/luafastdb/main/{appid}.lua"
            ]
            
            for url in lua_urls:
                try:
                    self.logger.info(f"📥 Tentando download .lua: {url}")
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200 and len(response.content) > 100:
                        lua_path = os.path.join(temp_dir, f"{appid}.lua")
                        with open(lua_path, 'wb') as f:
                            f.write(response.content)
                        files_baixados += 1
                        self.logger.info(f"✅ .lua BAIXADO COM SUCESSO: {os.path.basename(url)} - {len(response.content)} bytes")
                        break  # Um .lua é suficiente
                    else:
                        self.logger.debug(f"⚠️ .lua não disponível ou vazio: {url}")
                except Exception as e:
                    self.logger.debug(f"⚠️ Falha no download .lua {url}: {e}")
                    continue
            
            # 📄 TENTAR BAIXAR ARQUIVOS .manifest
            manifest_urls = [
                f"https://raw.githubusercontent.com/SteamAutoCracks/ManifestHub/{appid}/{appid}.manifest",
                f"https://raw.githubusercontent.com/OpenSteamLoader/GameFiles/main/{appid}.manifest",
                f"https://raw.githubusercontent.com/SPIN0ZAi/SB_manifest_DB/{appid}/{appid}.manifest"
            ]
            
            for url in manifest_urls:
                try:
                    self.logger.info(f"📥 Tentando download .manifest: {url}")
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200 and len(response.content) > 100:
                        manifest_path = os.path.join(temp_dir, f"{appid}.manifest")
                        with open(manifest_path, 'wb') as f:
                            f.write(response.content)
                        files_baixados += 1
                        self.logger.info(f"✅ .manifest BAIXADO COM SUCESSO: {os.path.basename(url)} - {len(response.content)} bytes")
                        break  # Um .manifest é suficiente
                    else:
                        self.logger.debug(f"⚠️ .manifest não disponível ou vazio: {url}")
                except Exception as e:
                    self.logger.debug(f"⚠️ Falha no download .manifest {url}: {e}")
                    continue
            
            if files_baixados > 0:
                self.logger.info(f"🎯 DOWNLOAD INDIVIDUAL BEM-SUCEDIDO: {files_baixados} arquivos em {temp_dir}")
                
                # Listar arquivos baixados para debug
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        self.logger.info(f"   📄 {file} - {os.path.getsize(file_path)} bytes")
                
                return True, temp_dir
            else:
                self.logger.warning("❌ NENHUM ARQUIVO INDIVIDUAL ENCONTRADO para download")
                self._limpar_diretorio_temp(temp_dir)
                return False, None
                
        except Exception as e:
            self.logger.error(f"❌ ERRO CRÍTICO NO DOWNLOAD INDIVIDUAL: {e}")
            if temp_dir:
                self._limpar_diretorio_temp(temp_dir)
            return False, None

    def _baixar_via_git_clone_branch_especifica(self, appid: str) -> Tuple[bool, Optional[str]]:
        """
        🎯 MÉTODO 2 EXCLUSIVO DO KEY INSTALLER: CLONE DE BRANCH ESPECÍFICA
        Faz git clone especificamente na branch com nome do AppID
        """
        temp_dir = None
        try:
            # Verificar se git está disponível
            if not self._is_git_available():
                self.logger.warning("⚠️ Git não disponível no sistema")
                return False, None
            
            temp_dir = tempfile.mkdtemp(prefix=f"steam_git_branch_{appid}_")
            
            self.logger.info(f"🔧 INICIANDO CLONE GIT BRANCH ESPECÍFICA: {appid}")
            
            for repo_url in REPOSITORIOS:
                try:
                    self.logger.info(f"📁 Clonando: {repo_url} (branch: {appid})")
                    
                    # Comando git simplificado e robusto
                    success, stdout, stderr = self._executar_comando_git([
                        'git', 'clone',
                        '--depth', '1',
                        '--branch', str(appid),
                        '--single-branch',
                        repo_url, temp_dir
                    ], timeout=GIT_TIMEOUT)
                    
                    if success:
                        # Verificar arquivos baixados
                        lua_files = list(Path(temp_dir).rglob("*.lua"))
                        manifest_files = list(Path(temp_dir).rglob("*.manifest"))
                        
                        total_files = len(lua_files) + len(manifest_files)
                        
                        if total_files > 0:
                            self.logger.info(f"✅ CLONE BRANCH ESPECÍFICA BEM-SUCEDIDO: {total_files} arquivos da branch {appid}")
                            return True, temp_dir
                        else:
                            self.logger.warning(f"⚠️ Clone bem-sucedido mas nenhum arquivo encontrado na branch {appid}")
                    
                    # Limpar para próxima tentativa
                    self.logger.debug(f"❌ Clone falhou para {repo_url}: {stderr}")
                    self._limpar_diretorio_temp(temp_dir)
                    temp_dir = tempfile.mkdtemp(prefix=f"steam_git_branch_{appid}_")
                    
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"⏰ Timeout no clone: {repo_url}")
                    continue
                except Exception as e:
                    self.logger.debug(f"⚠️ Erro no clone {repo_url}: {e}")
                    continue
            
            self.logger.error("❌ TODOS OS CLONES DE BRANCH ESPECÍFICA FALHARAM")
            return False, None
            
        except Exception as e:
            self.logger.error(f"❌ ERRO CRÍTICO NO CLONE DE BRANCH: {e}")
            if temp_dir:
                self._limpar_diretorio_temp(temp_dir)
            return False, None

    def _is_git_available(self) -> bool:
        """Verifica se Git está disponível no sistema"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            self.logger.debug("⚠️ Git não disponível no sistema")
            return False

    def _executar_comando_git(self, args: List[str], timeout: int = 60) -> Tuple[bool, str, str]:
        """Executa comando Git com tratamento robusto de erros"""
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, shell=False)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)

    # -------------------- VERIFICAÇÃO UNIFICADA DE APIS --------------------
    def _verificar_disponibilidade_appid(self, appid: str) -> List[Dict]:
        """
        Verifica em TODAS as APIs se o appid está disponível
        Retorna lista de APIs que têm o conteúdo disponível
        """
        cache = self.cache_manager
        cached = cache.get_cached_api_check(appid)
        if cached:
            self.logger.info(f"✅ Usando cache de verificação para AppID {appid}")
            return [api for api in EXTERNAL_APIS if api["name"] in cached.get('available_apis', [])]
        
        apis_disponiveis = []
        
        for api_config in EXTERNAL_APIS:
            if not api_config.get("enabled", True):
                continue
                
            api_name = api_config["name"]
            url_template = api_config["url"]
            success_code = api_config["success_code"]
            
            try:
                download_url = url_template.replace("<appid>", str(appid))
                
                # Verificação HEAD rápida
                try:
                    head_response = self.session.head(download_url, timeout=8, allow_redirects=True)
                    if head_response.status_code == success_code:
                        content_type = head_response.headers.get('Content-Type', '')
                        content_length = head_response.headers.get('Content-Length')
                        
                        # Verificar se é um arquivo válido (não página de erro)
                        if content_length and int(content_length) > 100:
                            apis_disponiveis.append(api_config)
                            self.logger.info(f"✅ API {api_name} tem conteúdo para AppID {appid}")
                            continue
                        else:
                            self.logger.debug(f"⚠️ API {api_name} retornou conteúdo muito pequeno")
                    else:
                        self.logger.debug(f"❌ API {api_name} retornou código {head_response.status_code}")
                except Exception as e:
                    self.logger.debug(f"⚠️ Erro no HEAD para {api_name}: {e}")
                
            except Exception as e:
                self.logger.debug(f"❌ Erro verificando API {api_name}: {e}")
                continue
        
        # Salvar no cache
        if apis_disponiveis:
            cache.save_api_check_cache(appid, [api["name"] for api in apis_disponiveis])
        
        return apis_disponiveis

    # -------------------- DOWNLOAD UNIFICADO DE APIS --------------------
    def _baixar_de_apis_unificado(self, appid: str) -> Tuple[bool, Optional[str], str]:
        """
        Função UNIFICADA para baixar de TODAS as APIs
        Tenta na ordem das APIs disponíveis
        """
        temp_dir = None
        
        try:
            # Primeiro verifica quais APIs têm o conteúdo
            apis_disponiveis = self._verificar_disponibilidade_appid(appid)
            
            if not apis_disponiveis:
                self.logger.warning(f"❌ NENHUMA API TEM CONTEÚDO ZIP para AppID {appid}")
                return False, None, "nenhuma"
            
            temp_dir = tempfile.mkdtemp(prefix=f"steam_unified_{appid}_")
            
            for api_config in apis_disponiveis:
                api_name = api_config["name"]
                url_template = api_config["url"]
                
                try:
                    download_url = url_template.replace("<appid>", str(appid))
                    destino = os.path.join(temp_dir, f"{appid}_{api_name.replace(' ', '_')}.zip")
                    
                    self.logger.info(f"🔄 BAIXANDO ZIP DE {api_name}: {download_url}")
                    
                    response = self.session.get(download_url, stream=True, timeout=DOWNLOAD_TIMEOUT)
                    response.raise_for_status()
                    
                    # Verificar tamanho do conteúdo
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) < 100:
                        self.logger.warning(f"⚠️ Conteúdo ZIP muito pequeno da API {api_name}: {content_length} bytes")
                        continue
                    
                    # Fazer download
                    with open(destino, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verificar se arquivo é válido
                    if os.path.exists(destino) and os.path.getsize(destino) > 100:
                        self.logger.info(f"✅ DOWNLOAD ZIP BEM-SUCEDIDO de {api_name}: {os.path.getsize(destino)} bytes")
                        
                        # Verificar se é ZIP válido (se for arquivo zip)
                        if destino.lower().endswith('.zip'):
                            try:
                                with zipfile.ZipFile(destino, 'r') as zip_test:
                                    if zip_test.testzip() is None:
                                        return True, destino, api_name
                                    else:
                                        self.logger.warning(f"⚠️ ZIP corrompido da API {api_name}")
                                        continue
                            except zipfile.BadZipFile:
                                self.logger.warning(f"⚠️ Arquivo não é ZIP válido da API {api_name}")
                                # Retorna mesmo assim, pode ser outro formato
                                return True, destino, api_name
                        else:
                            return True, destino, api_name
                    
                    self.logger.debug(f"❌ Arquivo ZIP inválido da API {api_name}")
                    if os.path.exists(destino):
                        os.remove(destino)
                        
                except Exception as e:
                    self.logger.debug(f"❌ Erro baixando ZIP de {api_name}: {e}")
                    continue
            
            # Se chegou aqui, nenhuma API funcionou
            self.logger.error("❌ TODAS AS APIS ZIP DISPONÍVEIS FALHARAM NO DOWNLOAD")
            return False, None, "nenhuma"
            
        except Exception as e:
            self.logger.error(f"💥 ERRO CRÍTICO NO SISTEMA UNIFICADO DE APIS: {e}")
            return False, None, "erro"
        finally:
            # Limpeza se falhou
            if temp_dir and os.path.exists(temp_dir):
                files = list(Path(temp_dir).glob("*"))
                if not files or all(f.stat().st_size == 0 for f in files):
                    shutil.rmtree(temp_dir, ignore_errors=True)

    # -------------------- MÉTODO GIT TRADICIONAL (MANTIDO PARA COMPATIBILIDADE) --------------------
    def _baixar_via_git_tradicional(self, appid: str) -> Tuple[bool, Optional[str]]:
        """
        Método Git tradicional (mantido para compatibilidade)
        Tenta clone da branch principal/master
        """
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"steam_git_trad_{appid}_")
            
            for repo in REPOSITORIOS:
                try:
                    # Tenta clone da branch principal
                    success, out, err = self._executar_comando_git([
                        'git', 'clone', '--depth', '1', repo, temp_dir
                    ], timeout=GIT_TIMEOUT)
                    
                    if success:
                        # Procurar por arquivos do appid específico
                        arquivos_encontrados = []
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                if str(appid) in file and (file.endswith('.lua') or file.endswith('.manifest')):
                                    arquivos_encontrados.append(os.path.join(root, file))
                        
                        if arquivos_encontrados:
                            self.logger.info(f"✅ Git tradicional bem-sucedido: {len(arquivos_encontrados)} arquivos")
                            return True, temp_dir
                    
                    self._limpar_diretorio_temp(temp_dir)
                    temp_dir = tempfile.mkdtemp(prefix=f"steam_git_trad_{appid}_")
                    
                except Exception as e:
                    self.logger.debug(f"❌ Erro no git tradicional {repo}: {e}")
                    continue
                    
            return False, None
            
        except Exception as e:
            if temp_dir:
                self._limpar_diretorio_temp(temp_dir)
            self.logger.debug(f"❌ Erro _baixar_via_git_tradicional: {e}")
            return False, None

    # -------------------- FUNÇÃO MULTI-FONTE CORRIGIDA --------------------
    def baixar_manifesto_multi_fonte(self, appid: str) -> Tuple[Optional[str], str, List[str]]:
        """
        🚀 FUNÇÃO PRINCIPAL DE DOWNLOAD MULTI-FONTE
        Versão integrada e compatível com store_search.py
        """
        self.logger.info(f"🔍 INICIANDO BUSCA MULTI-FONTE para AppID {appid}...")
        
        # 📦 1. TENTAR APIS UNIFICADAS (ZIPs)
        self.logger.info("🔄 TENTANDO APIS UNIFICADAS (ZIPs completos)...")
        success, caminho, fonte_api = self._baixar_de_apis_unificado(appid)
        if success and caminho:
            self.logger.info(f"✅ SUCESSO VIA API UNIFICADA: {fonte_api}")
            apis_disponiveis = self._verificar_disponibilidade_appid(appid)
            nomes_apis = [api["name"] for api in apis_disponiveis]
            return caminho, fonte_api, nomes_apis
        
        # 📄 2. TENTAR DOWNLOAD INDIVIDUAL DE ARQUIVOS (MÉTODO EXCLUSIVO)
        self.logger.info("📥 TENTANDO DOWNLOAD INDIVIDUAL DE ARQUIVOS GITHUB...")
        success, caminho_individual = self._baixar_arquivos_individuais_github(appid)
        if success and caminho_individual:
            self.logger.info(f"✅ SUCESSO VIA DOWNLOAD INDIVIDUAL GITHUB: {caminho_individual}")
            return caminho_individual, "github_individual", ["github_individual"]
        
        # 🔧 3. TENTAR CLONE DE BRANCH ESPECÍFICA (MÉTODO EXCLUSIVO)
        self.logger.info("🔧 TENTANDO CLONE GIT DE BRANCH ESPECÍFICA...")
        success, caminho_git_branch = self._baixar_via_git_clone_branch_especifica(appid)
        if success and caminho_git_branch:
            self.logger.info(f"✅ SUCESSO VIA CLONE DE BRANCH ESPECÍFICA: {caminho_git_branch}")
            return caminho_git_branch, "git_branch", ["git_branch"]
        
        # 🌀 4. TENTAR GIT TRADICIONAL (FALLBACK)
        self.logger.info("🌀 TENTANDO GIT TRADICIONAL (fallback)...")
        success, caminho_git_trad = self._baixar_via_git_tradicional(appid)
        if success and caminho_git_trad:
            self.logger.info(f"✅ SUCESSO VIA GIT TRADICIONAL: {caminho_git_trad}")
            return caminho_git_trad, "git_tradicional", ["git_tradicional"]
        
        # ❌ SE TUDO FALHOU
        apis_disponiveis = self._verificar_disponibilidade_appid(appid)
        nomes_apis = [api["name"] for api in apis_disponiveis]
        
        if apis_disponiveis:
            self.logger.error(f"❌ APIS DISPONÍVEIS MAS TODOS OS DOWNLOADS FALHARAM: {nomes_apis}")
        else:
            self.logger.error(f"❌ NENHUMA FONTE DISPONÍVEL para AppID {appid}")
        
        return None, "nenhuma", nomes_apis

    # -------------------- FUNÇÃO PRINCIPAL DE DOWNLOAD --------------------
    def baixar_manifesto(self, appid: str) -> Dict[str, Any]:
        """
        🚀 FUNÇÃO PRINCIPAL DE DOWNLOAD - COMPATÍVEL COM STORE_SEARCH
        Esta função substitui a função de mesmo nome no store_search.py
        """
        try:
            self.logger.info(f"🎮 INICIANDO DOWNLOAD COMPLETO para AppID: {appid}")
            
            # Buscar fontes
            caminho_download, fonte, apis_disponiveis = self.baixar_manifesto_multi_fonte(appid)
            
            if not caminho_download:
                error_msg = "❌ FALHA NO DOWNLOAD DE TODAS AS FONTES"
                self.logger.error(error_msg)
                
                mensagem_erro = error_msg
                if apis_disponiveis:
                    mensagem_erro += f". APIs verificadas: {', '.join(apis_disponiveis)}"
                else:
                    mensagem_erro += ". Nenhuma API tem conteúdo para este AppID."
                
                return {
                    "success": False,
                    "appid": appid,
                    "error": mensagem_erro,
                    "source": "nenhuma",
                    "apis_disponiveis": apis_disponiveis
                }
            
            self.logger.info(f"✅ DOWNLOAD CONCLUÍDO via {fonte}: {caminho_download}")
            
            # Processar download (usando file_processing existente)
            try:
                from .file_processing import process_downloaded_game_files
                processing_result = process_downloaded_game_files(caminho_download, appid)
            except ImportError:
                # Fallback se file_processing não estiver disponível
                processing_result = {
                    "success": True,
                    "message": "Download concluído (processamento manual necessário)",
                    "files_processed": 1
                }
            
            # Limpeza
            try:
                if os.path.exists(caminho_download):
                    if os.path.isfile(caminho_download):
                        os.remove(caminho_download)
                        self.logger.info(f"🧹 ARQUIVO ORIGINAL REMOVIDO: {caminho_download}")
                    elif os.path.isdir(caminho_download):
                        shutil.rmtree(caminho_download, ignore_errors=True)
                        self.logger.info(f"🧹 DIRETÓRIO ORIGINAL REMOVIDO: {caminho_download}")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro na limpeza: {e}")
            
            # Resultado final
            result = {
                "success": True,
                "appid": appid,
                "source": fonte,
                "apis_disponiveis": apis_disponiveis,
                "processing_result": processing_result,
                "message": f"Download concluído via {fonte} - {processing_result.get('files_processed', 0)} arquivos processados"
            }
            
            self.logger.info(f"🎯 PROCESSO FINALIZADO COM SUCESSO via {fonte}")
            return result
            
        except Exception as e:
            self.logger.error(f"💥 ERRO CRÍTICO em baixar_manifesto: {e}")
            import traceback
            self.logger.error(f"💥 TRACEBACK: {traceback.format_exc()}")
            
            return {
                "success": False,
                "appid": appid,
                "error": f"Erro crítico: {e}",
                "source": "erro",
                "apis_disponiveis": []
            }

    # -------------------- UTILITÁRIOS --------------------
    def _limpar_diretorio_temp(self, caminho: str) -> bool:
        """Limpar diretório temporário"""
        try:
            if caminho and os.path.exists(caminho):
                shutil.rmtree(caminho)
                return True
        except Exception as e:
            self.logger.debug(f"Erro limpando temp {caminho}: {e}")
        return False

    def get_system_status(self) -> Dict[str, Any]:
        """✅ CORREÇÃO: Status do sistema de download COM CACHE"""
        global _SYSTEM_STATUS_CACHE
        
        # ✅ SE JÁ TEM CACHE, RETORNA DIRETO
        if _SYSTEM_STATUS_CACHE is not None:
            self.logger.debug("Retornando cache de status do sistema")
            return _SYSTEM_STATUS_CACHE
            
        try:
            # Verificar status das APIs externas (APENAS UMA VEZ)
            apis_status = {}
            
            for api in EXTERNAL_APIS:
                if not api.get("enabled", True):
                    apis_status[api["name"]] = "disabled"
                    continue
                    
                try:
                    # Usar um appid de teste conhecido (Steam)
                    test_url = api["url"].replace("<appid>", "570")  # Dota 2 como teste
                    response = self.session.head(test_url, timeout=8, allow_redirects=True)
                    
                    if response.status_code == api["success_code"]:
                        apis_status[api["name"]] = "online"
                    elif response.status_code == api.get("unavailable_code", 404):
                        apis_status[api["name"]] = "no_content"
                    else:
                        apis_status[api["name"]] = f"http_{response.status_code}"
                        
                except requests.exceptions.Timeout:
                    apis_status[api["name"]] = "timeout"
                except requests.exceptions.ConnectionError:
                    apis_status[api["name"]] = "connection_error"
                except Exception as e:
                    apis_status[api["name"]] = f"error: {str(e)}"
            
            # ✅ Verificar disponibilidade do Git (APENAS UMA VEZ)
            git_available = self._is_git_available()
            
            status_result = {
                "download_system_available": True,
                "git_available": git_available,
                "external_apis_status": apis_status,
                "external_apis_count": len([api for api in EXTERNAL_APIS if api.get("enabled", True)]),
                "repositories_count": len(REPOSITORIOS),
                "cache_enabled": True,
                "version": "1.0_integrado",
                "status": "operacional",
                "last_updated": time.time()
            }
            
            # ✅ SALVAR NO CACHE GLOBAL
            _SYSTEM_STATUS_CACHE = status_result
            
            return status_result
            
        except Exception as e:
            self.logger.debug(f"Erro get_system_status: {e}")
            return {"status": "erro", "error": str(e)}

# -------------------- FUNÇÕES DE COMPATIBILIDADE CORRIGIDAS --------------------
def criar_gerenciador_download() -> DownloadManager:
    """✅ CORREÇÃO: Cria instância SINGLETON do gerenciador de download"""
    global _DOWNLOAD_MANAGER_INSTANCE
    
    if _DOWNLOAD_MANAGER_INSTANCE is None:
        _DOWNLOAD_MANAGER_INSTANCE = DownloadManager()
    
    return _DOWNLOAD_MANAGER_INSTANCE

# ✅ CORREÇÃO: Função de compatibilidade usando Singleton
def baixar_manifesto(appid: str) -> Dict[str, Any]:
    """
    FUNÇÃO DE COMPATIBILIDADE DIRETA COM SINGLETON
    Permite que o código existente continue funcionando sem alterações
    """
    manager = criar_gerenciador_download()  # ✅ Usa singleton agora
    return manager.baixar_manifesto(appid)

# ✅ CORREÇÃO: Função de compatibilidade usando Singleton
def _verificar_disponibilidade_appid(appid: str) -> List[Dict]:
    """
    FUNÇÃO DE COMPATIBILIDADE DIRETA COM SINGLETON
    Para uso do store_search.py sem quebrar
    """
    manager = criar_gerenciador_download()  # ✅ Usa singleton agora
    return manager._verificar_disponibilidade_appid(appid)

# ✅ CORREÇÃO: Função para resetar cache (útil para testes)
def reset_download_cache():
    """Reseta todo o cache do sistema de download - útil para testes"""
    global _DOWNLOAD_MANAGER_INSTANCE, _DOWNLOAD_MANAGER_INITIALIZED, _SYSTEM_STATUS_CACHE
    
    _DOWNLOAD_MANAGER_INSTANCE = None
    _DOWNLOAD_MANAGER_INITIALIZED = False
    _SYSTEM_STATUS_CACHE = None
    
    logger.info("Cache do sistema de download resetado")

# -------------------- TESTE DO MÓDULO CORRIGIDO --------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    print("🧪 TESTE DO DOWNLOAD_MANAGER.PY - SISTEMA INTEGRADO VERIFICAÇÃO ÚNICA")
    print("=" * 60)
    
    # Testar criação do manager (APENAS UMA VEZ)
    manager = criar_gerenciador_download()
    
    # Testar status do sistema (DEVE USAR CACHE)
    status = manager.get_system_status()
    print("📊 Status do Sistema de Download (PRIMEIRA VEZ):")
    for key, value in status.items():
        if key != "external_apis_status":
            print(f"  • {key}: {value}")
    
    # Testar novamente (DEVE USAR CACHE)
    status2 = manager.get_system_status()
    print(f"\n✅ Status usando cache: {status2['status']}")
    
    print("\n🔍 Status das APIs:")
    for api_name, api_status in status.get("external_apis_status", {}).items():
        print(f"  • {api_name}: {api_status}")
    
    # Testar função de compatibilidade
    print(f"\n🔧 Função de compatibilidade disponível: {callable(baixar_manifesto)}")
    
    # Testar reset de cache
    print("\n" + "=" * 60)
    reset_download_cache()
    print("Cache resetado - pode testar novamente")