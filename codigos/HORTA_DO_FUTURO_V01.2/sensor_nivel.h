#ifndef SENSOR_NIVEL_H
#define SENSOR_NIVEL_H

#include "config.h"
#include "dados.h"

void iniciarSensorNivel() {
    pinMode(PINO_NIVEL, INPUT_PULLUP);
    Serial.println("Sensor de nivel (Boia) preparado.");
}

void lerNivel() {
    int estado = digitalRead(PINO_NIVEL);
    if(estado == LOW) {
        solucao.nivelOK = true;
        solucao.nivelPercentual = 100.0;
    } else {
        solucao.nivelOK = false;
        solucao.nivelPercentual = 0.0;
    }
}

#endif
