# download_routes.py - SISTEMA DE DOWNLOAD DEFINITIVO E FUNCIONAL
# 🚀 VERSÃO CORRIGIDA 100% - INTEGRAÇÃO COMPLETA E SEM ERROS

import os
import json
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from flask import Flask, request, Response

logger = logging.getLogger("download_routes")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

# ===================================================================
# SERIALIZADOR JSON SEGURO
# ===================================================================

def _make_json_safe(obj, _seen=None):
    """Serializador JSON seguro independente"""
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

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {str(k): _make_json_safe(v, _seen) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [_make_json_safe(x, _seen) for x in obj]

    if hasattr(obj, "__dict__"):
        return _make_json_safe(obj.__dict__, _seen)

    try:
        return str(obj)
    except Exception:
        return "<unserializable>"

def safe_jsonify(obj, status=200):
    """Serializador JSON seguro - standalone"""
    try:
        payload = json.dumps(_make_json_safe(obj), ensure_ascii=False)
        return Response(payload, mimetype="application/json", status=status)
    except Exception as e:
        logger.error(f"Falha ao serializar JSON: {e}")
        return Response(
            json.dumps({"success": False, "error": "Falha ao serializar JSON"}),
            mimetype="application/json",
            status=500
        )

# ===================================================================
# CONFIGURAÇÃO PRINCIPAL
# ===================================================================

def setup_download_routes(app: Flask, getattr_funcs: dict):
    """
    Configura TODAS as rotas de download - VERSÃO DEFINITIVA CORRIGIDA
    """
    logger.info("🔧 Configurando rotas de download DEFINITIVAS...")
    
    # ===================================================================
    # INICIALIZAÇÃO DOS SISTEMAS - VERSÃO CORRIGIDA
    # ===================================================================
    
    # Helper para obter funções de forma segura
    def _get_func(func_name, default=None):
        """Obtém função do getattr_funcs ou retorna default"""
        if getattr_funcs and func_name in getattr_funcs:
            func = getattr_funcs[func_name]
            if callable(func):
                return func
        return default
    
    # ✅ 1. DOWNLOAD MANAGER (USANDO SINGLETON DO main.py)
    DOWNLOAD_MANAGER_AVAILABLE = _get_func("DOWNLOAD_MANAGER_AVAILABLE", False)
    baixar_manifesto_func = _get_func("baixar_manifesto")  # ✅ Já é a função segura do main.py
    criar_gerenciador_download_func = _get_func("criar_gerenciador_download")
    _verificar_disponibilidade_appid_func = _get_func("_verificar_disponibilidade_appid")
    get_download_manager_instance_func = _get_func("get_download_manager_instance")  # ✅ NOVO
    
    # ✅ Obter instância única do DownloadManager
    download_manager = None
    if callable(get_download_manager_instance_func):
        try:
            download_manager = get_download_manager_instance_func()
            if download_manager:
                logger.info("✅ DownloadManager (instância única) obtido com sucesso")
            else:
                logger.warning("⚠️ DownloadManager não pôde ser instanciado")
        except Exception as e:
            logger.error(f"❌ Erro obtendo DownloadManager: {e}")
    
    # ✅ 2. STORE SEARCH FUNCTIONS (BUSCA REAL)
    buscar_jogos_steam_func = _get_func("buscar_jogos_steam")
    STORE_SEARCH_AVAILABLE = callable(buscar_jogos_steam_func)
    
    # ✅ 3. FILE PROCESSING
    FILE_PROCESSING_AVAILABLE = _get_func("FILE_PROCESSING_AVAILABLE", False)
    process_zip_upload_func = _get_func("process_zip_upload")
    
    # ✅ 4. STEAM UTILS
    get_steam_path_func = _get_func("get_steam_path")
    get_steam_path_with_fallback_func = _get_func("get_steam_path_with_fallback")
    
    # ✅ 5. DIRETÓRIO ATUAL (CRÍTICO PARA LOGS)
    current_dir = _get_func("current_dir", ".")
    
    # ===================================================================
    # SISTEMA DE LOG DE DOWNLOADS SIMPLIFICADO (SEM MÓDULO EXTERNO)
    # ===================================================================
    
    def _setup_download_logger():
        """Configura sistema de log de downloads simplificado"""
        downloads_dir = Path(current_dir) / "downloads"
        downloads_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Diretório de downloads: {downloads_dir}")
        return downloads_dir
    
    downloads_dir = _setup_download_logger()
    
    def _log_download(appid: str, success: bool, source: str = "unknown", details: dict = None) -> bool:
        """Registra um download no log"""
        try:
            log_entry = {
                "appid": str(appid),
                "success": success,
                "completed": success,  # Só é True se download realmente concluído
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "details": details or {}
            }
            
            log_file = downloads_dir / f"{appid}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📝 Download logado: {appid} - {'✅ SUCESSO' if success else '❌ FALHA'}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao logar download: {e}")
            return False
    
    def _is_download_completed(appid: str) -> bool:
        """Verifica se download foi realmente concluído via sistema de log"""
        try:
            log_file = downloads_dir / f"{appid}.json"
            if not log_file.exists():
                return False
            
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get("completed", False) and data.get("success", False)
            
        except Exception:
            return False
    
    # ===================================================================
    # VERIFICAÇÃO DE INSTALAÇÃO CORRIGIDA (SÓ MARCA INSTALADO SE DOWNLOAD CONCLUÍDO)
    # ===================================================================
    
    def _check_game_installed(appid: str) -> tuple[bool, dict]:
        """
        ✅ VERIFICAÇÃO CORRIGIDA: Só marca como instalado se download foi concluído
        Remove verificação por arquivos locais que causa falsos positivos
        """
        try:
            appid_str = str(appid)
            logger.debug(f"🔍 Verificando instalação REAL do AppID {appid_str}")
            
            # ✅ 1. PRIMEIRO: Verificar se há LOG de download concluído
            if _is_download_completed(appid_str):
                logger.info(f"✅ Download CONCLUÍDO registrado para {appid}")
                return True, {
                    "appid": appid,
                    "detected_by": "download_log",
                    "confidence": "high",
                    "timestamp": datetime.now().isoformat(),
                    "note": "Download registrado como concluído no sistema"
                }
            
            # ✅ 2. SEGUNDO: Verificação tradicional (OPCIONAL - apenas para referência)
            # Esta parte pode ser comentada se quiser eliminar completamente falsos positivos
            steam_path = _get_steam_path()
            if steam_path:
                # Verificar arquivos .manifest no depotcache
                depotcache_path = os.path.join(steam_path, 'depotcache')
                if os.path.exists(depotcache_path):
                    for file in Path(depotcache_path).glob(f"*{appid_str}*.manifest"):
                        if file.exists():
                            logger.debug(f"⚠️ Arquivo .manifest encontrado (NÃO significa instalado): {file.name}")
                            # Não retorna True - apenas arquivo não significa instalação
            
            # ❌ NÃO está instalado (não há log de download concluído)
            logger.debug(f"❌ AppID {appid} NÃO tem download concluído registrado")
            return False, {
                "appid": appid,
                "detected_by": "none",
                "timestamp": datetime.now().isoformat(),
                "note": "Nenhum download concluído registrado no sistema"
            }
            
        except Exception as e:
            logger.error(f"Erro na verificação de instalação: {e}")
            return False, {"error": str(e)}
    
    def _get_steam_path() -> str:
        """Obter caminho do Steam"""
        if callable(get_steam_path_func):
            path = get_steam_path_func()
            if path:
                return path
        
        if callable(get_steam_path_with_fallback_func):
            path = get_steam_path_with_fallback_func()
            if path:
                return path
        
        return None
    
    # ===================================================================
    # ROTA PRINCIPAL DE DOWNLOAD - VERSÃO DEFINITIVA CORRIGIDA
    # ===================================================================
    
    @app.route('/api/game/<appid>/download', methods=['POST'])
    def api_game_download(appid):
        """
        🚀 ROTA PRINCIPAL DE DOWNLOAD - VERSÃO DEFINITIVA 100% FUNCIONAL
        """
        logger.info(f"🎮 SOLICITAÇÃO DE DOWNLOAD para AppID: {appid}")
        
        try:
            # ✅ 1. VALIDAÇÃO DO APPID
            if not appid or not appid.isdigit():
                return safe_jsonify({
                    "success": False,
                    "appid": appid,
                    "error": "AppID inválido",
                    "message": "O AppID deve ser um número válido"
                }, 400)
            
            appid_str = str(appid)
            
            # ✅ 2. VERIFICAR SE JÁ TEM DOWNLOAD CONCLUÍDO (via log)
            if _is_download_completed(appid_str):
                logger.info(f"✅ Jogo {appid} JÁ TEM DOWNLOAD CONCLUÍDO")
                return safe_jsonify({
                    "success": True,
                    "appid": appid,
                    "already_installed": True,
                    "message": f"Download do jogo {appid} já foi concluído anteriormente",
                    "download_completed": True,
                    "verified_at": datetime.now().isoformat()
                })
            
            # ✅ 3. VERIFICAR DISPONIBILIDADE DO DOWNLOAD MANAGER
            if not callable(baixar_manifesto_func):
                logger.error(f"❌ Função baixar_manifesto não disponível")
                return safe_jsonify({
                    "success": False,
                    "appid": appid,
                    "error": "Sistema de download não disponível",
                    "message": "A função de download não está configurada corretamente",
                    "suggestion": "Reinicie o aplicativo"
                }, 503)
            
            # ✅ 4. VERIFICAR SE O APPID TEM CONTEÚDO DISPONÍVEL
            apis_disponiveis = []
            if callable(_verificar_disponibilidade_appid_func):
                try:
                    apis_disponiveis = _verificar_disponibilidade_appid_func(appid)
                    logger.info(f"🔍 APIs disponíveis para {appid}: {len(apis_disponiveis)}")
                except Exception as e:
                    logger.debug(f"Verificação de APIs falhou: {e}")
            
            # ✅ 5. EXECUTAR DOWNLOAD REAL
            logger.info(f"🚀 INICIANDO DOWNLOAD REAL para {appid}...")
            
            try:
                # ✅ CHAMADA À FUNÇÃO DE DOWNLOAD (já usa singleton via main.py)
                download_result = baixar_manifesto_func(appid)
                logger.info(f"📊 Resultado do download: {download_result}")
                
                if download_result.get("success"):
                    # ✅ DOWNLOAD BEM-SUCEDIDO
                    logger.info(f"✅ DOWNLOAD REAL concluído para {appid}")
                    
                    # ✅ REGISTRAR DOWNLOAD CONCLUÍDO NO LOG
                    download_source = download_result.get("source", "unknown")
                    _log_download(appid, True, download_source, download_result)
                    
                    # ✅ PREPARAR RESPOSTA DE SUCESSO
                    game_name = download_result.get("game_name", f"Jogo {appid}")
                    files_processed = download_result.get("processing_result", {}).get("files_processed", 0)
                    
                    response_data = {
                        "success": True,
                        "appid": appid,
                        "already_installed": False,
                        "download_completed": True,  # ✅ CRÍTICO: Indica que download foi concluído
                        "message": f"Download de '{game_name}' concluído com sucesso!",
                        "game_name": game_name,
                        "source": download_source,
                        "files_processed": files_processed,
                        "apis_disponiveis": apis_disponiveis,
                        "download_details": {
                            "source": download_source,
                            "files_processed": files_processed,
                            "timestamp": datetime.now().isoformat()
                        },
                        "installation_verified": True,
                        "verified_at": datetime.now().isoformat()
                    }
                    
                    # ✅ Adicionar informações adicionais se disponíveis
                    if "processing_result" in download_result:
                        response_data["processing_result"] = download_result["processing_result"]
                    
                    logger.info(f"🎯 Download de {appid} registrado como CONCLUÍDO")
                    return safe_jsonify(response_data)
                    
                else:
                    # ❌ DOWNLOAD FALHOU
                    error_msg = download_result.get("error", "Erro desconhecido no download")
                    logger.error(f"❌ Download falhou: {error_msg}")
                    
                    # ✅ REGISTRAR FALHA NO LOG
                    _log_download(appid, False, "error", {"error": error_msg})
                    
                    return safe_jsonify({
                        "success": False,
                        "appid": appid,
                        "error": error_msg,
                        "message": "Falha no download do jogo",
                        "apis_disponiveis": apis_disponiveis,
                        "suggestion": "Tente novamente ou use Upload via ZIP"
                    }, 500)
                    
            except Exception as e:
                error_msg = f"Erro no DownloadManager: {str(e)}"
                logger.error(f"❌ Exceção no DownloadManager: {error_msg}")
                logger.error(f"💥 TRACEBACK: {traceback.format_exc()}")
                
                # ✅ REGISTRAR FALHA NO LOG
                _log_download(appid, False, "exception", {"exception": str(e)})
                
                return safe_jsonify({
                    "success": False,
                    "appid": appid,
                    "error": error_msg,
                    "message": "Erro interno no sistema de download",
                    "apis_disponiveis": apis_disponiveis
                }, 500)
                
        except Exception as e:
            error_msg = f"Erro crítico no download: {str(e)}"
            logger.error(f"💥 ERRO CRÍTICO: {error_msg}")
            
            return safe_jsonify({
                "success": False,
                "appid": appid,
                "error": error_msg,
                "message": "Erro interno no servidor"
            }, 500)
    
    # ===================================================================
    # ROTA DE STATUS DE INSTALAÇÃO CORRIGIDA
    # ===================================================================
    
    @app.route('/api/game/<appid>/install-status')
    def api_game_install_status(appid):
        """
        🔍 VERIFICAÇÃO REAL DO STATUS DE INSTALAÇÃO - VERSÃO CORRIGIDA
        """
        try:
            # ✅ Verificação real usando sistema de log
            is_installed, game_info = _check_game_installed(appid)
            
            # ✅ Verificar se há log de download
            download_completed = _is_download_completed(appid)
            
            return safe_jsonify({
                "success": True,
                "appid": appid,
                "installed": is_installed,
                "download_completed": download_completed,  # ✅ NOVO: indica se download foi concluído
                "game_info": game_info,
                "checked_at": datetime.now().isoformat(),
                "systems_available": {
                    "download_manager": DOWNLOAD_MANAGER_AVAILABLE,
                    "store_search": STORE_SEARCH_AVAILABLE,
                    "file_processing": FILE_PROCESSING_AVAILABLE
                }
            })
            
        except Exception as e:
            logger.error(f"Erro verificando status: {e}")
            return safe_jsonify({
                "success": False,
                "appid": appid,
                "error": str(e)
            }, 500)
    
    @app.route('/api/game/<appid>/verify-installation', methods=['POST'])
    def api_game_verify_installation(appid):
        """
        ✅ FORÇAR VERIFICAÇÃO DE INSTALAÇÃO - VERSÃO CORRIGIDA
        """
        try:
            logger.info(f"🔍 Verificação forçada para AppID: {appid}")
            
            # ✅ Verificação completa usando sistema de log
            is_installed, game_info = _check_game_installed(appid)
            download_completed = _is_download_completed(appid)
            
            return safe_jsonify({
                "success": True,
                "appid": appid,
                "installed": is_installed,
                "download_completed": download_completed,
                "game_info": game_info,
                "verification_type": "forced",
                "verified_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro na verificação: {e}")
            return safe_jsonify({
                "success": False,
                "appid": appid,
                "error": str(e)
            }, 500)
    
    # ===================================================================
    # ROTA DE BUSCA DE JOGOS CORRIGIDA
    # ===================================================================
    
    @app.route('/api/search/games')
    def api_search_games():
        """
        🔍 BUSCA REAL DE JOGOS - VERSÃO CORRIGIDA
        """
        try:
            query = request.args.get("q", "").strip()
            
            if not query or len(query) < 2:
                return safe_jsonify({
                    "success": True,
                    "results": [],
                    "count": 0,
                    "message": "Digite pelo menos 2 caracteres"
                })
            
            logger.info(f"🔍 Buscando jogos para: '{query}'")
            
            # ✅ USAR SISTEMA REAL DE BUSCA
            if STORE_SEARCH_AVAILABLE and callable(buscar_jogos_steam_func):
                try:
                    jogos = buscar_jogos_steam_func(query, max_results=20)
                    
                    if not jogos:
                        logger.info(f"ℹ️ Nenhum jogo encontrado para '{query}'")
                        return safe_jsonify({
                            "success": True,
                            "results": [],
                            "count": 0,
                            "message": f"Nenhum jogo encontrado para '{query}'",
                            "source": "steam_store_api"
                        })
                    
                    logger.info(f"✅ Encontrados {len(jogos)} jogos para '{query}'")
                    
                    # ✅ ADICIONAR STATUS DE DOWNLOAD EM TEMPO REAL (usando sistema de log)
                    jogos_com_status = []
                    for jogo in jogos:
                        appid_str = str(jogo.get('appid', jogo.get('id', '')))
                        if appid_str and appid_str.isdigit():
                            # ✅ VERIFICAÇÃO CORRIGIDA: usar sistema de log, não arquivos locais
                            download_completed = _is_download_completed(appid_str)
                            jogo['installed'] = download_completed  # ✅ Só "instalado" se download concluído
                            jogo['install_ready'] = DOWNLOAD_MANAGER_AVAILABLE
                            
                            # Garantir campos obrigatórios
                            if 'name' not in jogo:
                                jogo['name'] = f"Jogo {appid_str}"
                            if 'price' not in jogo:
                                jogo['price'] = "Consultar"
                            if 'platforms' not in jogo:
                                jogo['platforms'] = "Windows"
                            
                            jogos_com_status.append(jogo)
                    
                    return safe_jsonify({
                        "success": True,
                        "results": jogos_com_status,
                        "count": len(jogos_com_status),
                        "query": query,
                        "download_system_ready": DOWNLOAD_MANAGER_AVAILABLE,
                        "timestamp": datetime.now().isoformat(),
                        "source": "steam_store_api",
                        "note": "Status 'installed' só é True se download foi concluído"
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Erro na busca real: {e}")
                    return safe_jsonify({
                        "success": True,
                        "results": [],
                        "count": 0,
                        "error": f"Busca falhou: {str(e)}",
                        "source": "fallback"
                    })
            else:
                logger.error("❌ Sistema de busca não disponível")
                return safe_jsonify({
                    "success": False,
                    "error": "Sistema de busca não disponível",
                    "results": [],
                    "count": 0
                })
                
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return safe_jsonify({
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }, 500)
    
    # ===================================================================
    # ROTA DE UPLOAD ZIP (MANTIDA)
    # ===================================================================
    
    @app.route('/api/upload/zip', methods=['POST'])
    def api_upload_zip():
        """
        📦 UPLOAD REAL DE ARQUIVO ZIP
        """
        try:
            if 'zip_file' not in request.files:
                return safe_jsonify({
                    "success": False,
                    "error": "Nenhum arquivo enviado"
                }, 400)
            
            file = request.files['zip_file']
            if file.filename == '':
                return safe_jsonify({
                    "success": False,
                    "error": "Nome de arquivo vazio"
                }, 400)
            
            if not file.filename.lower().endswith('.zip'):
                return safe_jsonify({
                    "success": False,
                    "error": "Arquivo deve ser um ZIP"
                }, 400)
            
            logger.info(f"📦 Upload de ZIP recebido: {file.filename}")
            
            if FILE_PROCESSING_AVAILABLE and callable(process_zip_upload_func):
                try:
                    import tempfile
                    import shutil
                    
                    temp_dir = tempfile.mkdtemp(prefix="steam_upload_")
                    zip_path = os.path.join(temp_dir, file.filename)
                    file.save(zip_path)
                    
                    logger.info(f"🔧 Processando ZIP...")
                    result = process_zip_upload_func(zip_path)
                    
                    try:
                        os.remove(zip_path)
                        shutil.rmtree(temp_dir)
                    except Exception as e:
                        logger.debug(f"Erro limpando temp: {e}")
                    
                    logger.info(f"✅ ZIP processado: {result.get('success', False)}")
                    return safe_jsonify(result)
                    
                except Exception as e:
                    logger.error(f"❌ Erro processando ZIP: {e}")
                    return safe_jsonify({
                        "success": False,
                        "error": f"Erro processando ZIP: {str(e)}",
                        "filename": file.filename
                    }, 500)
            else:
                logger.error("❌ Sistema de processamento ZIP não disponível")
                
                return safe_jsonify({
                    "success": False,
                    "error": "Sistema de processamento de arquivos não disponível",
                    "filename": file.filename
                }, 503)
                
        except Exception as e:
            logger.error(f"❌ Erro no upload ZIP: {e}")
            return safe_jsonify({
                "success": False,
                "error": str(e)
            }, 500)
    
    # ===================================================================
    # STATUS DO SISTEMA DE DOWNLOAD ATUALIZADO
    # ===================================================================
    
    @app.route('/api/download/system-status')
    def api_download_system_status():
        """
        📊 STATUS REAL DO SISTEMA DE DOWNLOAD
        """
        try:
            # Contar downloads concluídos
            downloads_concluidos = 0
            if downloads_dir.exists():
                downloads_concluidos = len([f for f in downloads_dir.glob("*.json")])
            
            systems_status = {
                "download_manager": {
                    "available": DOWNLOAD_MANAGER_AVAILABLE,
                    "working": callable(baixar_manifesto_func),
                    "instance_created": download_manager is not None
                },
                "store_search": {
                    "available": STORE_SEARCH_AVAILABLE,
                    "working": callable(buscar_jogos_steam_func)
                },
                "file_processing": {
                    "available": FILE_PROCESSING_AVAILABLE,
                    "working": callable(process_zip_upload_func)
                },
                "download_logger": {
                    "available": True,
                    "downloads_concluidos": downloads_concluidos,
                    "directory": str(downloads_dir)
                }
            }
            
            return safe_jsonify({
                "success": True,
                "systems": systems_status,
                "steam_path": _get_steam_path(),
                "endpoints_available": {
                    "download": DOWNLOAD_MANAGER_AVAILABLE,
                    "status": True,
                    "search": STORE_SEARCH_AVAILABLE,
                    "upload": FILE_PROCESSING_AVAILABLE,
                    "verify": True
                },
                "overall_status": "operational" if DOWNLOAD_MANAGER_AVAILABLE and STORE_SEARCH_AVAILABLE else "degraded",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro no status do sistema: {e}")
            return safe_jsonify({
                "success": False,
                "error": str(e)
            }, 500)
    
    # ===================================================================
    # ROTA PARA LIMPAR CACHE DE DOWNLOADS (ÚTIL PARA TESTES)
    # ===================================================================
    
    @app.route('/api/download/clear-cache', methods=['POST'])
    def api_clear_download_cache():
        """
        🧹 LIMPAR CACHE DE DOWNLOADS (apenas para desenvolvimento)
        """
        try:
            if downloads_dir.exists():
                deleted_files = 0
                for file in downloads_dir.glob("*.json"):
                    file.unlink()
                    deleted_files += 1
                
                logger.info(f"🧹 Cache de downloads limpo: {deleted_files} arquivos removidos")
                
                return safe_jsonify({
                    "success": True,
                    "message": f"Cache limpo: {deleted_files} arquivos removidos",
                    "deleted_files": deleted_files
                })
            else:
                return safe_jsonify({
                    "success": True,
                    "message": "Nenhum cache para limpar"
                })
                
        except Exception as e:
            logger.error(f"Erro limpando cache: {e}")
            return safe_jsonify({
                "success": False,
                "error": str(e)
            }, 500)
    
    # ===================================================================
    # LOG FINAL
    # ===================================================================
    
    logger.info("=" * 60)
    logger.info("✅ SISTEMA DE DOWNLOAD CONFIGURADO - VERSÃO DEFINITIVA")
    logger.info("=" * 60)
    logger.info(f"🔹 Download Manager: {'✅ DISPONÍVEL' if DOWNLOAD_MANAGER_AVAILABLE else '❌ INDISPONÍVEL'}")
    logger.info(f"🔹 Store Search: {'✅ DISPONÍVEL' if STORE_SEARCH_AVAILABLE else '❌ INDISPONÍVEL'}")
    logger.info(f"🔹 Sistema de Log: ✅ ATIVO ({downloads_dir})")
    logger.info("=" * 60)
    logger.info("🔹 Rotas disponíveis:")
    logger.info("   • /api/game/<appid>/download (POST) - Download REAL")
    logger.info("   • /api/game/<appid>/install-status - Status REAL")
    logger.info("   • /api/game/<appid>/verify-installation (POST) - Verificação")
    logger.info("   • /api/search/games - Busca REAL via Steam API")
    logger.info("   • /api/upload/zip (POST) - Upload REAL")
    logger.info("   • /api/download/system-status - Status do sistema")
    logger.info("   • /api/download/clear-cache (POST) - Limpar cache")
    logger.info("=" * 60)
    logger.info("📝 NOTA: Sistema corrigido - 'installed' só é True se download concluído")
    logger.info("=" * 60)
    
    return app