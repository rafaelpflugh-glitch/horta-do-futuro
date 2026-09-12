#ifndef DADOS_H
#define DADOS_H

#include <Arduino.h>

//=================================================
// PERFIL DA PLANTA
//=================================================

struct Planta
{
    String nome;

    float phMin;
    float phMax;

    float ecMin;
    float ecMax;

    float temperaturaMin;
    float temperaturaMax;

    float umidadeMin;
    float umidadeMax;

    int horasLuz;
};


//=================================================
// AMBIENTE
//=================================================

struct Ambiente
{
    float temperaturaAr;
    float umidadeAr;
};


//=================================================
// SOLUÇÃO NUTRITIVA
//=================================================

struct Solucao
{
    float temperaturaAgua;

    float ph;

    float ec;

    bool nivelOK;
};


//=================================================
// ALERTAS
//=================================================

struct Alertas
{
    bool phBaixo;
    bool phAlto;

    bool ecBaixo;
    bool ecAlto;

    bool temperaturaBaixa;
    bool temperaturaAlta;

    bool umidadeBaixa;
    bool umidadeAlta;

    bool nivelBaixo;
};


//=================================================
// ATUADORES
//=================================================

struct Atuadores
{
    bool luz;
    bool ventilador;
    bool aeracao;
};


//=================================================
// VARIÁVEIS GLOBAIS
//=================================================

extern Planta cultivoAtual;

extern Ambiente ambiente;

extern Solucao solucao;

extern Alertas alertas;

extern Atuadores atuadores;

extern String mensagemSistema;

extern int saudeCultivo;

#endif