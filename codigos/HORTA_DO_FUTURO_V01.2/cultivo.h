#ifndef CULTIVO_H
#define CULTIVO_H

#include <Arduino.h>
#include "config.h"
#include "dados.h"

Planta alface = {
    "ALFACE",
    "VEGETATIVO",
    5.5, 6.5,
    1.0, 1.8,
    18.0, 26.0,
    18.0, 26.0,
    50.0, 80.0,
    18,
    6, 0,
    15, 45
};

Planta manjericao = {
    "MANJERICAO",
    "VEGETATIVO",
    5.5, 6.5,
    1.0, 1.6,
    20.0, 30.0,
    18.0, 26.0,
    50.0, 80.0,
    16,
    6, 0,
    15, 45
};

void carregarAlface() {
    cultivoAtual = alface;
}

void carregarManjericao() {
    cultivoAtual = manjericao;
}

void alternarCultivoPadrao() {
    if (cultivoAtual.nome.indexOf("ALFACE") >= 0 || cultivoAtual.nome.indexOf("Alface") >= 0) {
        carregarManjericao();
    } else {
        carregarAlface();
    }
}

void iniciarCultivo() {
    carregarAlface();
    Serial.println("Cultivo selecionado: ALFACE");
}

#endif
