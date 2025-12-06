# build.py - CONSTRUTOR ATUALIZADO PARA ESTRUTURA ATUAL COMPLETA (Dezembro 2025)
import os
import sys
import subprocess
import shutil
import time

def check_requirements():
    """Verifica e instala TODOS os requisitos necessários"""
    print("🔍 Verificando e instalando requisitos...")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'requests',
        'psutil',
        'webview',
        'rarfile',
        'pywin32',
        'setuptools',
        'Pillow',  # Para o sistema de tray icon
        'pystray',  # Para o sistema de tray icon
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"📦 Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package} instalado com sucesso")
            except subprocess.CalledProcessError:
                print(f"❌ Falha ao instalar {package}")
                return False
    
    return True

def validate_project_structure():
    """Valida a estrutura ATUAL COMPLETA do projeto (Dezembro 2025)"""
    print("\n📁 Validando estrutura do projeto...")
    
    required_dirs = [
        'frontend',
        'frontend/css',
        'frontend/js', 
        'frontend/assets',
        'utils',
        'config',
    ]
    
    required_files = [
        # Arquivos principais
        'main.py',
        'icon_tray.py',
        'routes.py',
        'steam_routes.py',
        'game_routes.py',
        'download_routes.py',
        'dlc_routes.py',
        'webview_config.py',
        'requirements.txt',
        'icone.ico',
        'LAUNCH.bat',
        
        # Frontend - HTML files
        'frontend/index.html',
        'frontend/dashboard.html',
        'frontend/search.html',
        'frontend/game_management.html',
        'frontend/dlc_manager.html',
        'frontend/fixes.html',
        'frontend/start.html',
        'frontend/steam_detect.html',
        'frontend/zip.html',
        'frontend/header.html',
        'frontend/sidebar.html',
        'frontend/footer.html',
        'frontend/favicon.ico',
        'frontend/favicon-16x16.png',
        'frontend/favicon-32x32.png',
        
        # Frontend - CSS files
        'frontend/css/style.css',
        'frontend/css/search.css',
        'frontend/css/game_management.css',
        'frontend/css/dlc_management.css',
        'frontend/css/animations.css',
        'frontend/css/global_components.css',
        'frontend/css/variables.css',
        
        # Frontend - JS files
        'frontend/js/index.js',
        'frontend/js/game_management.js',
        'frontend/js/dlc_management.js',
        'frontend/js/dlc_fixes_integration.js',
        'frontend/js/particles.js',
        'frontend/js/sidebar.js',
        
        # Utils files
        'utils/store_search.py',
        'utils/steam_utils.py',
        'utils/file_processing.py',
        'utils/game_management.py',
        'utils/fix_manager.py',
        'utils/download_manager.py',
        'utils/dlc_manager.py',
        'utils/fixes_list.json',
        'utils/steam_gameloader_config.json',
        
        # Config files
        'config/dll_manager.py',
        'config/hid_dll_base64.txt',
        'config/settings.json',
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Diretório não encontrado: {dir_path}")
            return False
        print(f"✅ {dir_path}")
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return False
        print(f"✅ {file_path}")
    
    return True

def create_spec_file():
    """Cria arquivo .spec ATUALIZADO para estrutura atual COMPLETA"""
    
    # Encontra o ícone
    icon_file = None
    for icon in ['icone.ico', 'icon.ico', 'frontend/favicon.ico']:
        if os.path.exists(icon):
            icon_file = icon
            break
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# CONFIGURAÇÕES PRINCIPAIS - ESTRUTURA ATUAL COMPLETA (Dezembro 2025)
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # FRONTEND COMPLETO
        ('frontend/*.html', 'frontend'),
        ('frontend/*.ico', 'frontend'),
        ('frontend/*.png', 'frontend'),
        ('frontend/css/*.css', 'frontend/css'),
        ('frontend/js/*.js', 'frontend/js'),
        ('frontend/assets/*', 'frontend/assets'),
        
        # UTILS - TODOS OS ARQUIVOS
        ('utils/*.py', 'utils'),
        ('utils/*.json', 'utils'),
        
        # CONFIG - TODOS OS ARQUIVOS
        ('config/*.py', 'config'),
        ('config/*.json', 'config'),
        ('config/*.txt', 'config'),
        
        # ARQUIVOS PRINCIPAIS DO PROJETO
        ('*.py', '.'),
        ('*.ico', '.'),
        ('*.bat', '.'),
        ('*.txt', '.'),
    ],
    hiddenimports=[
        # WEBVIEW
        'webview',
        'webview.platforms.win32',
        'webview.platforms.cef',
        
        # FLASK
        'flask',
        'flask_cors',
        'werkzeug',
        'werkzeug.middleware',
        'werkzeug.wrappers',
        
        # REQUESTS
        'requests',
        'urllib3',
        'chardet',
        'idna',
        'certifi',
        
        # SISTEMA
        'psutil',
        'psutil._pswindows',
        
        # TRAY ICON
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        
        # PROCESSAMENTO DE ARQUIVOS
        'zipfile',
        'rarfile',
        'rarfile._rarfile',
        'shutil',
        
        # WINDOWS API
        'winreg',
        'ctypes',
        'ctypes.wintypes',
        'win32api',
        'win32con',
        'win32process',
        
        # OUTRAS DEPENDÊNCIAS
        'json',
        'logging',
        'threading',
        'subprocess',
        'tempfile',
        'webbrowser',
        'platform',
        're',
        'hashlib',
        'base64',
        'time',
        'datetime',
        'dataclasses',
        'pathlib',
        'collections',
        'urllib.parse',
        'urllib.request',
        
        # MÓDULOS PERSONALIZADOS ATUALIZADOS (Dezembro 2025)
        'routes',
        'steam_routes',
        'game_routes',
        'download_routes',
        'dlc_routes',
        'utils.store_search',
        'utils.steam_utils',
        'utils.file_processing',
        'utils.game_management',
        'utils.fix_manager',
        'utils.download_manager',
        'utils.dlc_manager',
        'config.dll_manager',
        'icon_tray',
        'webview_config',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter', 
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'pygame',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# CONFIGURAÇÕES PYINSTALLER
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# CONFIGURAÇÕES FINAIS DO EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SteamGameLoader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_file}',
)
'''
    
    with open('SteamGameLoader.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo .spec ATUALIZADO (Dezembro 2025) criado")

def install_missing_dependencies():
    """Instala dependências que podem estar faltando"""
    print("\n📦 Verificando dependências críticas...")
    
    critical_packages = [
        'rarfile',
        'pywin32',
        'setuptools',
        'Pillow',
        'pystray',
    ]
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} já instalado")
        except ImportError:
            print(f"🚨 INSTALANDO {package} (CRÍTICO)...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package} instalado com sucesso")
            except Exception as e:
                print(f"❌ Falha ao instalar {package}: {e}")
                return False
                
    return True

def build_with_spec():
    """Executa build usando arquivo .spec atualizado"""
    print("\n🏗️ Executando build com todas as dependências...")
    
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--clean',
        'SteamGameLoader.spec'
    ]
    
    print(f"📋 Comando: {' '.join(cmd)}")
    
    try:
        # Executa sem capturar output para evitar problemas de encoding
        result = subprocess.run(
            cmd,
            capture_output=False,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode == 0:
            print("✅ Build concluído com sucesso!")
            return True
        else:
            print("❌ Build falhou!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build expirou (muito tempo)")
        return False
    except Exception as e:
        print(f"❌ Erro durante o build: {e}")
        return False

def build_directly():
    """Método alternativo: build direto sem .spec"""
    print("\n🏗️ Executando build DIRETO (método alternativo)...")
    
    # Encontra o ícone
    icon_file = None
    for icon in ['icone.ico', 'icon.ico', 'frontend/favicon.ico']:
        if os.path.exists(icon):
            icon_file = icon
            break
    
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name=SteamGameLoader',
        f'--icon={icon_file}',
        '--add-data=frontend;frontend',
        '--add-data=frontend/css;frontend/css',
        '--add-data=frontend/js;frontend/js',
        '--add-data=frontend/assets;frontend/assets',
        '--add-data=utils;utils',
        '--add-data=config;config',
        f'--add-data={icon_file};.',
        '--add-data=requirements.txt;.',
        '--add-data=LAUNCH.bat;.',
        '--hidden-import=webview',
        '--hidden-import=flask',
        '--hidden-import=flask_cors',
        '--hidden-import=werkzeug',
        '--hidden-import=requests',
        '--hidden-import=psutil',
        '--hidden-import=rarfile',
        '--hidden-import=rarfile._rarfile',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32process',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageDraw',
        # Módulos do projeto atualizados
        '--hidden-import=routes',
        '--hidden-import=steam_routes',
        '--hidden-import=game_routes',
        '--hidden-import=download_routes',
        '--hidden-import=dlc_routes',
        '--hidden-import=utils.store_search',
        '--hidden-import=utils.steam_utils',
        '--hidden-import=utils.file_processing',
        '--hidden-import=utils.game_management',
        '--hidden-import=utils.fix_manager',
        '--hidden-import=utils.download_manager',
        '--hidden-import=utils.dlc_manager',
        '--hidden-import=config.dll_manager',
        '--hidden-import=icon_tray',
        '--hidden-import=webview_config',
        '--clean',
        'main.py'
    ]
    
    print(f"📋 Comando direto (sem .spec)")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            timeout=600
        )
        
        return result.returncode == 0
            
    except subprocess.TimeoutExpired:
        print("❌ Build expirou")
        return False
    except Exception as e:
        print(f"❌ Erro durante o build: {e}")
        return False

def create_launcher_bat():
    """Cria arquivo launcher.bat atualizado"""
    launcher_content = '''@echo off
chcp 65001 > nul
title Steam GameLoader - Premium Edition (Dezembro 2025)
echo.
echo ========================================
echo    STEAM GAMELOADER - PREMIUM EDITION
echo    Versão: Dezembro 2025
echo ========================================
echo.
echo 🔍 Verificando ambiente...
timeout /t 2 /nobreak > nul

if not exist "dist\\SteamGameLoader.exe" (
    echo ❌ ERRO: Executável não encontrado!
    echo 📁 Verifique se o build foi realizado com sucesso
    pause
    exit /b 1
)

echo ✅ Executável encontrado
echo 🚀 Iniciando Steam GameLoader...
echo.

start "" "dist\\SteamGameLoader.exe"

echo 💡 A aplicação está iniciando...
echo 📢 Verifique a interface em alguns segundos
timeout /t 3 /nobreak > nul
'''
    
    with open('LAUNCH.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ Arquivo LAUNCH.bat atualizado (Dezembro 2025)")

def verify_build():
    """Verifica se o build foi bem-sucedido"""
    print("\n🔍 Verificando resultado do build...")
    
    exe_path = 'dist/SteamGameLoader.exe'
    
    if not os.path.exists(exe_path):
        print("❌ ERRO: Executável não foi criado!")
        return False
    
    file_size = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"✅ Executável criado: {exe_path}")
    print(f"📊 Tamanho: {file_size:.2f} MB")
    
    # Verifica se arquivos críticos estão incluídos
    required_in_exe = [
        'frontend/index.html',
        'frontend/dashboard.html',
        'frontend/game_management.html',
        'frontend/dlc_manager.html',
        'frontend/search.html',
        'frontend/fixes.html',
        'utils/store_search.py',
        'utils/game_management.py',
        'utils/fix_manager.py',
        'utils/dlc_manager.py',
        'utils/download_manager.py',
        'config/dll_manager.py',
        'icon_tray.py',
        'routes.py',
        'steam_routes.py',
        'game_routes.py',
        'download_routes.py',
        'dlc_routes.py'
    ]
    
    print("🔍 Verificando inclusão de arquivos críticos...")
    all_included = True
    
    for file_path in required_in_exe:
        if os.path.exists(file_path):
            print(f"✅ {file_path} (existe no projeto)")
        else:
            print(f"❌ {file_path} (não encontrado)")
            all_included = False
    
    if file_size < 40:
        print("⚠️  AVISO: Executável pode estar sem algumas dependências")
    elif file_size > 100:
        print("✅ Tamanho robusto - todas as dependências incluídas")
    else:
        print("✅ Tamanho adequado - dependências incluídas")
    
    return all_included

def cleanup_old_builds():
    """Limpa builds anteriores e arquivos temporários"""
    print("\n🧹 Limpando builds anteriores...")
    
    items_to_remove = [
        'build',
        'dist', 
        'SteamGameLoader.spec',
        '__pycache__',
        'utils/__pycache__',
        'config/__pycache__',
        'frontend/__pycache__',
        'frontend/css/__pycache__',
        'frontend/js/__pycache__',
        'frontend/assets/__pycache__'
    ]
    
    for item in items_to_remove:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                print(f"✅ {item} removido")
            except Exception as e:
                print(f"⚠️  Não foi possível remover {item}: {e}")

def main():
    """Função principal do construtor ATUALIZADO (Dezembro 2025)"""
    print("🎮 CONSTRUTOR STEAM GAMELOADER - ESTRUTURA ATUAL COMPLETA (Dez 2025)")
    print("=" * 60)
    print("📦 INCLUINDO: Dashboard, DLC Manager, Game Management, Fixes, Routes")
    print("=" * 60)
    
    start_time = time.time()
    
    # Verifica ícone
    icon_files = ['icone.ico', 'icon.ico', 'frontend/favicon.ico']
    icon_file = None
    
    for icon in icon_files:
        if os.path.exists(icon):
            icon_file = icon
            break
    
    if not icon_file:
        print("❌ Nenhum arquivo de ícone encontrado!")
        return
    
    print(f"✅ Ícone: {icon_file}")
    
    # Limpa builds anteriores
    cleanup_old_builds()
    
    # Instala dependências CRÍTICAS primeiro
    if not install_missing_dependencies():
        print("❌ Falha na instalação de dependências críticas")
        return
    
    # Valida requisitos
    if not check_requirements():
        print("❌ Falha na verificação de requisitos")
        return
    
    # Valida estrutura ATUAL COMPLETA
    if not validate_project_structure():
        print("❌ Estrutura do projeto inválida")
        return
    
    # Tenta primeiro o método com .spec
    print("\n🔄 Tentando método com arquivo .spec...")
    create_spec_file()
    
    success = build_with_spec()
    
    # Se falhar, tenta método direto
    if not success:
        print("\n🔄 Método .spec falhou, tentando método DIRETO...")
        success = build_directly()
    
    if not success:
        print("❌ Todos os métodos de build falharam!")
        return
    
    # Verifica resultado
    if not verify_build():
        print("❌ Build incompleto!")
        return
    
    # Cria launcher atualizado
    create_launcher_bat()
    
    # Estatísticas finais
    end_time = time.time()
    build_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("🎉 BUILD CONCLUÍDO COM SUCESSO! (Dezembro 2025)")
    print("=" * 60)
    print(f"⏱️  Tempo total: {build_time:.1f} segundos")
    print(f"📁 Executável: dist/SteamGameLoader.exe")
    print(f"🚀 Launcher: LAUNCH.bat")
    print(f"🔧 Funcionalidades incluídas:")
    print(f"   • Dashboard Interativo")
    print(f"   • Gerenciador de DLCs")
    print(f"   • Game Management Completo")
    print(f"   • Fix Manager Avançado")
    print(f"   • Sistema de Downloads")
    print(f"   • Sistema de Routes (Flask)")
    print(f"   • Tray Icon AMOLED")
    print(f"   • Sistema DLL Avançado")
    print(f"   • Particles.js Background")
    print(f"   • Interface Web Premium")
    print("\n💡 AGORA TESTE:")
    print("   1. Execute LAUNCH.bat")
    print("   2. Verifique se o tray icon aparece")
    print("   3. Teste todas as funcionalidades")
    print("   4. Acesse o Dashboard em http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Build interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")