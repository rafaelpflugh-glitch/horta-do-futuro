"""
============================================================
HORTA DO FUTURO
RELÓGIO DA GÊMEA DIGITAL
============================================================

Relógio central da simulação.

Este relógio reúne duas necessidades do projeto:

1. TEMPO REAL DA SIMULAÇÃO
   --------------------------------
   Mantém uma data/hora completa.

2. VELOCIDADE DA SIMULAÇÃO
   --------------------------------
   Permite acelerar a passagem do tempo.

Exemplos:

    1x
        tempo normal da simulação

    10x
        10 vezes mais rápido

    100x
        100 vezes mais rápido

Além disso, permite:

    - pausar
    - continuar
    - avançar minutos
    - avançar horas
    - avançar dias
    - definir data/hora
    - resetar
    - consultar tempo total simulado

IMPORTANTE:

Este módulo controla APENAS o tempo.

Ele não conhece:

    - planta
    - sensores
    - bombas
    - iluminação
    - ventilação
    - fertilizantes

Esses sistemas serão consumidores do relógio.

============================================================
"""

from datetime import datetime, timedelta


class RelogioSimulado:

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(
        self,
        data_inicial=None,
        velocidade=1.0
    ):
        """
        Cria o relógio da Gêmea Digital.

        velocidade representa quantas vezes o tempo
        da simulação será acelerado quando utilizado
        pelo ciclo automático.
        """

        if data_inicial is None:

            data_inicial = datetime.now()

        if not isinstance(
            data_inicial,
            datetime
        ):

            raise TypeError(
                "data_inicial deve ser um objeto datetime."
            )

        velocidade = float(
            velocidade
        )

        if velocidade <= 0:

            raise ValueError(
                "A velocidade deve ser maior que zero."
            )

        # --------------------------------------------------
        # Estado inicial
        # --------------------------------------------------

        self.data_inicial = data_inicial

        self.tempo_atual = data_inicial

        self.velocidade = velocidade

        self.pausado = False

        self.tempo_simulado_total = timedelta(0)

    # ======================================================
    # COMPATIBILIDADE COM O RELÓGIO ANTIGO
    # ======================================================

    @property
    def hora(self):
        """
        Retorna a hora atual da simulação.

        Compatibilidade com:

            modelo.relogio_virtual
        """

        return self.tempo_atual.hour

    # ------------------------------------------------------

    @property
    def minuto(self):
        """
        Retorna o minuto atual da simulação.

        Compatibilidade com:

            modelo.relogio_virtual
        """

        return self.tempo_atual.minute

    # ======================================================
    # TEMPO ATUAL
    # ======================================================

    def agora(self):

        return self.tempo_atual

    # ======================================================
    # DEFINIR HORA
    # ======================================================

    def definir_hora(
        self,
        hora,
        minuto
    ):
        """
        Define a hora da simulação.

        A data atual é preservada.
        """

        hora = int(hora)

        minuto = int(minuto)

        if hora < 0 or hora > 23:

            raise ValueError(
                "A hora deve estar entre 0 e 23."
            )

        if minuto < 0 or minuto > 59:

            raise ValueError(
                "O minuto deve estar entre 0 e 59."
            )

        self.tempo_atual = self.tempo_atual.replace(
            hour=hora,
            minute=minuto,
            second=0,
            microsecond=0
        )

    # ======================================================
    # AVANÇAR SEGUNDOS
    # ======================================================

    def avancar_segundos(
        self,
        segundos
    ):
        """
        Avança a simulação em segundos.

        O valor representa segundos VIRTUAIS.

        Se estiver pausado, nada acontece.
        """

        segundos = float(
            segundos
        )

        if segundos < 0:

            raise ValueError(
                "Não é permitido avançar tempo negativo."
            )

        if self.pausado:

            return self.tempo_atual

        intervalo = timedelta(
            seconds=segundos
        )

        self.tempo_atual += intervalo

        self.tempo_simulado_total += intervalo

        return self.tempo_atual

    # ======================================================
    # AVANÇAR MINUTOS
    # ======================================================

    def avancar_minutos(
        self,
        minutos
    ):
        """
        Avança minutos virtuais.
        """

        return self.avancar_segundos(
            float(minutos) * 60
        )

    # ------------------------------------------------------

    def avancar(
        self,
        minutos
    ):
        """
        Alias compatível com o relógio antigo.

        Exemplo:

            relogio.avancar(30)

        significa:

            avançar 30 minutos virtuais.
        """

        return self.avancar_minutos(
            minutos
        )

    # ======================================================
    # AVANÇAR HORAS
    # ======================================================

    def avancar_horas(
        self,
        horas
    ):
        """
        Avança horas virtuais.
        """

        return self.avancar_segundos(
            float(horas) * 3600
        )

    # ======================================================
    # AVANÇAR DIAS
    # ======================================================

    def avancar_dias(
        self,
        dias
    ):
        """
        Avança dias virtuais.
        """

        return self.avancar_segundos(
            float(dias) * 86400
        )

    # ======================================================
    # VELOCIDADE
    # ======================================================

    def definir_velocidade(
        self,
        velocidade
    ):
        """
        Define a velocidade da simulação.

        Exemplos:

            1
            10
            100
            1000
        """

        velocidade = float(
            velocidade
        )

        if velocidade <= 0:

            raise ValueError(
                "A velocidade deve ser maior que zero."
            )

        self.velocidade = velocidade

    # ------------------------------------------------------

    def configurar_velocidade(
        self,
        velocidade
    ):
        """
        Alias compatível com o relógio antigo.
        """

        self.definir_velocidade(
            velocidade
        )

    # ======================================================
    # PAUSAR
    # ======================================================

    def pausar(self):

        self.pausado = True

    # ======================================================
    # CONTINUAR
    # ======================================================

    def continuar(self):

        self.pausado = False

    # ======================================================
    # TICK
    # ======================================================

    def tick(
        self,
        segundos_reais=1.0
    ):
        """
        Avança automaticamente a simulação.

        Por padrão:

            1 segundo real

        representa:

            velocidade segundos virtuais.

        Exemplo:

            velocidade = 60

        então:

            1 segundo real
            =
            60 segundos virtuais
            =
            1 minuto virtual
        """

        if self.pausado:

            return self.tempo_atual

        segundos_reais = float(
            segundos_reais
        )

        if segundos_reais < 0:

            raise ValueError(
                "segundos_reais não pode ser negativo."
            )

        return self.avancar_segundos(
            segundos_reais
            * self.velocidade
        )

    # ======================================================
    # RESET
    # ======================================================

    def resetar(self):
        """
        Retorna ao instante inicial.
        """

        self.tempo_atual = self.data_inicial

        self.tempo_simulado_total = timedelta(0)

        self.pausado = False

    # ======================================================
    # TEMPO DECORRIDO
    # ======================================================

    def tempo_decorrido_segundos(self):

        return (
            self.tempo_simulado_total
            .total_seconds()
        )

    # ------------------------------------------------------

    def tempo_decorrido_dias(self):

        return (
            self.tempo_simulado_total
            .total_seconds()
            / 86400.0
        )

    # ======================================================
    # ESTADO
    # ======================================================

    @property
    def rodando(self):

        return not self.pausado

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __str__(self):

        estado = (
            "PAUSADO"
            if self.pausado
            else "RODANDO"
        )

        data_formatada = (
            self.tempo_atual.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )

        return (
            f"{data_formatada} | "
            f"{self.velocidade:g}x | "
            f"{estado}"
        )


# ==========================================================
# TESTE
# ==========================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "TESTE — RELÓGIO DA GÊMEA DIGITAL"
    )

    print("=" * 60)

    # ------------------------------------------------------
    # Data conhecida
    # ------------------------------------------------------

    inicio = datetime(
        2026,
        1,
        1,
        8,
        0,
        0
    )

    relogio = RelogioSimulado(
        data_inicial=inicio
    )

    # ------------------------------------------------------
    # Estado inicial
    # ------------------------------------------------------

    print()

    print("TEMPO INICIAL:")

    print(relogio)

    # ------------------------------------------------------
    # 1 hora
    # ------------------------------------------------------

    print()

    print(
        "AVANÇANDO 1 HORA..."
    )

    relogio.avancar_horas(1)

    print(relogio)

    # ------------------------------------------------------
    # 1 dia
    # ------------------------------------------------------

    print()

    print(
        "AVANÇANDO 1 DIA..."
    )

    relogio.avancar_dias(1)

    print(relogio)

    # ------------------------------------------------------
    # 7 dias
    # ------------------------------------------------------

    print()

    print(
        "AVANÇANDO 7 DIAS..."
    )

    relogio.avancar_dias(7)

    print(relogio)

    # ------------------------------------------------------
    # Velocidade
    # ------------------------------------------------------

    print()

    print(
        "ALTERANDO VELOCIDADE PARA 100x..."
    )

    relogio.definir_velocidade(100)

    print(relogio)

    # ------------------------------------------------------
    # Pausar
    # ------------------------------------------------------

    print()

    print("PAUSANDO...")

    relogio.pausar()

    print(relogio)

    # ------------------------------------------------------
    # Tentar avançar pausado
    # ------------------------------------------------------

    print()

    print(
        "TENTANDO AVANÇAR 1 DIA "
        "COM O RELÓGIO PAUSADO..."
    )

    antes = relogio.agora()

    relogio.avancar_dias(1)

    depois = relogio.agora()

    print(relogio)

    assert antes == depois

    print()

    print(
        "OK — RELÓGIO PERMANECEU PAUSADO."
    )

    # ------------------------------------------------------
    # Continuar
    # ------------------------------------------------------

    print()

    print("CONTINUANDO...")

    relogio.continuar()

    relogio.avancar_dias(1)

    print(relogio)

    # ------------------------------------------------------
    # Testar tick
    # ------------------------------------------------------

    print()

    print(
        "TESTANDO TICK EM 100x..."
    )

    antes = relogio.agora()

    relogio.tick()

    depois = relogio.agora()

    print(relogio)

    assert (
        depois - antes
        == timedelta(seconds=100)
    )

    print()

    print(
        "OK — TICK FUNCIONANDO."
    )

    # ------------------------------------------------------
    # Tempo total
    # ------------------------------------------------------

    print()

    print(
        "TEMPO SIMULADO TOTAL:"
    )

    print(
        relogio.tempo_decorrido_segundos(),
        "segundos"
    )

    print(
        relogio.tempo_decorrido_dias(),
        "dias"
    )

    # ------------------------------------------------------
    # Reset
    # ------------------------------------------------------

    print()

    print("RESETANDO...")

    relogio.resetar()

    print(relogio)

    assert (
        relogio.agora()
        == inicio
    )

    assert (
        relogio.tempo_decorrido_segundos()
        == 0
    )

    print()

    print(
        "OK — RESET FUNCIONANDO."
    )

    # ------------------------------------------------------
    # Compatibilidade com relógio antigo
    # ------------------------------------------------------

    print()

    print(
        "TESTANDO COMPATIBILIDADE..."
    )

    relogio.definir_hora(
        13,
        0
    )

    relogio.configurar_velocidade(
        60
    )

    relogio.avancar(
        30
    )

    assert relogio.hora == 13

    assert relogio.minuto == 30

    print(relogio)

    print()

    print(
        "OK — COMPATIBILIDADE FUNCIONANDO."
    )

    # ------------------------------------------------------
    # Final
    # ------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "✅ TESTE DO RELÓGIO FINALIZADO"
    )

    print("=" * 60)