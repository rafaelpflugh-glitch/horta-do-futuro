#ifndef DADOS_H
#define DADOS_H

#include <Arduino.h>
#include "config.h"

struct Planta {
    String nome;
    String fase;
    float phMin, phMax;
    float ecMin, ecMax;
    float temperaturaMin, temperaturaMax;
    float temperaturaAguaMin, temperaturaAguaMax;
    float umidadeMin, umidadeMax;
    int horasLuz;
    int horaInicioLuz;
    int minutoInicioLuz;
    int bombaOnMin;
    int bombaOffMin;
};

struct Ambiente {
    float temperaturaAr;
    float umidadeAr;
};

struct Solucao {
    float temperaturaAgua;
    float ph;
    float ec;
    bool nivelOK;
    float nivelPercentual;
};

struct Alertas {
    bool phBaixo, phAlto;
    bool ecBaixo, ecAlto;
    bool temperaturaBaixa, temperaturaAlta;
    bool tempAguaBaixa, tempAguaAlta;
    bool umidadeBaixa, umidadeAlta;
    bool nivelBaixo;
};

struct Atuadores {
    bool luz;
    bool ventilador;
    bool aeracao;
    bool bombaAgua;
};

extern Planta cultivoAtual;
extern Ambiente ambiente;
extern Solucao solucao;
extern Alertas alertas;
extern Atuadores atuadores;
extern String mensagemSistema;
extern int saudeCultivo;
extern int diaCultivo;

// 0 = AUTO, 1 = FORÇAR ON, 2 = FORÇAR OFF
extern int modoLuz;
extern int modoExaustor;
extern int modoBombaAgua;

// Calibração de sensores (Sincronizado com Display e Gêmeo Digital)
extern float offsetPH;
extern float fatorEC;

// Status de periféricos e sincronia
extern bool gemeoConectado;
extern bool sdPronto;
extern bool rtcPronto;

// Status da rede Wi-Fi e Web App embarcado
extern bool wifiConectado;
extern bool wifiModoAP;
extern String ipLocal;

// Histórico circular para plotagem no gráfico de Zoom do TFT
extern float histTempAr[TAMANHO_HISTORICO];
extern float histUmidAr[TAMANHO_HISTORICO];
extern float histPH[TAMANHO_HISTORICO];
extern float histEC[TAMANHO_HISTORICO];
extern int totalPontosHistorico;

void registrarPontoHistorico();

#endif
