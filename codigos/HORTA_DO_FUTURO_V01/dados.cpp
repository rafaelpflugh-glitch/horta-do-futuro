#include <Arduino.h>

#include "config.h"
#include "dados.h"


//=================================================
// CULTIVO ATUAL
//=================================================

Planta cultivoAtual =
{
    "Alface",

    PH_MIN_PADRAO,
    PH_MAX_PADRAO,

    EC_MIN_PADRAO,
    EC_MAX_PADRAO,

    TEMPERATURA_MIN_PADRAO,
    TEMPERATURA_MAX_PADRAO,

    UMIDADE_MIN_PADRAO,
    UMIDADE_MAX_PADRAO,

    HORAS_LUZ_PADRAO
};


//=================================================
// AMBIENTE
//=================================================

Ambiente ambiente =
{
    0.0,
    0.0
};


//=================================================
// SOLUÇÃO
//=================================================

Solucao solucao =
{
    0.0,
    0.0,
    0.0,
    false
};


//=================================================
// ALERTAS
//=================================================

Alertas alertas =
{
    false,
    false,

    false,
    false,

    false,
    false,

    false,
    false,

    false
};


//=================================================
// ATUADORES
//=================================================

Atuadores atuadores =
{
    false,
    false,
    false
};


//=================================================
// MENSAGEM DO SISTEMA
//=================================================

String mensagemSistema = "Sistema OK";


//=================================================
// SAÚDE DO CULTIVO
//=================================================

int saudeCultivo = 0;