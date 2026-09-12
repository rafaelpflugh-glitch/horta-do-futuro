"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

DIAGNÓSTICO DE CULTIVO
============================================================

Responsável por transformar o estado atual da Horta em
um diagnóstico operacional único.

O diagnóstico NÃO executa ações.

Ele apenas observa e informa:

    - o que está dentro da faixa
    - o que está abaixo
    - o que está acima
    - o que está em condição crítica

A decisão de agir pertence ao ControladorAutomacao.
============================================================
"""


class DiagnosticoCultivo:

    def __init__(self, horta):

        self.horta = horta

    # ======================================================
    # DIAGNÓSTICO DE FAIXA
    # ======================================================

    @staticmethod
    def avaliar_faixa(
        parametro,
        atual,
        minimo,
        maximo,
        alvo=None
    ):

        atual = float(atual)
        minimo = float(minimo)
        maximo = float(maximo)

        if alvo is None:

            alvo = (
                minimo + maximo
            ) / 2

        alvo = float(alvo)

        if atual < minimo:

            estado = "BAIXO"

        elif atual > maximo:

            estado = "ALTO"

        else:

            estado = "OK"

        return {

            "parametro": parametro,

            "estado": estado,

            "atual": atual,

            "minimo": minimo,

            "maximo": maximo,

            "alvo": alvo,

            "fora_faixa": (
                estado != "OK"
            ),

            "diferenca_alvo": round(
                alvo - atual,
                4
            )
        }

    # ======================================================
    # EC
    # ======================================================

    def ec(self):

        receita = (
            self.horta.config
            .receita_atual
        )

        return self.avaliar_faixa(

            parametro="EC",

            atual=self.horta.ec,

            minimo=receita.ec_min,

            maximo=receita.ec_max,

            alvo=(
                receita.ec_min
                + receita.ec_max
            ) / 2
        )

    # ======================================================
    # pH
    # ======================================================

    def ph(self):

        receita = (
            self.horta.config
            .receita_atual
        )

        return self.avaliar_faixa(

            parametro="PH",

            atual=self.horta.ph,

            minimo=receita.ph_min,

            maximo=receita.ph_max,

            alvo=(
                receita.ph_min
                + receita.ph_max
            ) / 2
        )

    # ======================================================
    # TEMPERATURA DO AR
    # ======================================================

    def temperatura_ar(self):

        receita = (
            self.horta.config
            .receita_atual
        )

        return self.avaliar_faixa(

            parametro="TEMPERATURA_AR",

            atual=self.horta.temperatura_ar,

            minimo=(
                receita.temperatura_ar_min
            ),

            maximo=(
                receita.temperatura_ar_max
            )
        )

    # ======================================================
    # TEMPERATURA DA ÁGUA
    # ======================================================

    def temperatura_agua(self):

        receita = (
            self.horta.config
            .receita_atual
        )

        return self.avaliar_faixa(

            parametro="TEMPERATURA_AGUA",

            atual=self.horta.temperatura_agua,

            minimo=(
                receita.temperatura_agua_min
            ),

            maximo=(
                receita.temperatura_agua_max
            )
        )

    # ======================================================
    # UMIDADE DO AR
    # ======================================================

    def umidade_ar(self):

        receita = (
            self.horta.config
            .receita_atual
        )

        return self.avaliar_faixa(

            parametro="UMIDADE_AR",

            atual=self.horta.umidade_ar,

            minimo=(
                receita.umidade_ar_min
            ),

            maximo=(
                receita.umidade_ar_max
            )
        )

    # ======================================================
    # NÍVEL DA ÁGUA
    # ======================================================

    def nivel_agua(self):

        nivel = float(
            self.horta.nivel_agua
        )

        if nivel <= 10:

            estado = "CRITICO"

        elif nivel <= 25:

            estado = "BAIXO"

        else:

            estado = "OK"

        return {

            "parametro": "NIVEL_AGUA",

            "estado": estado,

            "atual": nivel,

            "percentual": nivel,

            "fora_faixa": (
                estado != "OK"
            )
        }

    # ======================================================
    # DIAGNÓSTICO COMPLETO
    # ======================================================

    def executar(self):

        resultados = {

            "ec": self.ec(),

            "ph": self.ph(),

            "temperatura_ar": (
                self.temperatura_ar()
            ),

            "temperatura_agua": (
                self.temperatura_agua()
            ),

            "umidade_ar": (
                self.umidade_ar()
            ),

            "nivel_agua": (
                self.nivel_agua()
            )
        }

        problemas = []

        criticos = []

        for nome, resultado in (
            resultados.items()
        ):

            estado = resultado["estado"]

            if resultado.get(
                "fora_faixa",
                False
            ):

                problemas.append(
                    nome
                )

            if estado == "CRITICO":

                criticos.append(
                    nome
                )

        if criticos:

            estado_geral = "CRITICO"

        elif problemas:

            estado_geral = "ATENCAO"

        else:

            estado_geral = "OK"

        return {

            "estado_geral":
                estado_geral,

            "problemas":
                problemas,

            "criticos":
                criticos,

            "parametros":
                resultados
        }

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return self.executar()