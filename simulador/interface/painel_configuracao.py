
"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

PAINEL DE CONFIGURAÇÃO DE CULTIVO
============================================================

Interface gráfica responsável por:

    - selecionar cultura
    - criar nova cultura
    - editar cultura
    - salvar cultura
    - excluir cultura
    - alterar parâmetros do cultivo
    - aplicar configuração à Horta

O painel NÃO contém a lógica do Digital Twin.

Ele apenas conversa com:

    GerenciadorCulturas
            ↓
    ConfiguracaoCultivo
            ↓
          Horta

============================================================
"""

import customtkinter as ctk
from tkinter import messagebox

from modelo.configuracao import ConfiguracaoCultivo
from modelo.gerenciador_culturas import GerenciadorCulturas


class PainelConfiguracao(ctk.CTkFrame):

    # ========================================================
    # CORES
    # ========================================================

    FUNDO = "#101412"
    FUNDO_CARD = "#18201C"
    FUNDO_INPUT = "#202A24"

    VERDE = "#39D353"
    VERDE_ESCURO = "#1F8F3A"
    VERDE_HOVER = "#2FB84A"

    BRANCO = "#F2F5F3"
    CINZA = "#AAB5AE"
    CINZA_ESCURO = "#66736B"

    VERMELHO = "#E05252"
    VERMELHO_HOVER = "#C83E3E"

    BORDA = "#2D3A32"

    # ========================================================
    # CONSTRUTOR
    # ========================================================

    def __init__(
        self,
        master,
        horta=None,
        callback_atualizacao=None
    ):

        super().__init__(
            master,
            fg_color=self.FUNDO,
            corner_radius=0
        )

        self.horta = horta

        self.callback_atualizacao = (
            callback_atualizacao
        )

        self.configuracao_atual = None
        self.nome_original = None

        self.entries = {}

        # ----------------------------------------------------
        # GRID PRINCIPAL
        # ----------------------------------------------------

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            1,
            weight=1
        )

        # ----------------------------------------------------
        # CONSTRUÇÃO
        # ----------------------------------------------------

        self._criar_cabecalho()

        self._criar_area_principal()

        self._criar_botoes()

        # ----------------------------------------------------
        # CARREGAR CULTURA INICIAL
        # ----------------------------------------------------

        self._atualizar_lista_culturas()

        culturas = GerenciadorCulturas.listar()

        if culturas:

            self._selecionar_cultura(
                culturas[0]
            )

    # ========================================================
    # CABEÇALHO
    # ========================================================

    def _criar_cabecalho(self):

        frame = ctk.CTkFrame(
            self,
            fg_color=self.FUNDO,
            corner_radius=0
        )

        frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=24,
            pady=(20, 12)
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        titulo = ctk.CTkLabel(
            frame,
            text="HORTA DO FUTURO",
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            ),
            text_color=self.VERDE
        )

        titulo.grid(
            row=0,
            column=0,
            sticky="w"
        )

        subtitulo = ctk.CTkLabel(
            frame,
            text="CONFIGURAÇÃO DE CULTIVO",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=self.CINZA
        )

        subtitulo.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 0)
        )

    # ========================================================
    # ÁREA PRINCIPAL
    # ========================================================

    def _criar_area_principal(self):

        self.area = ctk.CTkFrame(
            self,
            fg_color=self.FUNDO,
            corner_radius=0
        )

        self.area.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=24,
            pady=0
        )

        self.area.grid_columnconfigure(
            0,
            weight=1,
            uniform="colunas"
        )

        self.area.grid_columnconfigure(
            1,
            weight=1,
            uniform="colunas"
        )

        self.area.grid_rowconfigure(
            0,
            weight=1
        )

        self._criar_coluna_esquerda()

        self._criar_coluna_direita()

    # ========================================================
    # CARD
    # ========================================================

    def _criar_card(
        self,
        coluna
    ):

        card = ctk.CTkFrame(
            coluna,
            fg_color=self.FUNDO_CARD,
            border_width=1,
            border_color=self.BORDA,
            corner_radius=12
        )

        card.pack(
            fill="both",
            expand=True,
            padx=7,
            pady=5
        )

        return card

    # ========================================================
    # COLUNA ESQUERDA
    # ========================================================

    def _criar_coluna_esquerda(self):

        coluna = ctk.CTkFrame(
            self.area,
            fg_color=self.FUNDO,
            corner_radius=0
        )

        coluna.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        card = self._criar_card(
            coluna
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        titulo = ctk.CTkLabel(
            card,
            text="IDENTIFICAÇÃO",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=self.VERDE
        )

        titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(15, 10)
        )

        # ----------------------------------------------------
        # CULTURA
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Cultura",
            1
        )

        self.combo_cultura = ctk.CTkComboBox(
            card,
            values=[],
            height=34,
            fg_color=self.FUNDO_INPUT,
            border_color=self.BORDA,
            button_color=self.VERDE_ESCURO,
            button_hover_color=self.VERDE_HOVER,
            text_color=self.BRANCO,
            dropdown_fg_color=self.FUNDO_CARD,
            dropdown_hover_color=self.VERDE_ESCURO,
            dropdown_text_color=self.BRANCO,
            command=self._selecionar_cultura
        )

        self.combo_cultura.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # NOME DO CULTIVO
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Nome individual da plantação",
            3
        )

        self.entries["nome_cultivo"] = (
            self._criar_entry(
                card,
                4
            )
        )

        # ----------------------------------------------------
        # FASE
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Fase do cultivo",
            5
        )

        self.combo_fase = ctk.CTkComboBox(
            card,
            values=[
                "SEMENTE",
                "MUDAS",
                "VEGETATIVO",
                "FLORAÇÃO",
                "FRUTIFICAÇÃO",
                "COLHEITA"
            ],
            height=34,
            fg_color=self.FUNDO_INPUT,
            border_color=self.BORDA,
            button_color=self.VERDE_ESCURO,
            button_hover_color=self.VERDE_HOVER,
            text_color=self.BRANCO,
            dropdown_fg_color=self.FUNDO_CARD,
            dropdown_hover_color=self.VERDE_ESCURO,
            dropdown_text_color=self.BRANCO
        )

        self.combo_fase.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # PH
        # ----------------------------------------------------

        self._criar_label(
            card,
            "pH ideal — mínimo / máximo",
            7
        )

        self._criar_par(
            card,
            "ph_min",
            "ph_max",
            8
        )

        # ----------------------------------------------------
        # EC
        # ----------------------------------------------------

        self._criar_label(
            card,
            "EC ideal — mínimo / máximo",
            9
        )

        self._criar_par(
            card,
            "ec_min",
            "ec_max",
            10
        )

    # ========================================================
    # COLUNA DIREITA
    # ========================================================

    def _criar_coluna_direita(self):

        coluna = ctk.CTkFrame(
            self.area,
            fg_color=self.FUNDO,
            corner_radius=0
        )

        coluna.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        card = self._criar_card(
            coluna
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        titulo = ctk.CTkLabel(
            card,
            text="PARÂMETROS AMBIENTAIS",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=self.VERDE
        )

        titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(15, 10)
        )

        # ----------------------------------------------------
        # TEMPERATURA DO AR
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Temperatura do ar — °C",
            1
        )

        self._criar_par(
            card,
            "temperatura_ar_min",
            "temperatura_ar_max",
            2
        )

        # ----------------------------------------------------
        # TEMPERATURA DA ÁGUA
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Temperatura da água — °C",
            3
        )

        self._criar_par(
            card,
            "temperatura_agua_min",
            "temperatura_agua_max",
            4
        )

        # ----------------------------------------------------
        # UMIDADE
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Umidade do ar — %",
            5
        )

        self._criar_par(
            card,
            "umidade_ar_min",
            "umidade_ar_max",
            6
        )

        # ----------------------------------------------------
        # FOTOPERÍODO
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Fotoperíodo — horas",
            7
        )

        self.entries["fotoperiodo_horas"] = (
            self._criar_entry(
                card,
                8
            )
        )

        # ----------------------------------------------------
        # INÍCIO DA LUZ
        # ----------------------------------------------------

        self._criar_label(
            card,
            "Início da iluminação",
            9
        )

        frame_hora = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        frame_hora.grid(
            row=10,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 10)
        )

        frame_hora.grid_columnconfigure(
            0,
            weight=1
        )

        frame_hora.grid_columnconfigure(
            1,
            weight=1
        )

        self.entries["inicio_luz_hora"] = (
            self._criar_entry(
                frame_hora,
                0
            )
        )

        self.entries["inicio_luz_minuto"] = (
            self._criar_entry(
                frame_hora,
                1
            )
        )

    # ========================================================
    # LABEL
    # ========================================================

    def _criar_label(
        self,
        parent,
        texto,
        row
    ):

        label = ctk.CTkLabel(
            parent,
            text=texto,
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            ),
            text_color=self.CINZA
        )

        label.grid(
            row=row,
            column=0,
            sticky="w",
            padx=18,
            pady=(2, 3)
        )

        return label

    # ========================================================
    # ENTRY
    # ========================================================

    def _criar_entry(
        self,
        parent,
        row,
        column=0
    ):

        entry = ctk.CTkEntry(
            parent,
            height=34,
            fg_color=self.FUNDO_INPUT,
            border_color=self.BORDA,
            text_color=self.BRANCO,
            placeholder_text_color=self.CINZA_ESCURO
        )

        entry.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=18,
            pady=(0, 8)
        )

        return entry

    # ========================================================
    # PAR DE ENTRIES
    # ========================================================

    def _criar_par(
        self,
        parent,
        chave_min,
        chave_max,
        row
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        frame.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 8)
        )

        frame.grid_columnconfigure(
            0,
            weight=1,
            uniform="par"
        )

        frame.grid_columnconfigure(
            1,
            weight=1,
            uniform="par"
        )

        self.entries[chave_min] = (
            self._criar_entry(
                frame,
                0,
                0
            )
        )

        self.entries[chave_max] = (
            self._criar_entry(
                frame,
                0,
                1
            )
        )

    # ========================================================
    # BOTÕES
    # ========================================================

    def _criar_botoes(self):

        frame = ctk.CTkFrame(
            self,
            fg_color=self.FUNDO,
            corner_radius=0
        )

        frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=24,
            pady=(12, 20)
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        frame.grid_columnconfigure(
            1,
            weight=1
        )

        frame.grid_columnconfigure(
            2,
            weight=1
        )

        frame.grid_columnconfigure(
            3,
            weight=1
        )

        # ----------------------------------------------------
        # NOVA
        # ----------------------------------------------------

        btn_nova = ctk.CTkButton(
            frame,
            text="+ NOVA CULTURA",
            height=40,
            fg_color=self.VERDE_ESCURO,
            hover_color=self.VERDE_HOVER,
            text_color=self.BRANCO,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self._nova_cultura
        )

        btn_nova.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=4
        )

        # ----------------------------------------------------
        # SALVAR
        # ----------------------------------------------------

        btn_salvar = ctk.CTkButton(
            frame,
            text="SALVAR",
            height=40,
            fg_color=self.VERDE,
            hover_color=self.VERDE_HOVER,
            text_color="#071008",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self._salvar
        )

        btn_salvar.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=4
        )

        # ----------------------------------------------------
        # EDITAR
        # ----------------------------------------------------

        btn_editar = ctk.CTkButton(
            frame,
            text="EDITAR",
            height=40,
            fg_color=self.FUNDO_INPUT,
            hover_color=self.VERDE_ESCURO,
            border_width=1,
            border_color=self.BORDA,
            text_color=self.BRANCO,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self._editar
        )

        btn_editar.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=4
        )

        # ----------------------------------------------------
        # EXCLUIR
        # ----------------------------------------------------

        btn_excluir = ctk.CTkButton(
            frame,
            text="EXCLUIR",
            height=40,
            fg_color=self.VERMELHO,
            hover_color=self.VERMELHO_HOVER,
            text_color=self.BRANCO,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self._excluir
        )

        btn_excluir.grid(
            row=0,
            column=3,
            sticky="ew",
            padx=4
        )

    # ========================================================
    # LISTA DE CULTURAS
    # ========================================================

    def _atualizar_lista_culturas(
        self,
        selecionar=None
    ):

        culturas = GerenciadorCulturas.listar()

        self.combo_cultura.configure(
            values=culturas
        )

        if not culturas:

            return

        if selecionar is None:

            selecionar = culturas[0]

        if selecionar not in culturas:

            selecionar = culturas[0]

        self.combo_cultura.set(
            selecionar
        )

    # ========================================================
    # SELECIONAR CULTURA
    # ========================================================

    def _selecionar_cultura(
        self,
        nome
    ):

        try:

            configuracao = (
                GerenciadorCulturas.carregar(
                    nome
                )
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                str(erro)
            )

            return

        self.configuracao_atual = (
            configuracao
        )

        self.nome_original = (
            configuracao.nome
        )

        self._preencher_formulario(
            configuracao
        )

    # ========================================================
    # PREENCHER FORMULÁRIO
    # ========================================================

    def _preencher_formulario(
        self,
        configuracao
    ):

        campos = [
            "nome_cultivo",
            "ph_min",
            "ph_max",
            "ec_min",
            "ec_max",
            "temperatura_ar_min",
            "temperatura_ar_max",
            "temperatura_agua_min",
            "temperatura_agua_max",
            "umidade_ar_min",
            "umidade_ar_max",
            "fotoperiodo_horas",
            "inicio_luz_hora",
            "inicio_luz_minuto"
        ]

        for campo in campos:

            entry = self.entries.get(
                campo
            )

            if entry is None:

                continue

            entry.delete(
                0,
                "end"
            )

            entry.insert(
                0,
                str(
                    getattr(
                        configuracao,
                        campo
                    )
                )
            )

        self.combo_fase.set(
            configuracao.fase
        )

    # ========================================================
    # LER FORMULÁRIO
    # ========================================================

    def _ler_formulario(self):

        if self.configuracao_atual is None:

            raise ValueError(
                "Nenhuma cultura selecionada."
            )

        configuracao = (
            self.configuracao_atual
        )

        configuracao.nome_cultivo = (
            self.entries[
                "nome_cultivo"
            ].get().strip()
        )

        configuracao.fase = (
            self.combo_fase.get().strip()
        )

        campos_float = [
            "ph_min",
            "ph_max",
            "ec_min",
            "ec_max",
            "temperatura_ar_min",
            "temperatura_ar_max",
            "temperatura_agua_min",
            "temperatura_agua_max",
            "umidade_ar_min",
            "umidade_ar_max",
            "fotoperiodo_horas"
        ]

        for campo in campos_float:

            texto = self.entries[
                campo
            ].get().strip()

            if not texto:

                raise ValueError(
                    f"O campo '{campo}' "
                    "não pode ficar vazio."
                )

            try:

                valor = float(
                    texto.replace(
                        ",",
                        "."
                    )
                )

            except ValueError:

                raise ValueError(
                    f"Valor inválido em "
                    f"'{campo}'."
                )

            setattr(
                configuracao,
                campo,
                valor
            )

        campos_int = [
            "inicio_luz_hora",
            "inicio_luz_minuto"
        ]

        for campo in campos_int:

            texto = self.entries[
                campo
            ].get().strip()

            try:

                valor = int(
                    texto
                )

            except ValueError:

                raise ValueError(
                    f"Valor inválido em "
                    f"'{campo}'."
                )

            setattr(
                configuracao,
                campo,
                valor
            )

        self._validar_configuracao(
            configuracao
        )

        return configuracao

    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    def _validar_configuracao(
        self,
        configuracao
    ):

        if not configuracao.nome_cultivo:

            raise ValueError(
                "O nome individual do cultivo "
                "não pode ficar vazio."
            )

        if not configuracao.fase:

            raise ValueError(
                "Selecione uma fase."
            )

        pares = [
            (
                "ph_min",
                "ph_max",
                "pH"
            ),
            (
                "ec_min",
                "ec_max",
                "EC"
            ),
            (
                "temperatura_ar_min",
                "temperatura_ar_max",
                "temperatura do ar"
            ),
            (
                "temperatura_agua_min",
                "temperatura_agua_max",
                "temperatura da água"
            ),
            (
                "umidade_ar_min",
                "umidade_ar_max",
                "umidade"
            )
        ]

        for minimo, maximo, nome in pares:

            if getattr(
                configuracao,
                minimo
            ) > getattr(
                configuracao,
                maximo
            ):

                raise ValueError(
                    f"O mínimo de {nome} "
                    "não pode ser maior "
                    "que o máximo."
                )

        if not (
            0
            <= configuracao.inicio_luz_hora
            <= 23
        ):

            raise ValueError(
                "A hora inicial deve estar "
                "entre 0 e 23."
            )

        if not (
            0
            <= configuracao.inicio_luz_minuto
            <= 59
        ):

            raise ValueError(
                "O minuto inicial deve estar "
                "entre 0 e 59."
            )

        if not (
            0
            <= configuracao.fotoperiodo_horas
            <= 24
        ):

            raise ValueError(
                "O fotoperíodo deve estar "
                "entre 0 e 24 horas."
            )

    # ========================================================
    # NOVA CULTURA
    # ========================================================

    def _nova_cultura(self):

        configuracao = (
            GerenciadorCulturas.nova()
        )

        self.configuracao_atual = (
            configuracao
        )

        self.nome_original = None

        # ----------------------------------------------------
        # Adicionamos temporariamente a cultura ao combo.
        # Ela só vai existir no JSON após SALVAR.
        # ----------------------------------------------------

        culturas = GerenciadorCulturas.listar()

        valores = list(culturas)

        if configuracao.nome not in valores:

            valores.append(
                configuracao.nome
            )

        self.combo_cultura.configure(
            values=valores
        )

        self.combo_cultura.set(
            configuracao.nome
        )

        self._preencher_formulario(
            configuracao
        )

        self.entries[
            "nome_cultivo"
        ].focus_set()

    # ========================================================
    # SALVAR
    # ========================================================

    def _salvar(self):

        try:

            configuracao = (
                self._ler_formulario()
            )

            # ------------------------------------------------
            # Cultura nova
            # ------------------------------------------------

            if self.nome_original is None:

                if GerenciadorCulturas.existe(
                    configuracao.nome
                ):

                    raise ValueError(
                        "Já existe uma cultura "
                        f"chamada '{configuracao.nome}'."
                    )

                GerenciadorCulturas.salvar(
                    configuracao
                )

            # ------------------------------------------------
            # Cultura existente
            # ------------------------------------------------

            else:

                GerenciadorCulturas.atualizar(
                    self.nome_original,
                    configuracao
                )

            self.configuracao_atual = (
                configuracao
            )

            self.nome_original = (
                configuracao.nome
            )

            self._atualizar_lista_culturas(
                configuracao.nome
            )

            self._aplicar_na_horta(
                configuracao
            )

            messagebox.showinfo(
                "Cultura salva",
                "A configuração foi salva "
                "com sucesso."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro ao salvar",
                str(erro)
            )

    # ========================================================
    # EDITAR
    # ========================================================

    def _editar(self):

        if self.configuracao_atual is None:

            messagebox.showwarning(
                "Editar",
                "Nenhuma cultura selecionada."
            )

            return

        self.entries[
            "nome_cultivo"
        ].focus_set()

        messagebox.showinfo(
            "Modo de edição",
            "Altere os parâmetros desejados "
            "e clique em SALVAR."
        )

    # ========================================================
    # EXCLUIR
    # ========================================================

    def _excluir(self):

        if self.configuracao_atual is None:

            return

        nome = (
            self.configuracao_atual.nome
        )

        if GerenciadorCulturas.eh_padrao(
            nome
        ):

            messagebox.showwarning(
                "Cultura padrão",
                "Culturas padrão não podem "
                "ser excluídas."
            )

            return

        confirmar = messagebox.askyesno(
            "Excluir cultura",
            f"Excluir a cultura '{nome}'?"
        )

        if not confirmar:

            return

        try:

            GerenciadorCulturas.excluir(
                nome
            )

            culturas = (
                GerenciadorCulturas.listar()
            )

            if culturas:

                self._atualizar_lista_culturas(
                    culturas[0]
                )

                self._selecionar_cultura(
                    culturas[0]
                )

            else:

                self.configuracao_atual = None
                self.nome_original = None

            messagebox.showinfo(
                "Cultura excluída",
                "A cultura foi excluída."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro ao excluir",
                str(erro)
            )

    # ========================================================
    # APLICAR NA HORTA
    # ========================================================

    def _aplicar_na_horta(
        self,
        configuracao
    ):

        if self.horta is not None:

            self.horta.aplicar_configuracao(
                configuracao
            )

        if self.callback_atualizacao:

            self.callback_atualizacao(
                configuracao
            )

    # ========================================================
    # MÉTODO PÚBLICO
    # ========================================================

    def aplicar_atual(self):

        if self.configuracao_atual is None:

            return

        self._aplicar_na_horta(
            self.configuracao_atual
        )

