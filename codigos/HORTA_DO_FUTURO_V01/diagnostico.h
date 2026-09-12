#ifndef DIAGNOSTICO_H
#define DIAGNOSTICO_H

#include <Arduino.h>
#include "dados.h"
#include "cultivo.h"

//=================================================
// LIMPAR ALERTAS
//=================================================
void limparAlertas() {
    alertas.phBaixo = false;
    alertas.phAlto = false;
    alertas.ecBaixo = false;
    alertas.ecAlto = false;
    alertas.temperaturaBaixa = false;
    alertas.temperaturaAlta = false;
    alertas.umidadeBaixa = false;
    alertas.umidadeAlta = false;
    alertas.nivelBaixo = false;
}

//=================================================
// DIAGNÓSTICO INDIVIDUAL DE PARÂMETROS
//=================================================
void diagnosticarPH() {
    if (solucao.ph < cultivoAtual.phMin) alertas.phBaixo = true;
    if (solucao.ph > cultivoAtual.phMax) alertas.phAlto = true;
}

void diagnosticarEC() {
    if (solucao.ec < cultivoAtual.ecMin) alertas.ecBaixo = true;
    if (solucao.ec > cultivoAtual.ecMax) alertas.ecAlto = true;
}

void diagnosticarTemperatura() {
    if (ambiente.temperaturaAr < cultivoAtual.temperaturaMin) alertas.temperaturaBaixa = true;
    if (ambiente.temperaturaAr > cultivoAtual.temperaturaMax) alertas.temperaturaAlta = true;
}

void diagnosticarUmidade() {
    if (ambiente.umidadeAr < cultivoAtual.umidadeMin) alertas.umidadeBaixa = true;
    if (ambiente.umidadeAr > cultivoAtual.umidadeMax) alertas.umidadeAlta = true;
}

void diagnosticarNivel() {
    if (!solucao.nivelOK) alertas.nivelBaixo = true;
}

//=================================================
// CÁLCULO DE SAÚDE (Embrionário do Gêmeo Digital)
//=================================================
void calcularSaude() {
    int pontos = 100;

    if (alertas.phBaixo || alertas.phAlto) pontos -= 20;
    if (alertas.ecBaixo || alertas.ecAlto) pontos -= 20;
    if (alertas.temperaturaBaixa || alertas.temperaturaAlta) pontos -= 20;
    if (alertas.umidadeBaixa || alertas.umidadeAlta) pontos -= 15;
    if (alertas.nivelBaixo) pontos -= 25;

    if (pontos < 0) pontos = 0;

    saudeCultivo = pontos;
}

//=================================================
// INICIALIZAÇÃO
//=================================================
void iniciarDiagnostico() {
    Serial.println("Diagnostico e motor de saude inicializados.");
    limparAlertas();
}

//=================================================
// ATUALIZAÇÃO GERAL DO DIAGNÓSTICO
//=================================================
void atualizarDiagnostico() {
    limparAlertas();
    diagnosticarPH();
    diagnosticarEC();
    diagnosticarTemperatura();
    diagnosticarUmidade();
    diagnosticarNivel();
    calcularSaude();
}

#endif