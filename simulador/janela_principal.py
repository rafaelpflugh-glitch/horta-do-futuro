import customtkinter as ctk
import json
import os
import csv
import threading
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    import serial
    import serial.tools.list_ports
    SERIAL_DISPONIVEL = True
except ImportError:
    SERIAL_DISPONIVEL = False

from modelo.horta import Horta
from modelo.configuracao import ConfiguracaoCultivo
from modelo.banco_cultivos import listar_culturas


class JanelaPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("HORTA DO FUTURO — Digital Twin & Hardware Controller")
        self.geometry("1520x940")
        self.minsize(1200, 800)

        self.configure(fg_color="#030508")

        self.horta = Horta()
        self.automacao_ativa = True
        self.demonstracao_ativa = False
        self.modo_hardware_real = False
        
        self.parametro_sincronia_ativo = "ph"
        
        self.ser = None
        self.serial_thread_ativa = False
        self.log_serial_buffer = ["[INFO] Sistema inicializado. Modo Gêmeo Digital / Simulador ativo.\n"]
        self.ultimo_valor_esp = {
            "temperatura_ar": 24.5, "umidade_ar": 60.0, "temperatura_agua": 22.0,
            "ph": 6.0, "ec": 1.4, "nivel_agua": 100.0, "dia_cultivo": 0
        }

        self.minutos_simulados = 0
        self.dias_cultivo = 0

        self.historico_logs = []
        self.historico_tempo = [0]
        self.historico_saude_gem = [100.0]
        
        self.historico_sinc = {
            "ph": {"gem": [6.0], "real": [6.0]},
            "ec": {"gem": [1.4], "real": [1.4]},
            "temp_ar": {"gem": [24.5], "real": [24.5]},
            "temp_agua": {"gem": [22.0], "real": [22.0]},
            "umidade": {"gem": [60.0], "real": [60.0]}
        }
        
        self.tempo_contador = 0

        self.sliders = {}
        self.labels_valores = {}
        self.labels_metas = {}
        self.labels_comparativo = {"real": {}, "gem": {}}
        self.entries_config = {}
        self.botoes_sidebar = {}
        self.botoes_aba_sinc = {}

        self.cultivos_salvos_cache = self.carregar_cultivos_disco()

        self.criar_interface()
        self.atualizar_interface()

        self.after(1000, self.ciclo_interface)

    def carregar_cultivos_disco(self):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cultivos_salvos.json")
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"Alface Experimental #01": {"cultura": "ALFACE", "fase": "VEGETATIVO", "fotoperiodo": 18.0, "hora": 6, "minuto": 0, "ph_min": 5.5, "ph_max": 6.5, "ec_min": 1.0, "ec_max": 1.8, "temp_ar_min": 18.0, "temp_ar_max": 26.0, "temp_agua_min": 18.0, "temp_agua_max": 26.0, "umidade_min": 50.0, "umidade_max": 80.0, "fertilizante": "Flex Azul + Vermelho (A+B)", "taxa_ab": 0.84}}

    def salvar_cultivos_disco(self):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cultivos_salvos.json")
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(self.cultivos_salvos_cache, f, indent=4, ensure_ascii=False)
        except: pass

    # ======================================================
    # ARQUITETURA PRINCIPAL DE INTERFACE
    # ======================================================

    def criar_interface(self):
        self.sidebar = ctk.CTkFrame(self, width=290, fg_color="#060913", corner_radius=0, border_width=1, border_color="#111827")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        topo_sidebar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        topo_sidebar.pack(fill="x", padx=20, pady=24)

        ctk.CTkLabel(topo_sidebar, text="HORTA DO FUTURO", font=("Segoe UI", 18, "bold"), text_color="#F8FAFC").pack(anchor="w")
        ctk.CTkLabel(topo_sidebar, text="DIGITAL TWIN V1.0", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", pady=(2, 0))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=10)

        itens_menu = [
            ("dashboard", "📊  Painel & Controles"),
            ("comparativo", "⚖️  Comparativo de Sincronia"),
            ("nutricao", "🌱  Receitas & Cultivo"),
            ("graficos", "📈  Gráficos & Logs"),
            ("config", "⚙️  Configurações ESP32")
        ]

        for chave, texto in itens_menu:
            btn = ctk.CTkButton(
                nav_frame, text=texto, anchor="w", height=46,
                fg_color="transparent", text_color="#94A3B8",
                hover_color="#0F172A", font=("Segoe UI", 13, "bold"),
                command=lambda c=chave: self.trocar_tela(c)
            )
            btn.pack(fill="x", pady=4)
            self.botoes_sidebar[chave] = btn

        sim_box = ctk.CTkFrame(self.sidebar, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        sim_box.pack(side="bottom", fill="x", padx=14, pady=14)

        self.label_titulo_sim_sidebar = ctk.CTkLabel(sim_box, text="CONTROLE DO SIMULADOR", font=("Segoe UI", 12, "bold"), text_color="#F59E0B")
        self.label_titulo_sim_sidebar.pack(pady=(12, 4))
        
        relogio_box = ctk.CTkFrame(sim_box, fg_color="#030508", corner_radius=6, border_width=1, border_color="#1E293B")
        relogio_box.pack(fill="x", padx=14, pady=(0, 8))
        self.label_relogio_topo = ctk.CTkLabel(relogio_box, text=datetime.now().strftime("%H:%M  %d/%m/%Y"), font=("Segoe UI", 13, "bold"), text_color="#F59E0B")
        self.label_relogio_topo.pack(pady=6)

        vel_box = ctk.CTkFrame(sim_box, fg_color="transparent")
        vel_box.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(vel_box, text="Velocidade:", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_vel_sidebar = ctk.CTkLabel(vel_box, text="1x", font=("Segoe UI", 13, "bold"), text_color="#F59E0B")
        self.label_vel_sidebar.pack(side="right")

        self.slider_vel_sidebar = ctk.CTkSlider(
            sim_box, from_=1, to=10, number_of_steps=9, command=self.mudar_velocidade,
            progress_color="#F59E0B", button_color="#F8FAFC", button_hover_color="#E2E8F0", fg_color="#030508", height=14
        )
        self.slider_vel_sidebar.pack(fill="x", padx=14, pady=6)
        self.slider_vel_sidebar.set(1)

        botoes_tempo_frame = ctk.CTkFrame(sim_box, fg_color="transparent")
        botoes_tempo_frame.pack(fill="x", padx=12, pady=4)

        for texto, minutos in [("+1h", 60), ("+1d", 1440)]:
            ctk.CTkButton(
                botoes_tempo_frame, text=texto, command=lambda m=minutos: self.avancar_tempo(m), height=30, width=60,
                fg_color="#0F172A", hover_color="#1E293B", text_color="#F8FAFC", font=("Segoe UI", 13, "bold"), corner_radius=6
            ).pack(side="left", expand=True, padx=3)

        self.btn_pausa_tempo = ctk.CTkButton(
            sim_box, text="▶ INICIAR SIMULADOR", command=self.alternar_demonstracao, height=36,
            fg_color="#F59E0B", hover_color="#D97706", text_color="#030508", font=("Segoe UI", 13, "bold")
        )
        self.btn_pausa_tempo.pack(fill="x", padx=14, pady=(8, 6))

        self.btn_reset = ctk.CTkButton(
            sim_box, text="↺ RESETAR CULTIVO", command=self.resetar_planta, height=32,
            fg_color="#1E293B", hover_color="#334155", text_color="#F8FAFC", font=("Segoe UI", 13, "bold")
        )
        self.btn_reset.pack(fill="x", padx=14, pady=(0, 12))

        self.main_container = ctk.CTkFrame(self, fg_color="#030508", corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        self.header = ctk.CTkFrame(self.main_container, height=65, fg_color="#060913", corner_radius=0, border_width=1, border_color="#111827")
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        header_content = ctk.CTkFrame(self.header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24)

        status_box = ctk.CTkFrame(header_content, fg_color="transparent")
        status_box.pack(side="left", fill="y", expand=True)
        
        self.label_status_esp = ctk.CTkLabel(status_box, text="● SIMULADOR MANUAL", font=("Segoe UI", 13, "bold"), text_color="#F59E0B")
        self.label_status_esp.pack(side="left")

        self.switch_hardware_topo = ctk.CTkSwitch(
            status_box, text="Modo ESP32", command=lambda: self.sincronizar_chaves("topo"),
            font=("Segoe UI", 13, "bold"), text_color="#94A3B8", progress_color="#38BDF8"
        )
        self.switch_hardware_topo.pack(side="right", padx=(20, 0))
        self.switch_hardware_topo.deselect()

        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=24, pady=24)

        self.telas = {
            "dashboard": self.criar_tela_dashboard(),
            "comparativo": self.criar_tela_comparativo(),
            "nutricao": self.criar_tela_nutricao(),
            "graficos": self.criar_tela_graficos(),
            "config": self.criar_tela_configuracao()
        }
        self.trocar_tela("dashboard")

    def trocar_tela(self, nome):
        for tela in self.telas.values():
            tela.pack_forget()
        self.telas[nome].pack(fill="both", expand=True)

        for chave, btn in self.botoes_sidebar.items():
            current_color = "#38BDF8" if self.modo_hardware_real else "#F59E0B"
            btn.configure(fg_color="#0F172A" if chave == nome else "transparent", text_color=current_color if chave == nome else "#94A3B8")

    # ======================================================
    # TELA 1: DASHBOARD
    # ======================================================

    def criar_tela_dashboard(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")

        titulo_box = ctk.CTkFrame(frame, fg_color="transparent")
        titulo_box.pack(fill="x", pady=(0, 12))
        self.label_titulo_painel = ctk.CTkLabel(titulo_box, text="Painel Geral • Gêmeo Digital", font=("Segoe UI", 24, "bold"), text_color="#F8FAFC")
        self.label_titulo_painel.pack(anchor="w")
        
        self.label_sub_cultivo = ctk.CTkLabel(titulo_box, text="ALFACE EXPERIMENTAL #01 • Fase: VEGETATIVO • Dia: 0 (Simulador)", font=("Segoe UI", 14, "bold"), text_color="#94A3B8")
        self.label_sub_cultivo.pack(anchor="w", pady=(2, 0))

        grid_principal = ctk.CTkFrame(frame, fg_color="transparent")
        grid_principal.pack(fill="both", expand=True, pady=(0, 10))
        grid_principal.grid_columnconfigure(0, weight=6, uniform="dash")
        grid_principal.grid_columnconfigure(1, weight=5, uniform="dash")
        grid_principal.grid_rowconfigure(0, weight=1)

        col_esq = ctk.CTkFrame(grid_principal, fg_color="transparent")
        col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        col_esq.grid_columnconfigure(0, weight=1)

        c1 = ctk.CTkFrame(col_esq, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        c1.pack(fill="x", pady=4)
        ctk.CTkLabel(c1, text="ÍNDICE DE SAÚDE BIOLÓGICA", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(14, 2))
        
        box_status = ctk.CTkFrame(c1, fg_color="transparent")
        box_status.pack(fill="x", padx=18, pady=2)
        self.label_saude_circulo = ctk.CTkLabel(box_status, text="100%", font=("Segoe UI", 36, "bold"), text_color="#10B981")
        self.label_saude_circulo.pack(side="left")
        
        self.label_saude_status_texto = ctk.CTkLabel(c1, text="✅ Condições ideais para o desenvolvimento", font=("Segoe UI", 13, "bold"), text_color="#10B981", wraplength=440, justify="left")
        self.label_saude_status_texto.pack(anchor="w", padx=18, pady=(2, 14))

        c2 = ctk.CTkFrame(col_esq, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        c2.pack(fill="x", pady=4)
        ctk.CTkLabel(c2, text="ATMOSFERA E CLIMA", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(14, 4))

        l_ar1 = ctk.CTkFrame(c2, fg_color="transparent")
        l_ar1.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(l_ar1, text="Temperatura do Ar", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_temp = ctk.CTkLabel(l_ar1, text="24.5 °C", font=("Segoe UI", 16, "bold"), text_color="#EF4444")
        self.label_dash_temp.pack(side="right")

        l_ar2 = ctk.CTkFrame(c2, fg_color="transparent")
        l_ar2.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(l_ar2, text="Umidade Relativa", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_umid = ctk.CTkLabel(l_ar2, text="62.0 %", font=("Segoe UI", 16, "bold"), text_color="#38BDF8")
        self.label_dash_umid.pack(side="right")
        
        l_ar3 = ctk.CTkFrame(c2, fg_color="transparent")
        l_ar3.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(l_ar3, text="Exaustor / Ventilador", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_fan = ctk.CTkLabel(l_ar3, text="OFF", font=("Segoe UI", 14, "bold"), text_color="#94A3B8")
        self.label_dash_fan.pack(side="right")

        l_ar4 = ctk.CTkFrame(c2, fg_color="transparent")
        l_ar4.pack(fill="x", padx=18, pady=(3, 12))
        ctk.CTkLabel(l_ar4, text="Iluminação", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_luz = ctk.CTkLabel(l_ar4, text="ON (Ativa)", font=("Segoe UI", 14, "bold"), text_color="#F59E0B")
        self.label_dash_luz.pack(side="right")

        c3 = ctk.CTkFrame(col_esq, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        c3.pack(fill="x", pady=4)
        ctk.CTkLabel(c3, text="SOLUÇÃO HIDROPÔNICA & RESERVATÓRIO", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(14, 4))
        
        l_dwc_temp = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc_temp.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(l_dwc_temp, text="Temp. da Água", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_temp_agua = ctk.CTkLabel(l_dwc_temp, text="22.0 °C", font=("Segoe UI", 16, "bold"), text_color="#2DD4BF")
        self.label_dash_temp_agua.pack(side="right")

        l_dwc1 = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc1.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(l_dwc1, text="pH da Solução", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_ph = ctk.CTkLabel(l_dwc1, text="6.10", font=("Segoe UI", 16, "bold"), text_color="#38BDF8")
        self.label_dash_ph.pack(side="right")

        l_dwc2 = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc2.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(l_dwc2, text="Condutividade (EC)", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_ec = ctk.CTkLabel(l_dwc2, text="1.4 mS/cm", font=("Segoe UI", 16, "bold"), text_color="#FB923C")
        self.label_dash_ec.pack(side="right")

        l_dwc3 = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc3.pack(fill="x", padx=18, pady=(3, 12))
        ctk.CTkLabel(l_dwc3, text="Nível do Reservatório", font=("Segoe UI", 14), text_color="#CBD5E1").pack(side="left")
        self.label_dash_nivel = ctk.CTkLabel(l_dwc3, text="OK (100%)", font=("Segoe UI", 14, "bold"), text_color="#10B981")
        self.label_dash_nivel.pack(side="right")

        col_dir = ctk.CTkFrame(grid_principal, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ctk.CTkLabel(col_dir, text="SIMULADOR DE SENSORES (MANUAL)", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(anchor="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(col_dir, text="Desative o ESP32 acima para mover os seletores:", font=("Segoe UI", 12), text_color="#94A3B8").pack(anchor="w", padx=16, pady=(0, 6))

        sim_scroll_frame = ctk.CTkFrame(col_dir, fg_color="transparent")
        sim_scroll_frame.pack(fill="both", expand=True, padx=12, pady=4)

        self.criar_controle(sim_scroll_frame, "Temperatura do ar", 10, 40, self.horta.temperatura_ar, self.mudar_temperatura_ar, "°C")
        self.criar_controle(sim_scroll_frame, "Umidade do ar", 0, 100, self.horta.umidade_ar, self.mudar_umidade_ar, "%")
        self.criar_controle(sim_scroll_frame, "Temperatura da água", 5, 40, self.horta.temperatura_agua, self.mudar_temperatura_agua, "°C")
        self.criar_controle(sim_scroll_frame, "pH", 2, 12, self.horta.ph, self.mudar_ph, "")
        self.criar_controle(sim_scroll_frame, "EC", 0, 3, self.horta.ec, self.mudar_ec, "mS/cm")
        self.criar_controle(sim_scroll_frame, "Nível da água", 0, 100, self.horta.nivel_agua, self.mudar_nivel_agua, "%")

        return frame

    # ======================================================
    # TELA 2: COMPARATIVO
    # ======================================================

    def criar_tela_comparativo(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        titulo_box = ctk.CTkFrame(frame, fg_color="transparent")
        titulo_box.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(titulo_box, text="Diagnóstico de Sincronia • ESP32 vs. Gêmeo Digital", font=("Segoe UI", 24, "bold"), text_color="#F8FAFC").pack(anchor="w")
        ctk.CTkLabel(titulo_box, text="Validação da precisão preditiva do modelo frente às leituras físicas do hardware.", font=("Segoe UI", 13), text_color="#94A3B8").pack(anchor="w", pady=(2, 0))

        graf_box = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        graf_box.pack(fill="x", pady=(0, 12))

        header_graf = ctk.CTkFrame(graf_box, fg_color="transparent")
        header_graf.pack(fill="x", padx=16, pady=(10, 4))
        ctk.CTkLabel(header_graf, text="CURVAS TEMPORAIS DE SINCRONIA", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(side="left")
        
        abas_frame = ctk.CTkFrame(header_graf, fg_color="transparent")
        abas_frame.pack(side="right")

        botoes_param = [("pH", "ph"), ("EC", "ec"), ("Temp. Ar", "temp_ar"), ("Temp. Água", "temp_agua"), ("Umidade", "umidade")]
        
        for text, key in botoes_param:
            btn = ctk.CTkButton(
                abas_frame, text=text, width=80, height=28,
                fg_color="#0F172A" if key != self.parametro_sincronia_ativo else "#1E293B",
                text_color="#94A3B8" if key != self.parametro_sincronia_ativo else "#F59E0B",
                font=("Segoe UI", 11, "bold"), corner_radius=6, command=lambda k=key: self.alternar_aba_sincronia(k)
            )
            btn.pack(side="left", padx=2)
            self.botoes_aba_sinc[key] = btn

        self.fig_sinc = Figure(figsize=(10, 1.8), dpi=100)
        self.fig_sinc.patch.set_facecolor('#0A0F1D')
        self.ax_sinc = self.fig_sinc.add_subplot(111)
        self.configurar_estilo_eixo(self.ax_sinc, "pH", 4, 9)
        self.canvas_sinc = FigureCanvasTkAgg(self.fig_sinc, master=graf_box)
        self.canvas_sinc.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=6)

        grid_comp = ctk.CTkFrame(frame, fg_color="transparent")
        grid_comp.pack(fill="both", expand=True)
        grid_comp.grid_columnconfigure((0, 1), weight=1, uniform="comp")
        grid_comp.grid_rowconfigure(0, weight=1)

        col_real = ctk.CTkFrame(grid_comp, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        col_real.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(col_real, text="📡 HARDWARE REAL (ESP32)", font=("Segoe UI", 13, "bold"), text_color="#38BDF8").pack(anchor="w", padx=16, pady=(12, 8))

        col_gem = ctk.CTkFrame(grid_comp, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        col_gem.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(col_gem, text="🔮 GÊMEO DIGITAL (PREDITIVO)", font=("Segoe UI", 13, "bold"), text_color="#F59E0B").pack(anchor="w", padx=16, pady=(12, 8))

        parametros = [
            ("Índice de Saúde Biológica", "saude", "%"), ("Temperatura do Ar", "temp_ar", "°C"),
            ("Umidade Relativa", "umidade", "%"), ("Temperatura da Água", "temp_agua", "°C"),
            ("pH da Solução", "ph", ""), ("Condutividade Elétrica (EC)", "ec", "mS/cm"),
            ("Nível do Reservatório", "nivel", "%")
        ]

        for nome, chave, unidade in parametros:
            f_r = ctk.CTkFrame(col_real, fg_color="#030508", corner_radius=6, height=36)
            f_r.pack(fill="x", padx=12, pady=3)
            f_r.pack_propagate(False)
            ctk.CTkLabel(f_r, text=nome, font=("Segoe UI", 12), text_color="#CBD5E1").pack(side="left", padx=10)
            lbl_r = ctk.CTkLabel(f_r, text="--", font=("Segoe UI", 13, "bold"), text_color="#38BDF8")
            lbl_r.pack(side="right", padx=10)
            self.labels_comparativo["real"][chave] = lbl_r

            f_g = ctk.CTkFrame(col_gem, fg_color="#030508", corner_radius=6, height=36)
            f_g.pack(fill="x", padx=12, pady=3)
            f_g.pack_propagate(False)
            ctk.CTkLabel(f_g, text=nome, font=("Segoe UI", 12), text_color="#CBD5E1").pack(side="left", padx=10)
            lbl_g = ctk.CTkLabel(f_g, text="--", font=("Segoe UI", 13, "bold"), text_color="#F59E0B")
            lbl_g.pack(side="right", padx=10)
            self.labels_comparativo["gem"][chave] = lbl_g

        return frame

    def alternar_aba_sincronia(self, chave):
        self.parametro_sincronia_ativo = chave
        for k, btn in self.botoes_aba_sinc.items():
            btn.configure(fg_color="#1E293B" if k == chave else "#0F172A", text_color="#F59E0B" if k == chave else "#94A3B8")
        self.atualizar_interface()

    # ======================================================
    # TELA 3: RECEITAS & CULTIVO (Com preenchimento orgânico inteligente)
    # ======================================================

    def criar_tela_nutricao(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="nut")
        frame.grid_rowconfigure(0, weight=1)

        col1 = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(col1, text="CADASTRO DE CULTIVO & LOTES", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(18, 10), anchor="w", padx=18)
        
        ctk.CTkLabel(col1, text="Lotes Salvos (Revisitar)", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(anchor="w", padx=18)
        self.combo_lotes_salvos = ctk.CTkComboBox(col1, values=list(self.cultivos_salvos_cache.keys()), command=self.carregar_lote_salvo, fg_color="#030508", border_color="#1E293B", button_color="#1E293B", height=36, font=("Segoe UI", 13, "bold"))
        self.combo_lotes_salvos.pack(fill="x", padx=18, pady=(4, 12))

        ctk.CTkLabel(col1, text="Cultura Agronômica", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(anchor="w", padx=18)
        self.combo_cultura = ctk.CTkComboBox(col1, values=listar_culturas(), command=self.carregar_cultura, fg_color="#030508", border_color="#1E293B", button_color="#1E293B", height=36, font=("Segoe UI", 13, "bold"))
        self.combo_cultura.pack(fill="x", padx=18, pady=(4, 12))

        ctk.CTkLabel(col1, text="Identificação do Lote / Cultivo", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(anchor="w", padx=18)
        self.entry_nome_cultivo = ctk.CTkEntry(col1, fg_color="#030508", border_color="#1E293B", height=36, font=("Segoe UI", 13, "bold"))
        self.entry_nome_cultivo.pack(fill="x", padx=18, pady=(4, 14))

        ctk.CTkLabel(col1, text="FASE FENOLÓGICA (Com Confirmação)", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(6, 4))
        # CORREÇÃO CRÍTICA: Os values agora usam exatamente as chaves do dicionário do seu modelo de dados ("MUDA", "VEGETATIVO", "FLORACAO")
        self.combo_fase_cadastro = ctk.CTkComboBox(col1, values=["MUDA", "VEGETATIVO", "FLORACAO"], command=self.pedir_confirmacao_mudanca_fase, fg_color="#030508", border_color="#1E293B", button_color="#1E293B", height=36, font=("Segoe UI", 13, "bold"))
        self.combo_fase_cadastro.pack(fill="x", padx=18, pady=(0, 14))

        col2 = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        col2.grid(row=0, column=1, sticky="nsew", padx=8)
        ctk.CTkLabel(col2, text="FOTOPERÍODO & TEMPORIZAÇÃO", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(18, 10), anchor="w", padx=18)

        f_p1 = ctk.CTkFrame(col2, fg_color="transparent")
        f_p1.pack(fill="x", padx=18, pady=(10, 0))
        ctk.CTkLabel(f_p1, text="Horas de luz / dia", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(side="left")
        self.entry_fotoperiodo = ctk.CTkEntry(f_p1, width=80, fg_color="#030508", border_color="#1E293B", height=34, font=("Segoe UI", 13, "bold"))
        self.entry_fotoperiodo.pack(side="right")
        self.entry_fotoperiodo.bind("<KeyRelease>", self.atualizar_label_escuridao)

        f_escuridao = ctk.CTkFrame(col2, fg_color="transparent")
        f_escuridao.pack(fill="x", padx=18, pady=(2, 10))
        self.label_escuridao = ctk.CTkLabel(f_escuridao, text="Escuridão: --h", text_color="#94A3B8", font=("Segoe UI", 12, "italic"))
        self.label_escuridao.pack(side="right")

        f_p2 = ctk.CTkFrame(col2, fg_color="transparent")
        f_p2.pack(fill="x", padx=18, pady=10)
        ctk.CTkLabel(f_p2, text="Início da luz (HH:MM)", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(side="left")
        self.entry_inicio_minuto = ctk.CTkEntry(f_p2, width=48, fg_color="#030508", border_color="#1E293B", height=34, font=("Segoe UI", 13, "bold"))
        self.entry_inicio_minuto.pack(side="right")
        ctk.CTkLabel(f_p2, text=":", text_color="#CBD5E1").pack(side="right", padx=2)
        self.entry_inicio_hora = ctk.CTkEntry(f_p2, width=48, fg_color="#030508", border_color="#1E293B", height=34, font=("Segoe UI", 13, "bold"))
        self.entry_inicio_hora.pack(side="right")

        col3 = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        col3.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(col3, text="CONDIÇÕES IDEAIS & RECEITA", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(18, 8), anchor="w", padx=18)

        for tit, c_min, c_max in [("pH (Mín / Máx)", "ph_min", "ph_max"), ("EC (Mín / Máx)", "ec_min", "ec_max"), ("Temp. Ar (°C)", "temperatura_ar_min", "temperatura_ar_max"), ("Temp. Água (°C)", "temperatura_agua_min", "temperatura_agua_max"), ("Umidade (%)", "umidade_ar_min", "umidade_ar_max")]:
            self.criar_campo_min_max(col3, tit, c_min, c_max)

        nut_box = ctk.CTkFrame(col3, fg_color="#030508", corner_radius=8, border_width=1, border_color="#1E293B")
        nut_box.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(nut_box, text="FERTILIZANTE COMERCIAL", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(pady=(8, 6), anchor="w", padx=12)
        
        f_prod = ctk.CTkFrame(nut_box, fg_color="transparent")
        f_prod.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(f_prod, text="Produto:", text_color="#CBD5E1", font=("Segoe UI", 13)).pack(side="left")
        self.entry_nome_fertilizante = ctk.CTkEntry(f_prod, width=220, fg_color="#0A0F1D", border_color="#1E293B", height=30, font=("Segoe UI", 13, "bold"))
        self.entry_nome_fertilizante.pack(side="right")

        self.entry_taxa_ab = self.criar_campo_nutricao(nut_box, "g/L por +1.0 EC:")

        botoes_acao_receita = ctk.CTkFrame(col3, fg_color="transparent")
        botoes_acao_receita.pack(fill="x", padx=18, pady=(12, 16))
        ctk.CTkButton(botoes_acao_receita, text="💾 SALVAR LOTE", command=self.salvar_receita_local, height=38, fg_color="#0F172A", hover_color="#1E293B", text_color="#F8FAFC", font=("Segoe UI", 13, "bold")).pack(side="left", expand=True, padx=(0, 4))
        ctk.CTkButton(botoes_acao_receita, text="⚡ SINCRONIZAR ESP32", command=self.sincronizar_receita_esp32, height=38, fg_color="#38BDF8", hover_color="#0284C7", text_color="#030508", font=("Segoe UI", 13, "bold")).pack(side="left", expand=True, padx=(4, 0))

        self.preencher_configuracao()
        return frame
        
    def atualizar_label_escuridao(self, event=None):
        try:
            texto = self.entry_fotoperiodo.get().replace(",", ".")
            if texto:
                luz = float(texto)
                if 0 <= luz <= 24:
                    escuro = 24.0 - luz
                    self.label_escuridao.configure(text=f"Escuridão: {escuro:.1f}h")
                else:
                    self.label_escuridao.configure(text="Escuridão: Inválido (0-24)")
            else:
                self.label_escuridao.configure(text="Escuridão: --h")
        except ValueError:
            self.label_escuridao.configure(text="Escuridão: Erro numérico")

    def pedir_confirmacao_mudanca_fase(self, nova_fase):
        fase_anterior = getattr(self.horta.config, 'fase', 'VEGETATIVO')
        
        if nova_fase == fase_anterior: 
            return

        self.combo_fase_cadastro.set(fase_anterior)

        top = ctk.CTkToplevel(self)
        top.title("Confirmação de Mudança de Fase")
        top.geometry("420x210")
        top.attributes("-topmost", True)
        top.configure(fg_color="#0A0F1D")
        top.grab_set()

        texto_fase_bonito = "FLORAÇÃO / FRUTIFICAÇÃO" if nova_fase == "FLORACAO" else nova_fase
        texto_ant_bonito = "FLORAÇÃO / FRUTIFICAÇÃO" if fase_anterior == "FLORACAO" else fase_anterior

        ctk.CTkLabel(top, text="⚠️ CONFIRMAR MUDANÇA DE FASE", font=("Segoe UI", 15, "bold"), text_color="#F59E0B").pack(pady=(20, 10))
        ctk.CTkLabel(top, text=f"Deseja alterar a fase de cultivo de\n'{texto_ant_bonito}' para '{texto_fase_bonito}'?\n(A receita agronômica será preenchida automaticamente)", font=("Segoe UI", 13), text_color="#CBD5E1", justify="center").pack(pady=(0, 16))

        f_btns = ctk.CTkFrame(top, fg_color="transparent")
        f_btns.pack(fill="x", padx=30)

        def confirmar():
            # 1. Altera a fase no cérebro do modelo
            self.horta.config.fase = nova_fase
            self.combo_fase_cadastro.set(nova_fase) 
            
            # 2. Define inteligentemente o fotoperíodo padrão
            if nova_fase == "FLORACAO":
                self.horta.config.fotoperiodo_horas = 12.0
                self.atualizar_log_serial("[INFO] Fase ajustada para FLORAÇÃO. Padrão de 12h carregado.\n")
            elif nova_fase == "MUDA":
                self.horta.config.fotoperiodo_horas = 18.0
                self.atualizar_log_serial("[INFO] Fase ajustada para MUDA. Receita delicada carregada.\n")
            else:
                self.horta.config.fotoperiodo_horas = 18.0
                self.atualizar_log_serial(f"[INFO] Fase ajustada para {nova_fase}.\n")

            # 3. MÁGICA: Preenche as caixinhas da tela automaticamente com os dados do modelo de plantas!
            self.preencher_configuracao()
            
            self.atualizar_label_escuridao()
            self.horta.diagnosticar()
            self.atualizar_interface()
            top.destroy()

        def cancelar():
            top.destroy()

        ctk.CTkButton(f_btns, text="CONFIRMAR", command=confirmar, fg_color="#10B981", hover_color="#059669", text_color="#FFFFFF", height=34, font=("Segoe UI", 12, "bold")).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(f_btns, text="CANCELAR", command=cancelar, fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF", height=34, font=("Segoe UI", 12, "bold")).pack(side="right", expand=True, padx=5)

    def carregar_lote_salvo(self, nome_lote):
        if nome_lote in self.cultivos_salvos_cache:
            dados = self.cultivos_salvos_cache[nome_lote]
            cfg = self.horta.config
            cfg.nome_cultivo = nome_lote
            # Evitar carregar com string antiga bugada se existir no cache
            fase_banco = dados.get("fase", "VEGETATIVO")
            if "FLORA" in fase_banco: fase_banco = "FLORACAO"
            cfg.fase = fase_banco
            
            cfg.fotoperiodo_horas = dados.get("fotoperiodo", 18.0)
            cfg.inicio_luz_hora = dados.get("hora", 6)
            cfg.inicio_luz_minuto = dados.get("minuto", 0)
            cfg.ph_min = dados.get("ph_min", 5.5)
            cfg.ph_max = dados.get("ph_max", 6.5)
            cfg.ec_min = dados.get("ec_min", 1.0)
            cfg.ec_max = dados.get("ec_max", 1.8)
            cfg.temperatura_ar_min = dados.get("temp_ar_min", 18.0)
            cfg.temperatura_ar_max = dados.get("temp_ar_max", 26.0)
            cfg.temperatura_agua_min = dados.get("temp_agua_min", 18.0)
            cfg.temperatura_agua_max = dados.get("temp_agua_max", 26.0)
            cfg.umidade_ar_min = dados.get("umidade_min", 50.0)
            cfg.umidade_ar_max = dados.get("umidade_max", 80.0)
            
            self.horta.nome_fertilizante = dados.get("fertilizante", "Flex Azul + Vermelho")
            self.horta.gramas_por_litro_recomendado = dados.get("taxa_ab", 0.84)

            self.preencher_configuracao()
            self.atualizar_interface()
            self.atualizar_log_serial(f"[INFO] Lote '{nome_lote}' carregado com sucesso!\n")

    # ======================================================
    # TELA 4: GRÁFICOS & LOGS
    # ======================================================

    def criar_tela_graficos(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="g")
        frame.grid_rowconfigure((0, 1), weight=1)

        g1_frame = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        g1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        ctk.CTkLabel(g1_frame, text="EVOLUÇÃO DA SAÚDE BIOLÓGICA (%)", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(12, 0))
        self.fig1 = Figure(figsize=(5, 2.4), dpi=100)
        self.fig1.patch.set_facecolor('#0A0F1D')
        self.ax1 = self.fig1.add_subplot(111)
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=g1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        g2_frame = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        g2_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        ctk.CTkLabel(g2_frame, text="DINÂMICA DE NUTRIÇÃO (pH & EC)", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(12, 0))
        self.fig2 = Figure(figsize=(5, 2.4), dpi=100)
        self.fig2.patch.set_facecolor('#0A0F1D')
        self.ax2 = self.fig2.add_subplot(111)
        self.configurar_estilo_eixo(self.ax2, "pH / EC", 0, 14)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=g2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        g3_frame = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        g3_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        g3_topo = ctk.CTkFrame(g3_frame, fg_color="transparent")
        g3_topo.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(g3_topo, text="MONITORAMENTO TÉRMICO COMPARATIVO (AR vs ÁGUA)", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(side="left")
        ctk.CTkButton(g3_topo, text="📥 EXPORTAR LOGS (CSV)", command=self.exportar_logs_csv, height=34, width=190, fg_color="#0F172A", hover_color="#1E293B", text_color="#F8FAFC", font=("Segoe UI", 13, "bold")).pack(side="right")
        self.fig3 = Figure(figsize=(10, 2.0), dpi=100)
        self.fig3.patch.set_facecolor('#0A0F1D')
        self.ax3 = self.fig3.add_subplot(111)
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=g3_frame)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        return frame

    # ======================================================
    # TELA 5: CONFIGURAÇÕES
    # ======================================================

    def criar_tela_configuracao(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="conf")
        frame.grid_rowconfigure(0, weight=1)
        
        c_hw = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        c_hw.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(c_hw, text="GERENCIAMENTO DE HARDWARE", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(18, 14), anchor="w", padx=18)
        self.switch_hardware_cfg = ctk.CTkSwitch(c_hw, text=" Ativar Comunicação com ESP32 (USB)", command=lambda: self.sincronizar_chaves("config"), font=("Segoe UI", 14, "bold"), text_color="#F8FAFC", progress_color="#38BDF8")
        self.switch_hardware_cfg.pack(anchor="w", padx=18, pady=10)
        self.switch_hardware_cfg.deselect()
        ctk.CTkLabel(c_hw, text="Quando ativado, busca porta serial real do ESP32 (Azul). Quando desativado, o simulador assume o gêmeo digital (Laranja).", font=("Segoe UI", 13), text_color="#94A3B8", wraplength=440, justify="left").pack(anchor="w", padx=18, pady=10)

        c_ser = ctk.CTkFrame(frame, fg_color="#0A0F1D", corner_radius=12, border_width=1, border_color="#1E293B")
        c_ser.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(c_ser, text="MONITOR DE COMUNICAÇÃO SERIAL (MATRIX)", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(18, 10), anchor="w", padx=18)
        self.serial_box_text = ctk.CTkTextbox(c_ser, fg_color="#000000", text_color="#00FF66", font=("Consolas", 14), corner_radius=8, border_width=1, border_color="#003311")
        self.serial_box_text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.serial_box_text.insert("0.0", "[INFO] Sistema inicializado. Modo Gêmeo Digital / Simulador ativo.\n")
        self.serial_box_text.configure(state="disabled")

        return frame

    # ======================================================
    # LÓGICA DE INTEGRAÇÃO & MÉTODOS SUPORTE
    # ======================================================

    def configurar_estilo_eixo(self, ax, ylabel, ymin, ymax):
        ax.set_facecolor('#0A0F1D')
        ax.tick_params(colors='#94A3B8', labelsize=10)
        ax.spines['bottom'].set_color('#1E293B')
        ax.spines['left'].set_color('#1E293B')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylabel(ylabel, color="#94A3B8", fontsize=10)
        ax.set_ylim(ymin, ymax)

    def criar_campo_min_max(self, parent, titulo, chave_min, chave_max):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=5)
        ctk.CTkLabel(linha, text=titulo, anchor="w", font=("Segoe UI", 13), text_color="#CBD5E1").pack(side="left")
        
        f_vals = ctk.CTkFrame(linha, fg_color="transparent")
        f_vals.pack(side="right")
        e_min = ctk.CTkEntry(f_vals, width=65, fg_color="#030508", border_color="#1E293B", height=32, font=("Segoe UI", 13, "bold"))
        e_min.pack(side="left", padx=(0, 4))
        self.entries_config[chave_min] = e_min
        ctk.CTkLabel(f_vals, text="-", text_color="#94A3B8", font=("Segoe UI", 13, "bold")).pack(side="left", padx=2)
        e_max = ctk.CTkEntry(f_vals, width=65, fg_color="#030508", border_color="#1E293B", height=32, font=("Segoe UI", 13, "bold"))
        e_max.pack(side="left", padx=(4, 0))
        self.entries_config[chave_max] = e_max

    def criar_campo_nutricao(self, parent, titulo):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(linha, text=titulo, anchor="w", font=("Segoe UI", 13), text_color="#CBD5E1").pack(side="left")
        entry = ctk.CTkEntry(linha, width=70, fg_color="#0A0F1D", border_color="#1E293B", height=30, font=("Segoe UI", 13, "bold"))
        entry.pack(side="right")
        return entry

    def criar_controle(self, parent, nome, minimo, maximo, valor, callback, unidade):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=12, pady=3)

        linha = ctk.CTkFrame(frame, fg_color="transparent")
        linha.pack(fill="x", padx=0, pady=0)

        ctk.CTkLabel(linha, text=nome, font=("Segoe UI", 12, "bold"), text_color="#F8FAFC").pack(side="left")
        cor_valor = "#38BDF8" if self.modo_hardware_real else "#F59E0B"
        label = ctk.CTkLabel(linha, text=f"{valor:.1f} {unidade}", font=("Segoe UI", 12, "bold"), text_color=cor_valor)
        label.pack(side="right")
        self.labels_valores[nome] = label

        linha_meta = ctk.CTkFrame(frame, fg_color="transparent")
        linha_meta.pack(fill="x", padx=0, pady=0)
        lbl_meta = ctk.CTkLabel(linha_meta, text="Meta: --", font=("Segoe UI", 10), text_color="#64748B")
        lbl_meta.pack(side="left")
        self.labels_metas[nome] = lbl_meta

        cor_progresso = "#38BDF8" if self.modo_hardware_real else "#F59E0B"
        slider = ctk.CTkSlider(
            frame, from_=minimo, to=maximo, number_of_steps=100, height=12,
            progress_color=cor_progresso, button_color="#F8FAFC", button_hover_color="#E2E8F0", fg_color="#1E293B"
        )
        slider.pack(fill="x", padx=0, pady=(1, 1))
        slider.set(valor)

        def mover(valor_slider):
            if not self.modo_hardware_real:
                callback(float(valor_slider))
                label.configure(text=f"{float(valor_slider):.1f} {unidade}")

        slider.configure(command=mover)
        self.sliders[nome] = slider

    def preencher_configuracao(self):
        try:
            config = self.horta.config
            valores = config.snapshot()

            for chave, entry in self.entries_config.items():
                if chave in valores:
                    entry.delete(0, "end")
                    entry.insert(0, str(valores[chave]))

            self.entry_nome_cultivo.delete(0, "end")
            self.entry_nome_cultivo.insert(0, getattr(config, 'nome_cultivo', 'Alface Experimental #01'))
            
            fase = getattr(config, 'fase', 'VEGETATIVO')
            self.combo_fase_cadastro.set(fase)

            self.entry_fotoperiodo.delete(0, "end")
            self.entry_fotoperiodo.insert(0, str(getattr(config, 'fotoperiodo_horas', 18)))
            
            self.entry_inicio_hora.delete(0, "end")
            self.entry_inicio_hora.insert(0, f"{getattr(config, 'inicio_luz_hora', 6):02d}")
            self.entry_inicio_minuto.delete(0, "end")
            self.entry_inicio_minuto.insert(0, f"{getattr(config, 'inicio_luz_minuto', 0):02d}")
            self.entry_nome_fertilizante.delete(0, "end")
            self.entry_nome_fertilizante.insert(0, getattr(self.horta, 'nome_fertilizante', 'Flex Azul + Vermelho (Hidropônico)'))
            self.entry_taxa_ab.delete(0, "end")
            self.entry_taxa_ab.insert(0, str(getattr(self.horta, 'gramas_por_litro_recomendado', 0.84)))
            
            self.atualizar_label_escuridao()
        except Exception as e: pass

    def coletar_dados_formulario(self):
        cfg = self.horta.config
        cfg.nome_cultivo = self.entry_nome_cultivo.get()
        cfg.fase = self.combo_fase_cadastro.get()
        cfg.fotoperiodo_horas = float(self.entry_fotoperiodo.get())
        cfg.inicio_luz_hora = int(self.entry_inicio_hora.get())
        cfg.inicio_luz_minuto = int(self.entry_inicio_minuto.get())

        for chave, entry in self.entries_config.items():
            setattr(cfg, chave, float(entry.get()))

        self.horta.nome_fertilizante = self.entry_nome_fertilizante.get()
        self.horta.gramas_por_litro_recomendado = float(self.entry_taxa_ab.get())
        return cfg

    def salvar_receita_local(self):
        try:
            cfg = self.coletar_dados_formulario()
            nome_lote = cfg.nome_cultivo
            
            self.cultivos_salvos_cache[nome_lote] = {
                "cultura": self.combo_cultura.get(),
                "fase": cfg.fase,
                "fotoperiodo": cfg.fotoperiodo_horas,
                "hora": cfg.inicio_luz_hora,
                "minuto": cfg.inicio_luz_minuto,
                "ph_min": cfg.ph_min, "ph_max": cfg.ph_max,
                "ec_min": cfg.ec_min, "ec_max": cfg.ec_max,
                "temp_ar_min": cfg.temperatura_ar_min, "temp_ar_max": cfg.temperatura_ar_max,
                "temp_agua_min": cfg.temperatura_agua_min, "temp_agua_max": cfg.temperatura_agua_max,
                "umidade_min": cfg.umidade_ar_min, "umidade_max": cfg.umidade_ar_max,
                "fertilizante": self.horta.nome_fertilizante,
                "taxa_ab": self.horta.gramas_por_litro_recomendado
            }
            self.salvar_cultivos_disco()
            self.combo_lotes_salvos.configure(values=list(self.cultivos_salvos_cache.keys()))
            self.combo_lotes_salvos.set(nome_lote)

            self.horta.diagnosticar()
            self.atualizar_interface()
            self.atualizar_log_serial(f"[SUCESSO] Lote '{nome_lote}' salvo e aplicado localmente!\n")
        except Exception as e: self.atualizar_log_serial(f"[ERRO] Falha ao salvar lote: {e}\n")

    def sincronizar_receita_esp32(self):
        try:
            cfg = self.coletar_dados_formulario()
            pacote_json = {
                "cmd": "set_config", "cultura": cfg.nome_cultivo, "fase": cfg.fase,
                "ph_min": cfg.ph_min, "ph_max": cfg.ph_max, "ec_min": cfg.ec_min,
                "ec_max": cfg.ec_max, "temp_ar_max": cfg.temperatura_ar_max,
                "fotoperiodo": cfg.fotoperiodo_horas, "inicio_luz": cfg.inicio_luz_hora
            }
            self.enviar_pacote_serial_raw(pacote_json)
            self.atualizar_log_serial("[SUCESSO] Receita sincronizada com o ESP32 via Serial!\n")
        except Exception as e: pass

    def enviar_pacote_serial_raw(self, dados_dict):
        if self.ser and self.ser.is_open:
            try:
                linha = json.dumps(dados_dict) + "\n"
                self.ser.write(linha.encode('utf-8'))
            except Exception as e: self.atualizar_log_serial(f"[ERRO] Falha ao enviar serial: {e}\n")
        else:
            self.atualizar_log_serial("[AVISO SERIAL] ESP32 não conectado. Comando simulado.\n")

    def carregar_cultura(self, nome):
        try:
            self.horta.selecionar_cultura(nome)
            self.preencher_configuracao()
            self.horta.diagnosticar()
            self.atualizar_interface()
            self.atualizar_log_serial(f"[INFO] Cultura agronômica carregada: {nome}\n")
        except Exception as e: pass

    def sincronizar_chaves(self, origem):
        estado = self.switch_hardware_topo.get() if origem == "topo" else self.switch_hardware_cfg.get()
        if estado:
            self.switch_hardware_topo.select()
            self.switch_hardware_cfg.select()
        else:
            self.switch_hardware_topo.deselect()
            self.switch_hardware_cfg.deselect()
        self.alternar_modo_hardware()

    def alternar_modo_hardware(self):
        self.modo_hardware_real = self.switch_hardware_topo.get() == 1
        estado_slider = "disabled" if self.modo_hardware_real else "normal"
        for s in self.sliders.values(): s.configure(state=estado_slider)
        
        cor_tema = "#38BDF8" if self.modo_hardware_real else "#F59E0B"
        self.label_titulo_sim_sidebar.configure(text_color=cor_tema)
        self.label_vel_sidebar.configure(text_color=cor_tema)
        self.slider_vel_sidebar.configure(progress_color=cor_tema)
        self.switch_hardware_topo.configure(progress_color=cor_tema)
        self.switch_hardware_cfg.configure(progress_color=cor_tema)
        self.label_relogio_topo.configure(text_color=cor_tema)
        
        for s in self.sliders.values(): s.configure(progress_color=cor_tema)
        for chave, btn in self.botoes_sidebar.items():
            if str(btn.cget("fg_color")) != "transparent":
                btn.configure(text_color=cor_tema)

        if self.modo_hardware_real:
            if self.demonstracao_ativa: self.alternar_demonstracao()
            self.label_status_esp.configure(text="● BUSCANDO ESP32...", text_color="#38BDF8")
            self.tentar_conectar_esp_real()
        else:
            self.fechar_conexao_serial()
            self.label_status_esp.configure(text="● SIMULADOR MANUAL", text_color="#F59E0B")
            self.btn_pausa_tempo.configure(fg_color="#F59E0B", hover_color="#D97706")
            if self.ultimo_valor_esp:
                for k, v in [("temperatura_ar", self.horta.alterar_temperatura_ar), ("umidade_ar", self.horta.alterar_umidade_ar), ("temperatura_agua", self.horta.alterar_temperatura_agua), ("ph", self.horta.alterar_ph), ("ec", self.horta.alterar_ec), ("nivel_agua", self.horta.alterar_nivel_agua)]:
                    if k in self.ultimo_valor_esp:
                        v(self.ultimo_valor_esp[k])
                        if k in self.sliders: self.sliders[k].set(self.ultimo_valor_esp[k])
            self.atualizar_log_serial("[MODO SIMULADOR] Fotografia dos dados do ESP carregada. Trabalhando com variáveis simuladas de forma isolada.\n")

    def tentar_conectar_esp_real(self):
        if not SERIAL_DISPONIVEL:
            self.label_status_esp.configure(text="● ERRO: PySerial ausente", text_color="#EF4444")
            return

        def scan_e_conectar():
            porta_encontrada = next((p.device for p in serial.tools.list_ports.comports() if "USB" in p.description.upper() or "UART" in p.description.upper() or "ESP32" in p.description.upper()), None)
            if porta_encontrada and self.modo_hardware_real:
                try:
                    self.ser = serial.Serial(porta_encontrada, 115200, timeout=1)
                    self.serial_thread_ativa = True
                    self.label_status_esp.configure(text=f"● ESP32 ({porta_encontrada})", text_color="#38BDF8")
                    self.atualizar_log_serial(f"[SUCESSO] Conectado ao hardware real na porta {porta_encontrada}\n")
                    
                    while self.serial_thread_ativa and self.ser and self.ser.is_open and self.modo_hardware_real:
                        linha = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if linha:
                            self.atualizar_log_serial(f"{linha}\n")
                            if linha.startswith("{") and linha.endswith("}"):
                                try:
                                    dados_esp = json.loads(linha)
                                    self.ultimo_valor_esp = dados_esp
                                    for k, v in [("temperatura_ar", self.horta.alterar_temperatura_ar), ("umidade_ar", self.horta.alterar_umidade_ar), ("temperatura_agua", self.horta.alterar_temperatura_agua), ("ph", self.horta.alterar_ph), ("ec", self.horta.alterar_ec), ("nivel_agua", self.horta.alterar_nivel_agua)]:
                                        if k in dados_esp: v(dados_esp[k])
                                except: pass
                except Exception as e:
                    self.label_status_esp.configure(text="● ESP32 NÃO ENCONTRADO", text_color="#EF4444")
            else:
                self.label_status_esp.configure(text="● SEM HARDWARE ESP32", text_color="#EF4444")

        threading.Thread(target=scan_e_conectar, daemon=True).start()

    def fechar_conexao_serial(self):
        self.serial_thread_ativa = False
        if self.ser and self.ser.is_open:
            try: self.ser.close()
            except: pass

    def atualizar_log_serial(self, texto):
        self.log_serial_buffer.append(texto)
        if len(self.log_serial_buffer) > 100: self.log_serial_buffer.pop(0)
        try:
            self.serial_box_text.configure(state="normal")
            self.serial_box_text.delete("0.0", "end")
            self.serial_box_text.insert("0.0", "".join(self.log_serial_buffer))
            self.serial_box_text.see("end")
            self.serial_box_text.configure(state="disabled")
        except: pass

    def mudar_temperatura_ar(self, v): self.horta.alterar_temperatura_ar(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_umidade_ar(self, v): self.horta.alterar_umidade_ar(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_temperatura_agua(self, v): self.horta.alterar_temperatura_agua(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_ph(self, v): self.horta.alterar_ph(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_ec(self, v): self.horta.alterar_ec(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_nivel_agua(self, v): self.horta.alterar_nivel_agua(v); self.horta.diagnosticar(); self.atualizar_interface()

    def mudar_velocidade(self, valor):
        v = float(valor)
        self.horta.configurar_velocidade_tempo(v)
        self.label_vel_sidebar.configure(text=f"{v:.0f}x")

    def alternar_demonstracao(self):
        if self.modo_hardware_real and not self.demonstracao_ativa:
            self.atualizar_log_serial("[AVISO] Alterne para o Modo Simulador para executar a simulação.\n")
            return
        self.demonstracao_ativa = not self.demonstracao_ativa
        if self.demonstracao_ativa:
            self.btn_pausa_tempo.configure(text="⏸ PAUSAR SIMULADOR", fg_color="#DC2626", hover_color="#B91C1C", text_color="#F8FAFC")
        else:
            self.btn_pausa_tempo.configure(text="▶ INICIAR SIMULADOR", fg_color="#F59E0B", hover_color="#D97706", text_color="#030508")

    def avancar_tempo(self, m):
        if self.modo_hardware_real: return
        self.minutos_simulados += m
        self.dias_cultivo = self.minutos_simulados // 1440
        self.horta.avancar_tempo(m)
        self.atualizar_interface()

    def resetar_planta(self):
        self.minutos_simulados = 0
        self.dias_cultivo = 0
        self.tempo_contador = 0
        
        self.historico_logs.clear()
        self.historico_tempo.clear()
        self.historico_saude_gem.clear()
        
        for k in self.historico_sinc:
            self.historico_sinc[k]["gem"].clear()
            self.historico_sinc[k]["real"].clear()
        
        for k, v in [("Temperatura do ar", 24.5), ("Umidade do ar", 60.0), ("Temperatura da água", 22.0), ("pH", 6.0), ("EC", 1.4), ("Nível da água", 100.0)]:
            if k in self.sliders: self.sliders[k].set(v)
            if k == "Temperatura do ar": self.horta.alterar_temperatura_ar(v)
            elif k == "Umidade do ar": self.horta.alterar_umidade_ar(v)
            elif k == "Temperatura da água": self.horta.alterar_temperatura_agua(v)
            elif k == "pH": self.horta.alterar_ph(v)
            elif k == "EC": self.horta.alterar_ec(v)
            elif k == "Nível da água": self.horta.alterar_nivel_agua(v)

        for ax, canvas in [(self.ax1, self.canvas1), (self.ax2, self.canvas2), (self.ax3, self.canvas3), (self.ax_sinc, self.canvas_sinc)]:
            ax.clear()
            canvas.draw()
        
        self.atualizar_interface()
        self.atualizar_log_serial("\n[SISTEMA] Cultivo resetado para o Dia 0.\n")

    def exportar_logs_csv(self):
        try:
            pasta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
            os.makedirs(pasta, exist_ok=True)
            caminho = os.path.join(pasta, f"telemetria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            if self.historico_logs:
                with open(caminho, "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=self.historico_logs[0].keys())
                    w.writeheader()
                    w.writerows(self.historico_logs)
            self.atualizar_log_serial(f"[SUCESSO] Logs exportados para {caminho}\n")
        except: pass

    def atualizar_graficos_avancados(self, dados, valores_reais):
        self.tempo_contador += 1
        self.historico_tempo.append(self.tempo_contador)
        self.historico_saude_gem.append(dados["saude"])

        self.historico_sinc["ph"]["gem"].append(dados["ph"])
        self.historico_sinc["ph"]["real"].append(valores_reais["ph"])
        self.historico_sinc["ec"]["gem"].append(dados["ec"])
        self.historico_sinc["ec"]["real"].append(valores_reais["ec"])
        self.historico_sinc["temp_ar"]["gem"].append(dados["temperatura_ar"])
        self.historico_sinc["temp_ar"]["real"].append(valores_reais["temp_ar"])
        self.historico_sinc["temp_agua"]["gem"].append(dados["temperatura_agua"])
        self.historico_sinc["temp_agua"]["real"].append(valores_reais["temp_agua"])
        self.historico_sinc["umidade"]["gem"].append(dados["umidade_ar"])
        self.historico_sinc["umidade"]["real"].append(valores_reais["umidade"])

        self.historico_logs.append({
            "tempo": self.tempo_contador, "saude": dados["saude"],
            "temp_ar": dados["temperatura_ar"], "ph": dados["ph"], "ec": dados["ec"]
        })

        if len(self.historico_tempo) > 30:
            self.historico_tempo.pop(0)
            self.historico_saude_gem.pop(0)
            for k in self.historico_sinc:
                self.historico_sinc[k]["gem"].pop(0)
                self.historico_sinc[k]["real"].pop(0)

        cor_grafico = "#38BDF8" if self.modo_hardware_real else "#F59E0B"

        self.ax1.clear()
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.ax1.plot(self.historico_tempo, self.historico_saude_gem, color=cor_grafico, linewidth=2.5)
        self.canvas1.draw()

        self.ax2.clear()
        self.configurar_estilo_eixo(self.ax2, "pH / EC", 0, 14)
        self.ax2.plot(self.historico_tempo, self.historico_sinc["ph"]["gem"], color="#38BDF8", label="pH", linewidth=2)
        self.ax2.plot(self.historico_tempo, self.historico_sinc["ec"]["gem"], color="#FB923C", label="EC", linewidth=2)
        self.ax2.legend(loc="upper right", facecolor="#0A0F1D", edgecolor="#1E293B", labelcolor="#F8FAFC", fontsize=9)
        self.canvas2.draw()

        self.ax3.clear()
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.ax3.plot(self.historico_tempo, self.historico_sinc["temp_ar"]["gem"], color="#EF4444", label="Ar", linewidth=2)
        self.ax3.plot(self.historico_tempo, self.historico_sinc["temp_agua"]["gem"], color="#2DD4BF", label="Água", linewidth=2)
        self.ax3.legend(loc="upper right", facecolor="#0A0F1D", edgecolor="#1E293B", labelcolor="#F8FAFC", fontsize=9)
        self.canvas3.draw()

        p_ativo = self.parametro_sincronia_ativo
        y_gem = self.historico_sinc[p_ativo]["gem"]
        y_real = self.historico_sinc[p_ativo]["real"]

        min_y, max_y, label_y = 0, 100, p_ativo.upper()
        if p_ativo == "ph": min_y, max_y, label_y = 4, 9, "pH"
        elif p_ativo == "ec": min_y, max_y, label_y = 0, 3, "EC (mS/cm)"
        elif p_ativo == "temp_ar": min_y, max_y, label_y = 10, 40, "Temp Ar (°C)"
        elif p_ativo == "temp_agua": min_y, max_y, label_y = 10, 35, "Temp Água (°C)"
        elif p_ativo == "umidade": min_y, max_y, label_y = 0, 100, "Umidade (%)"

        self.ax_sinc.clear()
        self.configurar_estilo_eixo(self.ax_sinc, label_y, min_y, max_y)
        self.ax_sinc.plot(self.historico_tempo, y_gem, color="#F59E0B", label=f"{label_y} Gêmeo", linewidth=2.2)
        self.ax_sinc.plot(self.historico_tempo, y_real, color="#38BDF8", label=f"{label_y} ESP32 Real", linewidth=2.2, linestyle="--")
        self.ax_sinc.legend(loc="upper right", facecolor="#0A0F1D", edgecolor="#1E293B", labelcolor="#F8FAFC", fontsize=9)
        self.canvas_sinc.draw()

    def atualizar_interface(self):
        self.horta.diagnosticar()
        dados = self.horta.snapshot()
        cfg = self.horta.config

        cultura_nome = getattr(cfg, 'nome_cultivo', 'Alface Experimental #01').upper()
        fase_atual = getattr(cfg, 'fase', 'VEGETATIVO')
        fase_visual = "FLORAÇÃO / FRUTIFICAÇÃO" if fase_atual == "FLORACAO" else fase_atual
        
        if self.modo_hardware_real:
            dia_exibicao = self.ultimo_valor_esp.get("dia_cultivo", 0)
            origem_tempo = "Hardware ESP32"
        else:
            dia_exibicao = self.dias_cultivo + getattr(cfg, 'dia_atual', 0)
            origem_tempo = "Simulador"
            
        self.label_sub_cultivo.configure(text=f"{cultura_nome} • Fase: {fase_visual} • Dia: {dia_exibicao} ({origem_tempo})")
        
        saude = dados['saude']
        self.label_saude_circulo.configure(text=f"{saude:.0f}%", text_color="#10B981" if saude > 80 else ("#F59E0B" if saude >= 40 else "#EF4444"))

        problemas = []
        if dados['ph'] < cfg.ph_min: problemas.append(f"• pH baixo ({dados['ph']:.2f} < {cfg.ph_min})")
        elif dados['ph'] > cfg.ph_max: problemas.append(f"• pH alto ({dados['ph']:.2f} > {cfg.ph_max})")

        if dados['ec'] < cfg.ec_min: problemas.append(f"• EC baixa ({dados['ec']:.1f} < {cfg.ec_min})")
        elif dados['ec'] > cfg.ec_max: problemas.append(f"• EC alta ({dados['ec']:.1f} > {cfg.ec_max})")

        if dados['temperatura_ar'] < cfg.temperatura_ar_min: problemas.append(f"• Ar frio ({dados['temperatura_ar']:.1f}°C)")
        elif dados['temperatura_ar'] > cfg.temperatura_ar_max: problemas.append(f"• Ar quente ({dados['temperatura_ar']:.1f}°C)")

        if dados['temperatura_agua'] < cfg.temperatura_agua_min: problemas.append(f"• Água fria ({dados['temperatura_agua']:.1f}°C)")
        elif dados['temperatura_agua'] > cfg.temperatura_agua_max: problemas.append(f"• Água quente ({dados['temperatura_agua']:.1f}°C)")

        if dados['nivel_agua'] < 20: problemas.append("• Reservatório baixo / Seco")

        fan_status = "OFF"; fan_color = "#94A3B8"
        if dados['temperatura_ar'] > cfg.temperatura_ar_max: fan_status = "ON (Calor)"; fan_color = "#FB923C"
        elif dados['umidade_ar'] > getattr(cfg, 'umidade_ar_max', 80): fan_status = "ON (Umidade)"; fan_color = "#38BDF8"
        self.label_dash_fan.configure(text=fan_status, text_color=fan_color)

        hora = dados.get('hora_atual', datetime.now().hour)
        inicio_luz = getattr(cfg, 'inicio_luz_hora', 6)
        fim_luz = (inicio_luz + getattr(cfg, 'fotoperiodo_horas', 18)) % 24
        luz_on = (inicio_luz <= hora < fim_luz) if inicio_luz < fim_luz else (hora >= inicio_luz or hora < fim_luz)
        self.label_dash_luz.configure(text="ON (Ativa)" if luz_on else "OFF (Noturno)", text_color="#F59E0B" if luz_on else "#94A3B8")

        if len(problemas) == 0 and saude > 80:
            self.label_saude_status_texto.configure(text="✅ Condições ideais para o desenvolvimento", text_color="#10B981")
        else:
            self.label_saude_status_texto.configure(text="⚠️ Anomalias Detectadas:\n" + "\n".join(problemas), text_color="#EF4444")

        if "Temperatura do ar" in self.labels_metas:
            self.labels_metas["Temperatura do ar"].configure(text=f"Meta: {cfg.temperatura_ar_min} a {cfg.temperatura_ar_max} °C")
            self.labels_metas["Umidade do ar"].configure(text=f"Meta: {cfg.umidade_ar_min} a {cfg.umidade_ar_max} %")
            self.labels_metas["Temperatura da água"].configure(text=f"Meta: {cfg.temperatura_agua_min} a {cfg.temperatura_agua_max} °C")
            self.labels_metas["pH"].configure(text=f"Meta: {cfg.ph_min} a {cfg.ph_max}")
            self.labels_metas["EC"].configure(text=f"Meta: {cfg.ec_min} a {cfg.ec_max} mS/cm")

        for nome, label in self.labels_valores.items():
            label.configure(text_color="#38BDF8" if self.modo_hardware_real else "#F59E0B")

        self.label_dash_temp.configure(text=f"{dados['temperatura_ar']:.1f} °C")
        self.label_dash_umid.configure(text=f"{dados['umidade_ar']:.0f} %")
        self.label_dash_temp_agua.configure(text=f"{dados['temperatura_agua']:.1f} °C")
        self.label_dash_ph.configure(text=f"{dados['ph']:.2f}")
        self.label_dash_ec.configure(text=f"{dados['ec']:.1f} mS/cm")
        self.label_dash_nivel.configure(text="OK (100%)" if dados['nivel_agua'] > 90 else f"{dados['nivel_agua']:.0f}%")

        t_real = self.ultimo_valor_esp.get("temperatura_ar", dados['temperatura_ar'])
        u_real = self.ultimo_valor_esp.get("umidade_ar", dados['umidade_ar'])
        ta_real = self.ultimo_valor_esp.get("temperatura_agua", dados['temperatura_agua'])
        ph_real = self.ultimo_valor_esp.get("ph", dados['ph'])
        ec_real = self.ultimo_valor_esp.get("ec", dados['ec'])
        nv_real = self.ultimo_valor_esp.get("nivel_agua", dados['nivel_agua'])
        saude_real = saude if self.modo_hardware_real else max(0.0, saude - 2.5)

        valores_reais = {"temp_ar": t_real, "umidade": u_real, "temp_agua": ta_real, "ph": ph_real, "ec": ec_real, "nivel": nv_real}

        if self.labels_comparativo["real"]:
            self.labels_comparativo["real"]["saude"].configure(text=f"{saude_real:.0f}%")
            self.labels_comparativo["real"]["temp_ar"].configure(text=f"{t_real:.1f} °C")
            self.labels_comparativo["real"]["umidade"].configure(text=f"{u_real:.0f} %")
            self.labels_comparativo["real"]["temp_agua"].configure(text=f"{ta_real:.1f} °C")
            self.labels_comparativo["real"]["ph"].configure(text=f"{ph_real:.2f}")
            self.labels_comparativo["real"]["ec"].configure(text=f"{ec_real:.1f} mS/cm")
            self.labels_comparativo["real"]["nivel"].configure(text=f"{nv_real:.0f}%")

            self.labels_comparativo["gem"]["saude"].configure(text=f"{saude:.0f}%")
            self.labels_comparativo["gem"]["temp_ar"].configure(text=f"{dados['temperatura_ar']:.1f} °C")
            self.labels_comparativo["gem"]["umidade"].configure(text=f"{dados['umidade_ar']:.0f} %")
            self.labels_comparativo["gem"]["temp_agua"].configure(text=f"{dados['temperatura_agua']:.1f} °C")
            self.labels_comparativo["gem"]["ph"].configure(text=f"{dados['ph']:.2f}")
            self.labels_comparativo["gem"]["ec"].configure(text=f"{dados['ec']:.1f} mS/cm")
            self.labels_comparativo["gem"]["nivel"].configure(text=f"{dados['nivel_agua']:.0f}%")
        
        texto_relogio = f"{hora:02d}:{dados.get('minuto_atual', 0):02d}  12/09/2026" if self.demonstracao_ativa else datetime.now().strftime("%H:%M  %d/%m/%Y")
        self.label_relogio_topo.configure(text=texto_relogio)
        
        self.atualizar_graficos_avancados(dados, valores_reais)

    def ciclo_interface(self):
        if self.demonstracao_ativa: self.horta.tick_tempo()
        if self.automacao_ativa: self.horta.executar_automacao()
        self.atualizar_interface()
        self.after(1000, self.ciclo_interface)

if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()
