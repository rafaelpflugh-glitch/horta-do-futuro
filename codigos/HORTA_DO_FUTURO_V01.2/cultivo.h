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

Planta rucula = {
    "RUCULA",
    "VEGETATIVO",
    6.0, 6.8,
    0.8, 1.4,
    16.0, 24.0,
    18.0, 24.0,
    50.0, 75.0,
    16,
    6, 0,
    15, 45
};

Planta morango = {
    "MORANGO",
    "FLORACAO",
    5.5, 6.2,
    1.2, 2.0,
    16.0, 25.0,
    18.0, 23.0,
    55.0, 75.0,
    14,
    6, 0,
    15, 45
};

void carregarAlface() {
    cultivoAtual = alface;
}

void carregarManjericao() {
    cultivoAtual = manjericao;
}

void carregarRucula() {
    cultivoAtual = rucula;
}

void carregarMorango() {
    cultivoAtual = morango;
}

bool carregarCultivoPorNome(const String& nome) {
    String n = nome;
    n.toUpperCase();
    if (n.indexOf("ALFACE") >= 0) { carregarAlface(); return true; }
    if (n.indexOf("MANJERIC") >= 0) { carregarManjericao(); return true; }
    if (n.indexOf("RUCUL") >= 0) { carregarRucula(); return true; }
    if (n.indexOf("MORANG") >= 0) { carregarMorango(); return true; }
    return false;
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
