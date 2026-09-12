#ifndef SENSOR_NIVEL_H
#define SENSOR_NIVEL_H

#include "config.h"
#include "dados.h"

void iniciarSensorNivel() {
    pinMode(PINO_NIVEL, INPUT_PULLUP);
    Serial.println("Sensor de nivel (Boia) preparado.");
}

void lerNivel() {
    // Lê o estado da boia física
    int estado = digitalRead(PINO_NIVEL);
    
    // Se a boia estiver ativada, o nível está OK
    if(estado == LOW) {
        solucao.nivelOK = true;
    } else {
        solucao.nivelOK = false;
    }
}

#endif