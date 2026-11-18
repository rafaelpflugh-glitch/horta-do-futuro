#ifndef SENSORES_H
#define SENSORES_H

#include <Arduino.h>
#include "config.h"
#include "dados.h"
#include "sensor_temperatura.h"
#include "sensor_ph.h"
#include "sensor_nivel.h"
#include "sensor_ec.h"

void iniciarSensores() {
    Serial.println("Inicializando varredura de sensores reais...");
    iniciarSensoresTemperatura();
    iniciarSensorPH();
    iniciarSensorNivel();
    iniciarSensorEC();
    Serial.println("Sensores de telemetria inicializados com sucesso.");
}

void atualizarSensores() {
    lerTemperatura();
    lerPH();
    lerNivel();
    lerEC();
}

void mostrarDadosSensores() {
    Serial.println("------ LEITURAS DA BANCADA ------");
    Serial.print("Temp ar: "); Serial.print(ambiente.temperaturaAr); Serial.println(" C");
    Serial.print("Umid ar: "); Serial.print(ambiente.umidadeAr); Serial.println(" %");
    Serial.print("Temp agua: "); Serial.print(solucao.temperaturaAgua); Serial.println(" C");
    Serial.print("pH: "); Serial.println(solucao.ph);
    Serial.print("EC: "); Serial.println(solucao.ec);
    Serial.print("Nivel: "); Serial.println(solucao.nivelOK ? "OK (Normal)" : "ALERTA (Baixo)");
    Serial.println("---------------------------------");
}

#endif
