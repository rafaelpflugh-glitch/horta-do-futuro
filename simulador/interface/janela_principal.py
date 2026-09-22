import customtkinter as ctk
import json
import os
import csv
import threading
from datetime import datetime
from tkinter import filedialog
from tkinter import messagebox

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
from modelo.banco_cultivos import listar_culturas, obter_configuracao_cultura


class JanelaPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("HORTA DO FUTURO — Digital Twin & Hardware Controller")
        self.geometry("1560x980")
        self.minsize(1250, 820)
        self.configure(fg_color="#02040A")

        self.horta = Horta()
        self.automacao_ativa = True
        self.demonstracao_ativa = False
        self.modo_hardware_real = False
        
        self.parametro_sincronia_ativo = "ph"
        self.ultimo_caminho_exportacao = os.path.expanduser("~")
        
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
        self.botoes_sidebar = {}
        self.botoes_aba_sinc = {}

        self.cultivos_salvos_cache = self.carregar_cultivos_disco()
        self.culturas_customizadas_cache = self.carregar_culturas_customizadas_disco()

        self.criar_interface()
        self.atualizar_interface()
        self.after(1000, self.ciclo_interface)

    # ================= ARQUIVOS E CACHE =================
    def carregar_cultivos_disco(self):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cultivos_salvos.json")
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {
            "Alface Experimental #01": {
                "cultura": "ALFACE", "fase": "VEGETATIVO", "fotoperiodo": 18.0, 
                "hora": 6, "minuto": 0, "ph_min": 5.5, "ph_max": 6.5, 
                "ec_min": 1.0, "ec_max": 1.8, "temp_ar_min": 18.0, "temp_ar_max": 26.0, 
                "temp_agua_min": 18.0, "temp_agua_max": 26.0, "umidade_min": 50.0, 
                "umidade_max": 80.0, "fertilizante": "Flex Azul + Vermelho (A+B)", "taxa_ab": 0.84,
                "bomba_on": 15, "bomba_off": 45, "fan_ex": 28.0, "fan_in": 25.0
            }
        }

    def salvar_cultivos_disco(self):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cultivos_salvos.json")
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(self.cultivos_salvos_cache, f, indent=4, ensure_ascii=False)
        except: pass

    def carregar_culturas_customizadas_disco(self):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "culturas_customizadas.json")
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}

    def salvar_culturas_customizadas_disco(self):
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "culturas_customizadas.json")
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(self.culturas_customizadas_cache, f, indent=4, ensure_ascii=False)
        except: pass

    def listar_todas_culturas(self):
        base = listar_culturas()
        custom = list(self.culturas_customizadas_cache.keys())
        return list(set(base + custom))

    # ================= CRIAÇÃO DA INTERFACE =================
    def criar_interface(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=290, fg_color="#050B14", corner_radius=0, border_width=1, border_color="#1E293B")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        topo_sidebar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        topo_sidebar.pack(fill="x", padx=20, pady=26)

        ctk.CTkLabel(topo_sidebar, text="HORTA DO FUTURO", font=("Segoe UI", 18, "bold"), text_color="#F8FAFC").pack(anchor="w")
        ctk.CTkLabel(topo_sidebar, text="INDUSTRIAL DIGITAL TWIN", font=("Segoe UI", 11, "bold"), text_color="#64748B").pack(anchor="w", pady=(3, 0))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=14, pady=12)

        itens_menu = [
            ("dashboard", "📊 Painel & Controles"),
            ("comparativo", "⚖️ Comparativo de Sincronia"),
            ("nutricao", "🌱 Receitas & Cultivo"),
            ("graficos", "📈 Gráficos & Logs"),
            ("config", "⚙️ Configurações ESP32")
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

        # Box Simulador Sidebar
        sim_box = ctk.CTkFrame(self.sidebar, fg_color="#080E1A", corner_radius=12, border_width=1, border_color="#1E293B")
        sim_box.pack(side="bottom", fill="x", padx=14, pady=14)

        self.label_titulo_sim_sidebar = ctk.CTkLabel(sim_box, text="CONTROLE DO SIMULADOR", font=("Segoe UI", 12, "bold"), text_color="#F59E0B")
        self.label_titulo_sim_sidebar.pack(pady=(14, 6))
        
        relogio_box = ctk.CTkFrame(sim_box, fg_color="#02040A", corner_radius=8, border_width=1, border_color="#1E293B")
        relogio_box.pack(fill="x", padx=14, pady=(0, 10))
        self.label_relogio_topo = ctk.CTkLabel(relogio_box, text=datetime.now().strftime("%H:%M  %d/%m/%Y"), font=("Segoe UI", 14, "bold"), text_color="#F59E0B")
        self.label_relogio_topo.pack(pady=8)

        vel_box = ctk.CTkFrame(sim_box, fg_color="transparent")
        vel_box.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(vel_box, text="Velocidade:", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_vel_sidebar = ctk.CTkLabel(vel_box, text="1x", font=("Segoe UI", 13, "bold"), text_color="#F59E0B")
        self.label_vel_sidebar.pack(side="right")

        self.slider_vel_sidebar = ctk.CTkSlider(
            sim_box, from_=1, to=10, number_of_steps=9, command=self.mudar_velocidade,
            progress_color="#F59E0B", button_color="#F8FAFC", button_hover_color="#E2E8F0", fg_color="#02040A", height=16
        )
        self.slider_vel_sidebar.pack(fill="x", padx=14, pady=8)
        self.slider_vel_sidebar.set(1)

        botoes_tempo_frame = ctk.CTkFrame(sim_box, fg_color="transparent")
        botoes_tempo_frame.pack(fill="x", padx=12, pady=4)

        for texto, minutos in [("+1h", 60), ("+1d", 1440)]:
            ctk.CTkButton(
                botoes_tempo_frame, text=texto, command=lambda m=minutos: self.avancar_tempo(m), height=32, width=60,
                fg_color="#0F172A", hover_color="#1E293B", text_color="#F8FAFC", font=("Segoe UI", 12, "bold"), corner_radius=6
            ).pack(side="left", expand=True, padx=3)

        self.btn_pausa_tempo = ctk.CTkButton(
            sim_box, text="▶ INICIAR SIMULADOR", command=self.alternar_demonstracao, height=38,
            fg_color="#F59E0B", hover_color="#D97706", text_color="#02040A", font=("Segoe UI", 13, "bold")
        )
        self.btn_pausa_tempo.pack(fill="x", padx=14, pady=(10, 8))

        self.btn_reset = ctk.CTkButton(
            sim_box, text="↺ RESETAR CULTIVO", command=self.resetar_planta, height=34,
            fg_color="#1E293B", hover_color="#334155", text_color="#F8FAFC", font=("Segoe UI", 12, "bold")
        )
        self.btn_reset.pack(fill="x", padx=14, pady=(0, 14))

        # Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="#02040A", corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        self.header = ctk.CTkFrame(self.main_container, height=65, fg_color="#050B14", corner_radius=0, border_width=1, border_color="#1E293B")
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        header_content = ctk.CTkFrame(self.header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=28)

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
        self.content_area.pack(fill="both", expand=True, padx=28, pady=28)

        # Telas
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

    # ================= TELAS =================
    def criar_tela_dashboard(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        titulo_box = ctk.CTkFrame(frame, fg_color="transparent")
        titulo_box.pack(fill="x", pady=(0, 14))
        self.label_titulo_painel = ctk.CTkLabel(titulo_box, text="Painel Geral • Gêmeo Digital", font=("Segoe UI", 24, "bold"), text_color="#F8FAFC")
        self.label_titulo_painel.pack(anchor="w")
        
        self.label_sub_cultivo = ctk.CTkLabel(titulo_box, text="ALFACE EXPERIMENTAL #01 • Fase: VEGETATIVO • Dia: 0 (Simulador)", font=("Segoe UI", 14, "bold"), text_color="#94A3B8")
        self.label_sub_cultivo.pack(anchor="w", pady=(4, 0))

        grid_principal = ctk.CTkFrame(frame, fg_color="transparent")
        grid_principal.pack(fill="both", expand=True, pady=(0, 10))
        grid_principal.grid_columnconfigure(0, weight=6, uniform="dash")
        grid_principal.grid_columnconfigure(1, weight=5, uniform="dash")
        grid_principal.grid_rowconfigure(0, weight=1)

        # ================= COLUNA ESQUERDA (DASHBOARDS COM SCROLL) =================
        col_esq_outer = ctk.CTkFrame(grid_principal, fg_color="transparent")
        col_esq_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        
        col_esq = ctk.CTkScrollableFrame(col_esq_outer, fg_color="transparent")
        col_esq.pack(fill="both", expand=True)
        col_esq.grid_columnconfigure(0, weight=1)

        # 1. Painel de Saúde
        self.card_saude_container = ctk.CTkFrame(col_esq, fg_color="#050B14", corner_radius=14, border_width=2, border_color="#1E293B")
        self.card_saude_container.pack(fill="x", pady=4)
        ctk.CTkLabel(self.card_saude_container, text="ÍNDICE DE SAÚDE BIOLÓGICA", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=20, pady=(16, 4))
        
        box_status = ctk.CTkFrame(self.card_saude_container, fg_color="transparent")
        box_status.pack(fill="x", padx=20, pady=(4, 16))
        self.label_saude_circulo = ctk.CTkLabel(box_status, text="100%", font=("Segoe UI", 48, "bold"), text_color="#10B981")
        self.label_saude_circulo.pack(side="left", padx=(0, 16))
        self.label_saude_status_texto = ctk.CTkLabel(box_status, text="✅ Condições ideais para o desenvolvimento", font=("Segoe UI", 13), text_color="#10B981", wraplength=340, justify="left")
        self.label_saude_status_texto.pack(side="left", fill="y", expand=True, pady=4)

        # Função auxiliar corrigida para retornar o widget lbl corretamente
        def criar_mini_card(parent, row, col, titulo, valor_padrao, cor_valor):
            f = ctk.CTkFrame(parent, fg_color="#02040A", corner_radius=10, border_width=1, border_color="#1E293B")
            f.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            ctk.CTkLabel(f, text=titulo, font=("Segoe UI", 12), text_color="#94A3B8").pack(anchor="w", padx=14, pady=(12, 0))
            lbl = ctk.CTkLabel(f, text=valor_padrao, font=("Segoe UI", 20, "bold"), text_color=cor_valor)
            lbl.pack(anchor="e", padx=14, pady=(4, 14))
            return lbl

        # 2. Clima (Grid 2x2)
        c2 = ctk.CTkFrame(col_esq, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        c2.pack(fill="x", pady=8)
        ctk.CTkLabel(c2, text="ATMOSFERA E CLIMA", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=20, pady=(16, 0))

        grid_ar = ctk.CTkFrame(c2, fg_color="transparent")
        grid_ar.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        grid_ar.grid_columnconfigure((0, 1), weight=1, uniform="a")
        
        self.label_dash_temp = criar_mini_card(grid_ar, 0, 0, "🌡️ Temperatura", "24.5 °C", "#EF4444")
        self.label_dash_umid = criar_mini_card(grid_ar, 0, 1, "💦 Umidade", "62 %", "#38BDF8")
        self.label_dash_fan = criar_mini_card(grid_ar, 1, 0, "💨 Exaustores", "OFF", "#94A3B8")
        self.label_dash_luz = criar_mini_card(grid_ar, 1, 1, "☀️ Iluminação", "ON", "#F59E0B")

        # 3. Hidroponia (Grid 2x2)
        c3 = ctk.CTkFrame(col_esq, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        c3.pack(fill="x", pady=4)
        ctk.CTkLabel(c3, text="SOLUÇÃO HIDROPÔNICA & RESERVATÓRIO", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=20, pady=(16, 0))
        
        grid_dwc = ctk.CTkFrame(c3, fg_color="transparent")
        grid_dwc.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        grid_dwc.grid_columnconfigure((0, 1), weight=1, uniform="b")

        self.label_dash_temp_agua = criar_mini_card(grid_dwc, 0, 0, "🌊 Temp. Água", "22.0 °C", "#2DD4BF")
        self.label_dash_ph = criar_mini_card(grid_dwc, 0, 1, "🧪 pH Solução", "6.10", "#38BDF8")
        self.label_dash_ec = criar_mini_card(grid_dwc, 1, 0, "⚡ EC Nutrientes", "1.4 mS/cm", "#FB923C")
        self.label_dash_nivel = criar_mini_card(grid_dwc, 1, 1, "🪣 Nível Tanque", "100%", "#10B981")

        # ================= COLUNA DIREITA (SIMULADOR) =================
        col_dir = ctk.CTkFrame(grid_principal, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        
        header_dir = ctk.CTkFrame(col_dir, fg_color="transparent")
        header_dir.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(header_dir, text="SIMULADOR DE SENSORES (MANUAL)", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w")
        ctk.CTkLabel(header_dir, text="Desative o ESP32 acima para mover os seletores:", font=("Segoe UI", 11), text_color="#94A3B8").pack(anchor="w", pady=(2, 0))

        sim_scroll_frame = ctk.CTkScrollableFrame(col_dir, fg_color="transparent", width=200)
        sim_scroll_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.criar_controle(sim_scroll_frame, "🌡️", "Temperatura do ar", 10, 40, self.horta.temperatura_ar, self.mudar_temperatura_ar, "°C")
        self.criar_controle(sim_scroll_frame, "💦", "Umidade do ar", 0, 100, self.horta.umidade_ar, self.mudar_umidade_ar, "%")
        self.criar_controle(sim_scroll_frame, "🌊", "Temperatura da água", 5, 40, self.horta.temperatura_agua, self.mudar_temperatura_agua, "°C")
        self.criar_controle(sim_scroll_frame, "🧪", "pH", 2, 12, self.horta.ph, self.mudar_ph, "")
        self.criar_controle(sim_scroll_frame, "⚡", "EC", 0, 3, self.horta.ec, self.mudar_ec, "mS/cm")
        self.criar_controle(sim_scroll_frame, "🪣", "Nível da água", 0, 100, self.horta.nivel_agua, self.mudar_nivel_agua, "%")

        return frame

    def criar_tela_comparativo(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        titulo_box = ctk.CTkFrame(frame, fg_color="transparent")
        titulo_box.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(titulo_box, text="Diagnóstico de Sincronia • ESP32 vs. Gêmeo Digital", font=("Segoe UI", 24, "bold"), text_color="#F8FAFC").pack(anchor="w")
        ctk.CTkLabel(titulo_box, text="Validação da precisão preditiva do modelo frente às leituras físicas do hardware.", font=("Segoe UI", 13), text_color="#94A3B8").pack(anchor="w", pady=(3, 0))

        graf_box = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        graf_box.pack(fill="x", pady=(0, 14))

        header_graf = ctk.CTkFrame(graf_box, fg_color="transparent")
        header_graf.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(header_graf, text="CURVAS TEMPORAIS DE SINCRONIA", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(side="left")
        
        abas_frame = ctk.CTkFrame(header_graf, fg_color="transparent")
        abas_frame.pack(side="right")

        botoes_param = [("pH", "ph"), ("EC", "ec"), ("Temp. Ar", "temp_ar"), ("Temp. Água", "temp_agua"), ("Umidade", "umidade")]
        
        for text, key in botoes_param:
            btn = ctk.CTkButton(
                abas_frame, text=text, width=80, height=30,
                fg_color="#0F172A" if key != self.parametro_sincronia_ativo else "#1E293B",
                text_color="#94A3B8" if key != self.parametro_sincronia_ativo else "#F59E0B",
                font=("Segoe UI", 12, "bold"), corner_radius=6, command=lambda k=key: self.alternar_aba_sincronia(k)
            )
            btn.pack(side="left", padx=3)
            self.botoes_aba_sinc[key] = btn

        self.fig_sinc = Figure(figsize=(10, 2.0), dpi=100)
        self.fig_sinc.patch.set_facecolor('#050B14')
        self.ax_sinc = self.fig_sinc.add_subplot(111)
        self.configurar_estilo_eixo(self.ax_sinc, "pH", 4, 9)
        self.canvas_sinc = FigureCanvasTkAgg(self.fig_sinc, master=graf_box)
        self.canvas_sinc.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=10)

        grid_comp = ctk.CTkFrame(frame, fg_color="transparent")
        grid_comp.pack(fill="both", expand=True)
        grid_comp.grid_columnconfigure((0, 1), weight=1, uniform="comp")
        grid_comp.grid_rowconfigure(0, weight=1)

        col_real = ctk.CTkFrame(grid_comp, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        col_real.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(col_real, text="📡 HARDWARE REAL (ESP32)", font=("Segoe UI", 12, "bold"), text_color="#38BDF8").pack(anchor="w", padx=18, pady=(16, 10))

        col_gem = ctk.CTkFrame(grid_comp, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        col_gem.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(col_gem, text="🔮 GÊMEO DIGITAL (PREDITIVO)", font=("Segoe UI", 12, "bold"), text_color="#F59E0B").pack(anchor="w", padx=18, pady=(16, 10))

        parametros = [
            ("Índice de Saúde Biológica", "saude", "%"), ("Temperatura do Ar", "temp_ar", "°C"),
            ("Umidade Relativa", "umidade", "%"), ("Temperatura da Água", "temp_agua", "°C"),
            ("pH da Solução", "ph", ""), ("Condutividade Elétrica (EC)", "ec", "mS/cm"),
            ("Nível do Reservatório", "nivel", "%")
        ]

        for nome, chave, unidade in parametros:
            f_r = ctk.CTkFrame(col_real, fg_color="#02040A", corner_radius=8, height=38)
            f_r.pack(fill="x", padx=14, pady=4)
            f_r.pack_propagate(False)
            ctk.CTkLabel(f_r, text=nome, font=("Segoe UI", 12), text_color="#CBD5E1").pack(side="left", padx=14)
            lbl_r = ctk.CTkLabel(f_r, text="--", font=("Segoe UI", 13, "bold"), text_color="#38BDF8")
            lbl_r.pack(side="right", padx=14)
            self.labels_comparativo["real"][chave] = lbl_r

            f_g = ctk.CTkFrame(col_gem, fg_color="#02040A", corner_radius=8, height=38)
            f_g.pack(fill="x", padx=14, pady=4)
            f_g.pack_propagate(False)
            ctk.CTkLabel(f_g, text=nome, font=("Segoe UI", 12), text_color="#CBD5E1").pack(side="left", padx=14)
            lbl_g = ctk.CTkLabel(f_g, text="--", font=("Segoe UI", 13, "bold"), text_color="#F59E0B")
            lbl_g.pack(side="right", padx=14)
            self.labels_comparativo["gem"][chave] = lbl_g

        return frame

    def alternar_aba_sincronia(self, chave):
        self.parametro_sincronia_ativo = chave
        for k, btn in self.botoes_aba_sinc.items():
            btn.configure(fg_color="#1E293B" if k == chave else "#0F172A", text_color="#F59E0B" if k == chave else "#94A3B8")
        self.atualizar_interface()

    # ================= TELA DE NUTRIÇÃO =================
    def criar_tela_nutricao(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="nut")
        frame.grid_rowconfigure(0, weight=1)

        # ================= COLUNA 1: IDENTIDADE =================
        col1 = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        header_col1 = ctk.CTkFrame(col1, fg_color="transparent")
        header_col1.pack(fill="x", padx=22, pady=(20, 4))
        ctk.CTkLabel(header_col1, text="1. RECEITA & IDENTIDADE DO CULTIVO", font=("Segoe UI", 12, "bold"), text_color="#38BDF8").pack(side="left")
        
        sub_c1 = ctk.CTkFrame(col1, fg_color="transparent")
        sub_c1.pack(fill="x", padx=22, pady=(0, 10))
        ctk.CTkLabel(sub_c1, text="Defina o perfil salvo e a espécie da planta.", font=("Segoe UI", 11), text_color="#64748B").pack(anchor="w")

        box_cultivos = ctk.CTkFrame(col1, fg_color="transparent")
        box_cultivos.pack(fill="x", padx=22, pady=6)
        
        lbl_l = ctk.CTkFrame(box_cultivos, fg_color="transparent")
        lbl_l.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(lbl_l, text="Meus Cultivos Salvos", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkButton(lbl_l, text="＋ Novo", command=self.acao_novo_cultivo_limpo, width=80, height=28, fg_color="#1E293B", hover_color="#334155", text_color="#38BDF8", font=("Segoe UI", 11, "bold"), corner_radius=6).pack(side="right")

        self.combo_cultivos_salvos = ctk.CTkComboBox(box_cultivos, values=list(self.cultivos_salvos_cache.keys()), command=self.carregar_cultivo_salvo, fg_color="#02040A", border_color="#1E293B", button_color="#1E293B", height=38, font=("Segoe UI", 13, "bold"))
        self.combo_cultivos_salvos.pack(fill="x")

        box_cultura = ctk.CTkFrame(col1, fg_color="transparent")
        box_cultura.pack(fill="x", padx=22, pady=10)

        lbl_c = ctk.CTkFrame(box_cultura, fg_color="transparent")
        lbl_c.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(lbl_c, text="Tipo de Planta", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkButton(lbl_c, text="＋ Nova", command=self.abrir_modal_nova_cultura, width=80, height=28, fg_color="#1E293B", hover_color="#334155", text_color="#F59E0B", font=("Segoe UI", 11, "bold"), corner_radius=6).pack(side="right")

        self.combo_cultura = ctk.CTkComboBox(box_cultura, values=self.listar_todas_culturas(), command=self.carregar_cultura, fg_color="#02040A", border_color="#1E293B", button_color="#1E293B", height=38, font=("Segoe UI", 13, "bold"))
        self.combo_cultura.pack(fill="x")

        box_detalhes = ctk.CTkFrame(col1, fg_color="transparent")
        box_detalhes.pack(fill="x", padx=22, pady=10)

        ctk.CTkLabel(box_detalhes, text="Nome do Cultivo Ativo", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 4))
        self.entry_nome_cultivo = ctk.CTkEntry(box_detalhes, fg_color="#02040A", border_color="#1E293B", height=38, font=("Segoe UI", 13, "bold"))
        self.entry_nome_cultivo.pack(fill="x")

        guia_box = ctk.CTkFrame(col1, fg_color="#080E1A", corner_radius=10, border_width=1, border_color="#10B981")
        guia_box.pack(fill="x", padx=22, pady=(18, 20))
        
        f_guia_top = ctk.CTkFrame(guia_box, fg_color="transparent")
        f_guia_top.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(f_guia_top, text="💡 GUIA DE CORREÇÃO NUTRICIONAL", font=("Segoe UI", 12, "bold"), text_color="#10B981").pack(anchor="w")
        
        self.label_guia_nutricional = ctk.CTkLabel(guia_box, text="Calculando orientações...", font=("Segoe UI", 11), text_color="#CBD5E1", justify="left")
        self.label_guia_nutricional.pack(anchor="w", padx=16, pady=(0, 12))

        # ================= COLUNA 2: AUTOMAÇÃO =================
        col2 = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        col2.grid(row=0, column=1, sticky="nsew", padx=12)

        header_col2 = ctk.CTkFrame(col2, fg_color="transparent")
        header_col2.pack(fill="x", padx=22, pady=(20, 4))
        ctk.CTkLabel(header_col2, text="2. PERFIS DE AUTOMAÇÃO", font=("Segoe UI", 12, "bold"), text_color="#38BDF8").pack(side="left")
        
        sub_c2 = ctk.CTkFrame(col2, fg_color="transparent")
        sub_c2.pack(fill="x", padx=22, pady=(0, 10))
        ctk.CTkLabel(sub_c2, text="Ciclos de iluminação, rega e controle climático.", font=("Segoe UI", 11), text_color="#64748B").pack(anchor="w")

        box_foto_conteudo = ctk.CTkFrame(col2, fg_color="transparent")
        box_foto_conteudo.pack(fill="x", padx=22, pady=2)

        ctk.CTkLabel(box_foto_conteudo, text="Fase de Crescimento", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 4))
        self.segmented_fase = ctk.CTkSegmentedButton(
            box_foto_conteudo, values=["MUDAS", "VEGA", "FLORA"], command=self.mudar_fase_via_segmento,
            font=("Segoe UI", 12, "bold"), height=38, fg_color="#02040A", selected_color="#38BDF8",
            selected_hover_color="#0284C7", unselected_color="#02040A", unselected_hover_color="#1E293B"
        )
        self.segmented_fase.pack(fill="x", pady=(0, 12))
        self.segmented_fase.set("VEGA")

        resumo_auto_box = ctk.CTkFrame(box_foto_conteudo, fg_color="#02040A", corner_radius=8, border_width=1, border_color="#1E293B")
        resumo_auto_box.pack(fill="x", pady=8)
        
        self.lbl_resumo_luz = ctk.CTkLabel(resumo_auto_box, text="☀️ Iluminação: -- h/dia (Início --:--)", font=("Segoe UI", 12), text_color="#F8FAFC", anchor="w")
        self.lbl_resumo_luz.pack(fill="x", padx=16, pady=(12, 4))
        self.lbl_resumo_bomba = ctk.CTkLabel(resumo_auto_box, text="💧 Irrigação: --m ON / --m OFF", font=("Segoe UI", 12), text_color="#F8FAFC", anchor="w")
        self.lbl_resumo_bomba.pack(fill="x", padx=16, pady=4)
        self.lbl_resumo_fan = ctk.CTkLabel(resumo_auto_box, text="💨 Clima: Exaustão > --°C", font=("Segoe UI", 12), text_color="#F8FAFC", anchor="w")
        self.lbl_resumo_fan.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkButton(box_foto_conteudo, text="⚙️ CONFIGURAR PARÂMETROS", command=self.abrir_modal_automacao, height=36, fg_color="#1E293B", hover_color="#334155", text_color="#38BDF8", font=("Segoe UI", 12, "bold"), corner_radius=6).pack(fill="x", pady=(12, 6))
        ctk.CTkButton(box_foto_conteudo, text="↺ Restaurar Automação Padrão", command=self.acao_novo_cultivo_limpo, height=30, fg_color="transparent", hover_color="#0F172A", text_color="#F59E0B", font=("Segoe UI", 11, "bold"), corner_radius=6).pack(fill="x", pady=2)

        # ================= COLUNA 3: METAS BIOLÓGICAS =================
        col3 = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        col3.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        
        f_col3_topo = ctk.CTkFrame(col3, fg_color="transparent")
        f_col3_topo.pack(fill="x", padx=22, pady=(20, 4))
        ctk.CTkLabel(f_col3_topo, text="3. METAS & ASSISTENTE NUTRICIONAL", font=("Segoe UI", 12, "bold"), text_color="#38BDF8").pack(side="left")
        
        sub_c3 = ctk.CTkFrame(col3, fg_color="transparent")
        sub_c3.pack(fill="x", padx=22, pady=(0, 10))
        ctk.CTkLabel(sub_c3, text="Limites ideais de pH e fertilização.", font=("Segoe UI", 11), text_color="#64748B").pack(anchor="w")

        resumo_metas_box = ctk.CTkFrame(col3, fg_color="#02040A", corner_radius=8, border_width=1, border_color="#1E293B")
        resumo_metas_box.pack(fill="x", padx=22, pady=4)
        
        f_m1 = ctk.CTkFrame(resumo_metas_box, fg_color="transparent")
        f_m1.pack(fill="x", padx=16, pady=(12, 4))
        self.lbl_resumo_ph = ctk.CTkLabel(f_m1, text="🧪 pH: -- a --", font=("Segoe UI", 12), text_color="#F8FAFC")
        self.lbl_resumo_ph.pack(side="left")
        self.lbl_resumo_ec = ctk.CTkLabel(f_m1, text="⚡ EC: -- a --", font=("Segoe UI", 12), text_color="#F8FAFC")
        self.lbl_resumo_ec.pack(side="right")

        f_m2 = ctk.CTkFrame(resumo_metas_box, fg_color="transparent")
        f_m2.pack(fill="x", padx=16, pady=4)
        self.lbl_resumo_tar = ctk.CTkLabel(f_m2, text="🌡️ Ar: -- a -- °C", font=("Segoe UI", 12), text_color="#F8FAFC")
        self.lbl_resumo_tar.pack(side="left")
        self.lbl_resumo_tag = ctk.CTkLabel(f_m2, text="🌊 Água: -- a -- °C", font=("Segoe UI", 12), text_color="#F8FAFC")
        self.lbl_resumo_tag.pack(side="right")

        self.lbl_resumo_umi = ctk.CTkLabel(resumo_metas_box, text="💦 Umidade Ar: -- a -- %", font=("Segoe UI", 12), text_color="#F8FAFC", anchor="w")
        self.lbl_resumo_umi.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkButton(col3, text="⚙️ AJUSTAR LIMITES BIOLÓGICOS", command=self.abrir_modal_metas, height=36, fg_color="#1E293B", hover_color="#334155", text_color="#10B981", font=("Segoe UI", 12, "bold"), corner_radius=6).pack(fill="x", padx=22, pady=(8, 12))

        nut_box = ctk.CTkFrame(col3, fg_color="transparent")
        nut_box.pack(fill="x", padx=18, pady=4)
        ctk.CTkLabel(nut_box, text="FERTILIZANTE COMERCIAL", font=("Segoe UI", 11, "bold"), text_color="#64748B").pack(pady=(6, 2), anchor="w", padx=4)
        
        f_prod = ctk.CTkFrame(nut_box, fg_color="transparent")
        f_prod.pack(fill="x", padx=4, pady=4)
        ctk.CTkLabel(f_prod, text="Produto:", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="left")
        self.entry_nome_fertilizante = ctk.CTkEntry(f_prod, width=190, fg_color="#02040A", border_color="#1E293B", height=36, font=("Segoe UI", 12, "bold"))
        self.entry_nome_fertilizante.pack(side="right")

        f_taxa = ctk.CTkFrame(nut_box, fg_color="transparent")
        f_taxa.pack(fill="x", padx=4, pady=4)
        ctk.CTkLabel(f_taxa, text="g/L por +1.0 EC:", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="left")
        self.entry_taxa_ab = ctk.CTkEntry(f_taxa, width=80, fg_color="#02040A", border_color="#1E293B", height=36, font=("Segoe UI", 12, "bold"), justify="center")
        self.entry_taxa_ab.pack(side="right")

        botoes_acao_receita = ctk.CTkFrame(col3, fg_color="transparent")
        botoes_acao_receita.pack(fill="x", padx=18, pady=(16, 20))
        ctk.CTkButton(botoes_acao_receita, text="💾 SALVAR", command=self.salvar_receita_local, height=42, fg_color="#0F172A", hover_color="#1E293B", text_color="#F8FAFC", font=("Segoe UI", 12, "bold"), corner_radius=6).pack(side="left", expand=True, padx=(0, 6))
        ctk.CTkButton(botoes_acao_receita, text="⚡ SINCRONIZAR", command=self.sincronizar_receita_esp32, height=42, fg_color="#38BDF8", hover_color="#0284C7", text_color="#02040A", font=("Segoe UI", 12, "bold"), corner_radius=6).pack(side="left", expand=True, padx=(6, 0))

        self.preencher_configuracao()
        return frame

    # ================= MODAIS & AÇÕES =================
    def abrir_modal_automacao(self):
        top = ctk.CTkToplevel(self)
        top.title("Configurar Automação (Ciclos & Clima)")
        top.geometry("400x520")
        top.attributes("-topmost", True)
        top.configure(fg_color="#050B14")
        top.grab_set()

        ctk.CTkLabel(top, text="⚙️ PARÂMETROS DE AUTOMAÇÃO", font=("Segoe UI", 15, "bold"), text_color="#38BDF8").pack(pady=(22, 12))
        f_form = ctk.CTkFrame(top, fg_color="transparent")
        f_form.pack(fill="x", padx=26, pady=4)

        cfg = self.horta.config
        
        def criar_input(parent, titulo, valor_padrao):
            linha = ctk.CTkFrame(parent, fg_color="transparent")
            linha.pack(fill="x", pady=6)
            ctk.CTkLabel(linha, text=titulo, text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="left")
            e = ctk.CTkEntry(linha, width=70, fg_color="#02040A", border_color="#1E293B", font=("Segoe UI", 13, "bold"), justify="center")
            e.pack(side="right")
            e.insert(0, str(valor_padrao))
            return e

        e_foto = criar_input(f_form, "Horas de Luz / Dia (h):", getattr(cfg, 'fotoperiodo_horas', 18.0))
        e_hora = criar_input(f_form, "Início da Luz (Hora 0-23):", getattr(cfg, 'inicio_luz_hora', 6))
        e_min = criar_input(f_form, "Início da Luz (Minuto 0-59):", getattr(cfg, 'inicio_luz_minuto', 0))
        ctk.CTkFrame(f_form, height=1, fg_color="#1E293B").pack(fill="x", pady=10)
        e_bon = criar_input(f_form, "Bomba Submersa - LIGADA (min):", getattr(cfg, 'bomba_on_min', 15))
        e_boff = criar_input(f_form, "Bomba Submersa - PAUSA (min):", getattr(cfg, 'bomba_off_min', 45))
        ctk.CTkFrame(f_form, height=1, fg_color="#1E293B").pack(fill="x", pady=10)
        e_fex = criar_input(f_form, "Ligar Exaustor se Ar > (°C):", getattr(cfg, 'fan_exaustao_trigger', 28.0))
        e_fin = criar_input(f_form, "Ligar Insuflador se Ar > (°C):", getattr(cfg, 'fan_insuflacao_trigger', 25.0))

        def salvar():
            try:
                cfg.fotoperiodo_horas = float(e_foto.get())
                cfg.inicio_luz_hora = int(e_hora.get())
                cfg.inicio_luz_minuto = int(e_min.get())
                cfg.bomba_on_min = int(e_bon.get())
                cfg.bomba_off_min = int(e_boff.get())
                cfg.fan_exaustao_trigger = float(e_fex.get())
                cfg.fan_insuflacao_trigger = float(e_fin.get())
                self.atualizar_resumos_visuais()
                top.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos. Use apenas números (ex: 28.0).")

        ctk.CTkButton(top, text="APLICAR", command=salvar, fg_color="#38BDF8", hover_color="#0284C7", text_color="#02040A", height=40, font=("Segoe UI", 13, "bold"), corner_radius=6).pack(fill="x", padx=26, pady=20)

    def abrir_modal_metas(self):
        top = ctk.CTkToplevel(self)
        top.title("Ajustar Limites Biológicos")
        top.geometry("400x480")
        top.attributes("-topmost", True)
        top.configure(fg_color="#050B14")
        top.grab_set()

        ctk.CTkLabel(top, text="⚙️ LIMITES BIOLÓGICOS", font=("Segoe UI", 15, "bold"), text_color="#10B981").pack(pady=(22, 12))
        f_form = ctk.CTkFrame(top, fg_color="transparent")
        f_form.pack(fill="x", padx=26, pady=4)

        cfg = self.horta.config
        
        def criar_input_duplo(parent, titulo, v_min, v_max):
            linha = ctk.CTkFrame(parent, fg_color="transparent")
            linha.pack(fill="x", pady=6)
            ctk.CTkLabel(linha, text=titulo, text_color="#CBD5E1", font=("Segoe UI", 12)).pack(side="left")
            
            f_vals = ctk.CTkFrame(linha, fg_color="transparent")
            f_vals.pack(side="right")
            e1 = ctk.CTkEntry(f_vals, width=50, fg_color="#02040A", border_color="#1E293B", justify="center", font=("Segoe UI", 12, "bold"))
            e1.pack(side="left")
            e1.insert(0, str(v_min))
            ctk.CTkLabel(f_vals, text="-", text_color="#94A3B8").pack(side="left", padx=4)
            e2 = ctk.CTkEntry(f_vals, width=50, fg_color="#02040A", border_color="#1E293B", justify="center", font=("Segoe UI", 12, "bold"))
            e2.pack(side="left")
            e2.insert(0, str(v_max))
            return e1, e2

        e_ph_min, e_ph_max = criar_input_duplo(f_form, "pH:", getattr(cfg, 'ph_min', 5.5), getattr(cfg, 'ph_max', 6.5))
        e_ec_min, e_ec_max = criar_input_duplo(f_form, "EC (mS/cm):", getattr(cfg, 'ec_min', 1.0), getattr(cfg, 'ec_max', 1.8))
        e_tar_min, e_tar_max = criar_input_duplo(f_form, "Temp. Ar (°C):", getattr(cfg, 'temperatura_ar_min', 18.0), getattr(cfg, 'temperatura_ar_max', 26.0))
        e_tag_min, e_tag_max = criar_input_duplo(f_form, "Temp. Água (°C):", getattr(cfg, 'temperatura_agua_min', 18.0), getattr(cfg, 'temperatura_agua_max', 26.0))
        e_umi_min, e_umi_max = criar_input_duplo(f_form, "Umidade (%):", getattr(cfg, 'umidade_ar_min', 50.0), getattr(cfg, 'umidade_ar_max', 80.0))

        def salvar():
            try:
                cfg.ph_min = float(e_ph_min.get()); cfg.ph_max = float(e_ph_max.get())
                cfg.ec_min = float(e_ec_min.get()); cfg.ec_max = float(e_ec_max.get())
                cfg.temperatura_ar_min = float(e_tar_min.get()); cfg.temperatura_ar_max = float(e_tar_max.get())
                cfg.temperatura_agua_min = float(e_tag_min.get()); cfg.temperatura_agua_max = float(e_tag_max.get())
                cfg.umidade_ar_min = float(e_umi_min.get()); cfg.umidade_ar_max = float(e_umi_max.get())
                self.atualizar_resumos_visuais()
                top.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos.")

        ctk.CTkButton(top, text="APLICAR", command=salvar, fg_color="#10B981", hover_color="#059669", text_color="#FFFFFF", height=40, font=("Segoe UI", 13, "bold"), corner_radius=6).pack(fill="x", padx=26, pady=20)

    def atualizar_resumos_visuais(self):
        cfg = self.horta.config
        
        h = getattr(cfg, 'inicio_luz_hora', 6)
        m = getattr(cfg, 'inicio_luz_minuto', 0)
        self.lbl_resumo_luz.configure(text=f"☀️ Iluminação: {getattr(cfg, 'fotoperiodo_horas', 18.0)} h/dia (Início {h:02d}:{m:02d})")
        self.lbl_resumo_bomba.configure(text=f"💧 Irrigação: {getattr(cfg, 'bomba_on_min', 15)}m ON / {getattr(cfg, 'bomba_off_min', 45)}m OFF")
        self.lbl_resumo_fan.configure(text=f"💨 Clima: Exaustão > {getattr(cfg, 'fan_exaustao_trigger', 28.0)}°C")
        
        self.lbl_resumo_ph.configure(text=f"🧪 pH: {getattr(cfg, 'ph_min', 5.5)} a {getattr(cfg, 'ph_max', 6.5)}")
        self.lbl_resumo_ec.configure(text=f"⚡ EC: {getattr(cfg, 'ec_min', 1.0)} a {getattr(cfg, 'ec_max', 1.8)}")
        self.lbl_resumo_tar.configure(text=f"🌡️ Ar: {getattr(cfg, 'temperatura_ar_min', 18.0)} a {getattr(cfg, 'temperatura_ar_max', 26.0)} °C")
        self.lbl_resumo_tag.configure(text=f"🌊 Água: {getattr(cfg, 'temperatura_agua_min', 18.0)} a {getattr(cfg, 'temperatura_agua_max', 26.0)} °C")
        self.lbl_resumo_umi.configure(text=f"💦 Umidade Ar: {getattr(cfg, 'umidade_ar_min', 50.0)} a {getattr(cfg, 'umidade_ar_max', 80.0)} %")

        try:
            if hasattr(self.horta, 'calcular_receita_dosagem'):
                guia = self.horta.calcular_receita_dosagem()
                texto_guia = f"Vol: {guia.get('volume_agua_litros', 10.0)}L | Fert A+B: +{guia.get('gramas_fertilizante', 0.0):.1f}g\n"
                texto_guia += f"pH Correção: {guia.get('acao_ph', 'Estável')} ({guia.get('ml_ph', 0.0):.1f}ml)"
                self.label_guia_nutricional.configure(text=texto_guia)
            else:
                luz = getattr(cfg, 'fotoperiodo_horas', 18.0)
                escuro = max(0.0, 24.0 - luz)
                self.label_guia_nutricional.configure(text=f"Vol: 10.0L | Luz: {luz}h | Escuro: {escuro:.1f}h\n(Orientações baseadas no volume)")
        except Exception:
            self.label_guia_nutricional.configure(text="Vol: 10.0L | Sistema Nutricional Ativo")

    def preencher_configuracao(self):
        try:
            config = self.horta.config
            self.entry_nome_cultivo.delete(0, "end")
            self.entry_nome_cultivo.insert(0, getattr(config, 'nome_cultivo', 'Alface Experimental #01'))
            
            fase = getattr(config, 'fase', 'VEGETATIVO')
            mapa_reverso = {"MUDAS": "MUDAS", "VEGETATIVO": "VEGA", "FLORACAO": "FLORA", "FLORACAO_FRUTIFICACAO": "FLORA"}
            if fase in mapa_reverso: self.segmented_fase.set(mapa_reverso[fase])

            self.entry_nome_fertilizante.delete(0, "end")
            self.entry_nome_fertilizante.insert(0, getattr(self.horta, 'nome_fertilizante', 'Flex Azul + Vermelho'))
            self.entry_taxa_ab.delete(0, "end")
            self.entry_taxa_ab.insert(0, str(getattr(self.horta, 'gramas_por_litro_recomendado', 0.84)))
            
            self.atualizar_resumos_visuais()
        except Exception as e: pass

    def coletar_dados_formulario(self):
        cfg = self.horta.config
        cfg.nome_cultivo = self.entry_nome_cultivo.get()
        
        val_atual = self.segmented_fase.get()
        mapa_fases = {"MUDAS": "MUDAS", "VEGA": "VEGETATIVO", "FLORA": "FLORACAO"}
        cfg.fase = mapa_fases.get(val_atual, "VEGETATIVO")

        self.horta.nome_fertilizante = self.entry_nome_fertilizante.get()
        try: self.horta.gramas_por_litro_recomendado = float(self.entry_taxa_ab.get())
        except: pass
        return cfg

    def acao_novo_cultivo_limpo(self):
        self.entry_nome_cultivo.delete(0, "end")
        self.entry_nome_cultivo.insert(0, "Novo Cultivo #01")
        self.combo_cultura.set("ALFACE")
        self.mudar_fase_via_segmento("VEGA")
        self.atualizar_resumos_visuais()
        self.atualizar_log_serial("[INFO] Formulário limpo. Pronto para configurar novo cultivo do zero.\n")

    def mudar_fase_via_segmento(self, valor_escolhido):
        mapa_fases = {"MUDAS": "MUDA", "VEGA": "VEGETATIVO", "FLORA": "FLORACAO"}
        nova_fase = mapa_fases.get(valor_escolhido, "VEGETATIVO")
        cfg = self.horta.config
        cfg.fase = nova_fase
        self.segmented_fase.set(valor_escolhido)
        
        if nova_fase == "MUDA":
            cfg.fotoperiodo_horas = 18.0; cfg.ec_min = 0.8; cfg.ec_max = 1.2
        elif nova_fase == "FLORACAO":
            cfg.fotoperiodo_horas = 12.0; cfg.ec_min = 1.8; cfg.ec_max = 2.5
        else:
            cfg.fotoperiodo_horas = 16.0; cfg.ec_min = 1.2; cfg.ec_max = 1.8

        self.atualizar_resumos_visuais()
        self.horta.diagnosticar()
        self.atualizar_interface()

    def abrir_modal_nova_cultura(self):
        top = ctk.CTkToplevel(self)
        top.title("Cadastrar Nova Espécie de Planta")
        top.geometry("460x310")
        top.attributes("-topmost", True)
        top.configure(fg_color="#050B14")
        top.grab_set()

        ctk.CTkLabel(top, text="🌾 CADASTRAR NOVA ESPÉCIE", font=("Segoe UI", 15, "bold"), text_color="#F59E0B").pack(pady=(22, 12))
        
        f_form = ctk.CTkFrame(top, fg_color="transparent")
        f_form.pack(fill="x", padx=26, pady=4)
        
        ctk.CTkLabel(f_form, text="Nome da Espécie (ex: TOMATE):", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w")
        entry_cult = ctk.CTkEntry(f_form, height=40, fg_color="#02040A", border_color="#1E293B", font=("Segoe UI", 13, "bold"))
        entry_cult.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(f_form, text="Fotoperíodo padrão (Horas de luz):", text_color="#CBD5E1", font=("Segoe UI", 12)).pack(anchor="w")
        entry_foto = ctk.CTkEntry(f_form, height=40, fg_color="#02040A", border_color="#1E293B", font=("Segoe UI", 13, "bold"))
        entry_foto.pack(fill="x", pady=(4, 14))
        entry_foto.insert(0, "16.0")

        def salvar():
            nome = entry_cult.get().strip().upper()
            try: foto = float(entry_foto.get().replace(",", "."))
            except ValueError: foto = 16.0
            if nome:
                self.culturas_customizadas_cache[nome] = {
                    "ph_min": 5.8, "ph_max": 6.3, "ec_min": 1.2, "ec_max": 2.0,
                    "temp_ar_min": 18.0, "temp_ar_max": 28.0, "temp_agua_min": 18.0, "temp_agua_max": 24.0,
                    "umidade_min": 60.0, "umidade_max": 80.0, "fotoperiodo_horas": foto
                }
                self.salvar_culturas_customizadas_disco()
                self.combo_cultura.configure(values=self.listar_todas_culturas())
                self.combo_cultura.set(nome)
                self.carregar_cultura(nome)
                self.atualizar_log_serial(f"[SUCESSO] Nova espécie '{nome}' cadastrada!\n")
                top.destroy()

        ctk.CTkButton(top, text="CADASTRAR ESPÉCIE", command=salvar, fg_color="#F59E0B", hover_color="#D97706", text_color="#02040A", height=40, font=("Segoe UI", 13, "bold"), corner_radius=6).pack(fill="x", padx=26, pady=10)

    def carregar_cultivo_salvo(self, nome_cultivo):
        if nome_cultivo in self.cultivos_salvos_cache:
            dados = self.cultivos_salvos_cache[nome_cultivo]
            cfg = self.horta.config
            cfg.nome_cultivo = nome_cultivo
            cfg.fase = dados.get("fase", "VEGETATIVO")
            
            cfg.fotoperiodo_horas = dados.get("fotoperiodo", 18.0)
            cfg.inicio_luz_hora = dados.get("hora", 6)
            cfg.inicio_luz_minuto = dados.get("minuto", 0)
            cfg.bomba_on_min = dados.get("bomba_on", 15)
            cfg.bomba_off_min = dados.get("bomba_off", 45)
            cfg.fan_exaustao_trigger = dados.get("fan_ex", 28.0)
            cfg.fan_insuflacao_trigger = dados.get("fan_in", 25.0)

            cfg.ph_min = dados.get("ph_min", 5.5); cfg.ph_max = dados.get("ph_max", 6.5)
            cfg.ec_min = dados.get("ec_min", 1.0); cfg.ec_max = dados.get("ec_max", 1.8)
            cfg.temperatura_ar_min = dados.get("temp_ar_min", 18.0); cfg.temperatura_ar_max = dados.get("temp_ar_max", 26.0)
            cfg.temperatura_agua_min = dados.get("temp_agua_min", 18.0); cfg.temperatura_agua_max = dados.get("temp_agua_max", 26.0)
            cfg.umidade_ar_min = dados.get("umidade_min", 50.0); cfg.umidade_ar_max = dados.get("umidade_max", 80.0)
            
            self.horta.nome_fertilizante = dados.get("fertilizante", "Flex Azul + Vermelho")
            self.horta.gramas_por_litro_recomendado = dados.get("taxa_ab", 0.84)

            self.preencher_configuracao()
            self.atualizar_interface()
            self.atualizar_log_serial(f"[INFO] Cultivo '{nome_cultivo}' carregado com sucesso!\n")

    def carregar_cultura(self, nome):
        try:
            cfg = self.horta.config
            if nome in self.culturas_customizadas_cache:
                d = self.culturas_customizadas_cache[nome]
                cfg.ph_min = d.get("ph_min", 5.5); cfg.ph_max = d.get("ph_max", 6.5)
                cfg.ec_min = d.get("ec_min", 1.0); cfg.ec_max = d.get("ec_max", 1.8)
                cfg.temperatura_ar_min = d.get("temp_ar_min", 18.0); cfg.temperatura_ar_max = d.get("temp_ar_max", 26.0)
                cfg.temperatura_agua_min = d.get("temp_agua_min", 18.0); cfg.temperatura_agua_max = d.get("temp_agua_max", 24.0)
                cfg.umidade_ar_min = d.get("umidade_min", 60.0); cfg.umidade_ar_max = d.get("umidade_max", 80.0)
                cfg.fotoperiodo_horas = d.get("fotoperiodo_horas", 18.0)
            else:
                cfg_cultura = obter_configuracao_cultura(nome)
                cfg.ph_min = cfg_cultura.ph_min; cfg.ph_max = cfg_cultura.ph_max
                cfg.ec_min = cfg_cultura.ec_min; cfg.ec_max = cfg_cultura.ec_max
                cfg.temperatura_ar_min = cfg_cultura.temperatura_ar_min; cfg.temperatura_ar_max = cfg_cultura.temperatura_ar_max
                cfg.temperatura_agua_min = cfg_cultura.temperatura_agua_min; cfg.temperatura_agua_max = cfg_cultura.temperatura_agua_max
                cfg.umidade_ar_min = cfg_cultura.umidade_ar_min; cfg.umidade_ar_max = cfg_cultura.umidade_ar_max
                cfg.fotoperiodo_horas = cfg_cultura.fotoperiodo_horas
            
            self.preencher_configuracao()
            self.horta.diagnosticar()
            self.atualizar_interface()
            self.atualizar_log_serial(f"[INFO] Espécie carregada: {nome} (Metas aplicadas)\n")
        except Exception as e: 
            self.atualizar_log_serial(f"[ERRO] Falha ao carregar espécie: {e}\n")

    def salvar_receita_local(self):
        try:
            cfg = self.coletar_dados_formulario()
            nome_cultivo = cfg.nome_cultivo
            
            self.cultivos_salvos_cache[nome_cultivo] = {
                "cultura": self.combo_cultura.get(), "fase": cfg.fase,
                "fotoperiodo": getattr(cfg, 'fotoperiodo_horas', 18.0), "hora": getattr(cfg, 'inicio_luz_hora', 6), "minuto": getattr(cfg, 'inicio_luz_minuto', 0),
                "bomba_on": getattr(cfg, 'bomba_on_min', 15), "bomba_off": getattr(cfg, 'bomba_off_min', 45),
                "fan_ex": getattr(cfg, 'fan_exaustao_trigger', 28.0), "fan_in": getattr(cfg, 'fan_insuflacao_trigger', 25.0),
                "ph_min": getattr(cfg, 'ph_min', 5.5), "ph_max": getattr(cfg, 'ph_max', 6.5), "ec_min": getattr(cfg, 'ec_min', 1.0), "ec_max": getattr(cfg, 'ec_max', 1.8),
                "temp_ar_min": getattr(cfg, 'temperatura_ar_min', 18.0), "temp_ar_max": getattr(cfg, 'temperatura_ar_max', 26.0),
                "temp_agua_min": getattr(cfg, 'temperatura_agua_min', 18.0), "temp_agua_max": getattr(cfg, 'temperatura_agua_max', 26.0),
                "umidade_min": getattr(cfg, 'umidade_ar_min', 50.0), "umidade_max": getattr(cfg, 'umidade_ar_max', 80.0),
                "fertilizante": self.horta.nome_fertilizante, "taxa_ab": self.horta.gramas_por_litro_recomendado
            }
            self.salvar_cultivos_disco()
            self.combo_cultivos_salvos.configure(values=list(self.cultivos_salvos_cache.keys()))
            self.combo_cultivos_salvos.set(nome_cultivo)

            self.horta.diagnosticar()
            self.atualizar_interface()
            self.atualizar_log_serial(f"[SUCESSO] Cultivo '{nome_cultivo}' salvo e aplicado localmente!\n")
        except Exception as e: self.atualizar_log_serial(f"[ERRO] Falha ao salvar cultivo: {e}\n")

    def sincronizar_receita_esp32(self):
        if not self.modo_hardware_real or not self.ser or not self.ser.is_open:
            top = ctk.CTkToplevel(self)
            top.title("Erro de Sincronização")
            top.geometry("420x200")
            top.attributes("-topmost", True)
            top.configure(fg_color="#050B14")
            top.grab_set()

            ctk.CTkLabel(top, text="❌ ESP32 DESCONECTADO", font=("Segoe UI", 14, "bold"), text_color="#EF4444").pack(pady=(22, 8))
            ctk.CTkLabel(top, text="Para sincronizar as configurações, ative o\n'Modo ESP32' no topo e certifique-se de\nque o hardware está conectado via USB.", font=("Segoe UI", 12), text_color="#CBD5E1", justify="center").pack(pady=(0, 16))
            ctk.CTkButton(top, text="ENTENDI", command=top.destroy, fg_color="#1E293B", hover_color="#334155", text_color="#F8FAFC", height=36, font=("Segoe UI", 12, "bold"), corner_radius=6).pack(fill="x", padx=28)
            
            self.atualizar_log_serial("[ERRO] Sincronização cancelada: ESP32 desconectado ou modo simulador ativo.\n")
            return

        try:
            cfg = self.coletar_dados_formulario()
            pacote_json = {
                "cmd": "set_config", "cultura": getattr(cfg, 'nome_cultivo', ''), "fase": getattr(cfg, 'fase', ''),
                "ph_min": getattr(cfg, 'ph_min', 0), "ph_max": getattr(cfg, 'ph_max', 0), "ec_min": getattr(cfg, 'ec_min', 0), "ec_max": getattr(cfg, 'ec_max', 0), 
                "temp_ar_max": getattr(cfg, 'temperatura_ar_max', 0), "fotoperiodo": getattr(cfg, 'fotoperiodo_horas', 0), "inicio_luz": getattr(cfg, 'inicio_luz_hora', 0),
                "fertilizante": self.horta.nome_fertilizante, "taxa_ab": self.horta.gramas_por_litro_recomendado
            }
            self.enviar_pacote_serial_raw(pacote_json)
            self.atualizar_log_serial("[SUCESSO] Parâmetros sincronizados com o ESP32 via Serial!\n")
        except Exception as e: 
            self.atualizar_log_serial(f"[ERRO] Falha ao sincronizar com ESP32: {e}\n")

    def enviar_pacote_serial_raw(self, dados_dict):
        if self.ser and self.ser.is_open:
            try:
                linha = json.dumps(dados_dict) + "\n"
                self.ser.write(linha.encode('utf-8'))
            except Exception as e: self.atualizar_log_serial(f"[ERRO] Falha ao enviar serial: {e}\n")
        else:
            self.atualizar_log_serial("[AVISO SERIAL] ESP32 não conectado. Comando simulado.\n")

    # ================= TELAS DE GRÁFICOS E CONFIG =================
    def criar_tela_graficos(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="g")
        frame.grid_rowconfigure((0, 1), weight=1)

        g1_frame = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        g1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        ctk.CTkLabel(g1_frame, text="EVOLUÇÃO DA SAÚDE BIOLÓGICA (%)", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(pady=(14, 0))
        self.fig1 = Figure(figsize=(5, 2.4), dpi=100)
        self.fig1.patch.set_facecolor('#050B14')
        self.ax1 = self.fig1.add_subplot(111)
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=g1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=10)

        g2_frame = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        g2_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        ctk.CTkLabel(g2_frame, text="DINÂMICA DE NUTRIÇÃO (pH & EC)", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(pady=(14, 0))
        self.fig2 = Figure(figsize=(5, 2.4), dpi=100)
        self.fig2.patch.set_facecolor('#050B14')
        self.ax2 = self.fig2.add_subplot(111)
        self.configurar_estilo_eixo(self.ax2, "pH / EC", 0, 14)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=g2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=10)

        g3_frame = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        g3_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        g3_topo = ctk.CTkFrame(g3_frame, fg_color="transparent")
        g3_topo.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(g3_topo, text="MONITORAMENTO TÉRMICO COMPARATIVO (AR vs ÁGUA)", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(side="left")
        ctk.CTkButton(g3_topo, text="📥 EXPORTAR LOGS (CSV)", command=self.exportar_logs_csv, height=36, width=190, fg_color="#0F172A", hover_color="#1E293B", text_color="#F8FAFC", font=("Segoe UI", 12, "bold"), corner_radius=6).pack(side="right")
        self.fig3 = Figure(figsize=(10, 2.2), dpi=100)
        self.fig3.patch.set_facecolor('#050B14')
        self.ax3 = self.fig3.add_subplot(111)
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=g3_frame)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=10)

        return frame

    def criar_tela_configuracao(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="conf")
        frame.grid_rowconfigure(0, weight=1)
        
        c_hw = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        c_hw.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(c_hw, text="GERENCIAMENTO DE HARDWARE", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(pady=(20, 16), anchor="w", padx=20)
        self.switch_hardware_cfg = ctk.CTkSwitch(c_hw, text=" Ativar Comunicação com ESP32 (USB)", command=lambda: self.sincronizar_chaves("config"), font=("Segoe UI", 13, "bold"), text_color="#F8FAFC", progress_color="#38BDF8")
        self.switch_hardware_cfg.pack(anchor="w", padx=20, pady=12)
        self.switch_hardware_cfg.deselect()
        ctk.CTkLabel(c_hw, text="Quando ativado, busca porta serial real do ESP32 (Azul). Quando desativado, o simulador assume o gêmeo digital (Laranja).", font=("Segoe UI", 12), text_color="#94A3B8", wraplength=460, justify="left").pack(anchor="w", padx=20, pady=12)

        c_ser = ctk.CTkFrame(frame, fg_color="#050B14", corner_radius=14, border_width=1, border_color="#1E293B")
        c_ser.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(c_ser, text="MONITOR DE COMUNICAÇÃO SERIAL (MATRIX)", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(pady=(20, 12), anchor="w", padx=20)
        self.serial_box_text = ctk.CTkTextbox(c_ser, fg_color="#000000", text_color="#00FF66", font=("Consolas", 13), corner_radius=8, border_width=1, border_color="#003311")
        self.serial_box_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.serial_box_text.insert("0.0", "[INFO] Sistema inicializado. Modo Gêmeo Digital / Simulador ativo.\n")
        self.serial_box_text.configure(state="disabled")

        return frame

    def configurar_estilo_eixo(self, ax, ylabel, ymin, ymax):
        ax.set_facecolor('#050B14')
        ax.tick_params(colors='#94A3B8', labelsize=11)
        ax.spines['bottom'].set_color('#1E293B')
        ax.spines['left'].set_color('#1E293B')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylabel(ylabel, color="#94A3B8", fontsize=11)
        ax.set_ylim(ymin, ymax)

    # ================= LOGICA DO ESP32 & SIMULADOR =================
    def sincronizar_chaves(self, origem):
        estado = self.switch_hardware_topo.get() if origem == "topo" else self.switch_hardware_cfg.get()
        if estado:
            self.switch_hardware_topo.select(); self.switch_hardware_cfg.select()
        else:
            self.switch_hardware_topo.deselect(); self.switch_hardware_cfg.deselect()
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
            if str(btn.cget("fg_color")) != "transparent": btn.configure(text_color=cor_tema)

        if self.modo_hardware_real:
            if self.demonstracao_ativa: self.alternar_demonstracao()
            self.label_status_esp.configure(text="● BUSCANDO ESP32...", text_color="#38BDF8")
            self.atualizar_log_serial("[INFO] Modo ESP32 ativado. Buscando dispositivo USB conectado...\n")
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
            self.atualizar_log_serial("[INFO] Modo Gêmeo Digital / Simulador ativado.\n")

    def tentar_conectar_esp_real(self):
        if not SERIAL_DISPONIVEL:
            self.label_status_esp.configure(text="● ERRO: PySerial Ausente", text_color="#EF4444")
            self.atualizar_log_serial("[ERRO] Biblioteca 'pyserial' não encontrada.\n")
            return

        def scan_e_conectar():
            portas = list(serial.tools.list_ports.comports())
            porta_encontrada = None
            
            for p in portas:
                desc = (p.description or "").upper()
                hwid = (p.hwid or "").upper()
                if any(x in desc or x in hwid for x in ["USB", "UART", "CH340", "CP210", "ESP32", "ARDUINO"]):
                    porta_encontrada = p.device
                    break
            
            if not porta_encontrada and len(portas) > 0: porta_encontrada = portas[0].device

            if porta_encontrada and self.modo_hardware_real:
                try:
                    self.ser = serial.Serial(porta_encontrada, 115200, timeout=1)
                    self.serial_thread_ativa = True
                    self.label_status_esp.configure(text=f"● ESP32 CONECTADO ({porta_encontrada})", text_color="#38BDF8")
                    self.atualizar_log_serial(f"[SUCESSO] Link estabelecido com ESP32 na porta física {porta_encontrada}\n")
                    
                    while self.serial_thread_ativa and self.ser and self.ser.is_open and self.modo_hardware_real:
                        linha = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if linha:
                            self.atualizar_log_serial(f"[ESP32] {linha}\n")
                            if linha.startswith("{") and linha.endswith("}"):
                                try:
                                    dados_esp = json.loads(linha)
                                    self.ultimo_valor_esp = dados_esp
                                    for k, v in [("temperatura_ar", self.horta.alterar_temperatura_ar), ("umidade_ar", self.horta.alterar_umidade_ar), ("temperatura_agua", self.horta.alterar_temperatura_agua), ("ph", self.horta.alterar_ph), ("ec", self.horta.alterar_ec), ("nivel_agua", self.horta.alterar_nivel_agua)]:
                                        if k in dados_esp: v(dados_esp[k])
                                except: pass
                except Exception as e:
                    self.label_status_esp.configure(text="● FALHA/DESCONEXÃO ESP32", text_color="#EF4444")
                    self.atualizar_log_serial(f"[ERRO SERIAL] Porta desconectada: {e}. Alternando para Simulador.\n")
                    self.after(0, lambda: self.switch_hardware_topo.deselect())
                    self.after(0, lambda: self.sincronizar_chaves("topo"))
            else:
                self.label_status_esp.configure(text="● NENHUM ESP32 DETECTADO", text_color="#EF4444")
                self.atualizar_log_serial("[AVISO] Nenhuma porta USB/Serial encontrada. Alternando para Simulador.\n")
                self.after(0, lambda: self.switch_hardware_topo.deselect())
                self.after(0, lambda: self.sincronizar_chaves("topo"))

        threading.Thread(target=scan_e_conectar, daemon=True).start()

    def fechar_conexao_serial(self):
        self.serial_thread_ativa = False
        if self.ser and self.ser.is_open:
            try: self.ser.close()
            except: pass

    def atualizar_log_serial(self, texto):
        self.log_serial_buffer.append(texto)
        if len(self.log_serial_buffer) > 120: self.log_serial_buffer.pop(0)
        try:
            self.serial_box_text.configure(state="normal")
            self.serial_box_text.delete("0.0", "end")
            self.serial_box_text.insert("0.0", "".join(self.log_serial_buffer))
            self.serial_box_text.see("end")
            self.serial_box_text.configure(state="disabled")
        except: pass

    # ================= CONTROLES MANUAIS (SLIM DESIGN) =================
    def mudar_temperatura_ar(self, v): self.horta.alterar_temperatura_ar(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_umidade_ar(self, v): self.horta.alterar_umidade_ar(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_temperatura_agua(self, v): self.horta.alterar_temperatura_agua(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_ph(self, v): self.horta.alterar_ph(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_ec(self, v): self.horta.alterar_ec(v); self.horta.diagnosticar(); self.atualizar_interface()
    def mudar_nivel_agua(self, v): self.horta.alterar_nivel_agua(v); self.horta.diagnosticar(); self.atualizar_interface()

    def criar_controle(self, parent, icone, nome, minimo, maximo, valor, callback, unidade):
        card = ctk.CTkFrame(parent, fg_color="#02040A", corner_radius=8, border_width=1, border_color="#1E293B")
        card.pack(fill="x", padx=10, pady=4)

        linha1 = ctk.CTkFrame(card, fg_color="transparent")
        linha1.pack(fill="x", padx=12, pady=(8, 0))

        ctk.CTkLabel(linha1, text=f"{icone} {nome}", font=("Segoe UI", 12, "bold"), text_color="#CBD5E1").pack(side="left")
        
        cor_valor = "#38BDF8" if self.modo_hardware_real else "#F59E0B"
        label = ctk.CTkLabel(linha1, text=f"{valor:.1f} {unidade}", font=("Segoe UI", 13, "bold"), text_color=cor_valor)
        label.pack(side="right")
        self.labels_valores[nome] = label

        cor_progresso = "#38BDF8" if self.modo_hardware_real else "#F59E0B"
        slider = ctk.CTkSlider(
            card, from_=minimo, to=maximo, number_of_steps=100, height=12,
            progress_color=cor_progresso, button_color="#F8FAFC", button_hover_color="#E2E8F0", fg_color="#1E293B"
        )
        slider.pack(fill="x", padx=12, pady=(4, 0))
        slider.set(valor)

        linha2 = ctk.CTkFrame(card, fg_color="transparent")
        linha2.pack(fill="x", padx=12, pady=(2, 8))
        lbl_meta = ctk.CTkLabel(linha2, text="Meta: --", font=("Segoe UI", 10), text_color="#64748B")
        lbl_meta.pack(side="left")
        self.labels_metas[nome] = lbl_meta

        def mover(valor_slider):
            if not self.modo_hardware_real:
                callback(float(valor_slider))
                label.configure(text=f"{float(valor_slider):.1f} {unidade}")

        slider.configure(command=mover)
        self.sliders[nome] = slider

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
            self.btn_pausa_tempo.configure(text="▶ INICIAR SIMULADOR", fg_color="#F59E0B", hover_color="#D97706", text_color="#02040A")

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
        
        self.historico_logs.clear(); self.historico_tempo.clear(); self.historico_saude_gem.clear()
        for k in self.historico_sinc:
            self.historico_sinc[k]["gem"].clear(); self.historico_sinc[k]["real"].clear()
        
        for k, v in [("Temperatura do ar", 24.5), ("Umidade do ar", 60.0), ("Temperatura da água", 22.0), ("pH", 6.0), ("EC", 1.4), ("Nível da água", 100.0)]:
            if k in self.sliders: self.sliders[k].set(v)
            if k == "Temperatura do ar": self.horta.alterar_temperatura_ar(v)
            elif k == "Umidade do ar": self.horta.alterar_umidade_ar(v)
            elif k == "Temperatura da água": self.horta.alterar_temperatura_agua(v)
            elif k == "pH": self.horta.alterar_ph(v)
            elif k == "EC": self.horta.alterar_ec(v)
            elif k == "Nível da água": self.horta.alterar_nivel_agua(v)

        for ax, canvas in [(self.ax1, self.canvas1), (self.ax2, self.canvas2), (self.ax3, self.canvas3), (self.ax_sinc, self.canvas_sinc)]:
            ax.clear(); canvas.draw()
        
        self.atualizar_interface()
        self.atualizar_log_serial("\n[SISTEMA] Cultivo resetado para o Dia 0.\n")

    def exportar_logs_csv(self):
        try:
            caminho_inicial = os.path.join(self.ultimo_caminho_exportacao, f"telemetria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            caminho = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Arquivo CSV (Excel)", "*.csv"), ("Todos os arquivos", "*.*")],
                initialfile=os.path.basename(caminho_inicial),
                initialdir=self.ultimo_caminho_exportacao,
                title="Salvar Relatório de Telemetria (CSV)"
            )
            if caminho:
                self.ultimo_caminho_exportacao = os.path.dirname(caminho)
                if self.historico_logs:
                    with open(caminho, "w", newline="", encoding="utf-8") as f:
                        w = csv.DictWriter(f, fieldnames=self.historico_logs[0].keys())
                        w.writeheader(); w.writerows(self.historico_logs)
                self.atualizar_log_serial(f"[SUCESSO] Relatório exportado para: {caminho}\n")
        except Exception as e:
            self.atualizar_log_serial(f"[ERRO] Falha ao exportar relatório: {e}\n")

    def persistir_log_automatico(self, registro):
        try:
            caminho_auto = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs_cultivo.csv")
            arquivo_existe = os.path.exists(caminho_auto)
            with open(caminho_auto, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=registro.keys())
                if not arquivo_existe:
                    w.writeheader()
                w.writerow(registro)
        except Exception:
            pass

    # ================= LOOP & ATUALIZAÇÃO =================
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

        registro_atual = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tempo": self.tempo_contador, "saude": dados["saude"],
            "temp_ar": dados["temperatura_ar"], "ph": dados["ph"], "ec": dados["ec"]
        }
        self.historico_logs.append(registro_atual)
        
        self.persistir_log_automatico(registro_atual)

        if len(self.historico_tempo) > 30:
            self.historico_tempo.pop(0); self.historico_saude_gem.pop(0)
            for k in self.historico_sinc:
                self.historico_sinc[k]["gem"].pop(0); self.historico_sinc[k]["real"].pop(0)

        cor_grafico = "#38BDF8" if self.modo_hardware_real else "#F59E0B"

        self.ax1.clear()
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.ax1.plot(self.historico_tempo, self.historico_saude_gem, color=cor_grafico, linewidth=2.5)
        self.canvas1.draw()

        self.ax2.clear()
        self.configurar_estilo_eixo(self.ax2, "pH / EC", 0, 14)
        self.ax2.plot(self.historico_tempo, self.historico_sinc["ph"]["gem"], color="#38BDF8", label="pH", linewidth=2)
        self.ax2.plot(self.historico_tempo, self.historico_sinc["ec"]["gem"], color="#FB923C", label="EC", linewidth=2)
        self.ax2.legend(loc="upper right", facecolor="#050B14", edgecolor="#1E293B", labelcolor="#F8FAFC", fontsize=10)
        self.canvas2.draw()

        self.ax3.clear()
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.ax3.plot(self.historico_tempo, self.historico_sinc["temp_ar"]["gem"], color="#EF4444", label="Ar", linewidth=2)
        self.ax3.plot(self.historico_tempo, self.historico_sinc["temp_agua"]["gem"], color="#2DD4BF", label="Água", linewidth=2)
        self.ax3.legend(loc="upper right", facecolor="#050B14", edgecolor="#1E293B", labelcolor="#F8FAFC", fontsize=10)
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
        self.ax_sinc.legend(loc="upper right", facecolor="#050B14", edgecolor="#1E293B", labelcolor="#F8FAFC", fontsize=10)
        self.canvas_sinc.draw()

    def atualizar_interface(self):
        self.horta.diagnosticar()
        dados = self.horta.snapshot()
        cfg = self.horta.config

        cultura_nome = getattr(cfg, 'nome_cultivo', 'Alface Experimental #01').upper()
        fase_atual = getattr(cfg, 'fase', 'VEGETATIVO')
        
        if self.modo_hardware_real:
            dia_exibicao = self.ultimo_valor_esp.get("dia_cultivo", 0)
            origem_tempo = "Hardware ESP32"
        else:
            dia_exibicao = self.dias_cultivo + getattr(cfg, 'dia_atual', 0)
            origem_tempo = "Simulador"
            
        self.label_sub_cultivo.configure(text=f"{cultura_nome} • Fase: {fase_atual} • Dia: {dia_exibicao} ({origem_tempo})")
        
        saude = dados['saude']
        self.label_saude_circulo.configure(text=f"{saude:.0f}%", text_color="#10B981" if saude > 80 else ("#F59E0B" if saude >= 40 else "#EF4444"))

        if saude < 40:
            self.card_saude_container.configure(border_color="#EF4444", border_width=2)
        elif saude <= 80:
            self.card_saude_container.configure(border_color="#F59E0B", border_width=2)
        else:
            self.card_saude_container.configure(border_color="#10B981", border_width=1)

        problemas = []
        if dados['ph'] < getattr(cfg, 'ph_min', 5.5): problemas.append(f"• pH baixo ({dados['ph']:.2f} < {cfg.ph_min})")
        elif dados['ph'] > getattr(cfg, 'ph_max', 6.5): problemas.append(f"• pH alto ({dados['ph']:.2f} > {cfg.ph_max})")
        if dados['ec'] < getattr(cfg, 'ec_min', 1.0): problemas.append(f"• EC baixa ({dados['ec']:.1f} < {cfg.ec_min})")
        elif dados['ec'] > getattr(cfg, 'ec_max', 1.8): problemas.append(f"• EC alta ({dados['ec']:.1f} > {cfg.ec_max})")
        if dados['temperatura_ar'] < getattr(cfg, 'temperatura_ar_min', 18): problemas.append(f"• Ar frio ({dados['temperatura_ar']:.1f}°C)")
        elif dados['temperatura_ar'] > getattr(cfg, 'temperatura_ar_max', 26): problemas.append(f"• Ar quente ({dados['temperatura_ar']:.1f}°C)")
        if dados['temperatura_agua'] < getattr(cfg, 'temperatura_agua_min', 18): problemas.append(f"• Água fria ({dados['temperatura_agua']:.1f}°C)")
        elif dados['temperatura_agua'] > getattr(cfg, 'temperatura_agua_max', 26): problemas.append(f"• Água quente ({dados['temperatura_agua']:.1f}°C)")
        if dados['nivel_agua'] < 20: problemas.append("• Reservatório baixo / Seco")

        fan_status = "OFF"; fan_color = "#94A3B8"
        if dados['temperatura_ar'] > getattr(cfg, 'temperatura_ar_max', 26): fan_status = "ON (Calor)"; fan_color = "#FB923C"
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
            self.labels_metas["Temperatura do ar"].configure(text=f"Meta: {getattr(cfg, 'temperatura_ar_min', 18)} a {getattr(cfg, 'temperatura_ar_max', 26)} °C")
            self.labels_metas["Umidade do ar"].configure(text=f"Meta: {getattr(cfg, 'umidade_ar_min', 50)} a {getattr(cfg, 'umidade_ar_max', 80)} %")
            self.labels_metas["Temperatura da água"].configure(text=f"Meta: {getattr(cfg, 'temperatura_agua_min', 18)} a {getattr(cfg, 'temperatura_agua_max', 26)} °C")
            self.labels_metas["pH"].configure(text=f"Meta: {getattr(cfg, 'ph_min', 5.5)} a {getattr(cfg, 'ph_max', 6.5)}")
            self.labels_metas["EC"].configure(text=f"Meta: {getattr(cfg, 'ec_min', 1.0)} a {getattr(cfg, 'ec_max', 1.8)} mS/cm")

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
        
        texto_relogio = f"{hora:02d}:{dados.get('minuto_atual', 0):02d}  15/09/2026" if self.demonstracao_ativa else datetime.now().strftime("%H:%M  %d/%m/%Y")
        self.label_relogio_topo.configure(text=texto_relogio)
        
        self.atualizar_graficos_avancados(dados, valores_reais)

    def ciclo_interface(self):
        if self.demonstracao_ativa: self.horta.tick_tempo()
        if self.automacao_ativa: self.horta.executar_automacao()
        self.atualizar_interface()
        self.after(1000, self.ciclo_interface)