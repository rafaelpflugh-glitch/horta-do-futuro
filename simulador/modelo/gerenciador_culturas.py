"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

GERENCIADOR DE CULTURAS
============================================================

Responsável por:

    - listar culturas padrão
    - listar culturas personalizadas
    - carregar cultura
    - criar nova cultura
    - salvar cultura
    - editar cultura
    - excluir cultura
    - persistir dados em JSON

As culturas padrão ficam em:

    modelo/banco_cultivos.py

As culturas criadas pelo usuário ficam em:

    dados/culturas.json

============================================================
"""

import json
from pathlib import Path

from modelo.configuracao import ConfiguracaoCultivo
from modelo.banco_cultivos import CULTURAS_PADRAO


class GerenciadorCulturas:

    # ========================================================
    # CAMINHOS
    # ========================================================

    DIRETORIO_DADOS = (
        Path(__file__).resolve().parent.parent
        / "dados"
    )

    ARQUIVO_CULTURAS = (
        DIRETORIO_DADOS
        / "culturas.json"
    )

    # ========================================================
    # ESTRUTURA
    # ========================================================

    @classmethod
    def _garantir_estrutura(cls):
        """
        Garante que a pasta de dados e o arquivo JSON existam.
        """

        cls.DIRETORIO_DADOS.mkdir(
            parents=True,
            exist_ok=True
        )

        if not cls.ARQUIVO_CULTURAS.exists():

            cls._salvar_json({})

    # ========================================================
    # LEITURA JSON
    # ========================================================

    @classmethod
    def _ler_json(cls):
        """
        Lê o arquivo de culturas personalizadas.

        Em caso de arquivo inválido ou corrompido,
        retorna um dicionário vazio.
        """

        cls._garantir_estrutura()

        try:

            with open(
                cls.ARQUIVO_CULTURAS,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(arquivo)

            if not isinstance(dados, dict):

                return {}

            return dados

        except (
            json.JSONDecodeError,
            OSError
        ):

            return {}

    # ========================================================
    # ESCRITA JSON
    # ========================================================

    @classmethod
    def _salvar_json(cls, dados):
        """
        Salva os dados de forma segura.

        Primeiro grava em arquivo temporário.
        Depois substitui o arquivo original.
        """

        cls.DIRETORIO_DADOS.mkdir(
            parents=True,
            exist_ok=True
        )

        arquivo_temporario = (
            cls.ARQUIVO_CULTURAS.with_suffix(".tmp")
        )

        with open(
            arquivo_temporario,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        arquivo_temporario.replace(
            cls.ARQUIVO_CULTURAS
        )

    # ========================================================
    # NORMALIZAR NOME
    # ========================================================

    @staticmethod
    def _normalizar_nome(nome):
        """
        Padroniza o nome interno da cultura.

        Exemplo:

            "tomate"
            " Tomate "
            "ToMaTe"

        tornam-se:

            "TOMATE"
        """

        if nome is None:

            raise ValueError(
                "O nome da cultura não pode ser vazio."
            )

        nome = str(nome).strip().upper()

        if not nome:

            raise ValueError(
                "O nome da cultura não pode ser vazio."
            )

        return nome

    # ========================================================
    # VALIDAR CONFIGURAÇÃO
    # ========================================================

    @staticmethod
    def _validar_configuracao(configuracao):

        if not isinstance(
            configuracao,
            ConfiguracaoCultivo
        ):

            raise TypeError(
                "A configuração deve ser "
                "uma ConfiguracaoCultivo."
            )

    # ========================================================
    # LISTAR TODAS
    # ========================================================

    @classmethod
    def listar(cls):
        """
        Retorna todas as culturas disponíveis.

        Inclui:

            - culturas padrão
            - culturas personalizadas
        """

        culturas = set(
            CULTURAS_PADRAO.keys()
        )

        dados = cls._ler_json()

        culturas.update(
            dados.keys()
        )

        return sorted(
            culturas
        )

    # ========================================================
    # LISTAR PADRÃO
    # ========================================================

    @classmethod
    def listar_padrao(cls):
        """
        Retorna somente as culturas fornecidas
        originalmente pelo sistema.
        """

        return sorted(
            CULTURAS_PADRAO.keys()
        )

    # ========================================================
    # LISTAR PERSONALIZADAS
    # ========================================================

    @classmethod
    def listar_personalizadas(cls):
        """
        Retorna somente as culturas criadas
        pelo usuário.
        """

        dados = cls._ler_json()

        return sorted(
            dados.keys()
        )

    # ========================================================
    # EXISTE
    # ========================================================

    @classmethod
    def existe(cls, nome):

        nome = cls._normalizar_nome(
            nome
        )

        return nome in cls.listar()

    # ========================================================
    # É PADRÃO?
    # ========================================================

    @classmethod
    def eh_padrao(cls, nome):

        nome = cls._normalizar_nome(
            nome
        )

        return nome in CULTURAS_PADRAO

    # ========================================================
    # É PERSONALIZADA?
    # ========================================================

    @classmethod
    def eh_personalizada(cls, nome):

        nome = cls._normalizar_nome(
            nome
        )

        dados = cls._ler_json()

        return nome in dados

    # ========================================================
    # CARREGAR
    # ========================================================

    @classmethod
    def carregar(cls, nome):
        """
        Carrega uma cultura.

        A cultura personalizada tem prioridade
        sobre a cultura padrão.
        """

        nome = cls._normalizar_nome(
            nome
        )

        # ----------------------------------------------------
        # PERSONALIZADA
        # ----------------------------------------------------

        dados = cls._ler_json()

        if nome in dados:

            configuracao = (
                ConfiguracaoCultivo(
                    **dados[nome]
                )
            )

            return configuracao

        # ----------------------------------------------------
        # PADRÃO
        # ----------------------------------------------------

        if nome in CULTURAS_PADRAO:

            original = (
                CULTURAS_PADRAO[nome]
            )

            return ConfiguracaoCultivo(
                **original.snapshot()
            )

        # ----------------------------------------------------
        # NÃO ENCONTRADA
        # ----------------------------------------------------

        raise ValueError(
            f"Cultura '{nome}' não encontrada."
        )

    # ========================================================
    # NOVA CULTURA
    # ========================================================

    @classmethod
    def nova(cls):
        """
        Cria uma nova configuração em memória.

        Ainda não salva no JSON.

        O painel poderá:

            NOVA CULTURA
                ↓
            editar campos
                ↓
              SALVAR
                ↓
          culturas.json
        """

        culturas = cls.listar()

        numero = 1

        while True:

            nome = (
                f"NOVA CULTURA {numero:02d}"
            )

            if nome not in culturas:

                break

            numero += 1

        return ConfiguracaoCultivo(

            nome=nome,

            nome_cultivo=(
                f"Novo Cultivo #{numero:02d}"
            ),

            fase="VEGETATIVO",

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
        )

    # ========================================================
    # SALVAR
    # ========================================================

    @classmethod
    def salvar(
        cls,
        configuracao
    ):
        """
        Salva uma nova cultura ou sobrescreve
        uma cultura personalizada existente.

        Culturas padrão também podem ser usadas
        como base, mas o registro salvo no JSON
        passa a ser personalizado.
        """

        cls._validar_configuracao(
            configuracao
        )

        nome = cls._normalizar_nome(
            configuracao.nome
        )

        configuracao.nome = nome

        dados = cls._ler_json()

        dados[nome] = (
            configuracao.snapshot()
        )

        cls._salvar_json(
            dados
        )

        return configuracao

    # ========================================================
    # ATUALIZAR
    # ========================================================

    @classmethod
    def atualizar(
        cls,
        nome_original,
        configuracao
    ):
        """
        Atualiza uma cultura personalizada.

        Permite também alterar seu nome.

        Exemplo:

            TOMATE

        para:

            TOMATE CEREJA
        """

        cls._validar_configuracao(
            configuracao
        )

        nome_original = (
            cls._normalizar_nome(
                nome_original
            )
        )

        novo_nome = cls._normalizar_nome(
            configuracao.nome
        )

        dados = cls._ler_json()

        # ----------------------------------------------------
        # CULTURA PADRÃO
        # ----------------------------------------------------

        if nome_original in CULTURAS_PADRAO:

            raise ValueError(
                f"A cultura padrão '{nome_original}' "
                "não pode ser editada diretamente."
            )

        # ----------------------------------------------------
        # CULTURA NÃO EXISTE
        # ----------------------------------------------------

        if nome_original not in dados:

            raise ValueError(
                f"Cultura personalizada "
                f"'{nome_original}' não encontrada."
            )

        # ----------------------------------------------------
        # NOVO NOME JÁ EXISTE
        # ----------------------------------------------------

        if (
            novo_nome != nome_original
            and novo_nome in cls.listar()
        ):

            raise ValueError(
                f"Já existe uma cultura chamada "
                f"'{novo_nome}'."
            )

        # ----------------------------------------------------
        # REMOVER ANTIGA
        # ----------------------------------------------------

        del dados[
            nome_original
        ]

        # ----------------------------------------------------
        # NORMALIZAR E SALVAR NOVA
        # ----------------------------------------------------

        configuracao.nome = novo_nome

        dados[
            novo_nome
        ] = configuracao.snapshot()

        cls._salvar_json(
            dados
        )

        return configuracao

    # ========================================================
    # EXCLUIR
    # ========================================================

    @classmethod
    def excluir(cls, nome):
        """
        Exclui uma cultura personalizada.

        Culturas padrão são protegidas.
        """

        nome = cls._normalizar_nome(
            nome
        )

        # ----------------------------------------------------
        # PROTEÇÃO PADRÃO
        # ----------------------------------------------------

        if nome in CULTURAS_PADRAO:

            raise ValueError(
                f"A cultura padrão '{nome}' "
                "não pode ser excluída."
            )

        dados = cls._ler_json()

        # ----------------------------------------------------
        # NÃO ENCONTRADA
        # ----------------------------------------------------

        if nome not in dados:

            raise ValueError(
                f"Cultura '{nome}' não encontrada."
            )

        # ----------------------------------------------------
        # EXCLUIR
        # ----------------------------------------------------

        del dados[
            nome
        ]

        cls._salvar_json(
            dados
        )

    # ========================================================
    # LIMPAR PERSONALIZADAS
    # ========================================================

    @classmethod
    def limpar_personalizadas(cls):
        """
        Remove todas as culturas personalizadas.

        As culturas padrão permanecem intactas.
        """

        cls._salvar_json({})

    # ========================================================
    # EXPORTAR TODAS
    # ========================================================

    @classmethod
    def exportar_todas(cls):
        """
        Retorna todas as culturas como dicionário.

        Útil futuramente para:

            - backup
            - exportação
            - API
            - ESP32
            - relatórios
            - sincronização
        """

        resultado = {}

        for nome in cls.listar():

            resultado[nome] = (
                cls.carregar(nome).snapshot()
            )

        return resultado