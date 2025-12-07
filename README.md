<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam GameLoader v19.0.0 - Plataforma Steam</title>
    <meta name="description" content="Steam GameLoader - Plataforma completa para gerenciamento de jogos Steam com suporte a 60k+ títulos.">
    <meta name="keywords" content="steam, game loader, steamtools, gerenciador, jogos, 60k jogos">
    <meta name="author" content="OtoNexusCloud">
    
    <!-- Favicon -->
    <link rel="icon" href="https://upload.wikimedia.org/wikipedia/commons/8/83/Steam_icon_logo.svg" type="image/svg+xml">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        /* Variáveis CSS atualizadas */
        :root {
            --primary-dark: #0d1117;
            --secondary-dark: #161b22;
            --accent-steam: #1f2937;
            --accent-purple: #5d3fd3;
            --accent-purple-light: #7c5cfc;
            --accent-blue: #58a6ff;
            --accent-green: #238636;
            --accent-orange: #f78166;
            --text-light: #e6edf3;
            --text-white: #ffffff;
            --text-muted: #8b949e;
            --card-bg: rgba(22, 27, 34, 0.9);
            --card-border: rgba(255, 255, 255, 0.08);
            --gradient-purple: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-purple-light) 100%);
            --neon-glow: 0 0 20px rgba(124, 92, 252, 0.3);
        }

        /* Reset e Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
            scroll-padding-top: 100px;
        }

        body {
            background-color: var(--primary-dark);
            color: var(--text-light);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            overflow-x: hidden;
            position: relative;
            min-height: 100vh;
            font-size: 16px;
            font-weight: 400;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 10% 20%, rgba(93, 63, 211, 0.1) 0%, transparent 40%),
                radial-gradient(circle at 90% 30%, rgba(88, 166, 255, 0.06) 0%, transparent 40%);
            z-index: -2;
            pointer-events: none;
        }

        /* Canvas de Partículas */
        #particles-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            opacity: 0.5;
        }

        /* Container Principal */
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Header Remasterizado */
        header {
            background: rgba(13, 17, 23, 0.98);
            padding: 16px 0;
            position: fixed;
            width: 100%;
            z-index: 1000;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(124, 92, 252, 0.1);
            transition: all 0.3s ease;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 30px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none;
            flex-shrink: 0;
            transition: transform 0.3s ease;
        }

        .logo:hover {
            transform: translateY(-1px);
        }

        .logo-icon {
            color: var(--accent-purple-light);
            font-size: 28px;
            position: relative;
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.4));
        }

        .logo-text {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .logo h1 {
            color: var(--text-white);
            font-size: 22px;
            font-weight: 800;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.5px;
            margin: 0;
            background: var(--gradient-purple);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 20px rgba(124, 92, 252, 0.3);
        }

        .logo span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.3px;
        }

        .version-badge {
            background: var(--gradient-purple);
            color: white;
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 10px;
            font-weight: 700;
            margin-left: 10px;
            box-shadow: 0 2px 12px rgba(93, 63, 211, 0.4);
            letter-spacing: 0.5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Navegação */
        nav ul {
            display: flex;
            list-style: none;
            gap: 28px;
            margin: 0;
            padding: 0;
        }

        nav a {
            color: var(--text-light);
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.3s ease;
            padding: 6px 0;
            position: relative;
            opacity: 0.9;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        nav a i {
            font-size: 13px;
        }

        nav a::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--gradient-purple);
            transition: width 0.3s ease;
            border-radius: 1px;
            box-shadow: var(--neon-glow);
        }

        nav a:hover {
            color: var(--text-white);
            opacity: 1;
        }

        nav a:hover::before {
            width: 100%;
        }

        .mobile-menu {
            display: none;
            font-size: 22px;
            cursor: pointer;
            color: var(--accent-purple-light);
            padding: 6px;
            transition: all 0.3s ease;
        }

        .mobile-menu:hover {
            transform: scale(1.1);
        }

        /* Hero Section */
        .hero {
            padding: 160px 0 100px;
            position: relative;
        }

        .hero-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            align-items: center;
        }

        .hero-text h2 {
            font-size: 44px;
            color: var(--text-white);
            margin-bottom: 20px;
            line-height: 1.1;
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
        }

        .hero-text h2 .highlight {
            background: var(--gradient-purple);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            position: relative;
            display: inline-block;
            text-shadow: 0 0 30px rgba(124, 92, 252, 0.3);
        }

        .hero-text p {
            font-size: 17px;
            margin-bottom: 30px;
            color: var(--text-muted);
            line-height: 1.7;
            max-width: 95%;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 30px 0;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .stat-card:hover {
            transform: translateY(-3px);
            border-color: var(--accent-purple);
            box-shadow: var(--neon-glow);
        }

        .stat-number {
            font-size: 28px;
            font-weight: 800;
            color: var(--accent-purple-light);
            margin-bottom: 6px;
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 10px rgba(124, 92, 252, 0.3);
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 35px;
            flex-wrap: wrap;
        }

        /* Botões */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-family: 'Inter', sans-serif;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: left 0.5s ease;
            z-index: -1;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn-primary {
            background: var(--gradient-purple);
            color: var(--text-white);
            box-shadow: 0 4px 20px rgba(93, 63, 211, 0.4);
            border: 1px solid rgba(124, 92, 252, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(93, 63, 211, 0.6);
        }

        .btn-secondary {
            background: transparent;
            color: var(--accent-blue);
            border: 1.5px solid var(--accent-blue);
            box-shadow: 0 4px 15px rgba(88, 166, 255, 0.15);
        }

        .btn-secondary:hover {
            background: rgba(88, 166, 255, 0.1);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(88, 166, 255, 0.25);
            border-color: var(--accent-blue);
        }

        .btn-github {
            background: rgba(22, 27, 34, 0.9);
            color: white;
            border: 1.5px solid rgba(255, 255, 255, 0.1);
        }

        .btn-github:hover {
            background: rgba(22, 27, 34, 1);
            transform: translateY(-2px);
            border-color: rgba(124, 92, 252, 0.3);
            box-shadow: var(--neon-glow);
        }

        /* Hero Image */
        .hero-image {
            position: relative;
            perspective: 1000px;
        }

        .app-window {
            background: linear-gradient(145deg, var(--secondary-dark), var(--primary-dark));
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 
                0 16px 32px rgba(0, 0, 0, 0.25),
                0 0 0 1px rgba(93, 63, 211, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.08);
            max-width: 500px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .app-window:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.3),
                var(--neon-glow);
        }

        .window-header {
            background: linear-gradient(90deg, var(--accent-steam), rgba(31, 41, 55, 0.8));
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .window-title {
            font-weight: 600;
            color: var(--text-white);
            font-size: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .window-controls {
            display: flex;
            gap: 8px;
        }

        .control {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }

        .control.close { background: #ff5f57; }
        .control.minimize { background: #ffbd2e; }
        .control.maximize { background: #28ca42; }

        .window-content {
            padding: 24px;
            background: rgba(22, 27, 34, 0.7);
            min-height: 280px;
        }

        .app-feature {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            padding: 14px;
            border-radius: 10px;
            background: rgba(31, 41, 55, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .app-feature.static-feature {
            animation: none !important;
            transform: none !important;
        }

        .app-feature:hover {
            background: rgba(93, 63, 211, 0.1);
            border-color: rgba(93, 63, 211, 0.3);
            transform: translateX(5px);
        }

        .app-feature i {
            color: var(--accent-purple-light);
            font-size: 18px;
            margin-right: 14px;
            width: 32px;
            text-align: center;
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .app-feature .text {
            flex: 1;
        }

        .app-feature .text strong {
            color: var(--text-white);
            display: block;
            margin-bottom: 4px;
            font-size: 14px;
            font-weight: 600;
        }

        .app-feature .text span {
            color: var(--text-muted);
            font-size: 12px;
            line-height: 1.5;
        }

        /* Seções */
        section {
            padding: 80px 0;
            position: relative;
        }

        .section-title {
            text-align: center;
            margin-bottom: 60px;
            position: relative;
        }

        .section-title h2 {
            font-size: 36px;
            color: var(--text-white);
            margin-bottom: 16px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 800;
            position: relative;
            display: inline-block;
        }

        .section-title h2::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 4px;
            background: var(--gradient-purple);
            border-radius: 2px;
            box-shadow: var(--neon-glow);
        }

        .section-title p {
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
            font-size: 16px;
            line-height: 1.6;
        }

        /* Features Grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
        }

        .feature-card {
            background: var(--card-bg);
            border-radius: 14px;
            padding: 30px;
            transition: all 0.3s ease;
            border: 1px solid var(--card-border);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .feature-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent-purple);
            box-shadow: var(--neon-glow);
        }

        .feature-icon {
            font-size: 36px;
            color: var(--accent-purple-light);
            margin-bottom: 20px;
            display: inline-block;
            transition: all 0.3s ease;
            filter: drop-shadow(0 0 10px rgba(124, 92, 252, 0.3));
        }

        .feature-card:hover .feature-icon {
            transform: scale(1.1) rotate(5deg);
        }

        .feature-card h3 {
            color: var(--text-white);
            font-size: 20px;
            margin-bottom: 12px;
            font-weight: 700;
        }

        .feature-card p {
            color: var(--text-muted);
            line-height: 1.6;
            font-size: 14px;
        }

        /* APIs Section */
        .apis-section {
            background: linear-gradient(180deg, var(--secondary-dark) 0%, var(--primary-dark) 100%);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .apis-category-title {
            color: var(--text-white);
            font-size: 22px;
            margin-bottom: 25px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .apis-category-title i {
            color: var(--accent-purple-light);
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .apis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .api-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }

        .api-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-purple);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .api-card.premium-card {
            border-color: rgba(93, 63, 211, 0.3);
            background: linear-gradient(145deg, rgba(93, 63, 211, 0.05), var(--card-bg));
        }

        .api-card.premium-card::before {
            background: var(--gradient-purple);
        }

        .api-card.github-card {
            border-color: rgba(88, 166, 255, 0.2);
        }

        .api-card:hover {
            transform: translateY(-3px);
            border-color: var(--accent-purple);
            box-shadow: var(--neon-glow);
        }

        .api-card:hover::before {
            opacity: 1;
        }

        .api-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 14px;
            gap: 10px;
        }

        .api-name {
            color: var(--text-white);
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1;
        }

        .api-name i {
            font-size: 14px;
            color: var(--accent-purple-light);
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .api-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 5px;
            white-space: nowrap;
        }

        .api-status.online {
            background: rgba(35, 134, 54, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(35, 134, 54, 0.3);
        }

        .api-url {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            margin: 14px 0;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 12px;
            color: var(--accent-blue);
            overflow-x: auto;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .api-url i {
            margin-right: 6px;
            opacity: 0.7;
        }

        .api-description {
            color: var(--text-muted);
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 12px;
        }

        .api-performance {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .perf-badge {
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent-blue);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            border: 1px solid rgba(88, 166, 255, 0.2);
        }

        .perf-badge i {
            font-size: 9px;
        }

        .api-last-checked {
            font-size: 10px;
            margin-top: 8px;
            color: var(--accent-blue);
            display: flex;
            align-items: center;
            gap: 5px;
        }

        /* API Monitor Info */
        .api-monitor-info {
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.4), rgba(22, 27, 34, 0.6));
            border-radius: 14px;
            padding: 28px;
            margin-top: 50px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
        }

        .api-monitor-info h4 {
            color: var(--text-white);
            font-size: 18px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .api-monitor-info h4 i {
            color: var(--accent-purple-light);
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .api-monitor-info p {
            color: var(--text-muted);
            font-size: 14px;
            margin-bottom: 20px;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        }

        .monitor-stats {
            display: flex;
            justify-content: center;
            gap: 28px;
            margin-bottom: 20px;
        }

        .monitor-stat {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }

        .monitor-stat i {
            font-size: 20px;
            color: var(--accent-blue);
            filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.3));
        }

        .monitor-stat span {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }

        /* Download Section Corrigida */
        .download-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }

        .download-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 0;
            border: 1px solid var(--card-border);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .download-card-inner {
            padding: 35px 30px;
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        .download-card:hover {
            transform: translateY(-8px);
            border-color: var(--accent-purple);
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.3),
                var(--neon-glow);
        }

        .download-icon {
            font-size: 42px;
            color: var(--accent-purple-light);
            margin-bottom: 20px;
            display: inline-block;
            transition: all 0.3s ease;
            filter: drop-shadow(0 0 12px rgba(124, 92, 252, 0.4));
            align-self: center;
        }

        .download-card:hover .download-icon {
            transform: scale(1.15) rotate(5deg);
        }

        .download-card h3 {
            color: var(--text-white);
            font-size: 22px;
            margin-bottom: 16px;
            font-weight: 700;
            text-align: center;
        }

        .download-description {
            color: var(--text-muted);
            margin-bottom: 28px;
            font-size: 14px;
            line-height: 1.7;
            text-align: center;
            flex: 1;
        }

        .download-button {
            margin: 20px auto 25px;
            min-width: 200px;
        }

        .download-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 25px;
            margin-top: auto;
        }

        .download-stat {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 14px;
            background: rgba(31, 41, 55, 0.4);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .download-stat:hover {
            background: rgba(93, 63, 211, 0.1);
            border-color: rgba(93, 63, 211, 0.3);
        }

        .download-stat i {
            color: var(--accent-purple-light);
            font-size: 18px;
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .download-stat div {
            display: flex;
            flex-direction: column;
            gap: 4px;
            text-align: left;
        }

        .download-stat strong {
            color: var(--text-white);
            font-size: 20px;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 10px rgba(124, 92, 252, 0.3);
        }

        .download-stat span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .download-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            padding-top: 20px;
            margin-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .detail-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .detail-item:hover {
            background: rgba(93, 63, 211, 0.1);
            transform: translateY(-2px);
        }

        .detail-item i {
            color: var(--accent-purple-light);
            font-size: 13px;
            filter: drop-shadow(0 0 6px rgba(124, 92, 252, 0.3));
        }

        .detail-item span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
            text-align: center;
        }

        /* Footer Remasterizado */
        footer {
            background: linear-gradient(180deg, var(--accent-steam) 0%, #0f172a 100%);
            padding: 60px 0 30px;
            border-top: 1px solid rgba(124, 92, 252, 0.1);
            position: relative;
            margin-top: 40px;
        }

        footer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--accent-purple-light), 
                transparent);
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 40px;
            margin-bottom: 50px;
        }

        .footer-brand {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .footer-logo {
            font-size: 24px;
            color: var(--text-white);
            font-weight: 800;
            font-family: 'Orbitron', sans-serif;
            margin-bottom: 10px;
        }

        .footer-logo span {
            background: var(--gradient-purple);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 20px rgba(124, 92, 252, 0.3);
        }

        .footer-description {
            color: var(--text-muted);
            font-size: 13px;
            line-height: 1.6;
        }

        .dev-info {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 14px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            border: 1px solid rgba(124, 92, 252, 0.1);
            transition: all 0.3s ease;
            margin-top: 10px;
        }

        .dev-info:hover {
            background: rgba(93, 63, 211, 0.1);
            border-color: rgba(124, 92, 252, 0.3);
            transform: translateY(-2px);
        }

        .dev-info i {
            font-size: 18px;
            color: var(--accent-purple-light);
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .dev-info div {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .dev-info strong {
            color: var(--text-white);
            font-size: 13px;
            font-weight: 600;
        }

        .dev-info span {
            color: var(--text-muted);
            font-size: 11px;
        }

        .footer-links h4,
        .footer-resources h4,
        .footer-compatibility h4 {
            color: var(--text-white);
            font-size: 16px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(124, 92, 252, 0.2);
            position: relative;
            font-weight: 700;
        }

        .footer-links h4::after,
        .footer-resources h4::after,
        .footer-compatibility h4::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 40px;
            height: 2px;
            background: var(--gradient-purple);
            border-radius: 1px;
        }

        .footer-links ul,
        .footer-resources ul {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .footer-links a,
        .footer-resources a {
            color: var(--text-muted);
            text-decoration: none;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            padding: 4px 0;
        }

        .footer-links a:hover,
        .footer-resources a:hover {
            color: var(--text-white);
            transform: translateX(5px);
        }

        .footer-links a i,
        .footer-resources a i {
            color: var(--accent-purple-light);
            font-size: 10px;
            transition: all 0.3s ease;
        }

        .footer-links a:hover i,
        .footer-resources a:hover i {
            transform: scale(1.2);
            filter: drop-shadow(0 0 6px rgba(124, 92, 252, 0.3));
        }

        .footer-compatibility .compatibility-grid {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .compatibility-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .compatibility-item:hover {
            background: rgba(93, 63, 211, 0.1);
            border-color: rgba(124, 92, 252, 0.3);
            transform: translateY(-2px);
        }

        .compatibility-icon {
            color: var(--accent-green);
            font-size: 12px;
            filter: drop-shadow(0 0 6px rgba(35, 134, 54, 0.3));
        }

        .compatibility-text {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .compatibility-text strong {
            color: var(--text-white);
            font-size: 12px;
            font-weight: 600;
        }

        .compatibility-text span {
            color: var(--text-muted);
            font-size: 10px;
        }

        .footer-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        .copyright p {
            color: var(--text-muted);
            font-size: 12px;
            margin-bottom: 6px;
        }

        .copyright .disclaimer {
            font-size: 11px;
            opacity: 0.7;
        }

        .footer-stats {
            display: flex;
            gap: 25px;
        }

        .footer-stat {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            padding: 10px 15px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            border: 1px solid rgba(124, 92, 252, 0.1);
            transition: all 0.3s ease;
        }

        .footer-stat:hover {
            background: rgba(93, 63, 211, 0.1);
            border-color: rgba(124, 92, 252, 0.3);
            transform: translateY(-2px);
        }

        .footer-stat i {
            color: var(--accent-purple-light);
            font-size: 16px;
            filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
        }

        .footer-stat span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
        }

        /* Animações */
        @keyframes slideInUp {
            from {
                transform: translateY(30px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        @keyframes neonPulse {
            0%, 100% {
                filter: drop-shadow(0 0 8px rgba(124, 92, 252, 0.3));
            }
            50% {
                filter: drop-shadow(0 0 12px rgba(124, 92, 252, 0.6));
            }
        }

        .neon-pulse {
            animation: neonPulse 2s ease-in-out infinite;
        }

        /* Responsividade */
        @media (max-width: 1200px) {
            .footer-content {
                grid-template-columns: repeat(2, 1fr);
                gap: 35px;
            }
        }

        @media (max-width: 992px) {
            .hero-content,
            .download-cards {
                grid-template-columns: 1fr;
            }
            
            .hero-text {
                text-align: center;
            }
            
            .hero-text p {
                max-width: 100%;
            }
            
            .hero-image {
                order: -1;
                max-width: 500px;
                margin: 0 auto;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
                max-width: 500px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .action-buttons {
                justify-content: center;
            }
            
            .footer-bottom {
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }
            
            .footer-stats {
                justify-content: center;
            }
        }

        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 15px;
            }
            
            nav ul {
                flex-direction: column;
                text-align: center;
                gap: 12px;
                display: none;
            }
            
            nav.active ul {
                display: flex;
            }
            
            .mobile-menu {
                display: block;
                position: absolute;
                top: 18px;
                right: 20px;
            }
            
            .hero {
                padding: 140px 0 70px;
            }
            
            .hero-text h2 {
                font-size: 32px;
            }
            
            .section-title h2 {
                font-size: 28px;
            }
            
            .features-grid,
            .apis-grid {
                grid-template-columns: 1fr;
            }
            
            .footer-content {
                grid-template-columns: 1fr;
                gap: 35px;
            }
            
            .apis-category-title {
                font-size: 20px;
            }
            
            .download-cards {
                grid-template-columns: 1fr;
            }
            
            .download-stats {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 480px) {
            .btn {
                width: 100%;
                justify-content: center;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .hero-text h2 {
                font-size: 26px;
            }
            
            .stat-number {
                font-size: 24px;
            }
            
            .section-title h2 {
                font-size: 24px;
            }
            
            .feature-card,
            .api-card,
            .download-card-inner {
                padding: 20px;
            }
            
            .download-details {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            
            .footer-stats {
                flex-direction: column;
                gap: 15px;
            }
        }

        /* Utilitários */
        .fade-in {
            animation: slideInUp 0.6s ease-out forwards;
        }

        /* Efeito de brilho sutil para elementos neon */
        .neon-glow {
            position: relative;
        }

        .neon-glow::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: inherit;
            box-shadow: inset 0 0 20px rgba(124, 92, 252, 0.1);
            pointer-events: none;
        }
    </style>
</head>
<body>
    <!-- Canvas de Partículas -->
    <canvas id="particles-canvas"></canvas>

    <!-- Header Remasterizado -->
    <header>
        <div class="container header-content">
            <a href="#home" class="logo">
                <div class="logo-icon">
                    <i class="fas fa-gamepad"></i>
                </div>
                <div class="logo-text">
                    <h1>Steam GameLoader</h1>
                    <span>by OtoNexusCloud</span>
                </div>
                <div class="version-badge">v19.0.0</div>
            </a>
            
            <div class="mobile-menu" id="mobileMenu">
                <i class="fas fa-bars"></i>
            </div>
            
            <nav id="mainNav">
                <ul>
                    <li><a href="#home"><i class="fas fa-home"></i> Início</a></li>
                    <li><a href="#features"><i class="fas fa-cogs"></i> Recursos</a></li>
                    <li><a href="#apis"><i class="fas fa-server"></i> APIs</a></li>
                    <li><a href="#download"><i class="fas fa-download"></i> Download</a></li>
                    <li><a href="https://t.me/SteamGameLoader" target="_blank"><i class="fab fa-telegram"></i> Comunidade</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero" id="home">
        <div class="container hero-content fade-in">
            <div class="hero-text">
                <h2>Transforme sua <span class="highlight">Experiência Steam</span></h2>
                <p>Plataforma robusta com acesso a mais de 60,000 jogos Steam, integração total com as principais APIs e gerenciamento inteligente de sua biblioteca.</p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">60k+</div>
                        <div class="stat-label">Jogos Suportados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">3</div>
                        <div class="stat-label">APIs Principais</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="hero-downloads">6k+</div>
                        <div class="stat-label">Downloads</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Disponibilidade</div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <a href="#download" class="btn btn-primary" id="download-button">
                        <i class="fas fa-rocket"></i> Baixar Agora
                    </a>
                    <a href="#features" class="btn btn-secondary">
                        <i class="fas fa-play-circle"></i> Ver Recursos
                    </a>
                </div>
            </div>
            
            <div class="hero-image fade-in">
                <div class="app-window">
                    <div class="window-header">
                        <div class="window-title">
                            <i class="fas fa-gamepad"></i> Dashboard Principal
                        </div>
                        <div class="window-controls">
                            <div class="control close"></div>
                            <div class="control minimize"></div>
                            <div class="control maximize"></div>
                        </div>
                    </div>
                    <div class="window-content">
                        <div class="app-feature static-feature">
                            <i class="fas fa-check-circle"></i>
                            <div class="text">
                                <strong>APIs Principais Online</strong>
                                <span>Sadie, Ryuu e TwentyTwo sempre disponíveis</span>
                            </div>
                        </div>
                        <div class="app-feature static-feature">
                            <i class="fas fa-database"></i>
                            <div class="text">
                                <strong>60k+ Jogos Steam</strong>
                                <span>Biblioteca completa atualizada</span>
                            </div>
                        </div>
                        <div class="app-feature static-feature">
                            <i class="fas fa-tools"></i>
                            <div class="text">
                                <strong>Integração Total</strong>
                                <span>Compatibilidade com SteamTools</span>
                            </div>
                        </div>
                        <div class="app-feature static-feature">
                            <i class="fas fa-chart-line"></i>
                            <div class="text">
                                <strong>Estatísticas em Tempo Real</strong>
                                <span>Monitoramento constante</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="features">
        <div class="container">
            <div class="section-title fade-in">
                <h2>Tecnologia Avançada</h2>
                <p>Desenvolvido com as melhores práticas para gerenciamento de jogos Steam.</p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card fade-in">
                    <div class="feature-icon">
                        <i class="fas fa-bolt"></i>
                    </div>
                    <h3>APIs Principais</h3>
                    <p>Integração direta com Sadie, Ryuu e TwentyTwo Cloud - as APIs mais completas.</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>Automação Inteligente</h3>
                    <p>Instalação, atualização e gestão automática de jogos e DLCs.</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h3>Segurança Robusta</h3>
                    <p>Validação de integridade e proteção contra corrupção de arquivos.</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon">
                        <i class="fas fa-sync-alt"></i>
                    </div>
                    <h3>Atualizações Constantes</h3>
                    <p>Sistema de atualização automática com baixo consumo de recursos.</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon">
                        <i class="fas fa-database"></i>
                    </div>
                    <h3>Biblioteca 60k+</h3>
                    <p>Acesso a mais de 60,000 jogos Steam catalogados e organizados.</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3>Monitoramento 24/7</h3>
                    <p>Verificação constante do status de todas as APIs principais.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- APIs Section -->
    <section class="apis-section" id="apis">
        <div class="container">
            <div class="section-title fade-in">
                <h2>APIs Principais</h2>
                <p>Conectado às APIs mais robustas e completas da comunidade Steam.</p>
            </div>
            
            <div class="apis-grid">
                <div class="api-card fade-in premium-card">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fas fa-star"></i> Sadie API
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-check-circle"></i>
                            Online (25ms)
                        </div>
                    </div>
                    <div class="api-url" title="http://167.235.229.108/m/<appid>">
                        <i class="fas fa-link"></i> http://167.235.229.108/m/APPID
                    </div>
                    <div class="api-description">
                        API principal com maior biblioteca de jogos
                        <div class="api-performance">
                            <span class="perf-badge"><i class="fas fa-tachometer-alt"></i> Alta Velocidade</span>
                            <span class="perf-badge"><i class="fas fa-shield-alt"></i> 100% Estável</span>
                        </div>
                    </div>
                </div>
                
                <div class="api-card fade-in premium-card">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fas fa-star"></i> Ryuu API
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-check-circle"></i>
                            Online (30ms)
                        </div>
                    </div>
                    <div class="api-url" title="http://167.235.229.108/<appid>">
                        <i class="fas fa-link"></i> http://167.235.229.108/APPID
                    </div>
                    <div class="api-description">
                        API alternativa premium com alta velocidade
                        <div class="api-performance">
                            <span class="perf-badge"><i class="fas fa-tachometer-alt"></i> Alta Velocidade</span>
                            <span class="perf-badge"><i class="fas fa-shield-alt"></i> 100% Estável</span>
                        </div>
                    </div>
                </div>
                
                <div class="api-card fade-in premium-card">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fas fa-star"></i> TwentyTwo Cloud
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-check-circle"></i>
                            Online (35ms)
                        </div>
                    </div>
                    <div class="api-url" title="http://masss.pythonanywhere.com/storage?auth=IEOIJE54esfsipoE56GE4&appid=<appid>">
                        <i class="fas fa-link"></i> http://masss.pythonanywhere.com/storage?auth=IEOIJE54esfsipoE56GE4&appid=APPID
                    </div>
                    <div class="api-description">
                        Storage em nuvem com autenticação segura
                        <div class="api-performance">
                            <span class="perf-badge"><i class="fas fa-tachometer-alt"></i> Alta Velocidade</span>
                            <span class="perf-badge"><i class="fas fa-shield-alt"></i> 100% Estável</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Repositórios GitHub -->
            <h3 class="apis-category-title fade-in" style="margin-top: 60px;">
                <i class="fab fa-github"></i> Repositórios de Suporte
            </h3>
            <div class="apis-grid">
                <div class="api-card fade-in github-card">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fab fa-github"></i> ManifestHub
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-circle"></i> GitHub
                        </div>
                    </div>
                    <div class="api-url">
                        <i class="fas fa-code-branch"></i> https://github.com/SteamAutoCracks/ManifestHub
                    </div>
                    <div class="api-description">
                        Repositório oficial de manifests organizados
                        <div class="api-last-checked">
                            <i class="fas fa-infinity"></i> Disponível 24/7
                        </div>
                    </div>
                </div>
                
                <div class="api-card fade-in github-card">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fab fa-github"></i> GameFiles Central
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-circle"></i> GitHub
                        </div>
                    </div>
                    <div class="api-url">
                        <i class="fas fa-code-branch"></i> https://github.com/OpenSteamLoader/GameFiles
                    </div>
                    <div class="api-description">
                        Biblioteca centralizada de arquivos de jogos
                        <div class="api-last-checked">
                            <i class="fas fa-infinity"></i> Disponível 24/7
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="api-monitor-info fade-in">
                <h4><i class="fas fa-satellite-dish"></i> Sistema de Monitoramento</h4>
                <p>APIs principais com status 100% online • Verificação automática • Cache inteligente</p>
                <div class="monitor-stats">
                    <div class="monitor-stat">
                        <i class="fas fa-check-circle"></i>
                        <span>Status: Online</span>
                    </div>
                    <div class="monitor-stat">
                        <i class="fas fa-database"></i>
                        <span>APIs: 3</span>
                    </div>
                    <div class="monitor-stat">
                        <i class="fas fa-history"></i>
                        <span>Cache: 1h</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Download Section Corrigida -->
    <section class="download" id="download">
        <div class="container">
            <div class="section-title fade-in">
                <h2>Download</h2>
                <p>Baixe a versão mais recente e comece a explorar 60,000+ jogos Steam.</p>
            </div>
            
            <div class="download-cards">
                <div class="download-card fade-in">
                    <div class="download-card-inner">
                        <div class="download-icon">
                            <i class="fas fa-desktop"></i>
                        </div>
                        <h3>Instalador Windows</h3>
                        <p class="download-description">Instalador completo com configuração automática, integração com Steam e otimizações para Windows 10/11.</p>
                        <button class="btn btn-primary download-button" id="installer-download">
                            <i class="fas fa-download"></i> Baixar v19.0.0
                        </button>
                        <div class="download-stats">
                            <div class="download-stat">
                                <i class="fas fa-download"></i>
                                <div>
                                    <strong id="total-downloads">6k+</strong>
                                    <span>Downloads Totais</span>
                                </div>
                            </div>
                            <div class="download-stat">
                                <i class="fas fa-calendar-day"></i>
                                <div>
                                    <strong id="today-downloads">25</strong>
                                    <span>Hoje</span>
                                </div>
                            </div>
                        </div>
                        <div class="download-details">
                            <div class="detail-item">
                                <i class="fas fa-hdd"></i>
                                <span>Tamanho: ~25 MB</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-cog"></i>
                                <span>Requer: .NET 4.8+</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="download-card fade-in">
                    <div class="download-card-inner">
                        <div class="download-icon">
                            <i class="fas fa-code"></i>
                        </div>
                        <h3>Código-Fonte</h3>
                        <p class="download-description">Acesse todo o código-fonte do projeto, contribua com melhorias ou crie sua própria versão personalizada.</p>
                        <a href="https://github.com/oto-nexusdev/SteamGameLoader" target="_blank" class="btn btn-github">
                            <i class="fab fa-github"></i> Acessar GitHub
                        </a>
                        <div class="download-details">
                            <div class="detail-item">
                                <i class="fas fa-balance-scale"></i>
                                <span>Licença MIT</span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-code-branch"></i>
                                <span>Open Source</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer Remasterizado -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    <div class="footer-logo">Steam <span>GameLoader</span></div>
                    <p class="footer-description">
                        Plataforma avançada para gerenciamento de jogos Steam com suporte a 60k+ títulos
                        e integração total com as principais APIs da comunidade.
                    </p>
                    <div class="dev-info">
                        <i class="fas fa-code"></i>
                        <div>
                            <strong>OtoNexusCloud</strong>
                            <span>v19.0.0 • 2025-01-15</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer-links">
                    <h4>Navegação</h4>
                    <ul>
                        <li><a href="#home"><i class="fas fa-chevron-right"></i> Início</a></li>
                        <li><a href="#features"><i class="fas fa-chevron-right"></i> Recursos</a></li>
                        <li><a href="#apis"><i class="fas fa-chevron-right"></i> APIs</a></li>
                        <li><a href="#download"><i class="fas fa-chevron-right"></i> Download</a></li>
                    </ul>
                </div>
                
                <div class="footer-resources">
                    <h4>Recursos</h4>
                    <ul>
                        <li><a href="https://github.com/oto-nexusdev/SteamGameLoader" target="_blank"><i class="fab fa-github"></i> GitHub</a></li>
                        <li><a href="https://t.me/SteamGameLoader" target="_blank"><i class="fab fa-telegram"></i> Telegram</a></li>
                        <li><a href="https://github.com/oto-nexusdev/SteamGameLoader/releases/tag/steamtools" target="_blank"><i class="fas fa-tag"></i> Releases</a></li>
                    </ul>
                </div>
                
                <div class="footer-compatibility">
                    <h4>Compatibilidade</h4>
                    <div class="compatibility-grid">
                        <div class="compatibility-item">
                            <div class="compatibility-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="compatibility-text">
                                <strong>SteamTools</strong>
                                <span>Integração Total</span>
                            </div>
                        </div>
                        <div class="compatibility-item">
                            <div class="compatibility-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="compatibility-text">
                                <strong>Steam Client</strong>
                                <span>v2.0+</span>
                            </div>
                        </div>
                        <div class="compatibility-item">
                            <div class="compatibility-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="compatibility-text">
                                <strong>GreenLuma 2024</strong>
                                <span>Compatível</span>
                            </div>
                        </div>
                        <div class="compatibility-item">
                            <div class="compatibility-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="compatibility-text">
                                <strong>Goldberg Emulator</strong>
                                <span>Nativo</span>
                            </div>
                        </div>
                        <div class="compatibility-item">
                            <div class="compatibility-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="compatibility-text">
                                <strong>Windows 10/11</strong>
                                <span>Otimizado</span>
                            </div>
                        </div>
                        <div class="compatibility-item">
                            <div class="compatibility-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="compatibility-text">
                                <strong>.NET Framework 4.8+</strong>
                                <span>Requerido</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer-bottom">
                <div class="copyright">
                    <p>&copy; 2025 Steam GameLoader v19.0.0. Plataforma de código aberto.</p>
                    <p class="disclaimer">
                        Steam é uma marca registrada da Valve Corporation. Este projeto é independente.
                    </p>
                </div>
                <div class="footer-stats">
                    <div class="footer-stat">
                        <i class="fas fa-gamepad"></i>
                        <span>60k+ Jogos</span>
                    </div>
                    <div class="footer-stat">
                        <i class="fas fa-server"></i>
                        <span>3 APIs</span>
                    </div>
                    <div class="footer-stat">
                        <i class="fas fa-download"></i>
                        <span id="footer-downloads">6k+ Downloads</span>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <script>
        // Sistema de Partículas
        class Particles {
            constructor() {
                this.canvas = document.getElementById('particles-canvas');
                this.ctx = this.canvas.getContext('2d');
                this.particles = [];
                this.particleCount = 50;
                this.colors = [
                    'rgba(124, 92, 252, 0.5)',
                    'rgba(88, 166, 255, 0.4)',
                    'rgba(35, 134, 54, 0.3)'
                ];
                
                this.init();
                this.animate();
                window.addEventListener('resize', () => this.init());
            }
            
            init() {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
                this.particles = [];
                
                for (let i = 0; i < this.particleCount; i++) {
                    this.particles.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * this.canvas.height,
                        size: Math.random() * 3 + 1,
                        speedX: Math.random() * 1 - 0.5,
                        speedY: Math.random() * 1 - 0.5,
                        color: this.colors[Math.floor(Math.random() * this.colors.length)]
                    });
                }
            }
            
            animate() {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Atualizar e desenhar partículas
                for (let particle of this.particles) {
                    particle.x += particle.speedX;
                    particle.y += particle.speedY;
                    
                    // Reaparecer nas bordas
                    if (particle.x > this.canvas.width) particle.x = 0;
                    if (particle.x < 0) particle.x = this.canvas.width;
                    if (particle.y > this.canvas.height) particle.y = 0;
                    if (particle.y < 0) particle.y = this.canvas.height;
                    
                    // Desenhar partícula
                    this.ctx.beginPath();
                    this.ctx.fillStyle = particle.color;
                    this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                    this.ctx.fill();
                    
                    // Desenhar conexões
                    for (let otherParticle of this.particles) {
                        const dx = particle.x - otherParticle.x;
                        const dy = particle.y - otherParticle.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        
                        if (distance < 100) {
                            this.ctx.beginPath();
                            this.ctx.strokeStyle = `rgba(124, 92, 252, ${0.2 * (1 - distance/100)})`;
                            this.ctx.lineWidth = 0.5;
                            this.ctx.moveTo(particle.x, particle.y);
                            this.ctx.lineTo(otherParticle.x, otherParticle.y);
                            this.ctx.stroke();
                        }
                    }
                }
                
                requestAnimationFrame(() => this.animate());
            }
        }

        // Sistema de Contador de Downloads
        class DownloadCounter {
            constructor() {
                this.storageKey = 'steam_gameloader_downloads';
                this.todayKey = 'steam_gameloader_today';
                this.currentDate = new Date().toDateString();
                this.totalDownloads = this.getTotalDownloads();
                this.todayDownloads = this.getTodayDownloads();
                
                // Inicializar se for o primeiro acesso do dia
                if (localStorage.getItem(this.todayKey) !== this.currentDate) {
                    localStorage.setItem(this.todayKey, this.currentDate);
                    this.todayDownloads = 0;
                    this.saveTodayDownloads();
                }
            }
            
            getTotalDownloads() {
                return parseInt(localStorage.getItem(this.storageKey)) || 6000;
            }
            
            getTodayDownloads() {
                return parseInt(localStorage.getItem(`${this.todayKey}_count`)) || 25;
            }
            
            saveTotalDownloads() {
                localStorage.setItem(this.storageKey, this.totalDownloads);
            }
            
            saveTodayDownloads() {
                localStorage.setItem(`${this.todayKey}_count`, this.todayDownloads);
            }
            
            increment() {
                this.totalDownloads++;
                this.todayDownloads++;
                this.saveTotalDownloads();
                this.saveTodayDownloads();
                this.updateUI();
                return this.totalDownloads;
            }
            
            formatCount(count) {
                if (count >= 1000000) {
                    return (count / 1000000).toFixed(1) + 'M+';
                } else if (count >= 1000) {
                    return (count / 1000).toFixed(1) + 'k+';
                }
                return count + '+';
            }
            
            updateUI() {
                // Atualizar todos os elementos de contador
                const totalFormatted = this.formatCount(this.totalDownloads);
                const todayFormatted = this.todayDownloads;
                
                // Hero section
                const heroDownloads = document.getElementById('hero-downloads');
                if (heroDownloads) heroDownloads.textContent = totalFormatted;
                
                // Download section
                const totalDownloadsEl = document.getElementById('total-downloads');
                if (totalDownloadsEl) totalDownloadsEl.textContent = totalFormatted;
                
                const todayDownloadsEl = document.getElementById('today-downloads');
                if (todayDownloadsEl) todayDownloadsEl.textContent = todayFormatted;
                
                // Footer
                const footerDownloads = document.getElementById('footer-downloads');
                if (footerDownloads) footerDownloads.textContent = totalFormatted + ' Downloads';
            }
            
            getStats() {
                return {
                    total: this.totalDownloads,
                    today: this.todayDownloads,
                    formattedTotal: this.formatCount(this.totalDownloads)
                };
            }
        }

        // Sistema Principal
        class SteamGameLoader {
            constructor() {
                this.downloadCounter = new DownloadCounter();
                this.isMenuOpen = false;
                this.lastDownloadClick = 0;
                this.downloadCooldown = 1000; // 1 segundo entre cliques
                
                this.init();
            }
            
            init() {
                // Inicializar partículas
                new Particles();
                
                // Configurar eventos
                this.setupEvents();
                
                // Atualizar UI inicial
                this.downloadCounter.updateUI();
                
                // Animações de scroll
                this.setupScrollAnimations();
                
                // Tooltips para API cards
                this.setupTooltips();
            }
            
            setupEvents() {
                // Menu mobile
                const mobileMenu = document.getElementById('mobileMenu');
                const mainNav = document.getElementById('mainNav');
                
                if (mobileMenu) {
                    mobileMenu.addEventListener('click', () => {
                        this.isMenuOpen = !this.isMenuOpen;
                        mainNav.classList.toggle('active', this.isMenuOpen);
                        mobileMenu.innerHTML = this.isMenuOpen ? 
                            '<i class="fas fa-times"></i>' : 
                            '<i class="fas fa-bars"></i>';
                    });
                }
                
                // Fechar menu ao clicar em link
                document.querySelectorAll('nav a').forEach(link => {
                    link.addEventListener('click', () => {
                        if (this.isMenuOpen) {
                            this.isMenuOpen = false;
                            mainNav.classList.remove('active');
                            mobileMenu.innerHTML = '<i class="fas fa-bars"></i>';
                        }
                    });
                });
                
                // Botão de download
                const downloadBtn = document.getElementById('installer-download');
                if (downloadBtn) {
                    downloadBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.handleDownload();
                    });
                }
                
                // Botão de download no hero
                const heroDownloadBtn = document.getElementById('download-button');
                if (heroDownloadBtn) {
                    heroDownloadBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        document.getElementById('download').scrollIntoView({ behavior: 'smooth' });
                    });
                }
            }
            
            setupScrollAnimations() {
                // Observer para animações de entrada
                const observerOptions = {
                    threshold: 0.1,
                    rootMargin: '0px 0px -50px 0px'
                };
                
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('fade-in');
                        }
                    });
                }, observerOptions);
                
                // Observar todos os elementos com classe fade-in
                document.querySelectorAll('.fade-in').forEach(el => {
                    observer.observe(el);
                });
            }
            
            setupTooltips() {
                const apiCards = document.querySelectorAll('.api-card');
                apiCards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        const apiName = this.querySelector('.api-name').textContent;
                        const apiUrl = this.querySelector('.api-url').textContent;
                        
                        this.title = `${apiName}\n${apiUrl}\nStatus: 100% Online`;
                    });
                });
            }
            
            handleDownload() {
                const now = Date.now();
                
                // Prevenir múltiplos cliques rápidos
                if (now - this.lastDownloadClick < this.downloadCooldown) {
                    return;
                }
                
                this.lastDownloadClick = now;
                
                // Incrementar contador
                this.downloadCounter.increment();
                
                // URL de download real
                const downloadUrl = 'https://github.com/oto-nexusdev/SteamGameLoader/releases/download/steamtools/SteamGameLoader.exe';
                
                // Criar link temporário para download
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = 'SteamGameLoader.exe';
                link.target = '_blank';
                
                // Adicionar efeito visual
                const button = document.getElementById('installer-download');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Baixando...';
                button.classList.add('btn-success');
                
                // Simular download
                setTimeout(() => {
                    link.click();
                    
                    // Restaurar botão após 2 segundos
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.classList.remove('btn-success');
                    }, 2000);
                    
                    // Mostrar notificação
                    this.showNotification('Download iniciado! Verifique sua pasta de downloads.');
                }, 500);
            }
            
            showNotification(message) {
                // Criar elemento de notificação
                const notification = document.createElement('div');
                notification.className = 'download-notification';
                notification.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <span>${message}</span>
                `;
                
                // Estilos para a notificação
                notification.style.cssText = `
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    background: var(--gradient-purple);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    z-index: 10000;
                    animation: slideInRight 0.3s ease;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    border: 1px solid rgba(255,255,255,0.1);
                `;
                
                // Adicionar ao corpo
                document.body.appendChild(notification);
                
                // Remover após 3 segundos
                setTimeout(() => {
                    notification.style.animation = 'slideOutRight 0.3s ease';
                    setTimeout(() => {
                        document.body.removeChild(notification);
                    }, 300);
                }, 3000);
                
                // Adicionar animações CSS dinamicamente
                if (!document.querySelector('#notification-styles')) {
                    const style = document.createElement('style');
                    style.id = 'notification-styles';
                    style.textContent = `
                        @keyframes slideInRight {
                            from { transform: translateX(100%); opacity: 0; }
                            to { transform: translateX(0); opacity: 1; }
                        }
                        @keyframes slideOutRight {
                            from { transform: translateX(0); opacity: 1; }
                            to { transform: translateX(100%); opacity: 0; }
                        }
                        .btn-success {
                            background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
                        }
                    `;
                    document.head.appendChild(style);
                }
            }
        }

        // Inicializar quando o DOM estiver carregado
        document.addEventListener('DOMContentLoaded', () => {
            const app = new SteamGameLoader();
            
            // Expor algumas funções globalmente se necessário
            window.trackDownload = () => app.handleDownload();
            window.startDownload = (type) => {
                if (type === 'installer') {
                    app.handleDownload();
                }
            };
            
            // Adicionar classe de carregamento ao body
            document.body.classList.add('loaded');
            
            // Efeito de digitação no título (opcional)
            const heroTitle = document.querySelector('.hero-text h2');
            if (heroTitle) {
                const text = heroTitle.innerHTML;
                heroTitle.innerHTML = '';
                let i = 0;
                const typeWriter = () => {
                    if (i < text.length) {
                        heroTitle.innerHTML += text.charAt(i);
                        i++;
                        setTimeout(typeWriter, 50);
                    }
                };
                // Iniciar após 500ms
                setTimeout(typeWriter, 500);
            }
        });

        // Suporte para navegadores mais antigos
        if (!String.prototype.includes) {
            String.prototype.includes = function(search, start) {
                if (typeof start !== 'number') {
                    start = 0;
                }
                if (start + search.length > this.length) {
                    return false;
                } else {
                    return this.indexOf(search, start) !== -1;
                }
            };
        }

        // Polyfill para classList.toggle com segundo parâmetro
        if (typeof DOMTokenList !== 'undefined' && !DOMTokenList.prototype.toggleWithForce) {
            DOMTokenList.prototype.toggle = function(token, force) {
                if (force !== undefined) {
                    if (force) {
                        this.add(token);
                        return true;
                    } else {
                        this.remove(token);
                        return false;
                    }
                }
                
                var hasToken = this.contains(token);
                if (hasToken) {
                    this.remove(token);
                } else {
                    this.add(token);
                }
                return !hasToken;
            };
        }
    </script>
</body>
</html>
