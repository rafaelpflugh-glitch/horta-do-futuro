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
// AVALIAÇÃO DE PARÂMETROS
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
// CÁLCULO DE SAÚDE BIOLÓGICA (Idêntico ao Gêmeo Digital)
//=================================================
void calcularSaude() {
    float pontos = 100.0;

    // Penalidade por pH (Crítico: -25%)
    if (alertas.phBaixo || alertas.phAlto) {
        pontos -= 25.0;
    }

    // Penalidade por EC/Nutrição (-20%)
    if (alertas.ecBaixo || alertas.ecAlto) {
        pontos -= 20.0;
    }

    // Penalidade por Nível d'água DWC (Crítico: -25%)
    if (alertas.nivelBaixo) {
        pontos -= 25.0;
    }

    // Penalidade por Clima/Temperatura (-15%)
    if (alertas.temperaturaBaixa || alertas.temperaturaAlta) {
        pontos -= 15.0;
    }

    // Penalidade por Umidade (-15%)
    if (alertas.umidadeBaixa || alertas.umidadeAlta) {
        pontos -= 15.0;
    }

    if (pontos < 0.0) pontos = 0.0;

    saudeCultivo = (int)pontos;
}

//=================================================
// RELATÓRIO DETALHADO DE MÚLTIPLOS PROBLEMAS
//=================================================
String obterMensagemAlertas() {
    String msg = "";
    int totalProblemas = 0;

    if (alertas.phBaixo) { msg += "[pH Baixo] "; totalProblemas++; }
    if (alertas.phAlto) { msg += "[pH Alto] "; totalProblemas++; }
    if (alertas.ecBaixo) { msg += "[EC Baixa] "; totalProblemas++; }
    if (alertas.ecAlto) { msg += "[EC Alta] "; totalProblemas++; }
    if (alertas.temperaturaBaixa) { msg += "[Temp Ar Baixa] "; totalProblemas++; }
    if (alertas.temperaturaAlta) { msg += "[Temp Ar Alta] "; totalProblemas++; }
    if (alertas.umidadeBaixa) { msg += "[Umidade Baixa] "; totalProblemas++; }
    if (alertas.umidadeAlta) { msg += "[Umidade Alta] "; totalProblemas++; }
    if (alertas.nivelBaixo) { msg += "[Nivel Agua Baixo] "; totalProblemas++; }

    if (totalProblemas == 0) {
        return "Sistema Operando Normalmente (Sem Alertas)";
    }
    
    return "Atencao! " + String(totalProblemas) + " problema(s) detectado(s): " + msg;
}

//=================================================
// INICIALIZAÇÃO E ATUALIZAÇÃO
//=================================================
void iniciarDiagnostico() {
    Serial.println("Motor de Diagnóstico e Saúde Unificado.");
    limparAlertas();
}

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