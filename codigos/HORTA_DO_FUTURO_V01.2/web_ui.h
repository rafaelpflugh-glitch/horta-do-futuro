#ifndef WEB_UI_H
#define WEB_UI_H

#include <Arduino.h>

//=================================================
// ÍCONE SVG PWA (100% OFFLINE)
//=================================================
const char ICON_SVG[] PROGMEM = R"HORTA_SVG(<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192">
<rect width="192" height="192" rx="40" fill="#02040A"/>
<rect x="8" y="8" width="176" height="176" rx="34" fill="#050B14" stroke="#38BDF8" stroke-width="4"/>
<path d="M96 42C66 56 50 84 56 116c4 20 18 32 40 34 22-2 36-14 40-34 6-32-10-60-40-74z" fill="none" stroke="#10B981" stroke-width="8" stroke-linejoin="round"/>
<path d="M96 58v92M96 92l-22-14M96 112l24-16" fill="none" stroke="#38BDF8" stroke-width="7" stroke-linecap="round"/>
<circle cx="96" cy="42" r="6" fill="#F59E0B"/>
</svg>)HORTA_SVG";

//=================================================
// MANIFEST PWA (Instalação como App em Tela Cheia)
//=================================================
const char MANIFEST_JSON[] PROGMEM = R"HORTA_MAN({
  "name": "HORTA DO FUTURO — Digital Twin & Computador de Plantas",
  "short_name": "Horta Futuro",
  "description": "Gêmeo Digital & Computador de Plantas (ESP32 Wi-Fi)",
  "start_url": "/",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#02040A",
  "theme_color": "#050B14",
  "icons": [
    {
      "src": "/icon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
})HORTA_MAN";

//=================================================
// INTERFACE WEB / PWA FIEL AO JANELA_PRINCIPAL.PY
// Paleta exata: #02040A / #050B14 / #080E1A / #1E293B / #38BDF8 / #F59E0B / #10B981
//=================================================
const char INDEX_HTML[] PROGMEM = R"HORTA_HTML(<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#050B14">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Horta Futuro">
<link rel="manifest" href="/manifest.json">
<link rel="icon" type="image/svg+xml" href="/icon.svg">
<title>HORTA DO FUTURO — Digital Twin &amp; Computador de Plantas</title>
<style>
:root{
  --bg:#02040A;
  --panel:#050B14;
  --box:#080E1A;
  --nav-act:#0F172A;
  --border:#1E293B;
  --border-hi:#334155;
  --text:#F8FAFC;
  --text-2:#CBD5E1;
  --muted:#94A3B8;
  --sec:#64748B;
  --blue:#38BDF8;
  --blue-h:#0284C7;
  --amber:#F59E0B;
  --amber-h:#D97706;
  --green:#10B981;
  --red:#EF4444;
  --teal:#2DD4BF;
  --orange:#FB923C;
  --theme:#38BDF8;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{
  font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;
  background:var(--bg);color:var(--text);min-height:100vh;
  display:flex;overflow-x:hidden;
}

/* ==================== SIDEBAR ESQUERDA (290px) ==================== */
.sidebar{
  width:290px;min-width:290px;background:var(--panel);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;justify-content:space-between;
  height:100vh;position:sticky;top:0;z-index:40;
}
.sb-top{padding:24px 20px 8px}
.sb-brand{font-size:18px;font-weight:700;color:var(--text);letter-spacing:.3px}
.sb-sub{font-size:10px;font-weight:700;color:var(--blue);margin-top:4px;letter-spacing:.4px}
.sb-nav{padding:12px 14px;display:flex;flex-direction:column;gap:6px}
.sb-btn{
  width:100%;height:42px;padding:0 14px;border-radius:8px;border:none;
  background:transparent;color:var(--muted);font-family:inherit;
  font-size:13px;font-weight:700;text-align:left;cursor:pointer;
  display:flex;align-items:center;gap:10px;transition:.15s;
}
.sb-btn:hover{background:var(--nav-act);color:var(--text)}
.sb-btn.active{background:var(--nav-act);color:var(--theme)}

/* Box Simulador na Sidebar */
.sim-box{
  margin:14px;padding:12px 14px;background:var(--box);
  border:1px solid var(--border);border-radius:12px;
}
.sim-title{font-size:12px;font-weight:700;color:var(--theme);text-align:center;margin-bottom:8px}
.clock-box{
  background:var(--bg);border:1px solid var(--border);border-radius:8px;
  padding:7px 10px;text-align:center;font-size:13px;font-weight:700;color:var(--theme);
  margin-bottom:8px;
}
.vel-row{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:4px}
.vel-row b{color:var(--theme)}
input[type=range].ctk-slider{
  -webkit-appearance:none;appearance:none;width:100%;height:10px;
  border-radius:999px;background:var(--border);outline:none;margin:6px 0;
}
input[type=range].ctk-slider::-webkit-slider-thumb{
  -webkit-appearance:none;appearance:none;width:16px;height:16px;
  border-radius:50%;background:var(--text);cursor:pointer;border:2px solid var(--theme);
}
input[type=range].ctk-slider:disabled{opacity:.45;cursor:not-allowed}
.time-btns{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:6px 0}
.ctk-btn{
  height:36px;padding:0 14px;border-radius:6px;border:1px solid transparent;
  font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;
  display:inline-flex;align-items:center;justify-content:center;gap:6px;transition:.15s;
}
.ctk-btn:active{transform:scale(.99)}
.btn-dark{background:var(--nav-act);color:var(--text);border-color:var(--border)}
.btn-dark:hover{background:var(--border)}
.btn-slate{background:var(--border);color:var(--text)}
.btn-slate:hover{background:var(--border-hi)}
.btn-blue{background:var(--blue);color:var(--bg)}
.btn-blue:hover{background:var(--blue-h);color:var(--text)}
.btn-amber{background:var(--amber);color:var(--bg)}
.btn-amber:hover{background:var(--amber-h)}
.btn-red{background:#DC2626;color:var(--text)}
.btn-green-dark{background:#064E3B;color:#A7F3D0;border:1px solid var(--green)}
.btn-green-dark:hover{background:#047857}
.btn-emerald{background:var(--green);color:#fff}

/* ==================== CONTAINER PRINCIPAL ==================== */
.main-container{flex:1;display:flex;flex-direction:column;min-width:0}
.header{
  height:65px;min-height:65px;background:var(--panel);
  border-bottom:1px solid var(--border);
  padding:0 28px;display:flex;align-items:center;justify-content:space-between;gap:12px;
  position:sticky;top:0;z-index:30;
}
.status-esp{font-size:13px;font-weight:700;color:var(--theme);display:flex;align-items:center;gap:8px}
.switch-wrap{display:flex;align-items:center;gap:10px;cursor:pointer;user-select:none}
.switch-wrap span{font-size:13px;font-weight:700;color:var(--muted)}
.sw-track{
  width:44px;height:22px;border-radius:999px;background:var(--border);
  position:relative;transition:.2s;
}
.sw-track.on{background:var(--blue)}
.sw-thumb{
  width:16px;height:16px;border-radius:50%;background:var(--text);
  position:absolute;top:3px;left:3px;transition:.2s;
}
.sw-track.on .sw-thumb{left:25px}

.content-area{padding:24px 28px;flex:1}
.tela{display:none}
.tela.active{display:block}
.page-title{font-size:24px;font-weight:700;color:var(--text)}
.page-sub{font-size:14px;font-weight:700;color:var(--muted);margin-top:4px;margin-bottom:16px}

/* Cards padrão CustomTkinter (#050B14 com borda #1E293B e raio 14px) */
.ctk-card{
  background:var(--panel);border:1px solid var(--border);
  border-radius:14px;padding:18px 20px;
}
.sec-label{font-size:12px;font-weight:700;color:var(--sec);text-transform:uppercase;letter-spacing:.4px}
.sec-label.blue{color:var(--blue)}
.sec-label.amber{color:var(--amber)}

/* Layouts em Grid idênticos ao janela_principal.py */
.dash-grid{display:grid;grid-template-columns:6fr 5fr;gap:20px;align-items:start}
.dash-left{display:flex;flex-direction:column;gap:14px}
.saude-card{border-width:2px}
.saude-row{display:flex;align-items:center;gap:18px;margin-top:8px;flex-wrap:wrap}
.saude-pct{font-size:48px;font-weight:700;color:var(--green);line-height:1}
.saude-txt{font-size:13px;color:var(--green);line-height:1.45;flex:1;min-width:200px;white-space:pre-line}

.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.mini-card{
  background:var(--bg);border:1px solid var(--border);border-radius:10px;
  padding:12px 14px;display:flex;flex-direction:column;justify-content:space-between;min-height:78px;
}
.mini-title{font-size:12px;color:var(--muted)}
.mini-val{font-size:20px;font-weight:700;text-align:right;margin-top:6px}

.act-row{
  background:var(--bg);border:1px solid var(--border);border-radius:8px;
  padding:8px 14px;margin-top:8px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;
}
.act-label{font-size:12px;font-weight:700;color:var(--text-2)}
.seg-group{
  display:inline-grid;grid-template-columns:repeat(3,60px);
  background:var(--panel);border:1px solid var(--border);border-radius:7px;padding:2px;gap:2px;
}
.seg-btn{
  height:28px;border:none;border-radius:5px;background:transparent;
  color:var(--muted);font-family:inherit;font-size:11px;font-weight:700;cursor:pointer;
}
.seg-btn:hover{background:var(--border);color:var(--text)}
.seg-btn.active{background:var(--blue);color:var(--bg)}

/* Coluna Direita: Sliders Slim Design */
.slider-list{display:flex;flex-direction:column;gap:8px;margin-top:12px}
.slider-card{
  background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 12px;
}
.slider-top{display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:700;color:var(--text-2)}
.slider-val{font-size:13px;font-weight:700;color:var(--theme)}
.slider-meta{font-size:10px;color:var(--sec);margin-top:2px}

/* Tela 2: Comparativo de Sincronia */
.comp-tabs{display:flex;gap:6px;flex-wrap:wrap}
.comp-tab{
  height:30px;padding:0 14px;border-radius:6px;border:none;
  background:var(--nav-act);color:var(--muted);font-size:12px;font-weight:700;cursor:pointer;
}
.comp-tab.active{background:var(--border);color:var(--amber)}
.comp-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:14px}
.comp-row{
  background:var(--bg);border-radius:8px;height:38px;padding:0 14px;
  display:flex;align-items:center;justify-content:space-between;margin-top:8px;font-size:12px;color:var(--text-2);
}
.comp-row b{font-size:13px}

/* Tela 3: Calibração */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items: stretch}
.inner-box{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin-top:14px}
.form-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0}
.form-row label{font-size:13px;font-weight:700;color:var(--text-2)}
.ctk-input,.ctk-select{
  height:38px;padding:0 12px;border-radius:6px;border:1px solid var(--border);
  background:var(--bg);color:var(--text);font-family:inherit;font-size:13px;font-weight:700;outline:none;
}
.ctk-input:focus,.ctk-select:focus{border-color:var(--blue)}

/* Tela 4: Receitas & Cultivo (3 Colunas) */
.three-col{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;align-items:stretch}
.field-block{margin-top:12px}
.field-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;font-size:12px;color:var(--text-2)}
.guia-box{
  background:var(--box);border:1px solid var(--green);border-radius:10px;
  padding:14px 16px;margin-top:18px;
}
.seg-fase{
  display:grid;grid-template-columns:repeat(3,1fr);
  background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:3px;gap:3px;margin-top:4px;
}
.seg-fase button{
  height:34px;border:none;border-radius:6px;background:transparent;
  color:var(--muted);font-family:inherit;font-size:12px;font-weight:700;cursor:pointer;
}
.seg-fase button.active{background:var(--blue);color:var(--bg)}
.resumo-box{
  background:var(--bg);border:1px solid var(--border);border-radius:8px;
  padding:12px 16px;margin-top:12px;display:flex;flex-direction:column;gap:8px;font-size:12px;color:var(--text);
}
.resumo-pair{display:flex;justify-content:space-between;gap:8px}

/* Tela 5: Gráficos & Logs */
.charts-top{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}
canvas.plot{width:100%;height:220px;display:block;background:var(--panel);border-radius:8px;margin-top:8px}

/* Tela 6: Configurações ESP32 & Monitor Matrix */
.matrix-box{
  background:#000000;border:1px solid #003311;border-radius:8px;
  color:#00FF66;font-family:Consolas,monospace;font-size:12.5px;
  padding:14px;height:420px;overflow-y:auto;white-space:pre-wrap;line-height:1.45;margin-top:12px;
}

/* Modais CustomTkinter */
.modal-backdrop{
  position:fixed;inset:0;background:rgba(0,0,0,.72);z-index:100;
  display:none;align-items:center;justify-content:center;padding:16px;
}
.modal-backdrop.open{display:flex}
.modal-win{
  width:100%;max-width:430px;background:var(--panel);border:1px solid var(--border);
  border-radius:14px;padding:20px;box-shadow:0 20px 60px rgba(0,0,0,.8);
}
.modal-body{background:var(--box);border:1px solid var(--border);border-radius:10px;padding:14px 16px;margin:12px 0}

/* Barra Inferior Mobile */
.mobile-nav{
  display:none;position:fixed;left:0;right:0;bottom:0;z-index:50;
  background:var(--panel);border-top:1px solid var(--border);
  grid-template-columns:repeat(6,1fr);padding:4px 4px calc(4px + env(safe-area-inset-bottom));
}
.m-btn{
  border:none;background:transparent;color:var(--muted);padding:6px 2px;
  border-radius:8px;font-size:10px;font-weight:700;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;gap:2px;
}
.m-btn.active{background:var(--nav-act);color:var(--theme)}

@media(max-width:1024px){
  .sidebar{display:none}
  .mobile-nav{display:grid}
  body{padding-bottom:64px}
  .content-area{padding:16px}
  .header{padding:0 16px}
  .dash-grid,.two-col,.three-col,.charts-top,.comp-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>

<!-- ==================== SIDEBAR ESQUERDA ==================== -->
<aside class="sidebar">
  <div>
    <div class="sb-top">
      <div class="sb-brand">HORTA DO FUTURO</div>
      <div class="sb-sub">DIGITAL TWIN &amp; COMPUTADOR DE PLANTAS</div>
    </div>
    <nav class="sb-nav">
      <button class="sb-btn active" data-tela="dashboard">📊 Painel &amp; Controles</button>
      <button class="sb-btn" data-tela="comparativo">⚖️ Comparativo de Sincronia</button>
      <button class="sb-btn" data-tela="calibracao">🎛️ Calibração de Sensores</button>
      <button class="sb-btn" data-tela="nutricao">🌱 Receitas &amp; Cultivo</button>
      <button class="sb-btn" data-tela="graficos">📈 Gráficos &amp; Logs</button>
      <button class="sb-btn" data-tela="config">⚙️ Configurações ESP32</button>
    </nav>
  </div>

  <div class="sim-box">
    <div class="sim-title">CONTROLE DO SIMULADOR</div>
    <div class="clock-box" id="lbl-relogio">--:--  --/--/----</div>
    <div class="vel-row"><span>Velocidade:</span><b id="lbl-vel">1x</b></div>
    <input id="sl-vel" class="ctk-slider" type="range" min="1" max="10" step="1" value="1">
    <div class="time-btns">
      <button class="ctk-btn btn-dark" onclick="avancarTempo(60)">+1h</button>
      <button class="ctk-btn btn-dark" onclick="avancarTempo(1440)">+1d</button>
    </div>
    <button id="btn-sim-toggle" class="ctk-btn btn-amber" style="width:100%;margin-top:6px" onclick="alternarDemonstracao()">▶ INICIAR SIMULADOR</button>
    <button class="ctk-btn btn-slate" style="width:100%;margin-top:6px" onclick="resetarPlanta()">↺  RESETAR CULTIVO</button>
  </div>
</aside>

<!-- ==================== CONTAINER PRINCIPAL ==================== -->
<div class="main-container">
  <header class="header">
    <div id="lbl-status-esp" class="status-esp">● ESP32 REAL CONECTADO (Wi-Fi)</div>
    <div class="switch-wrap" onclick="alternarModoHardware()">
      <div id="sw-hw-top" class="sw-track on"><div class="sw-thumb"></div></div>
      <span>Modo ESP32</span>
    </div>
  </header>

  <main class="content-area">

    <!-- ==================== 1. PAINEL & CONTROLES ==================== -->
    <section id="tela-dashboard" class="tela active">
      <div class="page-title">Painel Geral • Gêmeo Digital &amp; Computador de Plantas</div>
      <div id="lbl-sub-cultivo" class="page-sub">ALFACE EXPERIMENTAL #01 • Fase: VEGETATIVO • Dia: 0 (Hardware ESP32)</div>

      <div class="dash-grid">
        <!-- Coluna Esquerda -->
        <div class="dash-left">
          <div id="card-saude" class="ctk-card saude-card" style="border-color:var(--green)">
            <div class="sec-label">ÍNDICE DE SAÚDE BIOLÓGICA</div>
            <div class="saude-row">
              <div id="lbl-saude-pct" class="saude-pct">100%</div>
              <div id="lbl-saude-txt" class="saude-txt">✅ Condições ideais para o desenvolvimento</div>
            </div>
          </div>

          <div class="ctk-card">
            <div class="sec-label">ATMOSFERA E CLIMA</div>
            <div class="mini-grid">
              <div class="mini-card"><div class="mini-title">🌡️ Temperatura</div><div id="d-temp" class="mini-val" style="color:var(--red)">24.5 °C</div></div>
              <div class="mini-card"><div class="mini-title">💦 Umidade</div><div id="d-umid" class="mini-val" style="color:var(--blue)">60 %</div></div>
              <div class="mini-card"><div class="mini-title">💨 Exaustores</div><div id="d-fan" class="mini-val" style="color:var(--muted)">OFF (Auto)</div></div>
              <div class="mini-card"><div class="mini-title">☀️ Iluminação</div><div id="d-luz" class="mini-val" style="color:var(--amber)">ON (Ativa)</div></div>
            </div>
          </div>

          <div class="ctk-card">
            <div class="sec-label">SOLUÇÃO HIDROPÔNICA &amp; RESERVATÓRIO</div>
            <div class="mini-grid">
              <div class="mini-card"><div class="mini-title">🌊 Temp. Água</div><div id="d-tagua" class="mini-val" style="color:var(--teal)">22.0 °C</div></div>
              <div class="mini-card"><div class="mini-title">🧪 pH Solução</div><div id="d-ph" class="mini-val" style="color:var(--blue)">6.00</div></div>
              <div class="mini-card"><div class="mini-title">⚡ EC Nutrientes</div><div id="d-ec" class="mini-val" style="color:var(--orange)">1.4 mS/cm</div></div>
              <div class="mini-card"><div class="mini-title">🪣 Nível Tanque</div><div id="d-nivel" class="mini-val" style="color:var(--green)">OK (100%)</div></div>
            </div>
          </div>

          <div class="ctk-card">
            <div class="sec-label blue" style="margin-bottom:6px">CONTROLE DE ATUADORES &amp; RELÉS (ESPELHADO ESP32 / TFT)</div>
            <div class="act-row">
              <span class="act-label">☀️ Painel LED Grow (Relé 1):</span>
              <div class="seg-group">
                <button id="seg-luz-0" class="seg-btn active" onclick="setModoAtuador('modo_luz',0)">AUTO</button>
                <button id="seg-luz-1" class="seg-btn" onclick="setModoAtuador('modo_luz',1)">ON</button>
                <button id="seg-luz-2" class="seg-btn" onclick="setModoAtuador('modo_luz',2)">OFF</button>
              </div>
            </div>
            <div class="act-row">
              <span class="act-label">💨 Exaustor Climático (Relé 2):</span>
              <div class="seg-group">
                <button id="seg-fan-0" class="seg-btn active" onclick="setModoAtuador('modo_exaustor',0)">AUTO</button>
                <button id="seg-fan-1" class="seg-btn" onclick="setModoAtuador('modo_exaustor',1)">ON</button>
                <button id="seg-fan-2" class="seg-btn" onclick="setModoAtuador('modo_exaustor',2)">OFF</button>
              </div>
            </div>
            <div class="act-row">
              <span class="act-label">💧 Bomba Submersa DWC (Relé 3):</span>
              <div class="seg-group">
                <button id="seg-bomba-0" class="seg-btn active" onclick="setModoAtuador('modo_bomba_agua',0)">AUTO</button>
                <button id="seg-bomba-1" class="seg-btn" onclick="setModoAtuador('modo_bomba_agua',1)">ON</button>
                <button id="seg-bomba-2" class="seg-btn" onclick="setModoAtuador('modo_bomba_agua',2)">OFF</button>
              </div>
            </div>
            <div class="act-row">
              <span class="act-label">🫧 Oxigenador DWC (Relé 4 - Contínuo):</span>
              <b id="lbl-bomba-ar" style="font-size:12px;color:var(--green)">AR: ON | ÁGUA: ON</b>
            </div>
          </div>
        </div>

        <!-- Coluna Direita: Simulador Manual -->
        <div class="ctk-card">
          <div class="sec-label">SIMULADOR DE SENSORES (MANUAL)</div>
          <div style="font-size:11px;color:var(--muted);margin-top:2px">Desative o Modo ESP32 acima para mover os seletores:</div>
          <div class="slider-list">
            <div class="slider-card">
              <div class="slider-top"><span>🌡️ Temperatura do ar</span><span id="sv-tar" class="slider-val">24.5 °C</span></div>
              <input id="sl-tar" class="ctk-slider sim-sl" type="range" min="10" max="40" step="0.1" value="24.5" disabled oninput="onSimSlider('temperatura_ar',this.value)">
              <div id="sm-tar" class="slider-meta">Meta: 18 a 26 °C</div>
            </div>
            <div class="slider-card">
              <div class="slider-top"><span>💦 Umidade do ar</span><span id="sv-umi" class="slider-val">60.0 %</span></div>
              <input id="sl-umi" class="ctk-slider sim-sl" type="range" min="0" max="100" step="1" value="60" disabled oninput="onSimSlider('umidade_ar',this.value)">
              <div id="sm-umi" class="slider-meta">Meta: 50 a 80 %</div>
            </div>
            <div class="slider-card">
              <div class="slider-top"><span>🌊 Temperatura da água</span><span id="sv-tag" class="slider-val">22.0 °C</span></div>
              <input id="sl-tag" class="ctk-slider sim-sl" type="range" min="5" max="40" step="0.1" value="22.0" disabled oninput="onSimSlider('temperatura_agua',this.value)">
              <div id="sm-tag" class="slider-meta">Meta: 18 a 26 °C</div>
            </div>
            <div class="slider-card">
              <div class="slider-top"><span>🧪 pH</span><span id="sv-ph" class="slider-val">6.00</span></div>
              <input id="sl-ph" class="ctk-slider sim-sl" type="range" min="2" max="12" step="0.05" value="6.0" disabled oninput="onSimSlider('ph',this.value)">
              <div id="sm-ph" class="slider-meta">Meta: 5.5 a 6.5</div>
            </div>
            <div class="slider-card">
              <div class="slider-top"><span>⚡ EC</span><span id="sv-ec" class="slider-val">1.40 mS/cm</span></div>
              <input id="sl-ec" class="ctk-slider sim-sl" type="range" min="0" max="3" step="0.05" value="1.4" disabled oninput="onSimSlider('ec',this.value)">
              <div id="sm-ec" class="slider-meta">Meta: 1.0 a 1.8 mS/cm</div>
            </div>
            <div class="slider-card">
              <div class="slider-top"><span>🪣 Nível da água</span><span id="sv-niv" class="slider-val">100.0 %</span></div>
              <input id="sl-niv" class="ctk-slider sim-sl" type="range" min="0" max="100" step="1" value="100" disabled oninput="onSimSlider('nivel_agua',this.value)">
              <div class="slider-meta">Meta: 100 % (Boia de Nível DWC)</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 2. COMPARATIVO DE SINCRONIA ==================== -->
    <section id="tela-comparativo" class="tela">
      <div class="page-title">Diagnóstico de Sincronia • ESP32 vs. Gêmeo Digital</div>
      <div class="page-sub">Validação da precisão preditiva do modelo frente às leituras físicas do hardware.</div>

      <div class="ctk-card">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
          <span class="sec-label">CURVAS TEMPORAIS DE SINCRONIA</span>
          <div class="comp-tabs">
            <button class="comp-tab active" data-sinc="ph">pH</button>
            <button class="comp-tab" data-sinc="ec">EC</button>
            <button class="comp-tab" data-sinc="temp_ar">Temp. Ar</button>
            <button class="comp-tab" data-sinc="temp_agua">Temp. Água</button>
            <button class="comp-tab" data-sinc="umidade">Umidade</button>
          </div>
        </div>
        <canvas id="cv-sinc" class="plot" style="height:210px"></canvas>
      </div>

      <div class="comp-grid">
        <div class="ctk-card">
          <div class="sec-label blue" style="margin-bottom:8px">📡 HARDWARE REAL (ESP32)</div>
          <div class="comp-row"><span>Índice de Saúde Biológica</span><b id="cr-saude" style="color:var(--blue)">--</b></div>
          <div class="comp-row"><span>Temperatura do Ar</span><b id="cr-tar" style="color:var(--blue)">--</b></div>
          <div class="comp-row"><span>Umidade Relativa</span><b id="cr-umi" style="color:var(--blue)">--</b></div>
          <div class="comp-row"><span>Temperatura da Água</span><b id="cr-tag" style="color:var(--blue)">--</b></div>
          <div class="comp-row"><span>pH da Solução</span><b id="cr-ph" style="color:var(--blue)">--</b></div>
          <div class="comp-row"><span>Condutividade Elétrica (EC)</span><b id="cr-ec" style="color:var(--blue)">--</b></div>
          <div class="comp-row"><span>Nível do Reservatório</span><b id="cr-niv" style="color:var(--blue)">--</b></div>
        </div>
        <div class="ctk-card">
          <div class="sec-label amber" style="margin-bottom:8px">🔮 GÊMEO DIGITAL (PREDITIVO)</div>
          <div class="comp-row"><span>Índice de Saúde Biológica</span><b id="cg-saude" style="color:var(--amber)">--</b></div>
          <div class="comp-row"><span>Temperatura do Ar</span><b id="cg-tar" style="color:var(--amber)">--</b></div>
          <div class="comp-row"><span>Umidade Relativa</span><b id="cg-umi" style="color:var(--amber)">--</b></div>
          <div class="comp-row"><span>Temperatura da Água</span><b id="cg-tag" style="color:var(--amber)">--</b></div>
          <div class="comp-row"><span>pH da Solução</span><b id="cg-ph" style="color:var(--amber)">--</b></div>
          <div class="comp-row"><span>Condutividade Elétrica (EC)</span><b id="cg-ec" style="color:var(--amber)">--</b></div>
          <div class="comp-row"><span>Nível do Reservatório</span><b id="cg-niv" style="color:var(--amber)">--</b></div>
        </div>
      </div>
    </section>

    <!-- ==================== 3. CALIBRAÇÃO DE SENSORES ==================== -->
    <section id="tela-calibracao" class="tela">
      <div class="two-col">
        <div class="ctk-card">
          <div style="font-size:16px;font-weight:700;color:var(--blue)">🎛️ PAINEL DE CALIBRAÇÃO DE SENSORES</div>
          <div style="font-size:12px;color:var(--muted);margin-top:4px">Ajuste os fatores de correção para alinhar as leituras da bancada física.</div>
          <div class="inner-box">
            <div class="form-row">
              <label>Offset Sonda pH (+/-):</label>
              <input id="in-off-ph" class="ctk-input" type="number" step="0.1" value="0.0" style="width:100px;text-align:center">
            </div>
            <div class="form-row">
              <label>Fator Ganho Condutividade (EC):</label>
              <input id="in-fat-ec" class="ctk-input" type="number" step="0.05" value="1.0" style="width:100px;text-align:center">
            </div>
          </div>
          <button class="ctk-btn btn-blue" style="width:100%;height:42px;margin-top:18px;font-size:13px" onclick="aplicarCalibracao()">⚡ APLICAR &amp; ENVIAR AO ESP32</button>
        </div>

        <div class="ctk-card">
          <div class="sec-label" style="margin-bottom:14px">INSTRUÇÕES DE CALIBRAÇÃO</div>
          <div style="font-size:12.5px;color:var(--text-2);line-height:1.65;white-space:pre-line">1. pH Offset:
   Coloque a sonda no tampão pH 7.0. Se a leitura indicar 7.2, ajusta-se o Offset para -0.2.

2. Fator Ganho EC:
   Submerja a sonda na solução padrão 1.41 mS/cm. Se a leitura for 1.30, divida 1.41/1.30 e insira o multiplicador correspondente.

3. Envio ao Hardware:
   Certifique-se de que o 'Modo ESP32' está ativo no topo para transmitir via Wi-Fi diretamente ao ESP32.</div>
        </div>
      </div>
    </section>

    <!-- ==================== 4. RECEITAS & CULTIVO ==================== -->
    <section id="tela-nutricao" class="tela">
      <div class="three-col">
        <!-- Coluna 1 -->
        <div class="ctk-card">
          <div class="sec-label blue">1. RECEITA &amp; IDENTIDADE DO CULTIVO</div>
          <div style="font-size:11px;color:var(--sec);margin-top:2px">Defina o perfil salvo e a espécie da planta.</div>

          <div class="field-block">
            <div class="field-head">
              <span>Meus Cultivos Salvos</span>
              <button class="ctk-btn btn-slate" style="height:26px;padding:0 10px;color:var(--blue);font-size:11px" onclick="novoCultivoLimpo()">＋ Novo</button>
            </div>
            <select id="sel-cultivo-salvo" class="ctk-select" style="width:100%" onchange="carregarCultivoSalvo(this.value)"></select>
          </div>

          <div class="field-block">
            <div class="field-head">
              <span>Tipo de Planta</span>
              <button class="ctk-btn btn-slate" style="height:26px;padding:0 10px;color:var(--amber);font-size:11px" onclick="abrirModal('modal-especie')">＋ Nova</button>
            </div>
            <select id="sel-especie" class="ctk-select" style="width:100%" onchange="selecionarEspecie(this.value)"></select>
          </div>

          <div class="field-block">
            <div class="field-head"><span>Nome do Cultivo Ativo</span></div>
            <input id="in-nome-cultivo" class="ctk-input" type="text" style="width:100%" value="Alface Experimental #01">
          </div>

          <div class="guia-box">
            <div style="font-size:12px;font-weight:700;color:var(--green);margin-bottom:6px">💡 GUIA DE CORREÇÃO NUTRICIONAL</div>
            <div id="lbl-guia-nutri" style="font-size:11.5px;color:var(--text-2);line-height:1.5;white-space:pre-line">Vol: 10.0L | Fert A+B: +0.0g
pH Correção: Estável (0.0ml)</div>
            <button class="ctk-btn btn-green-dark" style="width:100%;height:32px;margin-top:10px;font-size:11px" onclick="aplicarCorrecaoSimulador()">🧪 APLICAR CORREÇÃO NO SIMULADOR</button>
          </div>
        </div>

        <!-- Coluna 2 -->
        <div class="ctk-card">
          <div class="sec-label blue">2. PERFIS DE AUTOMAÇÃO</div>
          <div style="font-size:11px;color:var(--sec);margin-top:2px">Ciclos de iluminação, rega e controle climático.</div>

          <div class="field-block">
            <div class="field-head"><span>Fase de Crescimento</span></div>
            <div class="seg-fase">
              <button id="bf-MUDA" onclick="mudarFase('MUDA')">MUDAS</button>
              <button id="bf-VEGETATIVO" class="active" onclick="mudarFase('VEGETATIVO')">VEGA</button>
              <button id="bf-FLORACAO" onclick="mudarFase('FLORACAO')">FLORA</button>
            </div>
          </div>

          <div class="resumo-box">
            <div id="res-luz">☀️ Iluminação: 18.0 h/dia (Início 06:00)</div>
            <div id="res-bomba">💧 Irrigação: 15m ON / 45m OFF</div>
            <div id="res-fan">💨 Clima: Exaustão &gt; 26.0°C</div>
          </div>

          <button class="ctk-btn btn-slate" style="width:100%;margin-top:14px;color:var(--blue)" onclick="abrirModal('modal-auto')">⚙️ CONFIGURAR PARÂMETROS</button>
          <button class="ctk-btn" style="width:100%;margin-top:6px;background:transparent;color:var(--amber)" onclick="novoCultivoLimpo()">↺ Restaurar Automação Padrão</button>
        </div>

        <!-- Coluna 3 -->
        <div class="ctk-card" style="display:flex;flex-direction:column;justify-content:space-between">
          <div>
            <div class="sec-label blue">3. METAS &amp; ASSISTENTE NUTRICIONAL</div>
            <div style="font-size:11px;color:var(--sec);margin-top:2px">Limites ideais de pH e fertilização.</div>

            <div class="resumo-box">
              <div class="resumo-pair"><span id="res-ph">🧪 pH: 5.5 a 6.5</span><span id="res-ec">⚡ EC: 1.0 a 1.8</span></div>
              <div class="resumo-pair"><span id="res-tar">🌡️ Ar: 18.0 a 26.0 °C</span><span id="res-tag">🌊 Água: 18.0 a 26.0 °C</span></div>
              <div id="res-umi">💦 Umidade Ar: 50.0 a 80.0 %</div>
            </div>

            <button class="ctk-btn btn-slate" style="width:100%;margin-top:12px;color:var(--green)" onclick="abrirModal('modal-metas')">⚙️ AJUSTAR LIMITES BIOLÓGICOS</button>

            <div style="margin-top:16px">
              <div class="sec-label" style="font-size:11px">FERTILIZANTE COMERCIAL</div>
              <div class="form-row" style="margin-top:4px">
                <label style="font-size:12px;font-weight:400">Produto:</label>
                <input id="in-fert-nome" class="ctk-input" type="text" value="Flex Azul + Vermelho (A+B)" style="width:185px;font-size:12px">
              </div>
              <div class="form-row">
                <label style="font-size:12px;font-weight:400">g/L por +1.0 EC:</label>
                <input id="in-fert-taxa" class="ctk-input" type="number" step="0.01" value="0.84" style="width:90px;text-align:center;font-size:12px">
              </div>
            </div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px">
            <button class="ctk-btn btn-dark" style="height:42px" onclick="salvarReceitaLocal()">💾 SALVAR</button>
            <button class="ctk-btn btn-blue" style="height:42px" onclick="sincronizarReceitaESP32()">⚡ SINCRONIZAR</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== 5. GRÁFICOS & LOGS ==================== -->
    <section id="tela-graficos" class="tela">
      <div class="charts-top">
        <div class="ctk-card">
          <div class="sec-label" style="text-align:center">EVOLUÇÃO DA SAÚDE BIOLÓGICA (%)</div>
          <canvas id="cv-saude" class="plot"></canvas>
        </div>
        <div class="ctk-card">
          <div class="sec-label" style="text-align:center">DINÂMICA DE NUTRIÇÃO (pH &amp; EC)</div>
          <canvas id="cv-nutri" class="plot"></canvas>
        </div>
      </div>
      <div class="ctk-card">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
          <span class="sec-label">MONITORAMENTO TÉRMICO COMPARATIVO (AR vs ÁGUA)</span>
          <div style="display:flex;gap:8px">
            <button class="ctk-btn btn-dark" onclick="exportarLogsCSV()">📥 EXPORTAR LOGS (CSV)</button>
            <a id="btn-sd-link" class="ctk-btn btn-slate" href="/api/csv" target="_blank" style="text-decoration:none;display:none">💾 CSV CARTÃO SD</a>
          </div>
        </div>
        <canvas id="cv-termico" class="plot"></canvas>
      </div>
    </section>

    <!-- ==================== 6. CONFIGURAÇÕES ESP32 ==================== -->
    <section id="tela-config" class="tela">
      <div class="two-col">
        <div class="ctk-card">
          <div class="sec-label">GERENCIAMENTO DE HARDWARE</div>
          <div class="switch-wrap" style="margin:16px 0" onclick="alternarModoHardware()">
            <div id="sw-hw-cfg" class="sw-track on"><div class="sw-thumb"></div></div>
            <span style="color:var(--text)">Ativar Comunicação com ESP32 (Wi-Fi Tempo Real)</span>
          </div>

          <div class="inner-box">
            <div style="font-size:12px;font-weight:700;color:var(--text-2);margin-bottom:8px">Status da Rede &amp; Periféricos ESP32:</div>
            <div id="cfg-info-rede" style="font-size:12px;color:var(--blue);line-height:1.6">Conectando ao ESP32...</div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px">
            <button class="ctk-btn btn-dark" style="height:38px" onclick="sincronizarRelogioRTC()">🕒 Sincronizar Relógio RTC</button>
            <button class="ctk-btn btn-dark" style="height:38px;color:var(--blue)" onclick="solicitarTelemetriaAgora()">📡 Solicitar Telemetria Agora</button>
          </div>

          <div class="inner-box" style="margin-top:14px">
            <div style="font-size:12px;font-weight:700;color:var(--text-2);margin-bottom:8px">Configurar Wi-Fi Doméstico na Memória NVS do ESP32:</div>
            <div class="form-row">
              <label style="font-size:12px">Rede Wi-Fi (SSID):</label>
              <input id="in-wifi-ssid" class="ctk-input" type="text" placeholder="Ex: MinhaCasa_2.4G" style="width:190px">
            </div>
            <div class="form-row">
              <label style="font-size:12px">Senha Wi-Fi:</label>
              <input id="in-wifi-pass" class="ctk-input" type="password" placeholder="••••••••" style="width:190px">
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px">
              <button class="ctk-btn btn-blue" onclick="salvarWifiNVS()">💾 Salvar Wi-Fi &amp; Reiniciar</button>
              <button class="ctk-btn btn-slate" onclick="reiniciarESP32()">🔄 Reiniciar ESP32</button>
            </div>
          </div>
        </div>

        <div class="ctk-card">
          <div class="sec-label">MONITOR DE COMUNICAÇÃO SERIAL / WI-FI (MATRIX)</div>
          <div id="matrix-log" class="matrix-box">[INFO] Sistema inicializado. Interface Gêmeo Digital Web ativa.
</div>
        </div>
      </div>
    </section>

  </main>
</div>

<!-- ==================== NAVEGAÇÃO MOBILE ==================== -->
<nav class="mobile-nav">
  <button class="m-btn active" data-tela="dashboard"><span>📊</span>Painel</button>
  <button class="m-btn" data-tela="comparativo"><span>⚖️</span>Sincronia</button>
  <button class="m-btn" data-tela="calibracao"><span>🎛️</span>Calibrar</button>
  <button class="m-btn" data-tela="nutricao"><span>🌱</span>Cultivo</button>
  <button class="m-btn" data-tela="graficos"><span>📈</span>Gráficos</button>
  <button class="m-btn" data-tela="config"><span>⚙️</span>ESP32</button>
</nav>

<!-- ==================== MODAL 1: AUTOMAÇÃO ==================== -->
<div id="modal-auto" class="modal-backdrop">
  <div class="modal-win">
    <div style="font-size:16px;font-weight:700;color:var(--blue);text-align:center">⚙️ PARÂMETROS DE AUTOMAÇÃO</div>
    <div class="modal-body">
      <div class="form-row"><label>Horas de Luz / Dia (h):</label><input id="m-foto" class="ctk-input" type="number" step="0.5" style="width:90px;text-align:center"></div>
      <div class="form-row"><label>Início da Luz (Hora 0-23):</label><input id="m-hora" class="ctk-input" type="number" style="width:90px;text-align:center"></div>
      <div class="form-row"><label>Início da Luz (Minuto 0-59):</label><input id="m-min" class="ctk-input" type="number" style="width:90px;text-align:center"></div>
      <div style="height:1px;background:var(--border);margin:6px 0"></div>
      <div class="form-row"><label>Bomba Submersa - ON (min):</label><input id="m-bon" class="ctk-input" type="number" style="width:90px;text-align:center"></div>
      <div class="form-row"><label>Bomba Submersa - PAUSA (min):</label><input id="m-boff" class="ctk-input" type="number" style="width:90px;text-align:center"></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <button class="ctk-btn btn-dark" style="height:40px" onclick="fecharModais()">CANCELAR</button>
      <button class="ctk-btn btn-blue" style="height:40px" onclick="salvarModalAutomacao()">SALVAR PARÂMETROS</button>
    </div>
  </div>
</div>

<!-- ==================== MODAL 2: LIMITES BIOLÓGICOS ==================== -->
<div id="modal-metas" class="modal-backdrop">
  <div class="modal-win">
    <div style="font-size:16px;font-weight:700;color:var(--green);text-align:center">⚙️ LIMITES BIOLÓGICOS</div>
    <div class="modal-body">
      <div class="form-row"><label>pH:</label><div><input id="m-ph-min" class="ctk-input" type="number" step="0.1" style="width:68px;text-align:center"> <span style="color:var(--muted);font-size:11px">até</span> <input id="m-ph-max" class="ctk-input" type="number" step="0.1" style="width:68px;text-align:center"></div></div>
      <div class="form-row"><label>EC (mS/cm):</label><div><input id="m-ec-min" class="ctk-input" type="number" step="0.1" style="width:68px;text-align:center"> <span style="color:var(--muted);font-size:11px">até</span> <input id="m-ec-max" class="ctk-input" type="number" step="0.1" style="width:68px;text-align:center"></div></div>
      <div class="form-row"><label>Temp. Ar (°C):</label><div><input id="m-tar-min" class="ctk-input" type="number" step="0.5" style="width:68px;text-align:center"> <span style="color:var(--muted);font-size:11px">até</span> <input id="m-tar-max" class="ctk-input" type="number" step="0.5" style="width:68px;text-align:center"></div></div>
      <div class="form-row"><label>Temp. Água (°C):</label><div><input id="m-tag-min" class="ctk-input" type="number" step="0.5" style="width:68px;text-align:center"> <span style="color:var(--muted);font-size:11px">até</span> <input id="m-tag-max" class="ctk-input" type="number" step="0.5" style="width:68px;text-align:center"></div></div>
      <div class="form-row"><label>Umidade (%):</label><div><input id="m-umi-min" class="ctk-input" type="number" step="1" style="width:68px;text-align:center"> <span style="color:var(--muted);font-size:11px">até</span> <input id="m-umi-max" class="ctk-input" type="number" step="1" style="width:68px;text-align:center"></div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <button class="ctk-btn btn-dark" style="height:40px" onclick="fecharModais()">CANCELAR</button>
      <button class="ctk-btn btn-emerald" style="height:40px" onclick="salvarModalMetas()">SALVAR LIMITES</button>
    </div>
  </div>
</div>

<!-- ==================== MODAL 3: NOVA ESPÉCIE ==================== -->
<div id="modal-especie" class="modal-backdrop">
  <div class="modal-win">
    <div style="font-size:15px;font-weight:700;color:var(--amber);text-align:center">🌾 CADASTRAR NOVA ESPÉCIE</div>
    <div class="modal-body">
      <div class="field-block" style="margin-top:0">
        <div class="field-head"><span>Nome da Espécie (ex: TOMATE):</span></div>
        <input id="m-esp-nome" class="ctk-input" type="text" style="width:100%">
      </div>
      <div class="field-block">
        <div class="field-head"><span>Fotoperíodo padrão (Horas de luz):</span></div>
        <input id="m-esp-foto" class="ctk-input" type="number" value="16" style="width:100%">
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <button class="ctk-btn btn-dark" style="height:40px" onclick="fecharModais()">CANCELAR</button>
      <button class="ctk-btn btn-amber" style="height:40px" onclick="salvarNovaEspecie()">CADASTRAR ESPÉCIE</button>
    </div>
  </div>
</div>

<script>
const $ = id => document.getElementById(id);

const ESPECIES_BASE = {
  "ALFACE":     { ph_min:5.5, ph_max:6.5, ec_min:1.0, ec_max:1.8, temp_ar_min:18, temp_ar_max:26, temp_agua_min:18, temp_agua_max:26, umidade_min:50, umidade_max:80, fotoperiodo:18 },
  "MANJERICÃO": { ph_min:5.5, ph_max:6.5, ec_min:1.0, ec_max:1.6, temp_ar_min:20, temp_ar_max:30, temp_agua_min:18, temp_agua_max:26, umidade_min:50, umidade_max:80, fotoperiodo:16 },
  "RÚCULA":     { ph_min:6.0, ph_max:6.8, ec_min:0.8, ec_max:1.4, temp_ar_min:16, temp_ar_max:24, temp_agua_min:18, temp_agua_max:24, umidade_min:50, umidade_max:75, fotoperiodo:16 },
  "MORANGO":    { ph_min:5.5, ph_max:6.2, ec_min:1.2, ec_max:2.0, temp_ar_min:16, temp_ar_max:25, temp_agua_min:18, temp_agua_max:23, umidade_min:55, umidade_max:75, fotoperiodo:14 }
};

let cultivosSalvos = {
  "Alface Experimental #01": { cultura:"ALFACE", fase:"VEGETATIVO", ...ESPECIES_BASE["ALFACE"], inicio_luz:6, inicio_minuto:0, bomba_on:15, bomba_off:45, fertilizante:"Flex Azul + Vermelho (A+B)", taxa_ab:0.84 }
};

let modoHardwareReal = true;
let demonstracaoAtiva = false;
let paramSincAtivo = 'ph';
let minutosSimulados = 0;

// Estado do Gêmeo Digital (Local) e Último Estado do ESP32 (Físico)
const gem = {
  nome_cultivo: "Alface Experimental #01",
  cultura: "ALFACE", fase: "VEGETATIVO",
  ph_min:5.5, ph_max:6.5, ec_min:1.0, ec_max:1.8,
  temp_ar_min:18, temp_ar_max:26, temp_agua_min:18, temp_agua_max:26,
  umidade_min:50, umidade_max:80,
  fotoperiodo:18, inicio_luz:6, inicio_minuto:0,
  bomba_on:15, bomba_off:45,
  temperatura_ar:24.5, umidade_ar:60.0, temperatura_agua:22.0,
  ph:6.0, ec:1.4, nivel_agua:100.0,
  saude:100.0, dia_cultivo:0,
  luz:true, exaustor:false, bomba_agua:true, bomba_ar:true,
  modo_luz:0, modo_exaustor:0, modo_bomba_agua:0,
  offset_ph:0.0, fator_ec:1.0,
  hora_v:13, min_v:0
};

let ultimoEsp = { ...gem, ip:"192.168.4.1", wifi_ap:false, rtc_ok:true, sd_ok:false, uptime_s:0 };
let receitaSincronizadaInicial = false;

const hist = {
  saude:[100],
  ph:{ gem:[6.0], real:[6.0] },
  ec:{ gem:[1.4], real:[1.4] },
  temp_ar:{ gem:[24.5], real:[24.5] },
  temp_agua:{ gem:[22.0], real:[22.0] },
  umidade:{ gem:[60.0], real:[60.0] }
};
const logsCSV = [];

function addMatrixLog(msg){
  const box = $('matrix-log');
  const lines = (box.textContent + msg + '\n').split('\n');
  if(lines.length > 90) lines.splice(0, lines.length - 90);
  box.textContent = lines.join('\n');
  box.scrollTop = box.scrollHeight;
}

function trocarTela(nome){
  document.querySelectorAll('.tela').forEach(el => el.classList.remove('active'));
  $('tela-' + nome).classList.add('active');
  document.querySelectorAll('[data-tela]').forEach(b => b.classList.toggle('active', b.dataset.tela === nome));
  setTimeout(desenharTodosGraficos, 40);
}
document.querySelectorAll('[data-tela]').forEach(b => b.addEventListener('click', () => trocarTela(b.dataset.tela)));

document.querySelectorAll('[data-sinc]').forEach(b => b.addEventListener('click', () => {
  paramSincAtivo = b.dataset.sinc;
  document.querySelectorAll('[data-sinc]').forEach(x => x.classList.toggle('active', x === b));
  desenharTodosGraficos();
}));

$('sl-vel').addEventListener('input', e => { $('lbl-vel').textContent = e.target.value + 'x'; });

function aplicarTemaModo(){
  const cor = modoHardwareReal ? '#38BDF8' : '#F59E0B';
  document.documentElement.style.setProperty('--theme', cor);
  $('sw-hw-top').classList.toggle('on', modoHardwareReal);
  $('sw-hw-cfg').classList.toggle('on', modoHardwareReal);
  document.querySelectorAll('.sim-sl').forEach(s => s.disabled = modoHardwareReal);
  if(modoHardwareReal){
    if(demonstracaoAtiva) alternarDemonstracao();
    $('lbl-status-esp').textContent = '● ESP32 REAL CONECTADO (Wi-Fi)';
  } else {
    $('lbl-status-esp').textContent = '● SIMULADOR MANUAL (GÊMEO DIGITAL)';
  }
}

function alternarModoHardware(){
  modoHardwareReal = !modoHardwareReal;
  aplicarTemaModo();
  addMatrixLog(modoHardwareReal ? '[INFO] Modo ESP32 Wi-Fi ativado.' : '[INFO] Modo Simulador Manual ativado.');
  atualizarInterface();
}

function diagnosticarSimulador(minDecorridos){
  let estresse = 0;
  if(gem.nivel_agua <= 0) estresse += 0.20;
  else if(gem.nivel_agua <= 20) estresse += 0.05;
  if(gem.ph < gem.ph_min || gem.ph > gem.ph_max) estresse += 0.05;
  if(gem.ec < gem.ec_min) estresse += 0.05;
  else if(gem.ec > gem.ec_max) estresse += 0.06;
  if(gem.temperatura_ar < gem.temp_ar_min || gem.temperatura_ar > gem.temp_ar_max) estresse += 0.04;
  if(gem.temperatura_agua < gem.temp_agua_min || gem.temperatura_agua > gem.temp_agua_max) estresse += 0.08;

  if(minDecorridos > 0){
    if(estresse > 0) gem.saude = Math.max(0, gem.saude - estresse * minDecorridos * 1.5);
    else gem.saude = Math.min(100, gem.saude + 0.05 * minDecorridos);
  } else {
    let pts = 100;
    if(gem.ph < gem.ph_min || gem.ph > gem.ph_max) pts -= 25;
    if(gem.ec < gem.ec_min || gem.ec > gem.ec_max) pts -= 20;
    if(gem.nivel_agua <= 20) pts -= 25;
    if(gem.temperatura_ar < gem.temp_ar_min || gem.temperatura_ar > gem.temp_ar_max) pts -= 15;
    if(gem.temperatura_agua < gem.temp_agua_min || gem.temperatura_agua > gem.temp_agua_max) pts -= 10;
    if(gem.umidade_ar < gem.umidade_min || gem.umidade_ar > gem.umidade_max) pts -= 15;
    gem.saude = Math.max(0, pts);
  }

  // Automação igual ao horta.py / automacao.h
  const ini = gem.inicio_luz * 60 + gem.inicio_minuto;
  const dur = Math.round(gem.fotoperiodo * 60);
  const fim = (ini + dur) % 1440;
  const ag = gem.hora_v * 60 + gem.min_v;
  const noHorario = dur >= 1440 ? true : (dur <= 0 ? false : (ini < fim ? (ag >= ini && ag < fim) : (ag >= ini || ag < fim)));
  gem.luz = gem.modo_luz === 1 ? true : (gem.modo_luz === 2 ? false : noHorario);
  gem.exaustor = gem.modo_exaustor === 1 ? true : (gem.modo_exaustor === 2 ? false : (gem.temperatura_ar > gem.temp_ar_max || gem.umidade_ar > gem.umidade_max));
  const crit = gem.nivel_agua <= 10;
  gem.bomba_ar = !crit;
  if(crit) gem.bomba_agua = false;
  else if(gem.modo_bomba_agua === 1) gem.bomba_agua = true;
  else if(gem.modo_bomba_agua === 2) gem.bomba_agua = false;
  else {
    const ciclo = Math.max(1, gem.bomba_on + gem.bomba_off);
    gem.bomba_agua = (ag % ciclo) < gem.bomba_on;
  }
}

function onSimSlider(campo, val){
  if(modoHardwareReal) return;
  gem[campo] = parseFloat(val);
  diagnosticarSimulador(0);
  atualizarInterface();
}

function avancarTempo(min){
  if(modoHardwareReal){
    addMatrixLog('[AVISO] Desative o Modo ESP32 para avançar o tempo no Simulador.');
    return;
  }
  minutosSimulados += min;
  gem.dia_cultivo = Math.floor(minutosSimulados / 1440);
  const tot = gem.hora_v * 60 + gem.min_v + min;
  gem.hora_v = Math.floor((tot / 60) % 24);
  gem.min_v = tot % 60;
  diagnosticarSimulador(min);
  registrarHistorico();
  atualizarInterface();
}

function alternarDemonstracao(){
  if(modoHardwareReal && !demonstracaoAtiva){
    addMatrixLog('[AVISO] Alterne para o Modo Simulador para iniciar a simulação.');
    return;
  }
  demonstracaoAtiva = !demonstracaoAtiva;
  const b = $('btn-sim-toggle');
  if(demonstracaoAtiva){
    b.textContent = '⏸ PAUSAR SIMULADOR';
    b.className = 'ctk-btn btn-red';
  } else {
    b.textContent = '▶ INICIAR SIMULADOR';
    b.className = 'ctk-btn btn-amber';
  }
}

function resetarPlanta(){
  minutosSimulados = 0;
  Object.assign(gem, {
    temperatura_ar:24.5, umidade_ar:60.0, temperatura_agua:22.0,
    ph:6.0, ec:1.4, nivel_agua:100.0, saude:100.0, dia_cultivo:0, hora_v:13, min_v:0
  });
  hist.saude = [100];
  ['ph','ec','temp_ar','temp_agua','umidade'].forEach(k => {
    hist[k].gem = [gem[k === 'umidade' ? 'umidade_ar' : (k === 'temp_ar' ? 'temperatura_ar' : (k === 'temp_agua' ? 'temperatura_agua' : k))]];
    hist[k].real = [...hist[k].gem];
  });
  sincronizarSliders(gem);
  atualizarInterface();
  addMatrixLog('[SISTEMA] Cultivo resetado para o Dia 0.');
}

function sincronizarSliders(d){
  $('sl-tar').value = d.temperatura_ar; $('sv-tar').textContent = d.temperatura_ar.toFixed(1) + ' °C';
  $('sl-umi').value = d.umidade_ar;     $('sv-umi').textContent = d.umidade_ar.toFixed(1) + ' %';
  $('sl-tag').value = d.temperatura_agua; $('sv-tag').textContent = d.temperatura_agua.toFixed(1) + ' °C';
  $('sl-ph').value = d.ph;              $('sv-ph').textContent = d.ph.toFixed(2);
  $('sl-ec').value = d.ec;              $('sv-ec').textContent = d.ec.toFixed(2) + ' mS/cm';
  $('sl-niv').value = d.nivel_agua;     $('sv-niv').textContent = d.nivel_agua.toFixed(1) + ' %';
}

function atualizarResumosReceita(cfg){
  const pad = n => String(n).padStart(2,'0');
  $('res-luz').textContent = `☀️ Iluminação: ${Number(cfg.fotoperiodo).toFixed(1)} h/dia (Início ${pad(cfg.inicio_luz)}:${pad(cfg.inicio_minuto||0)})`;
  $('res-bomba').textContent = `💧 Irrigação: ${cfg.bomba_on}m ON / ${cfg.bomba_off}m OFF`;
  $('res-fan').textContent = `💨 Clima: Exaustão > ${Number(cfg.temp_ar_max).toFixed(1)}°C`;
  $('res-ph').textContent = `🧪 pH: ${cfg.ph_min} a ${cfg.ph_max}`;
  $('res-ec').textContent = `⚡ EC: ${cfg.ec_min} a ${cfg.ec_max}`;
  $('res-tar').textContent = `🌡️ Ar: ${cfg.temp_ar_min} a ${cfg.temp_ar_max} °C`;
  $('res-tag').textContent = `🌊 Água: ${cfg.temp_agua_min} a ${cfg.temp_agua_max} °C`;
  $('res-umi').textContent = `💦 Umidade Ar: ${cfg.umidade_min} a ${cfg.umidade_max} %`;

  ['MUDA','VEGETATIVO','FLORACAO'].forEach(f => {
    const el = $('bf-' + f);
    if(el) el.classList.toggle('active', (cfg.fase || 'VEGETATIVO').indexOf(f.slice(0,4)) === 0);
  });

  // Guia de correção nutricional (mesma fórmula do horta.py)
  const d = modoHardwareReal ? ultimoEsp : gem;
  const litros = Math.max(0.5, (d.nivel_agua / 100) * 10.0);
  const taxa = parseFloat($('in-fert-taxa').value) || 0.84;
  const ecAlvo = (cfg.ec_min + cfg.ec_max) / 2;
  const phAlvo = (cfg.ph_min + cfg.ph_max) / 2;
  const diffEc = Math.max(0, ecAlvo - d.ec);
  const diffPh = d.ph - phAlvo;
  const gramas = diffEc * taxa * litros;
  let acaoPh = 'Estável (Ideal)', mlPh = 0;
  if(diffPh > 0.2){ acaoPh = 'Aplicar pH Down'; mlPh = diffPh * 0.5 * litros; }
  else if(diffPh < -0.2){ acaoPh = 'Aplicar pH Up'; mlPh = Math.abs(diffPh) * 0.5 * litros; }
  $('lbl-guia-nutri').textContent = `Vol: ${litros.toFixed(1)}L | Fert A+B: +${gramas.toFixed(1)}g\npH Correção: ${acaoPh} (${mlPh.toFixed(1)}ml)`;
}

function atualizarInterface(){
  const d = modoHardwareReal ? ultimoEsp : gem;
  const cfg = gem;

  const cultNome = ($('in-nome-cultivo').value || d.cultura || 'ALFACE').toUpperCase();
  const origem = modoHardwareReal ? 'Hardware ESP32' : 'Simulador';
  $('lbl-sub-cultivo').textContent = `${cultNome} • Fase: ${d.fase || cfg.fase} • Dia: ${d.dia_cultivo || 0} (${origem})`;

  const saude = Math.round(d.saude ?? 100);
  const corSaude = saude > 80 ? 'var(--green)' : (saude >= 40 ? 'var(--amber)' : 'var(--red)');
  $('lbl-saude-pct').textContent = saude + '%';
  $('lbl-saude-pct').style.color = corSaude;
  $('card-saude').style.borderColor = corSaude;

  const probs = [];
  if(d.ph < cfg.ph_min) probs.push(`• pH baixo (${d.ph.toFixed(2)} < ${cfg.ph_min})`);
  else if(d.ph > cfg.ph_max) probs.push(`• pH alto (${d.ph.toFixed(2)} > ${cfg.ph_max})`);
  if(d.ec < cfg.ec_min) probs.push(`• EC baixa (${d.ec.toFixed(1)} < ${cfg.ec_min})`);
  else if(d.ec > cfg.ec_max) probs.push(`• EC alta (${d.ec.toFixed(1)} > ${cfg.ec_max})`);
  if(d.temperatura_ar < cfg.temp_ar_min) probs.push(`• Ar frio (${d.temperatura_ar.toFixed(1)}°C)`);
  else if(d.temperatura_ar > cfg.temp_ar_max) probs.push(`• Ar quente (${d.temperatura_ar.toFixed(1)}°C)`);
  if(d.temperatura_agua < cfg.temp_agua_min) probs.push(`• Água fria (${d.temperatura_agua.toFixed(1)}°C)`);
  else if(d.temperatura_agua > cfg.temp_agua_max) probs.push(`• Água quente (${d.temperatura_agua.toFixed(1)}°C)`);
  if(d.nivel_agua < 20) probs.push('• Reservatório baixo / Seco');

  if(probs.length === 0 && saude > 80){
    $('lbl-saude-txt').textContent = '✅ Condições ideais para o desenvolvimento';
    $('lbl-saude-txt').style.color = 'var(--green)';
  } else {
    $('lbl-saude-txt').textContent = '⚠️ Anomalias Detectadas:\n' + probs.join('\n');
    $('lbl-saude-txt').style.color = 'var(--red)';
  }

  $('d-temp').textContent = d.temperatura_ar.toFixed(1) + ' °C';
  $('d-umid').textContent = d.umidade_ar.toFixed(0) + ' %';
  $('d-tagua').textContent = d.temperatura_agua.toFixed(1) + ' °C';
  $('d-ph').textContent = d.ph.toFixed(2);
  $('d-ec').textContent = d.ec.toFixed(1) + ' mS/cm';
  $('d-nivel').textContent = d.nivel_agua > 90 ? 'OK (100%)' : d.nivel_agua.toFixed(0) + '%';
  $('d-nivel').style.color = d.nivel_agua > 20 ? 'var(--green)' : 'var(--red)';

  // Status Exaustor e Luz idênticos ao janela_principal.py
  let fanTxt = 'OFF (Auto)', fanCol = 'var(--muted)';
  if(d.modo_exaustor === 1){ fanTxt = 'ON (Manual)'; fanCol = 'var(--green)'; }
  else if(d.modo_exaustor === 2){ fanTxt = 'OFF (Manual)'; fanCol = 'var(--red)'; }
  else if(d.exaustor){
    if(d.temperatura_ar > cfg.temp_ar_max){ fanTxt = 'ON (Calor)'; fanCol = 'var(--orange)'; }
    else { fanTxt = 'ON (Umidade)'; fanCol = 'var(--blue)'; }
  }
  $('d-fan').textContent = fanTxt; $('d-fan').style.color = fanCol;

  let luzTxt = d.luz ? 'ON (Ativa)' : 'OFF (Noturno)', luzCol = d.luz ? 'var(--amber)' : 'var(--muted)';
  if(d.modo_luz === 1){ luzTxt = 'ON (Manual)'; luzCol = 'var(--green)'; }
  else if(d.modo_luz === 2){ luzTxt = 'OFF (Manual)'; luzCol = 'var(--red)'; }
  $('d-luz').textContent = luzTxt; $('d-luz').style.color = luzCol;

  // Segmented buttons de atuadores
  const setSeg = (p, m) => { for(let i=0;i<3;i++) $(p+'-'+i).classList.toggle('active', m===i); };
  setSeg('seg-luz', d.modo_luz);
  setSeg('seg-fan', d.modo_exaustor);
  setSeg('seg-bomba', d.modo_bomba_agua);

  $('lbl-bomba-ar').textContent = `AR: ${d.bomba_ar ? 'ON' : 'PARADO'} | ÁGUA: ${d.bomba_agua ? 'ON' : 'OFF'}`;
  $('lbl-bomba-ar').style.color = d.bomba_ar ? 'var(--green)' : 'var(--red)';

  // Metas nos sliders
  $('sm-tar').textContent = `Meta: ${cfg.temp_ar_min} a ${cfg.temp_ar_max} °C`;
  $('sm-umi').textContent = `Meta: ${cfg.umidade_min} a ${cfg.umidade_max} %`;
  $('sm-tag').textContent = `Meta: ${cfg.temp_agua_min} a ${cfg.temp_agua_max} °C`;
  $('sm-ph').textContent  = `Meta: ${cfg.ph_min} a ${cfg.ph_max}`;
  $('sm-ec').textContent  = `Meta: ${cfg.ec_min} a ${cfg.ec_max} mS/cm`;

  // Comparativo Real vs Gêmeo
  const r = ultimoEsp;
  $('cr-saude').textContent = Math.round(r.saude ?? saude) + '%';
  $('cr-tar').textContent = r.temperatura_ar.toFixed(1) + ' °C';
  $('cr-umi').textContent = r.umidade_ar.toFixed(0) + ' %';
  $('cr-tag').textContent = r.temperatura_agua.toFixed(1) + ' °C';
  $('cr-ph').textContent = r.ph.toFixed(2);
  $('cr-ec').textContent = r.ec.toFixed(1) + ' mS/cm';
  $('cr-niv').textContent = r.nivel_agua.toFixed(0) + '%';

  $('cg-saude').textContent = Math.round(gem.saude) + '%';
  $('cg-tar').textContent = gem.temperatura_ar.toFixed(1) + ' °C';
  $('cg-umi').textContent = gem.umidade_ar.toFixed(0) + ' %';
  $('cg-tag').textContent = gem.temperatura_agua.toFixed(1) + ' °C';
  $('cg-ph').textContent = gem.ph.toFixed(2);
  $('cg-ec').textContent = gem.ec.toFixed(1) + ' mS/cm';
  $('cg-niv').textContent = gem.nivel_agua.toFixed(0) + '%';

  // Relógio topo sidebar
  const pad = n => String(n).padStart(2,'0');
  const dataStr = ultimoEsp.data || new Date().toLocaleDateString('pt-BR');
  if(modoHardwareReal && ultimoEsp.hora){
    $('lbl-relogio').textContent = `RTC ${ultimoEsp.hora}  ${dataStr}`;
  } else {
    $('lbl-relogio').textContent = `${pad(gem.hora_v)}:${pad(gem.min_v)}  Dia ${gem.dia_cultivo}`;
  }

  // Info Hardware na aba Config
  $('cfg-info-rede').innerHTML =
    `• Modo Wi-Fi: <b>${ultimoEsp.wifi_ap ? 'Access Point Reserva (HortaDoFuturo)' : 'Conectado à Rede Local (horta.local)'}</b><br>` +
    `• Endereço IP: <b>http://${ultimoEsp.ip || '192.168.4.1'}</b><br>` +
    `• Relógio RTC: <b>${ultimoEsp.rtc_ok ? 'DS3231 Ativo (Hardware)' : 'Software Timer'}</b> | Cartão SD: <b>${ultimoEsp.sd_ok ? 'Gravando /telemetria.csv' : 'Não detectado'}</b>`;
  $('btn-sd-link').style.display = ultimoEsp.sd_ok ? 'inline-flex' : 'none';

  atualizarResumosReceita(cfg);
  desenharTodosGraficos();
}

function registrarHistorico(){
  const push = (arr, v) => { arr.push(v); if(arr.length > 30) arr.shift(); };
  push(hist.saude, modoHardwareReal ? (ultimoEsp.saude ?? 100) : gem.saude);
  push(hist.ph.gem, gem.ph);               push(hist.ph.real, ultimoEsp.ph);
  push(hist.ec.gem, gem.ec);               push(hist.ec.real, ultimoEsp.ec);
  push(hist.temp_ar.gem, gem.temperatura_ar); push(hist.temp_ar.real, ultimoEsp.temperatura_ar);
  push(hist.temp_agua.gem, gem.temperatura_agua); push(hist.temp_agua.real, ultimoEsp.temperatura_agua);
  push(hist.umidade.gem, gem.umidade_ar);  push(hist.umidade.real, ultimoEsp.umidade_ar);

  const d = modoHardwareReal ? ultimoEsp : gem;
  logsCSV.push([new Date().toISOString(), Math.round(d.saude), d.temperatura_ar.toFixed(1), d.umidade_ar.toFixed(0), d.temperatura_agua.toFixed(1), d.ph.toFixed(2), d.ec.toFixed(2)]);
  if(logsCSV.length > 1000) logsCSV.shift();
}

function drawPlot(id, series, yMin, yMax, yLabel){
  const c = $(id);
  if(!c || !c.offsetWidth) return;
  const dpr = window.devicePixelRatio || 1;
  const w = c.offsetWidth, h = c.offsetHeight;
  c.width = w * dpr; c.height = h * dpr;
  const ctx = c.getContext('2d');
  ctx.scale(dpr, dpr);
  ctx.fillStyle = '#050B14';
  ctx.fillRect(0, 0, w, h);

  const pL = 44, pR = 14, pT = 18, pB = 24;
  const gw = w - pL - pR, gh = h - pT - pB;
  const yOf = v => pT + gh - ((Math.max(yMin, Math.min(yMax, v)) - yMin) / (yMax - yMin)) * gh;

  // Eixos #1E293B e ticks #94A3B8 como configurar_estilo_eixo() do matplotlib
  ctx.strokeStyle = '#1E293B'; ctx.lineWidth = 1;
  ctx.fillStyle = '#94A3B8'; ctx.font = '11px "Segoe UI",sans-serif'; ctx.textAlign = 'right';
  for(let i = 0; i <= 4; i++){
    const v = yMin + (yMax - yMin) * (i / 4);
    const y = yOf(v);
    ctx.beginPath(); ctx.moveTo(pL, y); ctx.lineTo(pL + gw, y); ctx.stroke();
    ctx.fillText(v.toFixed(yMax - yMin <= 5 ? 1 : 0), pL - 6, y + 4);
  }
  ctx.beginPath();
  ctx.moveTo(pL, pT); ctx.lineTo(pL, pT + gh); ctx.lineTo(pL + gw, pT + gh);
  ctx.stroke();

  series.forEach(s => {
    const arr = s.data || [];
    if(!arr.length) return;
    ctx.beginPath();
    ctx.strokeStyle = s.color;
    ctx.lineWidth = 2.2;
    ctx.setLineDash(s.dashed ? [5, 4] : []);
    arr.forEach((v, i) => {
      const x = pL + (arr.length === 1 ? gw / 2 : (i / (arr.length - 1)) * gw);
      const y = yOf(v);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.stroke();
    ctx.setLineDash([]);
  });

  // Legenda no canto superior direito
  if(series.length > 1){
    let lx = pL + gw - 8;
    ctx.font = 'bold 11px "Segoe UI",sans-serif';
    for(let i = series.length - 1; i >= 0; i--){
      const s = series[i];
      const tw = ctx.measureText(s.label).width;
      ctx.fillStyle = '#F8FAFC';
      ctx.textAlign = 'right';
      ctx.fillText(s.label, lx, pT + 12);
      ctx.fillStyle = s.color;
      ctx.fillRect(lx - tw - 16, pT + 4, 12, 4);
      lx -= tw + 28;
    }
  }
}

function desenharTodosGraficos(){
  const corSaude = modoHardwareReal ? '#38BDF8' : '#F59E0B';
  drawPlot('cv-saude', [{ label:'Saúde (%)', data:hist.saude, color:corSaude }], 0, 105, 'Saúde (%)');
  drawPlot('cv-nutri', [
    { label:'pH', data:modoHardwareReal ? hist.ph.real : hist.ph.gem, color:'#38BDF8' },
    { label:'EC', data:modoHardwareReal ? hist.ec.real : hist.ec.gem, color:'#FB923C' }
  ], 0, 14, 'pH / EC');
  drawPlot('cv-termico', [
    { label:'Ar', data:modoHardwareReal ? hist.temp_ar.real : hist.temp_ar.gem, color:'#EF4444' },
    { label:'Água', data:modoHardwareReal ? hist.temp_agua.real : hist.temp_agua.gem, color:'#2DD4BF' }
  ], 10, 45, 'Temp (°C)');

  const mapa = {
    ph: { min:4, max:9, lbl:'pH' },
    ec: { min:0, max:3, lbl:'EC (mS/cm)' },
    temp_ar: { min:10, max:40, lbl:'Temp Ar (°C)' },
    temp_agua: { min:10, max:35, lbl:'Temp Água (°C)' },
    umidade: { min:0, max:100, lbl:'Umidade (%)' }
  };
  const m = mapa[paramSincAtivo];
  drawPlot('cv-sinc', [
    { label: m.lbl + ' Gêmeo', data: hist[paramSincAtivo].gem, color:'#F59E0B' },
    { label: m.lbl + ' ESP32 Real', data: hist[paramSincAtivo].real, color:'#38BDF8', dashed:true }
  ], m.min, m.max, m.lbl);
}

// ==================== COMANDOS PARA O ESP32 ====================
async function enviarComandoESP32(pacote, logMsg){
  try{
    const r = await fetch('/api/cmd', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(pacote)
    });
    if(!r.ok) throw new Error('HTTP ' + r.status);
    const d = await r.json();
    aplicarTelemetriaESP32(d);
    if(logMsg) addMatrixLog(logMsg);
  }catch(e){
    addMatrixLog('[AVISO] Comando aplicado localmente no Gêmeo Digital.');
  }
}

function setModoAtuador(campo, val){
  gem[campo] = val;
  ultimoEsp[campo] = val;
  diagnosticarSimulador(0);
  atualizarInterface();
  const nomes = {0:'AUTO',1:'ON',2:'OFF'};
  enviarComandoESP32({
    cmd:'set_actuators',
    modo_luz: ultimoEsp.modo_luz,
    modo_exaustor: ultimoEsp.modo_exaustor,
    modo_bomba_agua: ultimoEsp.modo_bomba_agua
  }, `[COMANDO -> ESP32] ${campo} definido para ${nomes[val]}`);
}

function aplicarCalibracao(){
  const off = parseFloat($('in-off-ph').value) || 0.0;
  const fat = Math.max(0.1, parseFloat($('in-fat-ec').value) || 1.0);
  gem.offset_ph = off; gem.fator_ec = fat;
  enviarComandoESP32({ cmd:'set_calibration', offset_ph:off, fator_ec:fat },
    `[SUCESSO] Calibração transmitida ao ESP32! Offset pH: ${off.toFixed(2)}, Fator EC: ${fat.toFixed(2)}`);
}

// ==================== RECEITAS, MODAIS & CULTIVOS ====================
function popularDropdowns(){
  const s1 = $('sel-cultivo-salvo');
  s1.innerHTML = '';
  Object.keys(cultivosSalvos).forEach(k => {
    const o = document.createElement('option'); o.value = k; o.textContent = k; s1.appendChild(o);
  });
  const s2 = $('sel-especie');
  s2.innerHTML = '';
  Object.keys(ESPECIES_BASE).forEach(k => {
    const o = document.createElement('option'); o.value = k; o.textContent = k; s2.appendChild(o);
  });
}

function carregarCultivoSalvo(nome){
  const c = cultivosSalvos[nome];
  if(!c) return;
  Object.assign(gem, c, { nome_cultivo:nome });
  $('in-nome-cultivo').value = nome;
  $('sel-especie').value = c.cultura;
  $('in-fert-nome').value = c.fertilizante || 'Flex Azul + Vermelho (A+B)';
  $('in-fert-taxa').value = c.taxa_ab || 0.84;
  diagnosticarSimulador(0);
  atualizarInterface();
  addMatrixLog(`[INFO] Cultivo '${nome}' carregado com sucesso!`);
}

function selecionarEspecie(espNome){
  const base = ESPECIES_BASE[espNome];
  if(!base) return;
  Object.assign(gem, base, { cultura:espNome });
  diagnosticarSimulador(0);
  atualizarInterface();
  addMatrixLog(`[INFO] Espécie carregada: ${espNome} (Metas aplicadas)`);
}

function novoCultivoLimpo(){
  $('in-nome-cultivo').value = 'Novo Cultivo #01';
  selecionarEspecie('ALFACE');
  mudarFase('VEGETATIVO');
  addMatrixLog('[INFO] Formulário restaurado para o padrão.');
}

function mudarFase(novaFase){
  gem.fase = novaFase;
  if(novaFase === 'MUDA'){ gem.fotoperiodo = 18; gem.ec_min = 0.8; gem.ec_max = 1.2; }
  else if(novaFase === 'FLORACAO'){ gem.fotoperiodo = 12; gem.ec_min = 1.8; gem.ec_max = 2.5; }
  else { gem.fotoperiodo = 16; gem.ec_min = 1.2; gem.ec_max = 1.8; }
  diagnosticarSimulador(0);
  atualizarInterface();
}

function abrirModal(id){
  if(id === 'modal-auto'){
    $('m-foto').value = gem.fotoperiodo;
    $('m-hora').value = gem.inicio_luz;
    $('m-min').value = gem.inicio_minuto || 0;
    $('m-bon').value = gem.bomba_on;
    $('m-boff').value = gem.bomba_off;
  } else if(id === 'modal-metas'){
    $('m-ph-min').value = gem.ph_min; $('m-ph-max').value = gem.ph_max;
    $('m-ec-min').value = gem.ec_min; $('m-ec-max').value = gem.ec_max;
    $('m-tar-min').value = gem.temp_ar_min; $('m-tar-max').value = gem.temp_ar_max;
    $('m-tag-min').value = gem.temp_agua_min; $('m-tag-max').value = gem.temp_agua_max;
    $('m-umi-min').value = gem.umidade_min; $('m-umi-max').value = gem.umidade_max;
  }
  $(id).classList.add('open');
}
function fecharModais(){
  document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.remove('open'));
}

function salvarModalAutomacao(){
  gem.fotoperiodo = Math.max(0, Math.min(24, parseFloat($('m-foto').value) || 18));
  gem.inicio_luz = Math.max(0, Math.min(23, parseInt($('m-hora').value, 10) || 6));
  gem.inicio_minuto = Math.max(0, Math.min(59, parseInt($('m-min').value, 10) || 0));
  gem.bomba_on = Math.max(1, parseInt($('m-bon').value, 10) || 15);
  gem.bomba_off = Math.max(0, parseInt($('m-boff').value, 10) || 45);
  fecharModais();
  diagnosticarSimulador(0);
  atualizarInterface();
}

function salvarModalMetas(){
  gem.ph_min = parseFloat($('m-ph-min').value); gem.ph_max = parseFloat($('m-ph-max').value);
  gem.ec_min = parseFloat($('m-ec-min').value); gem.ec_max = parseFloat($('m-ec-max').value);
  gem.temp_ar_min = parseFloat($('m-tar-min').value); gem.temp_ar_max = parseFloat($('m-tar-max').value);
  gem.temp_agua_min = parseFloat($('m-tag-min').value); gem.temp_agua_max = parseFloat($('m-tag-max').value);
  gem.umidade_min = parseFloat($('m-umi-min').value); gem.umidade_max = parseFloat($('m-umi-max').value);
  fecharModais();
  diagnosticarSimulador(0);
  atualizarInterface();
}

function salvarNovaEspecie(){
  const nome = ($('m-esp-nome').value || '').trim().toUpperCase();
  const foto = parseFloat($('m-esp-foto').value) || 16;
  if(!nome) return;
  ESPECIES_BASE[nome] = { ph_min:5.8, ph_max:6.3, ec_min:1.2, ec_max:2.0, temp_ar_min:18, temp_ar_max:28, temp_agua_min:18, temp_agua_max:24, umidade_min:60, umidade_max:80, fotoperiodo:foto };
  popularDropdowns();
  $('sel-especie').value = nome;
  selecionarEspecie(nome);
  fecharModais();
  addMatrixLog(`[SUCESSO] Nova espécie '${nome}' cadastrada!`);
}

function aplicarCorrecaoSimulador(){
  if(modoHardwareReal){
    alert('No Modo ESP32 real, faça a dosagem física no reservatório seguindo as quantidades do Guia Nutricional.');
    return;
  }
  gem.ec = Number(((gem.ec_min + gem.ec_max) / 2).toFixed(2));
  gem.ph = Number(((gem.ph_min + gem.ph_max) / 2).toFixed(2));
  sincronizarSliders(gem);
  diagnosticarSimulador(0);
  atualizarInterface();
  addMatrixLog(`[DOSAGEM SIMULADOR] Solução corrigida -> pH=${gem.ph.toFixed(2)}, EC=${gem.ec.toFixed(2)}`);
}

function salvarReceitaLocal(){
  const nome = ($('in-nome-cultivo').value || 'Cultivo #01').trim();
  gem.cultura = $('sel-especie').value || 'ALFACE';
  cultivosSalvos[nome] = {
    ...gem,
    fertilizante: $('in-fert-nome').value,
    taxa_ab: parseFloat($('in-fert-taxa').value) || 0.84
  };
  popularDropdowns();
  $('sel-cultivo-salvo').value = nome;
  atualizarInterface();
  addMatrixLog(`[SUCESSO] Cultivo '${nome}' salvo localmente!`);
}

function sincronizarReceitaESP32(){
  gem.cultura = $('sel-especie').value || 'ALFACE';
  enviarComandoESP32({
    cmd:'set_config',
    cultura: gem.cultura,
    fase: gem.fase,
    ph_min: gem.ph_min, ph_max: gem.ph_max,
    ec_min: gem.ec_min, ec_max: gem.ec_max,
    temp_ar_min: gem.temp_ar_min, temp_ar_max: gem.temp_ar_max,
    temp_agua_min: gem.temp_agua_min, temp_agua_max: gem.temp_agua_max,
    umidade_min: gem.umidade_min, umidade_max: gem.umidade_max,
    fotoperiodo: gem.fotoperiodo,
    inicio_luz: gem.inicio_luz,
    inicio_minuto: gem.inicio_minuto || 0,
    bomba_on: gem.bomba_on,
    bomba_off: gem.bomba_off
  }, '[SUCESSO] Parâmetros da receita sincronizados com o ESP32 via Wi-Fi!');
}

function sincronizarRelogioRTC(){
  const now = new Date();
  enviarComandoESP32({
    cmd:'set_clock',
    hora:now.getHours(), minuto:now.getMinutes(), segundo:now.getSeconds()
  }, `[RTC -> ESP32] Horário sincronizado: ${now.toLocaleTimeString('pt-BR')}`);
}

function solicitarTelemetriaAgora(){
  enviarComandoESP32({ cmd:'sync_request' }, '[WIFI -> ESP32] Solicitação de telemetria imediata enviada.');
}

async function salvarWifiNVS(){
  const ssid = $('in-wifi-ssid').value.trim();
  const senha = $('in-wifi-pass').value;
  if(!ssid){ alert('Informe o SSID da rede Wi-Fi.'); return; }
  try{
    await fetch('/api/wifi', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ssid,senha}) });
    addMatrixLog(`[WIFI] Credenciais salvas para '${ssid}'. Reiniciando ESP32...`);
    setTimeout(() => fetch('/api/reboot', { method:'POST' }).catch(()=>{}), 400);
  }catch(e){ addMatrixLog('[ERRO] Falha ao salvar Wi-Fi.'); }
}

function reiniciarESP32(){
  if(!confirm('Reiniciar o ESP32 agora?')) return;
  fetch('/api/reboot', { method:'POST' }).catch(()=>{});
  addMatrixLog('[SISTEMA] Reiniciando ESP32...');
}

function exportarLogsCSV(){
  const hdr = 'Timestamp,Saude,TempAr,UmidAr,TempAgua,pH,EC\n';
  const csv = hdr + logsCSV.map(r => r.join(',')).join('\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8'}));
  a.download = 'telemetria_horta.csv';
  a.click();
  addMatrixLog('[SUCESSO] Relatório CSV exportado.');
}

function aplicarTelemetriaESP32(d){
  ultimoEsp = { ...ultimoEsp, ...d };
  if(!receitaSincronizadaInicial || modoHardwareReal){
    receitaSincronizadaInicial = true;
    ['cultura','fase','ph_min','ph_max','ec_min','ec_max','temp_ar_min','temp_ar_max','temp_agua_min','temp_agua_max','umidade_min','umidade_max','fotoperiodo','inicio_luz','inicio_minuto','bomba_on','bomba_off','modo_luz','modo_exaustor','modo_bomba_agua','offset_ph','fator_ec'].forEach(k => {
      if(d[k] !== undefined) gem[k] = d[k];
    });
    if(document.activeElement !== $('in-off-ph')) $('in-off-ph').value = Number(d.offset_ph ?? 0).toFixed(1);
    if(document.activeElement !== $('in-fat-ec')) $('in-fat-ec').value = Number(d.fator_ec ?? 1).toFixed(2);
  }
  if(modoHardwareReal){
    ['temperatura_ar','umidade_ar','temperatura_agua','ph','ec','nivel_agua','saude','dia_cultivo','luz','exaustor','bomba_agua','bomba_ar'].forEach(k => {
      if(d[k] !== undefined) gem[k] = d[k];
    });
    sincronizarSliders(d);
  }
  registrarHistorico();
  atualizarInterface();
}

async function carregarHistoricoInicial(){
  try{
    const r = await fetch('/api/history');
    if(!r.ok) return;
    const h = await r.json();
    if(Array.isArray(h.ph) && h.ph.length){ hist.ph.real = [...h.ph]; hist.ph.gem = [...h.ph]; }
    if(Array.isArray(h.ec) && h.ec.length){ hist.ec.real = [...h.ec]; hist.ec.gem = [...h.ec]; }
    if(Array.isArray(h.temp_ar) && h.temp_ar.length){ hist.temp_ar.real = [...h.temp_ar]; hist.temp_ar.gem = [...h.temp_ar]; }
    if(Array.isArray(h.umidade_ar) && h.umidade_ar.length){ hist.umidade.real = [...h.umidade_ar]; hist.umidade.gem = [...h.umidade_ar]; }
  }catch(e){}
}

async function cicloPolling(){
  if(demonstracaoAtiva && !modoHardwareReal){
    const vel = parseInt($('sl-vel').value, 10) || 1;
    avancarTempo(vel);
  }
  try{
    const r = await fetch('/api/status', { cache:'no-store' });
    if(!r.ok) throw new Error();
    const d = await r.json();
    addMatrixLog('[ESP32] ' + JSON.stringify(d));
    aplicarTelemetriaESP32(d);
  }catch(e){
    if(modoHardwareReal){
      $('lbl-status-esp').textContent = '● RECONECTANDO AO ESP32...';
    }
  }
}

window.addEventListener('resize', desenharTodosGraficos);
popularDropdowns();
aplicarTemaModo();
sincronizarSliders(gem);
atualizarInterface();
carregarHistoricoInicial().then(cicloPolling);
setInterval(cicloPolling, 2000);
</script>
</body>
</html>)HORTA_HTML";

#endif
