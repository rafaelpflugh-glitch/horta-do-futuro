#ifndef BOTOES_H
#define BOTOES_H

/*
=================================================

        HORTA DO FUTURO

        BOTOES

=================================================
*/

#include <Arduino.h>
#include "config.h"


//=================================================
// INICIALIZAÇÃO
//=================================================

void iniciarBotoes()
{

    pinMode(BTN_UP, INPUT_PULLUP);

    pinMode(BTN_DOWN, INPUT_PULLUP);

    pinMode(BTN_OK, INPUT_PULLUP);

    Serial.println("Botoes inicializados.");

}



//=================================================
// LEITURA
//=================================================

bool botaoCima()
{

    return digitalRead(BTN_UP) == LOW;

}


bool botaoBaixo()
{

    return digitalRead(BTN_DOWN) == LOW;

}


bool botaoOK()
{

    return digitalRead(BTN_OK) == LOW;

}


#endif