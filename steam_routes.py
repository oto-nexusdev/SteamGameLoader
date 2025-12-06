import os
import json
import logging
import time
import re
import urllib.request
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify

logger = logging.getLogger("steam_routes")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

# ===================================================================
# IMPORT DO FIX_MANAGER PARA ACESSO AOS FIXES LOCAIS
# ===================================================================

try:
    from fix_manager import get_local_fixes_manager, search_local_fixes, get_fix_manager
    FIX_MANAGER_AVAILABLE = True
    logger.info("✅ Fix Manager disponível para integração")
except ImportError as e:
    logger.warning(f"⚠️ Fix Manager não disponível: {e}")
    FIX_MANAGER_AVAILABLE = False

# ===================================================================
# SERIALIZADOR SEGURO LOCAL
# ===================================================================

def make_json_safe(obj, _seen=None):
    """Serializador seguro para evitar problemas com objetos complexos"""
    if _seen is None:
        _seen = set()
    oid = id(obj)
    if oid in _seen:
        return "<cyclic>"
    _seen.add(oid)

    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8", errors="ignore")
        except Exception:
            return str(obj)

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, (datetime)):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {str(k): make_json_safe(v, _seen) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [make_json_safe(x, _seen) for x in obj]

    if hasattr(obj, "__dict__"):
        return make_json_safe(obj.__dict__, _seen)

    try:
        return str(obj)
    except Exception:
        return "<unserializable>"

def safe_jsonify(obj, status=200):
    """Versão local de safe_jsonify"""
    try:
        payload = json.dumps(make_json_safe(obj), ensure_ascii=False)
        return Flask.response_class(payload, mimetype="application/json", status=status)
    except Exception as e:
        logger.error(f"Falha ao serializar JSON: {e}")
        return Flask.response_class(
            json.dumps({"success": False, "error": "Falha ao serializar JSON"}),
            mimetype="application/json",
            status=500
        )

# ===================================================================
# SETUP PRINCIPAL – ROTAS STEAM DEFINITIVAS
# ===================================================================

def setup_steam_routes(app: Flask, getattr_funcs: dict):
    """
    Configura rotas Steam ÚNICAS e DEFINITIVAS
    Sem redundâncias - Fonte única de verdade
    """
    logger.info("🔧 CONFIGURAÇÃO DEFINITIVA: Rotas Steam ÚNICAS...")

    # ===================================================================
    # HELPER DE ACESSO A STEAM_UTILS
    # ===================================================================
    
    def _get(name, default=None):
        """Obtém função de steam_utils de forma segura"""
        func = getattr_funcs.get(name)
        if callable(func):
            try:
                return func
            except Exception as e:
                logger.error(f"❌ Erro ao acessar função {name}: {e}")
                return default
        return default

    # ===================================================================
    # CARREGAR FUNÇÕES DO STEAM_UTILS
    # ===================================================================
    
    get_steam_path = _get("get_steam_path")
    is_steam_running = _get("is_steam_running")
    get_steam_info = _get("get_steam_info")
    launch_steam = _get("launch_steam")
    kill_steam = _get("kill_steam")
    get_steam_username = _get("get_steam_username")
    validate_steam_directory = _get("validate_steam_directory")
    clear_steam_cache = _get("clear_steam_cache")
    detect_steam_path = _get("detect_steam_path")
    get_header_data = _get("get_header_data")
    force_header_refresh = _get("force_header_refresh")
    
    # Verificar disponibilidade crítica
    CRITICAL_FUNCTIONS_AVAILABLE = all([
        callable(get_steam_path),
        callable(is_steam_running),
        callable(get_steam_username)
    ])
    
    if not CRITICAL_FUNCTIONS_AVAILABLE:
        logger.error("❌ FUNÇÕES CRÍTICAS DO STEAM_UTILS NÃO DISPONÍVEIS!")
    else:
        logger.info("✅ Todas as funções críticas disponíveis")

    # ===================================================================
    # FUNÇÕES AUXILIARES ESPECÍFICAS
    # ===================================================================
    
    def format_file_size(size_bytes):
        """Formatar tamanho de arquivo para exibição"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        size = size_bytes
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.2f} {size_names[i]}"
    
    def get_dll_status_simple():
        """✅ VERIFICAÇÃO SIMPLIFICADA DA HID.DLL"""
        try:
            steam_path = get_steam_path() if callable(get_steam_path) else None
            if not steam_path:
                return {
                    "exists": False,
                    "valid": False,
                    "path": None,
                    "steam_found": False,
                    "size": 0
                }
            
            dll_path = Path(steam_path) / "hid.dll"
            exists = dll_path.exists()
            
            result = {
                "exists": exists,
                "steam_found": True,
                "path": str(dll_path)
            }
            
            if exists:
                try:
                    file_size = dll_path.stat().st_size
                    result["size"] = file_size
                    result["size_formatted"] = format_file_size(file_size)
                    # ✅ VERIFICAÇÃO SIMPLES: se existe e tem tamanho > 0
                    result["valid"] = file_size > 0
                except Exception as e:
                    result["valid"] = False
                    result["error"] = str(e)
            else:
                result["valid"] = False
                result["size"] = 0
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao verificar DLL: {e}")
            return {
                "exists": False,
                "valid": False,
                "steam_found": False,
                "error": str(e),
                "size": 0
            }
    
    def check_hid_dll_exists():
        """✅ FUNÇÃO RÁPIDA: Verifica apenas se a hid.dll existe"""
        try:
            steam_path = get_steam_path() if callable(get_steam_path) else None
            if not steam_path:
                return False
            
            dll_path = Path(steam_path) / "hid.dll"
            return dll_path.exists() and dll_path.stat().st_size > 0
        except:
            return False
    
    # ===================================================================
    # ✅ ROTAS PRINCIPAIS - FONTE ÚNICA DE VERDADE
    # ===================================================================

    # ================================================================
    # 1. ROTA PRINCIPAL DE USERNAME
    # ================================================================
    
    @app.route('/api/steam/user/username', methods=['GET'])
    def api_steam_user_username():
        """✅ ROTA PRINCIPAL: Obtém username do Steam"""
        try:
            if not callable(get_steam_username):
                return jsonify({
                    "success": False,
                    "error": "Função get_steam_username não disponível",
                    "username": "Jogador",
                    "detected": False
                })
            
            # Forçar atualização para dados frescos
            if callable(clear_steam_cache):
                clear_steam_cache()
            
            username = get_steam_username()
            
            return jsonify({
                "success": username is not None,
                "username": username or "Jogador",
                "detected": username is not None,
                "source": "steam_utils_definitivo",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[STEAM USERNAME] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "username": "Jogador",
                "detected": False
            })
    
    # ================================================================
    # 2. ROTA COMPLETA DE USER INFO (PARA SIDEBAR) - VERSÃO CORRIGIDA
    # ================================================================
    
    @app.route('/api/steam/user/full-info', methods=['GET'])
    def api_steam_user_full_info():
        """✅ ROTA COMPLETA CORRIGIDA: Informações do usuário para sidebar"""
        try:
            # ✅ USAR get_header_data QUE JÁ TEM TUDO PRONTO
            if callable(get_header_data):
                header_data = get_header_data()
                
                # ✅ GARANTIR QUE OS CAMPOS NECESSÁRIOS EXISTEM
                if isinstance(header_data, dict):
                    # Se dll_available não existe, verificar
                    if 'dll_available' not in header_data:
                        header_data['dll_available'] = check_hid_dll_exists()
                    
                    # Se greeting não existe, criar
                    if 'greeting' not in header_data:
                        hour = datetime.now().hour
                        if hour < 12:
                            header_data['greeting'] = "Bom dia"
                        elif hour < 18:
                            header_data['greeting'] = "Boa tarde"
                        else:
                            header_data['greeting'] = "Boa noite"
                    
                    return jsonify({
                        "success": True,
                        "user": header_data,
                        "source": "get_header_data",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # ✅ FALLBACK MANUAL SE get_header_data NÃO FUNCIONAR
            logger.warning("⚠️ Usando fallback manual para user info")
            
            steam_path = get_steam_path() if callable(get_steam_path) else None
            username = get_steam_username() if callable(get_steam_username) else None
            steam_running = is_steam_running() if callable(is_steam_running) else False
            
            # Saudação baseada no horário
            hour = datetime.now().hour
            if hour < 12:
                greeting = "Bom dia"
            elif hour < 18:
                greeting = "Boa tarde"
            else:
                greeting = "Boa noite"
            
            # Verificação DLL SIMPLIFICADA
            dll_available = False
            if steam_path:
                dll_path = Path(steam_path) / "hid.dll"
                dll_available = dll_path.exists() and dll_path.stat().st_size > 0
            
            user_data = {
                "username": username or "Jogador",
                "greeting": greeting,
                "steam_path": steam_path,
                "steam_running": steam_running,
                "dll_available": dll_available,
                "timestamp": datetime.now().isoformat(),
                "source": "manual_fallback"
            }
            
            return jsonify({
                "success": True,
                "user": user_data,
                "source": "manual_fallback",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[STEAM USER INFO] Erro: {e}")
            # ✅ FALLBACK DE EMERGÊNCIA
            return jsonify({
                "success": False,
                "error": str(e),
                "user": {
                    "username": "Jogador",
                    "greeting": "Olá",
                    "steam_running": False,
                    "dll_available": False,
                    "timestamp": datetime.now().isoformat(),
                    "source": "error_fallback"
                },
                "timestamp": datetime.now().isoformat()
            })
    
    # ================================================================
    # 3. ROTA DE STATUS DO SISTEMA (PARA SIDEBAR STATUS)
    # ================================================================
    
    @app.route('/api/steam/system/status', methods=['GET'])
    def api_steam_system_status():
        """✅ ROTA DE STATUS: Status completo do sistema Steam"""
        try:
            steam_path = get_steam_path() if callable(get_steam_path) else None
            steam_running = is_steam_running() if callable(is_steam_running) else False
            steam_valid = validate_steam_directory(steam_path) if callable(validate_steam_directory) and steam_path else False
            
            dll_status = get_dll_status_simple()
            
            return jsonify({
                "success": True,
                "system": {
                    "steam": {
                        "path": steam_path,
                        "running": steam_running,
                        "valid": steam_valid,
                        "found": steam_path is not None
                    },
                    "dll": dll_status,
                    "api": {
                        "available": CRITICAL_FUNCTIONS_AVAILABLE,
                        "status": "online" if CRITICAL_FUNCTIONS_AVAILABLE else "offline"
                    },
                    "cache": {
                        "status": "active",
                        "can_clear": callable(clear_steam_cache)
                    }
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[SYSTEM STATUS] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "system": {
                    "steam": {"path": None, "running": False, "valid": False, "found": False},
                    "dll": {"exists": False, "valid": False, "steam_found": False},
                    "api": {"available": False, "status": "error"},
                    "cache": {"status": "error", "can_clear": False}
                }
            })
    
    # ================================================================
    # 4. ROTA DE HEALTH CHECK
    # ================================================================
    
    @app.route('/api/steam/health', methods=['GET'])
    def api_steam_health():
        """✅ HEALTH CHECK: Verifica saúde do sistema Steam"""
        try:
            # Testar funções críticas
            tests = {
                "get_steam_path": callable(get_steam_path),
                "is_steam_running": callable(is_steam_running),
                "get_steam_username": callable(get_steam_username),
                "get_header_data": callable(get_header_data),
                "steam_path_found": get_steam_path() is not None if callable(get_steam_path) else False
            }
            
            all_ok = all(tests.values())
            
            return jsonify({
                "success": True,
                "service": "steam_api",
                "status": "healthy" if all_ok else "degraded",
                "tests": tests,
                "critical_functions_available": CRITICAL_FUNCTIONS_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[STEAM HEALTH] Erro: {e}")
            return jsonify({
                "success": False,
                "service": "steam_api",
                "status": "unhealthy",
                "error": str(e)
            })
    
    # ================================================================
    # 5. ROTA DE CONTROLE DO STEAM
    # ================================================================
    
    @app.route('/api/steam/control', methods=['POST'])
    def api_steam_control():
        """✅ CONTROLE: Iniciar/parar/reiniciar Steam"""
        try:
            data = request.get_json() or {}
            action = data.get("action", "").lower()

            if action == "start":
                if not callable(launch_steam):
                    return jsonify({"success": False, "error": "Função launch_steam não disponível"})
                ok = launch_steam()
                return jsonify({
                    "success": ok, 
                    "action": "started",
                    "message": "Steam iniciado" if ok else "Falha ao iniciar Steam"
                })

            elif action == "stop":
                if not callable(kill_steam):
                    return jsonify({"success": False, "error": "Função kill_steam não disponível"})
                ok = kill_steam()
                return jsonify({
                    "success": ok, 
                    "action": "stopped",
                    "message": "Steam encerrado" if ok else "Falha ao encerrar Steam"
                })

            elif action == "restart":
                if not callable(kill_steam) or not callable(launch_steam):
                    return jsonify({"success": False, "error": "Funções de controle não disponíveis"})
                
                ok1 = kill_steam()
                time.sleep(2)
                ok2 = launch_steam()
                
                return jsonify({
                    "success": ok1 and ok2, 
                    "action": "restarted",
                    "message": "Steam reiniciado" if (ok1 and ok2) else "Falha ao reiniciar Steam"
                })

            return jsonify({
                "success": False, 
                "error": "Ação inválida. Use: start, stop, restart"
            })
            
        except Exception as e:
            logger.error(f"[STEAM CONTROL] Erro: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    # ================================================================
    # 6. ROTA DE CACHE
    # ================================================================
    
    @app.route('/api/steam/clear-cache', methods=['POST'])
    def api_steam_clear_cache():
        """✅ CACHE: Limpar cache do Steam"""
        try:
            if not callable(clear_steam_cache):
                return jsonify({"success": False, "error": "Função indisponível"})
            clear_steam_cache()
            return jsonify({
                "success": True, 
                "message": "Cache do Steam limpo",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"[STEAM CLEAR CACHE] Erro: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    # ================================================================
    # 7. ROTA DE ATUALIZAÇÃO FORÇADA
    # ================================================================
    
    @app.route('/api/steam/user/refresh', methods=['POST'])
    def api_steam_user_refresh():
        """✅ REFRESH: Força atualização dos dados"""
        try:
            if callable(force_header_refresh):
                refreshed_data = force_header_refresh()
                return jsonify({
                    "success": True,
                    "message": "Dados atualizados com força",
                    "user": refreshed_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Se não tem force_header_refresh, limpa cache
            if callable(clear_steam_cache):
                clear_steam_cache()
            
            # Obtém dados atualizados
            return api_steam_user_full_info()
            
        except Exception as e:
            logger.error(f"[USER REFRESH] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Falha ao atualizar dados"
            })
    
    # ================================================================
    # 8. ROTA DE DEBUG USERNAME
    # ================================================================
    
    @app.route('/api/steam/debug/username', methods=['GET'])
    def api_steam_debug_username():
        """✅ DEBUG: Informações detalhadas do username"""
        try:
            if not callable(get_steam_username):
                return jsonify({
                    "success": False,
                    "error": "Função get_steam_username não disponível"
                })
            
            username = get_steam_username()
            steam_path = get_steam_path() if callable(get_steam_path) else None
            
            return jsonify({
                "success": True,
                "username": username,
                "found": username is not None,
                "steam_path": steam_path,
                "steam_running": is_steam_running() if callable(is_steam_running) else False,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[DEBUG USERNAME] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # ===================================================================
    # ✅✅✅ ROTAS DE FIXES LOCAIS (CRÍTICAS PARA O FIXES.HTML)
    # ===================================================================
    
    @app.route('/api/fixes/local/all', methods=['GET'])
    def api_fixes_local_all():
        """✅ ROTA CRÍTICA: Retorna todos os fixes locais do fixes_list.json"""
        try:
            if not FIX_MANAGER_AVAILABLE:
                return jsonify({
                    "success": False,
                    "error": "Fix Manager não disponível",
                    "games": [],
                    "count": 0
                })
            
            # Obter gerenciador de fixes
            manager = get_local_fixes_manager()
            
            # Verificar se foi carregado
            if not manager.loaded:
                return jsonify({
                    "success": False,
                    "error": "Arquivo fixes_list.json não carregado",
                    "games": [],
                    "count": 0
                })
            
            # Obter todos os fixes
            fixes = manager.get_all_fixes()
            
            # Formatar para o frontend (estrutura esperada pelo fixes.html)
            formatted_fixes = []
            for fix in fixes:
                # Extrair appid da URL se possível
                appid = 0
                url = fix.get("url", "")
                if url:
                    match = re.search(r'/(\d+)\.zip$', url)
                    if match:
                        appid = int(match.group(1))
                
                formatted_fixes.append({
                    "appid": appid,
                    "name": fix.get("name", "Fix Desconhecido"),
                    "fix_url": url,
                    "original_name": fix.get("original_name", fix.get("name", "Fix Desconhecido")),
                    "type": "native_fix",
                    "is_native": True,
                    "installed": False,
                    "has_fix": False,
                    "fixStatus": "available",
                    "source": "fixes_list.json"
                })
            
            logger.info(f"✅ Retornando {len(formatted_fixes)} fixes locais")
            
            return jsonify({
                "success": True,
                "games": formatted_fixes,  # ✅ CAMPO CORRETO: "games" (esperado pelo frontend)
                "count": len(formatted_fixes),
                "source": "fixes_list.json",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter fixes locais: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "games": [],
                "count": 0
            })
    
    @app.route('/api/fixes/local/search', methods=['GET'])
    def api_fixes_local_search():
        """✅ Busca fixes locais por query"""
        try:
            query = request.args.get('q', '')
            if not query or not FIX_MANAGER_AVAILABLE:
                return jsonify({
                    "success": True,
                    "results": [],
                    "count": 0,
                    "query": query
                })
            
            # Usar função de busca do fix_manager
            result = search_local_fixes(query)
            
            # Formatar resultados
            formatted_results = []
            for item in result.get("results", []):
                formatted_results.append({
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "normalized_name": item.get("normalized_name", ""),
                    "match_score": item.get("match_score", 0)
                })
            
            return jsonify({
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro na busca local: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            })
    
    @app.route('/api/fixes/local/stats', methods=['GET'])
    def api_fixes_local_stats():
        """✅ Estatísticas dos fixes locais"""
        try:
            if not FIX_MANAGER_AVAILABLE:
                return jsonify({
                    "success": False,
                    "error": "Fix Manager não disponível",
                    "stats": {}
                })
            
            manager = get_local_fixes_manager()
            
            return jsonify({
                "success": True,
                "stats": {
                    "loaded": manager.loaded,
                    "count": len(manager.fixes_map),
                    "sample": list(manager.fixes_map.keys())[:5] if manager.fixes_map else []
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro nas estatísticas: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "stats": {}
            })
    
    # ================================================================
    # 9. ROTAS DE COMPATIBILIDADE (MANTIDAS)
    # ================================================================
    
    @app.route('/api/header/status', methods=['GET'])
    def api_header_status_compat():
        """Rota de compatibilidade - redireciona para fonte única"""
        try:
            logger.info("📡 Rota /api/header/status chamada, redirecionando...")
            return api_steam_user_full_info()
            
        except Exception as e:
            logger.error(f"[HEADER COMPAT] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Falha no redirecionamento"
            })
    
    @app.route('/api/header/username', methods=['GET'])
    def api_header_username_compat():
        """Rota de compatibilidade - redireciona para fonte única"""
        try:
            logger.info("📡 Rota /api/header/username chamada, redirecionando...")
            return api_steam_user_username()
            
        except Exception as e:
            logger.error(f"[HEADER USERNAME COMPAT] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "username": "Jogador",
                "detected": False
            })
    
    @app.route('/api/steam/dll-status', methods=['GET'])
    def api_steam_dll_status():
        """✅ Status da DLL - SIMPLIFICADO"""
        try:
            dll_status = get_dll_status_simple()
            
            return jsonify({
                "success": True,
                "dll_status": dll_status,
                "exists": dll_status.get("exists", False),
                "valid": dll_status.get("valid", False),
                "steam_found": dll_status.get("steam_found", False),
                "path": dll_status.get("path"),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[DLL STATUS] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "dll_status": {
                    "exists": False,
                    "valid": False,
                    "steam_found": False
                }
            })
    
    @app.route('/api/steam/path', methods=['GET'])
    def api_steam_path():
        """Caminho do Steam - compatibilidade"""
        try:
            p = get_steam_path() if callable(get_steam_path) else None
            valid = validate_steam_directory(p) if callable(validate_steam_directory) and p else False

            return jsonify({
                "success": True,
                "path": p,
                "valid": valid,
                "exists": p and os.path.exists(p),
                "functions_available": CRITICAL_FUNCTIONS_AVAILABLE
            })
        except Exception as e:
            logger.error(f"[STEAM PATH] Erro: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    @app.route('/api/steam/status', methods=['GET'])
    def api_steam_status():
        """Status Steam - compatibilidade"""
        try:
            running = is_steam_running() if callable(is_steam_running) else False
            info = get_steam_info() if callable(get_steam_info) else {}

            return jsonify({
                "success": True,
                "running": running,
                "steam_info": info,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"[STEAM STATUS] Erro: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    # ================================================================
    # 10. ✅ NOVA ROTA: VERIFICAÇÃO RÁPIDA DE DLL (PARA SIDEBAR)
    # ================================================================
    
    @app.route('/api/steam/check-dll', methods=['GET'])
    def api_steam_check_dll():
        """✅ VERIFICAÇÃO RÁPIDA: Apenas se DLL existe"""
        try:
            dll_exists = check_hid_dll_exists()
            
            return jsonify({
                "success": True,
                "dll_exists": dll_exists,
                "message": "DLL encontrada" if dll_exists else "DLL não encontrada",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[CHECK DLL] Erro: {e}")
            return jsonify({
                "success": False,
                "dll_exists": False,
                "error": str(e)
            })
    
    # ================================================================
    # 11. ✅ NOVA ROTA: TESTE COMPLETO DO USERNAME
    # ================================================================
    
    @app.route('/api/steam/test-username', methods=['GET'])
    def api_steam_test_username():
        """✅ TESTE: Verifica extração de username passo a passo"""
        try:
            if not callable(get_steam_username):
                return jsonify({
                    "success": False,
                    "error": "Função get_steam_username não disponível"
                })
            
            # Limpar cache primeiro
            if callable(clear_steam_cache):
                clear_steam_cache()
            
            # Obter username
            username = get_steam_username()
            steam_path = get_steam_path() if callable(get_steam_path) else None
            
            # Verificar arquivo VDF
            vdf_exists = False
            vdf_path = None
            vdf_size = 0
            
            if steam_path:
                vdf_path = Path(steam_path) / "config" / "loginusers.vdf"
                vdf_exists = vdf_path.exists()
                if vdf_exists:
                    vdf_size = os.path.getsize(vdf_path)
            
            return jsonify({
                "success": True,
                "username": username,
                "found": username is not None,
                "steam_path": steam_path,
                "vdf_exists": vdf_exists,
                "vdf_path": str(vdf_path) if vdf_path else None,
                "vdf_size": vdf_size,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[TEST USERNAME] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # ================================================================
    # ✅ ROTA DE FALLBACK PARA /api/fixes/all (COMPATIBILIDADE)
    # ================================================================
    
    @app.route('/api/fixes/all', methods=['GET'])
    def api_fixes_all_compat():
        """Rota de compatibilidade para fixes.html (usando fixes locais)"""
        logger.info("🔄 Rota /api/fixes/all chamada, redirecionando para /api/fixes/local/all")
        return api_fixes_local_all()
    
    # ================================================================
    # LOG FINAL DE CONFIGURAÇÃO
    # ================================================================
    
    logger.info("✅✅✅ ROTAS STEAM DEFINITIVAS CONFIGURADAS COM SUCESSO!")
    logger.info("📊 Rotas principais disponíveis:")
    logger.info("   🔹 /api/steam/user/username      - Username único")
    logger.info("   🔹 /api/steam/user/full-info    - Info completa para sidebar")
    logger.info("   🔹 /api/steam/system/status     - Status do sistema")
    logger.info("   🔹 /api/steam/health            - Health check")
    logger.info("   🔹 /api/steam/control           - Controle do Steam")
    logger.info("   🔹 /api/steam/clear-cache       - Limpar cache")
    logger.info("   🔹 /api/steam/check-dll         - Verificação rápida DLL")
    logger.info("   🔹 /api/steam/test-username     - Teste de username")
    logger.info("   🔹 /api/header/status           - Compatibilidade")
    logger.info("   🔹 /api/header/username         - Compatibilidade")
    logger.info("   🔹 /api/fixes/local/all         - ✅ TODOS FIXES LOCAIS (CRÍTICO)")
    logger.info("   🔹 /api/fixes/local/search      - Busca em fixes locais")
    logger.info("   🔹 /api/fixes/local/stats       - Estatísticas fixes locais")
    logger.info("   🔹 /api/fixes/all              - Compatibilidade (redireciona)")
    
    return app