"""
============================================================
HORTA DO FUTURO
RECEITA NUTRITIVA
============================================================

Define uma receita de preparo de solução nutritiva.

A receita não executa nenhuma dosagem.

Ela apenas descreve:

    - quais fertilizantes/insumos participam;
    - quanto utilizar por litro;
    - volume de solução;
    - fase do cultivo;
    - pH alvo;
    - EC alvo;
    - observações.

IMPORTANTE:

A receita NÃO tenta adivinhar quanto fertilizante é
necessário para atingir determinado EC.

A concentração real deve ser determinada através:

    fabricante
        ↓
    receita inicial
        ↓
    preparo
        ↓
    medição de EC
        ↓
    calibração

A execução da dosagem pertence ao SistemaDosagem.

============================================================
"""


class ReceitaNutritiva:

    # ======================================================
    # CONSTRUTOR
    # ======================================================

    def __init__(
        self,
        nome,
        fase=None,
        ph_min=None,
        ph_max=None,
        ec_min=None,
        ec_max=None,
        observacoes=None
    ):

        self.nome = str(
            nome
        ).strip()

        if not self.nome:

            raise ValueError(
                "O nome da receita não pode ser vazio."
            )

        # --------------------------------------------------
        # FASE
        # --------------------------------------------------

        if fase is None:

            self.fase = None

        else:

            self.fase = (
                str(fase)
                .strip()
                .upper()
            )

        # --------------------------------------------------
        # pH
        # --------------------------------------------------

        self.ph_min = (
            None
            if ph_min is None
            else float(ph_min)
        )

        self.ph_max = (
            None
            if ph_max is None
            else float(ph_max)
        )

        if (
            self.ph_min is not None
            and self.ph_max is not None
            and self.ph_min > self.ph_max
        ):

            raise ValueError(
                "ph_min não pode ser maior que ph_max."
            )

        # --------------------------------------------------
        # EC
        # --------------------------------------------------

        self.ec_min = (
            None
            if ec_min is None
            else float(ec_min)
        )

        self.ec_max = (
            None
            if ec_max is None
            else float(ec_max)
        )

        if (
            self.ec_min is not None
            and self.ec_max is not None
            and self.ec_min > self.ec_max
        ):

            raise ValueError(
                "ec_min não pode ser maior que ec_max."
            )

        # --------------------------------------------------
        # OBSERVAÇÕES
        # --------------------------------------------------

        self.observacoes = (
            None
            if observacoes is None
            else str(observacoes)
        )

        # --------------------------------------------------
        # COMPONENTES
        # --------------------------------------------------
        #
        # Cada componente será armazenado assim:
        #
        # {
        #     "nome": "FERTILIZANTE A",
        #     "quantidade_por_litro": 2.0,
        #     "unidade": "ml"
        # }
        #
        # Isso permite futuramente utilizar:
        #
        # A + B
        # A + B + CALMAG
        # A + PH UP
        # etc.
        # --------------------------------------------------

        self.componentes = []

    # ======================================================
    # ADICIONAR COMPONENTE
    # ======================================================

    def adicionar_componente(
        self,
        nome,
        quantidade_por_litro,
        unidade="ml"
    ):

        nome = str(
            nome
        ).strip().upper()

        if not nome:

            raise ValueError(
                "O nome do componente não pode ser vazio."
            )

        quantidade_por_litro = float(
            quantidade_por_litro
        )

        if quantidade_por_litro <= 0:

            raise ValueError(
                "A quantidade por litro deve ser positiva."
            )

        unidade = str(
            unidade
        ).strip().lower()

        if not unidade:

            raise ValueError(
                "A unidade não pode ser vazia."
            )

        componente = {

            "nome":
                nome,

            "quantidade_por_litro":
                quantidade_por_litro,

            "unidade":
                unidade
        }

        self.componentes.append(
            componente
        )

    # ======================================================
    # REMOVER COMPONENTE
    # ======================================================

    def remover_componente(
        self,
        nome
    ):

        nome = str(
            nome
        ).strip().upper()

        for indice, componente in enumerate(
            self.componentes
        ):

            if componente["nome"] == nome:

                return self.componentes.pop(
                    indice
                )

        raise KeyError(
            f"Componente não encontrado: {nome}"
        )

    # ======================================================
    # LIMPAR COMPONENTES
    # ======================================================

    def limpar_componentes(self):

        self.componentes.clear()

    # ======================================================
    # OBTER COMPONENTE
    # ======================================================

    def obter_componente(
        self,
        nome
    ):

        nome = str(
            nome
        ).strip().upper()

        for componente in self.componentes:

            if componente["nome"] == nome:

                return componente

        raise KeyError(
            f"Componente não encontrado: {nome}"
        )

    # ======================================================
    # CALCULAR QUANTIDADE
    # ======================================================

    def calcular_quantidade(
        self,
        nome,
        volume_litros
    ):

        volume_litros = float(
            volume_litros
        )

        if volume_litros <= 0:

            raise ValueError(
                "O volume deve ser positivo."
            )

        componente = self.obter_componente(
            nome
        )

        quantidade = (
            componente["quantidade_por_litro"]
            * volume_litros
        )

        return {

            "nome":
                componente["nome"],

            "quantidade_por_litro":
                componente["quantidade_por_litro"],

            "volume_litros":
                volume_litros,

            "quantidade":
                round(
                    quantidade,
                    3
                ),

            "unidade":
                componente["unidade"]
        }

    # ======================================================
    # CALCULAR PREPARO COMPLETO
    # ======================================================

    def calcular_preparo(
        self,
        volume_litros
    ):

        volume_litros = float(
            volume_litros
        )

        if volume_litros <= 0:

            raise ValueError(
                "O volume deve ser positivo."
            )

        preparo = []

        for componente in self.componentes:

            quantidade = (
                componente["quantidade_por_litro"]
                * volume_litros
            )

            preparo.append({

                "nome":
                    componente["nome"],

                "quantidade_por_litro":
                    componente[
                        "quantidade_por_litro"
                    ],

                "volume_litros":
                    volume_litros,

                "quantidade":
                    round(
                        quantidade,
                        3
                    ),

                "unidade":
                    componente["unidade"]
            })

        return preparo

    # ======================================================
    # FAIXA DE PH
    # ======================================================

    def faixa_ph(self):

        if (
            self.ph_min is None
            or self.ph_max is None
        ):

            return None

        return {

            "min":
                self.ph_min,

            "max":
                self.ph_max
        }

    # ======================================================
    # FAIXA DE EC
    # ======================================================

    def faixa_ec(self):

        if (
            self.ec_min is None
            or self.ec_max is None
        ):

            return None

        return {

            "min":
                self.ec_min,

            "max":
                self.ec_max
        }

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "fase":
                self.fase,

            "ph_min":
                self.ph_min,

            "ph_max":
                self.ph_max,

            "ec_min":
                self.ec_min,

            "ec_max":
                self.ec_max,

            "observacoes":
                self.observacoes,

            "componentes":
                [
                    dict(componente)
                    for componente
                    in self.componentes
                ]
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            "ReceitaNutritiva("
            f"nome={self.nome!r}, "
            f"fase={self.fase!r}, "
            f"componentes={len(self.componentes)}"
            ")"
        )