"""
============================================================
HORTA DO FUTURO
AUTOMAÇÃO — SEGURANÇA
============================================================

Camada responsável por impedir que a automação execute
ações potencialmente perigosas.

A receita diz:

    "O que queremos?"

A segurança diz:

    "Até onde podemos ir?"

Nenhuma ação automática deve ignorar esta camada.
============================================================
"""


class ResultadoSeguranca:

    def __init__(
        self,
        permitido=True,
        motivo="OK",
        codigo="OK"
    ):

        self.permitido = bool(permitido)

        self.motivo = str(motivo)

        self.codigo = str(codigo)

    def snapshot(self):

        return {
            "permitido": self.permitido,
            "motivo": self.motivo,
            "codigo": self.codigo,
        }


class SegurancaAutomacao:

    def __init__(

        self,

        # ==================================================
        # DOSAGEM
        # ==================================================

        dose_maxima_ciclo_ml=10.0,

        dose_maxima_diaria_ml=100.0,

        intervalo_minimo_dosagem_min=5,

        maximo_tentativas_ciclo=5,

        # ==================================================
        # RESERVATÓRIO DE INSUMO
        # ==================================================

        nivel_minimo_reservatorio_ml=5.0,

        nivel_minimo_solucao_percentual=10.0,

        # ==================================================
        # MISTURA
        # ==================================================

        tempo_mistura_segundos=30,

        # ==================================================
        # LIMITES ABSOLUTOS
        # ==================================================

        ec_maximo_absoluto=4.0,

        ph_minimo_absoluto=3.0,

        ph_maximo_absoluto=10.0
    ):

        self.dose_maxima_ciclo_ml = float(
            dose_maxima_ciclo_ml
        )

        self.dose_maxima_diaria_ml = float(
            dose_maxima_diaria_ml
        )

        self.intervalo_minimo_dosagem_min = int(
            intervalo_minimo_dosagem_min
        )

        self.maximo_tentativas_ciclo = int(
            maximo_tentativas_ciclo
        )

        self.nivel_minimo_reservatorio_ml = float(
            nivel_minimo_reservatorio_ml
        )

        self.nivel_minimo_solucao_percentual = float(
            nivel_minimo_solucao_percentual
        )

        self.tempo_mistura_segundos = int(
            tempo_mistura_segundos
        )

        self.ec_maximo_absoluto = float(
            ec_maximo_absoluto
        )

        self.ph_minimo_absoluto = float(
            ph_minimo_absoluto
        )

        self.ph_maximo_absoluto = float(
            ph_maximo_absoluto
        )

    # ======================================================
    # VALIDAR DOSAGEM
    # ======================================================

    def validar_dose(
        self,
        dose_ml
    ):

        dose_ml = float(dose_ml)

        if dose_ml <= 0:

            return ResultadoSeguranca(
                permitido=False,
                motivo="Dose deve ser maior que zero.",
                codigo="DOSE_INVALIDA"
            )

        if dose_ml > self.dose_maxima_ciclo_ml:

            return ResultadoSeguranca(
                permitido=False,
                motivo="Dose excede o limite por ciclo.",
                codigo="DOSE_MAXIMA_CICLO"
            )

        return ResultadoSeguranca()

    # ======================================================
    # VALIDAR RESERVATÓRIO
    # ======================================================

    def validar_reservatorio(
        self,
        nivel_ml
    ):

        nivel_ml = float(nivel_ml)

        if nivel_ml < self.nivel_minimo_reservatorio_ml:

            return ResultadoSeguranca(
                permitido=False,
                motivo=(
                    "Reservatório de insumo "
                    "abaixo do mínimo."
                ),
                codigo="RESERVATORIO_BAIXO"
            )

        return ResultadoSeguranca()

    # ======================================================
    # VALIDAR NÍVEL DA SOLUÇÃO
    # ======================================================

    def validar_nivel_solucao(
        self,
        nivel_percentual
    ):

        nivel_percentual = float(
            nivel_percentual
        )

        if (
            nivel_percentual
            < self.nivel_minimo_solucao_percentual
        ):

            return ResultadoSeguranca(
                permitido=False,
                motivo=(
                    "Nível da solução "
                    "abaixo do mínimo."
                ),
                codigo="SOLUCAO_BAIXA"
            )

        return ResultadoSeguranca()

    # ======================================================
    # VALIDAR EC
    # ======================================================

    def validar_ec(
        self,
        ec
    ):

        ec = float(ec)

        if ec < 0:

            return ResultadoSeguranca(
                permitido=False,
                motivo="EC inválido.",
                codigo="EC_INVALIDO"
            )

        if ec > self.ec_maximo_absoluto:

            return ResultadoSeguranca(
                permitido=False,
                motivo="EC acima do limite absoluto.",
                codigo="EC_ABSOLUTO"
            )

        return ResultadoSeguranca()

    # ======================================================
    # VALIDAR PH
    # ======================================================

    def validar_ph(
        self,
        ph
    ):

        ph = float(ph)

        if ph < self.ph_minimo_absoluto:

            return ResultadoSeguranca(
                permitido=False,
                motivo="pH abaixo do limite absoluto.",
                codigo="PH_ABSOLUTO"
            )

        if ph > self.ph_maximo_absoluto:

            return ResultadoSeguranca(
                permitido=False,
                motivo="pH acima do limite absoluto.",
                codigo="PH_ABSOLUTO"
            )

        return ResultadoSeguranca()

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "dose_maxima_ciclo_ml":
                self.dose_maxima_ciclo_ml,

            "dose_maxima_diaria_ml":
                self.dose_maxima_diaria_ml,

            "intervalo_minimo_dosagem_min":
                self.intervalo_minimo_dosagem_min,

            "maximo_tentativas_ciclo":
                self.maximo_tentativas_ciclo,

            "nivel_minimo_reservatorio_ml":
                self.nivel_minimo_reservatorio_ml,

            "nivel_minimo_solucao_percentual":
                self.nivel_minimo_solucao_percentual,

            "tempo_mistura_segundos":
                self.tempo_mistura_segundos,

            "ec_maximo_absoluto":
                self.ec_maximo_absoluto,

            "ph_minimo_absoluto":
                self.ph_minimo_absoluto,

            "ph_maximo_absoluto":
                self.ph_maximo_absoluto,
        }