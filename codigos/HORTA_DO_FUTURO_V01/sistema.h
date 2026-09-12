#ifndef SISTEMA_H
#define SISTEMA_H


#include <Arduino.h>


#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"
#include "fotoperiodo.h"
#include "sensores.h"
#include "diagnostico.h"
#include "automacao.h"
#include "botoes.h"
#include "estados.h"
#include "memoria_sd.h"
#include "display.h"
#include "menu.h"


//=================================================
// INICIALIZAÇÃO
//=================================================

void iniciarSistema()
{
    Serial.println();
    Serial.println("=================================");
    Serial.println("       HORTA DO FUTURO");
    Serial.println("       INICIALIZANDO...");
    Serial.println("=================================");


    //=============================================
    // CULTIVO
    //=============================================

    iniciarCultivo();


    //=============================================
    // RTC
    //=============================================

    iniciarRTC();


    //=============================================
    // FOTOPERÍODO
    //=============================================

    configurarFotoperiodo();


    //=============================================
    // SENSORES
    //=============================================

    iniciarSensores();


    //=============================================
    // BOTÕES
    //=============================================

    iniciarBotoes();


    //=============================================
    // DIAGNÓSTICO
    //=============================================

    iniciarDiagnostico();


    //=============================================
    // AUTOMAÇÃO
    //=============================================

    iniciarAutomacao();


    //=============================================
    // MEMÓRIA
    //=============================================

    iniciarMemoria();


    //=============================================
    // ESTADO
    //=============================================

    estadoAtual = INICIALIZACAO;


    Serial.println();
    Serial.println("=================================");
    Serial.println("       SISTEMA INICIALIZADO");
    Serial.println("=================================");
    Serial.println();
}


//=================================================
// CICLO PRINCIPAL
//=================================================

void executarCiclo()
{
    Serial.println();
    Serial.println("=================================");
    Serial.println("     NOVO CICLO DE MONITORAMENTO");
    Serial.println("=================================");


    //=============================================
    // 1. LEITURA
    //=============================================

    atualizarSensores();


    //=============================================
    // 2. DIAGNÓSTICO
    //=============================================

    atualizarDiagnostico();


    //=============================================
    // 3. AUTOMAÇÃO
    //=============================================

    atualizarAutomacao();


    //=============================================
    // 4. MEMÓRIA
    //=============================================

    registrarDados();


    //=============================================
    // 5. DEBUG
    //=============================================

    mostrarDadosSensores();


    Serial.print("Saude do cultivo: ");
    Serial.print(saudeCultivo);
    Serial.println("%");


    Serial.println("=================================");
}


//=================================================
// INTERFACE
//=================================================

void atualizarInterface()
{
    switch(estadoAtual)
    {

        case INICIALIZACAO:

            mostrarInicializacao();

            estadoAtual = MONITORAMENTO;

            break;


        case MONITORAMENTO:

            atualizarDisplay();

            break;


        case MENU_PRINCIPAL:

            mostrarMenu();

            break;


        default:

            atualizarDisplay();

            break;
    }
}


#endif