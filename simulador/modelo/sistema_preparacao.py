"""
============================================================
HORTA DO FUTURO
SISTEMA DE PREPARAÇÃO
============================================================

Integra:

    ReceitaNutritiva
          +
    ReservatorioCultivo
          ↓
    SistemaPreparacao
          ↓
    Plano de preparo

Responsabilidades:

- calcular quantidades dos componentes;
- calcular água inicial;
- calcular volume físico final;
- verificar capacidade;
- verificar disponibilidade de insumos;
- impedir preparação fisicamente impossível;
- gerar plano de preparo.

Ainda NÃO aciona bombas.
============================================================
"""


class SistemaPreparacao:

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(
        self,
        receita,
        reservatorio,
        sistema_dosagem=None
    ):

        self.receita = receita
        self.reservatorio = reservatorio
        self.sistema_dosagem = sistema_dosagem

    # ======================================================
    # VOLUME ALVO
    # ======================================================

    def volume_alvo(self):

        return float(
            self.reservatorio.volume_litros
        )

    # ======================================================
    # CAPACIDADE
    # ======================================================

    def capacidade_litros(self):

        return float(
            self.reservatorio.capacidade_litros
        )

    # ======================================================
    # CALCULAR COMPONENTES
    # ======================================================

    def calcular_quantidades(self):

        volume = self.volume_alvo()

        quantidades = []

        for componente in self.receita.componentes:

            # ------------------------------------------------
            # Compatibilidade com componentes armazenados
            # como dicionário.
            # ------------------------------------------------

            if isinstance(componente, dict):

                nome = componente["nome"]

                quantidade_por_litro = float(
                    componente[
                        "quantidade_por_litro"
                    ]
                )

                unidade = componente[
                    "unidade"
                ]

            else:

                nome = componente.nome

                quantidade_por_litro = float(
                    componente.quantidade_por_litro
                )

                unidade = componente.unidade

            # ------------------------------------------------
            # Quantidade total
            # ------------------------------------------------

            quantidade = (
                quantidade_por_litro
                * volume
            )

            quantidades.append({

                "nome":
                    nome,

                "quantidade":
                    quantidade,

                "quantidade_por_litro":
                    quantidade_por_litro,

                "unidade":
                    unidade,

                "volume_litros":
                    volume
            })

        return quantidades

    # ======================================================
    # VOLUME DOS INSUMOS
    # ======================================================

    def volume_insumos_ml(self):

        total = 0.0

        for item in self.calcular_quantidades():

            unidade = str(
                item["unidade"]
            ).lower().strip()

            # ------------------------------------------------
            # Somente líquidos em ml alteram diretamente
            # o volume físico.
            # ------------------------------------------------

            if unidade in (
                "ml",
                "mililitro",
                "mililitros"
            ):

                total += float(
                    item["quantidade"]
                )

        return total

    # ======================================================
    # VOLUME DOS INSUMOS EM LITROS
    # ======================================================

    def volume_insumos_litros(self):

        return (
            self.volume_insumos_ml()
            / 1000.0
        )

    # ======================================================
    # ÁGUA INICIAL
    # ======================================================

    def volume_agua_inicial_litros(self):

        volume_final = self.volume_alvo()

        insumos_litros = (
            self.volume_insumos_litros()
        )

        agua = (
            volume_final
            - insumos_litros
        )

        return max(
            0.0,
            agua
        )

    # ======================================================
    # VOLUME FÍSICO FINAL
    # ======================================================

    def volume_final_fisico_litros(self):

        agua = (
            self.volume_agua_inicial_litros()
        )

        insumos = (
            self.volume_insumos_litros()
        )

        return (
            agua
            + insumos
        )

    # ======================================================
    # EXCESSO FÍSICO
    # ======================================================

    def excesso_volume_litros(self):

        volume_fisico = (
            self.volume_final_fisico_litros()
        )

        capacidade = (
            self.capacidade_litros()
        )

        return max(
            0.0,
            volume_fisico - capacidade
        )

    # ======================================================
    # VERIFICAR CAPACIDADE
    # ======================================================

    def verificar_capacidade(self):

        volume_alvo = (
            self.volume_alvo()
        )

        capacidade = (
            self.capacidade_litros()
        )

        agua = (
            self.volume_agua_inicial_litros()
        )

        insumos = (
            self.volume_insumos_litros()
        )

        volume_fisico = (
            self.volume_final_fisico_litros()
        )

        excesso = (
            self.excesso_volume_litros()
        )

        # --------------------------------------------------
        # IMPORTANTE:
        #
        # Existem duas verificações independentes:
        #
        # 1. volume-alvo <= capacidade
        #
        # 2. volume-físico <= capacidade
        #
        # A primeira impede pedir uma solução maior que
        # o reservatório.
        #
        # A segunda protege contra receitas que adicionem
        # volume além do esperado.
        # --------------------------------------------------

        volume_alvo_dentro = (
            volume_alvo <= capacidade
        )

        volume_fisico_dentro = (
            volume_fisico <= capacidade
        )

        return {

            "volume_alvo_litros":
                volume_alvo,

            "capacidade_litros":
                capacidade,

            "agua_litros":
                agua,

            "insumos_liquidos_litros":
                insumos,

            "volume_final_fisico_litros":
                volume_fisico,

            "excesso_litros":
                excesso,

            "dentro_da_capacidade":
                (
                    volume_alvo_dentro
                    and volume_fisico_dentro
                ),

            "volume_alvo_dentro_da_capacidade":
                volume_alvo_dentro,

            "volume_fisico_dentro_da_capacidade":
                volume_fisico_dentro
        }

    # ======================================================
    # VERIFICAR INSUMOS
    # ======================================================

    def verificar_insumos(self):

        quantidades = (
            self.calcular_quantidades()
        )

        resultado = []

        # --------------------------------------------------
        # Sem sistema de dosagem
        # --------------------------------------------------

        if self.sistema_dosagem is None:

            for item in quantidades:

                resultado.append({

                    "insumo":
                        item["nome"],

                    "necessario":
                        item["quantidade"],

                    "disponivel":
                        None,

                    "suficiente":
                        None
                })

            return resultado

        # --------------------------------------------------
        # Com sistema de dosagem
        # --------------------------------------------------

        for item in quantidades:

            nome = item["nome"]

            try:

                status = (
                    self.sistema_dosagem
                    .status_insumo(
                        nome
                    )
                )

            except (
                AttributeError,
                KeyError
            ):

                resultado.append({

                    "insumo":
                        nome,

                    "necessario":
                        item["quantidade"],

                    "disponivel":
                        None,

                    "suficiente":
                        False
                })

                continue

            disponivel = float(
                status["nivel_ml"]
            )

            necessario = float(
                item["quantidade"]
            )

            resultado.append({

                "insumo":
                    nome,

                "necessario":
                    necessario,

                "disponivel":
                    disponivel,

                "suficiente":
                    (
                        disponivel
                        >= necessario
                    )
            })

        return resultado

    # ======================================================
    # VALIDAR
    # ======================================================

    def validar(self):

        problemas = []

        capacidade = (
            self.verificar_capacidade()
        )

        # --------------------------------------------------
        # PROBLEMA 1:
        # volume-alvo maior que capacidade
        # --------------------------------------------------

        if not capacidade[
            "volume_alvo_dentro_da_capacidade"
        ]:

            problemas.append({

                "tipo":
                    "CAPACIDADE",

                "mensagem":
                    (
                        "O volume alvo da "
                        "solução excede a "
                        "capacidade do "
                        "reservatório."
                    ),

                "volume_alvo_litros":
                    capacidade[
                        "volume_alvo_litros"
                    ],

                "capacidade_litros":
                    capacidade[
                        "capacidade_litros"
                    ]
            })

        # --------------------------------------------------
        # PROBLEMA 2:
        # volume físico maior que capacidade
        # --------------------------------------------------

        if not capacidade[
            "volume_fisico_dentro_da_capacidade"
        ]:

            problemas.append({

                "tipo":
                    "VOLUME_FISICO",

                "mensagem":
                    (
                        "O volume físico "
                        "final da preparação "
                        "excede a capacidade "
                        "do reservatório."
                    ),

                "volume_final_fisico_litros":
                    capacidade[
                        "volume_final_fisico_litros"
                    ],

                "capacidade_litros":
                    capacidade[
                        "capacidade_litros"
                    ],

                "excesso_litros":
                    capacidade[
                        "excesso_litros"
                    ]
            })

        # --------------------------------------------------
        # INSUMOS
        # --------------------------------------------------

        verificacao = (
            self.verificar_insumos()
        )

        for item in verificacao:

            # Sem sistema de dosagem:
            # não temos como verificar estoque.

            if item["suficiente"] is None:
                continue

            if not item["suficiente"]:

                problemas.append({

                    "tipo":
                        "INSUMO",

                    "insumo":
                        item["insumo"],

                    "necessario":
                        item["necessario"],

                    "disponivel":
                        item["disponivel"]
                })

        return {

            "valido":
                len(problemas) == 0,

            "problemas":
                problemas
        }

    # ======================================================
    # GERAR PLANO
    # ======================================================

    def gerar_plano(self):

        volume = (
            self.volume_alvo()
        )

        quantidades = (
            self.calcular_quantidades()
        )

        validacao = (
            self.validar()
        )

        etapas = []

        # --------------------------------------------------
        # ÁGUA
        # --------------------------------------------------

        etapas.append({

            "ordem":
                1,

            "tipo":
                "AGUA",

            "volume_litros":
                self.volume_agua_inicial_litros(),

            "descricao":
                (
                    "Adicionar água ao "
                    "reservatório."
                )
        })

        # --------------------------------------------------
        # INSUMOS
        # --------------------------------------------------

        ordem = 2

        for item in quantidades:

            etapa = {

                "ordem":
                    ordem,

                "tipo":
                    "DOSAGEM",

                "insumo":
                    item["nome"],

                "quantidade":
                    item["quantidade"],

                "unidade":
                    item["unidade"],

                "volume_reservatorio_litros":
                    volume
            }

            # ------------------------------------------------
            # Bomba dosadora
            # ------------------------------------------------

            if (
                self.sistema_dosagem
                is not None
            ):

                try:

                    tempo = (
                        self.sistema_dosagem
                        .tempo_para_dosar(
                            item["nome"],
                            item["quantidade"]
                        )
                    )

                    etapa[
                        "tempo_segundos"
                    ] = tempo

                except (
                    AttributeError,
                    KeyError
                ):

                    etapa[
                        "tempo_segundos"
                    ] = None

            etapas.append(
                etapa
            )

            ordem += 1

        # --------------------------------------------------
        # VERIFICAÇÃO
        # --------------------------------------------------

        etapas.append({

            "ordem":
                ordem,

            "tipo":
                "VERIFICACAO",

            "descricao":
                (
                    "Misturar a solução "
                    "e verificar pH e EC."
                )
        })

        return {

            "receita":
                self.receita.nome,

            "fase":
                self.receita.fase,

            "volume_final_litros":
                volume,

            "capacidade_reservatorio_litros":
                self.capacidade_litros(),

            "agua_inicial_litros":
                self.volume_agua_inicial_litros(),

            "volume_insumos_ml":
                self.volume_insumos_ml(),

            "volume_insumos_litros":
                self.volume_insumos_litros(),

            "volume_final_fisico_litros":
                self.volume_final_fisico_litros(),

            "excesso_litros":
                self.excesso_volume_litros(),

            "ph_alvo": {

                "min":
                    self.receita.ph_min,

                "max":
                    self.receita.ph_max
            },

            "ec_alvo": {

                "min":
                    self.receita.ec_min,

                "max":
                    self.receita.ec_max
            },

            "valido":
                validacao["valido"],

            "problemas":
                validacao["problemas"],

            "etapas":
                etapas
        }

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "receita":
                self.receita.snapshot(),

            "reservatorio":
                self.reservatorio.snapshot(),

            "capacidade":
                self.verificar_capacidade(),

            "quantidades":
                self.calcular_quantidades(),

            "agua_inicial_litros":
                self.volume_agua_inicial_litros(),

            "volume_insumos_ml":
                self.volume_insumos_ml(),

            "volume_final_fisico_litros":
                self.volume_final_fisico_litros(),

            "validacao":
                self.validar(),

            "plano":
                self.gerar_plano()
        }