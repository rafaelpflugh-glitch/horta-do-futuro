"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN
RESERVATÓRIO DE CULTIVO
============================================================

Representa o reservatório principal da hidroponia.

Diferente de ReservatorioInsumo:

    ReservatorioInsumo
        -> guarda fertilizante / pH / suplemento

    ReservatorioCultivo
        -> guarda a solução nutritiva onde as raízes estão.

Neste estágio tudo é virtual.

============================================================
"""


class ReservatorioCultivo:

    def __init__(
        self,
        capacidade_litros,
        volume_litros=None,
    ):

        self.capacidade_litros = float(
            capacidade_litros
        )

        if self.capacidade_litros <= 0:

            raise ValueError(
                "A capacidade do reservatório "
                "deve ser positiva."
            )

        if volume_litros is None:

            volume_litros = (
                self.capacidade_litros
            )

        self.volume_litros = max(
            0.0,
            min(
                self.capacidade_litros,
                float(volume_litros)
            )
        )

        # ==================================================
        # PARÂMETROS DA SOLUÇÃO
        # ==================================================

        self.ph = 6.0

        self.ec = 0.0

        self.temperatura_agua = 22.0

    # ======================================================
    # NÍVEL
    # ======================================================

    @property
    def percentual(self):

        return (
            self.volume_litros
            / self.capacidade_litros
            * 100
        )

    @property
    def vazio(self):

        return self.volume_litros <= 0

    # ======================================================
    # ADICIONAR ÁGUA
    # ======================================================

    def adicionar_agua(
        self,
        litros
    ):

        litros = float(litros)

        if litros <= 0:

            raise ValueError(
                "A quantidade de água "
                "deve ser positiva."
            )

        self.volume_litros = min(
            self.capacidade_litros,
            self.volume_litros + litros
        )

    # ======================================================
    # RETIRAR SOLUÇÃO
    # ======================================================

    def retirar_solucao(
        self,
        litros
    ):

        litros = float(litros)

        if litros <= 0:

            raise ValueError(
                "A quantidade deve ser positiva."
            )

        if litros > self.volume_litros:

            raise RuntimeError(
                "Volume insuficiente "
                "no reservatório."
            )

        self.volume_litros -= litros

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "capacidade_litros":
                self.capacidade_litros,

            "volume_litros":
                round(
                    self.volume_litros,
                    3
                ),

            "percentual":
                round(
                    self.percentual,
                    2
                ),

            "vazio":
                self.vazio,

            "ph":
                self.ph,

            "ec":
                self.ec,

            "temperatura_agua":
                self.temperatura_agua,
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            "ReservatorioCultivo("
            f"capacidade="
            f"{self.capacidade_litros} L, "
            f"volume="
            f"{self.volume_litros} L"
            ")"
        )