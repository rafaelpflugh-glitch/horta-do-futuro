# ============================================================
#
#                  HORTA DO FUTURO
#
#              DIGITAL TWIN - SIMULADOR
#
#                  DIAGNÓSTICO
#
# ============================================================


class Diagnostico:

    def __init__(self, horta):

        self.horta = horta

        self.alertas = []


    # ========================================================
    # EXECUTA DIAGNÓSTICO COMPLETO
    # ========================================================

    def executar(self):

        self.alertas = []

        pontos = 100


        # ----------------------------------------------------
        # PH
        # ----------------------------------------------------

        if self.horta.ph < 5.5:

            self.alertas.append(
                "pH muito baixo"
            )

            pontos -= 15


        elif self.horta.ph > 6.5:

            self.alertas.append(
                "pH muito alto"
            )

            pontos -= 15


        # ----------------------------------------------------
        # EC
        # ----------------------------------------------------

        if self.horta.ec < 1.0:

            self.alertas.append(
                "EC baixa - possível falta de nutrientes"
            )

            pontos -= 10


        elif self.horta.ec > 1.8:

            self.alertas.append(
                "EC alta - solução muito concentrada"
            )

            pontos -= 10


        # ----------------------------------------------------
        # TEMPERATURA DA ÁGUA
        # ----------------------------------------------------

        if self.horta.temperatura_agua < 18.0:

            self.alertas.append(
                "Água muito fria"
            )

            pontos -= 10


        elif self.horta.temperatura_agua > 26.0:

            self.alertas.append(
                "Água muito quente"
            )

            pontos -= 15


        # ----------------------------------------------------
        # TEMPERATURA DO AR
        # ----------------------------------------------------

        if self.horta.temperatura_ar < 18.0:

            self.alertas.append(
                "Temperatura ambiente baixa"
            )

            pontos -= 5


        elif self.horta.temperatura_ar > 26.0:

            self.alertas.append(
                "Temperatura ambiente alta"
            )

            pontos -= 10


        # ----------------------------------------------------
        # UMIDADE DO AR
        # ----------------------------------------------------

        if self.horta.umidade_ar < 50.0:

            self.alertas.append(
                "Umidade do ar baixa"
            )

            pontos -= 5


        elif self.horta.umidade_ar > 80.0:

            self.alertas.append(
                "Umidade do ar alta"
            )

            pontos -= 5


        # ----------------------------------------------------
        # NÍVEL DE ÁGUA
        # ----------------------------------------------------

        if not self.horta.nivel_agua_ok:

            self.alertas.append(
                "Nível de água baixo"
            )

            pontos -= 20


        # ----------------------------------------------------
        # LIMITES
        # ----------------------------------------------------

        if pontos < 0:

            pontos = 0


        if pontos > 100:

            pontos = 100


        # ----------------------------------------------------
        # SALVA SAÚDE
        # ----------------------------------------------------

        self.horta.saude = pontos


        # ----------------------------------------------------
        # MENSAGEM PRINCIPAL
        # ----------------------------------------------------

        if pontos >= 90:

            self.horta.mensagem = "Cultivo saudável"


        elif pontos >= 70:

            self.horta.mensagem = "Cultivo em boas condições"


        elif pontos >= 50:

            self.horta.mensagem = "Atenção necessária"


        elif pontos >= 30:

            self.horta.mensagem = "Cultivo sob estresse"


        else:

            self.horta.mensagem = "Condições críticas"


        return self.resultado()


    # ========================================================
    # RESULTADO DO DIAGNÓSTICO
    # ========================================================

    def resultado(self):

        return {

            "saude": self.horta.saude,

            "mensagem": self.horta.mensagem,

            "alertas": self.alertas.copy()

        }