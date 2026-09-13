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
#include "estados.h"
#include "memoria_sd.h"
#include "display.h"

void iniciarSistema() {
    Serial.println();
    Serial.println("=================================");
    Serial.println("       HORTA DO FUTURO");
    Serial.println("       INICIALIZANDO...");
    Serial.println("=================================");

    iniciarCultivo();
    iniciarRTC();
    configurarFotoperiodo();
    iniciarSensores();
    iniciarDiagnostico();
    iniciarAutomacao();
    iniciarMemoria();

    estadoAtual = INICIALIZACAO;

    Serial.println();
    Serial.println("=================================");
    Serial.println("       SISTEMA INICIALIZADO");
    Serial.println("=================================");
    Serial.println();
}

void executarCiclo() {
    Serial.println();
    Serial.println("=================================");
    Serial.println("     NOVO CICLO DE MONITORAMENTO");
    Serial.println("=================================");

    atualizarSensores();
    atualizarDiagnostico();
    enviarTelemetriaJSON();
    atualizarAutomacao();
    registrarDados();
    mostrarDadosSensores();

    // Exibe o status detalhado de saúde e múltiplos alertas ativos
    Serial.print("Saude do cultivo: ");
    Serial.print(saudeCultivo);
    Serial.println("%");
    
    Serial.println(obterMensagemAlertas());
    
    Serial.println("=================================");
}

void atualizarInterface() {
    switch(estadoAtual) {
        case INICIALIZACAO:
            mostrarInicializacao();
            estadoAtual = MONITORAMENTO;
            break;
        case MONITORAMENTO:
            atualizarDisplay(); // Lê o touch e renderiza a tela
            break;
        default:
            atualizarDisplay();
            break;
    }
}

#endif