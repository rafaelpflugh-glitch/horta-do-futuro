#include "estados.h"



EstadoSistema estadoAtual = INICIALIZACAO;



void atualizarEstado()
{

    switch(estadoAtual)
    {


        case INICIALIZACAO:

            estadoAtual = MONITORAMENTO;

        break;



        case MONITORAMENTO:

        break;



        default:

        break;


    }

}