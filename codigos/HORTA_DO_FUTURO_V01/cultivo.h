#ifndef CULTIVO_H
#define CULTIVO_H

#include <Arduino.h>
#include "dados.h"


//=================================================
// ALFACE
//=================================================

Planta alface =
{
    "Alface",

    5.5,
    6.5,

    1.0,
    1.8,

    18.0,
    26.0,

    50.0,
    80.0,

    16
};


//=================================================
// MANJERICÃO
//=================================================

Planta manjericao =
{
    "Manjericao",

    5.5,
    6.8,

    1.2,
    2.0,

    20.0,
    30.0,

    50.0,
    80.0,

    14
};


//=================================================
// CARREGAR ALFACE
//=================================================

void carregarAlface()
{
    cultivoAtual = alface;
}


//=================================================
// CARREGAR MANJERICÃO
//=================================================

void carregarManjericao()
{
    cultivoAtual = manjericao;
}


//=================================================
// INICIALIZAÇÃO
//=================================================

void iniciarCultivo()
{
    carregarAlface();

    Serial.println("Cultivo selecionado: ALFACE");
}


#endif