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
    pinMode(RELE_BOMBA_AGUA, OUTPUT);
    pinMode(RELE_BOMBA_AR, OUTPUT);

    // Relés Low-Trigger iniciam desligados (HIGH)
    digitalWrite(RELE_LUZ, HIGH);
    digitalWrite(RELE_VENTILADOR, HIGH);
    digitalWrite(RELE_BOMBA_AGUA, HIGH);
    digitalWrite(RELE_BOMBA_AR, HIGH);

    atuadores.luz = false;
    atuadores.ventilador = false;
    atuadores.aeracao = false;
    atuadores.bombaAgua = false;

    Serial.println("Automacao e reles inicializados.");
}

void controlarIluminacao() {
    bool ligar = false;
    if (modoLuz == 0) {
        ligar = luzLigada();
    } else if (modoLuz == 1) {
        ligar = true;
    } else if (modoLuz == 2) {
        ligar = false;
    }
    atuadores.luz = ligar;
    digitalWrite(RELE_LUZ, ligar ? LOW : HIGH);
}

void controlarVentilacao() {
    bool ligar = false;
    if (modoExaustor == 0) {
        if (ambiente.temperaturaAr > cultivoAtual.temperaturaMax) ligar = true;
        if (ambiente.umidadeAr > cultivoAtual.umidadeMax) ligar = true;
    } else if (modoExaustor == 1) {
        ligar = true;
    } else if (modoExaustor == 2) {
        ligar = false;
    }
    atuadores.ventilador = ligar;
    digitalWrite(RELE_VENTILADOR, ligar ? LOW : HIGH);
}

void controlarBombas() {
    bool nivelCritico = !solucao.nivelOK;
    bool statusAr = !nivelCritico;

    unsigned long onMs = (unsigned long)max(1, cultivoAtual.bombaOnMin) * 60000UL;
    unsigned long offMs = (unsigned long)max(0, cultivoAtual.bombaOffMin) * 60000UL;
    unsigned long cicloTotalMs = onMs + offMs;
    if (cicloTotalMs == 0) cicloTotalMs = 3600000UL;

    unsigned long tempoNoCiclo = millis() % cicloTotalMs;
    bool statusAgua = false;

    if (nivelCritico) {
        // Proteção contra queima a seco: desliga bomba submersa se nível crítico
        statusAgua = false;
    } else if (modoBombaAgua == 0) {
        statusAgua = (tempoNoCiclo < onMs);
    } else if (modoBombaAgua == 1) {
        statusAgua = true;
    } else if (modoBombaAgua == 2) {
        statusAgua = false;
    }

    atuadores.aeracao = statusAr;
    atuadores.bombaAgua = statusAgua;

    digitalWrite(RELE_BOMBA_AR, statusAr ? LOW : HIGH);
    digitalWrite(RELE_BOMBA_AGUA, statusAgua ? LOW : HIGH);
}

void atualizarAutomacao() {
    controlarIluminacao();
    controlarVentilacao();
    controlarBombas();
}

#endif
