import customtkinter as ctk
import json
import os

from modelo.horta import Horta
from modelo.configuracao import ConfiguracaoCultivo
from modelo.banco_cultivos import listar_culturas


class JanelaPrincipal(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "HORTA DO FUTURO — Digital Twin"
        )

        self.geometry(
            "1280x820"
        )

        self.minsize(
            1050,
            700
        )

        self.horta = Horta()

        self.automacao_ativa = True

        self.demonstracao_ativa = False

        self.sliders = {}

        self.entries_config = {}

        self.criar_interface()

        self.atualizar_interface()

        self.after(
            1000,
            self.ciclo_interface
        )

    # ======================================================
    # INTERFACE
    # ======================================================

    def criar_interface(self):

        titulo = ctk.CTkLabel(
            self,
            text="HORTA DO FUTURO",
            font=("Arial", 30, "bold")
        )

        titulo.pack(
            pady=(12, 0)
        )

        subtitulo = ctk.CTkLabel(
            self,
            text="COMPUTADOR DE PLANTAS • DIGITAL TWIN",
            font=("Arial", 14)
        )

        subtitulo.pack(
            pady=(0, 10)
        )

        self.tabs = ctk.CTkTabview(
            self
        )

        self.tabs.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.tab_dashboard = (
            self.tabs.add("🌱 DASHBOARD")
        )

        self.tab_config = (
            self.tabs.add("⚙ CONFIGURAÇÃO")
        )

        self.tab_demo = (
            self.tabs.add("⚡ SIMULAÇÃO")
        )

        self.criar_dashboard()

        self.criar_configuracao()

        self.criar_simulacao()

    # ======================================================
    # DASHBOARD
    # ======================================================

    def criar_dashboard(self):

        painel = self.tab_dashboard

        painel.grid_columnconfigure(
            0,
            weight=1
        )

        painel.grid_columnconfigure(
            1,
            weight=2
        )

        painel.grid_columnconfigure(
            2,
            weight=1
        )

        painel.grid_rowconfigure(
            0,
            weight=1
        )

        # --------------------------------------------------
        # ESTADO
        # --------------------------------------------------

        estado = ctk.CTkFrame(
            painel
        )

        estado.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=6,
            pady=6
        )

        ctk.CTkLabel(
            estado,
            text="ESTADO DA HORTA",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(15, 10)
        )

        self.label_cultivo = ctk.CTkLabel(
            estado,
            text="🌱 ALFACE",
            font=("Arial", 25, "bold")
        )

        self.label_cultivo.pack(
            pady=4
        )

        self.label_nome_cultivo = ctk.CTkLabel(
            estado,
            text="Alface Experimental #01",
            font=("Arial", 14)
        )

        self.label_nome_cultivo.pack()

        self.label_fase = ctk.CTkLabel(
            estado,
            text="VEGETATIVO",
            font=("Arial", 14)
        )

        self.label_fase.pack(
            pady=(0, 15)
        )

        self.label_status = ctk.CTkLabel(
            estado,
            text="SAUDÁVEL",
            font=("Arial", 20, "bold")
        )

        self.label_status.pack(
            pady=5
        )

        self.label_saude = ctk.CTkLabel(
            estado,
            text="SAÚDE: 100%",
            font=("Arial", 24, "bold")
        )

        self.label_saude.pack(
            pady=(12, 4)
        )

        self.barra_saude = ctk.CTkProgressBar(
            estado,
            width=220
        )

        self.barra_saude.pack(
            pady=(0, 20)
        )

        self.barra_saude.set(1)

        ctk.CTkLabel(
            estado,
            text="RESERVATÓRIO",
            font=("Arial", 15, "bold")
        ).pack()

        self.label_nivel = ctk.CTkLabel(
            estado,
            text="100% — CHEIO",
            font=("Arial", 19, "bold")
        )

        self.label_nivel.pack(
            pady=4
        )

        self.barra_agua = ctk.CTkProgressBar(
            estado,
            width=220
        )

        self.barra_agua.pack(
            pady=(0, 20)
        )

        self.barra_agua.set(1)

        ctk.CTkLabel(
            estado,
            text="RELÓGIO VIRTUAL",
            font=("Arial", 15, "bold")
        ).pack()

        self.label_relogio = ctk.CTkLabel(
            estado,
            text="13:00",
            font=("Arial", 30, "bold")
        )

        self.label_relogio.pack(
            pady=2
        )

        self.label_periodo = ctk.CTkLabel(
            estado,
            text="💡 LUZ LIGADA",
            font=("Arial", 14)
        )

        self.label_periodo.pack()

        # --------------------------------------------------
        # SENSORES
        # --------------------------------------------------

        sensores = ctk.CTkFrame(
            painel
        )

        sensores.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=6,
            pady=6
        )

        ctk.CTkLabel(
            sensores,
            text="SENSORES VIRTUAIS",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(15, 3)
        )

        ctk.CTkLabel(
            sensores,
            text="GOD MODE",
            font=("Arial", 12)
        ).pack(
            pady=(0, 8)
        )

        self.criar_controle(
            sensores,
            "Temperatura do ar",
            10,
            40,
            self.horta.temperatura_ar,
            self.mudar_temperatura_ar,
            "°C"
        )

        self.criar_controle(
            sensores,
            "Umidade do ar",
            0,
            100,
            self.horta.umidade_ar,
            self.mudar_umidade_ar,
            "%"
        )

        self.criar_controle(
            sensores,
            "Temperatura da água",
            5,
            40,
            self.horta.temperatura_agua,
            self.mudar_temperatura_agua,
            "°C"
        )

        self.criar_controle(
            sensores,
            "pH",
            2,
            12,
            self.horta.ph,
            self.mudar_ph,
            ""
        )

        self.criar_controle(
            sensores,
            "EC",
            0,
            3,
            self.horta.ec,
            self.mudar_ec,
            "mS/cm"
        )

        self.criar_controle(
            sensores,
            "Nível da água",
            0,
            100,
            self.horta.nivel_agua,
            self.mudar_nivel_agua,
            "%"
        )

        # --------------------------------------------------
        # AUTOMAÇÃO
        # --------------------------------------------------

        auto = ctk.CTkFrame(
            painel
        )

        auto.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=6,
            pady=6
        )

        ctk.CTkLabel(
            auto,
            text="AUTOMAÇÃO",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(15, 12)
        )

        self.label_ventilacao = (
            self.criar_status_atuador(
                auto,
                "VENTILAÇÃO"
            )
        )

        self.label_bomba = (
            self.criar_status_atuador(
                auto,
                "BOMBA"
            )
        )

        self.label_iluminacao = (
            self.criar_status_atuador(
                auto,
                "ILUMINAÇÃO"
            )
        )

        self.botao_automacao = ctk.CTkButton(
            auto,
            text="AUTOMAÇÃO: LIGADA",
            command=self.alternar_automacao
        )

        self.botao_automacao.pack(
            fill="x",
            padx=20,
            pady=(20, 5)
        )

        self.label_fotoperiodo = ctk.CTkLabel(
            auto,
            text="18h LIGADA / 6h DESLIGADA",
            font=("Arial", 14)
        )

        self.label_fotoperiodo.pack(
            pady=(20, 3)
        )

        self.label_inicio_luz = ctk.CTkLabel(
            auto,
            text="Início: 06:00",
            font=("Arial", 14)
        )

        self.label_inicio_luz.pack()

    # ======================================================
    # CONTROLE
    # ======================================================

    def criar_controle(
        self,
        parent,
        nome,
        minimo,
        maximo,
        valor,
        callback,
        unidade
    ):

        frame = ctk.CTkFrame(
            parent
        )

        frame.pack(
            fill="x",
            padx=15,
            pady=3
        )

        linha = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        linha.pack(
            fill="x",
            padx=8,
            pady=(4, 0)
        )

        ctk.CTkLabel(
            linha,
            text=nome,
            font=("Arial", 13, "bold")
        ).pack(
            side="left"
        )

        label = ctk.CTkLabel(
            linha,
            text=f"{valor:.1f} {unidade}",
            font=("Arial", 13)
        )

        label.pack(
            side="right"
        )

        slider = ctk.CTkSlider(
            frame,
            from_=minimo,
            to=maximo,
            number_of_steps=100
        )

        slider.pack(
            fill="x",
            padx=10,
            pady=(2, 6)
        )

        slider.set(valor)

        def mover(valor_slider):

            callback(
                float(valor_slider)
            )

            label.configure(
                text=f"{float(valor_slider):.1f} {unidade}"
            )

        slider.configure(
            command=mover
        )

        self.sliders[nome] = slider

    # ======================================================
    # ATUADOR
    # ======================================================

    def criar_status_atuador(
        self,
        parent,
        nome
    ):

        label = ctk.CTkLabel(
            parent,
            text=f"{nome}: DESLIGADA",
            font=("Arial", 14)
        )

        label.pack(
            pady=6
        )

        return label

    # ======================================================
    # CONFIGURAÇÃO
    # ======================================================

    def criar_configuracao(self):

        painel = self.tab_config

        painel.grid_columnconfigure(
            0,
            weight=1
        )

        painel.grid_columnconfigure(
            1,
            weight=1
        )

        painel.grid_rowconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            painel,
            text="CONFIGURAÇÃO DA CULTURA",
            font=("Arial", 23, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(15, 10)
        )

        # --------------------------------------------------
        # IDENTIDADE
        # --------------------------------------------------

        identidade = ctk.CTkFrame(
            painel
        )

        identidade.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=8
        )

        ctk.CTkLabel(
            identidade,
            text="CULTIVO",
            font=("Arial", 17, "bold")
        ).pack(
            pady=(15, 12)
        )

        ctk.CTkLabel(
            identidade,
            text="Cultura"
        ).pack(
            anchor="w",
            padx=20
        )

        self.combo_cultura = ctk.CTkComboBox(
            identidade,
            values=listar_culturas(),
            command=self.carregar_cultura
        )

        self.combo_cultura.pack(
            fill="x",
            padx=20,
            pady=(4, 12)
        )

        self.combo_cultura.set(
            self.horta.config.nome
        )

        ctk.CTkLabel(
            identidade,
            text="Nome individual do cultivo"
        ).pack(
            anchor="w",
            padx=20
        )

        self.entry_nome_cultivo = ctk.CTkEntry(
            identidade
        )

        self.entry_nome_cultivo.pack(
            fill="x",
            padx=20,
            pady=(4, 12)
        )

        self.entry_nome_cultivo.insert(
            0,
            self.horta.config.nome_cultivo
        )

        ctk.CTkLabel(
            identidade,
            text="Fase"
        ).pack(
            anchor="w",
            padx=20
        )

        self.combo_fase = ctk.CTkComboBox(
            identidade,
            values=[
                "MUDAS",
                "VEGETATIVO",
                "FLORAÇÃO",
                "FRUTIFICAÇÃO",
                "COLHEITA"
            ]
        )

        self.combo_fase.pack(
            fill="x",
            padx=20,
            pady=(4, 12)
        )

        self.combo_fase.set(
            self.horta.config.fase
        )

        # --------------------------------------------------
        # PARÂMETROS
        # --------------------------------------------------

        parametros = ctk.CTkFrame(
            painel
        )

        parametros.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=8,
            pady=8
        )

        ctk.CTkLabel(
            parametros,
            text="PARÂMETROS IDEAIS",
            font=("Arial", 17, "bold")
        ).pack(
            pady=(15, 10)
        )

        self.criar_campo_config(
            parametros,
            "pH mínimo",
            "ph_min"
        )

        self.criar_campo_config(
            parametros,
            "pH máximo",
            "ph_max"
        )

        self.criar_campo_config(
            parametros,
            "EC mínima",
            "ec_min"
        )

        self.criar_campo_config(
            parametros,
            "EC máxima",
            "ec_max"
        )

        self.criar_campo_config(
            parametros,
            "Temperatura ar mínima",
            "temperatura_ar_min"
        )

        self.criar_campo_config(
            parametros,
            "Temperatura ar máxima",
            "temperatura_ar_max"
        )

        self.criar_campo_config(
            parametros,
            "Temperatura água mínima",
            "temperatura_agua_min"
        )

        self.criar_campo_config(
            parametros,
            "Temperatura água máxima",
            "temperatura_agua_max"
        )

        self.criar_campo_config(
            parametros,
            "Umidade mínima",
            "umidade_ar_min"
        )

        self.criar_campo_config(
            parametros,
            "Umidade máxima",
            "umidade_ar_max"
        )

        # --------------------------------------------------
        # FOTOPERÍODO
        # --------------------------------------------------

        foto = ctk.CTkFrame(
            painel
        )

        foto.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=8,
            pady=8
        )

        ctk.CTkLabel(
            foto,
            text="☀ FOTOPERÍODO",
            font=("Arial", 17, "bold")
        ).pack(
            pady=(10, 5)
        )

        linha = ctk.CTkFrame(
            foto,
            fg_color="transparent"
        )

        linha.pack(
            pady=5
        )

        self.entry_fotoperiodo = ctk.CTkEntry(
            linha,
            width=80
        )

        self.entry_fotoperiodo.pack(
            side="left",
            padx=4
        )

        ctk.CTkLabel(
            linha,
            text="horas de luz  |  início:"
        ).pack(
            side="left"
        )

        self.entry_inicio_hora = ctk.CTkEntry(
            linha,
            width=55
        )

        self.entry_inicio_hora.pack(
            side="left",
            padx=4
        )

        ctk.CTkLabel(
            linha,
            text=":"
        ).pack(
            side="left"
        )

        self.entry_inicio_minuto = ctk.CTkEntry(
            linha,
            width=55
        )

        self.entry_inicio_minuto.pack(
            side="left",
            padx=4
        )

        # --------------------------------------------------
        # BOTÕES
        # --------------------------------------------------

        botoes = ctk.CTkFrame(
            painel,
            fg_color="transparent"
        )

        botoes.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=8,
            pady=(4, 15)
        )

        ctk.CTkButton(
            botoes,
            text="✓ APLICAR CONFIGURAÇÃO",
            command=self.aplicar_configuracao_interface
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=4
        )

        ctk.CTkButton(
            botoes,
            text="💾 SALVAR RECEITA",
            command=self.salvar_receita
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=4
        )

        self.preencher_configuracao()

    # ======================================================
    # CAMPO DE CONFIGURAÇÃO
    # ======================================================

    def criar_campo_config(
        self,
        parent,
        titulo,
        chave
    ):

        linha = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        linha.pack(
            fill="x",
            padx=20,
            pady=2
        )

        ctk.CTkLabel(
            linha,
            text=titulo,
            width=190,
            anchor="w"
        ).pack(
            side="left"
        )

        entry = ctk.CTkEntry(
            linha,
            width=90
        )

        entry.pack(
            side="right"
        )

        self.entries_config[chave] = entry

    # ======================================================
    # PREENCHER CONFIGURAÇÃO
    # ======================================================

    def preencher_configuracao(self):

        config = self.horta.config

        valores = config.snapshot()

        for chave, entry in self.entries_config.items():

            entry.delete(
                0,
                "end"
            )

            entry.insert(
                0,
                str(valores[chave])
            )

        self.entry_nome_cultivo.delete(
            0,
            "end"
        )

        self.entry_nome_cultivo.insert(
            0,
            config.nome_cultivo
        )

        self.combo_fase.set(
            config.fase
        )

        self.entry_fotoperiodo.delete(
            0,
            "end"
        )

        self.entry_fotoperiodo.insert(
            0,
            str(config.fotoperiodo_horas)
        )

        self.entry_inicio_hora.delete(
            0,
            "end"
        )

        self.entry_inicio_hora.insert(
            0,
            f"{config.inicio_luz_hora:02d}"
        )

        self.entry_inicio_minuto.delete(
            0,
            "end"
        )

        self.entry_inicio_minuto.insert(
            0,
            f"{config.inicio_luz_minuto:02d}"
        )

    # ======================================================
    # CARREGAR CULTURA
    # ======================================================

    def carregar_cultura(
        self,
        nome
    ):

        try:

            self.horta.selecionar_cultura(
                nome
            )

            self.preencher_configuracao()

            self.atualizar_interface()

        except Exception as erro:

            print(
                "Erro ao carregar cultura:",
                erro
            )

    # ======================================================
    # APLICAR CONFIGURAÇÃO
    # ======================================================

    def aplicar_configuracao_interface(self):

        try:

            valores = {}

            for chave, entry in self.entries_config.items():

                valores[chave] = float(
                    entry.get()
                )

            config = ConfiguracaoCultivo(

                nome=self.combo_cultura.get(),

                nome_cultivo=(
                    self.entry_nome_cultivo.get()
                    or "Cultivo #01"
                ),

                fase=self.combo_fase.get(),

                ph_min=valores["ph_min"],
                ph_max=valores["ph_max"],

                ec_min=valores["ec_min"],
                ec_max=valores["ec_max"],

                temperatura_ar_min=(
                    valores["temperatura_ar_min"]
                ),

                temperatura_ar_max=(
                    valores["temperatura_ar_max"]
                ),

                temperatura_agua_min=(
                    valores["temperatura_agua_min"]
                ),

                temperatura_agua_max=(
                    valores["temperatura_agua_max"]
                ),

                umidade_ar_min=(
                    valores["umidade_ar_min"]
                ),

                umidade_ar_max=(
                    valores["umidade_ar_max"]
                ),

                fotoperiodo_horas=float(
                    self.entry_fotoperiodo.get()
                ),

                inicio_luz_hora=int(
                    self.entry_inicio_hora.get()
                ),

                inicio_luz_minuto=int(
                    self.entry_inicio_minuto.get()
                )
            )

            self.horta.aplicar_configuracao(
                config
            )

            self.atualizar_interface()

            print(
                "Configuração aplicada."
            )

        except Exception as erro:

            print(
                "ERRO NA CONFIGURAÇÃO:",
                erro
            )

    # ======================================================
    # SALVAR RECEITA
    # ======================================================

    def salvar_receita(self):

        try:

            self.aplicar_configuracao_interface()

            dados = self.horta.config.snapshot()

            pasta = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                ),
                "receitas"
            )

            os.makedirs(
                pasta,
                exist_ok=True
            )

            nome = (
                self.horta.config.nome
                .lower()
                .replace(" ", "_")
                .replace("ã", "a")
                .replace("á", "a")
            )

            caminho = os.path.join(
                pasta,
                f"{nome}_{self.horta.config.fase.lower()}.json"
            )

            with open(
                caminho,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    dados,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

            print(
                f"Receita salva em:\n{caminho}"
            )

        except Exception as erro:

            print(
                "ERRO AO SALVAR:",
                erro
            )

    # ======================================================
    # SIMULAÇÃO
    # ======================================================

    def criar_simulacao(self):

        painel = self.tab_demo

        ctk.CTkLabel(
            painel,
            text="⚡ CONTROLE DA SIMULAÇÃO",
            font=("Arial", 23, "bold")
        ).pack(
            pady=(20, 10)
        )

        ctk.CTkLabel(
            painel,
            text="O multiplicador representa minutos virtuais por segundo real.",
            font=("Arial", 13)
        ).pack(
            pady=(0, 15)
        )

        self.label_velocidade = ctk.CTkLabel(
            painel,
            text="1x",
            font=("Arial", 25, "bold")
        )

        self.label_velocidade.pack()

        self.slider_velocidade = ctk.CTkSlider(
            painel,
            from_=0,
            to=1440,
            number_of_steps=144,
            command=self.mudar_velocidade
        )

        self.slider_velocidade.pack(
            fill="x",
            padx=100,
            pady=10
        )

        self.slider_velocidade.set(
            1
        )

        self.label_explicacao_velocidade = ctk.CTkLabel(
            painel,
            text="1 minuto virtual / segundo",
            font=("Arial", 14)
        )

        self.label_explicacao_velocidade.pack(
            pady=(0, 15)
        )

        linha = ctk.CTkFrame(
            painel,
            fg_color="transparent"
        )

        linha.pack(
            fill="x",
            padx=80,
            pady=10
        )

        botoes = [
            ("−10h", -600),
            ("−1h", -60),
            ("−10min", -10),
            ("+10min", 10),
            ("+1h", 60),
            ("+10h", 600)
        ]

        for texto, minutos in botoes:

            ctk.CTkButton(
                linha,
                text=texto,
                command=lambda m=minutos: (
                    self.avancar_tempo(m)
                )
            ).pack(
                side="left",
                expand=True,
                fill="x",
                padx=3
            )

        self.botao_demo = ctk.CTkButton(
            painel,
            text="▶ INICIAR MODO DEMONSTRAÇÃO",
            command=self.alternar_demonstracao,
            height=45
        )

        self.botao_demo.pack(
            fill="x",
            padx=100,
            pady=(25, 8)
        )

        ctk.CTkButton(
            painel,
            text="RESETAR HORTA",
            command=self.resetar
        ).pack(
            fill="x",
            padx=100,
            pady=5
        )

        ctk.CTkLabel(
            painel,
            text="Relógio virtual atual",
            font=("Arial", 15, "bold")
        ).pack(
            pady=(30, 5)
        )

        self.label_relogio_demo = ctk.CTkLabel(
            painel,
            text="13:00",
            font=("Arial", 45, "bold")
        )

        self.label_relogio_demo.pack()

    # ======================================================
    # CALLBACKS
    # ======================================================

    def mudar_temperatura_ar(self, valor):

        self.horta.alterar_temperatura_ar(
            valor
        )

        self.horta.diagnosticar()

    def mudar_umidade_ar(self, valor):

        self.horta.alterar_umidade_ar(
            valor
        )

        self.horta.diagnosticar()

    def mudar_temperatura_agua(self, valor):

        self.horta.alterar_temperatura_agua(
            valor
        )

        self.horta.diagnosticar()

    def mudar_ph(self, valor):

        self.horta.alterar_ph(
            valor
        )

        self.horta.diagnosticar()

    def mudar_ec(self, valor):

        self.horta.alterar_ec(
            valor
        )

        self.horta.diagnosticar()

    def mudar_nivel_agua(self, valor):

        self.horta.alterar_nivel_agua(
            valor
        )

        self.horta.diagnosticar()

    # ======================================================
    # AUTOMAÇÃO
    # ======================================================

    def alternar_automacao(self):

        self.automacao_ativa = (
            not self.automacao_ativa
        )

        self.botao_automacao.configure(
            text=(
                "AUTOMAÇÃO: LIGADA"
                if self.automacao_ativa
                else
                "AUTOMAÇÃO: DESLIGADA"
            )
        )

    # ======================================================
    # VELOCIDADE
    # ======================================================

    def mudar_velocidade(
        self,
        valor
    ):

        valor = float(valor)

        self.horta.configurar_velocidade_tempo(
            valor
        )

        if valor <= 0:

            texto = "PAUSADO"

            explicacao = (
                "Relógio parado"
            )

        elif valor < 60:

            texto = f"{valor:.0f}x"

            explicacao = (
                f"{valor:.0f} minutos virtuais / segundo"
            )

        elif valor % 60 == 0:

            horas = valor / 60

            texto = f"{valor:.0f}x"

            explicacao = (
                f"{horas:g} hora(s) virtual(is) / segundo"
            )

        else:

            texto = f"{valor:.0f}x"

            explicacao = (
                f"{valor:.0f} minutos virtuais / segundo"
            )

        self.label_velocidade.configure(
            text=texto
        )

        self.label_explicacao_velocidade.configure(
            text=explicacao
        )

    # ======================================================
    # DEMONSTRAÇÃO
    # ======================================================

    def alternar_demonstracao(self):

        self.demonstracao_ativa = (
            not self.demonstracao_ativa
        )

        if self.demonstracao_ativa:

            self.botao_demo.configure(
                text="■ PARAR MODO DEMONSTRAÇÃO"
            )

        else:

            self.botao_demo.configure(
                text="▶ INICIAR MODO DEMONSTRAÇÃO"
            )

    # ======================================================
    # AVANÇAR
    # ======================================================

    def avancar_tempo(
        self,
        minutos
    ):

        self.horta.avancar_tempo(
            minutos
        )

        self.atualizar_interface()

    # ======================================================
    # RESET
    # ======================================================

    def resetar(self):

        self.horta.resetar()

        self.atualizar_sliders()

        self.atualizar_interface()

    def atualizar_sliders(self):

        valores = {

            "Temperatura do ar":
                self.horta.temperatura_ar,

            "Umidade do ar":
                self.horta.umidade_ar,

            "Temperatura da água":
                self.horta.temperatura_agua,

            "pH":
                self.horta.ph,

            "EC":
                self.horta.ec,

            "Nível da água":
                self.horta.nivel_agua
        }

        for nome, valor in valores.items():

            if nome in self.sliders:

                self.sliders[nome].set(
                    valor
                )

    # ======================================================
    # ATUALIZAÇÃO
    # ======================================================

    def atualizar_interface(self):

        dados = self.horta.snapshot()

        self.label_cultivo.configure(
            text=f"🌱 {dados['cultivo']}"
        )

        self.label_nome_cultivo.configure(
            text=dados["nome_cultivo"]
        )

        self.label_fase.configure(
            text=dados["fase"]
        )

        self.label_status.configure(
            text=dados["status"]
        )

        self.label_saude.configure(
            text=f"SAÚDE: {dados['saude']}%"
        )

        self.barra_saude.set(
            dados["saude"] / 100
        )

        self.label_nivel.configure(
            text=(
                f"{dados['nivel_agua']:.0f}% — "
                f"{dados['nivel_agua_status']}"
            )
        )

        self.barra_agua.set(
            dados["nivel_agua"] / 100
        )

        hora = (
            f"{dados['hora_atual']:02d}:"
            f"{dados['minuto_atual']:02d}"
        )

        self.label_relogio.configure(
            text=hora
        )

        self.label_relogio_demo.configure(
            text=hora
        )

        self.label_periodo.configure(
            text=(
                "💡 LUZ LIGADA"
                if dados["periodo_luz"]
                else
                "🌙 LUZ DESLIGADA"
            )
        )

        self.label_ventilacao.configure(
            text=(
                "VENTILAÇÃO: LIGADA"
                if dados["ventilacao"]
                else
                "VENTILAÇÃO: DESLIGADA"
            )
        )

        self.label_bomba.configure(
            text=(
                "BOMBA: LIGADA"
                if dados["bomba"]
                else
                "BOMBA: DESLIGADA"
            )
        )

        self.label_iluminacao.configure(
            text=(
                "ILUMINAÇÃO: LIGADA"
                if dados["iluminacao"]
                else
                "ILUMINAÇÃO: DESLIGADA"
            )
        )

        horas = dados[
            "fotoperiodo_horas"
        ]

        horas_escuro = 24 - horas

        self.label_fotoperiodo.configure(
            text=(
                f"{horas:g}h LIGADA / "
                f"{horas_escuro:g}h DESLIGADA"
            )
        )

        self.label_inicio_luz.configure(
            text=(
                f"Início: "
                f"{dados['inicio_luz_hora']:02d}:"
                f"{dados['inicio_luz_minuto']:02d}"
            )
        )

    # ======================================================
    # LOOP
    # ======================================================

    def ciclo_interface(self):

        if self.demonstracao_ativa:

            self.horta.tick_tempo()

        if self.automacao_ativa:

            self.horta.executar_automacao()

        self.atualizar_interface()

        self.after(
            1000,
            self.ciclo_interface
        )