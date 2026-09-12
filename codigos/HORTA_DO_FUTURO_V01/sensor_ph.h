#ifndef SENSOR_PH_H
#define SENSOR_PH_H

#include "config.h"
#include "dados.h"

void iniciarSensorPH() {
    pinMode(PINO_PH, INPUT);
    Serial.println("Sensor de pH (PH-4502C) preparado.");
}

void lerPH() {
    int leituraAnaloga = analogRead(PINO_PH);
    
    // Converte a leitura do ESP32 (0-4095) para Voltagem (0-3.3V)
    float voltagem = leituraAnaloga * (3.3 / 4095.0);
    
    // Equação linear genérica (precisará de calibração com solução buffer)
    float valorCalculado = 7.0 + ((2.5 - voltagem) * 3.5); 
    
    solucao.ph = valorCalculado;
}

#endif