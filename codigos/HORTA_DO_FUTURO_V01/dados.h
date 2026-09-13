#ifndef DADOS_H
#define DADOS_H

#include <Arduino.h>

struct Planta {
    String nome;
    float phMin, phMax;
    float ecMin, ecMax;
    float temperaturaMin, temperaturaMax;
    float umidadeMin, umidadeMax;
    int horasLuz;
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
};

struct Alertas {
    bool phBaixo, phAlto;
    bool ecBaixo, ecAlto;
    bool temperaturaBaixa, temperaturaAlta;
    bool umidadeBaixa, umidadeAlta;
    bool nivelBaixo;
};

struct Atuadores {
    bool luz;
    bool ventilador;
    bool aeracao;
};

extern Planta cultivoAtual;
extern Ambiente ambiente;
extern Solucao solucao;
extern Alertas alertas;
extern Atuadores atuadores;
extern String mensagemSistema;
extern int saudeCultivo;

// 0 = AUTO (Relógio), 1 = FORÇAR ON, 2 = FORÇAR OFF
extern int modoLuz; 

#endif