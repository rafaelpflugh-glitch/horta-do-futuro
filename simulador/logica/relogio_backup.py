"""
============================================================
HORTA DO FUTURO
RELÓGIO DA GÊMEA DIGITAL
============================================================

Responsabilidade:

    Controlar o tempo da simulação da Horta Virtual.

O relógio possui:

    - data/hora atual da simulação;
    - velocidade da simulação;
    - pausa;
    - continuidade;
    - avanço manual;
    - reset;
    - tempo total simulado.

Exemplos:

    1x
        tempo normal

    10x
        tempo 10 vezes mais rápido

    100x
        tempo 100 vezes mais rápido

IMPORTANTE:

Este módulo NÃO controla:

    - sensores;
    - bombas;
    - iluminação;
    - planta;
    - alarmes.

Ele apenas fornece o tempo.

Os outros sistemas utilizarão este relógio
como referência temporal.

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
        """

        if data_inicial is None:
            data_inicial = datetime.now()

        if not isinstance(data_inicial, datetime):
            raise TypeError(
                "data_inicial deve ser um objeto datetime."
            )

        velocidade = float(velocidade)

        if velocidade <= 0:
            raise ValueError(
                "A velocidade deve ser maior que zero."
            )

        self.data_inicial = data_inicial

        self.tempo_atual = data_inicial

        self.velocidade = velocidade

        self.pausado = False

        self.tempo_simulado_total = timedelta(0)

    # ======================================================
    # TEMPO ATUAL
    # ======================================================

    def agora(self):
        """
        Retorna a data/hora atual da simulação.
        """

        return self.tempo_atual

    # ======================================================
    # AVANÇAR SEGUNDOS
    # ======================================================

    def avancar_segundos(self, segundos):
        """
        Avança o tempo da simulação.

        O valor representa segundos simulados.
        """

        segundos = float(segundos)

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

    def avancar_minutos(self, minutos):
        """
        Avança minutos simulados.
        """

        return self.avancar_segundos(
            minutos * 60
        )

    # ======================================================
    # AVANÇAR HORAS
    # ======================================================

    def avancar_horas(self, horas):
        """
        Avança horas simuladas.
        """

        return self.avancar_segundos(
            horas * 3600
        )

    # ======================================================
    # AVANÇAR DIAS
    # ======================================================

    def avancar_dias(self, dias):
        """
        Avança dias simulados.
        """

        return self.avancar_segundos(
            dias * 86400
        )

    # ======================================================
    # ALTERAR VELOCIDADE
    # ======================================================

    def definir_velocidade(self, velocidade):
        """
        Altera a velocidade da simulação.

        Exemplos:

            1
            10
            100
        """

        velocidade = float(velocidade)

        if velocidade <= 0:
            raise ValueError(
                "A velocidade deve ser maior que zero."
            )

        self.velocidade = velocidade

    # ======================================================
    # PAUSAR
    # ======================================================

    def pausar(self):
        """
        Pausa o relógio.
        """

        self.pausado = True

    # ======================================================
    # CONTINUAR
    # ======================================================

    def continuar(self):
        """
        Continua o relógio.
        """

        self.pausado = False

    # ======================================================
    # RESETAR
    # ======================================================

    def resetar(self):
        """
        Retorna a simulação para a data inicial.
        """

        self.tempo_atual = self.data_inicial

        self.tempo_simulado_total = timedelta(0)

        self.pausado = False

    # ======================================================
    # TEMPO DECORRIDO — SEGUNDOS
    # ======================================================

    def tempo_decorrido_segundos(self):
        """
        Retorna o total de segundos simulados.
        """

        return self.tempo_simulado_total.total_seconds()

    # ======================================================
    # TEMPO DECORRIDO — DIAS
    # ======================================================

    def tempo_decorrido_dias(self):
        """
        Retorna o total de dias simulados.
        """

        return (
            self.tempo_simulado_total.total_seconds()
            / 86400.0
        )

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __str__(self):
        """
        Representação amigável do relógio.
        """

        estado = "PAUSADO" if self.pausado else "RODANDO"

        data_formatada = self.tempo_atual.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        return (
            f"{data_formatada} | "
            f"{self.velocidade:g}x | "
            f"{estado}"
        )


# ==========================================================
# TESTE DO MÓDULO
# ==========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("TESTE — RELÓGIO DA GÊMEA DIGITAL")
    print("=" * 60)

    # ------------------------------------------------------
    # Criar uma data conhecida
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
    # Avançar 1 hora
    # ------------------------------------------------------

    print()
    print("AVANÇANDO 1 HORA...")

    relogio.avancar_horas(1)

    print(relogio)

    # ------------------------------------------------------
    # Avançar 1 dia
    # ------------------------------------------------------

    print()
    print("AVANÇANDO 1 DIA...")

    relogio.avancar_dias(1)

    print(relogio)

    # ------------------------------------------------------
    # Avançar 7 dias
    # ------------------------------------------------------

    print()
    print("AVANÇANDO 7 DIAS...")

    relogio.avancar_dias(7)

    print(relogio)

    # ------------------------------------------------------
    # Alterar velocidade
    # ------------------------------------------------------

    print()
    print("ALTERANDO VELOCIDADE PARA 100x...")

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
    # Testar avanço durante pausa
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
    # Mostrar tempo total
    # ------------------------------------------------------

    print()
    print("TEMPO SIMULADO TOTAL:")

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

    assert relogio.agora() == inicio

    assert (
        relogio.tempo_decorrido_segundos()
        == 0
    )

    print()
    print(
        "OK — RESET FUNCIONANDO."
    )

    print()
    print("=" * 60)
    print("✅ TESTE DO RELÓGIO FINALIZADO")
    print("=" * 60)