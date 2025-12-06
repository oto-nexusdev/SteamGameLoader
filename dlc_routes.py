# dlc_routes.py - ROTAS PARA DLC MANAGER v9.0

import logging
from flask import Flask, request, jsonify
from utils.dlc_manager import get_dlc_manager

logger = logging.getLogger("DLC_Routes")
logger.setLevel(logging.INFO)

def setup_dlc_routes(app: Flask):
    """Configura todas as rotas para o DLC Manager"""
    
    logger.info("🔧 Configurando rotas DLC Manager...")
    
    # ========== ROTAS DE STATUS ==========
    
    @app.route('/api/dlc/status', methods=['GET'])
    def api_dlc_status():
        """Retorna status completo do DLC Manager"""
        try:
            dlc_mgr = get_dlc_manager()
            status = dlc_mgr.get_status()
            return jsonify(status)
        except Exception as e:
            logger.error(f"[DLC STATUS] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "version": "DLCManager v9.0"
            })
    
    # ========== ROTAS DE JOGOS ==========
    
    @app.route('/api/dlc/games', methods=['GET'])
    def api_dlc_games():
        """Retorna todos os jogos instalados"""
        try:
            dlc_mgr = get_dlc_manager()
            force_refresh = request.args.get('refresh', 'false').lower() == 'true'
            
            result = dlc_mgr.get_installed_games(force_refresh=force_refresh)
            return jsonify(result)
        except Exception as e:
            logger.error(f"[DLC GAMES] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "games": []
            })
    
    @app.route('/api/dlc/games/<appid>', methods=['GET'])
    def api_dlc_game_detail(appid):
        """Retorna detalhes de um jogo específico"""
        try:
            dlc_mgr = get_dlc_manager()
            
            # Obter lista de jogos
            games_result = dlc_mgr.get_installed_games()
            if not games_result.get("success"):
                return jsonify(games_result)
            
            # Encontrar jogo específico
            game = games_result.get("games_by_appid", {}).get(str(appid))
            if not game:
                return jsonify({
                    "success": False,
                    "error": f"Jogo com AppID {appid} não encontrado"
                })
            
            # Adicionar DLCs instaladas
            installed_dlcs = dlc_mgr.get_installed_dlcs(appid)
            game["installed_dlcs"] = installed_dlcs
            game["installed_dlcs_count"] = len(installed_dlcs)
            
            return jsonify({
                "success": True,
                "game": game
            })
        except Exception as e:
            logger.error(f"[DLC GAME DETAIL] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # ========== ROTAS DE DLCs ==========
    
    @app.route('/api/dlc/<appid>/list', methods=['GET'])
    def api_dlc_list(appid):
        """Lista todas as DLCs disponíveis para um jogo"""
        try:
            dlc_mgr = get_dlc_manager()
            force_refresh = request.args.get('refresh', 'false').lower() == 'true'
            
            # Obter DLCs disponíveis
            available_dlcs = dlc_mgr.list_dlcs(appid)
            
            # Obter DLCs já instaladas
            installed_dlcs = dlc_mgr.get_installed_dlcs(appid)
            
            # Marcar quais estão instaladas
            for dlc in available_dlcs:
                dlc["installed"] = dlc.get("id") in installed_dlcs or dlc.get("appid") in installed_dlcs
            
            return jsonify({
                "success": True,
                "appid": appid,
                "available_dlcs": available_dlcs,
                "installed_dlcs": installed_dlcs,
                "total_available": len(available_dlcs),
                "total_installed": len(installed_dlcs)
            })
        except Exception as e:
            logger.error(f"[DLC LIST] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "appid": appid,
                "available_dlcs": [],
                "installed_dlcs": []
            })
    
    # ========== ROTAS DE INSTALAÇÃO ==========
    
    @app.route('/api/dlc/<appid>/install', methods=['POST'])
    def api_dlc_install(appid):
        """Instala DLCs para um jogo"""
        try:
            data = request.get_json() or {}
            dlc_ids = data.get('dlc_ids', [])
            
            if not dlc_ids:
                return jsonify({
                    "success": False,
                    "error": "Nenhuma DLC especificada para instalação"
                })
            
            dlc_mgr = get_dlc_manager()
            result = dlc_mgr.install_dlcs(appid, dlc_ids)
            
            # Registrar no log
            if result.get("success"):
                logger.info(f"DLCs instaladas para {appid}: {result.get('dlcs_added', [])}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"[DLC INSTALL] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    @app.route('/api/dlc/<appid>/uninstall', methods=['POST'])
    def api_dlc_uninstall(appid):
        """Remove DLCs de um jogo (limpa Steamtools.lua)"""
        try:
            dlc_mgr = get_dlc_manager()
            
            # Obter DLCs instaladas atualmente
            installed_dlcs = dlc_mgr.get_installed_dlcs(appid)
            
            if not installed_dlcs:
                return jsonify({
                    "success": True,
                    "message": "Nenhuma DLC instalada para este jogo",
                    "removed": 0
                })
            
            data = request.get_json() or {}
            dlc_ids_to_remove = data.get('dlc_ids', [])
            
            # Se nenhuma especificada, remove todas deste jogo
            if not dlc_ids_to_remove:
                dlc_ids_to_remove = installed_dlcs
            
            # Obter caminho do stplug-in
            stplug_path = dlc_mgr._get_stplug()
            if not stplug_path:
                return jsonify({
                    "success": False,
                    "error": "stplug-in não encontrado"
                })
            
            import os
            from pathlib import Path
            
            steamtools_path = stplug_path / "Steamtools.lua"
            if not steamtools_path.exists():
                return jsonify({
                    "success": True,
                    "message": "Nenhuma DLC instalada (arquivo não existe)",
                    "removed": 0
                })
            
            # Ler arquivo e remover DLCs
            with open(steamtools_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            removed_count = 0
            
            for line in lines:
                line_stripped = line.strip()
                should_keep = True
                
                # Verificar se é uma linha de DLC para este appid
                for dlc_id in dlc_ids_to_remove:
                    if f"addappid({dlc_id}" in line_stripped.replace(" ", ""):
                        should_keep = False
                        removed_count += 1
                        break
                
                if should_keep:
                    new_lines.append(line)
            
            # Salvar arquivo atualizado
            with open(steamtools_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            # Limpar caches
            dlc_mgr.dlc_cache.pop(appid, None)
            dlc_mgr.games_cache.pop("games", None)
            
            return jsonify({
                "success": True,
                "message": f"{removed_count} DLC(s) removida(s)",
                "removed": removed_count,
                "dlcs_removed": dlc_ids_to_remove if removed_count > 0 else []
            })
            
        except Exception as e:
            logger.error(f"[DLC UNINSTALL] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # ========== ROTAS DE BUSCA ==========
    
    @app.route('/api/dlc/search', methods=['GET'])
    def api_dlc_search():
        """Busca jogos por nome ou appid"""
        try:
            query = request.args.get('q', '').lower().strip()
            
            if not query:
                return jsonify({
                    "success": False,
                    "error": "Termo de busca não fornecido"
                })
            
            dlc_mgr = get_dlc_manager()
            games_result = dlc_mgr.get_installed_games()
            
            if not games_result.get("success"):
                return jsonify(games_result)
            
            games = games_result.get("games", [])
            
            # Filtrar jogos
            filtered_games = []
            for game in games:
                # Busca por nome
                if query in game.get("name", "").lower():
                    filtered_games.append(game)
                # Busca por appid
                elif query == str(game.get("appid", "")):
                    filtered_games.append(game)
                # Busca por caminho
                elif query in game.get("install_path", "").lower():
                    filtered_games.append(game)
            
            return jsonify({
                "success": True,
                "query": query,
                "games": filtered_games,
                "count": len(filtered_games)
            })
            
        except Exception as e:
            logger.error(f"[DLC SEARCH] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "games": []
            })
    
    # ========== ROTAS DE CACHE ==========
    
    @app.route('/api/dlc/cache/clear', methods=['POST'])
    def api_dlc_cache_clear():
        """Limpa o cache do DLC Manager"""
        try:
            dlc_mgr = get_dlc_manager()
            
            with dlc_mgr._lock:
                dlc_mgr.dlc_cache.clear()
                dlc_mgr.games_cache.clear()
            
            logger.info("Cache do DLC Manager limpo")
            
            return jsonify({
                "success": True,
                "message": "Cache do DLC Manager limpo",
                "dlc_cache_cleared": True,
                "games_cache_cleared": True
            })
        except Exception as e:
            logger.error(f"[DLC CACHE CLEAR] Erro: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            })
    
    # ========== ROTA DE HEALTH CHECK ==========
    
    @app.route('/api/dlc/health', methods=['GET'])
    def api_dlc_health():
        """Health check do DLC Manager"""
        try:
            dlc_mgr = get_dlc_manager()
            status = dlc_mgr.get_status()
            
            return jsonify({
                "success": True,
                "service": "dlc_manager",
                "status": "healthy",
                "version": "v9.0",
                "steam_path": status.get("steam_path"),
                "stplug-in_exists": bool(status.get("stplug-in")),
                "total_games": status.get("total_games", 0),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "service": "dlc_manager",
                "status": "unhealthy",
                "error": str(e),
                "version": "v9.0"
            })
    
    logger.info("✅ Rotas DLC Manager configuradas com sucesso")
    return app