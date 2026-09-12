"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN
MODELO DE INSUMO
============================================================

Representa qualquer produto físico que possa ser utilizado
pelo sistema de cultivo.

Exemplos:

    FERTILIZANTE_A
    FERTILIZANTE_B
    PH_UP
    PH_DOWN
    MICRONUTRIENTES
    SUPLEMENTO

O modelo NÃO assume que todo insumo é líquido.

Unidades possíveis:

    ml
    g

A unidade determina como o insumo será dosado futuramente.

============================================================
"""


class Insumo:

    TIPOS_VALIDOS = (
        "FERTILIZANTE",
        "CORRETIVO_PH",
        "MICRONUTRIENTE",
        "SUPLEMENTO",
        "OUTRO",
    )

    UNIDADES_VALIDAS = (
        "ml",
        "g",
    )

    def __init__(
        self,
        nome,
        tipo,
        unidade="ml",
        descricao=None,
        fabricante=None,
        produto=None,
    ):

        self.nome = (
            str(nome)
            .strip()
            .upper()
        )

        self.tipo = (
            str(tipo)
            .strip()
            .upper()
        )

        self.unidade = (
            str(unidade)
            .strip()
            .lower()
        )

        if self.tipo not in self.TIPOS_VALIDOS:

            raise ValueError(
                f"Tipo de insumo inválido: "
                f"{self.tipo}"
            )

        if self.unidade not in self.UNIDADES_VALIDAS:

            raise ValueError(
                f"Unidade inválida: "
                f"{self.unidade}. "
                f"Use: {self.UNIDADES_VALIDAS}"
            )

        self.descricao = descricao

        self.fabricante = fabricante

        self.produto = produto

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "tipo":
                self.tipo,

            "unidade":
                self.unidade,

            "descricao":
                self.descricao,

            "fabricante":
                self.fabricante,

            "produto":
                self.produto,
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            f"Insumo("
            f"nome='{self.nome}', "
            f"tipo='{self.tipo}', "
            f"unidade='{self.unidade}'"
            f")"
        )


class ReservatorioInsumo:

    def __init__(
        self,
        insumo,
        capacidade_ml,
        nivel_ml=None,
    ):

        if not isinstance(
            insumo,
            Insumo
        ):

            raise TypeError(
                "insumo deve ser uma "
                "instância de Insumo."
            )

        if insumo.unidade != "ml":

            raise ValueError(
                "ReservatorioInsumo trabalha "
                "com insumos líquidos em ml."
            )

        self.insumo = insumo

        self.capacidade_ml = float(
            capacidade_ml
        )

        if self.capacidade_ml <= 0:

            raise ValueError(
                "A capacidade deve ser positiva."
            )

        if nivel_ml is None:

            nivel_ml = (
                self.capacidade_ml
            )

        self.nivel_ml = max(
            0.0,
            min(
                self.capacidade_ml,
                float(nivel_ml)
            )
        )

    # ======================================================
    # ESTADO
    # ======================================================

    @property
    def vazio(self):

        return self.nivel_ml <= 0

    @property
    def percentual(self):

        return (
            self.nivel_ml
            / self.capacidade_ml
            * 100
        )

    # ======================================================
    # CONSUMIR
    # ======================================================

    def consumir(
        self,
        quantidade_ml
    ):

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "A quantidade deve ser positiva."
            )

        if quantidade_ml > self.nivel_ml:

            raise RuntimeError(
                f"Insumo insuficiente: "
                f"{self.insumo.nome}"
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
                "A quantidade deve ser positiva."
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

            "insumo":
                self.insumo.snapshot(),

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
                self.vazio,
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            "ReservatorioInsumo("
            f"insumo='{self.insumo.nome}', "
            f"capacidade_ml={self.capacidade_ml}, "
            f"nivel_ml={self.nivel_ml}"
            ")"
        )


class SistemaDosagem:

    """
    Gerencia os reservatórios de insumos líquidos.

    Neste estágio é uma simulação.

    Futuramente:

        SistemaDosagem
              ↓
           GPIO
              ↓
        MOSFET/relé
              ↓
        bomba peristáltica

    """

    def __init__(self):

        self.reservatorios = {}

        self.bombas_ativas = {}

        self.historico = []

    # ======================================================
    # ADICIONAR
    # ======================================================

    def adicionar_reservatorio(
        self,
        insumo,
        capacidade_ml,
        nivel_ml=None,
    ):

        if not isinstance(
            insumo,
            Insumo
        ):

            raise TypeError(
                "insumo deve ser uma "
                "instância de Insumo."
            )

        nome = insumo.nome

        if nome in self.reservatorios:

            raise ValueError(
                f"Já existe um reservatório "
                f"para {nome}."
            )

        reservatorio = ReservatorioInsumo(
            insumo=insumo,
            capacidade_ml=capacidade_ml,
            nivel_ml=nivel_ml,
        )

        self.reservatorios[
            nome
        ] = reservatorio

        self.bombas_ativas[
            nome
        ] = False

    # ======================================================
    # OBTER
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
                f"Reservatório não encontrado: "
                f"{nome}"
            )

        return self.reservatorios[
            nome
        ]

    # ======================================================
    # DOSAR
    # ======================================================

    def dosar(
        self,
        nome,
        quantidade_ml,
    ):

        reservatorio = (
            self.obter_reservatorio(nome)
        )

        quantidade = (
            reservatorio.consumir(
                quantidade_ml
            )
        )

        self.bombas_ativas[
            reservatorio.insumo.nome
        ] = True

        self.historico.append({

            "tipo":
                "DOSAGEM",

            "insumo":
                reservatorio.insumo.nome,

            "quantidade_ml":
                quantidade,
        })

        return quantidade

    # ======================================================
    # DESLIGAR BOMBAS
    # ======================================================

    def desligar_bombas(self):

        for nome in self.bombas_ativas:

            self.bombas_ativas[
                nome
            ] = False

    # ======================================================
    # STATUS
    # ======================================================

    def status_insumo(
        self,
        nome
    ):

        reservatorio = (
            self.obter_reservatorio(nome)
        )

        dados = reservatorio.snapshot()

        dados[
            "bomba_ativa"
        ] = self.bombas_ativas[
            reservatorio.insumo.nome
        ]

        return dados

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

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
                ),

            "historico":
                list(
                    self.historico
                ),
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            "SistemaDosagem("
            f"reservatorios="
            f"{len(self.reservatorios)}"
            ")"
        )