#include <Arduino.h>
#include "config.h"
#include "dados.h"

//=================================================
// CULTIVO ATUAL
//=================================================
Planta cultivoAtual = {
    "ALFACE",
    "VEGETATIVO",
    PH_MIN_PADRAO,
    PH_MAX_PADRAO,
    EC_MIN_PADRAO,
    EC_MAX_PADRAO,
    TEMPERATURA_MIN_PADRAO,
    TEMPERATURA_MAX_PADRAO,
    TEMP_AGUA_MIN_PADRAO,
    TEMP_AGUA_MAX_PADRAO,
    UMIDADE_MIN_PADRAO,
    UMIDADE_MAX_PADRAO,
    HORAS_LUZ_PADRAO,
    HORA_INICIO_LUZ,
    0,
    BOMBA_ON_MIN_PADRAO,
    BOMBA_OFF_MIN_PADRAO
};

//=================================================
// AMBIENTE
//=================================================
Ambiente ambiente = {
    24.5,
    60.0
};

//=================================================
// SOLUÇÃO
//=================================================
Solucao solucao = {
    22.0,
    6.0,
    1.4,
    true,
    100.0
};

//=================================================
// ALERTAS
//=================================================
Alertas alertas = {
    false, false,
    false, false,
    false, false,
    false, false,
    false, false,
    false
};

//=================================================
// ATUADORES
//=================================================
Atuadores atuadores = {
    false,
    false,
    true,
    false
};

//=================================================
// MODOS DE CONTROLE E CALIBRAÇÃO
//=================================================
int modoLuz = 0;        // 0 = Auto, 1 = ON, 2 = OFF
int modoExaustor = 0;   // 0 = Auto, 1 = ON, 2 = OFF
int modoBombaAgua = 0;  // 0 = Auto, 1 = ON, 2 = OFF

float offsetPH = 0.0;
float fatorEC = 1.0;

//=================================================
// STATUS DO SISTEMA E SAÚDE
//=================================================
String mensagemSistema = "Sistema OK";
int saudeCultivo = 100;
int diaCultivo = 0;

bool gemeoConectado = false;
bool sdPronto = false;
bool rtcPronto = false;

bool wifiConectado = false;
bool wifiModoAP = false;
String ipLocal = "0.0.0.0";

//=================================================
// HISTÓRICO PARA GRÁFICO TFT
//=================================================
float histTempAr[TAMANHO_HISTORICO] = {0};
float histUmidAr[TAMANHO_HISTORICO] = {0};
float histPH[TAMANHO_HISTORICO] = {0};
float histEC[TAMANHO_HISTORICO] = {0};
int totalPontosHistorico = 0;

void registrarPontoHistorico() {
    if (totalPontosHistorico < TAMANHO_HISTORICO) {
        histTempAr[totalPontosHistorico] = ambiente.temperaturaAr;
        histUmidAr[totalPontosHistorico] = ambiente.umidadeAr;
        histPH[totalPontosHistorico] = solucao.ph;
        histEC[totalPontosHistorico] = solucao.ec;
        totalPontosHistorico++;
    } else {
        for (int i = 0; i < TAMANHO_HISTORICO - 1; i++) {
            histTempAr[i] = histTempAr[i + 1];
            histUmidAr[i] = histUmidAr[i + 1];
            histPH[i] = histPH[i + 1];
            histEC[i] = histEC[i + 1];
        }
        histTempAr[TAMANHO_HISTORICO - 1] = ambiente.temperaturaAr;
        histUmidAr[TAMANHO_HISTORICO - 1] = ambiente.umidadeAr;
        histPH[TAMANHO_HISTORICO - 1] = solucao.ph;
        histEC[TAMANHO_HISTORICO - 1] = solucao.ec;
    }
}
