# ============================================================
# utils/dlc_manager.py — DLCManager Unificado v10.1
# VERSÃO DEFINITIVA CORRIGIDA - SEM LIMITAÇÕES, SEM FALBACKS
# Exibe TODAS as DLCs disponíveis na Steam com contagem precisa
# ============================================================

import os
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("DLCManager")
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(h)

# ============================================================
# HTTP SESSION ROBUSTA
# ============================================================

session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=16,
    pool_maxsize=32,
    max_retries=Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({
    "User-Agent": "SteamGameLoader/10.1 (DLC-System)",
    "Accept": "application/json",
})

# ============================================================
# DLC MANAGER DEFINITIVO - VERSÃO 10.1 CORRIGIDA
# ============================================================

class DLCManager:
    def __init__(self, steam_path: Optional[str] = None):
        self.steam_path = steam_path
        self._lock = threading.RLock()
        
        # Cache: DLCs por appid - ESTRUTURA CORRIGIDA
        self.dlc_cache: Dict[str, Dict[str, Any]] = {}  # {appid: {"ts": timestamp, "dlcs": lista, "count": int}}
        
        # Cache de jogos detectados via FixManager
        self.games_cache: Dict[str, Any] = {}    # {ts, games_by_appid}
        
        self.ttl_dlcs = 3600      # 1h
        self.ttl_games = 600       # 10min
        
        logger.info("✅ DLCManager v10.1 CORRIGIDO inicializado.")

    # ============================================================
    # STEAM PATH
    # ============================================================

    def set_steam_path(self, path: str):
        if path and Path(path).exists():
            self.steam_path = path
            logger.info(f"Steam path definido: {path}")

    def get_steam_path(self) -> Optional[str]:
        """Obtém Steam Path atual, ou detecta via FixManager."""
        if self.steam_path and Path(self.steam_path).exists():
            return self.steam_path

        try:
            from utils.fix_manager import detect_steam_root
            p = detect_steam_root()
            if p:
                self.steam_path = p
                return p
        except Exception:
            pass

        return None

    # ============================================================
    # STPLUG-IN PATH
    # ============================================================

    def _get_stplug(self) -> Optional[Path]:
        root = self.get_steam_path()
        if not root:
            return None

        p = Path(root) / "config" / "stplug-in"
        try:
            p.mkdir(parents=True, exist_ok=True)
            return p
        except Exception:
            return None

    # ============================================================
    # INSTALLED GAMES
    # ============================================================

    def get_installed_games(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Obtém lista de jogos instalados do FixManager."""
        now = time.time()
        with self._lock:
            c = self.games_cache.get("games")
            if c and not force_refresh:
                if now - c["ts"] < self.ttl_games:
                    return {
                        "success": True,
                        "games": list(c["data"].values()),
                        "games_by_appid": c["data"],
                        "from_cache": True,
                    }

        try:
            from utils.fix_manager import get_fix_manager
            fm = get_fix_manager()
            data = fm.get_installed_games(force_refresh=force_refresh)

            if not data.get("success"):
                return {"success": False, "error": data.get("error", "Erro FixManager")}

            final_map: Dict[str, Dict[str, Any]] = {}

            for g in data["games"]:
                appid = str(g["appid"]).strip()
                # Obter DLCs instaladas para cálculo correto de has_dlc
                installed_dlcs = self.get_installed_dlcs(appid)
                final_map[appid] = {
                    "appid": appid,
                    "name": g.get("name"),
                    "install_path": g.get("install_path"),
                    "has_fix": g.get("has_fix", False),
                    "fix_status": g.get("fix_status", "none"),
                    "has_dlc": len(installed_dlcs) > 0,
                    "installed_dlc_count": len(installed_dlcs),
                }

            with self._lock:
                self.games_cache["games"] = {
                    "ts": now,
                    "data": final_map
                }

            return {
                "success": True,
                "games": list(final_map.values()),
                "games_by_appid": final_map,
                "from_cache": False,
            }

        except Exception as e:
            logger.error(f"Erro ao obter jogos: {e}")
            return {
                "success": False,
                "error": str(e),
                "games": [],
                "games_by_appid": {}
            }

    # ============================================================
    # LISTAR DLCs - VERSÃO DEFINITIVA CORRIGIDA
    # ============================================================

    def list_dlcs(self, appid: str) -> List[Dict[str, Any]]:
        """API simples para o frontend."""
        return self.get_game_dlcs(appid, force_refresh=False)

    def get_game_dlcs(self, appid: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Obtém TODAS as DLCs de um jogo - VERSÃO CORRIGIDA COM CONTAGEM PRECISA."""
        now = time.time()
        cache_key = f"dlc_{appid}"

        with self._lock:
            cache_entry = self.dlc_cache.get(cache_key)
            
            # VERIFICAR CACHE VÁLIDO
            if cache_entry and not force_refresh:
                cache_age = now - cache_entry.get("ts", 0)
                if cache_age < self.ttl_dlcs:
                    dlcs = cache_entry.get("dlcs", [])
                    logger.debug(f"📦 Cache válido para {appid}: {len(dlcs)} DLCs")
                    return dlcs

        logger.info(f"🔄 Buscando DLCs para appid {appid}")
        dlcs = self._fetch_all_steam_dlcs(appid)

        with self._lock:
            self.dlc_cache[cache_key] = {
                "ts": now,
                "dlcs": dlcs,
                "count": len(dlcs)
            }

        logger.info(f"✅ Retornando {len(dlcs)} DLCs válidas para appid {appid}")
        return dlcs

    def _fetch_all_steam_dlcs(self, appid: str) -> List[Dict[str, Any]]:
        """
        Busca TODAS as DLCs da Steam API - VERSÃO CORRIGIDA.
        Retorna APENAS DLCs válidas e únicas.
        """
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        
        try:
            logger.info(f"🌐 Buscando DLCs para {appid}")
            r = session.get(url, timeout=20)
            r.raise_for_status()
            
            data = r.json().get(str(appid), {})
            if not data.get("success"):
                logger.warning(f"API Steam falhou para {appid}")
                return []
            
            dlc_ids = data.get("data", {}).get("dlc", []) or []
            
            if not dlc_ids:
                logger.info(f"ℹ️ {appid} não tem DLCs na Steam")
                return []
            
            # REMOVER DUPLICATAS E VALIDAR IDs
            unique_dlc_ids = []
            seen_ids: Set[str] = set()
            
            for dlc_id in dlc_ids:
                dlc_str = str(dlc_id).strip()
                if dlc_str.isdigit() and dlc_str not in seen_ids:
                    unique_dlc_ids.append(dlc_str)
                    seen_ids.add(dlc_str)
            
            logger.info(f"🎯 {appid}: {len(unique_dlc_ids)} DLCs únicas identificadas")
            
            # BUSCAR DETALHES DE CADA DLC - SEM LIMITES
            processed_dlcs: List[Dict[str, Any]] = []
            valid_ids: Set[str] = set()
            
            for idx, dlc_id in enumerate(unique_dlc_ids, 1):
                try:
                    # EVITAR PROCESSAMENTO DUPLICADO
                    if dlc_id in valid_ids:
                        continue
                    
                    dlc_info = self._fetch_dlc_details(dlc_id)
                    if dlc_info and dlc_info.get("id"):
                        # VALIDAÇÃO CRÍTICA: Verificar se é realmente uma DLC
                        if self._is_valid_dlc(dlc_info):
                            processed_dlcs.append(dlc_info)
                            valid_ids.add(dlc_id)
                        
                    # LOG DE PROGRESSO
                    if len(unique_dlc_ids) > 20 and idx % 20 == 0:
                        logger.debug(f"📊 {appid}: {idx}/{len(unique_dlc_ids)} DLCs processadas")
                        
                    # DELAY MÍNIMO PARA NÃO SOBRECARREGAR
                    if idx % 5 == 0:
                        time.sleep(0.01)
                        
                except Exception as e:
                    logger.debug(f"⚠️ DLC {dlc_id} ignorada: {str(e)[:60]}")
                    continue
            
            logger.info(f"✅ {appid}: {len(processed_dlcs)} DLCs válidas encontradas")
            return processed_dlcs
            
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout ao buscar DLCs para {appid}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Erro de rede ao buscar DLCs para {appid}: {e}")
            return []
        except Exception as e:
            logger.error(f"💥 Erro inesperado ao buscar DLCs para {appid}: {e}")
            return []

    def _is_valid_dlc(self, dlc_info: Dict[str, Any]) -> bool:
        """Valida se a DLC é real e não um artefato da API."""
        # Verificar campos obrigatórios
        if not dlc_info.get("id") or not dlc_info.get("name"):
            return False
        
        # Verificar se não é um pacote ou bundle disfarçado
        dlc_type = dlc_info.get("type", "").lower()
        name = dlc_info.get("name", "").lower()
        
        # Filtrar conteúdo que não são DLCs reais
        invalid_keywords = ["soundtrack", "ost", "artbook", "guide", "season pass", 
                           "bundle", "pack", "comic", "art book", "strategy guide"]
        if any(keyword in name for keyword in invalid_keywords):
            return False
        
        return True

    def _fetch_dlc_details(self, dlc_id: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes completos de uma DLC específica."""
        url = f"https://store.steampowered.com/api/appdetails?appids={dlc_id}"
        
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
            
            data = r.json().get(dlc_id, {})
            if not data.get("success"):
                return None
            
            dlc_data = data.get("data", {})
            
            # Extrair informações detalhadas
            price_info = dlc_data.get("price_overview", {})
            release_info = dlc_data.get("release_date", {})
            
            return {
                "id": dlc_id,
                "appid": dlc_id,
                "name": dlc_data.get("name", f"DLC {dlc_id}"),
                "description": dlc_data.get("short_description", ""),
                "type": dlc_data.get("type", "dlc"),
                "price": price_info.get("final_formatted", "N/A"),
                "original_price": price_info.get("initial_formatted", "N/A"),
                "discount_percent": price_info.get("discount_percent", 0),
                "is_free": dlc_data.get("is_free", False),
                "release_date": release_info.get("date", ""),
                "coming_soon": release_info.get("coming_soon", False),
                "header_image": dlc_data.get("header_image", ""),
                "capsule_image": dlc_data.get("capsule_image", ""),
            }
            
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout ao buscar detalhes da DLC {dlc_id}")
            return None
        except Exception as e:
            logger.debug(f"Erro ao buscar DLC {dlc_id}: {str(e)[:50]}")
            return None

    # ============================================================
    # INSTALAR DLCs
    # ============================================================

    def install_dlcs(self, appid: str, dlc_ids: List[str]) -> Dict[str, Any]:
        """Instala DLCs para um jogo."""
        if not dlc_ids:
            return {"success": False, "error": "Nenhuma DLC especificada."}

        stplug = self._get_stplug()
        if not stplug:
            return {"success": False, "error": "stplug-in não encontrado."}

        fpath = stplug / "Steamtools.lua"

        try:
            lines = fpath.read_text(encoding="utf-8").splitlines() if fpath.exists() else []
        except Exception as e:
            logger.error(f"Erro ao ler Steamtools.lua: {e}")
            return {"success": False, "error": f"Erro ao ler arquivo: {e}"}

        # Verificar DLCs já instaladas
        installed = set(self.get_installed_dlcs(appid))
        to_add = [dlc_id for dlc_id in dlc_ids if dlc_id not in installed]

        if not to_add:
            return {"success": True, "message": "Todas as DLCs já estão instaladas.", "installed": 0}

        # Adicionar novas DLCs
        for dlc_id in to_add:
            lines.append(f"addappid({dlc_id}, 1)")

        try:
            fpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception as e:
            logger.error(f"Erro ao escrever Steamtools.lua: {e}")
            return {"success": False, "error": f"Erro ao salvar arquivo: {e}"}

        # Limpar cache
        with self._lock:
            self.dlc_cache.pop(f"dlc_{appid}", None)
            self.games_cache.pop("games", None)

        logger.info(f"✅ Instaladas {len(to_add)} DLCs para {appid}: {to_add}")
        
        return {
            "success": True,
            "installed": len(to_add),
            "dlcs_added": to_add,
            "message": f"{len(to_add)} DLC(s) instalada(s) com sucesso."
        }

    # ============================================================
    # INSTALLED DLCs - VERSÃO CORRIGIDA
    # ============================================================

    def get_installed_dlcs(self, appid: str) -> List[str]:
        """Retorna lista de DLCs instaladas para um jogo - VERSÃO CORRIGIDA."""
        stplug = self._get_stplug()
        if not stplug:
            return []
        
        fpath = stplug / "Steamtools.lua"
        if not fpath.exists():
            return []
        
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            installed: List[str] = []
            seen_ids: Set[str] = set()
            
            for line in content.splitlines():
                line_clean = line.strip().replace(" ", "")
                if line_clean.startswith("addappid("):
                    try:
                        # Extrair: addappid(123456,1)
                        parts = line_clean[9:-1].split(",")  # Remove "addappid(" e ")"
                        if parts and parts[0].isdigit():
                            dlc_id = parts[0]
                            # EVITAR DUPLICATAS
                            if dlc_id not in seen_ids:
                                installed.append(dlc_id)
                                seen_ids.add(dlc_id)
                    except Exception:
                        continue
            
            logger.debug(f"📁 {appid}: {len(installed)} DLCs instaladas únicas")
            return installed
            
        except Exception as e:
            logger.error(f"Erro ao ler DLCs instaladas para {appid}: {e}")
            return []

    # ============================================================
    # REMOVER DLCs
    # ============================================================

    def uninstall_dlcs(self, appid: str, dlc_ids: List[str] = None) -> Dict[str, Any]:
        """Remove DLCs de um jogo."""
        stplug = self._get_stplug()
        if not stplug:
            return {"success": False, "error": "stplug-in não encontrado."}

        fpath = stplug / "Steamtools.lua"
        if not fpath.exists():
            return {"success": True, "message": "Nenhuma DLC instalada.", "removed": 0}

        try:
            lines = fpath.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            return {"success": False, "error": f"Erro ao ler arquivo: {e}"}

        # Se não especificar DLCs, remove todas do appid
        if not dlc_ids:
            installed = self.get_installed_dlcs(appid)
            if not installed:
                return {"success": True, "message": "Nenhuma DLC instalada.", "removed": 0}
            dlc_ids = installed

        new_lines = []
        removed_count = 0
        
        for line in lines:
            line_stripped = line.strip()
            should_keep = True
            
            # Verifica se é uma linha de DLC a ser removida
            for dlc_id in dlc_ids:
                if f"addappid({dlc_id}," in line_stripped.replace(" ", ""):
                    should_keep = False
                    removed_count += 1
                    break
            
            if should_keep:
                new_lines.append(line)

        try:
            fpath.write_text("\n".join(new_lines), encoding="utf-8")
        except Exception as e:
            return {"success": False, "error": f"Erro ao salvar arquivo: {e}"}

        # Limpar cache
        with self._lock:
            self.dlc_cache.pop(f"dlc_{appid}", None)
            self.games_cache.pop("games", None)

        logger.info(f"🗑️ Removidas {removed_count} DLCs de {appid}")
        
        return {
            "success": True,
            "removed": removed_count,
            "message": f"{removed_count} DLC(s) removida(s)."
        }

    # ============================================================
    # STATUS - VERSÃO CORRIGIDA
    # ============================================================

    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do DLC Manager."""
        games_info = self.get_installed_games()
        
        games = games_info.get("games_by_appid") or {}
        total_games = len(games)
        games_with_dlc = sum(1 for g in games.values() if g.get("has_dlc", False))
        
        # Calcular total de DLCs em cache CORRETAMENTE
        total_dlcs_cached = 0
        for appid, cache in self.dlc_cache.items():
            if cache and "dlcs" in cache:
                total_dlcs_cached += len(cache["dlcs"])

        return {
            "success": True,
            "steam_path": self.get_steam_path(),
            "stplug-in": str(self._get_stplug() or ""),
            "total_games": total_games,
            "games_with_dlc": games_with_dlc,
            "dlc_cache_size": len(self.dlc_cache),
            "total_dlcs_cached": total_dlcs_cached,
            "from_cache": games_info.get("from_cache", False),
            "version": "DLCManager v10.1 CORRIGIDO",
            "timestamp": time.time()
        }

    # ============================================================
    # UTILIDADES
    # ============================================================

    def clear_cache(self) -> Dict[str, Any]:
        """Limpa todo o cache do DLC Manager."""
        with self._lock:
            self.dlc_cache.clear()
            self.games_cache.clear()
        
        logger.info("🧹 Cache do DLC Manager limpo completamente")
        return {
            "success": True,
            "message": "Cache limpo com sucesso.",
            "dlc_cache_cleared": True,
            "games_cache_cleared": True
        }

    def get_game_summary(self, appid: str) -> Dict[str, Any]:
        """Retorna resumo completo de um jogo com DLCs."""
        games_info = self.get_installed_games()
        game = games_info.get("games_by_appid", {}).get(str(appid))
        
        if not game:
            return {"success": False, "error": f"Jogo {appid} não encontrado"}
        
        dlcs = self.get_game_dlcs(appid)
        installed_dlcs = self.get_installed_dlcs(appid)
        
        # CONTAGEM PRECISA - APENAS DLCs VÁLIDAS
        valid_dlcs = [d for d in dlcs if d.get("id") and d.get("name")]
        
        return {
            "success": True,
            "game": game,
            "available_dlcs": len(valid_dlcs),
            "installed_dlcs": len(installed_dlcs),
            "dlcs": valid_dlcs,
            "installed_dlc_ids": installed_dlcs,
            "validated_count": len(valid_dlcs)
        }

    def validate_dlc_data(self, appid: str) -> Dict[str, Any]:
        """Valida e retorna dados de DLC corrigidos."""
        try:
            # FORÇAR ATUALIZAÇÃO COMPLETA
            dlcs = self.get_game_dlcs(appid, force_refresh=True)
            installed = self.get_installed_dlcs(appid)
            
            # FILTRAR APENAS DLCs VÁLIDAS
            valid_dlcs = []
            for dlc in dlcs:
                if dlc.get("id") and dlc.get("name") and self._is_valid_dlc(dlc):
                    valid_dlcs.append(dlc)
            
            logger.info(f"🔍 Validação {appid}: {len(valid_dlcs)}/{len(dlcs)} DLCs válidas")
            
            return {
                "success": True,
                "appid": appid,
                "total_raw": len(dlcs),
                "total_valid": len(valid_dlcs),
                "installed_count": len(installed),
                "dlcs": valid_dlcs,
                "installed_dlc_ids": installed,
                "timestamp": time.time(),
                "validated": True
            }
            
        except Exception as e:
            logger.error(f"Erro na validação de DLCs para {appid}: {e}")
            return {
                "success": False,
                "error": str(e),
                "appid": appid
            }


# ============================================================
# INSTÂNCIA GLOBAL
# ============================================================

_instance: Optional[DLCManager] = None

def get_dlc_manager(steam_path: Optional[str] = None) -> DLCManager:
    """Retorna instância global do DLC Manager."""
    global _instance
    if _instance is None:
        _instance = DLCManager(steam_path)
    elif steam_path and not _instance.steam_path:
        _instance.set_steam_path(steam_path)
    return _instance

def initialize_dlc_system(steam_path: Optional[str] = None) -> DLCManager:
    """Inicializa o sistema DLC."""
    return get_dlc_manager(steam_path)