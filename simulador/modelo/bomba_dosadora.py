"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN
BOMBA DOSADORA
============================================================

Representa uma bomba dosadora no ambiente virtual.

A bomba possui:

    - nome
    - vazão nominal
    - vazão calibrada
    - estado ligado/desligado
    - volume total dosado
    - contador de acionamentos

A bomba NÃO aciona hardware.

Ela representa o comportamento que futuramente poderá
ser executado pelo ESP32.

Fluxo futuro:

    software
        ↓
    bomba.dosar_ml()
        ↓
    controlador
        ↓
    GPIO ESP32
        ↓
    MOSFET
        ↓
    bomba peristáltica
        ↓
    insumo

============================================================
"""


class BombaDosadora:

    # ======================================================
    # CONSTRUTOR
    # ======================================================

    def __init__(
        self,
        nome,
        vazao_ml_min,
        vazao_calibrada_ml_min=None,
    ):

        self.nome = (
            str(nome)
            .strip()
            .upper()
        )

        self.vazao_nominal_ml_min = float(
            vazao_ml_min
        )

        if self.vazao_nominal_ml_min <= 0:

            raise ValueError(
                "A vazão nominal deve ser positiva."
            )

        # --------------------------------------------------
        # Se ainda não existe calibração real,
        # usamos a vazão nominal.
        # --------------------------------------------------

        if vazao_calibrada_ml_min is None:

            vazao_calibrada_ml_min = (
                self.vazao_nominal_ml_min
            )

        self.vazao_calibrada_ml_min = float(
            vazao_calibrada_ml_min
        )

        if self.vazao_calibrada_ml_min <= 0:

            raise ValueError(
                "A vazão calibrada deve ser positiva."
            )

        # --------------------------------------------------
        # Estado
        # --------------------------------------------------

        self.ativa = False

        self.volume_total_dosado_ml = 0.0

        self.numero_acionamentos = 0

    # ======================================================
    # VAZÃO ATUAL
    # ======================================================

    @property
    def vazao_ml_min(self):

        return self.vazao_calibrada_ml_min

    # ======================================================
    # LIGAR
    # ======================================================

    def ligar(self):

        self.ativa = True

    # ======================================================
    # DESLIGAR
    # ======================================================

    def desligar(self):

        self.ativa = False

    # ======================================================
    # CALCULAR TEMPO
    # ======================================================

    def tempo_para_dosar(
        self,
        quantidade_ml
    ):
        """
        Retorna o tempo necessário em segundos
        para dosar determinada quantidade.
        """

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "A quantidade deve ser positiva."
            )

        minutos = (
            quantidade_ml
            / self.vazao_ml_min
        )

        segundos = minutos * 60

        return segundos

    # ======================================================
    # CALCULAR VOLUME
    # ======================================================

    def volume_por_tempo(
        self,
        segundos
    ):
        """
        Calcula quanto a bomba dosaria durante
        determinado tempo.
        """

        segundos = float(
            segundos
        )

        if segundos <= 0:

            raise ValueError(
                "O tempo deve ser positivo."
            )

        minutos = segundos / 60

        return (
            self.vazao_ml_min
            * minutos
        )

    # ======================================================
    # DOSAR
    # ======================================================

    def dosar_ml(
        self,
        quantidade_ml
    ):
        """
        Simula uma dosagem.

        Retorna o tempo de acionamento necessário.

        A bomba é ligada durante a operação e desligada
        automaticamente ao final da simulação.
        """

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "A quantidade deve ser positiva."
            )

        tempo_segundos = (
            self.tempo_para_dosar(
                quantidade_ml
            )
        )

        self.ligar()

        self.numero_acionamentos += 1

        self.volume_total_dosado_ml += (
            quantidade_ml
        )

        self.desligar()

        return tempo_segundos

    # ======================================================
    # CALIBRAÇÃO
    # ======================================================

    def calibrar(
        self,
        volume_medido_ml,
        tempo_segundos
    ):
        """
        Atualiza a vazão calibrada a partir de uma
        medição real.

        Exemplo:

            volume coletado = 20 ml
            tempo = 30 s

        Resultado:

            40 ml/min
        """

        volume_medido_ml = float(
            volume_medido_ml
        )

        tempo_segundos = float(
            tempo_segundos
        )

        if volume_medido_ml <= 0:

            raise ValueError(
                "O volume medido deve ser positivo."
            )

        if tempo_segundos <= 0:

            raise ValueError(
                "O tempo deve ser positivo."
            )

        minutos = (
            tempo_segundos
            / 60
        )

        vazao = (
            volume_medido_ml
            / minutos
        )

        self.vazao_calibrada_ml_min = (
            vazao
        )

        return vazao

    # ======================================================
    # RESET DOS CONTADORES
    # ======================================================

    def resetar_contadores(self):

        self.volume_total_dosado_ml = 0.0

        self.numero_acionamentos = 0

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "vazao_nominal_ml_min":
                self.vazao_nominal_ml_min,

            "vazao_calibrada_ml_min":
                round(
                    self.vazao_calibrada_ml_min,
                    4
                ),

            "ativa":
                self.ativa,

            "volume_total_dosado_ml":
                round(
                    self.volume_total_dosado_ml,
                    3
                ),

            "numero_acionamentos":
                self.numero_acionamentos,
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            "BombaDosadora("
            f"nome='{self.nome}', "
            f"vazao="
            f"{self.vazao_ml_min:.2f} ml/min"
            ")"
        )