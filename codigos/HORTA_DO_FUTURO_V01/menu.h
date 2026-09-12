#ifndef MENU_H
#define MENU_H

#include <Arduino.h>

#include "estados.h"

#include "display.h"

#include "botoes.h"


//=================================================
// MENU
//=================================================

int opcaoMenu = 0;

const int totalOpcoes = 5;


String opcoesMenu[] =
{
    "Monitoramento",
    "Cultivos",
    "Configuracoes",
    "Historico",
    "Sistema"
};


//=================================================
// MOSTRA MENU
//=================================================

void mostrarMenu()
{
    tela.clearDisplay();

    tela.setTextSize(1);

    tela.setCursor(0, 0);

    tela.println("MENU PRINCIPAL");


    for(
        int i = 0;
        i < totalOpcoes;
        i++
    )
    {
        tela.setCursor(
            0,
            14 + (i * 10)
        );


        if(i == opcaoMenu)
            tela.print("> ");
        else
            tela.print("  ");


        tela.println(
            opcoesMenu[i]
        );
    }


    tela.display();
}


//=================================================
// CIMA
//=================================================

void menuCima()
{
    opcaoMenu--;


    if(opcaoMenu < 0)
        opcaoMenu =
            totalOpcoes - 1;
}


//=================================================
// BAIXO
//=================================================

void menuBaixo()
{
    opcaoMenu++;


    if(
        opcaoMenu >= totalOpcoes
    )
    {
        opcaoMenu = 0;
    }
}


//=================================================
// SELECIONAR
//=================================================

void selecionarMenu()
{
    switch(opcaoMenu)
    {
        case 0:
            estadoAtual =
                MONITORAMENTO;
            break;

        case 1:
            estadoAtual =
                MENU_CULTIVOS;
            break;

        case 2:
            estadoAtual =
                MENU_CONFIGURACOES;
            break;

        case 3:
            estadoAtual =
                MENU_HISTORICO;
            break;

        case 4:
            estadoAtual =
                MENU_SISTEMA;
            break;
    }
}


//=================================================
// VOLTAR
//=================================================

void voltarMenu()
{
    estadoAtual =
        MENU_PRINCIPAL;
}


//=================================================
// ATUALIZAÇÃO
//=================================================

void atualizarMenu()
{
    /*
        Por enquanto a interface
        principal utiliza as telas.

        Os botões serão integrados
        progressivamente.
    */
}


#endif