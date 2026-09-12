"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN
FERTILIZANTE
============================================================

Representa um fertilizante comercial.

O objetivo deste objeto é armazenar os dados encontrados
no rótulo/ficha técnica do fabricante.

Exemplo:

    HydroFert Orquídeas
    N   = 30%
    P2O5 = 9%
    K2O = 10%
    B   = 0,1%
    Zn  = 0,3%

IMPORTANTE:

Este objeto NÃO decide quanto fertilizante usar.

Ele apenas representa:

    "O QUE É ESTE PRODUTO?"

A quantidade utilizada pertence à ReceitaNutritiva.

============================================================
"""


class Fertilizante:

    # ======================================================
    # CONSTRUTOR
    # ======================================================

    def __init__(
        self,
        nome,
        fabricante=None,
        registro_mapa=None,
        tipo=None,
        solubilidade=None,
        rendimento_litros=None,
        composicao=None,
        observacoes=None
    ):

        self.nome = (
            str(nome)
            .strip()
        )

        if not self.nome:

            raise ValueError(
                "O nome do fertilizante "
                "não pode ser vazio."
            )

        self.fabricante = (
            None
            if fabricante is None
            else str(fabricante).strip()
        )

        self.registro_mapa = (
            None
            if registro_mapa is None
            else str(registro_mapa).strip()
        )

        self.tipo = (
            None
            if tipo is None
            else str(tipo).strip()
        )

        self.solubilidade = (
            None
            if solubilidade is None
            else str(solubilidade).strip()
        )

        if rendimento_litros is None:

            self.rendimento_litros = None

        else:

            self.rendimento_litros = float(
                rendimento_litros
            )

            if self.rendimento_litros <= 0:

                raise ValueError(
                    "O rendimento deve ser "
                    "maior que zero."
                )

        # --------------------------------------------------
        # Composição
        # --------------------------------------------------

        if composicao is None:

            composicao = {}

        if not isinstance(
            composicao,
            dict
        ):

            raise TypeError(
                "A composição deve ser "
                "um dicionário."
            )

        self.composicao = {}

        for nutriente, percentual in (
            composicao.items()
        ):

            chave = (
                str(nutriente)
                .strip()
            )

            valor = float(
                percentual
            )

            if valor < 0:

                raise ValueError(
                    f"O percentual de "
                    f"'{chave}' não pode "
                    f"ser negativo."
                )

            self.composicao[
                chave
            ] = valor

        self.observacoes = (
            None
            if observacoes is None
            else str(observacoes).strip()
        )

    # ======================================================
    # NUTRIENTE
    # ======================================================

    def percentual_nutriente(
        self,
        nutriente
    ):

        return self.composicao.get(
            str(nutriente).strip(),
            0.0
        )

    # ======================================================
    # MASSA DE NUTRIENTE
    # ======================================================

    def massa_nutriente(
        self,
        nutriente,
        massa_fertilizante_g
    ):
        """
        Calcula aproximadamente quantos gramas de um
        nutriente estão presentes em determinada massa
        de fertilizante.

        Exemplo:

            N = 30%

            10 g de fertilizante

            → 3 g de N

        """

        massa_fertilizante_g = float(
            massa_fertilizante_g
        )

        if massa_fertilizante_g < 0:

            raise ValueError(
                "A massa do fertilizante "
                "não pode ser negativa."
            )

        percentual = (
            self.percentual_nutriente(
                nutriente
            )
        )

        return (
            massa_fertilizante_g
            * percentual
            / 100
        )

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "fabricante":
                self.fabricante,

            "registro_mapa":
                self.registro_mapa,

            "tipo":
                self.tipo,

            "solubilidade":
                self.solubilidade,

            "rendimento_litros":
                self.rendimento_litros,

            "composicao":
                dict(
                    self.composicao
                ),

            "observacoes":
                self.observacoes,
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        n = self.composicao.get(
            "N",
            0
        )

        p = self.composicao.get(
            "P2O5",
            0
        )

        k = self.composicao.get(
            "K2O",
            0
        )

        return (
            "Fertilizante("
            f"nome={self.nome!r}, "
            f"N={n}%, "
            f"P2O5={p}%, "
            f"K2O={k}%"
            ")"
        )