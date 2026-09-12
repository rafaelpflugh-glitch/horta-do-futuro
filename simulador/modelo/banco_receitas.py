"""
============================================================
HORTA DO FUTURO
BANCO DE RECEITAS NUTRITIVAS
============================================================

Catálogo central das receitas nutritivas utilizadas pelo
Digital Twin.

Responsabilidades:

    - cadastrar receitas;
    - localizar receitas;
    - listar receitas;
    - remover receitas;
    - filtrar por fase;
    - gerar snapshot.

IMPORTANTE:

Este módulo NÃO executa dosagem.

Ele apenas armazena receitas.

Fluxo:

    PRODUTO
       ↓
    RECEITA
       ↓
    BANCO DE RECEITAS
       ↓
    SISTEMA DE DOSAGEM

============================================================
"""

from modelo.receita_nutritiva import ReceitaNutritiva


class BancoReceitas:

    # ======================================================
    # CONSTRUTOR
    # ======================================================

    def __init__(self):

        self.receitas = {}

    # ======================================================
    # NORMALIZAR NOME
    # ======================================================

    @staticmethod
    def _normalizar_nome(nome):

        nome = str(
            nome
        ).strip().upper()

        if not nome:

            raise ValueError(
                "O nome da receita não pode ser vazio."
            )

        return nome

    # ======================================================
    # CADASTRAR
    # ======================================================

    def cadastrar(
        self,
        receita
    ):

        if not isinstance(
            receita,
            ReceitaNutritiva
        ):

            raise TypeError(
                "O cadastro deve receber uma "
                "ReceitaNutritiva."
            )

        nome = self._normalizar_nome(
            receita.nome
        )

        if nome in self.receitas:

            raise ValueError(
                f"Já existe uma receita cadastrada "
                f"com o nome: {nome}"
            )

        self.receitas[
            nome
        ] = receita

        return receita

    # ======================================================
    # CADASTRAR OU SUBSTITUIR
    # ======================================================

    def cadastrar_ou_substituir(
        self,
        receita
    ):

        if not isinstance(
            receita,
            ReceitaNutritiva
        ):

            raise TypeError(
                "O cadastro deve receber uma "
                "ReceitaNutritiva."
            )

        nome = self._normalizar_nome(
            receita.nome
        )

        self.receitas[
            nome
        ] = receita

        return receita

    # ======================================================
    # OBTER
    # ======================================================

    def obter(
        self,
        nome
    ):

        nome = self._normalizar_nome(
            nome
        )

        if nome not in self.receitas:

            raise KeyError(
                f"Receita não encontrada: {nome}"
            )

        return self.receitas[
            nome
        ]

    # ======================================================
    # EXISTE
    # ======================================================

    def existe(
        self,
        nome
    ):

        nome = self._normalizar_nome(
            nome
        )

        return nome in self.receitas

    # ======================================================
    # REMOVER
    # ======================================================

    def remover(
        self,
        nome
    ):

        nome = self._normalizar_nome(
            nome
        )

        if nome not in self.receitas:

            raise KeyError(
                f"Receita não encontrada: {nome}"
            )

        return self.receitas.pop(
            nome
        )

    # ======================================================
    # LISTAR
    # ======================================================

    def listar(self):

        return list(
            self.receitas.values()
        )

    # ======================================================
    # LISTAR NOMES
    # ======================================================

    def listar_nomes(self):

        return list(
            self.receitas.keys()
        )

    # ======================================================
    # FILTRAR POR FASE
    # ======================================================

    def por_fase(
        self,
        fase
    ):

        fase = (
            str(fase)
            .strip()
            .upper()
        )

        return [

            receita

            for receita
            in self.receitas.values()

            if receita.fase == fase
        ]

    # ======================================================
    # CONTAGEM
    # ======================================================

    def quantidade(self):

        return len(
            self.receitas
        )

    # ======================================================
    # LIMPAR
    # ======================================================

    def limpar(self):

        self.receitas.clear()

    # ======================================================
    # SNAPSHOT
    # ======================================================

    def snapshot(self):

        return {

            nome:
                receita.snapshot()

            for nome, receita
            in self.receitas.items()
        }

    # ======================================================
    # REPRESENTAÇÃO
    # ======================================================

    def __repr__(self):

        return (
            "BancoReceitas("
            f"receitas={self.quantidade()}"
            ")"
        )