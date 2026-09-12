#ifndef RTC_H
#define RTC_H

#include <Arduino.h>

#include "config.h"
#include "cultivo.h"


//=================================================
// DATA E HORA
//=================================================

int horaAtual = 12;
int minutoAtual = 0;
int segundoAtual = 0;

int diaAtual = 1;
int mesAtual = 1;
int anoAtual = 2026;


//=================================================
// INICIALIZAÇÃO
//=================================================

void iniciarRTC()
{
    Serial.println("RTC inicializado.");
}


//=================================================
// ATUALIZA RTC
//=================================================

void atualizarRTC()
{
    /*
        FUTURO:

        DS3231
    */
}


//=================================================
// OBTÉM HORA
//=================================================

String obterHora()
{
    char texto[9];

    sprintf(
        texto,
        "%02d:%02d:%02d",
        horaAtual,
        minutoAtual,
        segundoAtual
    );

    return String(texto);
}


//=================================================
// OBTÉM DATA
//=================================================

String obterData()
{
    char texto[11];

    sprintf(
        texto,
        "%02d/%02d/%04d",
        diaAtual,
        mesAtual,
        anoAtual
    );

    return String(texto);
}


//=================================================
// FOTOPERÍODO
//=================================================

bool luzLigada()
{
    int horaLiga = HORA_INICIO_LUZ;

    int horaDesliga =
        horaLiga + cultivoAtual.horasLuz;

    if(horaDesliga < 24)
    {
        return
        (
            horaAtual >= horaLiga &&
            horaAtual < horaDesliga
        );
    }

    return
    (
        horaAtual >= horaLiga ||
        horaAtual < (horaDesliga - 24)
    );
}


#endif