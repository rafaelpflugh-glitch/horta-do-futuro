"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN
============================================================

Modelo virtual da estufa.

A Horta representa o estado atual do cultivo.

A configuração da cultura é fornecida pelo banco de
cultivos e pode ser alterada pela interface sem modificar
o motor principal.

Arquitetura:

    BANCO DE CULTIVOS
            ↓
    CONFIGURAÇÃO DA CULTURA
            ↓
          HORTA
            ↓
      diagnóstico
            ↓
       automação
            ↓
      relógio virtual
            ↓
         ESP32

FASES:

    SEMENTE
       ↓
    MUDA
       ↓
    VEGETATIVO
       ↓
    FLORAÇÃO
       ↓
    COLHEITA

RESERVATÓRIO:

    A Horta agora representa o volume real da solução
    nutritiva em mililitros.

    Exemplo:

        capacidade = 10.000 mL
        volume     = 7.500 mL
        nível      = 75%

    O atributo nivel_agua continua existindo como
    compatibilidade com o código antigo.

DOSAGEM:

    A Horta registra a entrada de insumos na solução.

    IMPORTANTE:

        Este módulo NÃO calcula ainda a alteração da EC
        causada por uma dosagem.

        Isso será definido posteriormente a partir dos
        dados reais do fabricante do fertilizante.

============================================================
"""

from modelo.configuracao import ConfiguracaoCultivo
from modelo.relogio_virtual import RelogioVirtual
from modelo.banco_cultivos import obter_configuracao_cultura


class Horta:

    # ======================================================
    # FASES SUPORTADAS
    # ======================================================

    FASES_VALIDAS = (
        "SEMENTE",
        "MUDA",
        "VEGETATIVO",
        "FLORAÇÃO",
        "COLHEITA",
    )

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    def __init__(self):

        # --------------------------------------------------
        # CONFIGURAÇÃO INICIAL
        # --------------------------------------------------

        self.config = obter_configuracao_cultura(
            "ALFACE"
        )

        self.cultivo = self.config.nome

        # ==================================================
        # RESERVATÓRIO DA SOLUÇÃO NUTRITIVA
        # ==================================================

        # --------------------------------------------------
        # Capacidade física do reservatório.
        #
        # Valor inicial de simulação:
        #
        # 10 litros = 10.000 mL
        #
        # Posteriormente isso poderá vir da configuração
        # física da estufa.
        # --------------------------------------------------

        self.capacidade_reservatorio_ml = 10000.0

        # --------------------------------------------------
        # Volume atual da solução nutritiva.
        #
        # Inicialmente o reservatório está cheio.
        # --------------------------------------------------

        self.volume_solucao_ml = (
            self.capacidade_reservatorio_ml
        )

        # --------------------------------------------------
        # Compatibilidade com o modelo antigo.
        #
        # nivel_agua representa porcentagem:
        #
        # 100 = cheio
        # 50  = metade
        # 0   = vazio
        #
        # O valor é sincronizado automaticamente com o
        # volume real através de _atualizar_nivel_agua().
        # --------------------------------------------------

        self.nivel_agua = 100.0

        # --------------------------------------------------
        # SENSORES VIRTUAIS
        # --------------------------------------------------

        self.temperatura_ar = 24.5

        self.umidade_ar = 60.0

        self.temperatura_agua = 22.0

        self.ph = 6.0

        self.ec = 1.4

        # ==================================================
        # HISTÓRICO DE DOSAGEM
        # ==================================================

        # --------------------------------------------------
        # Registra eventos de dosagem ocorridos na solução.
        #
        # Exemplo:
        #
        # {
        #     "produto": "NUTRIENTE_A",
        #     "dose_ml": 10.0
        # }
        #
        # Esse histórico será útil futuramente para:
        #
        # - diagnóstico
        # - auditoria
        # - treinamento do modelo
        # - comparação entre dose prevista e EC real
        # --------------------------------------------------

        self.historico_dosagem = []

        # --------------------------------------------------
        # SAÚDE
        # --------------------------------------------------

        self.saude = 100

        self.status = "SAUDÁVEL"

        # --------------------------------------------------
        # ATUADORES
        # --------------------------------------------------

        self.ventilacao = False

        self.bomba = False

        self.iluminacao = False

        # --------------------------------------------------
        # RELÓGIO VIRTUAL
        # --------------------------------------------------

        self.relogio = RelogioVirtual(
            hora=13,
            minuto=0
        )

        # --------------------------------------------------
        # ESTADO INICIAL
        # --------------------------------------------------

        self._atualizar_nivel_agua()

        self.diagnosticar()

        self.atualizar_fotoperiodo()

    # ======================================================
    # PROPRIEDADES DO RELÓGIO
    # ======================================================

    @property
    def hora_atual(self):

        return self.relogio.hora

    @property
    def minuto_atual(self):

        return self.relogio.minuto

    @property
    def velocidade_tempo(self):

        return self.relogio.velocidade

    # ======================================================
    # RELÓGIO
    # ======================================================

    def definir_hora(
        self,
        hora,
        minuto
    ):

        self.relogio.definir_hora(
            hora,
            minuto
        )

        self.atualizar_fotoperiodo()

    # ------------------------------------------------------

    def avancar_tempo(
        self,
        minutos
    ):

        self.relogio.avancar(
            minutos
        )

        self.atualizar_fotoperiodo()

    # ------------------------------------------------------

    def avancar_horas(
        self,
        horas
    ):

        self.relogio.avancar_horas(
            horas
        )

        self.atualizar_fotoperiodo()

    # ------------------------------------------------------

    def avancar_dias(
        self,
        dias
    ):

        self.relogio.avancar_dias(
            dias
        )

        self.atualizar_fotoperiodo()

    # ------------------------------------------------------

    def configurar_velocidade_tempo(
        self,
        velocidade
    ):

        self.relogio.configurar_velocidade(
            velocidade
        )

    # ------------------------------------------------------

    def tick_tempo(self):

        self.relogio.tick()

        self.atualizar_fotoperiodo()

        self.executar_automacao()

    # ======================================================
    # SENSORES
    # ======================================================

    def alterar_temperatura_ar(
        self,
        valor
    ):

        self.temperatura_ar = float(valor)

    # ------------------------------------------------------

    def alterar_umidade_ar(
        self,
        valor
    ):

        self.umidade_ar = float(valor)

    # ------------------------------------------------------

    def alterar_temperatura_agua(
        self,
        valor
    ):

        self.temperatura_agua = float(valor)

    # ------------------------------------------------------

    def alterar_ph(
        self,
        valor
    ):

        self.ph = float(valor)

    # ------------------------------------------------------

    def alterar_ec(
        self,
        valor
    ):

        self.ec = float(valor)

    # ------------------------------------------------------

    def alterar_nivel_agua(
        self,
        valor
    ):

        valor = float(valor)

        # --------------------------------------------------
        # Compatibilidade:
        #
        # Este método continua recebendo porcentagem.
        #
        # Exemplo:
        #
        # alterar_nivel_agua(50)
        #
        # significa 50% do reservatório.
        # --------------------------------------------------

        self.nivel_agua = max(
            0.0,
            min(100.0, valor)
        )

        # --------------------------------------------------
        # Converte porcentagem para volume real.
        # --------------------------------------------------

        self.volume_solucao_ml = (
            self.capacidade_reservatorio_ml
            * self.nivel_agua
            / 100.0
        )

        # --------------------------------------------------
        # Segurança imediata da bomba.
        # --------------------------------------------------

        if self.nivel_agua <= 10:

            self.desligar_bomba()

    # ======================================================
    # RESERVATÓRIO
    # ======================================================

    def _atualizar_nivel_agua(self):

        """
        Sincroniza o nível percentual com o volume real.

        volume_solucao_ml
                ↓
        nivel_agua (%)
        """

        if self.capacidade_reservatorio_ml <= 0:

            self.nivel_agua = 0.0

            return

        self.volume_solucao_ml = max(
            0.0,
            min(
                self.capacidade_reservatorio_ml,
                float(self.volume_solucao_ml)
            )
        )

        self.nivel_agua = (
            self.volume_solucao_ml
            / self.capacidade_reservatorio_ml
            * 100.0
        )

    # ------------------------------------------------------

    def alterar_volume_solucao(
        self,
        volume_ml
    ):

        """
        Define diretamente o volume da solução nutritiva.

        Exemplo:

            horta.alterar_volume_solucao(7500)

        significa:

            7.500 mL de solução no reservatório.

        O nível percentual é atualizado automaticamente.
        """

        volume_ml = float(
            volume_ml
        )

        if volume_ml < 0:

            raise ValueError(
                "O volume da solução não pode ser negativo."
            )

        if volume_ml > self.capacidade_reservatorio_ml:

            raise ValueError(
                "O volume da solução não pode "
                "ultrapassar a capacidade do reservatório."
            )

        self.volume_solucao_ml = volume_ml

        self._atualizar_nivel_agua()

        # --------------------------------------------------
        # Segurança da bomba.
        # --------------------------------------------------

        if self.nivel_agua <= 10:

            self.desligar_bomba()

    # ------------------------------------------------------

    def adicionar_agua(
        self,
        quantidade_ml
    ):

        """
        Adiciona água ao reservatório.

        A EC e o pH NÃO são recalculados automaticamente
        nesta etapa.

        Posteriormente poderemos modelar a diluição da EC
        usando a composição real da água.
        """

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "A quantidade de água deve ser positiva."
            )

        novo_volume = (
            self.volume_solucao_ml
            + quantidade_ml
        )

        self.volume_solucao_ml = min(
            self.capacidade_reservatorio_ml,
            novo_volume
        )

        self._atualizar_nivel_agua()

    # ------------------------------------------------------

    def remover_solucao(
        self,
        quantidade_ml
    ):

        """
        Remove solução nutritiva do reservatório.

        Pode representar:

        - descarte
        - troca parcial
        - retirada manual
        - perda simulada
        """

        quantidade_ml = float(
            quantidade_ml
        )

        if quantidade_ml <= 0:

            raise ValueError(
                "A quantidade de solução removida "
                "deve ser positiva."
            )

        if quantidade_ml > self.volume_solucao_ml:

            raise RuntimeError(
                "Não é possível remover mais solução "
                "do que existe no reservatório."
            )

        self.volume_solucao_ml -= quantidade_ml

        self._atualizar_nivel_agua()

        if self.nivel_agua <= 10:

            self.desligar_bomba()

    # ======================================================
    # DOSAGEM NA SOLUÇÃO
    # ======================================================

    def aplicar_dosagem(
        self,
        produto,
        dose_ml
    ):

        """
        Registra uma dosagem aplicada à solução nutritiva.

        IMPORTANTE:

        Este método NÃO calcula alteração da EC.

        O motivo é intencional.

        A relação:

            dose → EC

        depende do produto real e das condições da água.

        Quando tivermos o fertilizante real, poderemos
        cadastrar as informações do fabricante e desenvolver
        o modelo apropriado.

        Parâmetros:

            produto:
                Nome do insumo.

            dose_ml:
                Quantidade adicionada à solução.

        Exemplo:

            horta.aplicar_dosagem(
                "NUTRIENTE_A",
                10
            )
        """

        produto = str(
            produto
        ).strip().upper()

        dose_ml = float(
            dose_ml
        )

        if not produto:

            raise ValueError(
                "O nome do produto não pode ser vazio."
            )

        if dose_ml <= 0:

            raise ValueError(
                "A dose deve ser positiva."
            )

        # --------------------------------------------------
        # Registrar evento.
        # --------------------------------------------------

        evento = {

            "produto":
                produto,

            "dose_ml":
                dose_ml,

            "volume_solucao_ml":
                round(
                    self.volume_solucao_ml,
                    3
                ),

            "ec_antes":
                self.ec,

            "ph_antes":
                self.ph,
        }

        self.historico_dosagem.append(
            evento
        )

        # --------------------------------------------------
        # IMPORTANTE:
        #
        # Não alteramos EC nem pH aqui.
        #
        # Isso será implementado quando tivermos os dados
        # reais do produto.
        # --------------------------------------------------

        return evento

    # ======================================================
    # NÍVEL DA ÁGUA
    # ======================================================

    def nivel_agua_status(self):

        if self.nivel_agua <= 0:

            return "VAZIO"

        if self.nivel_agua <= 25:

            return "MUITO BAIXO"

        if self.nivel_agua <= 40:

            return "BAIXO"

        if self.nivel_agua <= 70:

            return "MÉDIO"

        if self.nivel_agua <= 90:

            return "ALTO"

        return "CHEIO"

    # ======================================================
    # FASE
    # ======================================================

    @property
    def fase_atual(self):

        return self.config.fase

    # ------------------------------------------------------

    def definir_fase(
        self,
        fase
    ):

        fase = str(
            fase
        ).strip().upper()

        if fase not in self.FASES_VALIDAS:

            raise ValueError(
                f"Fase inválida: '{fase}'. "
                f"Fases válidas: "
                f"{', '.join(self.FASES_VALIDAS)}"
            )

        # --------------------------------------------------
        # A própria configuração é responsável por aplicar
        # a receita da fase.
        # --------------------------------------------------

        if hasattr(
            self.config,
            "definir_fase"
        ):

            self.config.definir_fase(
                fase
            )

        else:

            # Compatibilidade com versões antigas.

            self.config.fase = fase

        self.diagnosticar()

        self.atualizar_fotoperiodo()

    # ======================================================
    # FOTOPERÍODO
    # ======================================================

    def esta_no_periodo_luz(self):

        inicio = (
            self.config.inicio_luz_hora * 60
            + self.config.inicio_luz_minuto
        )

        duracao = int(
            round(
                self.config.fotoperiodo_horas
                * 60
            )
        )

        agora = (
            self.hora_atual * 60
            + self.minuto_atual
        )

        # --------------------------------------------------
        # 24 HORAS OU MAIS
        # --------------------------------------------------

        if duracao >= 1440:

            return True

        # --------------------------------------------------
        # ZERO HORAS
        # --------------------------------------------------

        if duracao <= 0:

            return False

        # --------------------------------------------------
        # FIM DO PERÍODO
        # --------------------------------------------------

        fim = (
            inicio + duracao
        ) % 1440

        # --------------------------------------------------
        # CICLO NORMAL
        # --------------------------------------------------

        if inicio < fim:

            return (
                inicio <= agora < fim
            )

        # --------------------------------------------------
        # CICLO PASSANDO DA MEIA-NOITE
        # --------------------------------------------------

        return (
            agora >= inicio
            or agora < fim
        )

    # ------------------------------------------------------

    def atualizar_fotoperiodo(self):

        if self.esta_no_periodo_luz():

            self.ligar_iluminacao()

        else:

            self.desligar_iluminacao()

    # ======================================================
    # CONFIGURAÇÃO MANUAL DO FOTOPERÍODO
    # ======================================================

    def configurar_fotoperiodo(
        self,
        horas,
        hora_inicio,
        minuto_inicio
    ):

        self.config.configurar_fotoperiodo(
            horas,
            hora_inicio,
            minuto_inicio
        )

        self.atualizar_fotoperiodo()

    # ======================================================
    # APLICAR CONFIGURAÇÃO
    # ======================================================

    def aplicar_configuracao(
        self,
        configuracao
    ):

        if not isinstance(
            configuracao,
            ConfiguracaoCultivo
        ):

            raise TypeError(
                "A configuração deve ser "
                "uma ConfiguracaoCultivo."
            )

        self.config = configuracao

        self.cultivo = (
            configuracao.nome
        )

        self.diagnosticar()

        self.atualizar_fotoperiodo()

    # ======================================================
    # SELECIONAR CULTURA
    # ======================================================

    def selecionar_cultura(
        self,
        nome
    ):

        configuracao = (
            obter_configuracao_cultura(
                nome
            )
        )

        self.aplicar_configuracao(
            configuracao
        )

    # ======================================================
    # ATUADORES
    # ======================================================

    def ligar_ventilacao(self):

        self.ventilacao = True

    # ------------------------------------------------------

    def desligar_ventilacao(self):

        self.ventilacao = False

    # ------------------------------------------------------

    def ligar_bomba(self):

        # --------------------------------------------------
        # PROTEÇÃO CONTRA FUNCIONAMENTO A SECO
        # --------------------------------------------------

        if self.nivel_agua > 10:

            self.bomba = True

        else:

            self.bomba = False

    # ------------------------------------------------------

    def desligar_bomba(self):

        self.bomba = False

    # ------------------------------------------------------

    def ligar_iluminacao(self):

        self.iluminacao = True

    # ------------------------------------------------------

    def desligar_iluminacao(self):

        self.iluminacao = False

    # ======================================================
    # DIAGNÓSTICO
    # ======================================================

    def diagnosticar(self):

        pontos = 100

        # ==================================================
        # pH
        # ==================================================

        if self.ph < self.config.ph_min:

            pontos -= 15

        elif self.ph > self.config.ph_max:

            pontos -= 15

        # ==================================================
        # EC
        # ==================================================

        if self.ec < self.config.ec_min:

            pontos -= 10

        elif self.ec > self.config.ec_max:

            pontos -= 10

        # ==================================================
        # TEMPERATURA DO AR
        # ==================================================

        if (
            self.temperatura_ar
            < self.config.temperatura_ar_min
        ):

            pontos -= 10

        elif (
            self.temperatura_ar
            > self.config.temperatura_ar_max
        ):

            pontos -= 10

        # ==================================================
        # TEMPERATURA DA ÁGUA
        # ==================================================

        if (
            self.temperatura_agua
            < self.config.temperatura_agua_min
        ):

            pontos -= 10

        elif (
            self.temperatura_agua
            > self.config.temperatura_agua_max
        ):

            pontos -= 10

        # ==================================================
        # UMIDADE
        # ==================================================

        if (
            self.umidade_ar
            < self.config.umidade_ar_min
        ):

            pontos -= 10

        elif (
            self.umidade_ar
            > self.config.umidade_ar_max
        ):

            pontos -= 10

        # ==================================================
        # NÍVEL DA ÁGUA
        # ==================================================

        if self.nivel_agua <= 0:

            pontos -= 20

        elif self.nivel_agua <= 20:

            pontos -= 15

        elif self.nivel_agua <= 35:

            pontos -= 10

        # ==================================================
        # LIMITES
        # ==================================================

        pontos = max(
            0,
            min(100, pontos)
        )

        self.saude = pontos

        # ==================================================
        # CLASSIFICAÇÃO
        # ==================================================

        if self.saude >= 80:

            self.status = "SAUDÁVEL"

        elif self.saude >= 60:

            self.status = "ATENÇÃO"

        elif self.saude >= 40:

            self.status = "ESTRESSADA"

        else:

            self.status = "RISCO"

        return self.saude

    # ======================================================
    # AUTOMAÇÃO
    # ======================================================

    def executar_automacao(self):

        # --------------------------------------------------
        # VENTILAÇÃO
        # --------------------------------------------------

        if (
            self.temperatura_ar
            > self.config.temperatura_ar_max
        ):

            self.ligar_ventilacao()

        else:

            self.desligar_ventilacao()

        # --------------------------------------------------
        # SEGURANÇA DA BOMBA
        # --------------------------------------------------

        if self.nivel_agua <= 10:

            self.desligar_bomba()

        # --------------------------------------------------
        # ILUMINAÇÃO
        # --------------------------------------------------

        self.atualizar_fotoperiodo()

        # --------------------------------------------------
        # DIAGNÓSTICO
        # --------------------------------------------------

        self.diagnosticar()

    # ======================================================
    # RESET
    # ======================================================

    def resetar(self):

        # --------------------------------------------------
        # SENSORES
        # --------------------------------------------------

        self.temperatura_ar = 24.5

        self.umidade_ar = 60.0

        self.temperatura_agua = 22.0

        self.ph = 6.0

        self.ec = 1.4

        # --------------------------------------------------
        # RESERVATÓRIO
        # --------------------------------------------------

        self.capacidade_reservatorio_ml = 10000.0

        self.volume_solucao_ml = (
            self.capacidade_reservatorio_ml
        )

        self.nivel_agua = 100.0

        # --------------------------------------------------
        # HISTÓRICO
        # --------------------------------------------------

        self.historico_dosagem = []

        # --------------------------------------------------
        # ATUADORES
        # --------------------------------------------------

        self.ventilacao = False

        self.bomba = False

        self.iluminacao = False

        # --------------------------------------------------
        # RELÓGIO
        # --------------------------------------------------

        self.relogio.definir_hora(
            13,
            0
        )

        self.relogio.configurar_velocidade(
            1
        )

        # --------------------------------------------------
        # ESTADO
        # --------------------------------------------------

        self._atualizar_nivel_agua()

        self.diagnosticar()

        self.atualizar_fotoperiodo()

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            # ------------------------------------------------
            # IDENTIFICAÇÃO
            # ------------------------------------------------

            "cultivo":
                self.cultivo,

            "nome_cultivo":
                self.config.nome_cultivo,

            "fase":
                self.config.fase,

            # ------------------------------------------------
            # SENSORES
            # ------------------------------------------------

            "temperatura_ar":
                self.temperatura_ar,

            "umidade_ar":
                self.umidade_ar,

            "temperatura_agua":
                self.temperatura_agua,

            "ph":
                self.ph,

            "ec":
                self.ec,

            # ------------------------------------------------
            # RESERVATÓRIO
            # ------------------------------------------------

            "capacidade_reservatorio_ml":
                self.capacidade_reservatorio_ml,

            "volume_solucao_ml":
                self.volume_solucao_ml,

            "nivel_agua":
                self.nivel_agua,

            "nivel_agua_status":
                self.nivel_agua_status(),

            # ------------------------------------------------
            # HISTÓRICO DE DOSAGEM
            # ------------------------------------------------

            "historico_dosagem":
                list(self.historico_dosagem),

            # ------------------------------------------------
            # SAÚDE
            # ------------------------------------------------

            "saude":
                self.saude,

            "status":
                self.status,

            # ------------------------------------------------
            # ATUADORES
            # ------------------------------------------------

            "ventilacao":
                self.ventilacao,

            "bomba":
                self.bomba,

            "iluminacao":
                self.iluminacao,

            # ------------------------------------------------
            # FOTOPERÍODO
            # ------------------------------------------------

            "fotoperiodo_horas":
                self.config.fotoperiodo_horas,

            "inicio_luz_hora":
                self.config.inicio_luz_hora,

            "inicio_luz_minuto":
                self.config.inicio_luz_minuto,

            # ------------------------------------------------
            # RELÓGIO
            # ------------------------------------------------

            "hora_atual":
                self.hora_atual,

            "minuto_atual":
                self.minuto_atual,

            "periodo_luz":
                self.esta_no_periodo_luz(),

            "velocidade_tempo":
                self.velocidade_tempo,

            # ------------------------------------------------
            # CONFIGURAÇÃO COMPLETA
            # ------------------------------------------------

            "configuracao":
                self.config.snapshot()
        }