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

# Tenta importar pyserial para comunicação com ESP32 real
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
        ctk.set_default_color_theme("green")

        self.title("HORTA DO FUTURO — Digital Twin & Hardware Controller")
        self.geometry("1420x880")
        self.minsize(1150, 750)

        # Fundo principal Preto Profundo (Carbon Black)
        self.configure(fg_color="#05070B")

        self.horta = Horta()
        self.automacao_ativa = True
        self.demonstracao_ativa = False
        self.modo_hardware_real = False
        
        # Variáveis de controle serial
        self.ser = None
        self.serial_thread_ativa = False
        self.log_serial_buffer = ["[INFO] Sistema pronto. Aguardando conexão ESP32...\n"]

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
        self.botoes_sidebar = {}

        self.criar_interface()
        self.atualizar_interface()

        self.after(1000, self.ciclo_interface)

    # ======================================================
    # ARQUITETURA PRINCIPAL (SIDEBAR + CONTEÚDO DINÂMICO)
    # ======================================================

    def criar_interface(self):
        # 1. BARRA LATERAL FIXA (SIDEBAR)
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color="#090E17", corner_radius=0, border_width=1, border_color="#131D31")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Topo da Sidebar
        topo_sidebar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        topo_sidebar.pack(fill="x", padx=20, pady=24)

        ctk.CTkLabel(
            topo_sidebar, text="HORTA DO FUTURO", font=("Segoe UI", 18, "bold"), text_color="#10B981"
        ).pack(anchor="w")
        ctk.CTkLabel(
            topo_sidebar, text="DIGITAL TWIN V1.0", font=("Segoe UI", 11, "bold"), text_color="#64748B"
        ).pack(anchor="w", pady=(2, 0))

        # Navegação
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=10)

        self.botoes_sidebar = {}
        itens_menu = [
            ("dashboard", "📊  Painel & Controles"),
            ("nutricao", "🌱  Receitas & Cultivo"),
            ("graficos", "📈  Gráficos & Logs"),
            ("config", "⚙️  Configurações ESP32")
        ]

        for chave, texto in itens_menu:
            btn = ctk.CTkButton(
                nav_frame, text=texto, anchor="w", height=44,
                fg_color="transparent", text_color="#94A3B8",
                hover_color="#131D31", font=("Segoe UI", 13, "bold"),
                command=lambda c=chave: self.trocar_tela(c)
            )
            btn.pack(fill="x", pady=4)
            self.botoes_sidebar[chave] = btn

        # PAINEL DO SIMULADOR (FIXO NA LATERAL)
        sim_box = ctk.CTkFrame(self.sidebar, fg_color="#0D1322", corner_radius=12, border_width=1, border_color="#1E293B")
        sim_box.pack(side="bottom", fill="x", padx=14, pady=14)

        ctk.CTkLabel(sim_box, text="CONTROLE DO SIMULADOR", font=("Segoe UI", 11, "bold"), text_color="#10B981").pack(anchor="w", padx=14, pady=(12, 4))
        
        vel_box = ctk.CTkFrame(sim_box, fg_color="transparent")
        vel_box.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(vel_box, text="Velocidade:", font=("Segoe UI", 12), text_color="#E2E8F0").pack(side="left")
        self.label_vel_sidebar = ctk.CTkLabel(vel_box, text="1x", font=("Segoe UI", 12, "bold"), text_color="#10B981")
        self.label_vel_sidebar.pack(side="right")

        self.slider_vel_sidebar = ctk.CTkSlider(
            sim_box, from_=1, to=10, number_of_steps=9, command=self.mudar_velocidade,
            progress_color="#059669", button_color="#FFFFFF", button_hover_color="#E2E8F0", fg_color="#05070B", height=14
        )
        self.slider_vel_sidebar.pack(fill="x", padx=14, pady=6)
        self.slider_vel_sidebar.set(1)

        botoes_tempo_frame = ctk.CTkFrame(sim_box, fg_color="transparent")
        botoes_tempo_frame.pack(fill="x", padx=12, pady=4)

        botoes_t = [("+1m", 1), ("+5m", 5), ("+30m", 30), ("+1h", 60)]
        for texto, minutos in botoes_t:
            ctk.CTkButton(
                botoes_tempo_frame, text=texto, command=lambda m=minutos: self.avancar_tempo(m), height=26, width=42,
                fg_color="#1E293B", hover_color="#334155", text_color="#FFFFFF", font=("Segoe UI", 11, "bold"), corner_radius=6
            ).pack(side="left", expand=True, padx=2)

        self.btn_pausa_tempo = ctk.CTkButton(
            sim_box, text="▶ INICIAR TEMPO", command=self.alternar_demonstracao, height=34,
            fg_color="#059669", hover_color="#047857", text_color="#FFFFFF", font=("Segoe UI", 12, "bold")
        )
        self.btn_pausa_tempo.pack(fill="x", padx=14, pady=(8, 12))

        # 2. ÁREA DE CONTEÚDO PRINCIPAL (DIREITA)
        self.main_container = ctk.CTkFrame(self, fg_color="#05070B", corner_radius=0)
        self.main_container.pack(side="right", fill="both", expand=True)

        # Header Superior
        self.header = ctk.CTkFrame(self.main_container, height=64, fg_color="#090E17", corner_radius=0, border_width=1, border_color="#131D31")
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        header_content = ctk.CTkFrame(self.header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24)

        status_box = ctk.CTkFrame(header_content, fg_color="transparent")
        status_box.pack(side="left", fill="y")
        
        self.label_status_esp = ctk.CTkLabel(
            status_box, text="● DIGITAL TWIN SIMULADO", font=("Segoe UI", 12, "bold"), text_color="#38BDF8"
        )
        self.label_status_esp.pack(side="left")

        self.label_relogio_topo = ctk.CTkLabel(
            header_content, text="13:00  12/09/2026", font=("Segoe UI", 14, "bold"), text_color="#E2E8F0"
        )
        self.label_relogio_topo.pack(side="right")

        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=24, pady=24)

        # Instancia as telas
        self.telas = {}
        self.telas["dashboard"] = self.criar_tela_dashboard()
        self.telas["nutricao"] = self.criar_tela_nutricao()
        self.telas["graficos"] = self.criar_tela_graficos()
        self.telas["config"] = self.criar_tela_configuracao()

        self.trocar_tela("dashboard")

    def trocar_tela(self, nome):
        for tela in self.telas.values():
            tela.pack_forget()
        self.telas[nome].pack(fill="both", expand=True)

        for chave, btn in self.botoes_sidebar.items():
            if chave == nome:
                btn.configure(fg_color="#131D31", text_color="#10B981")
            else:
                btn.configure(fg_color="transparent", text_color="#94A3B8")

    # ======================================================
    # TELA 1: DASHBOARD & CONTROLES EM TEMPO REAL
    # ======================================================

    def criar_tela_dashboard(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")

        titulo_box = ctk.CTkFrame(frame, fg_color="transparent")
        titulo_box.pack(fill="x", pady=(0, 14))
        
        ctk.CTkLabel(titulo_box, text="Painel Geral & Gêmeo Digital", font=("Segoe UI", 24, "bold"), text_color="#FFFFFF").pack(anchor="w")
        self.label_sub_cultivo = ctk.CTkLabel(titulo_box, text="Alface Experimental #01 • Fase: VEGETATIVO", font=("Segoe UI", 13), text_color="#94A3B8")
        self.label_sub_cultivo.pack(anchor="w", pady=(2, 0))

        grid_principal = ctk.CTkFrame(frame, fg_color="transparent")
        grid_principal.pack(fill="both", expand=True, pady=(0, 10))
        grid_principal.grid_columnconfigure(0, weight=6, uniform="dash")
        grid_principal.grid_columnconfigure(1, weight=5, uniform="dash")
        grid_principal.grid_rowconfigure(0, weight=1)

        # COLUNA ESQUERDA: STATUS E DIAGNÓSTICO DETALHADO DE PROBLEMAS
        col_esq = ctk.CTkFrame(grid_principal, fg_color="transparent")
        col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        col_esq.grid_rowconfigure((0, 1, 2), weight=1)
        col_esq.grid_columnconfigure(0, weight=1)

        # Card 1: Saúde & Diagnóstico Inteligente
        c1 = ctk.CTkFrame(col_esq, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        c1.grid(row=0, column=0, sticky="nsew", pady=4)
        
        ctk.CTkLabel(c1, text="SAÚDE BIOLÓGICA & DIAGNÓSTICO", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(12, 2))
        
        box_status = ctk.CTkFrame(c1, fg_color="transparent")
        box_status.pack(fill="x", padx=18, pady=2)
        self.label_saude_circulo = ctk.CTkLabel(box_status, text="100%", font=("Segoe UI", 30, "bold"), text_color="#10B981")
        self.label_saude_circulo.pack(side="left")
        
        self.label_saude_status_texto = ctk.CTkLabel(
            c1, text="✅ Todas as condições estão ideais", font=("Segoe UI", 12, "bold"), text_color="#10B981", wraplength=380, justify="left"
        )
        self.label_saude_status_texto.pack(anchor="w", padx=18, pady=(2, 12))

        # Card 2: Clima e Ar
        c2 = ctk.CTkFrame(col_esq, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        c2.grid(row=1, column=0, sticky="nsew", pady=4)

        ctk.CTkLabel(c2, text="🌡️ ATMOSFERA E CLIMA", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(12, 4))

        l_ar1 = ctk.CTkFrame(c2, fg_color="transparent")
        l_ar1.pack(fill="x", padx=18, pady=2)
        ctk.CTkLabel(l_ar1, text="Temperatura do Ar", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_dash_temp = ctk.CTkLabel(l_ar1, text="24.5 °C", font=("Segoe UI", 16, "bold"), text_color="#FFFFFF")
        self.label_dash_temp.pack(side="right")

        l_ar2 = ctk.CTkFrame(c2, fg_color="transparent")
        l_ar2.pack(fill="x", padx=18, pady=2)
        ctk.CTkLabel(l_ar2, text="Umidade Relativa", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_dash_umid = ctk.CTkLabel(l_ar2, text="62.0 %", font=("Segoe UI", 16, "bold"), text_color="#FFFFFF")
        self.label_dash_umid.pack(side="right")

        # Card 3: Solução DWC & Nível
        c3 = ctk.CTkFrame(col_esq, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        c3.grid(row=2, column=0, sticky="nsew", pady=4)

        ctk.CTkLabel(c3, text="💧 SOLUÇÃO HIDROPÔNICA & NÍVEL", font=("Segoe UI", 12, "bold"), text_color="#64748B").pack(anchor="w", padx=18, pady=(12, 4))

        l_dwc1 = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc1.pack(fill="x", padx=18, pady=2)
        ctk.CTkLabel(l_dwc1, text="pH da Solução", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_dash_ph = ctk.CTkLabel(l_dwc1, text="6.10", font=("Segoe UI", 16, "bold"), text_color="#38BDF8")
        self.label_dash_ph.pack(side="right")

        l_dwc2 = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc2.pack(fill="x", padx=18, pady=2)
        ctk.CTkLabel(l_dwc2, text="Condutividade (EC)", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_dash_ec = ctk.CTkLabel(l_dwc2, text="1.4 mS/cm", font=("Segoe UI", 16, "bold"), text_color="#FB923C")
        self.label_dash_ec.pack(side="right")

        l_dwc3 = ctk.CTkFrame(c3, fg_color="transparent")
        l_dwc3.pack(fill="x", padx=18, pady=(2, 6))
        ctk.CTkLabel(l_dwc3, text="Nível do Reservatório", font=("Segoe UI", 13), text_color="#94A3B8").pack(side="left")
        self.label_dash_nivel = ctk.CTkLabel(l_dwc3, text="OK (100%)", font=("Segoe UI", 14, "bold"), text_color="#10B981")
        self.label_dash_nivel.pack(side="right")

        # COLUNA DIREITA: SIMULADOR DE SENSORES
        col_dir = ctk.CTkFrame(grid_principal, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(
            col_dir, text="⚡ SIMULADOR DE SENSORES (TEMPO REAL)", font=("Segoe UI", 13, "bold"), text_color="#10B981"
        ).pack(anchor="w", padx=20, pady=(18, 4))
        
        ctk.CTkLabel(
            col_dir, text="Mova os seletores abaixo ou plugue seu ESP32 físico:", font=("Segoe UI", 11), text_color="#64748B"
        ).pack(anchor="w", padx=20, pady=(0, 14))

        self.criar_controle(col_dir, "Temperatura do ar", 10, 40, self.horta.temperatura_ar, self.mudar_temperatura_ar, "°C")
        self.criar_controle(col_dir, "Umidade do ar", 0, 100, self.horta.umidade_ar, self.mudar_umidade_ar, "%")
        self.criar_controle(col_dir, "Temperatura da água", 5, 40, self.horta.temperatura_agua, self.mudar_temperatura_agua, "°C")
        self.criar_controle(col_dir, "pH", 2, 12, self.horta.ph, self.mudar_ph, "")
        self.criar_controle(col_dir, "EC", 0, 3, self.horta.ec, self.mudar_ec, "mS/cm")
        self.criar_controle(col_dir, "Nível da água", 0, 100, self.horta.nivel_agua, self.mudar_nivel_agua, "%")

        return frame

    # ======================================================
    # TELA 2: RECEITAS & CULTIVO (COM ENVIO BIDIRECIONAL PARA O ESP32)
    # ======================================================

    def criar_tela_nutricao(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="nut")
        frame.grid_rowconfigure(0, weight=1)

        col1 = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(col1, text="IDENTIDADE DO CULTIVO", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(20, 10), anchor="w", padx=20)
        
        ctk.CTkLabel(col1, text="Cultura Cadastrada", text_color="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=20)
        self.combo_cultura = ctk.CTkComboBox(
            col1, values=listar_culturas(), command=self.carregar_cultura,
            fg_color="#05070B", border_color="#1E293B", button_color="#1E293B", height=36, font=("Segoe UI", 12)
        )
        self.combo_cultura.pack(fill="x", padx=20, pady=(4, 16))

        ctk.CTkLabel(col1, text="Nome do Lote / Cultivo", text_color="#94A3B8", font=("Segoe UI", 12)).pack(anchor="w", padx=20)
        self.entry_nome_cultivo = ctk.CTkEntry(col1, fg_color="#05070B", border_color="#1E293B", height=36, font=("Segoe UI", 12))
        self.entry_nome_cultivo.pack(fill="x", padx=20, pady=(4, 20))

        ctk.CTkLabel(col1, text="FASE DE DESENVOLVIMENTO", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(10, 10), anchor="w", padx=20)
        self.combo_fase = ctk.CTkComboBox(
            col1, values=["MUDA", "VEGETATIVO", "FLORAÇÃO / FRUTIFICAÇÃO"],
            command=self.ao_mudar_fase, fg_color="#05070B", border_color="#1E293B", height=36, font=("Segoe UI", 12)
        )
        self.combo_fase.pack(fill="x", padx=20, pady=(4, 20))

        col2 = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        col2.grid(row=0, column=1, sticky="nsew", padx=4)

        ctk.CTkLabel(col2, text="FOTOPERÍODO & LUZ", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(20, 10), anchor="w", padx=20)

        f_p1 = ctk.CTkFrame(col2, fg_color="transparent")
        f_p1.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_p1, text="Horas de luz / dia", text_color="#94A3B8", font=("Segoe UI", 12)).pack(side="left")
        self.entry_fotoperiodo = ctk.CTkEntry(f_p1, width=80, fg_color="#05070B", border_color="#1E293B", height=34, font=("Segoe UI", 12))
        self.entry_fotoperiodo.pack(side="right")

        f_p2 = ctk.CTkFrame(col2, fg_color="transparent")
        f_p2.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_p2, text="Início da luz (HH:MM)", text_color="#94A3B8", font=("Segoe UI", 12)).pack(side="left")
        self.entry_inicio_minuto = ctk.CTkEntry(f_p2, width=45, fg_color="#05070B", border_color="#1E293B", height=34, font=("Segoe UI", 12))
        self.entry_inicio_minuto.pack(side="right")
        ctk.CTkLabel(f_p2, text=":", text_color="#94A3B8").pack(side="right", padx=2)
        self.entry_inicio_hora = ctk.CTkEntry(f_p2, width=45, fg_color="#05070B", border_color="#1E293B", height=34, font=("Segoe UI", 12))
        self.entry_inicio_hora.pack(side="right")

        col3 = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        col3.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(col3, text="LIMITES & RECEITA DE NUTRIÇÃO", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(20, 8), anchor="w", padx=20)

        campos = [
            ("pH mín / máx", "ph_min"), ("EC mín / máx", "ec_min"),
            ("Temp. ar mín/máx", "temperatura_ar_min"), ("Temp. água mín/máx", "temperatura_agua_min"),
            ("Umidade mín/máx", "umidade_ar_min")
        ]
        for tit, chav in campos:
            self.criar_campo_config(col3, tit, chav)

        nut_box = ctk.CTkFrame(col3, fg_color="#05070B", corner_radius=8, border_width=1, border_color="#1E293B")
        nut_box.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(nut_box, text="🧪 FERTILIZANTE COMERCIAL", font=("Segoe UI", 11, "bold"), text_color="#10B981").pack(pady=(8, 4), anchor="w", padx=12)
        
        f_prod = ctk.CTkFrame(nut_box, fg_color="transparent")
        f_prod.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(f_prod, text="Produto:", text_color="#94A3B8", font=("Segoe UI", 11)).pack(side="left")
        self.entry_nome_fertilizante = ctk.CTkEntry(f_prod, width=130, fg_color="#0D1322", border_color="#1E293B", height=28, font=("Segoe UI", 11))
        self.entry_nome_fertilizante.pack(side="right")

        self.entry_taxa_ab = self.criar_campo_nutricao(nut_box, "g/L por +1.0 EC:")
        self.entry_taxa_ph_down = self.criar_campo_nutricao(nut_box, "pH Down (mL/L):")
        self.entry_taxa_ph_up = self.criar_campo_nutricao(nut_box, "pH Up (mL/L):")

        btn_salvar_rec = ctk.CTkButton(
            col3, text="💾 SALVAR & SINCRONIZAR COM ESP32", command=self.salvar_e_sincronizar_receita, height=36,
            fg_color="#059669", hover_color="#047857", text_color="#FFFFFF", font=("Segoe UI", 12, "bold")
        )
        btn_salvar_rec.pack(fill="x", padx=20, pady=(12, 16))

        self.preencher_configuracao()
        return frame

    # ======================================================
    # TELA 3: GRÁFICOS & LOGS
    # ======================================================

    def criar_tela_graficos(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="g")
        frame.grid_rowconfigure((0, 1), weight=1)

        g1_frame = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        g1_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        ctk.CTkLabel(g1_frame, text="📈 EVOLUÇÃO DA SAÚDE BIOLÓGICA (%)", font=("Segoe UI", 12, "bold"), text_color="#FFFFFF").pack(pady=(12, 0))
        
        self.fig1 = Figure(figsize=(5, 2.4), dpi=100)
        self.fig1.patch.set_facecolor('#0D1322')
        self.ax1 = self.fig1.add_subplot(111)
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=g1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        g2_frame = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        g2_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))
        ctk.CTkLabel(g2_frame, text="🧪 DINÂMICA DE NUTRIÇÃO (pH & EC)", font=("Segoe UI", 12, "bold"), text_color="#FFFFFF").pack(pady=(12, 0))
        
        self.fig2 = Figure(figsize=(5, 2.4), dpi=100)
        self.fig2.patch.set_facecolor('#0D1322')
        self.ax2 = self.fig2.add_subplot(111)
        self.configurar_estilo_eixo(self.ax2, "pH / EC", 0, 14)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=g2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        g3_frame = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        g3_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        
        g3_topo = ctk.CTkFrame(g3_frame, fg_color="transparent")
        g3_topo.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(g3_topo, text="🌡️ MONITORAMENTO TÉRMICO COMPARATIVO (AR vs ÁGUA)", font=("Segoe UI", 12, "bold"), text_color="#FFFFFF").pack(side="left")
        
        self.btn_exportar_csv = ctk.CTkButton(
            g3_topo, text="📥 EXPORTAR LOGS (CSV)", command=self.exportar_logs_csv, height=32, width=190,
            fg_color="#059669", hover_color="#047857", text_color="#FFFFFF", font=("Segoe UI", 11, "bold")
        )
        self.btn_exportar_csv.pack(side="right")

        self.fig3 = Figure(figsize=(10, 2.0), dpi=100)
        self.fig3.patch.set_facecolor('#0D1322')
        self.ax3 = self.fig3.add_subplot(111)
        self.configurar_estilo_eixo(self.ax3, "Temp (°C)", 10, 45)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=g3_frame)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)

        return frame

    # ======================================================
    # TELA 4: CONFIGURAÇÕES DO ESP32 & MONITOR SERIAL PLUG-AND-PLAY
    # ======================================================

    def criar_tela_configuracao(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure((0, 1), weight=1, uniform="conf")
        frame.grid_rowconfigure(0, weight=1)

        c_hw = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        c_hw.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(c_hw, text="GERENCIAMENTO DE HARDWARE PLUG-AND-PLAY", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(20, 14), anchor="w", padx=20)

        self.switch_hardware = ctk.CTkSwitch(
            c_hw, text=" Habilitar Leitura Automática do ESP32 (USB)",
            command=self.alternar_modo_hardware, font=("Segoe UI", 13, "bold"), text_color="#10B981",
            progress_color="#059669"
        )
        self.switch_hardware.pack(anchor="w", padx=20, pady=10)

        self.label_status_hw_detalhe = ctk.CTkLabel(
            c_hw, text="Plugue o ESP32 em qualquer porta USB. O sistema detectará automaticamente.", font=("Segoe UI", 12), text_color="#94A3B8", wraplength=450, justify="left"
        )
        self.label_status_hw_detalhe.pack(anchor="w", padx=20, pady=10)

        # Painel de Controle Manual de Atuadores (Relés)
        rel_box = ctk.CTkFrame(c_hw, fg_color="#05070B", corner_radius=10, border_width=1, border_color="#1E293B")
        rel_box.pack(fill="x", padx=20, pady=16)
        ctk.CTkLabel(rel_box, text="⚡ COMANDOS MANUAIS DE ATUADORES", font=("Segoe UI", 11, "bold"), text_color="#10B981").pack(anchor="w", padx=14, pady=(10, 6))

        botoes_acao_frame = ctk.CTkFrame(rel_box, fg_color="transparent")
        botoes_acao_frame.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkButton(
            botoes_acao_frame, text="Ligar Luz (Relé 1)", command=lambda: self.enviar_comando_esp("set_relay", {"dispositivo": "luz", "estado": "ON"}),
            fg_color="#059669", hover_color="#047857", height=32, font=("Segoe UI", 11, "bold")
        ).pack(side="left", expand=True, padx=(0, 4))

        ctk.CTkButton(
            botoes_acao_frame, text="Desligar Luz", command=lambda: self.enviar_comando_esp("set_relay", {"dispositivo": "luz", "estado": "OFF"}),
            fg_color="#334155", hover_color="#475569", height=32, font=("Segoe UI", 11, "bold")
        ).pack(side="left", expand=True, padx=(4, 0))

        c_ser = ctk.CTkFrame(frame, fg_color="#0D1322", corner_radius=14, border_width=1, border_color="#1E293B")
        c_ser.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(c_ser, text="MONITOR DE COMUNICAÇÃO SERIAL EM TEMPO REAL", font=("Segoe UI", 13, "bold"), text_color="#64748B").pack(pady=(20, 10), anchor="w", padx=20)
        
        self.serial_box_text = ctk.CTkTextbox(c_ser, fg_color="#05070B", text_color="#34D399", font=("Consolas", 12), corner_radius=8)
        self.serial_box_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.serial_box_text.insert("0.0", "[INFO] Aguardando ativação do hardware real...\n")
        self.serial_box_text.configure(state="disabled")

        return frame

    # ======================================================
    # MÉTODOS AUXILIARES E SUPORTE SERIAL & BIDIRECIONAL
    # ======================================================

    def configurar_estilo_eixo(self, ax, ylabel, ymin, ymax):
        ax.set_facecolor('#0D1322')
        ax.tick_params(colors='#94A3B8', labelsize=10)
        ax.spines['bottom'].set_color('#1E293B')
        ax.spines['left'].set_color('#1E293B')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylabel(ylabel, color="#94A3B8", fontsize=10)
        ax.set_ylim(ymin, ymax)

    def criar_campo_config(self, parent, titulo, chave):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(linha, text=titulo, anchor="w", font=("Segoe UI", 12), text_color="#94A3B8").pack(side="left")
        entry = ctk.CTkEntry(linha, width=80, fg_color="#05070B", border_color="#1E293B", height=30, font=("Segoe UI", 12))
        entry.pack(side="right")
        self.entries_config[chave] = entry

    def criar_campo_nutricao(self, parent, titulo):
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(linha, text=titulo, anchor="w", font=("Segoe UI", 11), text_color="#94A3B8").pack(side="left")
        entry = ctk.CTkEntry(linha, width=70, fg_color="#0D1322", border_color="#059669", height=28, font=("Segoe UI", 11))
        entry.pack(side="right")
        return entry

    def criar_controle(self, parent, nome, minimo, maximo, valor, callback, unidade):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=7)

        linha = ctk.CTkFrame(frame, fg_color="transparent")
        linha.pack(fill="x", padx=0, pady=(0, 2))

        ctk.CTkLabel(linha, text=nome, font=("Segoe UI", 12, "bold"), text_color="#FFFFFF").pack(side="left")
        label = ctk.CTkLabel(linha, text=f"{valor:.1f} {unidade}", font=("Segoe UI", 12, "bold"), text_color="#10B981")
        label.pack(side="right")
        self.labels_valores[nome] = label

        slider = ctk.CTkSlider(
            frame, from_=minimo, to=maximo, number_of_steps=100, height=14,
            progress_color="#059669", button_color="#FFFFFF", button_hover_color="#E2E8F0", fg_color="#05070B"
        )
        slider.pack(fill="x", padx=0, pady=(2, 2))
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
            self.combo_fase.set(getattr(config, 'fase', 'VEGETATIVO'))
            self.entry_fotoperiodo.delete(0, "end")
            self.entry_fotoperiodo.insert(0, str(getattr(config, 'fotoperiodo_horas', 18)))
            self.entry_inicio_hora.delete(0, "end")
            self.entry_inicio_hora.insert(0, f"{getattr(config, 'inicio_luz_hora', 6):02d}")
            self.entry_inicio_minuto.delete(0, "end")
            self.entry_inicio_minuto.insert(0, f"{getattr(config, 'inicio_luz_minuto', 0):02d}")
            self.entry_nome_fertilizante.delete(0, "end")
            self.entry_nome_fertilizante.insert(0, getattr(self.horta, 'nome_fertilizante', 'Flex Azul + Vermelho'))
            self.entry_taxa_ab.delete(0, "end")
            self.entry_taxa_ab.insert(0, str(getattr(self.horta, 'gramas_por_litro_recomendado', 0.84)))
            self.entry_taxa_ph_down.delete(0, "end")
            self.entry_taxa_ph_down.insert(0, str(getattr(self.horta, 'taxa_ph_down', 0.5)))
            self.entry_taxa_ph_up.delete(0, "end")
            self.entry_taxa_ph_up.insert(0, str(getattr(self.horta, 'taxa_ph_up', 0.5)))
        except Exception as e:
            print("Aviso ao preencher config:", e)

    def salvar_e_sincronizar_receita(self):
        # Atualiza os valores no modelo interno
        try:
            cfg = self.horta.config
            cfg.nome_cultivo = self.entry_nome_cultivo.get()
            cfg.fase = self.combo_fase.get()
            cfg.fotoperiodo_horas = float(self.entry_fotoperiodo.get())
            cfg.inicio_luz_hora = int(self.entry_inicio_hora.get())
            cfg.inicio_luz_minuto = int(self.entry_inicio_minuto.get())

            for chave, entry in self.entries_config.items():
                setattr(cfg, chave, float(entry.get()))

            self.horta.nome_fertilizante = self.entry_nome_fertilizante.get()
            self.horta.gramas_por_litro_recomendado = float(self.entry_taxa_ab.get())

            # Prepara pacote JSON para sincronizar com o ESP32 físico
            pacote_json = {
                "cmd": "set_config",
                "cultura": cfg.nome_cultivo,
                "fase": cfg.fase,
                "ph_min": cfg.ph_min,
                "ph_max": cfg.ph_max,
                "ec_min": cfg.ec_min,
                "ec_max": cfg.ec_max,
                "temp_ar_max": cfg.temperatura_ar_max,
                "fotoperiodo": cfg.fotoperiodo_horas,
                "inicio_luz": cfg.inicio_luz_hora
            }

            self.enviar_pacote_serial_raw(pacote_json)
            self.atualizar_log_serial("[SUCESSO] Receita salva e enviada ao ESP32 via Serial!\n")
        except Exception as e:
            print("Erro ao salvar receita:", e)

    def enviar_comando_esp(self, acao, payload):
        pacote = {"cmd": acao, **payload}
        self.enviar_pacote_serial_raw(pacote)
        self.atualizar_log_serial(f"[COMANDO] Enviado: {acao} -> {payload}\n")

    def enviar_pacote_serial_raw(self, dados_dict):
        if self.ser and self.ser.is_open:
            try:
                linha = json.dumps(dados_dict) + "\n"
                self.ser.write(linha.encode('utf-8'))
            except Exception as e:
                self.atualizar_log_serial(f"[ERRO] Falha ao enviar comando serial: {e}\n")
        else:
            print("[SIMULAÇÃO SERIAL] Pacote gerado (ESP offline):", dados_dict)

    def ao_mudar_fase(self, nova_fase): pass
    
    def carregar_cultura(self, nome):
        try:
            self.horta.selecionar_cultura(nome)
            self.preencher_configuracao()
            self.atualizar_interface()
        except Exception as e: print("Erro:", e)

    def alternar_modo_hardware(self):
        self.modo_hardware_real = self.switch_hardware.get() == 1
        estado = "disabled" if self.modo_hardware_real else "normal"
        for s in self.sliders.values(): s.configure(state=estado)
        
        if self.modo_hardware_real:
            self.label_status_esp.configure(text="● BUSCANDO ESP32...", text_color="#F59E0B")
            self.iniciar_conexao_serial_automatica()
        else:
            self.fechar_conexao_serial()
            self.label_status_esp.configure(text="● DIGITAL TWIN SIMULADO", text_color="#38BDF8")

    def iniciar_conexao_serial_automatica(self):
        if not SERIAL_DISPONIVEL:
            self.atualizar_log_serial("[ERRO] Biblioteca 'pyserial' não instalada. Execute: pip install pyserial\n")
            return

        def scan_e_conectar():
            porta_encontrada = None
            portas = serial.tools.list_ports.comports()
            
            for p in portas:
                descricao = p.description.upper()
                if "USB" in descricao or "UART" in descricao or "CP210" in descricao or "CH340" in descricao or "ESP32" in descricao:
                    porta_encontrada = p.device
                    break
            
            if not porta_encontrada and len(portas) > 0:
                porta_encontrada = portas[0].device

            if porta_encontrada:
                try:
                    self.ser = serial.Serial(porta_encontrada, 115200, timeout=1)
                    self.serial_thread_ativa = True
                    self.label_status_esp.configure(text=f"● ESP32 CONECTADO ({porta_encontrada})", text_color="#10B981")
                    self.atualizar_log_serial(f"[SUCESSO] Conectado na porta {porta_encontrada} a 115200 baud.\n")
                    
                    while self.serial_thread_ativa and self.ser and self.ser.is_open:
                        linha = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if linha:
                            self.atualizar_log_serial(f"{linha}\n")
                            if linha.startswith("{") and linha.endswith("}"):
                                try:
                                    dados_esp = json.loads(linha)
                                    if "temperatura_ar" in dados_esp: self.horta.alterar_temperatura_ar(dados_esp["temperatura_ar"])
                                    if "umidade_ar" in dados_esp: self.horta.alterar_umidade_ar(dados_esp["umidade_ar"])
                                    if "temperatura_agua" in dados_esp: self.horta.alterar_temperatura_agua(dados_esp["temperatura_agua"])
                                    if "ph" in dados_esp: self.horta.alterar_ph(dados_esp["ph"])
                                    if "ec" in dados_esp: self.horta.alterar_ec(dados_esp["ec"])
                                    if "nivel_agua" in dados_esp: self.horta.alterar_nivel_agua(dados_esp["nivel_agua"])
                                except json.JSONDecodeError:
                                    pass
                except Exception as e:
                    self.label_status_esp.configure(text="● ERRO DE CONEXÃO ESP32", text_color="#EF4444")
                    self.atualizar_log_serial(f"[ERRO] Falha ao abrir porta: {e}\n")
            else:
                self.label_status_esp.configure(text="● NENHUM ESP32 ENCONTRADO", text_color="#EF4444")
                self.atualizar_log_serial("[ALERTA] Nenhuma porta USB/Serial ativa detectada. Verifique o cabo.\n")

        threading.Thread(target=scan_e_conectar, daemon=True).start()

    def fechar_conexao_serial(self):
        self.serial_thread_ativa = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
        self.atualizar_log_serial("[INFO] Conexão serial encerrada. Retornando ao modo simulador.\n")

    def atualizar_log_serial(self, texto):
        self.log_serial_buffer.append(texto)
        if len(self.log_serial_buffer) > 100:
            self.log_serial_buffer.pop(0)
        try:
            self.serial_box_text.configure(state="normal")
            self.serial_box_text.delete("0.0", "end")
            self.serial_box_text.insert("0.0", "".join(self.log_serial_buffer))
            self.serial_box_text.see("end")
            self.serial_box_text.configure(state="disabled")
        except:
            pass

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
        self.demonstracao_ativa = not self.demonstracao_ativa
        if self.demonstracao_ativa:
            self.btn_pausa_tempo.configure(text="⏸ PAUSAR TEMPO", fg_color="#DC2626")
        else:
            self.btn_pausa_tempo.configure(text="▶ INICIAR TEMPO", fg_color="#059669")

    def avancar_tempo(self, m):
        self.horta.avancar_tempo(m)
        self.atualizar_interface()

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
        except Exception as e: print("Erro:", e)

    def atualizar_graficos_avancados(self, dados):
        self.tempo_contador += 1
        self.historico_tempo.append(self.tempo_contador)
        self.historico_saude.append(dados["saude"])
        self.historico_ph.append(dados["ph"])
        self.historico_ec.append(dados["ec"])
        self.historico_temp_ar.append(dados["temperatura_ar"])
        self.historico_temp_agua.append(dados["temperatura_agua"])

        self.historico_logs.append({
            "tempo": self.tempo_contador, "saude": dados["saude"],
            "temp_ar": dados["temperatura_ar"], "ph": dados["ph"], "ec": dados["ec"]
        })

        if len(self.historico_tempo) > 30:
            for h in [self.historico_tempo, self.historico_saude, self.historico_ph, self.historico_ec, self.historico_temp_ar, self.historico_temp_agua]:
                h.pop(0)

        self.ax1.clear()
        self.configurar_estilo_eixo(self.ax1, "Saúde (%)", 0, 105)
        self.ax1.plot(self.historico_tempo, self.historico_saude, color="#10B981", linewidth=2.5)
        self.canvas1.draw()

        self.ax2.clear()
        self.configurar_estilo_eixo(self.ax2, "pH/EC", 0, 14)
        self.ax2.plot(self.historico_tempo, self.historico_ph, color="#38BDF8", label="pH", linewidth=2)
        self.ax2.plot(self.historico_tempo, self.historico_ec, color="#FB923C", label="EC", linewidth=2)
        self.ax2.legend(loc="upper right", facecolor="#0D1322", edgecolor="#1E293B", labelcolor="#FFFFFF", fontsize=9)
        self.canvas2.draw()

        self.ax3.clear()
        self.configurar_estilo_eixo(self.ax3, "Temp", 10, 45)
        self.ax3.plot(self.historico_tempo, self.historico_temp_ar, color="#EF4444", label="Ar", linewidth=2)
        self.ax3.plot(self.historico_tempo, self.historico_temp_agua, color="#2DD4BF", label="Água", linewidth=2)
        self.ax3.legend(loc="upper right", facecolor="#0D1322", edgecolor="#1E293B", labelcolor="#FFFFFF", fontsize=9)
        self.canvas3.draw()

    def atualizar_interface(self):
        self.horta.diagnosticar()
        dados = self.horta.snapshot()

        self.label_sub_cultivo.configure(text=f"{dados['cultivo']} • Fase: {dados['fase']}")
        
        saude = dados['saude']
        self.label_saude_circulo.configure(text=f"{saude:.0f}%")
        
        problemas = []
        cfg = self.horta.config

        if dados['ph'] < cfg.ph_min:
            problemas.append(f"• pH baixo ({dados['ph']:.2f} < {cfg.ph_min})")
        elif dados['ph'] > cfg.ph_max:
            problemas.append(f"• pH alto ({dados['ph']:.2f} > {cfg.ph_max})")

        if dados['ec'] < cfg.ec_min:
            problemas.append(f"• EC baixa ({dados['ec']:.1f} < {cfg.ec_min})")
        elif dados['ec'] > cfg.ec_max:
            problemas.append(f"• EC alta ({dados['ec']:.1f} > {cfg.ec_max})")

        if dados['temperatura_ar'] < cfg.temperatura_ar_min:
            problemas.append(f"• Ar frio ({dados['temperatura_ar']:.1f}°C)")
        elif dados['temperatura_ar'] > cfg.temperatura_ar_max:
            problemas.append(f"• Ar quente ({dados['temperatura_ar']:.1f}°C)")

        if dados['temperatura_agua'] < cfg.temperatura_agua_min:
            problemas.append(f"• Água fria ({dados['temperatura_agua']:.1f}°C)")
        elif dados['temperatura_agua'] > cfg.temperatura_agua_max:
            problemas.append(f"• Água quente ({dados['temperatura_agua']:.1f}°C)")

        if dados['nivel_agua'] < 20:
            problemas.append("• Reservatório baixo / Seco")

        if len(problemas) == 0 and saude > 80:
            self.label_saude_status_texto.configure(text="✅ Condições ideais no cultivo", text_color="#10B981")
            self.label_saude_circulo.configure(text_color="#10B981")
        else:
            texto_alerta = "⚠️ Anomalias Detectadas:\n" + "\n".join(problemas)
            self.label_saude_status_texto.configure(text=texto_alerta, text_color="#EF4444")
            if saude < 40:
                self.label_saude_circulo.configure(text_color="#EF4444")
            else:
                self.label_saude_circulo.configure(text_color="#F59E0B")

        self.label_dash_temp.configure(text=f"{dados['temperatura_ar']:.1f} °C")
        self.label_dash_umid.configure(text=f"{dados['umidade_ar']:.0f} %")
        self.label_dash_ph.configure(text=f"{dados['ph']:.2f}")
        self.label_dash_ec.configure(text=f"{dados['ec']:.1f} mS/cm")
        
        nivel_status = dados.get("nivel_agua_status", "OK (100%)")
        self.label_dash_nivel.configure(text=nivel_status)
        
        hora = f"{dados['hora_atual']:02d}:{dados['minuto_atual']:02d}"
        self.label_relogio_topo.configure(text=f"{hora}  12/09/2026")
        
        self.atualizar_graficos_avancados(dados)

    def ciclo_interface(self):
        if self.demonstracao_ativa:
            self.horta.tick_tempo()
        if self.automacao_ativa:
            self.horta.executar_automacao()
        self.atualizar_interface()
        self.after(1000, self.ciclo_interface)