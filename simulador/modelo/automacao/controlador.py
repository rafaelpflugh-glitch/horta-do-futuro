"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

CONTROLADOR DE AUTOMAÇÃO

Fluxo:

    diagnosticar
         ↓
      decidir
         ↓
    segurança
         ↓
      dosar
         ↓
      mistura
         ↓
    nova leitura
         ↓
    corrigir ou encerrar

O controlador não tenta resolver situações que ultrapassam
seus limites de segurança.

Quando não pode corrigir automaticamente:

    → bloqueia
    → registra evento
    → solicita intervenção humana

IMPORTANTE:

O controlador NÃO define a composição química dos nutrientes.

O produto utilizado para correção é configurável.

Exemplo de produto no simulador:

    NUTRIENTE_A

Esse nome representa apenas um reservatório de solução
nutritiva. A composição real deverá ser definida posteriormente
conforme o fertilizante escolhido para o projeto físico.

============================================================
"""

from modelo.automacao.eventos import RegistroEventos
from modelo.automacao.seguranca import SegurancaAutomacao
from modelo.automacao.dosagem import SistemaDosagem


class ControladorAutomacao:

    def __init__(
        self,
        horta,
        dosagem=None,
        seguranca=None,
        eventos=None,
        produto_nutriente="NUTRIENTE_A"
    ):

        # ==================================================
        # DEPENDÊNCIAS
        # ==================================================

        self.horta = horta

        self.dosagem = (
            dosagem
            if dosagem is not None
            else SistemaDosagem()
        )

        self.seguranca = (
            seguranca
            if seguranca is not None
            else SegurancaAutomacao()
        )

        self.eventos = (
            eventos
            if eventos is not None
            else RegistroEventos()
        )

        # ==================================================
        # CONFIGURAÇÃO DO PRODUTO
        # ==================================================

        # Este nome identifica o reservatório utilizado pelo
        # simulador. Não representa uma composição química real.
        self.produto_nutriente = str(
            produto_nutriente
        )

        # ==================================================
        # ESTADO DO CONTROLADOR
        # ==================================================

        self.ativo = True

        self.ocupado = False

        self.em_mistura = False

        self.mistura_restante_segundos = 0

        # Número de ciclos de decisão executados.
        self.ciclo = 0

        # Número de dosagens realizadas nesta sessão.
        self.tentativas_ciclo = 0

        self.dose_total_ciclo_ml = 0.0

        self.dose_total_diaria_ml = 0.0

        self.ultima_acao = None

        self.ultimo_resultado = None

        self.estado = "PRONTO"

        self.intervencao_necessaria = False

        self.motivo_intervencao = None

        # ==================================================
        # DADOS DA MISTURA ATUAL
        # ==================================================

        self.produto_mistura = None

        self.dose_mistura_ml = 0.0

    # ======================================================
    # DIAGNÓSTICO GERAL
    # ======================================================

    def diagnosticar(self):

        return {

            "ec":
                self.diagnosticar_ec(),

            "ph":
                self.diagnosticar_ph(),

            "temperatura_ar": {

                "atual":
                    self.horta.temperatura_ar,

                "minimo":
                    self.horta.config.temperatura_ar_min,

                "maximo":
                    self.horta.config.temperatura_ar_max
            },

            "temperatura_agua": {

                "atual":
                    self.horta.temperatura_agua,

                "minimo":
                    self.horta.config.temperatura_agua_min,

                "maximo":
                    self.horta.config.temperatura_agua_max
            },

            "umidade_ar": {

                "atual":
                    self.horta.umidade_ar,

                "minimo":
                    self.horta.config.umidade_ar_min,

                "maximo":
                    self.horta.config.umidade_ar_max
            },

            "nivel_agua": {

                "atual":
                    self.horta.nivel_agua,

                "status":
                    self.horta.nivel_agua_status()
            }
        }

    # ======================================================
    # DIAGNÓSTICO EC
    # ======================================================

    def diagnosticar_ec(self):

        atual = float(
            self.horta.ec
        )

        minimo = float(
            self.horta.config.ec_min
        )

        maximo = float(
            self.horta.config.ec_max
        )

        alvo = (
            minimo + maximo
        ) / 2

        diferenca = alvo - atual

        # --------------------------------------------------
        # EC ABAIXO DO MÍNIMO
        # --------------------------------------------------

        if atual < minimo:

            estado = "BAIXO"

            correcao = True

            acao = (
                f"ADICIONAR_{self.produto_nutriente}"
            )

        # --------------------------------------------------
        # EC ACIMA DO MÁXIMO
        # --------------------------------------------------

        elif atual > maximo:

            estado = "ALTO"

            correcao = False

            acao = "DILUIR"

        # --------------------------------------------------
        # EC ABAIXO DO ALVO
        # --------------------------------------------------

        elif atual < alvo:

            estado = "ABAIXO_DO_ALVO"

            correcao = True

            acao = (
                f"ADICIONAR_{self.produto_nutriente}"
            )

        # --------------------------------------------------
        # EC ADEQUADA
        # --------------------------------------------------

        else:

            estado = "OK"

            correcao = False

            acao = "NENHUMA"

        return {

            "parametro":
                "EC",

            "estado":
                estado,

            "atual":
                atual,

            "minimo":
                minimo,

            "maximo":
                maximo,

            "alvo":
                alvo,

            "diferenca":
                diferenca,

            "correcao_necessaria":
                correcao,

            "acao":
                acao
        }

    # ======================================================
    # DIAGNÓSTICO PH
    # ======================================================

    def diagnosticar_ph(self):

        atual = float(
            self.horta.ph
        )

        minimo = float(
            self.horta.config.ph_min
        )

        maximo = float(
            self.horta.config.ph_max
        )

        alvo = (
            minimo + maximo
        ) / 2

        diferenca = alvo - atual

        # --------------------------------------------------
        # PH ABAIXO DO LIMITE
        # --------------------------------------------------

        if atual < minimo:

            estado = "BAIXO"

            correcao = False

            acao = "INTERVENCAO"

        # --------------------------------------------------
        # PH ACIMA DO LIMITE
        # --------------------------------------------------

        elif atual > maximo:

            estado = "ALTO"

            correcao = False

            acao = "INTERVENCAO"

        # --------------------------------------------------
        # PH NORMAL
        # --------------------------------------------------

        else:

            estado = "OK"

            correcao = False

            acao = "NENHUMA"

        return {

            "parametro":
                "PH",

            "estado":
                estado,

            "atual":
                atual,

            "minimo":
                minimo,

            "maximo":
                maximo,

            "alvo":
                alvo,

            "diferenca":
                diferenca,

            "correcao_necessaria":
                correcao,

            "acao":
                acao
        }

    # ======================================================
    # SOLICITAR INTERVENÇÃO
    # ======================================================

    def solicitar_intervencao(
        self,
        motivo,
        dados=None
    ):

        self.intervencao_necessaria = True

        self.motivo_intervencao = motivo

        self.estado = (
            "INTERVENCAO_NECESSARIA"
        )

        self.ocupado = False

        self.ultima_acao = "INTERVENCAO"

        self.eventos.aviso(
            "INTERVENCAO",
            motivo,
            dados or {}
        )

    # ======================================================
    # LIMPAR INTERVENÇÃO
    # ======================================================

    def limpar_intervencao(self):

        self.intervencao_necessaria = False

        self.motivo_intervencao = None

        if not self.em_mistura:

            self.estado = "PRONTO"

    # ======================================================
    # FINALIZAR BOMBA
    # ======================================================

    def finalizar_bomba(
        self,
        produto
    ):
        """
        Desliga a bomba após a dosagem.

        Mantém compatibilidade com diferentes versões
        do SistemaDosagem.
        """

        if produto is None:
            return

        # --------------------------------------------------
        # API EXPLÍCITA
        # --------------------------------------------------

        if hasattr(
            self.dosagem,
            "parar_bomba"
        ):

            self.dosagem.parar_bomba(
                produto
            )

            return

        # --------------------------------------------------
        # API ALTERNATIVA
        # --------------------------------------------------

        if hasattr(
            self.dosagem,
            "parar"
        ):

            try:

                self.dosagem.parar(
                    produto
                )

                return

            except TypeError:

                pass

        # --------------------------------------------------
        # COMPATIBILIDADE DIRETA
        # --------------------------------------------------

        bombas = getattr(
            self.dosagem,
            "bombas_ativas",
            None
        )

        if isinstance(
            bombas,
            dict
        ):

            bombas[produto] = False

    # ======================================================
    # SEGURANÇA EC
    # ======================================================

    def validar_ec(self):

        resultado = (
            self.seguranca.validar_ec(
                self.horta.ec
            )
        )

        if not resultado.permitido:

            self.solicitar_intervencao(
                resultado.motivo
            )

            return False

        return True

    # ======================================================
    # EXECUTAR UM CICLO
    # ======================================================

    def executar_ciclo(self):

        # ==================================================
        # SISTEMA DESATIVADO
        # ==================================================

        if not self.ativo:

            return {

                "estado":
                    "DESATIVADO"
            }

        # ==================================================
        # SISTEMA BLOQUEADO
        # ==================================================

        if self.intervencao_necessaria:

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # MISTURA EM ANDAMENTO
        # ==================================================

        if self.em_mistura:

            return {

                "estado":
                    "EM_MISTURA",

                "restante_segundos":
                    self.mistura_restante_segundos
            }

        # ==================================================
        # NOVO CICLO DE DECISÃO
        # ==================================================

        self.ciclo += 1

        self.eventos.info(
            "CONTROLADOR",
            "Iniciando ciclo de automação.",
            {
                "ciclo":
                    self.ciclo,

                "tentativa":
                    self.tentativas_ciclo + 1
            }
        )

        # ==================================================
        # LIMITE DE TENTATIVAS
        # ==================================================

        if (
            self.tentativas_ciclo
            >= self.seguranca
            .maximo_tentativas_ciclo
        ):

            self.solicitar_intervencao(
                "Número máximo de tentativas atingido.",
                {
                    "tentativas":
                        self.tentativas_ciclo,

                    "limite":
                        self.seguranca
                        .maximo_tentativas_ciclo
                }
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # SEGURANÇA EC
        # ==================================================

        if not self.validar_ec():

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # SEGURANÇA ABSOLUTA DO PH
        # ==================================================

        ph = self.diagnosticar_ph()

        if (
            ph["atual"]
            < self.seguranca
            .ph_minimo_absoluto
            or
            ph["atual"]
            > self.seguranca
            .ph_maximo_absoluto
        ):

            self.solicitar_intervencao(
                "pH fora do limite absoluto.",
                ph
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # DIAGNÓSTICO EC
        # ==================================================

        ec = self.diagnosticar_ec()

        self.ultimo_resultado = ec

        # ==================================================
        # EC NORMAL
        # ==================================================

        if not ec["correcao_necessaria"]:

            self.estado = "OK"

            self.ultima_acao = "NENHUMA"

            return {

                "estado":
                    "OK",

                "parametro":
                    "EC",

                "diagnostico":
                    ec
            }

        # ==================================================
        # EC ALTO
        # ==================================================

        if ec["estado"] == "ALTO":

            self.solicitar_intervencao(
                "EC acima do limite operacional. "
                "Diluição automática ainda não implementada.",
                ec
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao,

                "diagnostico":
                    ec
            }

        # ==================================================
        # PRODUTO DE CORREÇÃO
        # ==================================================

        produto = (
            self.produto_nutriente
        )

        # ==================================================
        # CALCULAR DOSE
        # ==================================================

        dose = min(
            abs(
                ec["diferenca"]
            ) * 50.0,

            self.seguranca
            .dose_maxima_ciclo_ml
        )

        dose = max(
            1.0,
            round(
                dose,
                2
            )
        )

        # ==================================================
        # SEGURANÇA DA DOSE
        # ==================================================

        resultado_seguranca = (
            self.seguranca
            .validar_dose(
                dose
            )
        )

        if not resultado_seguranca.permitido:

            self.solicitar_intervencao(
                resultado_seguranca.motivo
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # LIMITE DIÁRIO
        # ==================================================

        if (
            self.dose_total_diaria_ml
            + dose
            > self.seguranca
            .dose_maxima_diaria_ml
        ):

            self.solicitar_intervencao(
                "Limite diário de dosagem atingido.",
                {
                    "dose_diaria":
                        self.dose_total_diaria_ml,

                    "dose_solicitada":
                        dose,

                    "limite_diario":
                        self.seguranca
                        .dose_maxima_diaria_ml
                }
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # RESERVATÓRIO
        # ==================================================

        reservatorios = (
            self.dosagem
            .snapshot()
            .get(
                "reservatorios",
                {}
            )
        )

        reservatorio = (
            reservatorios.get(
                produto
            )
        )

        # --------------------------------------------------
        # RESERVATÓRIO NÃO EXISTE
        # --------------------------------------------------

        if reservatorio is None:

            self.solicitar_intervencao(
                f"Reservatório {produto} não existe.",
                {
                    "produto":
                        produto,

                    "reservatorios_disponiveis":
                        list(
                            reservatorios.keys()
                        )
                }
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # --------------------------------------------------
        # NÍVEL DO RESERVATÓRIO
        # --------------------------------------------------

        nivel = float(
            reservatorio[
                "nivel_ml"
            ]
        )

        nivel_minimo = float(
            self.seguranca
            .nivel_minimo_reservatorio_ml
        )

        if (
            nivel - dose
            < nivel_minimo
        ):

            self.solicitar_intervencao(
                f"Reservatório {produto} insuficiente.",
                {
                    "produto":
                        produto,

                    "nivel_ml":
                        nivel,

                    "dose_solicitada_ml":
                        dose,

                    "nivel_minimo_ml":
                        nivel_minimo
                }
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # EXECUTAR DOSAGEM
        # ==================================================

        sucesso = self.dosagem.dosar(
            produto,
            dose
        )

        if not sucesso:

            self.solicitar_intervencao(
                f"Falha na dosagem de {produto}.",
                {
                    "produto":
                        produto,

                    "dose_ml":
                        dose
                }
            )

            return {

                "estado":
                    "INTERVENCAO_NECESSARIA",

                "motivo":
                    self.motivo_intervencao
            }

        # ==================================================
        # REGISTRAR TENTATIVA
        # ==================================================

        self.tentativas_ciclo += 1

        self.dose_total_ciclo_ml += dose

        self.dose_total_diaria_ml += dose

        # ==================================================
        # PREPARAR MISTURA
        # ==================================================

        self.produto_mistura = produto

        self.dose_mistura_ml = dose

        self.em_mistura = True

        self.mistura_restante_segundos = (
            self.seguranca
            .tempo_mistura_segundos
        )

        self.ocupado = True

        self.estado = "MISTURA"

        self.ultima_acao = (
            f"DOSAGEM_{produto}"
        )

        # ==================================================
        # EVENTO DE DOSAGEM
        # ==================================================

        self.eventos.info(
            "DOSAGEM",
            "Dosagem executada.",
            {
                "produto":
                    produto,

                "dose_ml":
                    dose,

                "ciclo":
                    self.ciclo,

                "tentativa":
                    self.tentativas_ciclo,

                "dose_total_ciclo_ml":
                    self.dose_total_ciclo_ml
            }
        )

        # ==================================================
        # EVENTO DE MISTURA
        # ==================================================

        self.eventos.info(
            "MISTURA",
            "Período de mistura iniciado.",
            {
                "produto":
                    produto,

                "dose_ml":
                    dose,

                "duracao_segundos":
                    self.mistura_restante_segundos
            }
        )

        return {

            "estado":
                "DOSANDO",

            "parametro":
                "EC",

            "acao":
                f"DOSAGEM_{produto}",

            "produto":
                produto,

            "dose_ml":
                dose,

            "mistura_segundos":
                self.mistura_restante_segundos,

            "tentativa":
                self.tentativas_ciclo
        }

    # ======================================================
    # AVANÇAR MISTURA
    # ======================================================

    def avancar_mistura(
        self,
        segundos
    ):

        # ==================================================
        # NÃO HÁ MISTURA
        # ==================================================

        if not self.em_mistura:

            return {

                "estado":
                    "SEM_MISTURA"
            }

        segundos = max(
            0,
            float(segundos)
        )

        self.mistura_restante_segundos = max(
            0,
            self.mistura_restante_segundos
            - segundos
        )

        # ==================================================
        # MISTURA AINDA EM ANDAMENTO
        # ==================================================

        if (
            self.mistura_restante_segundos
            > 0
        ):

            return {

                "estado":
                    "MISTURANDO",

                "restante_segundos":
                    self.mistura_restante_segundos
            }

        # ==================================================
        # MISTURA CONCLUÍDA
        # ==================================================

        produto = (
            self.produto_mistura
        )

        dose = (
            self.dose_mistura_ml
        )

        # --------------------------------------------------
        # DESLIGAR BOMBA
        # --------------------------------------------------

        self.finalizar_bomba(
            produto
        )

        # ==================================================
        # SIMULAÇÃO DA RESPOSTA DO SENSOR
        # ==================================================

        if (
            produto
            == self.produto_nutriente
        ):

            # ------------------------------------------------
            # MODELO SIMPLIFICADO DO DIGITAL TWIN
            #
            # Isto NÃO representa uma relação física real
            # entre ml de fertilizante e EC.
            #
            # É apenas uma aproximação para validar a lógica
            # do controlador.
            # ------------------------------------------------

            incremento = (
                dose
                * 0.02
            )

            self.horta.ec = min(
                self.seguranca
                .ec_maximo_absoluto,

                self.horta.ec
                + incremento
            )

        ec_resultante = (
            self.horta.ec
        )

        # ==================================================
        # LIMPAR ESTADO DA MISTURA
        # ==================================================

        self.em_mistura = False

        self.ocupado = False

        self.mistura_restante_segundos = 0

        self.produto_mistura = None

        self.dose_mistura_ml = 0.0

        self.estado = "PRONTO"

        # ==================================================
        # REGISTRAR EVENTO
        # ==================================================

        self.eventos.info(
            "MISTURA",
            "Mistura concluída.",
            {
                "produto":
                    produto,

                "dose_ml":
                    dose,

                "ec_resultante":
                    ec_resultante
            }
        )

        # ==================================================
        # NOVA LEITURA
        # ==================================================

        diagnostico = (
            self.diagnosticar_ec()
        )

        self.ultimo_resultado = (
            diagnostico
        )

        return {

            "estado":
                "MISTURA_CONCLUIDA",

            "ec":
                ec_resultante,

            "diagnostico":
                diagnostico
        }

    # ======================================================
    # CICLO COMPLETO
    # ======================================================

    def executar_ciclo_completo(
        self,
        max_ciclos=10
    ):

        resultados = []

        # ==================================================
        # NOVA SESSÃO DE AUTOMAÇÃO
        # ==================================================

        self.tentativas_ciclo = 0

        self.dose_total_ciclo_ml = 0.0

        self.limpar_intervencao()

        self.estado = "AUTOMACAO"

        # ==================================================
        # EXECUÇÃO
        # ==================================================

        for _ in range(
            max_ciclos
        ):

            resultado = (
                self.executar_ciclo()
            )

            resultados.append(
                resultado
            )

            estado = (
                resultado.get(
                    "estado"
                )
            )

            # ==================================================
            # RESOLVIDO
            # ==================================================

            if estado == "OK":

                self.estado = "OK"

                self.eventos.info(
                    "CONTROLADOR",
                    "Correção automática concluída.",
                    {
                        "ec_final":
                            self.horta.ec,

                        "tentativas":
                            self.tentativas_ciclo,

                        "dose_total_ml":
                            self.dose_total_ciclo_ml
                    }
                )

                return {

                    "estado":
                        "OK",

                    "ec_final":
                        self.horta.ec,

                    "tentativas":
                        self.tentativas_ciclo,

                    "dose_total_ml":
                        self.dose_total_ciclo_ml,

                    "resultados":
                        resultados
                }

            # ==================================================
            # DOSAGEM → MISTURA → NOVA LEITURA
            # ==================================================

            if estado == "DOSANDO":

                mistura = (
                    self.avancar_mistura(
                        self.seguranca
                        .tempo_mistura_segundos
                    )
                )

                resultados.append(
                    mistura
                )

                continue

            # ==================================================
            # INTERVENÇÃO HUMANA
            # ==================================================

            if (
                estado
                == "INTERVENCAO_NECESSARIA"
            ):

                return {

                    "estado":
                        "INTERVENCAO_NECESSARIA",

                    "motivo":
                        self.motivo_intervencao,

                    "ec_final":
                        self.horta.ec,

                    "tentativas":
                        self.tentativas_ciclo,

                    "dose_total_ml":
                        self.dose_total_ciclo_ml,

                    "resultados":
                        resultados
                }

            # ==================================================
            # SISTEMA DESATIVADO
            # ==================================================

            if estado == "DESATIVADO":

                return {

                    "estado":
                        "DESATIVADO",

                    "ec_final":
                        self.horta.ec,

                    "tentativas":
                        self.tentativas_ciclo,

                    "dose_total_ml":
                        self.dose_total_ciclo_ml,

                    "resultados":
                        resultados
                }

        # ==================================================
        # LIMITE DO CICLO COMPLETO
        # ==================================================

        self.solicitar_intervencao(
            "Número máximo de ciclos automáticos atingido.",
            {
                "max_ciclos":
                    max_ciclos,

                "tentativas":
                    self.tentativas_ciclo,

                "ec_atual":
                    self.horta.ec
            }
        )

        return {

            "estado":
                "INTERVENCAO_NECESSARIA",

            "motivo":
                self.motivo_intervencao,

            "ec_final":
                self.horta.ec,

            "tentativas":
                self.tentativas_ciclo,

            "dose_total_ml":
                self.dose_total_ciclo_ml,

            "resultados":
                resultados
        }

    # ======================================================
    # RESET DO CICLO
    # ======================================================

    def resetar_ciclo(self):

        self.tentativas_ciclo = 0

        self.dose_total_ciclo_ml = 0.0

        self.ultima_acao = None

        self.ultimo_resultado = None

        self.limpar_intervencao()

        if not self.em_mistura:

            self.estado = "PRONTO"

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "ativo":
                self.ativo,

            "estado":
                self.estado,

            "ocupado":
                self.ocupado,

            "em_mistura":
                self.em_mistura,

            "mistura_restante_segundos":
                self.mistura_restante_segundos,

            "ciclo":
                self.ciclo,

            "tentativas_ciclo":
                self.tentativas_ciclo,

            "dose_total_ciclo_ml":
                self.dose_total_ciclo_ml,

            "dose_total_diaria_ml":
                self.dose_total_diaria_ml,

            "ultima_acao":
                self.ultima_acao,

            "ultimo_resultado":
                self.ultimo_resultado,

            "intervencao_necessaria":
                self.intervencao_necessaria,

            "motivo_intervencao":
                self.motivo_intervencao,

            "produto_nutriente":
                self.produto_nutriente,

            "produto_mistura":
                self.produto_mistura,

            "dose_mistura_ml":
                self.dose_mistura_ml,

            "dosagem":
                self.dosagem.snapshot(),

            "seguranca":
                self.seguranca.snapshot()
        }