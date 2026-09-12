"""
============================================================
HORTA DO FUTURO
RELÓGIO VIRTUAL
============================================================

Responsabilidade:

    Controlar o horário da Gêmea Digital.

Este relógio trabalha com:

    - hora atual;
    - minuto atual;
    - velocidade da simulação;
    - avanço manual;
    - avanço automático por tick;
    - quantidade de minutos acumulados.

============================================================

VELOCIDADE:

    A velocidade representa:

        MINUTOS VIRTUAIS POR TICK

Exemplos:

    1x
        1 minuto virtual por tick

    10x
        10 minutos virtuais por tick

    60x
        1 hora virtual por tick

    360x
        6 horas virtuais por tick

    1440x
        24 horas virtuais por tick

============================================================

IMPORTANTE:

    Este módulo NÃO conhece:

        - plantas;
        - sensores;
        - bombas;
        - iluminação;
        - pH;
        - EC;
        - crescimento;
        - automação.

    Ele apenas fornece o TEMPO.

    A Horta utiliza o tempo fornecido por este módulo
    para executar suas próprias regras.

============================================================

ARQUITETURA:

        RELÓGIO VIRTUAL
               │
               │ minutos decorridos
               ▼
             HORTA
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    planta   ambiente  automação

============================================================
"""


class RelogioVirtual:

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(
        self,
        hora=13,
        minuto=0
    ):
        """
        Cria um relógio virtual.

        Parâmetros:

            hora:
                Hora inicial da simulação.

            minuto:
                Minuto inicial da simulação.

        Exemplo:

            RelogioVirtual(
                hora=13,
                minuto=0
            )

        inicia a simulação às 13:00.
        """

        # --------------------------------------------------
        # HORA ATUAL
        # --------------------------------------------------

        self.hora = int(hora)

        # --------------------------------------------------
        # MINUTO ATUAL
        # --------------------------------------------------

        self.minuto = int(minuto)

        # --------------------------------------------------
        # VELOCIDADE
        #
        # Minutos virtuais por tick.
        #
        # Padrão:
        #
        # 1x = 1 minuto virtual por tick
        # --------------------------------------------------

        self.velocidade = 1.0

        # --------------------------------------------------
        # ACUMULADOR
        #
        # Mantém frações de minuto quando necessário.
        #
        # Exemplo:
        #
        # velocidade = 0.5
        #
        # Tick 1:
        #     0.5 minuto acumulado
        #
        # Tick 2:
        #     1.0 minuto
        #
        # O relógio então avança 1 minuto.
        #
        # Isso será útil para velocidades menores que 1x.
        # --------------------------------------------------

        self._minutos_acumulados = 0.0

        # --------------------------------------------------
        # DEFINIR HORÁRIO INICIAL
        # --------------------------------------------------

        self.definir_hora(
            self.hora,
            self.minuto
        )

    # ======================================================
    # HORA ATUAL EM MINUTOS
    # ======================================================

    @property
    def minutos_do_dia(self):
        """
        Retorna o horário atual convertido para minutos.

        Exemplo:

            13:30

        retorna:

            810
        """

        return (
            self.hora * 60
            + self.minuto
        )

    # ======================================================
    # HORA
    # ======================================================

    def definir_hora(
        self,
        hora,
        minuto
    ):
        """
        Define manualmente o horário da simulação.

        O horário é limitado ao formato de relógio:

            hora   = 0 a 23
            minuto = 0 a 59

        Ao definir um novo horário, o acumulador de tempo
        fracionário é zerado.
        """

        hora = max(
            0,
            min(23, int(hora))
        )

        minuto = max(
            0,
            min(59, int(minuto))
        )

        self.hora = hora

        self.minuto = minuto

        # --------------------------------------------------
        # Como houve uma alteração manual do relógio,
        # descartamos qualquer fração acumulada.
        # --------------------------------------------------

        self._minutos_acumulados = 0.0

    # ======================================================
    # VELOCIDADE
    # ======================================================

    def configurar_velocidade(
        self,
        velocidade
    ):
        """
        Define a velocidade da simulação.

        Exemplos:

            1
            10
            60
            360
            1440

        Também aceita valores fracionários:

            0.5
            0.1

        Valores negativos não são permitidos.

        0 significa relógio parado.
        """

        velocidade = float(
            velocidade
        )

        if velocidade < 0:

            raise ValueError(
                "A velocidade não pode ser negativa."
            )

        self.velocidade = velocidade

    # ======================================================
    # AVANÇAR MINUTOS
    # ======================================================

    def avancar(
        self,
        minutos
    ):
        """
        Avança manualmente o relógio.

        Parâmetro:

            minutos:
                quantidade de minutos virtuais.

        Retorna:

            quantidade efetivamente avançada.

        IMPORTANTE:

            O avanço manual NÃO utiliza a velocidade.

        Exemplo:

            relogio.avancar(90)

        significa:

            avançar exatamente 90 minutos.
        """

        minutos = float(
            minutos
        )

        if minutos < 0:

            raise ValueError(
                "Não é permitido avançar "
                "tempo negativo."
            )

        if minutos == 0:

            return 0.0

        # --------------------------------------------------
        # Horário atual convertido para minutos.
        # --------------------------------------------------

        total = (
            self.minutos_do_dia
            + minutos
        )

        # --------------------------------------------------
        # O relógio é cíclico dentro das 24 horas.
        # --------------------------------------------------

        total %= 1440

        # --------------------------------------------------
        # Converter novamente para hora/minuto.
        #
        # O horário público continua trabalhando com
        # minutos inteiros.
        # --------------------------------------------------

        self.hora = int(
            total // 60
        )

        self.minuto = int(
            total % 60
        )

        return minutos

    # ======================================================
    # HORAS
    # ======================================================

    def avancar_horas(
        self,
        horas
    ):
        """
        Avança horas simuladas.

        Exemplo:

            avancar_horas(2)

        avança exatamente 2 horas.
        """

        return self.avancar(
            float(horas) * 60
        )

    # ======================================================
    # DIAS
    # ======================================================

    def avancar_dias(
        self,
        dias
    ):
        """
        Avança dias simulados.

        Exemplo:

            avancar_dias(1)

        avança exatamente 24 horas.
        """

        return self.avancar(
            float(dias) * 1440
        )

    # ======================================================
    # TICK
    # ======================================================

    def tick(self):
        """
        Executa um ciclo do relógio.

        A quantidade avançada depende da velocidade.

        Exemplos:

            velocidade = 1

                tick()
                ↓
                +1 minuto

            velocidade = 60

                tick()
                ↓
                +60 minutos

            velocidade = 1440

                tick()
                ↓
                +1440 minutos

        RETORNO:

            Retorna a quantidade de minutos virtuais
            avançados neste tick.

        Isso é MUITO importante para a próxima camada.

        A Horta poderá fazer:

            minutos = relogio.tick()

            e então saber exatamente quanto tempo passou.

        """

        # --------------------------------------------------
        # Relógio parado
        # --------------------------------------------------

        if self.velocidade <= 0:

            return 0.0

        # --------------------------------------------------
        # Adicionar a velocidade ao acumulador.
        # --------------------------------------------------

        self._minutos_acumulados += (
            self.velocidade
        )

        # --------------------------------------------------
        # Quantidade inteira de minutos que pode ser
        # aplicada ao relógio.
        #
        # Exemplo:
        #
        # acumulado = 2.7
        #
        # minutos inteiros = 2
        #
        # sobra = 0.7
        # --------------------------------------------------

        minutos_inteiros = int(
            self._minutos_acumulados
        )

        # --------------------------------------------------
        # Nenhum minuto completo ainda.
        #
        # Isso acontece principalmente com velocidades
        # menores que 1.
        # --------------------------------------------------

        if minutos_inteiros <= 0:

            return 0.0

        # --------------------------------------------------
        # Preservar a parte fracionária.
        # --------------------------------------------------

        self._minutos_acumulados -= (
            minutos_inteiros
        )

        # --------------------------------------------------
        # Avançar o relógio.
        # --------------------------------------------------

        self.avancar(
            minutos_inteiros
        )

        # --------------------------------------------------
        # Informar à Horta quanto tempo passou.
        # --------------------------------------------------

        return float(
            minutos_inteiros
        )

    # ======================================================
    # ESTADO
    # ======================================================

    def snapshot(self):
        """
        Retorna o estado atual do relógio.

        Esse método será útil para:

            - interface;
            - logs;
            - diagnóstico;
            - salvar simulação;
            - API;
            - comunicação com outros módulos.
        """

        return {

            "hora":
                self.hora,

            "minuto":
                self.minuto,

            "minutos_do_dia":
                self.minutos_do_dia,

            "velocidade":
                self.velocidade,

            "minutos_acumulados":
                self._minutos_acumulados,
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __str__(self):
        """
        Representação amigável do relógio.
        """

        return (
            f"{self.hora:02d}:"
            f"{self.minuto:02d} | "
            f"{self.velocidade:g}x"
        )


# ==========================================================
# TESTE DO MÓDULO
# ==========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("TESTE — RELÓGIO VIRTUAL DA HORTA")
    print("=" * 60)

    # ======================================================
    # CRIAÇÃO
    # ======================================================

    relogio = RelogioVirtual(
        hora=13,
        minuto=0
    )

    print()
    print("HORÁRIO INICIAL:")

    print(relogio)

    # ======================================================
    # TESTE DE AVANÇO MANUAL
    # ======================================================

    print()
    print("AVANÇANDO 2 HORAS...")

    resultado = relogio.avancar_horas(2)

    print(relogio)

    assert relogio.hora == 15
    assert relogio.minuto == 0
    assert resultado == 120.0

    print("OK — AVANÇO MANUAL FUNCIONANDO.")

    # ======================================================
    # TESTE 60x
    # ======================================================

    print()
    print("CONFIGURANDO 60x...")

    relogio.configurar_velocidade(60)

    print(relogio)

    print()
    print("EXECUTANDO TICK...")

    avancado = relogio.tick()

    print(relogio)

    assert avancado == 60.0
    assert relogio.hora == 16
    assert relogio.minuto == 0

    print("OK — TICK DE 60 MINUTOS FUNCIONANDO.")

    # ======================================================
    # TESTE 1440x
    # ======================================================

    print()
    print("CONFIGURANDO 1440x...")

    relogio.configurar_velocidade(1440)

    avancado = relogio.tick()

    print(relogio)

    assert avancado == 1440.0

    print("OK — TICK DE 24 HORAS FUNCIONANDO.")

    # ======================================================
    # TESTE VELOCIDADE FRACIONÁRIA
    # ======================================================

    print()
    print("TESTANDO VELOCIDADE 0.5x...")

    relogio.configurar_velocidade(0.5)

    antes = (
        relogio.hora,
        relogio.minuto
    )

    # Primeiro tick:
    #
    # 0.5 minuto acumulado.
    #

    resultado = relogio.tick()

    assert resultado == 0.0

    depois = (
        relogio.hora,
        relogio.minuto
    )

    assert antes == depois

    print(
        "TICK 1:",
        relogio,
        "| avançado:",
        resultado,
        "min"
    )

    # Segundo tick:
    #
    # 0.5 + 0.5 = 1 minuto.
    #

    resultado = relogio.tick()

    assert resultado == 1.0

    print(
        "TICK 2:",
        relogio,
        "| avançado:",
        resultado,
        "min"
    )

    print(
        "OK — VELOCIDADE FRACIONÁRIA FUNCIONANDO."
    )

    # ======================================================
    # TESTE SNAPSHOT
    # ======================================================

    print()
    print("SNAPSHOT:")

    print(
        relogio.snapshot()
    )

    print()
    print("=" * 60)
    print("✅ TESTE DO RELÓGIO VIRTUAL FINALIZADO")
    print("=" * 60)