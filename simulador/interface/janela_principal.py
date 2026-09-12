import customtkinter as ctk
import json
import os
import csv
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from modelo.horta import Horta
from modelo.configuracao import ConfiguracaoCultivo
from modelo.banco_cultivos import listar_culturas


class JanelaPrincipal(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.title("HORTA DO FUTURO — Digital Twin & Hardware Controller")
        self.geometry("1400x880")
        self.minsize(1150, 720)

        self.configure(fg_color="#1E2229")

        self.horta = Horta()
        self.automacao_ativa = True
        self.demonstracao_ativa = False
        self.modo_hardware_real = False

        self.historico_logs = []
        self.historico_saude = [100.0]
        self.historico_ph = [6.0]
        self.historico_ec = [1.4]
        self.historico_temp_ar = [24.5]
        self.historico_temp_agua = [22.0]
        self.historico_tempo = [0]
        self.tempo_contador = 0

        self.sliders = {}
        self.labels_valores = {}
        self.entries_config = {}

        self.criar_interface()
        self.atualizar_interface()

        self.after(1000, self.ciclo_interface)

    # ======================================================
    # INTERFACE PRINCIPAL & ABAS
    # ======================================================

    def criar_interface(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(14, 8))

        titulo_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        titulo_box.pack(side="left")

        titulo = ctk.CTkLabel(
            titulo_box,
            text="HORTA DO FUTURO",
            font=("Arial", 24, "bold"),
            text_color="#E2E8F0"
        )
        titulo.pack(side="left")

        subtitulo = ctk.CTkLabel(
            titulo_box,
            text="COMPUTADOR DE PLANTAS • DIGITAL TWIN",
            font=("Arial", 11, "bold"),
            text_color="#94A3B8"
        )
        subtitulo.pack(side="left", padx=14, pady=(5, 0))

        self.switch_hardware = ctk.CTkSwitch(
            header_frame,
            text=" MODO SENSOR FÍSICO (ESP32)",
            command=self.alternar_modo_hardware,
            font=("Arial", 11, "bold"),
            text_color="#A3E635",
            progress_color="#4E9F3D",
            button_color="#FFFFFF",
            button_hover_color="#E2E8F0"
        )
        self.switch_hardware.pack(side="right", padx=6)

        self.tabs = ctk.CTkTabview(
            self, 
            fg_color="#262B35", 
            segmented_button_fg_color="#1E2229", 
            segmented_button_selected_color="#3B7A57", 
            segmented_button_selected_hover_color="#2F6344",
            text_color="#E2E8F0"
        )
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(2, 16))

        self.tab_dashboard = self.tabs.add("🌱 MONITOR & SIMULADOR")
        self.tab_config = self.tabs.add("⚙ CONFIGURAÇÃO DA CULTURA")
        self.tab_graficos = self.tabs.add("📈 ANÁLISE & TELEMETRIA")

        self.criar_dashboard()
        self.criar_configuracao()
        self.criar_aba_graficos()

    # ======================================================
    # DASHBOARD (PRIMEIRA TELA)
    # ======================================================

    def criar_dashboard(self):
        painel = self.tab_dashboard

        painel.grid_columnconfigure(0, weight=1, uniform="col")
        painel.grid_columnconfigure(1, weight=1, uniform="col")
        painel.grid_columnconfigure(2, weight=1, uniform="col")
        painel.grid_rowconfigure(0, weight=1)

        # COLUNA 1: ESTADO BIOLÓGICO
        col1 = ctk.CTkFrame(
            painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846"
        )
        col1.grid(row=0, column=0, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(
            col1, text="ESTADO BIOLÓGICO", font=("Arial", 13, "bold"), text_color="#E2E8F0"
        ).pack(pady=(16, 6))

        self.label_cultivo = ctk.CTkLabel(
            col1, text="🌱 ALFACE", font=("Arial", 24, "bold"), text_color="#4E9F3D"
        )
        self.label_cultivo.pack(pady=2)

        self.label_nome_cultivo = ctk.CTkLabel(
            col1, text="Alface Experimental #01", font=("Arial", 12), text_color="#94A3B8"
        )
        self.label_nome_cultivo.pack()

        self.label_fase = ctk.CTkLabel(
            col1, text="VEGETATIVO", font=("Arial", 12, "bold"), text_color="#6B8E23"
        )
        self.label_fase.pack(pady=(2, 10))

        self.label_saude = ctk.CTkLabel(
            col1, text="SAÚDE: 100%", font=("Arial", 18, "bold"), text_color="#4E9F3D"
        )
        self.label_saude.pack(pady=(2, 4))

        self.barra_saude = ctk.CTkProgressBar(col1, width=220, height=14, progress_color="#4E9F3D", fg_color="#1E2229")
        self.barra_saude.pack(pady=(0, 10))
        self.barra_saude.set(1)

        self.label_alertas = ctk.CTkLabel(
            col1, text="✅ Condições ideais", font=("Arial", 11, "bold"), text_color="#A3E635", wraplength=220, justify="center"
        )
        self.label_alertas.pack(pady=(0, 12))

        ctk.CTkLabel(
            col1, text="RESERVATÓRIO DE ÁGUA", font=("Arial", 12, "bold"), text_color="#E2E8F0"
        ).pack(pady=(4, 2))

        self.label_nivel = ctk.CTkLabel(
            col1, text="100% — CHEIO", font=("Arial", 14, "bold"), text_color="#E2E8F0"
        )
        self.label_nivel.pack(pady=2)

        self.barra_agua = ctk.CTkProgressBar(col1, width=220, height=12, progress_color="#3D85C6", fg_color="#1E2229")
        self.barra_agua.pack(pady=(0, 12))
        self.barra_agua.set(1)

        ctk.CTkLabel(
            col1, text="RELÓGIO VIRTUAL", font=("Arial", 12, "bold"), text_color="#E2E8F0"
        ).pack(pady=(4, 2))

        self.label_relogio = ctk.CTkLabel(
            col1, text="13:00", font=("Arial", 32, "bold"), text_color="#4E9F3D"
        )
        self.label_relogio.pack(pady=2)

        self.label_periodo = ctk.CTkLabel(
            col1, text="💡 LUZ LIGADA", font=("Arial", 12, "bold"), text_color="#94A3B8"
        )
        self.label_periodo.pack(pady=(0, 14))

        # COLUNA 2: SENSORES VIRTUAIS
        col2 = ctk.CTkFrame(
            painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846"
        )
        col2.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(
            col2, text="SENSORES & AMBIENTE", font=("Arial", 13, "bold"), text_color="#E2E8F0"
        ).pack(pady=(16, 2))

        self.label_modo_telemetria = ctk.CTkLabel(
            col2, text="AJUSTE OS PARÂMETROS EM TEMPO REAL", font=("Arial", 10, "bold"), text_color="#94A3B8"
        )
        self.label_modo_telemetria.pack(pady=(0, 8))

        self.criar_controle(col2, "Temperatura do ar", 10, 40, self.horta.temperatura_ar, self.mudar_temperatura_ar, "°C")
        self.criar_controle(col2, "Umidade do ar", 0, 100, self.horta.umidade_ar, self.mudar_umidade_ar, "%")
        self.criar_controle(col2, "Temperatura da água", 5, 40, self.horta.temperatura_agua, self.mudar_temperatura_agua, "°C")
        self.criar_controle(col2, "pH", 2, 12, self.horta.ph, self.mudar_ph, "")
        self.criar_controle(col2, "EC", 0, 3, self.horta.ec, self.mudar_ec, "mS/cm")
        self.criar_controle(col2, "Nível da água", 0, 100, self.horta.nivel_agua, self.mudar_nivel_agua, "%")

        # COLUNA 3: TEMPO E SIMULAÇÃO
        col3 = ctk.CTkFrame(
            painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846"
        )
        col3.grid(row=0, column=2, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(
            col3, text="SIMULAÇÃO & TEMPO", font=("Arial", 13, "bold"), text_color="#E2E8F0"
        ).pack(pady=(16, 2))

        ctk.CTkLabel(
            col3, text="VELOCIDADE DA SIMULAÇÃO", font=("Arial", 10, "bold"), text_color="#94A3B8"
        ).pack(pady=(0, 2))

        self.label_velocidade = ctk.CTkLabel(
            col3, text="1x", font=("Arial", 20, "bold"), text_color="#4E9F3D"
        )
        self.label_velocidade.pack()

        self.slider_velocidade = ctk.CTkSlider(
            col3, from_=0, to=1440, number_of_steps=144, command=self.mudar_velocidade,
            progress_color="#4E9F3D", button_color="#4E9F3D", button_hover_color="#3B7A57", fg_color="#1E2229", height=16
        )
        self.slider_velocidade.pack(fill="x", padx=18, pady=4)
        self.slider_velocidade.set(1)

        self.label_explicacao_velocidade = ctk.CTkLabel(
            col3, text="1 min virtual / segundo", font=("Arial", 10), text_color="#94A3B8"
        )
        self.label_explicacao_velocidade.pack(pady=(0, 8))

        botoes_tempo_frame = ctk.CTkFrame(col3, fg_color="transparent")
        botoes_tempo_frame.pack(fill="x", padx=12, pady=2)

        botoes = [("−1h", -60), ("+10m", 10), ("+1h", 60), ("+10h", 600)]
        for texto, minutos in botoes:
            ctk.CTkButton(
                botoes_tempo_frame, text=texto, command=lambda m=minutos: self.avancar_tempo(m), height=30, width=50,
                fg_color="#323846", hover_color="#3F4656", text_color="#E2E8F0", font=("Arial", 11, "bold")
            ).pack(side="left", expand=True, padx=3)

        ctk.CTkLabel(
            col3, text="SISTEMAS AUTOMÁTICOS", font=("Arial", 12, "bold"), text_color="#E2E8F0"
        ).pack(pady=(12, 4))

        self.label_ventilacao = self.criar_status_atuador(col3, "VENTILAÇÃO")
        self.label_iluminacao = self.criar_status_atuador(col3, "ILUMINAÇÃO")

        self.botao_automacao = ctk.CTkButton(
            col3, text="AUTOMAÇÃO: LIGADA", command=self.alternar_automacao, height=34, width=210,
            fg_color="#3B7A57", hover_color="#2F6344", text_color="#FFFFFF", font=("Arial", 11, "bold")
        )
        self.botao_automacao.pack(pady=(6, 4))

        self.botao_demo = ctk.CTkButton(
            col3, text="▶ INICIAR SIMULAÇÃO", command=self.alternar_demonstracao, height=36, width=210,
            fg_color="#3B7A57", hover_color="#2F6344", text_color="#FFFFFF", font=("Arial", 11, "bold")
        )
        self.botao_demo.pack(pady=4)

        ctk.CTkButton(
            col3, text="🔄 RESETAR PLANTA", command=self.resetar, height=32, width=210,
            fg_color="#A93226", hover_color="#C0392B", text_color="#FFFFFF", font=("Arial", 11, "bold")
        ).pack(pady=(6, 8))

    # ======================================================
    # CONFIGURAÇÃO (SEGUNDA TELA EM 3 COLUNAS HARMONIOSAS)
    # ======================================================

    def criar_configuracao(self):
        painel = self.tab_config
        painel.grid_columnconfigure(0, weight=1, uniform="c")
        painel.grid_columnconfigure(1, weight=1, uniform="c")
        painel.grid_columnconfigure(2, weight=1, uniform="c")
        painel.grid_rowconfigure(0, weight=0)
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_rowconfigure(2, weight=0)

        ctk.CTkLabel(
            painel, text="PARÂMETROS E RECEITAS DE CULTIVO", font=("Arial", 16, "bold"), text_color="#E2E8F0"
        ).grid(row=0, column=0, columnspan=3, pady=(12, 8))

        # --- COLUNA 1: IDENTIDADE & FASE ---
        col1 = ctk.CTkFrame(painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846")
        col1.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(col1, text="IDENTIDADE DO CULTIVO", font=("Arial", 13, "bold"), text_color="#E2E8F0").pack(pady=(16, 8))

        ctk.CTkLabel(col1, text="Cultura cadastrada", text_color="#94A3B8", font=("Arial", 11, "bold")).pack(anchor="w", padx=16)
        self.combo_cultura = ctk.CTkComboBox(
            col1, values=listar_culturas(), command=self.carregar_cultura,
            fg_color="#1E2229", border_color="#323846", button_color="#323846", button_hover_color="#3B7A57", height=30, font=("Arial", 11)
        )
        self.combo_cultura.pack(fill="x", padx=16, pady=(2, 10))
        self.combo_cultura.set(self.horta.config.nome)

        ctk.CTkLabel(col1, text="Nome do Lote / Cultivo", text_color="#94A3B8", font=("Arial", 11, "bold")).pack(anchor="w", padx=16)
        self.entry_nome_cultivo = ctk.CTkEntry(col1, fg_color="#1E2229", border_color="#323846", height=30, font=("Arial", 11))
        self.entry_nome_cultivo.pack(fill="x", padx=16, pady=(2, 16))

        ctk.CTkLabel(col1, text="FASE DE DESENVOLVIMENTO", font=("Arial", 13, "bold"), text_color="#E2E8F0").pack(pady=(6, 8))

        ctk.CTkLabel(col1, text="Fase Atual", text_color="#94A3B8", font=("Arial", 11, "bold")).pack(anchor="w", padx=16)
        self.combo_fase = ctk.CTkComboBox(
            col1, values=["MUDA", "VEGETATIVO", "FLORAÇÃO / FRUTIFICAÇÃO"],
            command=self.ao_mudar_fase,
            fg_color="#1E2229", border_color="#323846", button_color="#323846", button_hover_color="#3B7A57", height=30, font=("Arial", 11)
        )
        self.combo_fase.pack(fill="x", padx=16, pady=(2, 10))
        self.combo_fase.set(self.horta.config.fase)

        # --- COLUNA 2: FOTOPERÍODO, LUZ & PWM ---
        col2 = ctk.CTkFrame(painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846")
        col2.grid(row=1, column=1, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(col2, text="FOTOPERÍODO & ILUMINAÇÃO", font=("Arial", 13, "bold"), text_color="#E2E8F0").pack(pady=(16, 8))

        linha_f1 = ctk.CTkFrame(col2, fg_color="transparent")
        linha_f1.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(linha_f1, text="Horas de luz / dia:", text_color="#94A3B8", font=("Arial", 11, "bold")).pack(side="left")
        self.entry_fotoperiodo = ctk.CTkEntry(linha_f1, width=70, fg_color="#1E2229", border_color="#323846", height=28, font=("Arial", 11))
        self.entry_fotoperiodo.pack(side="right")

        linha_f2 = ctk.CTkFrame(col2, fg_color="transparent")
        linha_f2.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(linha_f2, text="Início da luz (HH:MM):", text_color="#94A3B8", font=("Arial", 11, "bold")).pack(side="left")
        self.entry_inicio_minuto = ctk.CTkEntry(linha_f2, width=40, fg_color="#1E2229", border_color="#323846", height=28, font=("Arial", 11))
        self.entry_inicio_minuto.pack(side="right")
        ctk.CTkLabel(linha_f2, text=":", text_color="#94A3B8").pack(side="right", padx=2)
        self.entry_inicio_hora = ctk.CTkEntry(linha_f2, width=40, fg_color="#1E2229", border_color="#323846", height=28, font=("Arial", 11))
        self.entry_inicio_hora.pack(side="right")

        ctk.CTkLabel(col2, text="DIMMER PWM MAX (%)", font=("Arial", 11, "bold"), text_color="#94A3B8").pack(anchor="w", padx=16, pady=(14, 2))
        self.slider_dimmer = ctk.CTkSlider(
            col2, from_=10, to=100, number_of_steps=18, height=16, command=self.mudar_dimmer_manual,
            progress_color="#4E9F3D", button_color="#4E9F3D", button_hover_color="#3B7A57", fg_color="#1E2229"
        )
        self.slider_dimmer.pack(fill="x", padx=16, pady=(4, 10))
        self.slider_dimmer.set(100)

        # --- COLUNA 3: CONDIÇÕES IDEAIS & FERTILIZANTE ---
        col3 = ctk.CTkFrame(painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846")
        col3.grid(row=1, column=2, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(col3, text="CONDIÇÕES & NUTRIÇÃO", font=("Arial", 13, "bold"), text_color="#E2E8F0").pack(pady=(16, 4))

        campos = [
            ("pH mín / máx", "ph_min"), ("EC mín / máx (mS/cm)", "ec_min"),
            ("Temp. ar mín/máx (°C)", "temperatura_ar_min"), ("Temp. água mín/máx (°C)", "temperatura_agua_min"),
            ("Umidade mín/máx (%)", "umidade_ar_min")
        ]
        for titulo_campo, chave in campos:
            self.criar_campo_config(col3, titulo_campo, chave)

        nutricao_frame = ctk.CTkFrame(col3, corner_radius=8, fg_color="#1E2229", border_width=1, border_color="#323846")
        nutricao_frame.pack(fill="x", padx=12, pady=(8, 8))
        
        ctk.CTkLabel(nutricao_frame, text="🧪 FERTILIZANTE", font=("Arial", 10, "bold"), text_color="#A3E635").pack(pady=(4, 2))

        linha_ad = ctk.CTkFrame(nutricao_frame, fg_color="transparent")
        linha_ad.pack(fill="x", padx=8, pady=1)
        ctk.CTkLabel(linha_ad, text="Produto:", anchor="w", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(side="left")
        self.entry_nome_fertilizante = ctk.CTkEntry(linha_ad, width=110, fg_color="#262B35", border_color="#3B7A57", height=22, font=("Arial", 10))
        self.entry_nome_fertilizante.pack(side="right")

        self.entry_taxa_ab = self.criar_campo_nutricao(nutricao_frame, "g/L por +1.0 EC:")
        self.entry_taxa_ph_down = self.criar_campo_nutricao(nutricao_frame, "pH Down (mL/L):")
        self.entry_taxa_ph_up = self.criar_campo_nutricao(nutricao_frame, "pH Up (mL/L):")

        # --- BARRA INFERIOR DE AÇÕES ---
        botoes = ctk.CTkFrame(painel, fg_color="transparent")
        botoes.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(8, 14))

        ctk.CTkButton(
            botoes, text="➕ NOVA PLANTA", command=self.preparar_novo_cadastro, height=40,
            fg_color="#323846", hover_color="#3F4656", text_color="#E2E8F0", font=("Arial", 11, "bold")
        ).pack(side="left", expand=True, fill="x", padx=6)

        ctk.CTkButton(
            botoes, text="📡 APLICAR & SINCRONIZAR", command=self.aplicar_configuracao_interface, height=40,
            fg_color="#3B7A57", hover_color="#2F6344", text_color="#FFFFFF", font=("Arial", 11, "bold")
        ).pack(side="left", expand=True, fill="x", padx=6)

        ctk.CTkButton(
            botoes, text="💾 GRAVAR PARÂMETROS", command=self.salvar_receita, height=40,
            fg_color="#27AE60", hover_color="#219150", text_color="#FFFFFF", font=("Arial", 11, "bold")
        ).pack(side="left", expand=True, fill="x", padx=6)

        self.preencher_configuracao()

    # ======================================================
    # TERCEIRA ABA: GRÁFICOS AVANÇADOS & EXPORTAÇÃO DE LOGS
    # ======================================================

    def criar_aba_graficos(self):
        painel = self.tab_graficos
        painel.grid_columnconfigure(0, weight=1, uniform="g")
        painel.grid_columnconfigure(1, weight=1, uniform="g")
        painel.grid_rowconfigure(0, weight=1)
        painel.grid_rowconfigure(1, weight=1)
        painel.grid_rowconfigure(2, weight=0)

        # Gráfico 1: Saúde Biológica
        g1_frame = ctk.CTkFrame(painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846")
        g1_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(g1_frame, text="📈 EVOLUÇÃO DA SAÚDE BIOLÓGICA (%)", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(pady=(10, 2))
        
        self.fig1 = Figure(figsize=(5, 2.8), dpi=100)
        self.fig1.patch.set_facecolor('#262B35')
        self.ax1 = self.fig1.add_subplot(111)
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=g1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=8)

        # Gráfico 2: pH e EC (Nutrição)
        g2_frame = ctk.CTkFrame(painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846")
        g2_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(g2_frame, text="🧪 DINÂMICA DE NUTRIÇÃO (pH & EC)", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(pady=(10, 2))
        
        self.fig2 = Figure(figsize=(5, 2.8), dpi=100)
        self.fig2.patch.set_facecolor('#262B35')
        self.ax2 = self.fig2.add_subplot(111)
        self.configurar_estilo_eixo(self.ax2, "pH / EC", 0, 14)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=g2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=8)

        # Gráfico 3: Temperaturas (Ar vs Água)
        g3_frame = ctk.CTkFrame(painel, corner_radius=14, fg_color="#262B35", border_width=1, border_color="#323846")
        g3_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(g3_frame, text="🌡️ MONITORAMENTO TÉRMICO COMPARATIVO (AR vs ÁGUA)", font=("Arial", 12, "bold"), text_color="#E2E8F0").pack(pady=(10, 2))
        
        self.fig3 = Figure(figsize=(10, 2.2), dpi=100)
        self.fig3.patch.set_facecolor('#262B35')
        self.ax3 = self.fig3.add_subplot(111)
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=g3_frame)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=8)

        # --- BARRA INFERIOR DE EXPORTAÇÃO E LOGS EXTERNOS ---
        acoes_logs = ctk.CTkFrame(painel, fg_color="transparent")
        acoes_logs.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 10))

        self.label_status_log = ctk.CTkLabel(
            acoes_logs, text="ℹ️ Sistema pronto para exportar telemetria em formato aberto (CSV).", font=("Arial", 11), text_color="#94A3B8"
        )
        self.label_status_log.pack(side="left", padx=10)

        ctk.CTkButton(
            acoes_logs, text="📥 EXPORTAR LOGS (CSV)", command=self.exportar_logs_csv, height=36, width=220,
            fg_color="#3B7A57", hover_color="#2F6344", text_color="#FFFFFF", font=("Arial", 11, "bold")
        ).pack(side="right", padx=10)

    def configurar_estilo_eixo(self, ax, ylabel, ymin, ymax):
        ax.set_facecolor('#1E2229')
        ax.tick_params(colors='#94A3B8', labelsize=9)
        ax.spines['bottom'].set_color('#323846')
        ax.spines['left'].set_color('#323846')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylabel(ylabel, color="#94A3B8", fontsize=9)
        ax.set_ylim(ymin, ymax)

    def atualizar_graficos_avancados(self, dados):
        self.tempo_contador += 1
        self.historico_tempo.append(self.tempo_contador)
        self.historico_saude.append(dados["saude"])
        self.historico_ph.append(dados["ph"])
        self.historico_ec.append(dados["ec"])
        self.historico_temp_ar.append(dados["temperatura_ar"])
        self.historico_temp_agua.append(dados["temperatura_agua"])

        self.historico_logs.append({
            "tempo_virtual_min": self.tempo_contador,
            "hora_sistema": f"{dados['hora_atual']:02d}:{dados['minuto_atual']:02d}",
            "cultivo": dados["cultivo"],
            "fase": dados["fase"],
            "saude_pct": dados["saude"],
            "status_planta": dados["status"],
            "temperatura_ar_C": dados["temperatura_ar"],
            "umidade_ar_pct": dados["umidade_ar"],
            "temperatura_agua_C": dados["temperatura_agua"],
            "ph": dados["ph"],
            "ec_mS_cm": dados["ec"],
            "nivel_agua_pct": dados["nivel_agua"]
        })

        if len(self.historico_tempo) > 40:
            self.historico_tempo.pop(0)
            self.historico_saude.pop(0)
            self.historico_ph.pop(0)
            self.historico_ec.pop(0)
            self.historico_temp_ar.pop(0)
            self.historico_temp_agua.pop(0)

        # Atualiza Gráfico 1 (Saúde)
        self.ax1.clear()
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        cor_s = "#4E9F3D" if dados['saude'] > 60 else ("#F1C40F" if dados['saude'] > 25 else "#E74C3C")
        self.ax1.plot(self.historico_tempo, self.historico_saude, color=cor_s, linewidth=2.5, marker='o', markersize=3)
        self.canvas1.draw()

        # Atualiza Gráfico 2 (pH & EC)
        self.ax2.clear()
        self.configurar_estilo_eixo(self.ax2, "Valores", 0, 14)
        self.ax2.plot(self.historico_tempo, self.historico_ph, color="#3498DB", linewidth=2, label="pH")
        self.ax2.plot(self.historico_tempo, self.historico_ec, color="#E67E22", linewidth=2, label="EC (mS/cm)")
        self.ax2.legend(loc="upper right", facecolor="#1E2229", edgecolor="#323846", labelcolor="#E2E8F0", fontsize=8)
        self.canvas2.draw()

        # Atualiza Gráfico 3 (Temperaturas)
        self.ax3.clear()
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.ax3.plot(self.historico_tempo, self.historico_temp_ar, color="#E74C3C", linewidth=2, label="Temp. Ar (°C)")
        self.ax3.plot(self.historico_tempo, self.historico_temp_agua, color="#1ABC9C", linewidth=2, label="Temp. Água (°C)")
        self.ax3.legend(loc="upper right", facecolor="#1E2229", edgecolor="#323846", labelcolor="#E2E8F0", fontsize=8)
        self.canvas3.draw()

    def exportar_logs_csv(self):
        try:
            if not self.historico_logs:
                self.label_status_log.configure(text="⚠️ Nenhum dado histórico registrado para exportar.", text_color="#E74C3C")
                return

            pasta_logs = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
            )
            os.makedirs(pasta_logs, exist_ok=True)

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_csv = os.path.join(pasta_logs, f"telemetria_horta_{timestamp_str}.csv")

            chaves = self.historico_logs[0].keys()
            with open(caminho_csv, mode="w", newline="", encoding="utf-8") as arquivo_csv:
                escritor = csv.DictWriter(arquivo_csv, fieldnames=chaves)
                escritor.writeheader()
                for linha in self.historico_logs:
                    escritor.writerow(linha)

            self.label_status_log.configure(
                text=f"✅ Log exportado com sucesso: logs/telemetria_horta_{timestamp_str}.csv", text_color="#A3E635"
            )
        except Exception as e:
            self.label_status_log.configure(text=f"❌ Erro ao exportar CSV: {e}", text_color="#E74C3C")

    # ======================================================
    # AUXILIARES E CALLBACKS
    # ======================================================

    def criar_campo_config(self, parent, titulo, chave):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(linha, text=titulo, anchor="w", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(side="left")
        entry = ctk.CTkEntry(linha, width=55, fg_color="#1E2229", border_color="#323846", height=22, font=("Arial", 10))
        entry.pack(side="right")
        self.entries_config[chave] = entry

    def criar_campo_nutricao(self, parent, titulo):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=8, pady=1)

        ctk.CTkLabel(linha, text=titulo, anchor="w", font=("Arial", 10, "bold"), text_color="#94A3B8").pack(side="left")
        entry = ctk.CTkEntry(linha, width=55, fg_color="#262B35", border_color="#3B7A57", height=22, font=("Arial", 10))
        entry.pack(side="right")
        return entry

    def criar_controle(self, parent, nome, minimo, maximo, valor, callback, unidade):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=14, pady=4)

        linha = ctk.CTkFrame(frame, fg_color="transparent")
        linha.pack(fill="x", padx=2, pady=(2, 2))

        ctk.CTkLabel(linha, text=nome, font=("Arial", 11, "bold"), text_color="#E2E8F0").pack(side="left")
        label = ctk.CTkLabel(linha, text=f"{valor:.1f} {unidade}", font=("Arial", 12, "bold"), text_color="#4E9F3D")
        label.pack(side="right")
        self.labels_valores[nome] = label

        slider = ctk.CTkSlider(
            frame, from_=minimo, to=maximo, number_of_steps=100, height=16,
            progress_color="#4E9F3D", button_color="#4E9F3D", button_hover_color="#3B7A57", fg_color="#1E2229"
        )
        slider.pack(fill="x", padx=2, pady=(2, 4))
        slider.set(valor)

        def mover(valor_slider):
            if not self.modo_hardware_real:
                callback(float(valor_slider))
                label.configure(text=f"{float(valor_slider):.1f} {unidade}")

        slider.configure(command=mover)
        self.sliders[nome] = slider

    def criar_status_atuador(self, parent, nome):
        label = ctk.CTkLabel(parent, text=f"{nome}: DESLIGADA", font=("Arial", 11, "bold"), text_color="#94A3B8")
        label.pack(pady=3)
        return label

    def preencher_configuracao(self):
        config = self.horta.config
        valores = config.snapshot()

        for chave, entry in self.entries_config.items():
            entry.delete(0, "end")
            entry.insert(0, str(valores[chave]))

        self.entry_nome_cultivo.delete(0, "end")
        self.entry_nome_cultivo.insert(0, config.nome_cultivo)
        self.combo_fase.set(config.fase)
        self.label_fase.configure(text=config.fase)

        self.entry_fotoperiodo.delete(0, "end")
        self.entry_fotoperiodo.insert(0, str(config.fotoperiodo_horas))
        self.entry_inicio_hora.delete(0, "end")
        self.entry_inicio_hora.insert(0, f"{config.inicio_luz_hora:02d}")
        self.entry_inicio_minuto.delete(0, "end")
        self.entry_inicio_minuto.insert(0, f"{config.inicio_luz_minuto:02d}")

        self.entry_nome_fertilizante.delete(0, "end")
        self.entry_nome_fertilizante.insert(0, self.horta.nome_fertilizante)

        self.entry_taxa_ab.delete(0, "end")
        self.entry_taxa_ab.insert(0, str(self.horta.gramas_por_litro_recomendado))
        
        self.entry_taxa_ph_down.delete(0, "end")
        self.entry_taxa_ph_down.insert(0, str(self.horta.taxa_ph_down))
        
        self.entry_taxa_ph_up.delete(0, "end")
        self.entry_taxa_ph_up.insert(0, str(self.horta.taxa_ph_up))

        self.slider_dimmer.set(self.horta.dimmer_manual_nivel)

    def ao_mudar_fase(self, nova_fase):
        nova_fase = str(nova_fase).upper()
        if "MUDA" in nova_fase:
            horas_sugeridas = "18.0"
        elif "VEGETATIVO" in nova_fase:
            horas_sugeridas = "18.0"
        elif "FLORAÇÃO" in nova_fase or "FRUTIFICAÇÃO" in nova_fase:
            horas_sugeridas = "12.0"
        else:
            horas_sugeridas = "16.0"

        if hasattr(self, 'entry_fotoperiodo'):
            self.entry_fotoperiodo.delete(0, "end")
            self.entry_fotoperiodo.insert(0, horas_sugeridas)

        self.label_fase.configure(text=nova_fase)

    def preparar_novo_cadastro(self):
        self.combo_cultura.set("NOVA_CULTURA")
        self.entry_nome_cultivo.delete(0, "end")
        self.entry_nome_cultivo.insert(0, "Cultivo Experimental #01")
        self.combo_fase.set("VEGETATIVO")
        self.label_fase.configure(text="VEGETATIVO")

        padroes = {
            "ph_min": "5.5", "ph_max": "6.5",
            "ec_min": "1.0", "ec_max": "2.0",
            "temperatura_ar_min": "18.0", "temperatura_ar_max": "28.0",
            "temperatura_agua_min": "18.0", "temperatura_agua_max": "24.0",
            "umidade_ar_min": "50.0", "umidade_ar_max": "80.0"
        }
        for chave, entry in self.entries_config.items():
            entry.delete(0, "end")
            entry.insert(0, padroes.get(chave, "0.0"))

        self.entry_fotoperiodo.delete(0, "end")
        self.entry_fotoperiodo.insert(0, "18.0")
        self.entry_inicio_hora.delete(0, "end")
        self.entry_inicio_hora.insert(0, "06")
        self.entry_inicio_minuto.delete(0, "end")
        self.entry_inicio_minuto.insert(0, "00")

    def carregar_cultura(self, nome):
        try:
            self.horta.selecionar_cultura(nome)
            self.preencher_configuracao()
            self.atualizar_interface()
        except Exception as erro:
            print("Erro ao carregar cultura:", erro)

    def aplicar_configuracao_interface(self):
        try:
            valores = {}
            for chave, entry in self.entries_config.items():
                valores[chave] = float(entry.get())

            config = ConfiguracaoCultivo(
                nome=self.combo_cultura.get(),
                nome_cultivo=self.entry_nome_cultivo.get() or "Cultivo #01",
                fase=self.combo_fase.get(),
                ph_min=valores["ph_min"], ph_max=valores["ph_max"],
                ec_min=valores["ec_min"], ec_max=valores["ec_max"],
                temperatura_ar_min=valores["temperatura_ar_min"], temperatura_ar_max=valores["temperatura_ar_max"],
                temperatura_agua_min=valores["temperatura_agua_min"], temperatura_agua_max=valores["temperatura_agua_max"],
                umidade_ar_min=valores["umidade_ar_min"], umidade_ar_max=valores["umidade_ar_max"],
                fotoperiodo_horas=float(self.entry_fotoperiodo.get()),
                inicio_luz_hora=int(self.entry_inicio_hora.get()),
                inicio_luz_minuto=int(self.entry_inicio_minuto.get())
            )

            self.horta.nome_fertilizante = self.entry_nome_fertilizante.get() or "Nutriente Padrão"
            self.horta.gramas_por_litro_recomendado = float(self.entry_taxa_ab.get())
            self.horta.taxa_ph_down = float(self.entry_taxa_ph_down.get())
            self.horta.taxa_ph_up = float(self.entry_taxa_ph_up.get())

            enviar_esp = self.modo_hardware_real
            self.horta.aplicar_configuracao(config, enviar_para_esp32=enviar_esp)
            
            self.label_fase.configure(text=config.fase)
            self.atualizar_interface()
        except Exception as erro:
            print("ERRO NA CONFIGURAÇÃO:", erro)

    def salvar_receita(self):
        try:
            self.aplicar_configuracao_interface()
            dados = self.horta.config.snapshot()
            
            pasta = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "receitas"
            )
            os.makedirs(pasta, exist_ok=True)
            
            nome_planta = self.combo_cultura.get().strip().upper().replace(" ", "_")
            if not nome_planta:
                nome_planta = "CULTURA_CUSTOM"

            caminho = os.path.join(pasta, f"{nome_planta.lower()}.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=4)

            culturas_atualizadas = listar_culturas()
            if nome_planta not in culturas_atualizadas:
                culturas_atualizadas.append(nome_planta)
            self.combo_cultura.configure(values=culturas_atualizadas)
            self.combo_cultura.set(nome_planta)
            
        except Exception as erro:
            print("ERRO AO GRAVAR RECEITA:", erro)

    def mudar_dimmer_manual(self, valor):
        self.horta.modo_dimmer_manual = True
        self.horta.alterar_dimmer(float(valor))
        self.horta.atualizar_fotoperiodo()

    def alternar_modo_hardware(self):
        self.modo_hardware_real = self.switch_hardware.get() == 1
        estado_sliders = "disabled" if self.modo_hardware_real else "normal"
        for slider in self.sliders.values():
            slider.configure(state=estado_sliders)

        if self.modo_hardware_real:
            self.label_modo_telemetria.configure(text="🛰️ DADOS VINDOS DO ESP32 (TEMPO REAL)", text_color="#4E9F3D")
        else:
            self.label_modo_telemetria.configure(text="AJUSTE OS PARÂMETROS EM TEMPO REAL", text_color="#94A3B8")

    def mudar_temperatura_ar(self, valor):
        self.horta.alterar_temperatura_ar(valor)
        self.horta.diagnosticar()

    def mudar_umidade_ar(self, valor):
        self.horta.alterar_umidade_ar(valor)
        self.horta.diagnosticar()

    def mudar_temperatura_agua(self, valor):
        self.horta.alterar_temperatura_agua(valor)
        self.horta.diagnosticar()

    def mudar_ph(self, valor):
        self.horta.alterar_ph(valor)
        self.horta.diagnosticar()

    def mudar_ec(self, valor):
        self.horta.alterar_ec(valor)
        self.horta.diagnosticar()

    def mudar_nivel_agua(self, valor):
        self.horta.alterar_nivel_agua(valor)
        self.horta.diagnosticar()

    def alternar_automacao(self):
        self.automacao_ativa = not self.automacao_ativa
        self.botao_automacao.configure(
            text="AUTOMAÇÃO: LIGADA" if self.automacao_ativa else "AUTOMAÇÃO: DESLIGADA",
            fg_color="#3B7A57" if self.automacao_ativa else "#323846",
            text_color="#FFFFFF" if self.automacao_ativa else "#94A3B8"
        )

    def mudar_velocidade(self, valor):
        valor = float(valor)
        self.horta.configurar_velocidade_tempo(valor)

        if valor <= 0:
            texto, explicacao = "PAUSADO", "Relógio parado"
        elif valor < 60:
            texto, explicacao = f"{valor:.0f}x", f"{valor:.0f} min virtuais / segundo"
        elif valor % 60 == 0:
            horas = valor / 60
            texto, explicacao = f"{valor:.0f}x", f"{horas:g} hora(s) virtual(is) / seg"
        else:
            texto, explicacao = f"{valor:.0f}x", f"{valor:.0f} min virtuais / segundo"

        self.label_velocidade.configure(text=texto)
        self.label_explicacao_velocidade.configure(text=explicacao)

    def alternar_demonstracao(self):
        self.demonstracao_ativa = not self.demonstracao_ativa
        if self.demonstracao_ativa:
            self.botao_demo.configure(text="■ PAUSAR SIMULAÇÃO", fg_color="#C0392B", hover_color="#A93226", text_color="#FFFFFF")
        else:
            self.botao_demo.configure(text="▶ INICIAR SIMULAÇÃO", fg_color="#3B7A57", hover_color="#2F6344", text_color="#FFFFFF")

    def avancar_tempo(self, minutos):
        self.horta.avancar_tempo(minutos)
        self.atualizar_interface()

    def resetar(self):
        self.horta.resetar()
        self.atualizar_sliders()
        self.atualizar_interface()

    def atualizar_sliders(self):
        valores = {
            "Temperatura do ar": self.horta.temperatura_ar,
            "Umidade do ar": self.horta.umidade_ar,
            "Temperatura da água": self.horta.temperatura_agua,
            "pH": self.horta.ph,
            "EC": self.horta.ec,
            "Nível da água": self.horta.nivel_agua
        }
        for nome, valor in valores.items():
            if nome in self.sliders:
                self.sliders[nome].set(valor)

    def atualizar_interface(self):
        dados = self.horta.snapshot()

        self.label_cultivo.configure(text=f"🌱 {dados['cultivo']}")
        self.label_nome_cultivo.configure(text=dados["nome_cultivo"])
        self.label_fase.configure(text=dados["fase"])
        
        cor_saude = "#4E9F3D" if dados['saude'] > 60 else ("#F1C40F" if dados['saude'] > 25 else "#E74C3C")
        self.label_saude.configure(text=f"SAÚDE: {dados['saude']:.0f}% ({dados['status']})", text_color=cor_saude)
        self.barra_saude.configure(progress_color=cor_saude)
        self.barra_saude.set(dados["saude"] / 100)

        if dados["alertas"]:
            self.label_alertas.configure(text="\n".join(dados["alertas"]), text_color="#E74C3C")
        else:
            self.label_alertas.configure(text="✅ Condições ideais de cultivo", text_color="#A3E635")

        self.label_nivel.configure(
            text=f"{dados['nivel_agua']:.0f}% — {dados['nivel_agua_status']}"
        )
        self.barra_agua.set(dados["nivel_agua"] / 100)

        hora = f"{dados['hora_atual']:02d}:{dados['minuto_atual']:02d}"
        self.label_relogio.configure(text=hora)

        self.label_periodo.configure(
            text="💡 LUZ LIGADA" if dados["periodo_luz"] else "🌙 LUZ DESLIGADA"
        )
        
        self.label_ventilacao.configure(
            text="VENTILAÇÃO: LIGADA" if dados["ventilacao"] else "VENTILAÇÃO: DESLIGADA",
            text_color="#4E9F3D" if dados["ventilacao"] else "#94A3B8"
        )
        
        if dados.get("iluminacao"):
            pwm_val = dados.get("intensidade_iluminacao_pwm", 100)
            self.label_iluminacao.configure(
                text=f"ILUMINAÇÃO PWM: {pwm_val}%",
                text_color="#F1C40F"
            )
        else:
            self.label_iluminacao.configure(
                text="ILUMINAÇÃO: DESLIGADA",
                text_color="#94A3B8"
            )

        if self.modo_hardware_real:
            self.atualizar_sliders()

        self.atualizar_graficos_avancados(dados)

    def ciclo_interface(self):
        if self.demonstracao_ativa:
            self.horta.tick_tempo()
        if self.automacao_ativa:
            self.horta.executar_automacao()
        self.atualizar_interface()
        self.after(1000, self.ciclo_interface)