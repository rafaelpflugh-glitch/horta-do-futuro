"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

RECEITA DE FASE DE CULTIVO
============================================================

Uma ReceitaFase representa as condições ideais de uma
determinada fase de uma cultura.

Exemplo:

    ALFACE
        ├── GERMINAÇÃO
        ├── MUDA
        └── VEGETATIVO

Cada fase possui sua própria receita.

A receita contém:

    - pH
    - EC
    - temperatura do ar
    - temperatura da água
    - umidade do ar
    - fotoperíodo
    - horário de início da iluminação

O Digital Twin utiliza a receita da fase atualmente ativa
para realizar o diagnóstico do cultivo.

============================================================
"""


class ReceitaFase:

    # ========================================================
    # CONSTRUTOR
    # ========================================================

    def __init__(
        self,
        nome="VEGETATIVO",

        ph_min=5.5,
        ph_max=6.5,

        ec_min=1.0,
        ec_max=1.8,

        temperatura_ar_min=18.0,
        temperatura_ar_max=26.0,

        temperatura_agua_min=18.0,
        temperatura_agua_max=26.0,

        umidade_ar_min=50.0,
        umidade_ar_max=80.0,

        fotoperiodo_horas=18.0,

        inicio_luz_hora=6,
        inicio_luz_minuto=0
    ):

        self.nome = str(nome).strip().upper()

        self.ph_min = float(ph_min)
        self.ph_max = float(ph_max)

        self.ec_min = float(ec_min)
        self.ec_max = float(ec_max)

        self.temperatura_ar_min = float(
            temperatura_ar_min
        )

        self.temperatura_ar_max = float(
            temperatura_ar_max
        )

        self.temperatura_agua_min = float(
            temperatura_agua_min
        )

        self.temperatura_agua_max = float(
            temperatura_agua_max
        )

        self.umidade_ar_min = float(
            umidade_ar_min
        )

        self.umidade_ar_max = float(
            umidade_ar_max
        )

        self.fotoperiodo_horas = float(
            fotoperiodo_horas
        )

        self.inicio_luz_hora = int(
            inicio_luz_hora
        )

        self.inicio_luz_minuto = int(
            inicio_luz_minuto
        )

        self.validar()

    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    def validar(self):

        if not self.nome:

            raise ValueError(
                "O nome da fase não pode ser vazio."
            )

        if not (
            0 <= self.inicio_luz_hora <= 23
        ):

            raise ValueError(
                "A hora de início da luz deve "
                "estar entre 0 e 23."
            )

        if not (
            0 <= self.inicio_luz_minuto <= 59
        ):

            raise ValueError(
                "O minuto de início da luz deve "
                "estar entre 0 e 59."
            )

        if self.ph_min > self.ph_max:

            raise ValueError(
                "ph_min não pode ser maior que ph_max."
            )

        if self.ec_min > self.ec_max:

            raise ValueError(
                "ec_min não pode ser maior que ec_max."
            )

        if (
            self.temperatura_ar_min
            > self.temperatura_ar_max
        ):

            raise ValueError(
                "temperatura_ar_min não pode ser "
                "maior que temperatura_ar_max."
            )

        if (
            self.temperatura_agua_min
            > self.temperatura_agua_max
        ):

            raise ValueError(
                "temperatura_agua_min não pode ser "
                "maior que temperatura_agua_max."
            )

        if (
            self.umidade_ar_min
            > self.umidade_ar_max
        ):

            raise ValueError(
                "umidade_ar_min não pode ser "
                "maior que umidade_ar_max."
            )

        if not (
            0 <= self.fotoperiodo_horas <= 24
        ):

            raise ValueError(
                "O fotoperíodo deve estar entre "
                "0 e 24 horas."
            )

    # ========================================================
    # FOTOPERÍODO
    # ========================================================

    @property
    def inicio_luz_minutos(self):

        return (
            self.inicio_luz_hora * 60
            + self.inicio_luz_minuto
        )

    @property
    def duracao_luz_minutos(self):

        return int(
            round(
                self.fotoperiodo_horas * 60
            )
        )

    @property
    def fim_luz_minutos(self):

        return (
            self.inicio_luz_minutos
            + self.duracao_luz_minutos
        ) % 1440

    @staticmethod
    def _formatar_hora_minuto(total_minutos):

        total_minutos %= 1440

        hora = total_minutos // 60
        minuto = total_minutos % 60

        return f"{hora:02d}:{minuto:02d}"

    @property
    def inicio_luz_formatado(self):

        return self._formatar_hora_minuto(
            self.inicio_luz_minutos
        )

    @property
    def fim_luz_formatado(self):

        return self._formatar_hora_minuto(
            self.fim_luz_minutos
        )

    @property
    def fotoperiodo_formatado(self):

        minutos = self.duracao_luz_minutos

        horas = minutos // 60
        minutos_restantes = minutos % 60

        return (
            f"{horas:02d}h "
            f"{minutos_restantes:02d}min"
        )

    # ========================================================
    # ALTERAR FOTOPERÍODO
    # ========================================================

    def configurar_fotoperiodo(
        self,
        horas,
        inicio_hora,
        inicio_minuto=0
    ):

        self.fotoperiodo_horas = float(
            horas
        )

        self.inicio_luz_hora = int(
            inicio_hora
        )

        self.inicio_luz_minuto = int(
            inicio_minuto
        )

        self.validar()

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(self):

        return {

            "nome":
                self.nome,

            "ph_min":
                self.ph_min,

            "ph_max":
                self.ph_max,

            "ec_min":
                self.ec_min,

            "ec_max":
                self.ec_max,

            "temperatura_ar_min":
                self.temperatura_ar_min,

            "temperatura_ar_max":
                self.temperatura_ar_max,

            "temperatura_agua_min":
                self.temperatura_agua_min,

            "temperatura_agua_max":
                self.temperatura_agua_max,

            "umidade_ar_min":
                self.umidade_ar_min,

            "umidade_ar_max":
                self.umidade_ar_max,

            "fotoperiodo_horas":
                self.fotoperiodo_horas,

            "inicio_luz_hora":
                self.inicio_luz_hora,

            "inicio_luz_minuto":
                self.inicio_luz_minuto,

            "inicio_luz":
                self.inicio_luz_formatado,

            "fim_luz":
                self.fim_luz_formatado,

            "fotoperiodo":
                self.fotoperiodo_formatado
        }

    # ========================================================
    # REPRESENTAÇÃO
    # ========================================================

    def __repr__(self):

        return (
            "ReceitaFase("
            f"nome={self.nome!r}, "
            f"ph={self.ph_min}-{self.ph_max}, "
            f"ec={self.ec_min}-{self.ec_max}, "
            f"luz={self.fotoperiodo_formatado}, "
            f"inicio={self.inicio_luz_formatado}, "
            f"fim={self.fim_luz_formatado}"
            ")"
        )