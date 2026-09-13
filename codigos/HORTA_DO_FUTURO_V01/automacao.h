#ifndef AUTOMACAO_H
#define AUTOMACAO_H

#include <Arduino.h>
#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"

void iniciarAutomacao() {
    pinMode(RELE_LUZ, OUTPUT);
    pinMode(RELE_VENTILADOR, OUTPUT);
    pinMode(RELE_BOMBA, OUTPUT);

    digitalWrite(RELE_LUZ, LOW);
    digitalWrite(RELE_VENTILADOR, LOW);
    digitalWrite(RELE_BOMBA, LOW);

    atuadores.luz = false;
    atuadores.ventilador = false;
    atuadores.aeracao = false;

    Serial.println("Automacao e reles inicializados.");
}

void controlarIluminacao() {
    bool ligar = false;
    
    if (modoLuz == 0) {
        ligar = luzLigada(); // Segue o relógio
    } else if (modoLuz == 1) {
        ligar = true;        // Força ligado
    } else if (modoLuz == 2) {
        ligar = false;       // Força desligado
    }

    atuadores.luz = ligar;
    digitalWrite(RELE_LUZ, ligar ? HIGH : LOW);
}

void controlarVentilacao() {
    bool ligar = false;
    if (ambiente.temperaturaAr > cultivoAtual.temperaturaMax) ligar = true;
    if (ambiente.umidadeAr > cultivoAtual.umidadeMax) ligar = true;

    atuadores.ventilador = ligar;
    digitalWrite(RELE_VENTILADOR, ligar ? HIGH : LOW);
}

void controlarAeracao() {
    bool ligar = solucao.nivelOK;
    atuadores.aeracao = ligar;
    digitalWrite(RELE_BOMBA, ligar ? HIGH : LOW);
}

void atualizarAutomacao() {
    controlarIluminacao();
    controlarVentilacao();
    controlarAeracao();
}

#endif