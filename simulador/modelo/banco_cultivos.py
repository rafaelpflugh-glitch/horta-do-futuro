"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

BANCO DE CULTIVOS PADRÃO
============================================================

Este módulo contém apenas as culturas que vêm originalmente
com o sistema.

IMPORTANTE:

Este arquivo NÃO é responsável pela persistência das culturas
criadas pelo usuário.

Culturas personalizadas são administradas pelo:

    modelo.gerenciador_culturas

e armazenadas em:

    dados/culturas.json

============================================================
"""

from modelo.configuracao import ConfiguracaoCultivo


# ============================================================
# CULTURAS PADRÃO
# ============================================================

CULTURAS_PADRAO = {

    "ALFACE": ConfiguracaoCultivo(
        nome="ALFACE",
        nome_cultivo="Alface Experimental #01",
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
    ),

    "MANJERICÃO": ConfiguracaoCultivo(
        nome="MANJERICÃO",
        nome_cultivo="Manjericão Experimental #01",
        fase="VEGETATIVO",

        ph_min=5.5,
        ph_max=6.5,

        ec_min=1.0,
        ec_max=1.6,

        temperatura_ar_min=20.0,
        temperatura_ar_max=30.0,

        temperatura_agua_min=18.0,
        temperatura_agua_max=26.0,

        umidade_ar_min=50.0,
        umidade_ar_max=80.0,

        fotoperiodo_horas=16.0,

        inicio_luz_hora=6,
        inicio_luz_minuto=0
    )
}


# ============================================================
# LISTAR CULTURAS PADRÃO
# ============================================================

def listar_culturas():

    return list(
        CULTURAS_PADRAO.keys()
    )


# ============================================================
# OBTER CONFIGURAÇÃO DE CULTURA PADRÃO
# ============================================================

def obter_configuracao_cultura(nome):

    if not nome:
        raise ValueError(
            "O nome da cultura não pode ser vazio."
        )

    nome = str(nome).strip().upper()

    if nome not in CULTURAS_PADRAO:

        raise ValueError(
            f"Cultura padrão '{nome}' não encontrada."
        )

    configuracao = CULTURAS_PADRAO[nome]

    # Retorna uma cópia para impedir que o banco original
    # seja alterado acidentalmente.

    return ConfiguracaoCultivo(
        **configuracao.snapshot()
    )