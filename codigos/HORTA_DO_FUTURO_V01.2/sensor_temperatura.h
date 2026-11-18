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
    float tempAr = dht.readTemperature();
    float umidAr = dht.readHumidity();

    if (!isnan(tempAr) && tempAr > -10.0 && tempAr < 80.0) ambiente.temperaturaAr = tempAr;
    if (!isnan(umidAr) && umidAr >= 0.0 && umidAr <= 100.0) ambiente.umidadeAr = umidAr;

    sensorAgua.requestTemperatures();
    float tempAguaLida = sensorAgua.getTempCByIndex(0);
    // Filtra erro -127.0 C ou 85.0 C quando o DS18B20 está inicializando ou desconectado
    if (tempAguaLida > -20.0 && tempAguaLida < 80.0) {
        solucao.temperaturaAgua = tempAguaLida;
    }
}

#endif
