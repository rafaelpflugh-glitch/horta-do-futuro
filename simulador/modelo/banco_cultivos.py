"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN

BANCO DE CULTIVOS PADRÃO
============================================================
"""

from modelo.configuracao import ConfiguracaoCultivo


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


def listar_culturas():
    return list(CULTURAS_PADRAO.keys())


def obter_configuracao_cultura(nome):
    if not nome:
        raise ValueError("O nome da cultura não pode ser vazio.")
    
    nome = str(nome).strip().upper()
    if nome not in CULTURAS_PADRAO:
        raise ValueError(f"Cultura padrão '{nome}' não encontrada.")
    
    configuracao = CULTURAS_PADRAO[nome]
    return ConfiguracaoCultivo(**configuracao.snapshot())


# Alias de compatibilidade caso alguma parte chame 'obter_cultura'
def obter_cultura(nome):
    return obter_configuracao_cultura(nome)