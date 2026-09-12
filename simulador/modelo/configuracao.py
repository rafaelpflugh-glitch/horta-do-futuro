"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

CONFIGURAÇÃO DE CULTIVO
============================================================

Representa uma cultura completa.

Uma cultura possui:

    - nome da espécie/cultura
    - nome individual do cultivo
    - fase atual
    - receitas específicas para cada fase

Exemplo:

    ALFACE
        SEMENTE
        MUDA
        VEGETATIVO

A receita da fase determina:

    - pH
    - EC
    - temperatura do ar
    - temperatura da água
    - umidade
    - fotoperíodo
    - horário de início da luz

IMPORTANTE:

    Cada fase possui sua própria receita.

    Portanto, ao mudar de:

        SEMENTE
            ↓
        MUDA
            ↓
        VEGETATIVO

    os parâmetros podem mudar automaticamente.

Compatibilidade:

    O modelo continua expondo propriedades como:

        config.ph_min
        config.ph_max
        config.ec_min
        config.fotoperiodo_horas

    Essas propriedades apontam sempre para a receita
    da fase atual.

============================================================
"""

from copy import deepcopy

from modelo.receita_fase import ReceitaFase


class ConfiguracaoCultivo:

    # ======================================================
    # FASES DISPONÍVEIS
    # ======================================================

    FASES_VALIDAS = (
        "SEMENTE",
        "MUDA",
        "VEGETATIVO",
    )

    # ======================================================
    # CAMPOS ACEITOS PELA ReceitaFase
    # ======================================================

    CAMPOS_RECEITA = (
        "nome",

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
        "inicio_luz_minuto",
    )

    # ======================================================
    # CONSTRUTOR
    # ======================================================

    def __init__(
        self,
        nome="ALFACE",
        nome_cultivo="Alface Experimental #01",
        fase="VEGETATIVO",

        # --------------------------------------------------
        # Parâmetros legados / compatibilidade
        # --------------------------------------------------

        ph_min=5.5,
        ph_max=6.5,

        ec_min=1.0,
        ec_max=1.8,

        temperatura_ar_min=18.0,
        temperatura_ar_max=26.0,

        temperatura_agua_min=18.0,
        temperatura_agua_max=26.0,

        umidade_ar_min=50.0,
        umidade_ar_max=80.0,

        fotoperiodo_horas=18.0,

        inicio_luz_hora=6,
        inicio_luz_minuto=0,

        receitas=None
    ):

        # ==================================================
        # IDENTIFICAÇÃO
        # ==================================================

        self.nome = (
            str(nome)
            .strip()
            .upper()
        )

        self.nome_cultivo = (
            str(nome_cultivo)
            .strip()
        )

        # ==================================================
        # FASE ATUAL
        # ==================================================

        self.fase = (
            str(fase)
            .strip()
            .upper()
        )

        if self.fase not in self.FASES_VALIDAS:

            raise ValueError(
                f"Fase inválida: {self.fase}. "
                f"Use: {', '.join(self.FASES_VALIDAS)}"
            )

        # ==================================================
        # RECEITAS
        # ==================================================

        self.receitas = {}

        # --------------------------------------------------
        # Carrega receitas recebidas.
        #
        # Pode receber:
        #
        #   ReceitaFase
        #
        # ou:
        #
        #   dict
        #
        # inclusive um dict vindo diretamente de
        # ConfiguracaoCultivo.snapshot().
        # --------------------------------------------------

        if receitas:

            if not isinstance(
                receitas,
                dict
            ):

                raise TypeError(
                    "O parâmetro 'receitas' deve ser "
                    "um dicionário."
                )

            for nome_fase, receita in receitas.items():

                nome_fase = (
                    str(nome_fase)
                    .strip()
                    .upper()
                )

                if nome_fase not in self.FASES_VALIDAS:

                    continue

                # ------------------------------------------
                # Receita já pronta
                # ------------------------------------------

                if isinstance(
                    receita,
                    ReceitaFase
                ):

                    copia = deepcopy(
                        receita
                    )

                    copia.nome = nome_fase

                    self.receitas[
                        nome_fase
                    ] = copia

                # ------------------------------------------
                # Receita serializada
                # ------------------------------------------

                elif isinstance(
                    receita,
                    dict
                ):

                    self.receitas[
                        nome_fase
                    ] = self._receita_a_partir_dict(
                        receita,
                        nome_fase
                    )

                else:

                    raise TypeError(
                        f"Receita da fase "
                        f"'{nome_fase}' deve ser "
                        f"ReceitaFase ou dict."
                    )

        # ==================================================
        # RECEITA LEGADA DO VEGETATIVO
        # ==================================================
        #
        # Se estamos carregando um arquivo antigo que não
        # possuía receitas por fase, os parâmetros antigos
        # são transformados em uma receita VEGETATIVO.
        #
        # Se já existe uma receita VEGETATIVO válida,
        # ela tem prioridade.
        # ==================================================

        if "VEGETATIVO" not in self.receitas:

            self.receitas[
                "VEGETATIVO"
            ] = ReceitaFase(

                nome="VEGETATIVO",

                ph_min=ph_min,
                ph_max=ph_max,

                ec_min=ec_min,
                ec_max=ec_max,

                temperatura_ar_min=(
                    temperatura_ar_min
                ),

                temperatura_ar_max=(
                    temperatura_ar_max
                ),

                temperatura_agua_min=(
                    temperatura_agua_min
                ),

                temperatura_agua_max=(
                    temperatura_agua_max
                ),

                umidade_ar_min=(
                    umidade_ar_min
                ),

                umidade_ar_max=(
                    umidade_ar_max
                ),

                fotoperiodo_horas=(
                    fotoperiodo_horas
                ),

                inicio_luz_hora=(
                    inicio_luz_hora
                ),

                inicio_luz_minuto=(
                    inicio_luz_minuto
                )
            )

        # ==================================================
        # GARANTIR TODAS AS FASES
        # ==================================================

        self._garantir_receita_fase(
            "SEMENTE"
        )

        self._garantir_receita_fase(
            "MUDA"
        )

        self._garantir_receita_fase(
            "VEGETATIVO"
        )

    # ======================================================
    # CONVERTER DICT → ReceitaFase
    # ======================================================

    @classmethod
    def _receita_a_partir_dict(
        cls,
        dados,
        nome_fase
    ):
        """
        Reconstrói uma ReceitaFase a partir de um dicionário.

        Isso é importante porque snapshot() pode conter
        informações calculadas/formatadas como:

            inicio_luz
            fim_luz
            fotoperiodo

        Esses campos não fazem parte do construtor da
        ReceitaFase e, portanto, precisam ser ignorados.
        """

        if not isinstance(
            dados,
            dict
        ):

            raise TypeError(
                "Os dados da receita devem ser "
                "um dicionário."
            )

        argumentos = {}

        for campo in cls.CAMPOS_RECEITA:

            if campo in dados:

                argumentos[
                    campo
                ] = dados[campo]

        # --------------------------------------------------
        # Nome da fase é controlado pela Configuração.
        # --------------------------------------------------

        argumentos["nome"] = nome_fase

        return ReceitaFase(
            **argumentos
        )

    # ======================================================
    # CRIAR RECEITA PADRÃO
    # ======================================================

    def _garantir_receita_fase(
        self,
        fase
    ):

        fase = (
            str(fase)
            .strip()
            .upper()
        )

        if fase not in self.FASES_VALIDAS:

            raise ValueError(
                f"Fase inválida: {fase}"
            )

        # --------------------------------------------------
        # Já existe
        # --------------------------------------------------

        if fase in self.receitas:

            return

        # --------------------------------------------------
        # Usa VEGETATIVO como base
        # --------------------------------------------------

        base = self.receitas[
            "VEGETATIVO"
        ]

        receita = deepcopy(
            base
        )

        receita.nome = fase

        # ==================================================
        # REGRAS INICIAIS
        # ==================================================
        #
        # Estes valores são apenas uma BASE inicial.
        #
        # Não estamos afirmando que todas as espécies
        # possuem exatamente as mesmas necessidades.
        #
        # O painel poderá alterar cada fase individualmente.
        # ==================================================

        if fase == "SEMENTE":

            receita.fotoperiodo_horas = 16.0

        elif fase == "MUDA":

            receita.fotoperiodo_horas = 18.0

        self.receitas[
            fase
        ] = receita

    # ======================================================
    # RECEITA DA FASE ATUAL
    # ======================================================

    @property
    def receita_atual(self):

        return self.receitas[
            self.fase
        ]

    # ======================================================
    # ALTERAR FASE
    # ======================================================

    def definir_fase(
        self,
        fase
    ):

        fase = (
            str(fase)
            .strip()
            .upper()
        )

        if fase not in self.FASES_VALIDAS:

            raise ValueError(
                f"Fase inválida: {fase}. "
                f"Use: {', '.join(self.FASES_VALIDAS)}"
            )

        self._garantir_receita_fase(
            fase
        )

        self.fase = fase

    # ======================================================
    # OBTER RECEITA
    # ======================================================

    def obter_receita(
        self,
        fase=None
    ):

        if fase is None:

            fase = self.fase

        fase = (
            str(fase)
            .strip()
            .upper()
        )

        if fase not in self.FASES_VALIDAS:

            raise ValueError(
                f"Fase inválida: {fase}"
            )

        self._garantir_receita_fase(
            fase
        )

        return self.receitas[
            fase
        ]

    # ======================================================
    # DEFINIR RECEITA
    # ======================================================

    def definir_receita(
        self,
        fase,
        receita
    ):

        fase = (
            str(fase)
            .strip()
            .upper()
        )

        if fase not in self.FASES_VALIDAS:

            raise ValueError(
                f"Fase inválida: {fase}"
            )

        if not isinstance(
            receita,
            ReceitaFase
        ):

            raise TypeError(
                "A receita deve ser "
                "uma ReceitaFase."
            )

        copia = deepcopy(
            receita
        )

        copia.nome = fase

        self.receitas[
            fase
        ] = copia

    # ======================================================
    # PROPRIEDADES COMPATÍVEIS COM O MOTOR ANTIGO
    # ======================================================

    @property
    def ph_min(self):

        return (
            self.receita_atual
            .ph_min
        )

    @ph_min.setter
    def ph_min(self, valor):

        self.receita_atual.ph_min = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def ph_max(self):

        return (
            self.receita_atual
            .ph_max
        )

    @ph_max.setter
    def ph_max(self, valor):

        self.receita_atual.ph_max = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def ec_min(self):

        return (
            self.receita_atual
            .ec_min
        )

    @ec_min.setter
    def ec_min(self, valor):

        self.receita_atual.ec_min = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def ec_max(self):

        return (
            self.receita_atual
            .ec_max
        )

    @ec_max.setter
    def ec_max(self, valor):

        self.receita_atual.ec_max = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def temperatura_ar_min(self):

        return (
            self.receita_atual
            .temperatura_ar_min
        )

    @temperatura_ar_min.setter
    def temperatura_ar_min(self, valor):

        self.receita_atual.temperatura_ar_min = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def temperatura_ar_max(self):

        return (
            self.receita_atual
            .temperatura_ar_max
        )

    @temperatura_ar_max.setter
    def temperatura_ar_max(self, valor):

        self.receita_atual.temperatura_ar_max = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def temperatura_agua_min(self):

        return (
            self.receita_atual
            .temperatura_agua_min
        )

    @temperatura_agua_min.setter
    def temperatura_agua_min(self, valor):

        self.receita_atual.temperatura_agua_min = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def temperatura_agua_max(self):

        return (
            self.receita_atual
            .temperatura_agua_max
        )

    @temperatura_agua_max.setter
    def temperatura_agua_max(self, valor):

        self.receita_atual.temperatura_agua_max = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def umidade_ar_min(self):

        return (
            self.receita_atual
            .umidade_ar_min
        )

    @umidade_ar_min.setter
    def umidade_ar_min(self, valor):

        self.receita_atual.umidade_ar_min = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def umidade_ar_max(self):

        return (
            self.receita_atual
            .umidade_ar_max
        )

    @umidade_ar_max.setter
    def umidade_ar_max(self, valor):

        self.receita_atual.umidade_ar_max = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def fotoperiodo_horas(self):

        return (
            self.receita_atual
            .fotoperiodo_horas
        )

    @fotoperiodo_horas.setter
    def fotoperiodo_horas(self, valor):

        self.receita_atual.fotoperiodo_horas = (
            float(valor)
        )

    # ------------------------------------------------------

    @property
    def inicio_luz_hora(self):

        return (
            self.receita_atual
            .inicio_luz_hora
        )

    @inicio_luz_hora.setter
    def inicio_luz_hora(self, valor):

        self.receita_atual.inicio_luz_hora = (
            int(valor)
        )

    # ------------------------------------------------------

    @property
    def inicio_luz_minuto(self):

        return (
            self.receita_atual
            .inicio_luz_minuto
        )

    @inicio_luz_minuto.setter
    def inicio_luz_minuto(self, valor):

        self.receita_atual.inicio_luz_minuto = (
            int(valor)
        )

    # ======================================================
    # CONFIGURAR FOTOPERÍODO
    # ======================================================

    def configurar_fotoperiodo(
        self,
        horas,
        hora_inicio,
        minuto_inicio
    ):

        horas = float(
            horas
        )

        hora_inicio = int(
            hora_inicio
        )

        minuto_inicio = int(
            minuto_inicio
        )

        if horas < 0:

            raise ValueError(
                "O fotoperíodo não pode ser negativo."
            )

        if horas > 24:

            raise ValueError(
                "O fotoperíodo não pode "
                "ultrapassar 24 horas."
            )

        if not 0 <= hora_inicio <= 23:

            raise ValueError(
                "A hora de início deve estar "
                "entre 0 e 23."
            )

        if not 0 <= minuto_inicio <= 59:

            raise ValueError(
                "O minuto de início deve estar "
                "entre 0 e 59."
            )

        self.receita_atual.fotoperiodo_horas = (
            horas
        )

        self.receita_atual.inicio_luz_hora = (
            hora_inicio
        )

        self.receita_atual.inicio_luz_minuto = (
            minuto_inicio
        )

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        receita = (
            self.receita_atual.snapshot()
        )

        resultado = {

            # ------------------------------------------------
            # IDENTIFICAÇÃO
            # ------------------------------------------------

            "nome":
                self.nome,

            "nome_cultivo":
                self.nome_cultivo,

            "fase":
                self.fase,

            # ------------------------------------------------
            # PARÂMETROS DA FASE ATUAL
            #
            # Mantidos no nível superior para compatibilidade
            # com o código antigo.
            # ------------------------------------------------

            "ph_min":
                receita["ph_min"],

            "ph_max":
                receita["ph_max"],

            "ec_min":
                receita["ec_min"],

            "ec_max":
                receita["ec_max"],

            "temperatura_ar_min":
                receita["temperatura_ar_min"],

            "temperatura_ar_max":
                receita["temperatura_ar_max"],

            "temperatura_agua_min":
                receita["temperatura_agua_min"],

            "temperatura_agua_max":
                receita["temperatura_agua_max"],

            "umidade_ar_min":
                receita["umidade_ar_min"],

            "umidade_ar_max":
                receita["umidade_ar_max"],

            "fotoperiodo_horas":
                receita["fotoperiodo_horas"],

            "inicio_luz_hora":
                receita["inicio_luz_hora"],

            "inicio_luz_minuto":
                receita["inicio_luz_minuto"],

            # ------------------------------------------------
            # TODAS AS RECEITAS
            # ------------------------------------------------

            "receitas":
                {
                    nome: receita.snapshot()
                    for nome, receita
                    in self.receitas.items()
                }
        }

        return resultado