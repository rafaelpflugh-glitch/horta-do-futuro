#ifndef SIMULACAO_H
#define SIMULACAO_H

#include "config.h"
#include "dados.h"


//=================================================
// SIMULAÇÃO
//=================================================

void simularSensores()
{
#if MODO_SIMULACAO

    ambiente.temperaturaAr = 24.5;

    ambiente.umidadeAr = 62.0;

    solucao.temperaturaAgua = 22.3;

    solucao.ph = 6.1;

    solucao.ec = 1.4;

    solucao.nivelOK = true;

#endif
}


//=================================================
// VARIAÇÃO DA SIMULAÇÃO
//=================================================

void variarSimulacao()
{
#if MODO_SIMULACAO

    /*
        Pequena variação para permitir
        testar o sistema futuramente.
    */

#endif
}


#endif