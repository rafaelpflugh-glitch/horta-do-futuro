"""
============================================================
HORTA DO FUTURO
CULTIVO

Representa uma cultura individual dentro da estufa.

A ideia é separar:

    HORTA
        ↓
    CULTIVO
        ↓
    CONFIGURAÇÃO DA CULTURA

Hoje temos apenas um cultivo.

No futuro poderemos ter:

    Estufa
        ├── Alface
        ├── Manjericão
        └── Outra cultura

sem precisar reescrever o motor principal.
============================================================
"""


class Cultivo:

    def __init__(
        self,
        nome="ALFACE",
        variedade="PADRÃO",
        identificacao="CULTIVO-01"
    ):

        # ==================================================
        # IDENTIFICAÇÃO
        # ==================================================

        self.id = identificacao

        self.nome = nome

        self.variedade = variedade


        # ==================================================
        # FASE
        # ==================================================

        self.fase = "VEGETATIVO"


        # ==================================================
        # ESTADO
        # ==================================================

        self.ativo = True


    # ======================================================
    # ALTERAÇÃO
    # ======================================================

    def renomear(
        self,
        nome
    ):

        nome = str(nome).strip()

        if nome:

            self.nome = nome.upper()


    def definir_variedade(
        self,
        variedade
    ):

        variedade = str(variedade).strip()

        if variedade:

            self.variedade = variedade.upper()


    def definir_fase(
        self,
        fase
    ):

        fase = str(fase).strip()

        if fase:

            self.fase = fase.upper()


    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            "id": self.id,

            "nome": self.nome,

            "variedade": self.variedade,

            "fase": self.fase,

            "ativo": self.ativo

        }