import os
import json
import logging
from pathlib import Path
from datetime import datetime, date
from flask import Flask, jsonify, request, send_file, render_template, abort, Response, redirect, send_from_directory

logger = logging.getLogger("routes")
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(h)

# HELPER FUNCTIONS

def make_json_safe(obj, _seen=None):
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

    if isinstance(obj, (datetime, date)):
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
    try:
        payload = json.dumps(make_json_safe(obj), ensure_ascii=False)
        return Response(payload, mimetype="application/json", status=status)
    except Exception as e:
        logger.error(f"Falha ao serializar JSON: {e}")
        return Response(
            json.dumps({"success": False, "error": "Falha ao serializar JSON"}),
            mimetype="application/json",
            status=500
        )

# MAIN ROUTES SETUP

def setup_all_routes(app: Flask, frontend_path: str, base_path: str, getattr_funcs: dict = None):
    """
    Configura TODAS as rotas NÃO-STEAM do sistema
    Rotas Steam estão em steam_routes.py (fonte única)
    Rotas Game Management (.lua) estão em game_routes.py (fonte única)
    """
    logger.info("🔧 CONFIGURAÇÃO DEFINITIVA: Rotas não-Steam (SEM redundâncias)...")
    logger.info("🎯 IMPORTANTE: Rotas de gerenciamento de jogos agora em game_routes.py")

    # INICIALIZAÇÃO DOS SISTEMAS NÃO-STEAM

    # 1. FIX MANAGER
    try:
        from utils.fix_manager import get_fix_manager
        fix_manager = get_fix_manager(None)
        FIX_MANAGER_AVAILABLE = True
        logger.info("✅ FixManager carregado")
    except Exception as e:
        FIX_MANAGER_AVAILABLE = False
        fix_manager = None
        logger.error(f"❌ FixManager erro: {e}")

    # 2. DLC MANAGER v9.0
    DLC_MANAGER = None
    try:
        from utils.dlc_manager import get_dlc_manager
        DLC_MANAGER = get_dlc_manager(None)
        DLC_MANAGER_AVAILABLE = True
        logger.info("✅ DLC Manager v9.0 carregado")
    except Exception as e:
        DLC_MANAGER_AVAILABLE = False
        DLC_MANAGER = None
        logger.error(f"❌ DLC Manager erro: {e}")

    # ❌❌❌ REMOVIDO COMPLETO: GAME MANAGEMENT (.lua)
    # TODAS as rotas de gerenciamento de jogos agora estão em game_routes.py
    # NÃO vamos mais importar ou configurar game_management aqui
    logger.info("🎮 GAME MANAGEMENT (.lua): Movido para game_routes.py (fonte única)")

    # HELPER FUNCTIONS INTERNAS

    def _safe_frontend(*parts):
        """Serve arquivos do frontend com segurança"""
        base = Path(frontend_path).resolve()
        file = (base.joinpath(*parts)).resolve()
        
        # Prevenir directory traversal
        if not str(file).startswith(str(base)):
            abort(404)
        if not file.exists():
            abort(404)
        return send_file(str(file))

    def _safe_send_html(filename):
        """Serve arquivos HTML específicos do frontend"""
        try:
            html_path = Path(frontend_path) / filename
            if html_path.exists():
                return send_file(str(html_path))
            else:
                # Fallback para arquivo na raiz do frontend
                return _safe_frontend(filename)
        except Exception as e:
            logger.error(f"Erro ao servir {filename}: {e}")
            abort(404)

    def _normalize_games(g):
        if g is None: return []
        if isinstance(g, list): return g
        if isinstance(g, dict): return list(g.values())
        return []

    # ROTAS DE PÁGINAS HTML (100% ESTÁTICAS) - SEM ROTAS STEAM

    # 🔥 CORREÇÃO: Redirecionar "/" para "/dashboard" (definitivo)
    @app.route("/")
    def root():
        logger.info("📍 Redirecionando '/' para '/dashboard'")
        return redirect("/dashboard")

    # ✅ ROTA /games (agora redireciona para game_management.html)
    @app.route("/games")
    def games_page():
        """Página do Game Manager - redireciona para arquivo estático"""
        try:
            logger.info("🎮 Servindo '/games' (página do Game Manager - estático)")
            return _safe_send_html("game_management.html")
        except Exception as e:
            logger.error(f"❌ Erro ao servir /games: {e}")
            return _safe_send_html("game_management.html")

    # ✅ ROTA /dlc
    @app.route("/dlc")
    def dlc_manager_page():
        """Página do DLC Manager"""
        try:
            logger.info("🧩 Servindo '/dlc' (página do DLC Manager)")
            return render_template("dlc_manager.html")
        except Exception as e:
            logger.error(f"❌ Erro ao servir /dlc: {e}")
            return _safe_send_html("dlc_manager.html")

    # ✅ ROTA /fixes
    @app.route("/fixes")
    def fixes_page():
        """Página do Fix Manager"""
        try:
            logger.info("🎯 Servindo '/fixes' (página do Fix Manager)")
            return render_template("fixes.html")
        except Exception as e:
            logger.error(f"❌ Erro ao servir /fixes: {e}")
            return _safe_send_html("fixes.html")

    # ✅ ROTA /search
    @app.route("/search")
    def search_main_page():
        """Página de busca principal"""
        try:
            logger.info("🔍 Servindo '/search' (página de busca principal)")
            return render_template("search.html")
        except Exception as e:
            logger.error(f"❌ Erro ao servir /search: {e}")
            return _safe_send_html("search.html")

    # ✅ ROTA /start (compatibilidade)
    @app.route("/start")
    def start_page():
        try:
            return render_template("start.html")
        except:
            return _safe_frontend("start.html")

    # ✅ ROTA /app (home principal)
    @app.route("/app")
    def app_main():
        """Home/Launcher principal"""
        try:
            logger.info("📍 Servindo '/app' (home/launcher - index.html)")
            return render_template("index.html")
        except:
            return _safe_frontend("index.html")

    # ✅ ROTA /dashboard (página principal)
    @app.route("/dashboard")
    def dashboard_page():
        """Dashboard como página principal"""
        try:
            logger.info("📊 Servindo '/dashboard' (dashboard.html)")
            return render_template("dashboard.html")
        except:
            return _safe_send_html("dashboard.html")

    # Rotas estáticas para arquivos HTML
    @app.route("/header.html")
    def serve_header():
        return _safe_send_html("header.html")

    @app.route("/sidebar.html")
    def serve_sidebar():
        return _safe_send_html("sidebar.html")

    @app.route("/dlc_manager.html")
    def serve_dlc_manager():
        return _safe_send_html("dlc_manager.html")

    @app.route("/footer.html")
    def serve_footer():
        return _safe_send_html("footer.html")

    @app.route("/search.html")
    def serve_search():
        return _safe_send_html("search.html")

    @app.route("/game_management.html")
    def serve_game_management():
        """Servir página de game management - arquivo estático"""
        return _safe_send_html("game_management.html")

    @app.route("/fixes.html")
    def serve_fixes():
        return _safe_send_html("fixes.html")

    @app.route("/favicon.ico")
    def favicon():
        return _safe_frontend("favicon.ico")

    # Rotas para assets
    @app.route("/css/<path:f>")
    def css(f): 
        return _safe_frontend("css", f)

    @app.route("/js/<path:f>")
    def js(f): 
        return _safe_frontend("js", f)

    @app.route("/assets/<path:f>")
    def assets(f): 
        return _safe_frontend("assets", f)

    # ROTA DE STATUS GLOBAL - SEM INFORMAÇÕES STEAM
    
    @app.route("/api/status")
    def api_status():
        """✅ Status simplificado - APENAS sistemas não-Steam"""
        return safe_jsonify({
            "success": True,
            "systems": {
                "fix": FIX_MANAGER_AVAILABLE,
                "dlc": DLC_MANAGER_AVAILABLE,
                "game_routes": {
                    "available": "consulte game_routes.py",
                    "note": "Rotas de gerenciamento de jogos agora em game_routes.py"
                },
                "steam": {
                    "available": "consulte /api/steam/health (em steam_routes.py)",
                    "note": "Todas as rotas Steam estão em steam_routes.py"
                }
            },
            "timestamp": datetime.now().isoformat(),
            "important_notes": [
                "✅ ROTAS STEAM MOVIDAS PARA steam_routes.py (fonte única)",
                "✅ ROTAS GAME MANAGEMENT MOVIDAS PARA game_routes.py (fonte única)",
                "✅ Este arquivo contém apenas rotas Fix, DLC e páginas estáticas"
            ]
        })

    # DETECÇÃO DE JOGOS INSTALADOS (VIA DLC MANAGER) - SOMENTE DLC

    @app.route("/api/games/installed")
    def api_games_installed():
        """⚠️ ROTA DEPRECIADA: Redireciona para API DLC"""
        logger.warning("⚠️ ROTA /api/games/installed chamada - Redirecionando para DLC Manager...")
        
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({
                "success": False, 
                "error": "DLCManager indisponível",
                "note": "Use /api/dlc/games para jogos com DLC"
            })

        try:
            force = request.args.get("force", "").lower() in ("1", "true")
            result = DLC_MANAGER.get_installed_games(force_refresh=force)

            if not result.get("success"):
                return safe_jsonify({"success": False, "error": result.get("error")})

            games = _normalize_games(result.get("games"))

            for g in games:
                g["type"] = "steam"
                g["installed"] = True

            return safe_jsonify({
                "success": True, 
                "games": games,
                "source": "dlc_manager",
                "note": "Para jogos .lua, use game_routes.py (rotas em /api/games/*)"
            })

        except Exception as e:
            logger.error(f"Erro instalados: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    # FIX MANAGER - ROTAS COMPLETAS (NÃO-STEAM)

    @app.route("/api/fixes/check/<appid>")
    def api_check_fix(appid):
        if not FIX_MANAGER_AVAILABLE:
            return safe_jsonify({"success": False, "error": "FixManager indisponível"})
        try:
            return safe_jsonify(fix_manager.check_game_fixes(int(appid)))
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/fixes/apply", methods=["POST"])
    def api_apply_fix():
        if not FIX_MANAGER_AVAILABLE:
            return safe_jsonify({"success": False, "error": "FixManager indisponível"})
        try:
            data = request.get_json() or {}
            appid = data.get("appid")
            fix_type = data.get("fix_type", "auto")
            if not appid:
                return safe_jsonify({"success": False, "error": "AppID não fornecido"}, 400)
            return safe_jsonify(fix_manager.apply_fix(int(appid), fix_type))
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/fixes/remove/<appid>", methods=["POST"])
    def api_remove_fix(appid):
        if not FIX_MANAGER_AVAILABLE:
            return safe_jsonify({"success": False, "error": "FixManager indisponível"})
        try:
            return safe_jsonify(fix_manager.remove_fix(int(appid)))
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/fixes/apply-status/<appid>")
    def api_fix_apply_status(appid):
        """Status da aplicação de fix"""
        if not FIX_MANAGER_AVAILABLE:
            return safe_jsonify({"success": False, "error": "FixManager indisponível"})
        try:
            from utils.fix_manager import get_apply_fix_status
            return safe_jsonify(get_apply_fix_status(int(appid)))
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/fixes/remove-status/<appid>")
    def api_fix_remove_status(appid):
        """Status da remoção de fix"""
        if not FIX_MANAGER_AVAILABLE:
            return safe_jsonify({"success": False, "error": "FixManager indisponível"})
        try:
            from utils.fix_manager import get_unfix_status
            return safe_jsonify(get_unfix_status(int(appid)))
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/fixes/system-status")
    def api_fixes_system_status():
        """Status do sistema de fixes"""
        try:
            if not FIX_MANAGER_AVAILABLE or not fix_manager:
                return safe_jsonify({"success": False, "error": "FixManager indisponível"})
            
            report = fix_manager.get_system_report() if hasattr(fix_manager, 'get_system_report') else {}
            
            return safe_jsonify({
                "success": True,
                "status": "online",
                "report": report,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Erro no status do sistema de fixes: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/fixes/cancel/<appid>", methods=["POST"])
    def api_cancel_fix(appid):
        """Cancelar operação de fix"""
        if not FIX_MANAGER_AVAILABLE:
            return safe_jsonify({"success": False, "error": "FixManager indisponível"})
        try:
            return safe_jsonify(fix_manager.cancel_fix_operation(int(appid)))
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)})

    # DLC MANAGER v9.0 - ROTAS COMPLETAS (NÃO-STEAM)

    @app.route("/api/dlc/status", methods=["GET"])
    def api_dlc_status():
        """Status do DLC Manager v9.0"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            status = DLC_MANAGER.get_status()
            return safe_jsonify(status)
        except Exception as e:
            logger.error(f"Erro no status do DLC: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/games")
    def api_dlc_games():
        """Retorna todos os jogos instalados (com dados DLC)"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            force = request.args.get("refresh", "false").lower() == "true"
            result = DLC_MANAGER.get_installed_games(force_refresh=force)
            return safe_jsonify(result)
        except Exception as e:
            logger.error(f"Erro ao listar jogos DLC: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/<appid>/list", methods=["GET"])
    def api_dlc_list(appid):
        """Lista DLCs disponíveis para um jogo"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            force_refresh = request.args.get("refresh", "false").lower() == "true"
            dlcs = DLC_MANAGER.get_game_dlcs(appid, force_refresh=force_refresh)
            
            installed_dlcs = DLC_MANAGER.get_installed_dlcs(appid)
            
            for dlc in dlcs:
                dlc_id = dlc.get("id") or dlc.get("appid")
                dlc["installed"] = dlc_id in installed_dlcs
            
            return safe_jsonify({
                "success": True,
                "appid": appid,
                "available_dlcs": dlcs,
                "installed_dlcs": installed_dlcs,
                "total_available": len(dlcs),
                "total_installed": len(installed_dlcs)
            })
        except Exception as e:
            logger.error(f"Erro ao listar DLCs para {appid}: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/<appid>/install", methods=["POST"])
    def api_dlc_install(appid):
        """Instala DLCs para um jogo"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            data = request.get_json() or {}
            dlc_ids = data.get("dlc_ids", [])
            
            if not dlc_ids:
                return safe_jsonify({
                    "success": False,
                    "error": "Nenhuma DLC especificada para instalação"
                })
            
            result = DLC_MANAGER.install_dlcs(appid, dlc_ids)
            
            if result.get("success"):
                logger.info(f"DLCs instaladas para {appid}: {result.get('dlcs_added', [])}")
            
            return safe_jsonify(result)
        except Exception as e:
            logger.error(f"Erro ao instalar DLCs para {appid}: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/<appid>/uninstall", methods=["POST"])
    def api_dlc_uninstall(appid):
        """Remove DLCs de um jogo"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            data = request.get_json() or {}
            dlc_ids = data.get("dlc_ids", [])
            
            if not dlc_ids:
                installed_dlcs = DLC_MANAGER.get_installed_dlcs(appid)
                dlc_ids = installed_dlcs
            
            if not dlc_ids:
                return safe_jsonify({
                    "success": True,
                    "message": "Nenhuma DLC instalada para este jogo",
                    "removed": 0
                })
            
            stplug_path = DLC_MANAGER._get_stplug()
            if not stplug_path:
                return safe_jsonify({
                    "success": False,
                    "error": "stplug-in não encontrado"
                })
            
            steamtools_path = stplug_path / "Steamtools.lua"
            if not steamtools_path.exists():
                return safe_jsonify({
                    "success": True,
                    "message": "Nenhuma DLC instalada (arquivo não existe)",
                    "removed": 0
                })
            
            with open(steamtools_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            removed_count = 0
            
            for line in lines:
                line_stripped = line.strip()
                should_keep = True
                
                for dlc_id in dlc_ids:
                    if f"addappid({dlc_id}" in line_stripped.replace(" ", ""):
                        should_keep = False
                        removed_count += 1
                        break
                
                if should_keep:
                    new_lines.append(line)
            
            with open(steamtools_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            DLC_MANAGER.dlc_cache.pop(appid, None)
            DLC_MANAGER.games_cache.pop("games", None)
            
            return safe_jsonify({
                "success": True,
                "message": f"{removed_count} DLC(s) removida(s)",
                "removed": removed_count,
                "dlcs_removed": dlc_ids if removed_count > 0 else []
            })
            
        except Exception as e:
            logger.error(f"Erro ao remover DLCs de {appid}: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/search", methods=["GET"])
    def api_dlc_search():
        """Busca jogos no DLC Manager"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            query = request.args.get('q', '').lower().strip()
            
            if not query:
                return safe_jsonify({
                    "success": False,
                    "error": "Termo de busca não fornecido"
                })
            
            games_result = DLC_MANAGER.get_installed_games()
            
            if not games_result.get("success"):
                return safe_jsonify(games_result)
            
            games = games_result.get("games", [])
            
            filtered_games = []
            for game in games:
                if query in game.get("name", "").lower():
                    filtered_games.append(game)
                elif query == str(game.get("appid", "")):
                    filtered_games.append(game)
                elif query in game.get("install_path", "").lower():
                    filtered_games.append(game)
            
            return safe_jsonify({
                "success": True,
                "query": query,
                "games": filtered_games,
                "count": len(filtered_games)
            })
            
        except Exception as e:
            logger.error(f"Erro na busca DLC: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/cache/clear", methods=["POST"])
    def api_dlc_cache_clear():
        """Limpa cache do DLC Manager"""
        if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
            return safe_jsonify({"success": False, "error": "DLCManager indisponível"})
        try:
            with DLC_MANAGER._lock:
                DLC_MANAGER.dlc_cache.clear()
                DLC_MANAGER.games_cache.clear()
            
            logger.info("Cache do DLC Manager limpo")
            
            return safe_jsonify({
                "success": True,
                "message": "Cache do DLC Manager limpo",
                "dlc_cache_cleared": True,
                "games_cache_cleared": True
            })
        except Exception as e:
            logger.error(f"Erro ao limpar cache DLC: {e}")
            return safe_jsonify({"success": False, "error": str(e)})

    @app.route("/api/dlc/health", methods=["GET"])
    def api_dlc_health():
        """Health check do DLC Manager"""
        try:
            if not DLC_MANAGER_AVAILABLE or not DLC_MANAGER:
                return safe_jsonify({
                    "success": False,
                    "service": "dlc_manager",
                    "status": "unhealthy",
                    "error": "DLCManager não disponível"
                })
            
            status = DLC_MANAGER.get_status()
            
            return safe_jsonify({
                "success": True,
                "service": "dlc_manager",
                "status": "healthy",
                "version": "v9.0",
                "steam_path": status.get("steam_path"),
                "stplug-in_exists": bool(status.get("stplug-in")),
                "total_games": status.get("total_games", 0),
                "games_with_dlc": status.get("games_with_dlc", 0),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            return safe_jsonify({
                "success": False,
                "service": "dlc_manager",
                "status": "unhealthy",
                "error": str(e),
                "version": "v9.0"
            })

    # ROTA DE COMPATIBILIDADE - REDIRECIONA PARA STEAM_ROUTES.PY
    
    @app.route("/api/system/status")
    def api_system_status():
        """⚠️ ROTA DE COMPATIBILIDADE - Redireciona para steam_routes.py"""
        try:
            logger.warning("⚠️ ROTA /api/system/status chamada - Redirecionando para steam_routes.py...")
            
            # Esta rota não deve mais existir aqui
            # Todas as rotas Steam estão em steam_routes.py
            return safe_jsonify({
                "success": False,
                "error": "ROTA MOVIDA PARA STEAM_ROUTES.PY",
                "message": "Esta rota agora está em steam_routes.py. Use:",
                "alternatives": {
                    "steam_system_status": "/api/steam/system/status",
                    "non_steam_status": "/api/status (apenas sistemas não-Steam)",
                    "steam_health": "/api/steam/health",
                    "steam_user_info": "/api/steam/user/full-info"
                },
                "important_notes": [
                    "✅ Todas as rotas Steam agora estão em steam_routes.py",
                    "✅ Este arquivo contém apenas rotas Fix, DLC e páginas estáticas"
                ]
            })
            
        except Exception as e:
            return safe_jsonify({"success": False, "error": str(e)}, 500)

    # ROTA DE REDIRECIONAMENTO PARA GAME MANAGEMENT (GAME_ROUTES.PY)
    
    @app.route("/api/games/<path:path>")
    def api_games_redirect(path):
        """⚠️ REDIRECIONA todas as rotas /api/games/* para game_routes.py"""
        logger.warning(f"⚠️ ROTA /api/games/{path} chamada no routes.py - Deveria estar em game_routes.py")
        
        return safe_jsonify({
            "success": False,
            "error": "ROTA NO LOCAL ERRADO",
            "message": f"Rota /api/games/{path} deveria ser tratada por game_routes.py",
            "action_required": "Certifique-se que game_routes.py está configurado no main.py",
            "current_configuration": {
                "game_routes_available": getattr_funcs.get("GAME_ROUTES_AVAILABLE", False) if getattr_funcs else "unknown",
                "note": "Configure game_routes.py no main.py usando setup_game_routes()"
            }
        })
    

    # ===================================================================
    # LOG FINAL DE CONFIGURAÇÃO
    # ===================================================================

    logger.info("✅✅✅ ROTAS NÃO-STEAM CONFIGURADAS COM SUCESSO!")
    logger.info("📊 Sistemas carregados (APENAS não-Steam):")
    logger.info("   🔹 Fix Manager: " + ("✅" if FIX_MANAGER_AVAILABLE else "❌"))
    logger.info("   🔹 DLC Manager v9.0: " + ("✅" if DLC_MANAGER_AVAILABLE else "❌"))
    logger.info("   🔹 Game Management (.lua): ❌ REMOVIDO (agora em game_routes.py)")
    logger.info("📡 Fontes únicas configuradas:")
    logger.info("   🔹 Rotas Steam: steam_routes.py (fonte única)")
    logger.info("   🔹 Rotas Game Management: game_routes.py (fonte única)")
    logger.info("   🔹 Este arquivo: APENAS Fix, DLC e páginas estáticas")
    logger.info("✅ ARQUITETURA CORRIGIDA: Sem redundâncias, sem duplicações de rotas Steam!")
    logger.info("🎯 Sidebar deve usar: /api/steam/user/full-info (em steam_routes.py)")

    return app