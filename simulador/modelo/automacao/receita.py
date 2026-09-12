"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

RECEITAS NUTRITIVAS

Define quais produtos participam da correção
de cada cultivo.

IMPORTANTE:
Os valores de dosagem são parâmetros de simulação.
Não representam ainda uma recomendação agrícola real.
============================================================
"""


class ReceitaNutritiva:

    def __init__(
        self,
        nome="ALFACE_DWC",
        ec_min=1.0,
        ec_alvo=1.4,
        ec_max=1.8
    ):

        self.nome = nome

        self.ec_min = float(ec_min)
        self.ec_alvo = float(ec_alvo)
        self.ec_max = float(ec_max)

        # Produtos que compõem a solução nutritiva.
        #
        # A proporção real será definida posteriormente
        # de acordo com o fertilizante escolhido.
        self.produtos = {
            "NUTRIENTE_A": {
                "nome": "Nutriente A",
                "ativo": True,
                "ordem": 1
            },

            "NUTRIENTE_B": {
                "nome": "Nutriente B",
                "ativo": True,
                "ordem": 2
            }
        }

    # ======================================================
    # PRODUTOS ATIVOS
    # ======================================================

    def produtos_ativos(self):

        return [
            produto
            for produto, dados in sorted(
                self.produtos.items(),
                key=lambda item: item[1]["ordem"]
            )
            if dados["ativo"]
        ]

    # ======================================================
    # PRIMEIRO PRODUTO
    # ======================================================

    def primeiro_produto(self):

        ativos = self.produtos_ativos()

        if not ativos:
            return None

        return ativos[0]

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {
            "nome": self.nome,

            "ec": {
                "minimo": self.ec_min,
                "alvo": self.ec_alvo,
                "maximo": self.ec_max
            },

            "produtos": self.produtos,

            "produtos_ativos":
                self.produtos_ativos()
        }