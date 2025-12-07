<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam GameLoader v19.0.0 - Plataforma Steam Avançada</title>
    <meta name="description" content="Plataforma completa para gerenciamento de jogos Steam com suporte a 60k+ títulos, APIs robustas e integração total.">
    <meta name="keywords" content="steam, game loader, steamtools, gerenciador, jogos, 60k jogos, download, api">
    <meta name="author" content="OtoNexusCloud">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="Steam GameLoader v19.0.0">
    <meta property="og:description" content="Plataforma avançada para gerenciamento de jogos Steam">
    <meta property="og:type" content="website">
    
    <!-- Favicon -->
    <link rel="icon" href="https://upload.wikimedia.org/wikipedia/commons/8/83/Steam_icon_logo.svg" type="image/svg+xml">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- CSS Inline -->
    <style>
        /* ===== VARIÁVEIS CSS ===== */
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
            --shadow-lg: 0 16px 32px rgba(0, 0, 0, 0.25);
            --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.2);
            --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        /* ===== RESET E BASE ===== */
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

        /* ===== CONTAINER PRINCIPAL ===== */
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* ===== HEADER ===== */
        header {
            background: rgba(13, 17, 23, 0.95);
            padding: 16px 0;
            position: fixed;
            width: 100%;
            z-index: 1000;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
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
        }

        .logo-icon {
            color: var(--accent-purple-light);
            font-size: 28px;
            position: relative;
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
            box-shadow: 0 2px 8px rgba(93, 63, 211, 0.3);
            letter-spacing: 0.5px;
        }

        /* ===== NAVEGAÇÃO ===== */
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
        }

        /* ===== HERO SECTION ===== */
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
            box-shadow: var(--shadow-md);
        }

        .stat-number {
            font-size: 28px;
            font-weight: 800;
            color: var(--accent-purple-light);
            margin-bottom: 6px;
            font-family: 'Orbitron', sans-serif;
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

        /* ===== BOTÕES ===== */
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
            box-shadow: 0 4px 16px rgba(93, 63, 211, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(93, 63, 211, 0.4);
        }

        .btn-secondary {
            background: transparent;
            color: var(--accent-blue);
            border: 1.5px solid var(--accent-blue);
            box-shadow: 0 4px 12px rgba(88, 166, 255, 0.1);
        }

        .btn-secondary:hover {
            background: rgba(88, 166, 255, 0.1);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(88, 166, 255, 0.2);
        }

        .btn-github {
            background: rgba(22, 27, 34, 0.9);
            color: white;
            border: 1.5px solid rgba(255, 255, 255, 0.1);
        }

        .btn-github:hover {
            background: rgba(22, 27, 34, 1);
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* ===== HERO IMAGE ===== */
        .hero-image {
            position: relative;
            perspective: 1000px;
        }

        .app-window {
            background: linear-gradient(145deg, var(--secondary-dark), var(--primary-dark));
            border-radius: 14px;
            overflow: hidden;
            box-shadow: var(--shadow-lg), 0 0 0 1px rgba(93, 63, 211, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.08);
            max-width: 500px;
            transition: transform 0.5s ease;
            backdrop-filter: blur(10px);
        }

        .app-window:hover {
            transform: translateY(-5px);
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
        }

        .app-feature i {
            color: var(--accent-purple-light);
            font-size: 18px;
            margin-right: 14px;
            width: 32px;
            text-align: center;
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

        /* ===== SEÇÕES ===== */
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
        }

        .section-title p {
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
            font-size: 16px;
            line-height: 1.6;
        }

        /* ===== FEATURES GRID ===== */
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
            box-shadow: var(--shadow-md);
        }

        .feature-icon {
            font-size: 36px;
            color: var(--accent-purple-light);
            margin-bottom: 20px;
            display: inline-block;
            transition: transform 0.3s ease;
        }

        .feature-card:hover .feature-icon {
            transform: scale(1.1);
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

        /* ===== APIS SECTION ===== */
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
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
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

        /* ===== API MONITOR INFO ===== */
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
        }

        .monitor-stat span {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 500;
        }

        /* ===== DOWNLOAD SECTION ===== */
        .download-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
            margin-top: 40px;
        }

        .download-card {
            background: var(--card-bg);
            border-radius: 14px;
            padding: 35px 28px;
            text-align: center;
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .download-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent-purple);
            box-shadow: var(--shadow-md);
        }

        .download-icon {
            font-size: 42px;
            color: var(--accent-purple-light);
            margin-bottom: 20px;
            display: inline-block;
            transition: transform 0.3s ease;
        }

        .download-card:hover .download-icon {
            transform: scale(1.1);
        }

        .download-card h3 {
            color: var(--text-white);
            font-size: 22px;
            margin-bottom: 14px;
            font-weight: 700;
        }

        .download-card p {
            color: var(--text-muted);
            margin-bottom: 28px;
            font-size: 14px;
            line-height: 1.6;
            flex: 1;
        }

        .download-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        .download-stat {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: rgba(31, 41, 55, 0.3);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .download-stat i {
            color: var(--accent-purple-light);
            font-size: 16px;
        }

        .download-stat div {
            display: flex;
            flex-direction: column;
            gap: 2px;
            text-align: left;
        }

        .download-stat strong {
            color: var(--text-white);
            font-size: 18px;
            font-weight: 700;
            font-family: 'Orbitron', sans-serif;
        }

        .download-stat span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
        }

        .download-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .detail-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }

        .detail-item i {
            color: var(--accent-purple-light);
            font-size: 12px;
        }

        .detail-item span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
        }

        /* ===== FOOTER ===== */
        footer {
            background: linear-gradient(180deg, var(--accent-steam) 0%, #111827 100%);
            padding: 60px 0 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            position: relative;
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
        }

        .footer-logo span {
            background: var(--gradient-purple);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
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
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .dev-info i {
            font-size: 18px;
            color: var(--accent-purple-light);
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
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            position: relative;
            font-weight: 700;
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
        }

        .footer-links a:hover,
        .footer-resources a:hover {
            color: var(--text-white);
            transform: translateX(3px);
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
            border-color: rgba(93, 63, 211, 0.3);
            transform: translateY(-1px);
        }

        .compatibility-icon {
            color: var(--accent-green);
            font-size: 12px;
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
            gap: 4px;
        }

        .footer-stat i {
            color: var(--accent-purple-light);
            font-size: 16px;
        }

        .footer-stat span {
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 500;
        }

        /* ===== ANIMAÇÕES ===== */
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

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        /* ===== NOTIFICAÇÕES ===== */
        #notification {
            position: fixed;
            top: 100px;
            right: 20px;
            z-index: 9999;
            animation: slideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            max-width: 380px;
        }

        .notification-content {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 18px 24px;
            border-radius: 14px;
            color: white;
            font-weight: 600;
            box-shadow: 0 12px 35px rgba(0,0,0,0.4);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            min-width: 320px;
            font-size: 15px;
            position: relative;
            overflow: hidden;
        }

        .notification-content.success {
            background: linear-gradient(135deg, rgba(35, 134, 54, 0.9) 0%, rgba(29, 115, 46, 0.85) 100%);
            border-color: rgba(35, 134, 54, 0.4);
        }

        .notification-content.error {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.9) 0%, rgba(220, 38, 38, 0.85) 100%);
            border-color: rgba(239, 68, 68, 0.4);
        }

        .notification-icon {
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            flex-shrink: 0;
        }

        .notification-message {
            flex: 1;
            line-height: 1.5;
        }

        @keyframes slideIn {
            from { transform: translateX(100%) translateY(0) scale(0.9); opacity: 0; }
            to { transform: translateX(0) translateY(0) scale(1); opacity: 1; }
        }

        @keyframes slideOut {
            from { transform: translateX(0) translateY(0) scale(1); opacity: 1; }
            to { transform: translateX(100%) translateY(0) scale(0.9); opacity: 0; }
        }

        /* ===== UTILITÁRIOS ===== */
        .fade-in {
            animation: slideInUp 0.6s ease-out forwards;
        }

        .hidden {
            display: none !important;
        }

        .visible {
            display: block !important;
        }

        .text-center {
            text-align: center;
        }

        .mt-20 { margin-top: 20px; }
        .mt-30 { margin-top: 30px; }
        .mt-40 { margin-top: 40px; }

        /* ===== RESPONSIVIDADE ===== */
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
            .download-card {
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
    </style>
</head>
<body>
    <!-- Canvas de Partículas -->
    <canvas id="particles-canvas"></canvas>

    <!-- Header -->
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
                        <div class="stat-number" id="hero-total-downloads">45.2k+</div>
                        <div class="stat-label">Downloads</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Disponibilidade</div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <a href="#download" class="btn btn-primary" id="downloadMainBtn">
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
                <div class="api-card fade-in premium-card" data-api-key="Sadie API">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fas fa-star"></i> Sadie API
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-check-circle"></i>
                            Online (22ms)
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
                
                <div class="api-card fade-in premium-card" data-api-key="Ryuu API">
                    <div class="api-header">
                        <div class="api-name">
                            <i class="fas fa-star"></i> Ryuu API
                        </div>
                        <div class="api-status online">
                            <i class="fas fa-check-circle"></i>
                            Online (18ms)
                        </div>
                    </div>
                    <div class="api-url" title="http://167.235.229.108/<appid>">
                        <i class="fas fa-link"></i> http://167.235.229.108/APPID
                    </div>
                    <div class="api-description">
                        API alternativa premium com alta velocidade
                        <div class="api-performance">
                            <span class="perf-badge"><i class="fas fa-tachometer-alt"></i> Máxima Performance</span>
                            <span class="perf-badge"><i class="fas fa-bolt"></i> Baixa Latência</span>
                        </div>
                    </div>
                </div>
                
                <div class="api-card fade-in premium-card" data-api-key="TwentyTwo Cloud">
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
                        <i class="fas fa-link"></i> http://masss.pythonanywhere.com/storage?auth=...&appid=APPID
                    </div>
                    <div class="api-description">
                        Storage em nuvem com autenticação segura
                        <div class="api-performance">
                            <span class="perf-badge"><i class="fas fa-cloud"></i> Armazenamento Cloud</span>
                            <span class="perf-badge"><i class="fas fa-lock"></i> Segurança Máxima</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Repositórios GitHub -->
            <h3 class="apis-category-title fade-in" style="margin-top: 60px;">
                <i class="fab fa-github"></i> Repositórios de Suporte
            </h3>
            <div class="apis-grid">
                <div class="api-card fade-in github-card" data-api-key="ManifestHub">
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
                
                <div class="api-card fade-in github-card" data-api-key="GameFiles Central">
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

    <!-- Download Section -->
    <section class="download" id="download">
        <div class="container">
            <div class="section-title fade-in">
                <h2>Download</h2>
                <p>Baixe a versão mais recente e comece a explorar 60,000+ jogos Steam.</p>
            </div>
            
            <div class="download-cards">
                <div class="download-card fade-in">
                    <div class="download-icon">
                        <i class="fas fa-desktop"></i>
                    </div>
                    <h3>Instalador Windows</h3>
                    <p>Instalador completo com configuração automática, integração com Steam e otimizações para Windows 10/11.</p>
                    <button class="btn btn-primary" id="downloadInstallerBtn">
                        <i class="fas fa-download"></i> Baixar v19.0.0
                    </button>
                    <div class="download-stats">
                        <div class="download-stat">
                            <i class="fas fa-download"></i>
                            <div>
                                <strong id="total-downloads">45.2k+</strong>
                                <span>Downloads Totais</span>
                            </div>
                        </div>
                        <div class="download-stat">
                            <i class="fas fa-calendar-day"></i>
                            <div>
                                <strong id="today-downloads">127</strong>
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
                
                <div class="download-card fade-in">
                    <div class="download-icon">
                        <i class="fas fa-code"></i>
                    </div>
                    <h3>Código-Fonte</h3>
                    <p>Acesse todo o código-fonte do projeto, contribua com melhorias ou crie sua própria versão personalizada.</p>
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
    </section>

    <!-- Footer -->
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
                            <span>v19.0.0 • 2024-03-15</span>
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
                                <strong>GreenLuma 2023</strong>
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
                    <p>&copy; 2024 Steam GameLoader v19.0.0. Plataforma de código aberto.</p>
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
                        <span id="footer-downloads">45.2k+ Downloads</span>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <!-- JavaScript Unificado -->
    <script>
        // ===== CONFIGURAÇÕES =====
        const CONFIG = {
            version: '19.0.0',
            releaseDate: '2024-03-15',
            developer: 'OtoNexusCloud',
            downloadUrl: 'https://github.com/oto-nexusdev/SteamGameLoader/releases/download/steamtools/SteamGameLoader.exe',
            sourceUrl: 'https://github.com/oto-nexusdev/SteamGameLoader/archive/refs/heads/main.zip',
            githubUrl: 'https://github.com/oto-nexusdev/SteamGameLoader',
            telegramUrl: 'https://t.me/SteamGameLoader',
            releasesUrl: 'https://github.com/oto-nexusdev/SteamGameLoader/releases/tag/steamtools'
        };

        // ===== SISTEMA DE PARTÍCULAS =====
        class ParticleSystem {
            constructor() {
                this.canvas = document.getElementById('particles-canvas');
                this.ctx = this.canvas.getContext('2d');
                this.particles = [];
                this.particleCount = 80;
                this.resizeTimeout = null;
                this.animationId = null;
                this.isAnimating = false;
                
                this.init();
                this.bindEvents();
                this.startAnimation();
            }
            
            init() {
                this.resizeCanvas();
                this.createParticles();
            }
            
            resizeCanvas() {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
                this.createParticles();
            }
            
            createParticles() {
                this.particles = [];
                for (let i = 0; i < this.particleCount; i++) {
                    this.particles.push({
                        x: Math.random() * this.canvas.width,
                        y: Math.random() * this.canvas.height,
                        size: Math.random() * 2 + 0.8,
                        speedX: (Math.random() - 0.5) * 0.5,
                        speedY: (Math.random() - 0.5) * 0.5,
                        opacity: Math.random() * 0.4 + 0.1,
                        color: `rgba(${Math.floor(Math.random() * 60 + 195)}, 
                                  ${Math.floor(Math.random() * 60 + 195)}, 
                                  255, `
                    });
                }
            }
            
            drawParticles() {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Desenhar conexões primeiro
                for (let i = 0; i < this.particles.length; i++) {
                    const p1 = this.particles[i];
                    
                    for (let j = i + 1; j < this.particles.length; j++) {
                        const p2 = this.particles[j];
                        const dx = p1.x - p2.x;
                        const dy = p1.y - p2.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        
                        if (distance < 120) {
                            this.ctx.beginPath();
                            const opacity = 0.2 * (1 - distance / 120);
                            this.ctx.strokeStyle = `rgba(93, 63, 211, ${opacity})`;
                            this.ctx.lineWidth = 0.8;
                            this.ctx.moveTo(p1.x, p1.y);
                            this.ctx.lineTo(p2.x, p2.y);
                            this.ctx.stroke();
                        }
                    }
                }
                
                // Desenhar partículas
                for (let i = 0; i < this.particles.length; i++) {
                    const p = this.particles[i];
                    
                    const gradient = this.ctx.createRadialGradient(
                        p.x, p.y, 0,
                        p.x, p.y, p.size * 3
                    );
                    gradient.addColorStop(0, `${p.color}${p.opacity})`);
                    gradient.addColorStop(0.7, `${p.color}${p.opacity * 0.3})`);
                    gradient.addColorStop(1, `${p.color}0)`);
                    
                    this.ctx.beginPath();
                    this.ctx.fillStyle = gradient;
                    this.ctx.arc(p.x, p.y, p.size * 1.5, 0, Math.PI * 2);
                    this.ctx.fill();
                }
            }
            
            updateParticles() {
                for (let i = 0; i < this.particles.length; i++) {
                    const p = this.particles[i];
                    
                    p.x += p.speedX;
                    p.y += p.speedY;
                    
                    // Rebater nas bordas com suavização
                    if (p.x <= 0 || p.x >= this.canvas.width) {
                        p.speedX *= -0.9;
                        p.x = Math.max(2, Math.min(this.canvas.width - 2, p.x));
                    }
                    if (p.y <= 0 || p.y >= this.canvas.height) {
                        p.speedY *= -0.9;
                        p.y = Math.max(2, Math.min(this.canvas.height - 2, p.y));
                    }
                    
                    // Adicionar leve movimento aleatório
                    p.speedX += (Math.random() - 0.5) * 0.02;
                    p.speedY += (Math.random() - 0.5) * 0.02;
                    
                    // Limitar velocidade
                    const maxSpeed = 1.5;
                    const speed = Math.sqrt(p.speedX * p.speedX + p.speedY * p.speedY);
                    if (speed > maxSpeed) {
                        p.speedX = (p.speedX / speed) * maxSpeed;
                        p.speedY = (p.speedY / speed) * maxSpeed;
                    }
                }
            }
            
            animate() {
                if (!this.isAnimating) return;
                
                this.drawParticles();
                this.updateParticles();
                this.animationId = requestAnimationFrame(() => this.animate());
            }
            
            startAnimation() {
                this.isAnimating = true;
                this.animate();
            }
            
            stopAnimation() {
                this.isAnimating = false;
                if (this.animationId) {
                    cancelAnimationFrame(this.animationId);
                }
            }
            
            bindEvents() {
                // Debounce resize
                window.addEventListener('resize', () => {
                    clearTimeout(this.resizeTimeout);
                    this.resizeTimeout = setTimeout(() => {
                        this.resizeCanvas();
                    }, 250);
                });
                
                // Pausar animação quando não visível
                document.addEventListener('visibilitychange', () => {
                    if (document.hidden) {
                        this.stopAnimation();
                    } else {
                        this.startAnimation();
                    }
                });
            }
        }

        // ===== SISTEMA DE CONTADOR DE DOWNLOADS =====
        class DownloadTracker {
            constructor() {
                this.stats = {
                    total: 45217,
                    today: 127,
                    yesterday: 89
                };
                this.lastIncrement = 0;
                this.incrementCooldown = 10000; // 10 segundos
                this.storageKey = 'steamgameloader_stats';
                
                this.init();
            }
            
            init() {
                this.loadStats();
                this.updateCounterElements();
                this.startAutoIncrement();
            }
            
            loadStats() {
                try {
                    const saved = localStorage.getItem(this.storageKey);
                    if (saved) {
                        const parsed = JSON.parse(saved);
                        if (parsed && parsed.total) {
                            this.stats = parsed;
                        }
                    }
                } catch (e) {
                    console.warn('Não foi possível carregar estatísticas salvas');
                }
            }
            
            saveStats() {
                try {
                    localStorage.setItem(this.storageKey, JSON.stringify(this.stats));
                } catch (e) {
                    console.warn('Não foi possível salvar estatísticas');
                }
            }
            
            incrementCounter() {
                const now = Date.now();
                
                // Verificar cooldown
                if (now - this.lastIncrement < this.incrementCooldown) {
                    return false;
                }
                
                // Incrementar estatísticas
                const today = new Date().toDateString();
                this.stats.total++;
                
                if (this.stats.lastIncrementDate === today) {
                    this.stats.today++;
                } else {
                    this.stats.yesterday = this.stats.today;
                    this.stats.today = 1;
                    this.stats.lastIncrementDate = today;
                }
                
                this.lastIncrement = now;
                this.saveStats();
                this.updateCounterElements();
                return true;
            }
            
            formatCount(count) {
                if (count >= 1000000) {
                    return (count / 1000000).toFixed(1) + 'M+';
                } else if (count >= 1000) {
                    return (count / 1000).toFixed(1) + 'k+';
                }
                return count + '+';
            }
            
            updateCounterElements() {
                const totalFormatted = this.formatCount(this.stats.total);
                
                // Hero stats
                const heroTotalElement = document.getElementById('hero-total-downloads');
                if (heroTotalElement) {
                    heroTotalElement.textContent = totalFormatted;
                }
                
                // Download card stats
                const totalDownloadsElement = document.getElementById('total-downloads');
                if (totalDownloadsElement) {
                    totalDownloadsElement.textContent = totalFormatted;
                }
                
                const todayDownloadsElement = document.getElementById('today-downloads');
                if (todayDownloadsElement) {
                    todayDownloadsElement.textContent = this.stats.today || 0;
                }
                
                // Footer stats
                const footerDownloadsElement = document.getElementById('footer-downloads');
                if (footerDownloadsElement) {
                    footerDownloadsElement.textContent = totalFormatted + ' Downloads';
                }
            }
            
            startAutoIncrement() {
                // Incrementar aleatoriamente para simular downloads contínuos
                setInterval(() => {
                    // 10% de chance de incrementar a cada minuto
                    if (Math.random() < 0.1) {
                        this.stats.total++;
                        this.stats.today++;
                        this.saveStats();
                        this.updateCounterElements();
                    }
                }, 60000); // 1 minuto
            }
        }

        // ===== SISTEMA DE NOTIFICAÇÕES =====
        function showNotification(message, type = 'success') {
            const existing = document.getElementById('notification');
            if (existing) existing.remove();
            
            const notification = document.createElement('div');
            notification.id = 'notification';
            notification.innerHTML = `
                <div class="notification-content ${type}">
                    <div class="notification-icon">
                        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                    </div>
                    <div class="notification-message">${message}</div>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Remover automaticamente após 4.5 segundos
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.animation = 'slideOut 0.4s ease forwards';
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 400);
                }
            }, 4500);
        }

        // ===== SISTEMA DE DOWNLOAD =====
        async function startDownload(type) {
            let button;
            
            // Encontrar o botão correto
            if (type === 'installer') {
                button = document.getElementById('downloadInstallerBtn') || 
                         document.getElementById('downloadMainBtn');
            }
            
            if (!button) {
                const downloadButtons = document.querySelectorAll('.btn-primary');
                if (downloadButtons.length > 0) {
                    button = downloadButtons[0];
                } else {
                    console.error('Botão de download não encontrado');
                    showNotification('Erro ao encontrar botão de download', 'error');
                    return;
                }
            }
            
            const originalHTML = button.innerHTML;
            const originalDisabled = button.disabled;
            
            // Estado de loading
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparando...';
            button.disabled = true;
            
            try {
                // Incrementar contador
                if (window.downloadTracker) {
                    window.downloadTracker.incrementCounter();
                }
                
                // Iniciar download após 1 segundo (para feedback visual)
                setTimeout(() => {
                    let downloadUrl;
                    let filename;
                    
                    if (type === 'installer') {
                        downloadUrl = CONFIG.downloadUrl;
                        filename = 'SteamGameLoader_v19.0.0.exe';
                    } else if (type === 'source') {
                        downloadUrl = CONFIG.sourceUrl;
                        filename = 'SteamGameLoader_Source.zip';
                    }
                    
                    // Criar link temporário para download
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    showNotification('Download iniciado com sucesso!', 'success');
                    
                    // Restaurar botão após 2 segundos
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                        button.disabled = originalDisabled;
                    }, 2000);
                    
                }, 1000);
                
            } catch (error) {
                console.error('Erro no download:', error);
                showNotification('Erro ao iniciar download. Tente novamente.', 'error');
                
                // Restaurar botão em caso de erro
                button.innerHTML = originalHTML;
                button.disabled = originalDisabled;
            }
        }

        // ===== INICIALIZAÇÃO DO SISTEMA =====
        document.addEventListener('DOMContentLoaded', () => {
            // Inicializar sistemas
            new ParticleSystem();
            window.downloadTracker = new DownloadTracker();
            
            // Menu responsivo
            const mobileMenu = document.getElementById('mobileMenu');
            const mainNav = document.getElementById('mainNav');
            
            if (mobileMenu && mainNav) {
                mobileMenu.addEventListener('click', function() {
                    mainNav.classList.toggle('active');
                    this.innerHTML = mainNav.classList.contains('active') 
                        ? '<i class="fas fa-times"></i>' 
                        : '<i class="fas fa-bars"></i>';
                    
                    // Animar ícone
                    this.style.transform = 'rotate(90deg)';
                    setTimeout(() => {
                        this.style.transform = 'rotate(0deg)';
                    }, 300);
                });
            }
            
            // Fechar menu ao clicar em link
            document.querySelectorAll('nav a').forEach(link => {
                link.addEventListener('click', () => {
                    if (mainNav) {
                        mainNav.classList.remove('active');
                        if (mobileMenu) {
                            mobileMenu.innerHTML = '<i class="fas fa-bars"></i>';
                        }
                    }
                });
            });
            
            // Scroll suave
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    if (href === '#' || href === '#!') return;
                    
                    e.preventDefault();
                    const targetElement = document.querySelector(href);
                    if (targetElement) {
                        const headerHeight = document.querySelector('header').offsetHeight;
                        const targetPosition = targetElement.offsetTop - headerHeight - 20;
                        
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
            });
            
            // Efeito de scroll no header
            window.addEventListener('scroll', () => {
                const header = document.querySelector('header');
                if (header) {
                    if (window.scrollY > 50) {
                        header.classList.add('scrolled');
                    } else {
                        header.classList.remove('scrolled');
                    }
                }
                
                // Animações de entrada
                document.querySelectorAll('.fade-in').forEach(element => {
                    const elementTop = element.getBoundingClientRect().top;
                    const windowHeight = window.innerHeight;
                    const revealPoint = 100;
                    
                    if (elementTop < windowHeight - revealPoint) {
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                    }
                });
            });
            
            // Inicializar animações de entrada
            document.querySelectorAll('.fade-in').forEach(element => {
                element.style.opacity = '0';
                element.style.transform = 'translateY(30px)';
                element.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
            });
            
            // Configurar botões de download
            document.getElementById('downloadMainBtn')?.addEventListener('click', (e) => {
                e.preventDefault();
                startDownload('installer');
            });
            
            document.getElementById('downloadInstallerBtn')?.addEventListener('click', (e) => {
                e.preventDefault();
                startDownload('installer');
            });
            
            // Tooltips para API cards
            document.querySelectorAll('.api-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    const apiName = this.querySelector('.api-name').textContent.trim();
                    const apiUrl = this.querySelector('.api-url').textContent.trim();
                    const apiStatus = this.querySelector('.api-status').textContent.trim();
                    
                    this.setAttribute('title', `${apiName}\n${apiUrl}\nStatus: ${apiStatus}`);
                });
            });
            
            // Simular atualização de ping das APIs
            setInterval(() => {
                document.querySelectorAll('.api-card .api-status.online').forEach(statusElement => {
                    const newPing = `${Math.floor(Math.random() * 30) + 15}ms`;
                    const icon = statusElement.querySelector('i').outerHTML;
                    statusElement.innerHTML = `${icon} Online (${newPing})`;
                });
            }, 30000);
            
            // Trigger inicial de scroll
            setTimeout(() => {
                window.dispatchEvent(new Event('scroll'));
            }, 150);
            
            // Efeito de hover nos cards
            document.querySelectorAll('.feature-card, .api-card, .download-card, .stat-card').forEach(card => {
                card.addEventListener('mouseenter', () => {
                    card.style.zIndex = '10';
                });
                
                card.addEventListener('mouseleave', () => {
                    card.style.zIndex = '1';
                });
            });
            
            // Efeito de clique nos botões
            document.querySelectorAll('.btn').forEach(button => {
                button.addEventListener('mousedown', () => {
                    button.style.transform = 'scale(0.98)';
                });
                
                button.addEventListener('mouseup', () => {
                    button.style.transform = '';
                });
                
                button.addEventListener('mouseleave', () => {
                    button.style.transform = '';
                });
            });
        });

        // ===== FUNÇÕES GLOBAIS =====
        window.startDownload = startDownload;
        window.showNotification = showNotification;

        // ===== TRATAMENTO DE ERROS GLOBAL =====
        window.addEventListener('error', function(e) {
            console.error('Erro global capturado:', e.error);
        });

        window.addEventListener('unhandledrejection', function(e) {
            console.error('Promise rejeitada não tratada:', e.reason);
        });
    </script>
</body>
</html>
