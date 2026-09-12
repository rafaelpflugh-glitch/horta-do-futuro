
"""
============================================================
HORTA DO FUTURO
AUTOMAÇÃO — DOSAGEM

Sistema de insumos e bombas dosadoras do Digital Twin.

Responsabilidades:

    ReservatorioInsumo
        → armazena fisicamente o insumo virtual

    InsumoDosagem
        → descreve o que o insumo faz

    SistemaDosagem
        → administra reservatórios, insumos e bombas

IMPORTANTE:

    O controlador não deve conhecer a química do produto.

    Ele solicita:

        "preciso aumentar EC"

    e o SistemaDosagem responde:

        "use este insumo"

    A relação entre quantidade dosada e efeito simulado
    pertence ao InsumoDosagem.

Futuramente:

    InsumoDosagem
          ↓
    bomba virtual
          ↓
       ESP32
          ↓
    bomba peristáltica real

============================================================
"""


class ReservatorioInsumo:

    def __init__(
        self,
        nome,
        capacidade_ml,
        nivel_ml=None
    ):

        self.nome = str(nome).strip().upper()

        self.capacidade_ml = float(
            capacidade_ml
        )

        if self.capacidade_ml <= 0:

            raise ValueError(
                "A capacidade do reservatório deve ser positiva."
            )

        if nivel_ml is None:

            nivel_ml = capacidade_ml

        self.nivel_ml = max(
            0.0,
            min(
                self.capacidade_ml,
                float(nivel_ml)
            )
        )

    # ======================================================
    # DISPONIBILIDADE
    # ======================================================

    @property
    def vazio(self):

        return self.nivel_ml <= 0

    @property
    def percentual(self):

        if self.capacidade_ml <= 0:

            return 0.0

        return (
            self.nivel_ml
            / self.capacidade_ml
            * 100.0
        )

    # ======================================================
    # DOSAR
    # ======================================================

    def dosar(
        self,
        quantidade_ml
    ):

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "Quantidade de dosagem "
                "deve ser positiva."
            )

        if quantidade_ml > self.nivel_ml:

            raise RuntimeError(
                f"Reservatório {self.nome} "
                f"insuficiente."
            )

        self.nivel_ml -= quantidade_ml

        return quantidade_ml

    # ======================================================
    # REABASTECER
    # ======================================================

    def reabastecer(
        self,
        quantidade_ml
    ):

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "Quantidade de reabastecimento "
                "deve ser positiva."
            )

        self.nivel_ml = min(
            self.capacidade_ml,
            self.nivel_ml + quantidade_ml
        )

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "capacidade_ml":
                self.capacidade_ml,

            "nivel_ml":
                round(
                    self.nivel_ml,
                    3
                ),

            "percentual":
                round(
                    self.percentual,
                    2
                ),

            "vazio":
                self.vazio
        }


class InsumoDosagem:

    """
    Representa um produto/insumo que pode ser dosado.

    Exemplo:

        nome = "NUTRIENTE_A"

        funcao = "AUMENTAR_EC"

        efeito_por_ml = 0.02

    O efeito é propositalmente um modelo simplificado
    do Digital Twin.

    Não representa uma concentração química real.
    """

    FUNCOES_VALIDAS = (
        "AUMENTAR_EC",
        "REDUZIR_PH",
        "AUMENTAR_PH",
        "DILUIR",
        "REPOSICAO_AGUA",
    )

    def __init__(
        self,
        nome,
        funcao,
        efeito_por_ml=0.0,
        unidade_efeito="EC"
    ):

        self.nome = (
            str(nome)
            .strip()
            .upper()
        )

        self.funcao = (
            str(funcao)
            .strip()
            .upper()
        )

        if self.funcao not in self.FUNCOES_VALIDAS:

            raise ValueError(
                f"Função de insumo inválida: "
                f"{self.funcao}. "
                f"Use: {', '.join(self.FUNCOES_VALIDAS)}"
            )

        self.efeito_por_ml = float(
            efeito_por_ml
        )

        self.unidade_efeito = (
            str(unidade_efeito)
            .strip()
            .upper()
        )

        if self.efeito_por_ml < 0:

            raise ValueError(
                "O efeito por ml não pode ser negativo."
            )

    # ======================================================
    # CALCULAR EFEITO
    # ======================================================

    def calcular_efeito(
        self,
        quantidade_ml
    ):

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml < 0:

            raise ValueError(
                "A quantidade não pode ser negativa."
            )

        return (
            quantidade_ml
            * self.efeito_por_ml
        )

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "funcao":
                self.funcao,

            "efeito_por_ml":
                self.efeito_por_ml,

            "unidade_efeito":
                self.unidade_efeito
        }


class SistemaDosagem:

    """
    Gerenciador central dos insumos e bombas.

    O sistema conhece:

        - quais insumos existem
        - onde estão armazenados
        - qual função possuem
        - qual efeito possuem
        - estado das bombas

    O controlador não precisa conhecer esses detalhes.
    """

    def __init__(self):

        self.reservatorios = {}

        self.insumos = {}

        self.bombas_ativas = {}

    # ======================================================
    # CADASTRAR INSUMO
    # ======================================================

    def adicionar_insumo(
        self,
        nome,
        funcao,
        efeito_por_ml=0.0,
        unidade_efeito="EC"
    ):

        insumo = InsumoDosagem(

            nome=nome,

            funcao=funcao,

            efeito_por_ml=efeito_por_ml,

            unidade_efeito=unidade_efeito
        )

        self.insumos[
            insumo.nome
        ] = insumo

        return insumo

    # ======================================================
    # OBTER INSUMO
    # ======================================================

    def obter_insumo(
        self,
        nome
    ):

        nome = (
            str(nome)
            .strip()
            .upper()
        )

        if nome not in self.insumos:

            raise KeyError(
                f"Insumo não encontrado: {nome}"
            )

        return self.insumos[
            nome
        ]

    # ======================================================
    # ENCONTRAR INSUMO POR FUNÇÃO
    # ======================================================

    def encontrar_insumo(
        self,
        funcao
    ):

        funcao = (
            str(funcao)
            .strip()
            .upper()
        )

        for insumo in self.insumos.values():

            if insumo.funcao == funcao:

                return insumo

        return None

    # ======================================================
    # ADICIONAR RESERVATÓRIO
    # ======================================================

    def adicionar_reservatorio(
        self,
        nome,
        capacidade_ml,
        nivel_ml=None
    ):

        nome = (
            str(nome)
            .strip()
            .upper()
        )

        self.reservatorios[
            nome
        ] = ReservatorioInsumo(

            nome=nome,

            capacidade_ml=capacidade_ml,

            nivel_ml=nivel_ml
        )

        # Garante que exista estado para a bomba.
        self.bombas_ativas[
            nome
        ] = False

    # ======================================================
    # OBTER RESERVATÓRIO
    # ======================================================

    def obter_reservatorio(
        self,
        nome
    ):

        nome = (
            str(nome)
            .strip()
            .upper()
        )

        if nome not in self.reservatorios:

            raise KeyError(
                f"Reservatório não encontrado: {nome}"
            )

        return self.reservatorios[
            nome
        ]

    # ======================================================
    # VALIDAR DOSAGEM
    # ======================================================

    def pode_dosar(
        self,
        nome,
        quantidade_ml
    ):

        reservatorio = (
            self.obter_reservatorio(
                nome
            )
        )

        quantidade_ml = float(
            quantidade_ml
        )

        return (
            quantidade_ml > 0
            and
            quantidade_ml <= reservatorio.nivel_ml
        )

    # ======================================================
    # DOSAR
    # ======================================================

    def dosar(
        self,
        nome,
        quantidade_ml
    ):

        reservatorio = (
            self.obter_reservatorio(
                nome
            )
        )

        quantidade = (
            reservatorio.dosar(
                quantidade_ml
            )
        )

        self.bombas_ativas[
            reservatorio.nome
        ] = True

        return quantidade

    # ======================================================
    # DESLIGAR UMA BOMBA
    # ======================================================

    def desligar_bomba(
        self,
        nome
    ):

        nome = (
            str(nome)
            .strip()
            .upper()
        )

        if nome in self.bombas_ativas:

            self.bombas_ativas[
                nome
            ] = False

    # ======================================================
    # ALIAS DE COMPATIBILIDADE
    # ======================================================

    def parar_bomba(
        self,
        nome
    ):

        self.desligar_bomba(
            nome
        )

    # ======================================================
    # DESLIGAR TODAS AS BOMBAS
    # ======================================================

    def desligar_bombas(self):

        for nome in self.bombas_ativas:

            self.bombas_ativas[
                nome
            ] = False

    # ======================================================
    # CALCULAR EFEITO DO INSUMO
    # ======================================================

    def calcular_efeito(
        self,
        nome,
        quantidade_ml
    ):

        insumo = (
            self.obter_insumo(
                nome
            )
        )

        return insumo.calcular_efeito(
            quantidade_ml
        )

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "insumos":
                {
                    nome:
                        insumo.snapshot()

                    for nome, insumo
                    in self.insumos.items()
                },

            "reservatorios":
                {
                    nome:
                        reservatorio.snapshot()

                    for nome, reservatorio
                    in self.reservatorios.items()
                },

            "bombas_ativas":
                dict(
                    self.bombas_ativas
                )
        }

