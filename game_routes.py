# utils/game_routes.py - ROTAS DE INTEGRAÇÃO PARA GAME_MANAGEMENT.PY
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import sys
import os

# Adicionar caminho para importar game_management
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger("game_routes")

# ===================================================================
# CONFIGURAÇÃO DAS ROTAS
# ===================================================================

def setup_game_routes(app: Flask, steam_utils_funcs: dict):
    """Configura rotas de gerenciamento de jogos - VERSÃO CORRIGIDA"""
    logger.info("🔧 CONFIGURAÇÃO: Rotas de Game Management CORRIGIDAS...")
    
    # ===================================================================
    # IMPORTAÇÃO DINÂMICA DO SISTEMA CORRETO
    # ===================================================================
    
    try:
        # Importar o sistema CORRETO de game_management
        from utils.game_management import create_game_manager
        
        # Função helper para obter steam path
        def get_steam_path():
            get_path_func = steam_utils_funcs.get("get_steam_path")
            if callable(get_path_func):
                return get_path_func()
            return None
        
        # Criar instância do gerenciador
        game_manager = None
        steam_path = get_steam_path()
        if steam_path:
            game_manager = create_game_manager(steam_path)
            logger.info(f"🎮 GameManager inicializado com Steam path: {steam_path}")
        
        # ===================================================================
        # ROTAS CORRETAS DE GERENCIAMENTO DE JOGOS
        # ===================================================================
        
        @app.route('/api/games/detect', methods=['POST'])
        def api_games_detect():
            """✅ ROTA CORRIGIDA: Detecta jogos .lua no Steam/config/stplug-in/"""
            try:
                data = request.get_json() or {}
                fetch_names = data.get("fetch_names", True)
                
                # Obter caminho do Steam
                steam_path = data.get("steam_path")
                if not steam_path:
                    steam_path = get_steam_path()
                
                if not steam_path:
                    return jsonify({
                        "success": False,
                        "error": "Caminho do Steam não encontrado",
                        "games": [],
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Criar gerenciador com o caminho
                manager = create_game_manager(steam_path)
                
                # Detectar jogos usando o sistema CORRETO
                result = manager.detect_games(fetch_names=fetch_names)
                
                return jsonify({
                    "success": result["success"],
                    "games": result.get("games", []),
                    "total_games": result.get("total_games", 0),
                    "total_size": result.get("total_size", 0),
                    "processing_time": result.get("processing_time", "0s"),
                    "message": result.get("message", ""),
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"[GAMES DETECT] Erro: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "games": [],
                    "timestamp": datetime.now().isoformat()
                })
        
        @app.route('/api/games/refresh/<appid>', methods=['POST'])
        def api_games_refresh(appid):
            """✅ ROTA CORRIGIDA: Atualiza nome do jogo usando Steam API"""
            try:
                # Obter caminho do Steam
                steam_path = get_steam_path()
                if not steam_path:
                    return jsonify({
                        "success": False,
                        "appid": appid,
                        "error": "Caminho do Steam não encontrado",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Criar gerenciador
                manager = create_game_manager(steam_path)
                
                # Atualizar dados do jogo
                game = manager.refresh_game_data(appid)
                
                if game:
                    return jsonify({
                        "success": True,
                        "appid": appid,
                        "game": game,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        "success": False,
                        "appid": appid,
                        "error": "Jogo não encontrado ou erro na atualização",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"[GAMES REFRESH] Erro: {e}")
                return jsonify({
                    "success": False,
                    "appid": appid,
                    "error": str(e)
                })
        
        @app.route('/api/games/backup', methods=['POST'])
        def api_games_backup():
            """✅ ROTA CORRIGIDA: Faz backup de jogos selecionados"""
            try:
                data = request.get_json() or {}
                games = data.get("games", [])
                backup_dir = data.get("backup_dir")
                
                if not games:
                    return jsonify({
                        "success": False,
                        "error": "Nenhum jogo fornecido para backup",
                        "message": "Nenhum jogo selecionado"
                    })
                
                # Obter caminho do Steam
                steam_path = get_steam_path()
                if not steam_path:
                    return jsonify({
                        "success": False,
                        "error": "Caminho do Steam não encontrado"
                    })
                
                # Criar gerenciador
                manager = create_game_manager(steam_path)
                
                # Fazer backup usando o sistema CORRETO
                result = manager.backup_games(games, backup_dir)
                
                return jsonify({
                    "success": result["success"],
                    "message": result.get("message", ""),
                    "backup_path": result.get("backup_path"),
                    "success_count": result.get("success_count", 0),
                    "total_count": result.get("total_count", 0),
                    "failed_count": result.get("failed_count", 0),
                    "failed_games": result.get("failed_games", []),
                    "report_file": result.get("report_file"),
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"[GAMES BACKUP] Erro: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        
        @app.route('/api/games/remove', methods=['POST'])
        def api_games_remove():
            """✅ ROTA CORRIGIDA: Remove jogos selecionados"""
            try:
                data = request.get_json() or {}
                games = data.get("games", [])
                
                if not games:
                    return jsonify({
                        "success": False,
                        "error": "Nenhum jogo fornecido para remoção",
                        "message": "Nenhum jogo selecionado"
                    })
                
                # Obter caminho do Steam
                steam_path = get_steam_path()
                if not steam_path:
                    return jsonify({
                        "success": False,
                        "error": "Caminho do Steam não encontrado"
                    })
                
                # Criar gerenciador
                manager = create_game_manager(steam_path)
                
                # Remover jogos usando o sistema CORRETO
                result = manager.remove_games(games)
                
                return jsonify({
                    "success": result["success"],
                    "message": result.get("message", ""),
                    "removed_count": result.get("removed_count", 0),
                    "total_count": result.get("total_count", 0),
                    "failed_count": result.get("failed_count", 0),
                    "failed_games": result.get("failed_games", []),
                    "backup_dir": result.get("backup_dir"),
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"[GAMES REMOVE] Erro: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        
        # ===================================================================
        # ROTAS ADICIONAIS CORRETAS
        # ===================================================================
        
        @app.route('/api/games/status', methods=['GET'])
        def api_games_status():
            """Status do sistema de gerenciamento de jogos"""
            try:
                steam_path = get_steam_path()
                
                if steam_path:
                    # Validar se o caminho é adequado para jogos .lua
                    from utils.game_management import validate_steam_path_for_games
                    validation = validate_steam_path_for_games(steam_path)
                    
                    return jsonify({
                        "success": True,
                        "system": {
                            "steam_path": steam_path,
                            "steam_exists": steam_path is not None,
                            "game_routes_available": True,
                            "stplug_in_exists": validation.get("has_stplugin_dir", False),
                            "lua_files_count": validation.get("lua_files_count", 0),
                            "timestamp": datetime.now().isoformat()
                        },
                        "validation": validation
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Steam path não disponível",
                        "system": {
                            "steam_path": None,
                            "steam_exists": False,
                            "game_routes_available": True,
                            "timestamp": datetime.now().isoformat()
                        }
                    })
                    
            except Exception as e:
                logger.error(f"[GAMES STATUS] Erro: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        
        @app.route('/api/games/validate-path', methods=['POST'])
        def api_games_validate_path():
            """Valida se o caminho do Steam é adequado para jogos .lua"""
            try:
                data = request.get_json() or {}
                steam_path = data.get("steam_path")
                
                if not steam_path:
                    steam_path = get_steam_path()
                
                from utils.game_management import validate_steam_path_for_games
                validation = validate_steam_path_for_games(steam_path)
                
                return jsonify({
                    "success": True,
                    "validation": validation,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"[GAMES VALIDATE PATH] Erro: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        
        @app.route('/api/games/statistics', methods=['GET'])
        def api_games_statistics():
            """Estatísticas dos jogos detectados"""
            try:
                steam_path = get_steam_path()
                if not steam_path:
                    return jsonify({
                        "success": False,
                        "error": "Steam path não encontrado"
                    })
                
                manager = create_game_manager(steam_path)
                stats = manager.get_statistics()
                
                return jsonify({
                    "success": True,
                    "statistics": stats,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"[GAMES STATISTICS] Erro: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        
        logger.info("✅✅✅ ROTAS GAME MANAGEMENT CORRIGIDAS COM SUCESSO!")
        logger.info("📊 Rotas CORRETAS disponíveis:")
        logger.info("   🔹 /api/games/detect         - Detecta jogos .lua em stplug-in/")
        logger.info("   🔹 /api/games/refresh/:id    - Atualiza nome do jogo")
        logger.info("   🔹 /api/games/backup         - Fazer backup de jogos")
        logger.info("   🔹 /api/games/remove         - Remover jogos")
        logger.info("   🔹 /api/games/status         - Status do sistema")
        logger.info("   🔹 /api/games/validate-path  - Valida caminho")
        logger.info("   🔹 /api/games/statistics     - Estatísticas")
        
        return app
        
    except ImportError as e:
        logger.error(f"❌ ERRO CRÍTICO: Não foi possível importar game_management: {e}")
        
        @app.route('/api/games/detect', methods=['POST'])
        def api_games_detect_fallback():
            return jsonify({
                "success": False,
                "error": f"Sistema de gerenciamento não disponível: {str(e)}",
                "games": []
            })
        
        return app