#ifndef AUTOMACAO_H
#define AUTOMACAO_H

#include <Arduino.h>
#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"

//=================================================
// INICIALIZAÇÃO DOS ATUADORES
//=================================================
void iniciarAutomacao() {
    pinMode(RELE_LUZ, OUTPUT);
    pinMode(RELE_VENTILADOR, OUTPUT);
    pinMode(RELE_BOMBA, OUTPUT);

    // Estado inicial seguro (Desligado)
    digitalWrite(RELE_LUZ, LOW);
    digitalWrite(RELE_VENTILADOR, LOW);
    digitalWrite(RELE_BOMBA, LOW);

    atuadores.luz = false;
    atuadores.ventilador = false;
    atuadores.aeracao = false;

    Serial.println("Automacao e relés inicializados.");
}

//=================================================
// CONTROLE DE ILUMINAÇÃO (Fotoperíodo)
//=================================================
void controlarIluminacao() {
    bool ligar = luzLigada();
    atuadores.luz = ligar;
    digitalWrite(RELE_LUZ, ligar ? HIGH : LOW);
}

//=================================================
// CONTROLE DE VENTILAÇÃO (Ar)
//=================================================
void controlarVentilacao() {
    bool ligar = false;

    if (ambiente.temperaturaAr > cultivoAtual.temperaturaMax) {
        ligar = true;
    }
    if (ambiente.umidadeAr > cultivoAtual.umidadeMax) {
        ligar = true;
    }

    atuadores.ventilador = ligar;
    digitalWrite(RELE_VENTILADOR, ligar ? HIGH : LOW);
}

//=================================================
// CONTROLE DE AERAÇÃO DWC (Oxigenação Crítica)
//=================================================
void controlarAeracao() {
    // Na V1, a aeração opera de forma contínua desde que o nível d'água esteja OK
    bool ligar = solucao.nivelOK;

    atuadores.aeracao = ligar;
    digitalWrite(RELE_BOMBA, ligar ? HIGH : LOW);
}

//=================================================
// CICLO COMPLETO DE AUTOMAÇÃO
//=================================================
void atualizarAutomacao() {
    controlarIluminacao();
    controlarVentilacao();
    controlarAeracao();
}

#endif