#ifndef SISTEMA_H
#define SISTEMA_H

#include <Arduino.h>
#include <ArduinoJson.h> 
#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"
#include "fotoperiodo.h"
#include "sensores.h"
#include "diagnostico.h"
#include "automacao.h"
#include "estados.h"
#include "memoria_sd.h"
#include "display.h"

void enviarTelemetriaJSON() {
#if ARDUINOJSON_VERSION_MAJOR >= 7
    JsonDocument doc;
#else
    StaticJsonDocument<1024> doc;
#endif
    
    // Leituras de sensores
    doc["temperatura_ar"] = round(ambiente.temperaturaAr * 10.0) / 10.0;
    doc["umidade_ar"] = round(ambiente.umidadeAr * 10.0) / 10.0;
    doc["temperatura_agua"] = round(solucao.temperaturaAgua * 10.0) / 10.0;
    doc["ph"] = round(solucao.ph * 100.0) / 100.0;
    doc["ec"] = round(solucao.ec * 100.0) / 100.0;
    doc["nivel_agua"] = solucao.nivelOK ? 100.0 : 0.0;
    doc["saude"] = saudeCultivo;
    doc["dia_cultivo"] = diaCultivo;
    doc["hora"] = obterHora();

    // Estado real dos relés / atuadores
    doc["luz"] = atuadores.luz;
    doc["exaustor"] = atuadores.ventilador;
    doc["bomba_agua"] = atuadores.bombaAgua;
    doc["bomba_ar"] = atuadores.aeracao;

    // Modos de operação (0=AUTO, 1=ON, 2=OFF)
    doc["modo_luz"] = modoLuz;
    doc["modo_exaustor"] = modoExaustor;
    doc["modo_bomba_agua"] = modoBombaAgua;

    // Calibração ativa
    doc["offset_ph"] = round(offsetPH * 100.0) / 100.0;
    doc["fator_ec"] = round(fatorEC * 100.0) / 100.0;

    // Receita e Metas Ativas no ESP32
    doc["cultura"] = cultivoAtual.nome;
    doc["fase"] = cultivoAtual.fase;
    doc["ph_min"] = round(cultivoAtual.phMin * 100.0) / 100.0;
    doc["ph_max"] = round(cultivoAtual.phMax * 100.0) / 100.0;
    doc["ec_min"] = round(cultivoAtual.ecMin * 100.0) / 100.0;
    doc["ec_max"] = round(cultivoAtual.ecMax * 100.0) / 100.0;
    doc["temp_ar_min"] = round(cultivoAtual.temperaturaMin * 10.0) / 10.0;
    doc["temp_ar_max"] = round(cultivoAtual.temperaturaMax * 10.0) / 10.0;
    doc["temp_agua_min"] = round(cultivoAtual.temperaturaAguaMin * 10.0) / 10.0;
    doc["temp_agua_max"] = round(cultivoAtual.temperaturaAguaMax * 10.0) / 10.0;
    doc["umidade_min"] = round(cultivoAtual.umidadeMin * 10.0) / 10.0;
    doc["umidade_max"] = round(cultivoAtual.umidadeMax * 10.0) / 10.0;
    doc["fotoperiodo"] = cultivoAtual.horasLuz;
    doc["inicio_luz"] = cultivoAtual.horaInicioLuz;
    doc["bomba_on"] = cultivoAtual.bombaOnMin;
    doc["bomba_off"] = cultivoAtual.bombaOffMin;

    serializeJson(doc, Serial);
    Serial.println(); 
}

void receberComandosJSON() {
    while (Serial.available() > 0) {
        String linha = Serial.readStringUntil('\n');
        linha.trim();
        if (linha.length() < 2 || !linha.startsWith("{")) continue;

#if ARDUINOJSON_VERSION_MAJOR >= 7
        JsonDocument doc;
#else
        StaticJsonDocument<1024> doc;
#endif
        DeserializationError erro = deserializeJson(doc, linha);
        if (erro) continue;

        gemeoConectado = true;
        String cmd = doc["cmd"] | "";

        if (cmd == "set_config") {
            if (!doc["cultura"].isNull()) cultivoAtual.nome = doc["cultura"].as<String>();
            if (!doc["fase"].isNull()) cultivoAtual.fase = doc["fase"].as<String>();
            if (!doc["ph_min"].isNull()) cultivoAtual.phMin = doc["ph_min"].as<float>();
            if (!doc["ph_max"].isNull()) cultivoAtual.phMax = doc["ph_max"].as<float>();
            if (!doc["ec_min"].isNull()) cultivoAtual.ecMin = doc["ec_min"].as<float>();
            if (!doc["ec_max"].isNull()) cultivoAtual.ecMax = doc["ec_max"].as<float>();
            if (!doc["temp_ar_min"].isNull()) cultivoAtual.temperaturaMin = doc["temp_ar_min"].as<float>();
            if (!doc["temp_ar_max"].isNull()) cultivoAtual.temperaturaMax = doc["temp_ar_max"].as<float>();
            if (!doc["temp_agua_min"].isNull()) cultivoAtual.temperaturaAguaMin = doc["temp_agua_min"].as<float>();
            if (!doc["temp_agua_max"].isNull()) cultivoAtual.temperaturaAguaMax = doc["temp_agua_max"].as<float>();
            if (!doc["umidade_min"].isNull()) cultivoAtual.umidadeMin = doc["umidade_min"].as<float>();
            if (!doc["umidade_max"].isNull()) cultivoAtual.umidadeMax = doc["umidade_max"].as<float>();
            if (!doc["fotoperiodo"].isNull()) cultivoAtual.horasLuz = (int)round(doc["fotoperiodo"].as<float>());
            if (!doc["inicio_luz"].isNull()) cultivoAtual.horaInicioLuz = doc["inicio_luz"].as<int>();
            if (!doc["inicio_minuto"].isNull()) cultivoAtual.minutoInicioLuz = doc["inicio_minuto"].as<int>();
            if (!doc["bomba_on"].isNull()) cultivoAtual.bombaOnMin = doc["bomba_on"].as<int>();
            if (!doc["bomba_off"].isNull()) cultivoAtual.bombaOffMin = doc["bomba_off"].as<int>();

            configurarFotoperiodo();
            atualizarDiagnostico();
            atualizarAutomacao();
            atualizarValoresDisplay();
            enviarTelemetriaJSON();
        }
        else if (cmd == "set_calibration") {
            if (!doc["offset_ph"].isNull()) offsetPH = doc["offset_ph"].as<float>();
            if (!doc["fator_ec"].isNull()) fatorEC = max(0.1f, doc["fator_ec"].as<float>());

            lerPH();
            lerEC();
            atualizarDiagnostico();
            atualizarValoresDisplay();
            enviarTelemetriaJSON();
        }
        else if (cmd == "set_actuators") {
            if (!doc["modo_luz"].isNull()) modoLuz = constrain(doc["modo_luz"].as<int>(), 0, 2);
            if (!doc["modo_exaustor"].isNull()) modoExaustor = constrain(doc["modo_exaustor"].as<int>(), 0, 2);
            if (!doc["modo_bomba_agua"].isNull()) modoBombaAgua = constrain(doc["modo_bomba_agua"].as<int>(), 0, 2);

            atualizarAutomacao();
            atualizarValoresDisplay();
            enviarTelemetriaJSON();
        }
        else if (cmd == "set_clock") {
            int h = doc["hora"] | horaAtual;
            int m = doc["minuto"] | minutoAtual;
            int s = doc["segundo"] | 0;
            ajustarHorarioManual(h, m, s);
            atualizarAutomacao();
            atualizarValoresDisplay();
            enviarTelemetriaJSON();
        }
        else if (cmd == "sync_request") {
            atualizarValoresDisplay();
            enviarTelemetriaJSON();
        }
    }
}

void iniciarSistema() {
    iniciarCultivo();
    iniciarRTC();
    configurarFotoperiodo();
    iniciarSensores();
    iniciarDiagnostico();
    iniciarAutomacao();
    iniciarMemoria();
    atualizarSensores();
    atualizarDiagnostico();
    atualizarAutomacao();
    registrarPontoHistorico();
    estadoAtual = MONITORAMENTO;
}

void executarCiclo() {
    atualizarRTC();
    atualizarSensores();
    atualizarDiagnostico();
    atualizarAutomacao();
    registrarPontoHistorico();
    atualizarValoresDisplay();
    enviarTelemetriaJSON();
    registrarDados();
}

#endif
