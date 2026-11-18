#ifndef SENSOR_PH_H
#define SENSOR_PH_H

#include "config.h"
#include "dados.h"

void iniciarSensorPH() {
    pinMode(PINO_PH, INPUT);
    Serial.println("Sensor de pH (PH-4502C) preparado.");
}

void lerPH() {
#if SENSOR_PH_REAL_ATIVO
    // Média móvel de 10 amostras para filtrar ruído do ADC do ESP32
    long soma = 0;
    for (int i = 0; i < 10; i++) {
        soma += analogRead(PINO_PH);
        delayMicroseconds(200);
    }
    float leituraMedia = soma / 10.0;
    float voltagem = leituraMedia * (3.3 / 4095.0);
    float valorBase = 7.0 + ((2.5 - voltagem) * 3.5);
#else
    float valorBase = 6.0;
#endif

    float phFinal = valorBase + offsetPH;
    if (phFinal < 0.0) phFinal = 0.0;
    if (phFinal > 14.0) phFinal = 14.0;
    solucao.ph = phFinal;
}

#endif
