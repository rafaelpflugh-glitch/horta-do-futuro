#ifndef SENSOR_TEMPERATURA_H
#define SENSOR_TEMPERATURA_H

#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "config.h"
#include "dados.h"

#define TIPO_DHT DHT22

DHT dht(PINO_DHT, TIPO_DHT);
OneWire barramentoTemperatura(PINO_DS18B20);
DallasTemperature sensorAgua(&barramentoTemperatura);

void iniciarSensoresTemperatura() {
    dht.begin();
    sensorAgua.begin();
    Serial.println("Sensores de temperatura (Ar e Agua) preparados.");
}

void lerTemperatura() {
    // Leitura do Ar (DHT22)
    float tempAr = dht.readTemperature();
    float umidAr = dht.readHumidity();

    if (!isnan(tempAr)) ambiente.temperaturaAr = tempAr;
    if (!isnan(umidAr)) ambiente.umidadeAr = umidAr;

    // Leitura da Solução Nutritiva (DS18B20)
    sensorAgua.requestTemperatures();
    solucao.temperaturaAgua = sensorAgua.getTempCByIndex(0);
}

#endif