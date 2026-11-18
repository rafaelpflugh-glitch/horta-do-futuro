#ifndef SENSOR_EC_H
#define SENSOR_EC_H

#include "config.h"
#include "dados.h"

void iniciarSensorEC() {
    pinMode(PINO_EC, INPUT);
    Serial.println("Sensor EC preparado.");
}

void lerEC() {
#if SENSOR_EC_REAL_ATIVO
    long soma = 0;
    for (int i = 0; i < 10; i++) {
        soma += analogRead(PINO_EC);
        delayMicroseconds(200);
    }
    float leituraMedia = soma / 10.0;
    float voltagem = leituraMedia * (3.3 / 4095.0);

    // Compensação térmica padrão (referência 25°C)
    float tempAgua = (solucao.temperaturaAgua > 5.0 && solucao.temperaturaAgua < 50.0) ? solucao.temperaturaAgua : 25.0;
    float coefTemp = 1.0 + 0.02 * (tempAgua - 25.0);
    if (coefTemp <= 0.2) coefTemp = 1.0;

    // Conversão de tensão para mS/cm (ajustável pelo fatorEC na tela ou no Gêmeo Digital)
    float ecBruto = (voltagem / coefTemp) * 1.35;
#else
    float ecBruto = 1.4;
#endif

    float ecFinal = ecBruto * fatorEC;
    if (ecFinal < 0.0) ecFinal = 0.0;
    if (ecFinal > 10.0) ecFinal = 10.0;
    solucao.ec = ecFinal;
}

#endif
