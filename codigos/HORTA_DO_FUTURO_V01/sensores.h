    #ifndef SENSORES_H
    #define SENSORES_H

    #include <Arduino.h>
    #include "config.h"
    #include "dados.h"
    #include "sensor_temperatura.h"
    #include "sensor_ph.h"
    #include "sensor_nivel.h"

    void iniciarSensores() {
        Serial.println("Inicializando sensores reais...");
        
        iniciarSensoresTemperatura();
        iniciarSensorPH();
        iniciarSensorNivel();
        
        Serial.println("Sensores inicializados com sucesso.");
    }

    void atualizarSensores() {
        lerTemperatura();
        lerPH();
        lerNivel();
        
        // EC manual provisório até implementação física
        solucao.ec = 1.4; 
    }

    void mostrarDadosSensores() {
        Serial.println();
        Serial.println("------ LEITURAS REAIS ------");
        Serial.print("Temp ar: "); Serial.print(ambiente.temperaturaAr); Serial.println(" C");
        Serial.print("Umid ar: "); Serial.print(ambiente.umidadeAr); Serial.println(" %");
        Serial.print("Temp agua: "); Serial.print(solucao.temperaturaAgua); Serial.println(" C");
        Serial.print("pH: "); Serial.println(solucao.ph);
        Serial.print("EC: "); Serial.println(solucao.ec);
        Serial.print("Nivel: "); Serial.println(solucao.nivelOK ? "OK" : "BAIXO");
        Serial.println("----------------------------");
    }

    void enviarTelemetriaJSON() {
        // Formato exato que a interface Python espera ler na Serial
        Serial.print("{\"temperatura_ar\":");
        Serial.print(ambiente.temperaturaAr, 1);
        Serial.print(",\"umidade_ar\":");
        Serial.print(ambiente.umidadeAr, 1);
        Serial.print(",\"temperatura_agua\":");
        Serial.print(solucao.temperaturaAgua, 1);
        Serial.print(",\"ph\":");
        Serial.print(solucao.ph, 2);
        Serial.print(",\"ec\":");
        Serial.print(solucao.ec, 2);
        Serial.print(",\"nivel_agua\":");
        Serial.print(solucao.nivelOK ? 100 : 0);
        Serial.print(",\"saude\":");
        Serial.print(saudeCultivo);
        Serial.println("}");
    }

    #endif