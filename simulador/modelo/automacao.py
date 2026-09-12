"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

AUTOMAÇÃO
============================================================

Camada responsável pelas decisões automáticas da Horta.

Arquitetura:

    SENSORES
       ↓
    HORTA
       ↓
    AUTOMAÇÃO
       ↓
    REGRAS
       ↓
    ATUADORES

A automação NÃO armazena os sensores.

Ela consulta o objeto Horta e decide quais atuadores
devem ser acionados.

Princípio importante:

    diagnóstico ≠ ação

O sistema pode detectar que pH ou EC estão fora da faixa
sem necessariamente possuir ainda um atuador físico capaz
de corrigir o problema.

Isso permite desenvolver o cérebro antes do hardware.

============================================================
"""


class Automacao:

    def __init__(self, horta):

        self.horta = horta

        # ==================================================
        # ESTADO DA AUTOMAÇÃO
        # ==================================================

        self.ultima_decisao = None

        self.historico = []

        # ==================================================
        # LIMITES DE SEGURANÇA
        # ==================================================

        self.nivel_minimo_bomba = 10.0

    # ======================================================
    # EXECUTAR CICLO COMPLETO
    # ======================================================

    def executar(self):

        decisoes = []

        # --------------------------------------------------
        # 1. PROTEÇÃO DA BOMBA
        # --------------------------------------------------

        decisao = self._controlar_bomba()

        if decisao:
            decisoes.append(decisao)

        # --------------------------------------------------
        # 2. VENTILAÇÃO
        # --------------------------------------------------

        decisao = self._controlar_ventilacao()

        if decisao:
            decisoes.append(decisao)

        # --------------------------------------------------
        # 3. ILUMINAÇÃO
        # --------------------------------------------------

        decisao = self._controlar_iluminacao()

        if decisao:
            decisoes.append(decisao)

        # --------------------------------------------------
        # 4. DIAGNÓSTICO QUÍMICO
        # --------------------------------------------------

        decisao = self._diagnosticar_ph()

        if decisao:
            decisoes.append(decisao)

        decisao = self._diagnosticar_ec()

        if decisao:
            decisoes.append(decisao)

        # --------------------------------------------------
        # 5. DIAGNÓSTICO GERAL
        # --------------------------------------------------

        self.horta.diagnosticar()

        resultado = {
            "decisoes": decisoes,
            "saude": self.horta.saude,
            "status": self.horta.status,
        }

        self.ultima_decisao = resultado

        self.historico.append(resultado)

        # --------------------------------------------------
        # LIMITA HISTÓRICO
        # --------------------------------------------------

        if len(self.historico) > 100:

            self.historico.pop(0)

        return resultado

    # ======================================================
    # BOMBA
    # ======================================================

    def _controlar_bomba(self):

        nivel = self.horta.nivel_agua

        # --------------------------------------------------
        # SEGURANÇA
        # --------------------------------------------------

        if nivel <= self.nivel_minimo_bomba:

            if self.horta.bomba:

                self.horta.desligar_bomba()

                return (
                    "BOMBA DESLIGADA: "
                    "nível de água insuficiente."
                )

            return None

        # --------------------------------------------------
        # IMPORTANTE
        #
        # A automação não liga a bomba continuamente.
        #
        # Futuramente teremos uma regra própria para
        # irrigação/circulação.
        # --------------------------------------------------

        return None

    # ======================================================
    # VENTILAÇÃO
    # ======================================================

    def _controlar_ventilacao(self):

        temperatura = (
            self.horta.temperatura_ar
        )

        limite = (
            self.horta.config
            .temperatura_ar_max
        )

        # --------------------------------------------------
        # ACIONAR
        # --------------------------------------------------

        if temperatura > limite:

            if not self.horta.ventilacao:

                self.horta.ligar_ventilacao()

                return (
                    "VENTILAÇÃO LIGADA: "
                    f"temperatura do ar {temperatura:.1f}°C "
                    f"> limite {limite:.1f}°C."
                )

            return None

        # --------------------------------------------------
        # DESLIGAR
        # --------------------------------------------------

        if self.horta.ventilacao:

            self.horta.desligar_ventilacao()

            return (
                "VENTILAÇÃO DESLIGADA: "
                f"temperatura do ar {temperatura:.1f}°C "
                f"dentro do limite."
            )

        return None

    # ======================================================
    # ILUMINAÇÃO
    # ======================================================

    def _controlar_iluminacao(self):

        deve_estar_ligada = (
            self.horta.esta_no_periodo_luz()
        )

        # --------------------------------------------------
        # LIGAR
        # --------------------------------------------------

        if deve_estar_ligada:

            if not self.horta.iluminacao:

                self.horta.ligar_iluminacao()

                return (
                    "ILUMINAÇÃO LIGADA: "
                    "dentro do período de luz."
                )

            return None

        # --------------------------------------------------
        # DESLIGAR
        # --------------------------------------------------

        if self.horta.iluminacao:

            self.horta.desligar_iluminacao()

            return (
                "ILUMINAÇÃO DESLIGADA: "
                "fora do período de luz."
            )

        return None

    # ======================================================
    # pH
    # ======================================================

    def _diagnosticar_ph(self):

        valor = self.horta.ph

        minimo = (
            self.horta.config.ph_min
        )

        maximo = (
            self.horta.config.ph_max
        )

        if valor < minimo:

            return (
                f"ALERTA pH: {valor:.2f} "
                f"< mínimo {minimo:.2f}."
            )

        if valor > maximo:

            return (
                f"ALERTA pH: {valor:.2f} "
                f"> máximo {maximo:.2f}."
            )

        return None

    # ======================================================
    # EC
    # ======================================================

    def _diagnosticar_ec(self):

        valor = self.horta.ec

        minimo = (
            self.horta.config.ec_min
        )

        maximo = (
            self.horta.config.ec_max
        )

        if valor < minimo:

            return (
                f"ALERTA EC: {valor:.2f} "
                f"< mínimo {minimo:.2f}."
            )

        if valor > maximo:

            return (
                f"ALERTA EC: {valor:.2f} "
                f"> máximo {maximo:.2f}."
            )

        return None

    # ======================================================
    # EXECUTAR VÁRIAS VEZES
    # ======================================================

    def executar_ciclo(self):

        return self.executar()

    # ======================================================
    # LIMPAR HISTÓRICO
    # ======================================================

    def limpar_historico(self):

        self.historico.clear()

        self.ultima_decisao = None

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "ultima_decisao":
                self.ultima_decisao,

            "historico":
                list(self.historico),

            "nivel_minimo_bomba":
                self.nivel_minimo_bomba,
        }