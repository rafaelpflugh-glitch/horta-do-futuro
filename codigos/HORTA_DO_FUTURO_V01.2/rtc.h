#ifndef RTC_H
#define RTC_H

#include <Arduino.h>
#include <Wire.h>
#include <RTClib.h> // Módulo de relógio real blindado
#include "config.h"
#include "dados.h"
#include "cultivo.h"

RTC_DS3231 rtc_modulo;

int horaAtual = 13;
int minutoAtual = 0;
int segundoAtual = 0;
int diaAtual = 16;
int mesAtual = 11;
int anoAtual = 2026;

unsigned long ultimoTickRelogioSoft = 0;

void iniciarRTC() {
    Wire.begin(21, 22); 
    
    if (!rtc_modulo.begin()) {
        rtcPronto = false;
        Serial.println("ALERTA: Modulo RTC DS3231 nao encontrado! Usando relogio interno (Software RTC).");
    } else {
        rtcPronto = true;
        Serial.println("RTC DS3231 inicializado com sucesso.");
        if (rtc_modulo.lostPower()) {
            Serial.println("RTC perdeu energia. Ajustando relogio interno...");
            rtc_modulo.adjust(DateTime(F(__DATE__), F(__TIME__)));
        }
    }
    ultimoTickRelogioSoft = millis();
}

void atualizarRTC() {
    if (rtcPronto) {
        DateTime agora = rtc_modulo.now();
        horaAtual = agora.hour();
        minutoAtual = agora.minute();
        segundoAtual = agora.second();
        diaAtual = agora.day();
        mesAtual = agora.month();
        anoAtual = agora.year();
    } else {
        // Fallback: Relógio em software via millis() caso o DS3231 esteja desconectado
        unsigned long agoraMs = millis();
        while (agoraMs - ultimoTickRelogioSoft >= 1000UL) {
            ultimoTickRelogioSoft += 1000UL;
            segundoAtual++;
            if (segundoAtual >= 60) {
                segundoAtual = 0;
                minutoAtual++;
                if (minutoAtual >= 60) {
                    minutoAtual = 0;
                    horaAtual++;
                    if (horaAtual >= 24) {
                        horaAtual = 0;
                        diaCultivo++;
                    }
                }
            }
        }
    }
}

void ajustarHorarioManual(int h, int m, int s = 0) {
    horaAtual = constrain(h, 0, 23);
    minutoAtual = constrain(m, 0, 59);
    segundoAtual = constrain(s, 0, 59);
    if (rtcPronto) {
        rtc_modulo.adjust(DateTime(anoAtual, mesAtual, diaAtual, horaAtual, minutoAtual, segundoAtual));
    }
}

String obterHora() {
    char texto[9];
    sprintf(texto, "%02d:%02d:%02d", horaAtual, minutoAtual, segundoAtual);
    return String(texto);
}

String obterData() {
    char texto[11];
    sprintf(texto, "%02d/%02d/%04d", diaAtual, mesAtual, anoAtual);
    return String(texto);
}

bool luzLigada() {
    int inicioMinutos = (cultivoAtual.horaInicioLuz * 60) + cultivoAtual.minutoInicioLuz;
    int duracaoMinutos = cultivoAtual.horasLuz * 60;
    if (duracaoMinutos >= 1440) return true;
    if (duracaoMinutos <= 0) return false;

    int fimMinutos = (inicioMinutos + duracaoMinutos) % 1440;
    int agoraMinutos = (horaAtual * 60) + minutoAtual;

    if (inicioMinutos < fimMinutos) {
        return (agoraMinutos >= inicioMinutos && agoraMinutos < fimMinutos);
    }
    return (agoraMinutos >= inicioMinutos || agoraMinutos < fimMinutos);
}

#endif
