#ifndef MEMORIA_SD_H
#define MEMORIA_SD_H

#include <Arduino.h>

#include "config.h"
#include "dados.h"


//=================================================
// INICIALIZAÇÃO
//=================================================

void iniciarMemoria()
{
    /*
        FUTURO:

        SD.begin(SD_CS)
    */

    Serial.println("Memoria SD preparada.");
}


//=================================================
// REGISTRO
//=================================================

void registrarDados()
{
    /*
        FUTURO:

        CSV:

        data
        hora
        temperatura_ar
        umidade_ar
        temperatura_agua
        ph
        ec
        nivel
        saude
    */

    Serial.println("Dados registrados.");
}


#endif