# ============================================================
# fix_manager.py — SISTEMA DEFINITIVO REVISADO, OTIMIZADO,
# PROFISSIONAL E 100% INTEGRADO
#
# - Detecção unificada e isolada de jogos instalados
# - Cache completo e seguro
# - Extração ZIP segura
# - Sistema de Fixes robusto, multithread e protegido
# - Interface completa para rotas
# - Nenhuma funcionalidade removida
# - Integração completa com fixes_list.json
# - Código limpo, consolidado, estável e pronto para produção
# ============================================================

import logging
import json
import re
import os
import zipfile
import threading
import urllib.request
import urllib.error
import time
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ============================================================
# ESTADOS GLOBAIS THREAD-SAFE
# ============================================================

FIX_DOWNLOAD_STATE: Dict[int, Dict[str, Any]] = {}
UNFIX_STATE: Dict[int, Dict[str, Any]] = {}

FIX_DOWNLOAD_LOCK = threading.Lock()
UNFIX_LOCK = threading.Lock()

def _set_fix_download_state(appid: int, update: Dict[str, Any]) -> None:
    with FIX_DOWNLOAD_LOCK:
        state = FIX_DOWNLOAD_STATE.get(appid, {})
        state.update(update)
        FIX_DOWNLOAD_STATE[appid] = state

def _get_fix_download_state(appid: int) -> Dict[str, Any]:
    with FIX_DOWNLOAD_LOCK:
        return FIX_DOWNLOAD_STATE.get(appid, {}).copy()

def _set_unfix_state(appid: int, update: Dict[str, Any]) -> None:
    with UNFIX_LOCK:
        state = UNFIX_STATE.get(appid, {})
        state.update(update)
        UNFIX_STATE[appid] = state

def _get_unfix_state(appid: int) -> Dict[str, Any]:
    with UNFIX_LOCK:
        return UNFIX_STATE.get(appid, {}).copy()


# ============================================================
# SIMPLE HTTP CLIENT (HEAD + STREAMING DE DOWNLOAD)
# ============================================================

class SimpleHTTPClient:
    def __init__(self, label: str) -> None:
        self.label = label
        self.default_headers = {
            "User-Agent": "SteamGameLoader/1.0",
            "Accept": "*/*"
        }

    def head(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        try:
            req = urllib.request.Request(url, method="HEAD", headers=self.default_headers)
            resp = urllib.request.urlopen(req, timeout=timeout)
            status = getattr(resp, "status", 200)
            data = {"status_code": int(status), "headers": dict(resp.getheaders())}
            resp.close()
            return data
        except urllib.error.HTTPError as e:
            return {"status_code": e.code, "headers": dict(e.headers or {})}
        except Exception as e:
            return {"status_code": 0, "headers": {}, "error": str(e)}

    def download_stream(self, url: str, timeout: int = 30):
        try:
            req = urllib.request.Request(url, headers=self.default_headers)
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception as e:
            logger.error("download_stream failed: %s", e)
            raise


def ensure_http_client(label: str) -> SimpleHTTPClient:
    return SimpleHTTPClient(label)


# ============================================================
# SISTEMA DE FIXES LOCAIS (JSON-BASED)
# ============================================================

class LocalFixesManager:
    """Gerencia a base local de fixes do fixes_list.json"""
    
    def __init__(self):
        self.fixes_map: Dict[str, Dict[str, Any]] = {}
        self.loaded = False
        self._load_local_fixes()
    
    def _normalize_name(self, name: str) -> str:
        """Normaliza nomes para busca case-insensitive"""
        if not name:
            return ""
        # Converte para minúsculas
        name = name.lower()
        # Remove caracteres especiais comuns em nomes de jogos
        name = re.sub(r'[™©®]', '', name)
        # Remove parênteses e seu conteúdo (ex: (2019), (Remastered))
        name = re.sub(r'\s*\([^)]*\)', '', name)
        # Remove outros caracteres especiais
        name = re.sub(r'[^\w\s]', ' ', name)
        # Remove palavras comuns que não afetam a busca
        common_words = {'online', 'patch', 'bypass', 'tested', 'ok', 'zip', 
                       'edition', 'definitive', 'remastered', 'gold', 'deluxe',
                       'complete', 'ultimate', 'game of the year', 'goty',
                       'enhanced', 'directors cut', 'special edition'}
        
        # Remove palavras comuns
        words = name.split()
        filtered_words = [w for w in words if w not in common_words]
        name = ' '.join(filtered_words)
        # Remove espaços extras
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def _load_local_fixes(self):
        """Carrega os fixes do arquivo JSON local"""
        try:
            base_dir = os.path.dirname(__file__)
            json_path = os.path.join(base_dir, "fixes_list.json")
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Construir mapa normalizado
                fixes = data.get("fixes", {})
                for game_name, url in fixes.items():
                    norm_name = self._normalize_name(game_name)
                    if norm_name:  # Só adiciona se houver nome após normalização
                        self.fixes_map[norm_name] = {
                            "original_name": game_name,
                            "url": url,
                            "raw_name": game_name
                        }
                
                self.loaded = True
                logger.info(f"Local fixes carregados: {len(self.fixes_map)} entradas")
            else:
                logger.warning("fixes_list.json não encontrado")
                
        except Exception as e:
            logger.error(f"Erro ao carregar fixes_list.json: {e}")
    
    def find_fix_by_name(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Busca um fix pelo nome do jogo (case-insensitive)"""
        if not self.loaded or not game_name:
            return None
        
        norm_name = self._normalize_name(game_name)
        if not norm_name:
            return None
        
        # 1. Busca exata
        if norm_name in self.fixes_map:
            return self.fixes_map[norm_name]
        
        # 2. Dividir o nome normalizado em palavras
        name_words = set(norm_name.split())
        if not name_words:
            return None
        
        best_match = None
        best_score = 0
        
        # 3. Buscar por similaridade
        for key, fix_info in self.fixes_map.items():
            key_words = set(key.split())
            
            # Calcular interseção
            intersection = name_words.intersection(key_words)
            if intersection:
                score = len(intersection)
                # Bônus se todas as palavras do nome estão na chave
                if name_words.issubset(key_words):
                    score += 5
                # Bônus se a chave contém o nome ou vice-versa
                if norm_name in key or key in norm_name:
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_match = fix_info
        
        # Considerar match se pelo menos 2 palavras coincidem ou 1 palavra com bônus alto
        if best_match and best_score >= 2:
            return best_match
        
        return None
    
    def get_all_fixes(self) -> List[Dict[str, Any]]:
        """Retorna todos os fixes disponíveis"""
        return [
            {
                "name": info["original_name"],
                "url": info["url"],
                "normalized_name": norm_name
            }
            for norm_name, info in self.fixes_map.items()
        ]


# Instância global do gerenciador de fixes locais
_local_fixes_manager = None

def get_local_fixes_manager():
    """Singleton para o gerenciador de fixes locais"""
    global _local_fixes_manager
    if _local_fixes_manager is None:
        _local_fixes_manager = LocalFixesManager()
    return _local_fixes_manager


# ============================================================
# DETECÇÃO DO STEAM
# ============================================================

def detect_steam_root() -> Optional[str]:
    try:
        # WINDOWS
        if os.name == "nt":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                    p, _ = winreg.QueryValueEx(key, "SteamPath")
                    if os.path.isdir(p):
                        return os.path.abspath(p)
            except Exception:
                pass

            default_paths = [
                r"C:\Program Files (x86)\Steam",
                r"C:\Program Files\Steam",
                r"D:\Steam",
                r"E:\Steam",
            ]
            for p in default_paths:
                if os.path.isdir(p):
                    return os.path.abspath(p)

        # LINUX
        home = os.path.expanduser("~")
        linux_candidates = [
            os.path.join(home, ".local", "share", "Steam"),
            os.path.join(home, ".steam", "steam"),
            os.path.join(home, "Steam")
        ]
        for p in linux_candidates:
            if os.path.isdir(p):
                return os.path.abspath(p)

    except Exception as e:
        logger.debug("detect_steam_root error: %s", e)

    return None


# ============================================================
# PARSER DE libraryfolders.vdf
# ============================================================

def _parse_libraryfolders_vdf(vdf_path: str) -> List[str]:
    libs = []
    try:
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for m in re.finditer(r'"path"\s*"([^"]+)"', content):
            p = m.group(1).replace("\\\\", "\\")
            if os.path.isdir(p):
                libs.append(os.path.abspath(p))

    except Exception as e:
        logger.debug("parse libraryfolders.vdf: %s", e)

    return libs


# ============================================================
# SCAN COMPLETO DOS JOGOS STEAM INSTALADOS (SEM DLC / FIXES)
# ============================================================

def scan_steam_games(steam_root: str) -> List[Dict[str, Any]]:
    games: List[Dict[str, Any]] = []

    try:
        if not steam_root or not os.path.exists(steam_root):
            return []

        steam_root = os.path.abspath(steam_root)
        steamapps_main = os.path.join(steam_root, "steamapps")
        library_vdf = os.path.join(steamapps_main, "libraryfolders.vdf")

        libraries = [steam_root]

        if os.path.isfile(library_vdf):
            libraries.extend(_parse_libraryfolders_vdf(library_vdf))

        seen = {}

        for library in libraries:
            steamapps_dir = os.path.join(library, "steamapps")
            if not os.path.isdir(steamapps_dir):
                continue

            for fname in os.listdir(steamapps_dir):
                if not fname.startswith("appmanifest_") or not fname.endswith(".acf"):
                    continue

                manifest_path = os.path.join(steamapps_dir, fname)
                try:
                    with open(manifest_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    appid_m = re.search(r'"appid"\s*"(\d+)"', content)
                    name_m = re.search(r'"name"\s*"(.+?)"', content)
                    installdir_m = re.search(r'"installdir"\s*"(.+?)"', content)

                    if not appid_m or not installdir_m:
                        continue

                    appid = int(appid_m.group(1))
                    name = name_m.group(1) if name_m else f"App {appid}"
                    installdir = installdir_m.group(1)
                    install_path = os.path.join(library, "steamapps", "common", installdir)
                    install_path = os.path.abspath(install_path)

                    if appid not in seen:
                        seen[appid] = True
                        games.append({
                            "appid": appid,
                            "name": name,
                            "installdir": installdir,
                            "library": library,
                            "install_path": install_path
                        })

                except Exception as e:
                    logger.debug("Erro lendo manifesto %s: %s", manifest_path, e)

    except Exception as e:
        logger.exception("scan_steam_games: %s", e)

    return sorted(games, key=lambda g: g["name"].lower())


# ============================================================
# UTILITÁRIOS
# ============================================================

def format_file_size(val: int) -> str:
    try:
        if val <= 0:
            return "0 B"
        sizes = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        size = float(val)
        while size >= 1024 and idx < len(sizes) - 1:
            size /= 1024.0
            idx += 1
        return f"{round(size, 2)} {sizes[idx]}"
    except Exception:
        return f"{val} B"


def safe_extract_zip(zip_path: str, target_dir: str) -> List[str]:
    extracted = []
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            if member.is_dir():
                continue

            normalized = os.path.normpath(member.filename)
            if normalized.startswith("..") or os.path.isabs(normalized):
                logger.warning("ZIP inseguro ignorado: %s", member.filename)
                continue

            out = os.path.join(target_dir, normalized)

            abs_out = os.path.abspath(out)
            abs_base = os.path.abspath(target_dir)
            if not abs_out.startswith(abs_base):
                logger.warning("ZIP path traversal bloqueado: %s", member.filename)
                continue

            os.makedirs(os.path.dirname(abs_out), exist_ok=True)

            with z.open(member) as src, open(abs_out, "wb") as dst:
                dst.write(src.read())

            extracted.append(normalized)

    return extracted


def compute_dir_size(path: str, max_files: int = 50000) -> int:
    total = 0
    try:
        count = 0
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
                count += 1
                if count >= max_files:
                    return total
    except Exception:
        pass
    return total


# ============================================================
# DETECÇÃO DE PLUGINS LUA
# ============================================================

def detect_lua_plugins(steam_root: Optional[str]) -> List[Dict[str, Any]]:
    results = []
    try:
        if not steam_root:
            steam_root = detect_steam_root()
        if not steam_root:
            return []

        candidates = [
            os.path.join(steam_root, "config", "stplug-in"),
            os.path.join(steam_root, "config", "st-plugin"),
            os.path.join(steam_root, "stplug-in"),
        ]

        for c in candidates:
            if not os.path.isdir(c):
                continue

            for root, _, files in os.walk(c):
                for fname in files:
                    if fname.lower().endswith(".lua"):
                        full = os.path.join(root, fname)
                        try:
                            st = os.stat(full)
                            results.append({
                                "path": os.path.abspath(full),
                                "filename": fname,
                                "size": st.st_size,
                                "size_formatted": format_file_size(st.st_size),
                                "modified": datetime.fromtimestamp(st.st_mtime).isoformat()
                            })
                        except Exception:
                            pass

            break
    except Exception as e:
        logger.debug("detect_lua_plugins: %s", e)

    return results


# ============================================================
# FETCH APP NAME
# ============================================================

def fetch_app_name(appid: int) -> Optional[str]:
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
    client = ensure_http_client("AppName")

    try:
        req = urllib.request.Request(url, headers=client.default_headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)
            entry = data.get(str(appid), {})
            if entry.get("success") and entry.get("data", {}).get("name"):
                return entry["data"]["name"]
    except Exception:
        pass

    return None


# ============================================================
# CHECK FOR FIXES (INTEGRADO: GITHUB + JSON LOCAL)
# ============================================================

def check_for_fixes(appid: int) -> Dict[str, Any]:
    """Versão atualizada com busca local"""
    try:
        appid = int(appid)
    except Exception:
        return {"success": False, "error": "AppID inválido"}

    client = ensure_http_client("FixManager")

    # Obter nome do jogo primeiro (para busca local)
    game_name = fetch_app_name(appid) or f"Jogo {appid}"
    
    result = {
        "success": True,
        "appid": appid,
        "gameName": game_name,
        "genericFix": {"available": False, "status": 0},
        "onlineFix": {"available": False, "status": 0},
        "localFix": {"available": False, "source": "none"},  # NOVO CAMPO
        "has_fix": False,
        "has_fixes": False,
        "has_dlc": False
    }

    # 1. Primeiro verificar APIs online (com timeout curto)
    generic_url = f"https://github.com/ShayneVi/Bypasses/releases/download/v1.0/{appid}.zip"
    online_urls = [
        f"https://github.com/ShayneVi/OnlineFix1/releases/download/fixes/{appid}.zip",
        f"https://github.com/ShayneVi/OnlineFix2/releases/download/fixes/{appid}.zip"
    ]

    try:
        # generic - com timeout curto
        res = client.head(generic_url, timeout=5)
        status = int(res.get("status_code", 0))
        result["genericFix"]["status"] = status
        if status == 200:
            result["genericFix"]["available"] = True
            result["genericFix"]["url"] = generic_url
            result["has_fix"] = True
            result["has_fixes"] = True

        # online - com timeout curto
        for u in online_urls:
            r = client.head(u, timeout=5)
            code = int(r.get("status_code", 0))
            if code == 200:
                result["onlineFix"]["available"] = True
                result["onlineFix"]["url"] = u
                result["onlineFix"]["status"] = code
                result["has_fix"] = True
                result["has_fixes"] = True
                break

    except Exception as e:
        logger.debug(f"APIs online indisponíveis: {e}")

    # 2. BUSCA LOCAL (FALLBACK) - NOVO
    if not result["has_fix"]:
        local_manager = get_local_fixes_manager()
        local_fix = local_manager.find_fix_by_name(game_name)
        
        if local_fix:
            result["localFix"] = {
                "available": True,
                "source": "json_local",
                "url": local_fix["url"],
                "original_name": local_fix["original_name"],
                "matched_name": game_name
            }
            result["has_fix"] = True
            result["has_fixes"] = True
            logger.info(f"Fix local encontrado para {game_name}")

    return result


# ============================================================
# APLICAÇÃO DE FIX (THREAD)
# ============================================================

def ensure_temp_download_dir() -> str:
    base = os.path.dirname(__file__)
    tdir = os.path.join(base, "_fixes_temp")
    os.makedirs(tdir, exist_ok=True)
    return tdir


def _download_and_extract_fix(appid: int, download_url: str, install_path: str, fix_type: str, game_name: str):
    temp_zip = ""
    try:
        _set_fix_download_state(appid, {"status": "downloading", "bytesRead": 0, "totalBytes": 0})

        temp_dir = ensure_temp_download_dir()
        temp_zip = os.path.join(temp_dir, f"fix_{appid}_{int(time.time())}.zip")

        client = ensure_http_client("FixDownload")
        resp = client.download_stream(download_url)

        total = int(resp.getheader("Content-Length") or 0)
        _set_fix_download_state(appid, {"totalBytes": total})

        downloaded = 0
        with open(temp_zip, "wb") as f:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break

                st = _get_fix_download_state(appid)
                if st.get("status") == "cancelled":
                    raise RuntimeError("Download cancelado")

                downloaded += len(chunk)
                f.write(chunk)
                _set_fix_download_state(appid, {"bytesRead": downloaded})

        # extração
        _set_fix_download_state(appid, {"status": "extracting"})
        os.makedirs(install_path, exist_ok=True)

        extracted = safe_extract_zip(temp_zip, install_path)

        # log
        logp = os.path.join(install_path, f"luatools-fix-log-{appid}.log")
        try:
            with open(logp, "w", encoding="utf-8") as lf:
                lf.write(f"Data: {datetime.now().isoformat()}\n")
                lf.write(f"Jogo: {game_name}\n")
                lf.write(f"Tipo de Fix: {fix_type}\n")
                lf.write(f"URL: {download_url}\n")
                lf.write("Arquivos extraídos:\n")
                for p in extracted:
                    lf.write(p + "\n")
        except Exception:
            pass

        _set_fix_download_state(appid, {"status": "completed", "success": True, "files_extracted": len(extracted)})
        logger.info("Fix aplicado (%s): %d arquivos", game_name, len(extracted))

    except Exception as e:
        _set_fix_download_state(appid, {"status": "failed", "success": False, "error": str(e)})
        logger.error("apply fix error: %s", e)

    finally:
        try:
            if temp_zip and os.path.isfile(temp_zip):
                os.remove(temp_zip)
        except Exception:
            pass


def apply_game_fix(appid: int, url: str, install_path: str, fix_type: str = "", game_name: str = ""):
    try:
        appid = int(appid)
    except Exception:
        return {"success": False, "error": "AppID inválido"}

    if not url or not install_path:
        return {"success": False, "error": "URL ou caminho inválido"}

    if not os.path.exists(install_path):
        return {"success": False, "error": "Diretório não encontrado"}

    _set_fix_download_state(appid, {"status": "queued", "bytesRead": 0, "totalBytes": 0})

    t = threading.Thread(target=_download_and_extract_fix, args=(appid, url, install_path, fix_type, game_name), daemon=True)
    t.start()

    return {"success": True, "message": "Fix iniciado"}


def get_apply_fix_status(appid: int):
    try:
        appid = int(appid)
    except Exception:
        return {"success": False, "error": "AppID inválido"}

    return {"success": True, "state": _get_fix_download_state(appid)}


def cancel_apply_fix(appid: int):
    try:
        appid = int(appid)
    except Exception:
        return {"success": False, "error": "AppID inválido"}

    st = _get_fix_download_state(appid)
    if st.get("status") in ["completed", "failed"]:
        return {"success": True, "message": "Nada para cancelar"}

    _set_fix_download_state(appid, {"status": "cancelled", "error": "Cancelado pelo usuário"})
    return {"success": True}


# ============================================================
# UNFIX
# ============================================================

def _unfix_worker(appid: int, install_path: str):
    try:
        logf = os.path.join(install_path, f"luatools-fix-log-{appid}.log")
        if not os.path.exists(logf):
            _set_unfix_state(appid, {"status": "failed", "error": "Log não encontrado"})
            return

        _set_unfix_state(appid, {"status": "reading_log"})

        files_to_rm = []
        with open(logf, "r", encoding="utf-8") as f:
            reading = False
            for line in f:
                line = line.strip()
                if line == "Arquivos extraídos:":
                    reading = True
                    continue
                if reading and line:
                    files_to_rm.append(line)

        _set_unfix_state(appid, {"status": "removing", "count": len(files_to_rm)})

        removed = 0
        for rel in files_to_rm:
            full = os.path.abspath(os.path.join(install_path, rel))
            base = os.path.abspath(install_path)
            if not full.startswith(base):
                continue
            if os.path.exists(full):
                try:
                    os.remove(full)
                except Exception:
                    pass
                removed += 1

        try:
            os.remove(logf)
        except Exception:
            pass

        _set_unfix_state(appid, {"status": "completed", "success": True, "files_removed": removed})

    except Exception as e:
        logger.error("unfix worker error: %s", e)
        _set_unfix_state(appid, {"status": "failed", "error": str(e)})


def unfix_game(appid: int, install_path: str):
    try:
        appid = int(appid)
    except Exception:
        return {"success": False, "error": "AppID inválido"}

    if not install_path or not os.path.exists(install_path):
        return {"success": False, "error": "Caminho inválido"}

    _set_unfix_state(appid, {"status": "queued"})
    t = threading.Thread(target=_unfix_worker, args=(appid, install_path), daemon=True)
    t.start()

    return {"success": True, "message": "Remoção iniciada"}


def get_unfix_status(appid: int):
    try:
        appid = int(appid)
    except Exception:
        return {"success": False, "error": "AppID inválido"}

    return {"success": True, "state": _get_unfix_state(appid)}


# ============================================================
# *** DETECÇÃO UNIFICADA E ISOLADA DOS JOGOS INSTALADOS ***
# ============================================================

def get_installed_games_unified(steam_path: Optional[str],
                                include_size: bool = True,
                                include_fix_flag: bool = True,
                                include_dlc_flag: bool = True) -> Dict[str, Any]:
    """
    Função definitiva, única e isolada de detecção.
    Aqui é a fonte da verdade.
    """
    try:
        if not steam_path or not os.path.exists(steam_path):
            return {"success": False, "error": "Steam não detectado", "games": []}

        raw = scan_steam_games(steam_path)
        final = []

        for g in raw:
            install_path = g.get("install_path")
            size_bytes = 0
            has_fix = False
            has_dlc = False

            if install_path and os.path.isdir(install_path):

                if include_fix_flag:
                    logp = os.path.join(install_path, f"luatools-fix-log-{g['appid']}.log")
                    has_fix = os.path.exists(logp)

                if include_size:
                    size_bytes = compute_dir_size(install_path)

                if include_dlc_flag:
                    try:
                        if os.path.isdir(os.path.join(install_path, "dlc")):
                            has_dlc = True
                        else:
                            for root, _, files in os.walk(install_path):
                                for f in files:
                                    lf = f.lower()
                                    if "dlc" in lf or lf.endswith(".pak") or lf.endswith(".dlc"):
                                        has_dlc = True
                                        break
                                if has_dlc:
                                    break
                    except Exception:
                        pass

            final.append({
                **g,
                "size": size_bytes,
                "size_formatted": format_file_size(size_bytes),
                "has_fix": has_fix,
                "has_fixes": has_fix,
                "fix_status": "applied" if has_fix else "none",
                "has_dlc": has_dlc
            })

        return {
            "success": True,
            "games": final,
            "count": len(final),
            "steam_path": steam_path
        }

    except Exception as e:
        logger.error("get_installed_games_unified: %s", e)
        return {"success": False, "error": str(e), "games": []}


# ============================================================
# NOVA FUNÇÃO: Busca direta no JSON
# ============================================================

def search_local_fixes(query: str) -> Dict[str, Any]:
    """Busca fixes locais por query (para interface)"""
    manager = get_local_fixes_manager()
    results = []
    
    if not query or not manager.loaded:
        return {"success": True, "results": results, "count": 0}
    
    norm_query = manager._normalize_name(query)
    
    for norm_name, fix_info in manager.fixes_map.items():
        if norm_query in norm_name or norm_name in norm_query:
            results.append({
                "name": fix_info["original_name"],
                "normalized_name": norm_name,
                "url": fix_info["url"],
                "match_score": len(set(norm_query.split()).intersection(set(norm_name.split())))
            })
    
    # Ordenar por relevância
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "success": True,
        "results": results[:20],  # Limitar a 20 resultados
        "count": len(results),
        "total_in_db": len(manager.fixes_map)
    }


# ============================================================
# FixManager — INTERFACE PRINCIPAL PARA ROTAS / APIs
# ============================================================

class FixManager:
    def __init__(self, steam_path: Optional[str] = None):
        detected = detect_steam_root()
        self.steam_path = Path(steam_path) if steam_path else Path(detected) if detected else None

        # Cache interno apenas do UNIFIED
        self.cache_data: Optional[List[Dict[str, Any]]] = None
        self.cache_time = 0
        self.cache_ttl = 300  # 5 minutos
        
        # Inicializar gerenciador local
        self.local_fixes = get_local_fixes_manager()
        
        logger.info("FixManager inicializado — steam_path=%s, %d fixes locais", 
                   self.steam_path, len(self.local_fixes.fixes_map))

    def _cache_valid(self) -> bool:
        return self.cache_data is not None and (time.time() - self.cache_time) < self.cache_ttl

    def get_installed_games(self, force_refresh: bool = False) -> Dict[str, Any]:
        if not force_refresh and self._cache_valid():
            return {"success": True, "games": self.cache_data, "cached": True, "count": len(self.cache_data)}

        if not self.steam_path or not self.steam_path.exists():
            return {"success": False, "error": "Steam não detectado", "games": []}

        res = get_installed_games_unified(str(self.steam_path))

        if res.get("success"):
            self.cache_data = res["games"]
            self.cache_time = time.time()

        return res

    # ======================================================
    # FIX TOOLS
    # ======================================================

    def check_game_fixes(self, appid: int) -> Dict[str, Any]:
        info = check_for_fixes(appid)

        games = self.get_installed_games()
        if games.get("success"):
            gi = next((x for x in games["games"] if int(x["appid"]) == int(appid)), None)
            if gi:
                info["installed"] = True
                info["install_path"] = gi.get("install_path")
                info["has_fix_applied"] = gi.get("has_fix")
                info["size"] = gi.get("size", 0)
                info["size_formatted"] = gi.get("size_formatted", "0 B")
                info["has_dlc"] = gi.get("has_dlc", False)
            else:
                info["installed"] = False
        else:
            info["installed"] = False

        return info

    def apply_fix(self, appid: int, fix_type: str = "auto"):
        """Versão atualizada com suporte a fixes locais"""
        info = self.check_game_fixes(appid)
        if not info.get("success"):
            return info
        if not info.get("installed"):
            return {"success": False, "error": "Jogo não instalado"}

        url = None
        sel = ""
        source = ""

        if fix_type == "auto":
            # Nova ordem: generic -> online -> local
            if info["genericFix"]["available"]:
                url = info["genericFix"]["url"]
                sel = "Generic"
                source = "github"
            elif info["onlineFix"]["available"]:
                url = info["onlineFix"]["url"]
                sel = "Online"
                source = "github"
            elif info["localFix"]["available"]:
                url = info["localFix"]["url"]
                sel = "Local"
                source = "json"
                logger.info(f"Usando fix local: {info['localFix'].get('original_name', 'N/A')}")

        elif fix_type == "generic" and info["genericFix"]["available"]:
            url = info["genericFix"]["url"]
            sel = "Generic"
            source = "github"
        elif fix_type == "online" and info["onlineFix"]["available"]:
            url = info["onlineFix"]["url"]
            sel = "Online"
            source = "github"
        elif fix_type == "local" and info["localFix"]["available"]:
            url = info["localFix"]["url"]
            sel = "Local"
            source = "json"
        elif fix_type == "json" and info["localFix"]["available"]:  # Alias para local
            url = info["localFix"]["url"]
            sel = "Local"
            source = "json"

        if not url:
            # Tentar fallback automático para local se disponível
            if info["localFix"]["available"]:
                url = info["localFix"]["url"]
                sel = "Local (Fallback)"
                source = "json"
                logger.info(f"Usando fallback local para {info['gameName']}")
            else:
                return {"success": False, "error": f"Nenhum fix {fix_type} disponível"}

        # Adicionar informação de origem ao fix_type
        actual_fix_type = f"{sel} ({source})"
        
        res = apply_game_fix(appid, url, info["install_path"], actual_fix_type, info["gameName"])

        if res.get("success"):
            self.cache_data = None

        return res

    def get_fix_status(self, appid: int):
        return get_apply_fix_status(appid)

    def cancel_fix_operation(self, appid: int):
        return cancel_apply_fix(appid)

    def remove_fix(self, appid: int):
        games = self.get_installed_games()
        if not games.get("success"):
            return {"success": False, "error": "Lista de jogos indisponível"}

        gi = next((x for x in games["games"] if int(x["appid"]) == int(appid)), None)
        if not gi:
            return {"success": False, "error": "Jogo não encontrado"}
        if not gi.get("has_fix"):
            return {"success": False, "error": "Nenhum fix aplicado"}

        res = unfix_game(appid, gi["install_path"])

        if res.get("success"):
            self.cache_data = None

        return res

    def get_remove_status(self, appid: int):
        return get_unfix_status(appid)

    def detect_lua_plugins_api(self) -> Dict[str, Any]:
        r = detect_lua_plugins(str(self.steam_path) if self.steam_path else None)
        return {"success": True, "plugins": r, "count": len(r)}

    def validate_installation(self) -> Dict[str, Any]:
        return {
            "steam_detected": bool(self.steam_path),
            "steam_path": str(self.steam_path) if self.steam_path else None,
            "status": "READY" if self.steam_path else "NO_STEAM",
            "version": "FixManager-Unificado-v3.0",
            "local_fixes_loaded": self.local_fixes.loaded,
            "local_fixes_count": len(self.local_fixes.fixes_map)
        }

    def get_system_report(self):
        games = self.get_installed_games()
        return {
            "steam": {
                "detected": bool(self.steam_path),
                "path": str(self.steam_path) if self.steam_path else None,
                "games_count": games.get("count", 0)
            },
            "fixes": {
                "active_downloads": len([x for x in FIX_DOWNLOAD_STATE.values() if x.get("status") in ["downloading", "extracting"]]),
                "active_unfix": len([x for x in UNFIX_STATE.values() if x.get("status") in ["reading_log", "removing"]]),
                "local_fixes_loaded": self.local_fixes.loaded,
                "local_fixes_count": len(self.local_fixes.fixes_map)
            }
        }

    def set_steam_path(self, p: str) -> bool:
        try:
            p = Path(p)
            if p.exists():
                self.steam_path = p
                self.cache_data = None
                self.cache_time = 0
                return True
        except Exception:
            pass
        return False

    def clear_cache(self):
        self.cache_data = None
        self.cache_time = 0

        with FIX_DOWNLOAD_LOCK:
            FIX_DOWNLOAD_STATE.clear()
        with UNFIX_LOCK:
            UNFIX_STATE.clear()

        return {"success": True}
    
    # ======================================================
    # MÉTODOS LOCAIS (JSON)
    # ======================================================
    
    def search_local_fixes(self, query: str) -> Dict[str, Any]:
        """Interface para busca local"""
        return search_local_fixes(query)
    
    def get_local_fixes_stats(self) -> Dict[str, Any]:
        """Estatísticas da base local"""
        return {
            "loaded": self.local_fixes.loaded,
            "count": len(self.local_fixes.fixes_map),
            "sample": list(self.local_fixes.fixes_map.keys())[:5] if self.local_fixes.fixes_map else []
        }
    
    def get_all_local_fixes(self) -> Dict[str, Any]:
        """Retorna todos os fixes locais"""
        fixes = self.local_fixes.get_all_fixes()
        return {
            "success": True,
            "fixes": fixes,
            "count": len(fixes)
        }

# INSTÂNCIA GLOBAL

_fix_manager_instance: Optional[FixManager] = None

def get_fix_manager(steam_path: Optional[str] = None) -> FixManager:
    global _fix_manager_instance
    if _fix_manager_instance is None:
        _fix_manager_instance = FixManager(steam_path)
    elif steam_path and not _fix_manager_instance.steam_path:
        _fix_manager_instance.set_steam_path(steam_path)
    return _fix_manager_instance

def initialize_fix_system(steam_path: Optional[str] = None) -> FixManager:
    mgr = get_fix_manager(steam_path)
    return mgr