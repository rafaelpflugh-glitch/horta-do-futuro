#ifndef ESTADOS_H
#define ESTADOS_H


enum EstadoSistema
{
    INICIALIZACAO,

    MONITORAMENTO,

    MENU_PRINCIPAL,

    MENU_CULTIVOS,

    MENU_CONFIGURACOES,

    MENU_HISTORICO,

    MENU_SISTEMA
};


extern EstadoSistema estadoAtual;


void atualizarEstado();


#endif