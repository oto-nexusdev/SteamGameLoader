# utils/file_processing.py - BACKEND COMPLETO CORRIGIDO E DEFINITIVO
# SISTEMA DE PROCESSAMENTO DE ARQUIVOS STEAM INTEGRADO TOTALMENTE CORRIGIDO

import os
import sys
import logging
import shutil
import zipfile
import rarfile
import tempfile
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# 🎯 CONFIGURAÇÃO DE LOGGING AVANÇADA
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SteamBackend:
    """
    🚀 BACKEND COMPLETO PARA PROCESSAMENTO DE ARQUIVOS STEAM - VERSÃO CORRIGIDA DEFINITIVA
    Sistema especializado APENAS em processamento de arquivos - TOTALMENTE INTEGRADO
    """
    
    def __init__(self):
        self.logger = logger
        self._is_processing = False
        
        # ⚙️ CONFIGURAÇÕES PRINCIPAIS OTIMIZADAS
        self.make_backup = True
        self.extract_archives = True
        self.overwrite_existing = True
        self.auto_install_keys = True
        
        # 📁 CAMINHOS DO STEAM - SISTEMA ROBUSTO
        self.steam_path = self._get_steam_path_robust()
        self._setup_destination_paths()
        
        # 📊 ESTATÍSTICAS E CONTROLE APRIMORADO
        self._processed_count = 0
        self._error_count = 0
        self._current_operation = None
        self._processing_results = {}
        
        self.logger.info("🚀 Steam Backend inicializado - VERSÃO CORRIGIDA DEFINITIVA")

    def _get_steam_path_robust(self) -> Optional[str]:
        """🎯 OBTER CAMINHO DO STEAM DE FORMA ROBUSTA - CORRIGIDO DEFINITIVO"""
        try:
            # ✅ TENTAR IMPORTAR STEAM_UTILS PRIMEIRO
            try:
                from utils.steam_utils import get_steam_path_with_fallback
                steam_path = get_steam_path_with_fallback()
                
                if steam_path and os.path.exists(steam_path):
                    self.logger.info(f"✅ Steam path obtido via steam_utils: {steam_path}")
                    return steam_path
                else:
                    self.logger.warning("⚠️ Steam path não encontrado via steam_utils")
            except ImportError as e:
                self.logger.warning(f"⚠️ steam_utils não disponível: {e}")
            
            # ✅ FALLBACK: BUSCA EM LOCAIS COMUNS CORRIGIDA
            possible_paths = [
                os.path.expandvars(r"%ProgramFiles%\Steam"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                os.path.expanduser(r"~/.steam/steam"),
                os.path.expanduser(r"~/.local/share/Steam"),
                r"C:\Program Files\Steam",
                r"C:\Program Files (x86)\Steam",
                r"D:\Program Files\Steam", 
                r"D:\Program Files (x86)\Steam",
                r"E:\Program Files\Steam",
                r"E:\Program Files (x86)\Steam"
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    # ✅ VERIFICAÇÃO ROBUSTA: Verificar se é realmente Steam
                    steam_exe = os.path.join(path, "steam.exe")
                    steamapps_dir = os.path.join(path, "steamapps")
                    config_dir = os.path.join(path, "config")
                    
                    # ✅ ACEITA SE TEM steam.exe OU steamapps/ OU config/
                    if (os.path.exists(steam_exe) or 
                        os.path.exists(steamapps_dir) or 
                        os.path.exists(config_dir)):
                        self.logger.info(f"✅ Steam detectado via fallback: {path}")
                        return path
        
            self.logger.warning("⚠️ Steam não detectado automaticamente")
            return None
                
        except Exception as e:
            self.logger.error(f"❌ Erro crítico ao obter steam_path: {e}")
            return None

    def _setup_destination_paths(self):
        """🎯 CONFIGURA CAMINHOS DE DESTINO CORRETOS - VERSÃO CORRIGIDA DEFINITIVA"""
        try:
            if not self.steam_path:
                self.logger.warning("⚠️ Steam path não disponível - criando estrutura local")
                # Criar estrutura local para testes
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.steam_path = os.path.join(current_dir, "..", "steam_simulation")
                self.logger.info(f"📁 Usando estrutura simulada: {self.steam_path}")
            
            # 🎯 CAMINHOS DEFINITIVOS - CORRIGIDOS
            self.target_depotcache = os.path.join(self.steam_path, 'depotcache')
            self.target_stplugin = os.path.join(self.steam_path, 'config', 'stplug-in')
            
            # 🏗️ CRIAR DIRETÓRIOS CRÍTICOS COM VERIFICAÇÃO ROBUSTA
            critical_paths = [self.target_depotcache, self.target_stplugin]
            
            for path in critical_paths:
                try:
                    os.makedirs(path, exist_ok=True)
                    if os.path.exists(path):
                        # ✅ VERIFICAR PERMISSÕES DE ESCRITA
                        test_file = os.path.join(path, "write_test.tmp")
                        try:
                            with open(test_file, 'w') as f:
                                f.write("test")
                            os.remove(test_file)
                            self.logger.info(f"✅ Diretório crítico com permissões: {path}")
                        except (IOError, OSError) as e:
                            self.logger.error(f"❌ Sem permissão de escrita em {path}: {e}")
                            continue
                    else:
                        self.logger.error(f"❌ Falha ao criar diretório: {path}")
                except Exception as e:
                    self.logger.error(f"❌ Erro criando diretório {path}: {e}")

            self.logger.info("🎯 Caminhos de destino configurados e validados")
                
        except Exception as e:
            self.logger.error(f"❌ Erro configurando paths de destino: {e}")

    def process_files(self, files: List[str]) -> Dict[str, Any]:
        """🚀 PROCESSAR ARQUIVOS - MÉTODO PRINCIPAL CORRIGIDO E DEFINITIVO"""
        if not files:
            self.logger.warning("ℹ️ Nenhum arquivo para processar")
            return self._create_error_result("Nenhum arquivo selecionado para processamento")

        try:
            self._is_processing = True
            self._processed_count = 0
            self._error_count = 0
            self._processing_results = self._initialize_results()

            self.logger.info(f"🎯 Iniciando processamento de {len(files)} arquivo(s)")

            # ✅ VERIFICAÇÃO CRÍTICA DE CONDIÇÕES INICIAIS
            if not self._validate_initial_conditions():
                error_msg = "❌ Condições iniciais não atendidas - verifique diretórios Steam"
                self.logger.error(error_msg)
                return self._create_error_result(error_msg)

            total_files = len(files)
            
            for i, file_path in enumerate(files):
                if not self._is_processing:
                    self.logger.warning("⏹️ Processamento interrompido pelo usuário")
                    break

                self._update_progress(i, total_files, file_path)

                try:
                    file_result = self._process_single_file(file_path)
                    self._collect_results(file_result)

                except Exception as e:
                    error_msg = f"Erro em {os.path.basename(file_path)}: {str(e)}"
                    self._handle_processing_error(error_msg)

            return self._finalize_processing()
            
        except Exception as e:
            return self._handle_critical_error(e)

    def _validate_initial_conditions(self) -> bool:
        """✅ VALIDA CONDIÇÕES INICIAIS - VERSÃO CORRIGIDA DEFINITIVA"""
        # Verificar se os diretórios críticos existem e têm permissões
        critical_paths = [self.target_depotcache, self.target_stplugin]
        
        for path in critical_paths:
            if not os.path.exists(path):
                self.logger.error(f"❌ Diretório não existe: {path}")
                try:
                    os.makedirs(path, exist_ok=True)
                    if not os.path.exists(path):
                        self.logger.error(f"❌ Não foi possível criar diretório: {path}")
                        return False
                    self.logger.info(f"✅ Diretório criado: {path}")
                except Exception as e:
                    self.logger.error(f"❌ Erro criando diretório {path}: {e}")
                    return False
            
            # Verificar permissões de escrita
            try:
                test_file = os.path.join(path, "write_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except (IOError, OSError) as e:
                self.logger.error(f"❌ Sem permissão de escrita em {path}: {e}")
                return False

        self.logger.info("✅ Todas as condições iniciais validadas")
        return True

    def _initialize_results(self) -> Dict[str, Any]:
        """📊 INICIALIZAR ESTRUTURA DE RESULTADOS - EXPANDIDA"""
        return {
            'success': False,
            'total_processed': 0,
            'successful_files': 0,
            'failed_files': 0,
            'app_ids': set(),
            'extracted_files': [],
            'moved_files': [],  # ✅ LISTA DE ARQUIVOS MOVIDOS
            'backups_created': [],
            'errors': [],
            'installation_validations': {},
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'steam_path': self.steam_path,
            'target_paths': {
                'depotcache': self.target_depotcache,
                'stplug_in': self.target_stplugin
            },
            'files_destination_details': [],  # ✅ NOVO: DETALHES DE DESTINO
            'processing_log': []  # ✅ NOVO: LOG DE PROCESSAMENTO
        }

    def _update_progress(self, index: int, total: int, file_path: str):
        """📊 ATUALIZAR PROGRESSO - MELHORADO"""
        filename = os.path.basename(file_path)
        self._current_operation = f"Processando: {filename}"
        progress_pct = (index + 1) / total * 100
        progress_msg = f"📁 [{index+1}/{total}] ({progress_pct:.1f}%) Processando: {filename}"
        self.logger.info(progress_msg)
        self._processing_results['processing_log'].append(progress_msg)

    def _collect_results(self, file_result: Optional[Dict]):
        """📝 COLETAR RESULTADOS DO PROCESSAMENTO - CORRIGIDO DEFINITIVO"""
        if file_result:
            self._processing_results['total_processed'] += 1
            
            if file_result.get('success', False):
                self._processing_results['successful_files'] += 1
                
                # ✅ ADICIONAR ARQUIVOS MOVIDOS À LISTA PRINCIPAL - CORRIGIDO
                if 'moved' in file_result and file_result['moved']:
                    for moved_pair in file_result['moved']:
                        if isinstance(moved_pair, tuple) and len(moved_pair) == 2:
                            src, dest = moved_pair
                            file_info = {
                                'from': src,
                                'to': dest,
                                'filename': os.path.basename(dest),
                                'size': os.path.getsize(dest) if os.path.exists(dest) else 0,
                                'destination_type': os.path.basename(os.path.dirname(dest))
                            }
                            self._processing_results['moved_files'].append(file_info)
                            self._processing_results['files_destination_details'].append(file_info)
                            
                            success_msg = f"✅ Arquivo registrado: {os.path.basename(dest)} → {file_info['destination_type']}"
                            self.logger.info(success_msg)
                            self._processing_results['processing_log'].append(success_msg)
            else:
                self._processing_results['failed_files'] += 1
            
            if 'extracted' in file_result:
                self._processing_results['extracted_files'].extend(file_result['extracted'])
            
            if 'backup_created' in file_result:
                self._processing_results['backups_created'].append(file_result['backup_created'])
            
            if 'appid' in file_result and file_result['appid']:
                appid = file_result['appid']
                self._processing_results['app_ids'].add(appid)
                appid_msg = f"🔍 AppID detectado: {appid}"
                self.logger.info(appid_msg)
                self._processing_results['processing_log'].append(appid_msg)

    def _handle_processing_error(self, error_msg: str):
        """❌ TRATAR ERRO DE PROCESSAMENTO - MELHORADO"""
        self._processing_results['errors'].append(error_msg)
        self._processing_results['failed_files'] += 1
        self.logger.error(f"❌ {error_msg}")
        self._processing_results['processing_log'].append(f"❌ {error_msg}")

    def _finalize_processing(self) -> Dict[str, Any]:
        """✅ FINALIZAR PROCESSAMENTO - VERSÃO COMPLETA DEFINITIVA"""
        self._processing_results['end_time'] = datetime.now().isoformat()
        self._processing_results['success'] = self._processing_results['successful_files'] > 0
        
        # ✅ ADICIONAR RESUMO EXECUTIVO DETALHADO
        total_processed = self._processing_results['total_processed']
        successful = self._processing_results['successful_files']
        
        self._processing_results['summary'] = {
            'total_files': total_processed,
            'successful': successful,
            'failed': self._processing_results['failed_files'],
            'success_rate': f"{(successful / total_processed * 100):.1f}%" if total_processed > 0 else "0%",
            'files_moved': len(self._processing_results['moved_files']),
            'unique_appids': len(self._processing_results['app_ids']),
            'processing_time': self._get_processing_time()
        }
        
        # ✅ VALIDAÇÃO DAS INSTALAÇÕES
        self._validate_installations()
        
        self._current_operation = None
        self._is_processing = False
        
        # ✅ LOG FINAL DETALHADO
        if self._processing_results['success']:
            success_msg = f"✅ PROCESSAMENTO CONCLUÍDO: {successful}/{total_processed} arquivos processados com sucesso"
            summary_msg = f"📊 RESUMO: {len(self._processing_results['moved_files'])} arquivos movidos para Steam"
            self.logger.info(success_msg)
            self.logger.info(summary_msg)
            self._processing_results['processing_log'].extend([success_msg, summary_msg])
        else:
            error_msg = f"❌ PROCESSAMENTO FINALIZADO COM FALHAS: {self._processing_results['failed_files']} erros"
            self.logger.error(error_msg)
            self._processing_results['processing_log'].append(error_msg)
        
        return self._processing_results

    def _get_processing_time(self) -> str:
        """⏱️ CALCULAR TEMPO DE PROCESSAMENTO"""
        try:
            start_time = datetime.fromisoformat(self._processing_results['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(self._processing_results['end_time'].replace('Z', '+00:00'))
            duration = end_time - start_time
            return str(duration)
        except:
            return "N/A"

    def _handle_critical_error(self, error: Exception) -> Dict[str, Any]:
        """💥 TRATAR ERRO CRÍTICO - MELHORADO"""
        error_msg = f"❌ Erro crítico no processamento: {str(error)}"
        self.logger.error(error_msg)
        
        result = self._create_error_result(error_msg)
        result['success'] = False
        return result

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """📝 CRIAR RESULTADO DE ERRO - EXPANDIDO"""
        return {
            'success': False,
            'error': error_message,
            'total_processed': 0,
            'successful_files': 0,
            'failed_files': 1,
            'errors': [error_message],
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'summary': {
                'total_files': 0,
                'successful': 0,
                'failed': 1,
                'success_rate': '0%'
            },
            'steam_path': self.steam_path,
            'target_paths': {
                'depotcache': self.target_depotcache,
                'stplug_in': self.target_stplugin
            },
            'processing_log': [f"❌ {error_message}"]
        }

    def _process_single_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """🎯 PROCESSAR ARQUIVO INDIVIDUAL - VERSÃO CORRIGIDA DEFINITIVA"""
        try:
            filename = os.path.basename(file_path)
            self.logger.info(f"📄 Processando arquivo: {filename}")
            self._processing_results['processing_log'].append(f"📄 Processando arquivo: {filename}")

            # ✅ VALIDAÇÃO ROBUSTA DO ARQUIVO
            validation_error = self._validate_file(file_path)
            if validation_error:
                self.logger.error(f"❌ Validação falhou: {filename} - {validation_error}")
                self._processing_results['processing_log'].append(f"❌ Validação falhou: {filename} - {validation_error}")
                return {
                    'success': False,
                    'file': file_path,
                    'error': validation_error
                }

            # 📦 PROCESSAMENTO BASEADO NO TIPO
            if self._is_archive_file(file_path) and self.extract_archives:
                self.logger.info(f"📦 Detectado arquivo compactado: {filename}")
                self._processing_results['processing_log'].append(f"📦 Detectado arquivo compactado: {filename}")
                return self._extract_and_process_archive_robust(file_path)
            else:
                return self._process_single_file_direct(file_path)

        except Exception as e:
            error_msg = f"❌ Erro processando {os.path.basename(file_path)}: {e}"
            self.logger.error(error_msg)
            self._processing_results['processing_log'].append(error_msg)
            return {
                'success': False,
                'file': file_path,
                'error': error_msg
            }

    def _validate_file(self, file_path: str) -> Optional[str]:
        """✅ VALIDAR ARQUIVO - VERSÃO COMPLETA"""
        if not os.path.exists(file_path):
            return "❌ Arquivo não encontrado"
        
        if not os.path.isfile(file_path):
            return "❌ Caminho não é um arquivo"
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return "❌ Arquivo vazio"
        
        # Verificar permissões de leitura
        if not os.access(file_path, os.R_OK):
            return "❌ Sem permissão para ler o arquivo"
        
        # Verificar se não é arquivo de sistema
        if self._is_system_file(os.path.basename(file_path)):
            return "❌ Arquivo de sistema ignorado"
        
        return None

    def _is_archive_file(self, file_path: str) -> bool:
        """📦 VERIFICAR SE É ARQUIVO COMPACTADO - CORRIGIDO"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.zip':
                return zipfile.is_zipfile(file_path)
            elif ext == '.rar':
                # Tentar importar rarfile, mas continuar se não disponível
                try:
                    return rarfile.is_rarfile(file_path)
                except NameError:
                    self.logger.warning("⚠️ rarfile não disponível - ignorando arquivos RAR")
                    return False
            return False
        except Exception as e:
            self.logger.debug(f"⚠️ Erro verificando arquivo compactado {file_path}: {e}")
            return False

    def _extract_and_process_archive_robust(self, archive_path: str) -> Optional[Dict[str, Any]]:
        """📦 EXTRAIR E PROCESSAR ARQUIVO COMPACTADO - VERSÃO CORRIGIDA DEFINITIVA"""
        temp_dir = None
        original_size = os.path.getsize(archive_path)
        
        try:
            filename = os.path.basename(archive_path)
            self.logger.info(f"📦 Extraindo arquivo: {filename} ({original_size} bytes)")
            self._processing_results['processing_log'].append(f"📦 Extraindo arquivo: {filename} ({original_size} bytes)")
            
            extracted_files = []
            moved_files = []
            app_ids = set()

            # 🏗️ CRIAR DIRETÓRIO TEMPORÁRIO SEGURO
            temp_dir = self._create_secure_temp_dir()
            if not temp_dir:
                return None

            # 🔄 EXTRAIR ARQUIVO COM VERIFICAÇÃO
            success, extracted_files = self._extract_archive_robust(archive_path, temp_dir)
            if not success or not extracted_files:
                self.logger.error(f"❌ Falha na extração: {archive_path}")
                self._processing_results['processing_log'].append(f"❌ Falha na extração: {archive_path}")
                return None

            # 🔍 PROCESSAR ARQUIVOS EXTRAÍDOS
            processed_count = 0
            for extracted_file in extracted_files:
                if not self._is_processing:
                    break

                # Ignorar arquivos de sistema
                if self._is_system_file(os.path.basename(extracted_file)):
                    continue

                result = self._process_single_file_direct(extracted_file)
                if result and result.get('success', False):
                    processed_count += 1
                    moved_files.extend(result.get('moved', []))
                    
                    if 'appid' in result and result['appid']:
                        app_ids.add(result['appid'])

            success_msg = f"✅ Extraídos {processed_count} arquivos de {filename}"
            self.logger.info(success_msg)
            self._processing_results['processing_log'].append(success_msg)
            
            return {
                'success': processed_count > 0,
                'extracted': extracted_files,
                'moved': moved_files,
                'appid': list(app_ids)[0] if app_ids else None
            }

        except Exception as e:
            error_msg = f"❌ Erro extraindo {archive_path}: {e}"
            self.logger.error(error_msg)
            self._processing_results['processing_log'].append(error_msg)
            return None
        finally:
            if temp_dir:
                self._secure_cleanup_temp_dir(temp_dir)

    def _extract_archive_robust(self, archive_path: str, extract_dir: str) -> Tuple[bool, List[str]]:
        """🔄 EXTRAIR ARQUIVO COMPACTADO COM VERIFICAÇÃO DE INTEGRIDADE - CORRIGIDO DEFINITIVO"""
        extracted_files = []
        
        try:
            ext = os.path.splitext(archive_path)[1].lower()
            
            if ext == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    # ✅ VERIFICAR INTEGRIDADE PRIMEIRO
                    bad_file = zip_ref.testzip()
                    if bad_file is not None:
                        error_msg = f"❌ Arquivo ZIP corrompido: {bad_file}"
                        self.logger.error(error_msg)
                        self._processing_results['processing_log'].append(error_msg)
                        return False, []
                    
                    # ✅ EXTRAIR TODOS OS ARQUIVOS
                    zip_ref.extractall(extract_dir)
                    
                    # ✅ VERIFICAR ARQUIVOS EXTRAÍDOS
                    for file_info in zip_ref.infolist():
                        if not file_info.is_dir():
                            extracted_path = os.path.join(extract_dir, file_info.filename)
                            if os.path.exists(extracted_path):
                                extracted_files.append(extracted_path)
                
                success_msg = f"✅ ZIP extraído: {len(extracted_files)} arquivos"
                self.logger.info(success_msg)
                self._processing_results['processing_log'].append(success_msg)
                return True, extracted_files
                
            elif ext == '.rar':
                try:
                    with rarfile.RarFile(archive_path, 'r') as rar_ref:
                        # ✅ EXTRAIR TODOS OS ARQUIVOS
                        rar_ref.extractall(extract_dir)
                        
                        # ✅ LISTAR ARQUIVOS EXTRAÍDOS
                        for file_info in rar_ref.infolist():
                            if not file_info.isdir:
                                extracted_path = os.path.join(extract_dir, file_info.filename)
                                if os.path.exists(extracted_path):
                                    extracted_files.append(extracted_path)
                    
                    success_msg = f"✅ RAR extraído: {len(extracted_files)} arquivos"
                    self.logger.info(success_msg)
                    self._processing_results['processing_log'].append(success_msg)
                    return True, extracted_files
                except NameError:
                    error_msg = "❌ rarfile não disponível - não é possível extrair RAR"
                    self.logger.error(error_msg)
                    self._processing_results['processing_log'].append(error_msg)
                    return False, []
                except Exception as e:
                    error_msg = f"❌ Erro extraindo RAR: {e}"
                    self.logger.error(error_msg)
                    self._processing_results['processing_log'].append(error_msg)
                    return False, []
                
            else:
                warning_msg = f"⚠️ Formato não suportado: {ext}"
                self.logger.warning(warning_msg)
                self._processing_results['processing_log'].append(warning_msg)
                return False, []
                
        except Exception as e:
            error_msg = f"❌ Erro extraindo {archive_path}: {e}"
            self.logger.error(error_msg)
            self._processing_results['processing_log'].append(error_msg)
            return False, []

    def _process_single_file_direct(self, file_path: str) -> Optional[Dict[str, Any]]:
        """🎯 PROCESSAMENTO DIRETO DE ARQUIVO - CORAÇÃO DO SISTEMA CORRIGIDO DEFINITIVO"""
        try:
            filename = os.path.basename(file_path)
            original_size = os.path.getsize(file_path)
            self.logger.info(f"➡️ Movendo arquivo: {filename} ({original_size} bytes)")
            self._processing_results['processing_log'].append(f"➡️ Movendo arquivo: {filename} ({original_size} bytes)")

            # 🎯 DETERMINAR DESTINO CORRETO
            dest_dir = self._get_destination_directory(filename)
            if not dest_dir:
                error_msg = f"⚠️ Tipo não suportado: {filename}"
                self.logger.warning(error_msg)
                self._processing_results['processing_log'].append(error_msg)
                return {
                    'success': False,
                    'file': file_path,
                    'error': error_msg
                }

            # 📁 MOVER ARQUIVO COM VERIFICAÇÃO ROBUSTA
            success, final_path, error_msg = self._move_file_with_validation(file_path, dest_dir, original_size)
            
            if success:
                # 📝 REGISTRAR SUCESSO COMPLETO
                dest_name = os.path.basename(os.path.dirname(dest_dir))
                final_size = os.path.getsize(final_path)
                
                success_msg = f"✅ {filename} → {dest_name} ({final_size} bytes)"
                self.logger.info(success_msg)
                self._processing_results['processing_log'].append(success_msg)
                
                # 🔍 EXTRAIR APPID
                appid = self._extract_appid_from_filename(filename)
                
                result = {
                    'success': True,
                    'file': file_path,
                    'moved': [(file_path, final_path)],  # ✅ TUPLA CORRETA
                    'original_size': original_size,
                    'final_size': final_size,
                    'destination': dest_name,
                    'destination_path': final_path
                }
                
                if appid:
                    result['appid'] = appid
                    appid_msg = f"🔍 AppID detectado: {appid}"
                    self.logger.info(appid_msg)
                    self._processing_results['processing_log'].append(appid_msg)
                    
                return result
            else:
                error_msg = f"❌ Falha ao mover {filename}: {error_msg}"
                self.logger.error(error_msg)
                self._processing_results['processing_log'].append(error_msg)
                return {
                    'success': False,
                    'file': file_path,
                    'error': error_msg
                }

        except Exception as e:
            error_msg = f"❌ Erro movendo {file_path}: {e}"
            self.logger.error(error_msg)
            self._processing_results['processing_log'].append(error_msg)
            return {
                'success': False,
                'file': file_path,
                'error': error_msg
            }

    def _move_file_with_validation(self, src_path: str, dest_dir: str, expected_size: int) -> Tuple[bool, str, str]:
        """📁 MOVER ARQUIVO COM VALIDAÇÃO DE INTEGRIDADE COMPLETA - CORRIGIDO DEFINITIVO"""
        try:
            filename = os.path.basename(src_path)
            dest_path = os.path.join(dest_dir, filename)
            
            # ✅ VERIFICAÇÕES DE SEGURANÇA
            if not os.path.exists(src_path):
                return False, "", "Arquivo origem não existe"
                
            # Verificar/Criar diretório de destino
            try:
                os.makedirs(dest_dir, exist_ok=True)
                if not os.path.exists(dest_dir):
                    return False, "", f"Falha ao criar diretório: {dest_dir}"
            except Exception as e:
                return False, "", f"Falha ao criar diretório: {e}"
            
            # 🔄 SUBSTITUIÇÃO SEGURA DE ARQUIVO EXISTENTE
            if os.path.exists(dest_path):
                if not self.overwrite_existing:
                    return False, "", "Arquivo já existe e overwrite desabilitado"
                
                try:
                    # Fazer backup se configurado
                    if self.make_backup:
                        backup_path = dest_path + '.backup'
                        shutil.copy2(dest_path, backup_path)
                        backup_msg = f"📦 Backup criado: {backup_path}"
                        self.logger.info(backup_msg)
                        self._processing_results['processing_log'].append(backup_msg)
                    
                    os.remove(dest_path)
                    replace_msg = f"🔄 Substituindo arquivo existente: {filename}"
                    self.logger.info(replace_msg)
                    self._processing_results['processing_log'].append(replace_msg)
                except Exception as e:
                    return False, "", f"Falha ao remover arquivo existente: {e}"

            # 📁 COPIAR COM MÉTODO ROBUSTO
            try:
                shutil.copy2(src_path, dest_path)
                
                # ✅ VERIFICAÇÃO FINAL DE INTEGRIDADE
                if not os.path.exists(dest_path):
                    return False, "", "Arquivo destino não criado"
                    
                final_size = os.path.getsize(dest_path)
                
                # Verificar se o tamanho é consistente
                if final_size != expected_size and final_size > 0:
                    warning_msg = f"⚠️ Tamanho diferente: origem={expected_size}, destino={final_size}"
                    self.logger.warning(warning_msg)
                    self._processing_results['processing_log'].append(warning_msg)
                
                # Verificar se o arquivo é legível
                try:
                    with open(dest_path, 'rb') as f:
                        header = f.read(100)  # Ler primeiros 100 bytes
                    if len(header) == 0:
                        return False, "", "Arquivo destino corrompido (vazio)"
                except Exception:
                    return False, "", "Arquivo destino corrompido (ilegível)"
                
                success_msg = f"✅ Movimento validado: {filename} - {final_size} bytes"
                self.logger.info(success_msg)
                self._processing_results['processing_log'].append(success_msg)
                return True, dest_path, ""
                
            except Exception as e:
                return False, "", f"Erro na cópia: {e}"

        except Exception as e:
            return False, "", f"Erro crítico: {e}"

    def _get_destination_directory(self, filename: str) -> Optional[str]:
        """🎯 DETERMINAR DIRETÓRIO DE DESTINO CORRETO - VERSÃO DEFINITIVA"""
        if not self.steam_path:
            self.logger.error("❌ Steam path não disponível")
            return None

        filename_lower = filename.lower()
        
        # 🎯 REGRAS ABSOLUTAMENTE CLARAS E CORRETAS
        if filename_lower.endswith('.manifest'):
            destination = self.target_depotcache
            self.logger.info(f"🎯 .manifest detectado: {filename} → depotcache")
            self._processing_results['processing_log'].append(f"🎯 .manifest detectado: {filename} → depotcache")
            
        elif filename_lower.endswith('.lua'):
            destination = self.target_stplugin
            self.logger.info(f"🎯 .lua detectado: {filename} → stplug-in")
            self._processing_results['processing_log'].append(f"🎯 .lua detectado: {filename} → stplug-in")
            
        else:
            warning_msg = f"⚠️ Tipo de arquivo não suportado: {filename}"
            self.logger.warning(warning_msg)
            self._processing_results['processing_log'].append(warning_msg)
            return None
        
        # ✅ VERIFICAÇÃO/CRIAÇÃO ROBUSTA DO DESTINO
        if destination:
            if not os.path.exists(destination):
                try:
                    os.makedirs(destination, exist_ok=True)
                    if os.path.exists(destination):
                        success_msg = f"📁 Diretório criado: {destination}"
                        self.logger.info(success_msg)
                        self._processing_results['processing_log'].append(success_msg)
                    else:
                        error_msg = f"❌ Falha ao criar diretório: {destination}"
                        self.logger.error(error_msg)
                        self._processing_results['processing_log'].append(error_msg)
                        return None
                except Exception as e:
                    error_msg = f"❌ Erro criando diretório {destination}: {e}"
                    self.logger.error(error_msg)
                    self._processing_results['processing_log'].append(error_msg)
                    return None
            
            # ✅ VERIFICAR PERMISSÕES DE ESCRITA
            try:
                test_file = os.path.join(destination, "write_test.tmp")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except (IOError, OSError) as e:
                error_msg = f"❌ Sem permissão de escrita em {destination}: {e}"
                self.logger.error(error_msg)
                self._processing_results['processing_log'].append(error_msg)
                return None
            
            return destination
        else:
            return None

    def _validate_installations(self):
        """✅ VALIDAR INSTALAÇÕES REALIZADAS - CORRIGIDO DEFINITIVO"""
        try:
            from utils.steam_utils import validate_steam_installation
        except ImportError as e:
            self.logger.debug(f"ℹ️ steam_utils não disponível para validação: {e}")
            return
        
        for appid in self._processing_results['app_ids']:
            try:
                validation = validate_steam_installation(self.steam_path, appid)
                self._processing_results['installation_validations'][appid] = validation
                validation_msg = f"✅ Validação para AppID {appid}: {validation.get('valid', False)}"
                self.logger.info(validation_msg)
                self._processing_results['processing_log'].append(validation_msg)
            except Exception as e:
                error_msg = f"⚠️ Erro validando instalação {appid}: {e}"
                self.logger.debug(error_msg)
                self._processing_results['processing_log'].append(error_msg)

    def _extract_appid_from_filename(self, filename: str) -> Optional[str]:
        """🔍 EXTRAIR APPID DO NOME DO ARQUIVO - VERSÃO MELHORADA"""
        try:
            patterns = [
                r'(\d{5,})',  # 5+ dígitos
                r'app?[_-]?(\d{5,})',
                r'(\d{5,})\.(manifest|lua)$',
                r'manifest_(\d{5,})\.manifest',
                r'(\d{5,})_manifest\.manifest',
                r'app?manifest_(\d{5,})\.acf',
                r'^(\d{5,})_',  # Padrão no início
                r'_(\d{5,})\.'  # Padrão no meio
            ]
            
            for pattern in patterns:
                match = re.search(pattern, filename, re.IGNORECASE)
                if match and match.group(1).isdigit():
                    appid = match.group(1)
                    # Validar range comum de AppIDs Steam
                    if 5 <= len(appid) <= 7:
                        appid_msg = f"🔍 AppID detectado: {appid} de {filename}"
                        self.logger.info(appid_msg)
                        self._processing_results['processing_log'].append(appid_msg)
                        return appid
            
            debug_msg = f"🔍 Nenhum AppID detectado em: {filename}"
            self.logger.debug(debug_msg)
            self._processing_results['processing_log'].append(debug_msg)
            return None
            
        except Exception as e:
            error_msg = f"⚠️ Erro na extração de AppID: {e}"
            self.logger.debug(error_msg)
            self._processing_results['processing_log'].append(error_msg)
            return None

    def _create_secure_temp_dir(self) -> Optional[str]:
        """🏗️ CRIAR DIRETÓRIO TEMPORÁRIO SEGURO - CORRIGIDO"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="steamloader_")
            success_msg = f"📁 Diretório temporário criado: {temp_dir}"
            self.logger.info(success_msg)
            self._processing_results['processing_log'].append(success_msg)
            return temp_dir
        except Exception as e:
            error_msg = f"❌ Erro criando diretório temporário: {e}"
            self.logger.error(error_msg)
            self._processing_results['processing_log'].append(error_msg)
            return None

    def _secure_cleanup_temp_dir(self, temp_dir: str):
        """🧹 LIMPEZA SEGURA DO DIRETÓRIO TEMPORÁRIO - CORRIGIDO"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                success_msg = f"🧹 Diretório temporário removido: {temp_dir}"
                self.logger.info(success_msg)
                self._processing_results['processing_log'].append(success_msg)
        except Exception as e:
            warning_msg = f"⚠️ Erro limpando diretório temporário: {e}"
            self.logger.warning(warning_msg)
            self._processing_results['processing_log'].append(warning_msg)

    def _is_system_file(self, filename: str) -> bool:
        """🔍 VERIFICAR SE É ARQUIVO DE SISTEMA - EXPANDIDO"""
        system_files = {
            'thumbs.db', '.ds_store', 'desktop.ini', 
            '.localized', '._.ds_store', '.gitignore',
            'readme.txt', 'readme.md', 'license.txt',
            '.gitkeep', '.gitattributes', '.gitmodules',
            'placeholder.txt', '.placeholder'
        }
        return filename.lower() in system_files

    # 🔧 CONTROLES DE PROCESSAMENTO - MANTIDOS
    def stop_processing(self):
        """⏹️ PARAR PROCESSAMENTO"""
        self._is_processing = False
        self.logger.info("⏹️ Processamento parado pelo usuário")
        self._processing_results['processing_log'].append("⏹️ Processamento parado pelo usuário")

    def get_processing_status(self) -> Dict[str, Any]:
        """📊 OBTER STATUS DO PROCESSAMENTO - EXPANDIDO"""
        return {
            'is_processing': self._is_processing,
            'current_operation': self._current_operation,
            'processed_count': self._processed_count,
            'error_count': self._error_count,
            'steam_path': self.steam_path,
            'target_paths': {
                'depotcache': self.target_depotcache,
                'stplug_in': self.target_stplugin
            },
            'paths_exist': {
                'depotcache': os.path.exists(self.target_depotcache),
                'stplug_in': os.path.exists(self.target_stplugin)
            },
            'paths_writable': {
                'depotcache': os.access(self.target_depotcache, os.W_OK) if os.path.exists(self.target_depotcache) else False,
                'stplug_in': os.access(self.target_stplugin, os.W_OK) if os.path.exists(self.target_stplugin) else False
            },
            'processing_log': self._processing_results.get('processing_log', [])
        }

    # ⚙️ CONFIGURAÇÕES - MANTIDAS
    def update_settings(self, make_backup=None, extract_archives=None, overwrite_existing=None):
        """⚙️ ATUALIZAR CONFIGURAÇÕES"""
        if make_backup is not None:
            self.make_backup = make_backup
            setting_msg = f"📦 Backup de arquivos: {'ativado' if make_backup else 'desativado'}"
            self.logger.info(setting_msg)
            self._processing_results['processing_log'].append(setting_msg)
        
        if extract_archives is not None:
            self.extract_archives = extract_archives
            setting_msg = f"📦 Extração de arquivos: {'ativada' if extract_archives else 'desativada'}"
            self.logger.info(setting_msg)
            self._processing_results['processing_log'].append(setting_msg)
        
        if overwrite_existing is not None:
            self.overwrite_existing = overwrite_existing
            setting_msg = f"🔄 Substituição de arquivos: {'ativada' if overwrite_existing else 'desativada'}"
            self.logger.info(setting_msg)
            self._processing_results['processing_log'].append(setting_msg)
        
        self.logger.info("⚙️ Configurações atualizadas")
        self._processing_results['processing_log'].append("⚙️ Configurações atualizadas")

    def get_steam_info(self) -> Dict[str, Any]:
        """🔍 OBTER INFORMAÇÕES DO STEAM - VERSÃO COMPLETA DEFINITIVA"""
        try:
            steam_running = False
            system_info = {}
            
            # Tentar obter informações do steam_utils se disponível
            try:
                from utils.steam_utils import (
                    validate_steam_installation,
                    is_steam_running,
                    get_system_info
                )
                
                steam_validation = validate_steam_installation(self.steam_path) if self.steam_path else {}
                steam_running = is_steam_running()
                system_info = get_system_info()
            except ImportError:
                steam_validation = {}
                # Verificação básica se Steam está rodando
                try:
                    import psutil
                    for proc in psutil.process_iter(['name']):
                        if 'steam' in proc.info['name'].lower():
                            steam_running = True
                            break
                except ImportError:
                    steam_running = False
            
            return {
                'steam_path': self.steam_path,
                'steam_running': steam_running,
                'validation': steam_validation,
                'system_info': system_info,
                'target_paths': {
                    'depotcache': self.target_depotcache,
                    'stplug_in': self.target_stplugin
                },
                'paths_exist': {
                    'depotcache': os.path.exists(self.target_depotcache),
                    'stplug_in': os.path.exists(self.target_stplugin)
                },
                'paths_writable': {
                    'depotcache': os.access(self.target_depotcache, os.W_OK) if os.path.exists(self.target_depotcache) else False,
                    'stplug_in': os.access(self.target_stplugin, os.W_OK) if os.path.exists(self.target_stplugin) else False
                },
                'backend_status': 'OPERATIONAL' if self.steam_path else 'MISSING_STEAM_PATH',
                'processing_log': self._processing_results.get('processing_log', [])
            }
        except Exception as e:
            self.logger.error(f"❌ Erro obtendo informações Steam: {e}")
            return {
                'steam_path': self.steam_path,
                'steam_running': False,
                'error': str(e),
                'backend_status': 'ERROR',
                'processing_log': self._processing_results.get('processing_log', [])
            }


# ✅ SISTEMA DE UPLOAD ZIP ESPECIALIZADO - NOVA CLASSE ADICIONADA
class ZipUploadProcessor:
    """
    🚀 PROCESSADOR ESPECIALIZADO PARA UPLOAD DE ARQUIVOS ZIP
    Sistema robusto para extrair e instalar jogos via arquivos ZIP
    """
    
    def __init__(self, steam_backend=None):
        self.steam_backend = steam_backend or SteamBackend()
        self.logger = logging.getLogger(__name__)
        self.temp_dir = None
        
    def process_zip_upload(self, zip_file_path: str) -> Dict[str, Any]:
        """
        📦 PROCESSAR UPLOAD DE ZIP - MÉTODO PRINCIPAL
        """
        try:
            self.logger.info(f"🎯 Iniciando processamento de ZIP: {zip_file_path}")
            
            # ✅ VALIDAÇÕES INICIAIS
            if not os.path.exists(zip_file_path):
                return self._create_upload_error("Arquivo ZIP não encontrado")
                
            if not zipfile.is_zipfile(zip_file_path):
                return self._create_upload_error("Arquivo não é um ZIP válido")
            
            # 📁 CRIAR DIRETÓRIO TEMPORÁRIO SEGURO
            self.temp_dir = self._create_secure_temp_dir()
            if not self.temp_dir:
                return self._create_upload_error("Falha ao criar diretório temporário")
            
            # 🔄 EXTRAIR ZIP
            extraction_result = self._extract_zip_file(zip_file_path, self.temp_dir)
            if not extraction_result['success']:
                return extraction_result
            
            # 🔍 ANALISAR CONTEÚDO EXTRAÍDO
            content_analysis = self._analyze_extracted_content(self.temp_dir)
            self.logger.info(f"📊 Análise de conteúdo: {content_analysis}")
            
            # 🎯 PROCESSAR ARQUIVOS ENCONTRADOS
            if not content_analysis['valid_files']:
                return self._create_upload_error("Nenhum arquivo .manifest ou .lua válido encontrado no ZIP")
            
            # 🚀 EXECUTAR PROCESSAMENTO COM STEAM BACKEND
            processing_result = self.steam_backend.process_files(content_analysis['valid_files'])
            
            # ✅ ADICIONAR METADADOS DO UPLOAD
            processing_result['upload_metadata'] = {
                'zip_file': os.path.basename(zip_file_path),
                'extracted_files': content_analysis['file_count'],
                'valid_files_found': len(content_analysis['valid_files']),
                'detected_appids': content_analysis['detected_appids'],
                'content_analysis': content_analysis
            }
            
            # 🧹 LIMPEZA
            self._cleanup_temp_dir()
            
            self.logger.info(f"✅ Upload ZIP processado com sucesso: {len(content_analysis['valid_files'])} arquivos")
            return processing_result
            
        except Exception as e:
            self.logger.error(f"❌ Erro crítico no processamento ZIP: {e}")
            self._cleanup_temp_dir()
            return self._create_upload_error(f"Erro no processamento: {str(e)}")
    
    def _extract_zip_file(self, zip_path: str, extract_dir: str) -> Dict[str, Any]:
        """📦 EXTRAIR ARQUIVO ZIP COM VALIDAÇÃO"""
        try:
            extracted_files = []
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # ✅ VERIFICAR INTEGRIDADE
                bad_file = zip_ref.testzip()
                if bad_file is not None:
                    return self._create_upload_error(f"ZIP corrompido: {bad_file}")
                
                # ✅ LISTAR CONTEÚDO
                file_list = zip_ref.namelist()
                self.logger.info(f"📦 Conteúdo do ZIP: {len(file_list)} itens")
                
                # ✅ EXTRAIR
                zip_ref.extractall(extract_dir)
                
                # ✅ VERIFICAR ARQUIVOS EXTRAÍDOS
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        extracted_files.append(full_path)
            
            return {
                'success': True,
                'extracted_files': extracted_files,
                'total_files': len(extracted_files)
            }
            
        except zipfile.BadZipFile:
            return self._create_upload_error("Arquivo ZIP inválido ou corrompido")
        except Exception as e:
            return self._create_upload_error(f"Erro na extração: {str(e)}")
    
    def _analyze_extracted_content(self, extract_dir: str) -> Dict[str, Any]:
        """🔍 ANALISAR CONTEÚDO EXTRAÍDO - DETECTAR JOGOS"""
        valid_files = []
        detected_appids = set()
        file_types = {
            'manifest': [],
            'lua': [],
            'other': []
        }
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                full_path = os.path.join(root, file)
                filename_lower = file.lower()
                
                # 🎯 FILTRAR APENAS ARQUIVOS VÁLIDOS
                if filename_lower.endswith('.manifest'):
                    file_types['manifest'].append(full_path)
                    valid_files.append(full_path)
                    
                    # 🔍 TENTAR DETECTAR APPID
                    appid = self._extract_appid_from_filename(file)
                    if appid:
                        detected_appids.add(appid)
                        
                elif filename_lower.endswith('.lua'):
                    file_types['lua'].append(full_path)
                    valid_files.append(full_path)
                    
                    # 🔍 TENTAR DETECTAR APPID EM SCRIPTS LUA
                    lua_appid = self._extract_appid_from_lua_file(full_path)
                    if lua_appid:
                        detected_appids.add(lua_appid)
                else:
                    file_types['other'].append(full_path)
        
        return {
            'valid_files': valid_files,
            'file_count': len(valid_files),
            'detected_appids': list(detected_appids),
            'file_types': file_types,
            'has_manifest_files': len(file_types['manifest']) > 0,
            'has_lua_files': len(file_types['lua']) > 0
        }
    
    def _extract_appid_from_lua_file(self, lua_path: str) -> Optional[str]:
        """🔍 EXTRAIR APPID DE ARQUIVO LUA"""
        try:
            with open(lua_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Padrões comuns em scripts LUA
            patterns = [
                r'app[_-]?id[\s\=\:]+[\'\""]?(\d{5,})[\'\""]?',
                r'AppID[\s\=\:]+(\d{5,})',
                r'steam[_-]?app[_-]?id[\s\=\:]+[\'\""]?(\d{5,})[\'\""]?',
                r'(\d{5,}).*manifest'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match and match.group(1).isdigit():
                    appid = match.group(1)
                    if 5 <= len(appid) <= 7:
                        self.logger.info(f"🔍 AppID detectado em LUA: {appid}")
                        return appid
                        
        except Exception as e:
            self.logger.debug(f"⚠️ Erro lendo arquivo LUA {lua_path}: {e}")
            
        return None
    
    def _extract_appid_from_filename(self, filename: str) -> Optional[str]:
        """🔍 EXTRAIR APPID DO NOME DO ARQUIVO"""
        patterns = [
            r'(\d{5,})',  # 5+ dígitos
            r'app?[_-]?(\d{5,})',
            r'(\d{5,})\.(manifest|lua)$',
            r'manifest_(\d{5,})\.manifest'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match and match.group(1).isdigit():
                appid = match.group(1)
                if 5 <= len(appid) <= 7:
                    return appid
        return None
    
    def _create_secure_temp_dir(self) -> Optional[str]:
        """🏗️ CRIAR DIRETÓRIO TEMPORÁRIO SEGURO"""
        try:
            temp_dir = tempfile.mkdtemp(prefix="steam_upload_")
            self.logger.info(f"📁 Diretório temporário criado: {temp_dir}")
            return temp_dir
        except Exception as e:
            self.logger.error(f"❌ Erro criando diretório temporário: {e}")
            return None
    
    def _cleanup_temp_dir(self):
        """🧹 LIMPEZA SEGURA DO DIRETÓRIO TEMPORÁRIO"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"🧹 Diretório temporário removido: {self.temp_dir}")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro limpando diretório temporário: {e}")
    
    def _create_upload_error(self, error_message: str) -> Dict[str, Any]:
        """📝 CRIAR RESULTADO DE ERRO PARA UPLOAD"""
        self.logger.error(f"❌ Erro no upload: {error_message}")
        return {
            'success': False,
            'error': error_message,
            'upload_metadata': {
                'zip_file': 'N/A',
                'extracted_files': 0,
                'valid_files_found': 0,
                'detected_appids': []
            }
        }


# 🎯 FUNÇÃO DE FÁCIL ACESSO - MANTIDA
def create_steam_backend() -> SteamBackend:
    """CRIAR INSTÂNCIA DO BACKEND STEAM ESPECIALIZADO EM PROCESSAMENTO"""
    return SteamBackend()

# ✅ FUNÇÃO DE FÁCIL ACESSO PARA UPLOADS
def create_zip_processor() -> ZipUploadProcessor:
    """CRIAR PROCESSADOR DE UPLOAD ZIP"""
    return ZipUploadProcessor()

# ✅ FUNÇÃO COMPATÍVEL COM API
def process_zip_upload(zip_file_path: str) -> Dict[str, Any]:
    """
    ✅ PROCESSAR UPLOAD DE ARQUIVO ZIP
    Função principal para integração com API
    """
    processor = ZipUploadProcessor()
    return processor.process_zip_upload(zip_file_path)

# ✅ FUNÇÃO DE PROCESSAMENTO COMPATÍVEL COM STORE_SEARCH
def process_downloaded_game_files(file_path: str, appid: str = None) -> Dict[str, Any]:
    """
    ✅ FUNÇÃO DE PROCESSAMENTO COMPATÍVEL COM STORE_SEARCH
    Processa arquivos baixados e os move para os diretórios Steam corretos
    """
    backend = SteamBackend()
    
    try:
        # Se for um diretório, processar todos os arquivos
        if os.path.isdir(file_path):
            files_to_process = []
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    if not backend._is_system_file(file):
                        files_to_process.append(full_path)
            
            if not files_to_process:
                return {
                    'success': False,
                    'error': 'Nenhum arquivo válido encontrado no diretório',
                    'files_processed': 0
                }
            
            result = backend.process_files(files_to_process)
            return result
        
        # Se for um arquivo, processar individualmente
        elif os.path.isfile(file_path):
            result = backend.process_files([file_path])
            return result
        
        else:
            return {
                'success': False,
                'error': f'Caminho inválido: {file_path}',
                'files_processed': 0
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro no processamento: {str(e)}',
            'files_processed': 0
        }


if __name__ == "__main__":
    # Exemplo de uso
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    backend = create_steam_backend()
    
    # Obter informações do Steam
    steam_info = backend.get_steam_info()
    print("Steam Info:", json.dumps(steam_info, indent=2))
    
    # Testar status
    status = backend.get_processing_status()
    print("Status:", json.dumps(status, indent=2))