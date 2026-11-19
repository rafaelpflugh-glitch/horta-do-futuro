#ifndef DISPLAY_H
#define DISPLAY_H

#include "config.h"
#include "dados.h"

#if USAR_DISPLAY_TFT

#include <SPI.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#include "cultivo.h"
#include "rtc.h"
#include "sensores.h"
#include "diagnostico.h"
#include "automacao.h"

// Pinos do Touch (XPT2046)
#ifndef TOUCH_CS
#define TOUCH_CS 33
#endif

TFT_eSPI tft = TFT_eSPI();
XPT2046_Touchscreen touch(TOUCH_CS);

//=================================================
// PALETA DE CORES DARK THEME - OLED & ALTA LEGIBILIDADE
//=================================================
#define COR_BG       0x0000  // Preto Absoluto (OLED Black)
#define COR_CARD     0x10A2  // Cinza Chumbo Escuro para os Cartões
#define COR_BORDA    0x3186  // Linha Guia Sutil
#define COR_TEXTO    0xFFFF  // Branco Puro (Máxima nitidez)
#define COR_SUBTEXTO 0xCE79  // Cinza Claro Nítido (Rótulos)
#define COR_VERDE    0x07E0  // Verde Sucesso / Ótimo
#define COR_AZUL     0x2CDF  // Azul Destaque / Ações
#define COR_ALERTA   0xF800  // Vermelho / Perigo
#define COR_AVISO    0xFD20  // Laranja / Atenção

//=================================================
// ESTADOS DA INTERFACE & ANIMAÇÃO
//=================================================
enum TelaTFT { SPLASH, HOME, CLIMA, DWC, CONTROLE, SISTEMA, GRAFICO };
TelaTFT telaAtual = SPLASH;

bool graficoZoomAtivo = false;
int graficoSelecionado = 0; // 0 = Temp Ar, 1 = Umidade, 2 = pH, 3 = EC

// Protótipos externos e internos
void enviarTelemetriaJSON();
void atualizarDisplayCompleto();
void atualizarValoresDisplay();
void desenharNavBar();
void renderizarSplash();
void renderizarGraficoZoom();

//=================================================
// FUNÇÕES DE DESENHO AUXILIARES
//=================================================
void desenharBotao(int x, int y, int w, int h, String texto, uint16_t corBase, uint16_t corTexto) {
    tft.fillRoundRect(x, y, w, h, 6, corBase);
    tft.drawRoundRect(x, y, w, h, 6, COR_BORDA);
    tft.setTextColor(corTexto, corBase);
    tft.setTextDatum(MC_DATUM); 
    tft.drawString(texto, x + (w/2), y + (h/2), 2);
    tft.setTextDatum(TL_DATUM); 
}

//=================================================
// BARRA DE NAVEGAÇÃO INFERIOR (FIXA - 5 ABAS)
//=================================================
void desenharNavBar() {
    tft.fillRect(0, 205, 320, 35, COR_BG);
    tft.drawFastHLine(0, 205, 320, COR_BORDA);

    uint16_t c0 = (telaAtual == HOME) ? COR_AZUL : COR_CARD;
    uint16_t c1 = (telaAtual == CLIMA) ? COR_AZUL : COR_CARD;
    uint16_t c2 = (telaAtual == DWC) ? COR_AZUL : COR_CARD;
    uint16_t c3 = (telaAtual == CONTROLE) ? COR_AZUL : COR_CARD;
    uint16_t c4 = (telaAtual == SISTEMA) ? COR_AZUL : COR_CARD;

    desenharBotao(10,  210, 56, 22, "HOME", c0, COR_TEXTO);
    desenharBotao(71,  210, 56, 22, "CLIMA", c1, COR_TEXTO);
    desenharBotao(132, 210, 56, 22, "DWC", c2, COR_TEXTO);
    desenharBotao(193, 210, 56, 22, "CONT", c3, COR_TEXTO);
    desenharBotao(254, 210, 56, 22, "SIST", c4, COR_TEXTO);
}

//=================================================
// TELA 0: SPLASH COM BOTÃO CENTRAL E ANIMAÇÃO
//=================================================
void renderizarSplash() {
    tft.fillScreen(COR_BG);
    
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.setTextDatum(MC_DATUM);
    tft.drawString("HORTA DO FUTURO", 160, 50, 4);
    
    tft.setTextColor(COR_SUBTEXTO, COR_BG);
    tft.drawString("Computador de Plantas & Digital Twin", 160, 85, 2);

    tft.fillRoundRect(60, 115, 200, 55, 8, COR_CARD);
    tft.drawRoundRect(60, 115, 200, 55, 8, COR_AZUL);
    tft.setTextColor(COR_TEXTO, COR_CARD);
    tft.drawString("INICIAR SISTEMA", 160, 142, 2);

    tft.setTextDatum(TL_DATUM);
}

void executarAnimacaoInicializacao() {
    tft.fillScreen(COR_BG);
    tft.setTextDatum(MC_DATUM);
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString("Sincronizando Digital Twin...", 160, 90, 2);
    
    for (int i = 0; i <= 100; i += 20) {
        tft.drawRoundRect(60, 130, 200, 16, 4, COR_BORDA);
        int w = map(i, 0, 100, 0, 192);
        tft.fillRoundRect(64, 134, w, 8, 2, COR_VERDE);
        delay(120);
    }
    
    tft.setTextColor(COR_VERDE, COR_BG);
    tft.drawString("Sistema Operacional Pronto!", 160, 175, 2);
    delay(600);
    tft.setTextDatum(TL_DATUM);
}

//=================================================
// 1. TELA HOME (DASHBOARD)
//=================================================
void desenharConteudoHome() {
    tft.setTextColor(COR_SUBTEXTO, COR_BG);
    tft.drawString(obterHora() + "  ", 230, 8, 2);

    // Card Cultura (Toque alterna Alface / Manjericão)
    tft.fillRoundRect(12, 38, 145, 35, 6, COR_CARD);
    tft.drawRoundRect(12, 38, 145, 35, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("CULTURA:", 20, 44, 1);
    tft.setTextColor(COR_VERDE, COR_CARD);
    tft.drawString(cultivoAtual.nome.substring(0, 10), 75, 44, 1);
    tft.setTextColor(COR_AZUL, COR_CARD);
    tft.drawString("Fase: " + cultivoAtual.fase.substring(0, 10), 20, 58, 1);

    // Card Saúde Biológica
    tft.fillRoundRect(12, 78, 145, 120, 6, COR_CARD);
    tft.drawRoundRect(12, 78, 145, 120, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("SAUDE BIOLOGICA", 22, 88, 1);
    
    uint16_t corSaude = (saudeCultivo > 75) ? COR_VERDE : (saudeCultivo > 40 ? COR_AVISO : COR_ALERTA);
    tft.drawRoundRect(22, 120, 125, 10, 4, COR_BORDA);
    int larguraPreenchimento = map(constrain(saudeCultivo, 0, 100), 0, 100, 0, 121);
    tft.fillRoundRect(24, 122, larguraPreenchimento, 6, 2, corSaude);
    
    tft.setTextDatum(MC_DATUM);
    tft.setTextColor(corSaude, COR_CARD);
    tft.drawString(String(saudeCultivo) + "%", 84, 158, 4);
    tft.setTextDatum(TL_DATUM);

    // Card Estado da Bancada
    tft.fillRoundRect(167, 38, 141, 160, 6, COR_CARD);
    tft.drawRoundRect(167, 38, 141, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("ESTADO BANCADA", 177, 46, 1);
    
    tft.setTextColor(COR_TEXTO, COR_CARD);
    tft.drawString("Ar: " + String(ambiente.temperaturaAr, 1) + "C | " + String(ambiente.umidadeAr, 0) + "%", 177, 68, 1);
    tft.drawString("Agua: " + String(solucao.temperaturaAgua, 1) + "C", 177, 88, 1);
    tft.drawString("pH: " + String(solucao.ph, 2) + " | EC: " + String(solucao.ec, 1), 177, 108, 1);
    tft.setTextColor(atuadores.luz ? COR_AVISO : COR_SUBTEXTO, COR_CARD);
    tft.drawString("Luz: " + String(atuadores.luz ? "LIGADA" : "DESLIG"), 177, 130, 1);
    tft.setTextColor(atuadores.ventilador ? COR_AZUL : COR_SUBTEXTO, COR_CARD);
    tft.drawString("Fan: " + String(atuadores.ventilador ? "LIGADO" : "DESLIG"), 177, 150, 1);
    tft.setTextColor(solucao.nivelOK ? COR_VERDE : COR_ALERTA, COR_CARD);
    tft.drawString("DWC: " + String(solucao.nivelOK ? "NIVEL OK" : "NIVEL BAIXO"), 177, 170, 1);
}

void renderizarHome() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString("HORTA DO FUTURO", 12, 8, 2);
    tft.drawFastHLine(10, 28, 300, COR_BORDA);
    desenharConteudoHome();
    desenharNavBar();
}

//=================================================
// 2. TELA CLIMA (ATMOSFERA)
//=================================================
void desenharConteudoClima() {
    tft.fillRoundRect(12, 38, 145, 160, 6, COR_CARD);
    tft.drawRoundRect(12, 38, 145, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("TEMP AR [ZOOM]", 22, 48, 1);
    uint16_t corTemp = (alertas.temperaturaBaixa || alertas.temperaturaAlta) ? COR_ALERTA : COR_TEXTO;
    tft.setTextColor(corTemp, COR_CARD);
    tft.drawString(String(ambiente.temperaturaAr, 1) + " C", 22, 88, 4);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("Meta: " + String(cultivoAtual.temperaturaMin, 0) + "-" + String(cultivoAtual.temperaturaMax, 0) + "C", 22, 140, 1);
    tft.setTextColor(COR_AZUL, COR_CARD);
    tft.drawString("Toque p/ grafico", 22, 168, 1);

    tft.fillRoundRect(167, 38, 141, 160, 6, COR_CARD);
    tft.drawRoundRect(167, 38, 141, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("UMIDADE [ZOOM]", 177, 48, 1);
    uint16_t corUmid = (alertas.umidadeBaixa || alertas.umidadeAlta) ? COR_AVISO : COR_TEXTO;
    tft.setTextColor(corUmid, COR_CARD);
    tft.drawString(String(ambiente.umidadeAr, 0) + " %", 177, 88, 4);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("Meta: " + String(cultivoAtual.umidadeMin, 0) + "-" + String(cultivoAtual.umidadeMax, 0) + "%", 177, 140, 1);
    tft.setTextColor(COR_AZUL, COR_CARD);
    tft.drawString("Toque p/ grafico", 177, 168, 1);
}

void renderizarClima() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString("MONITORAMENTO CLIMATICO", 12, 8, 2);
    tft.drawFastHLine(10, 28, 300, COR_BORDA);
    desenharConteudoClima();
    desenharNavBar();
}

//=================================================
// 3. TELA DWC (RESERVATÓRIO E SOLUÇÃO)
//=================================================
void desenharConteudoDWC() {
    tft.fillRoundRect(12, 38, 95, 160, 6, COR_CARD);
    tft.drawRoundRect(12, 38, 95, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("NIVEL DWC", 20, 48, 1);
    tft.setTextColor(solucao.nivelOK ? COR_VERDE : COR_ALERTA, COR_CARD);
    tft.drawString(solucao.nivelOK ? "OK" : "BAIXO", 20, 85, 2);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString(solucao.nivelOK ? "100% (10L)" : "CRITICO!", 20, 130, 1);
    tft.drawString(atuadores.bombaAgua ? "Bomba: ON" : "Bomba: OFF", 20, 155, 1);

    tft.fillRoundRect(113, 38, 95, 160, 6, COR_CARD);
    tft.drawRoundRect(113, 38, 95, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("TEMP AGUA", 121, 48, 1);
    uint16_t corTagua = (alertas.tempAguaBaixa || alertas.tempAguaAlta) ? COR_ALERTA : COR_TEXTO;
    tft.setTextColor(corTagua, COR_CARD);
    tft.drawString(String(solucao.temperaturaAgua, 1) + "C", 121, 85, 2);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("Meta: " + String(cultivoAtual.temperaturaAguaMin, 0) + "-" + String(cultivoAtual.temperaturaAguaMax, 0) + "C", 121, 130, 1);
    tft.drawString(atuadores.aeracao ? "Ar: ON" : "Ar: OFF", 121, 155, 1);

    tft.fillRoundRect(214, 38, 94, 160, 6, COR_CARD);
    tft.drawRoundRect(214, 38, 94, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("NUTRI [ZOOM]", 220, 48, 1);
    
    uint16_t corPH = (alertas.phBaixo || alertas.phAlto) ? COR_ALERTA : COR_VERDE;
    uint16_t corEC = (alertas.ecBaixo || alertas.ecAlto) ? COR_AVISO : COR_AZUL;
    tft.setTextColor(corPH, COR_CARD);
    tft.drawString("pH:" + String(solucao.ph, 2), 220, 85, 2);
    tft.setTextColor(corEC, COR_CARD);
    tft.drawString("EC:" + String(solucao.ec, 2), 220, 125, 2);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("Toque p/ zoom", 220, 165, 1);
}

void renderizarDWC() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString("RESERVATORIO DWC", 12, 8, 2);
    tft.drawFastHLine(10, 28, 300, COR_BORDA);
    desenharConteudoDWC();
    desenharNavBar();
}

//=================================================
// 4. TELA CONTROLE (MANUAL & RELÉS BIDIRECIONAL)
//=================================================
void desenharConteudoControle() {
    tft.setTextColor(COR_SUBTEXTO, COR_BG);
    tft.drawString("ILUMINACAO LED (REL 1): " + String(atuadores.luz ? "[ON]  " : "[OFF] "), 12, 35, 1);
    desenharBotao(12,  48, 92, 30, "AUTO", (modoLuz==0)?COR_AZUL:COR_CARD, COR_TEXTO);
    desenharBotao(112, 48, 92, 30, "ON",   (modoLuz==1)?COR_VERDE:COR_CARD, COR_TEXTO);
    desenharBotao(212, 48, 96, 30, "OFF",  (modoLuz==2)?COR_ALERTA:COR_CARD, COR_TEXTO);

    tft.setTextColor(COR_SUBTEXTO, COR_BG);
    tft.drawString("EXAUSTOR CLIMA (REL 2): " + String(atuadores.ventilador ? "[ON]  " : "[OFF] "), 12, 88, 1);
    desenharBotao(12,  101, 92, 30, "AUTO", (modoExaustor==0)?COR_AZUL:COR_CARD, COR_TEXTO);
    desenharBotao(112, 101, 92, 30, "ON",   (modoExaustor==1)?COR_VERDE:COR_CARD, COR_TEXTO);
    desenharBotao(212, 101, 96, 30, "OFF",  (modoExaustor==2)?COR_ALERTA:COR_CARD, COR_TEXTO);

    tft.setTextColor(COR_SUBTEXTO, COR_BG);
    tft.drawString("BOMBA AGUA DWC (REL 3): " + String(atuadores.bombaAgua ? "[ON]  " : "[OFF] "), 12, 141, 1);
    desenharBotao(12,  154, 92, 30, "AUTO", (modoBombaAgua==0)?COR_AZUL:COR_CARD, COR_TEXTO);
    desenharBotao(112, 154, 92, 30, "ON",   (modoBombaAgua==1)?COR_VERDE:COR_CARD, COR_TEXTO);
    desenharBotao(212, 154, 96, 30, "OFF",  (modoBombaAgua==2)?COR_ALERTA:COR_CARD, COR_TEXTO);
}

void renderizarControle() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString("CONTROLE DE ATUADORES", 12, 8, 2);
    tft.drawFastHLine(10, 28, 300, COR_BORDA);
    desenharConteudoControle();
    desenharNavBar();
}

//=================================================
// 5. TELA SISTEMA & CALIBRAÇÃO
//=================================================
void desenharConteudoSistema() {
    tft.fillRoundRect(12, 38, 145, 160, 6, COR_CARD);
    tft.drawRoundRect(12, 38, 145, 160, 6, COR_BORDA);
    
    // Calibração Offset pH
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("Offset pH:", 20, 44, 1);
    desenharBotao(20, 58, 38, 30, "-", COR_BG, COR_TEXTO);
    tft.setTextDatum(MC_DATUM);
    tft.setTextColor(COR_VERDE, COR_CARD);
    tft.drawString(String(offsetPH, 1), 84, 73, 2);
    tft.setTextDatum(TL_DATUM);
    desenharBotao(110, 58, 38, 30, "+", COR_BG, COR_TEXTO);

    // Calibração Fator EC
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("Ganho EC:", 20, 102, 1);
    desenharBotao(20, 116, 38, 30, "-", COR_BG, COR_TEXTO);
    tft.setTextDatum(MC_DATUM);
    tft.setTextColor(COR_AZUL, COR_CARD);
    tft.drawString(String(fatorEC, 2), 84, 131, 2);
    tft.setTextDatum(TL_DATUM);
    desenharBotao(110, 116, 38, 30, "+", COR_BG, COR_TEXTO);

    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("pH:" + String(solucao.ph, 2) + " EC:" + String(solucao.ec, 2), 20, 165, 1);

    // Card Diagnóstico
    tft.fillRoundRect(167, 38, 141, 160, 6, COR_CARD);
    tft.drawRoundRect(167, 38, 141, 160, 6, COR_BORDA);
    tft.setTextColor(COR_SUBTEXTO, COR_CARD);
    tft.drawString("DIAGNOSTICO", 177, 45, 1);
    tft.setTextColor((wifiConectado || wifiModoAP) ? COR_VERDE : COR_AVISO, COR_CARD);
    String txtWifi = wifiConectado ? ("> IP: " + ipLocal) : (wifiModoAP ? ("> AP: " + ipLocal) : "> WiFi: Offline");
    tft.drawString(txtWifi.substring(0, 21), 175, 64, 1);
    tft.setTextColor(gemeoConectado ? COR_VERDE : COR_AVISO, COR_CARD);
    tft.drawString(gemeoConectado ? "> Gemeo: Sync OK" : "> Gemeo: Serial", 175, 86, 1);
    tft.setTextColor(COR_VERDE, COR_CARD);
    tft.drawString("> USB: 115200 bps", 175, 108, 1);
    tft.setTextColor(rtcPronto ? COR_VERDE : COR_AVISO, COR_CARD);
    tft.drawString(rtcPronto ? "> RTC: DS3231 OK" : "> RTC: Soft Timer", 175, 130, 1);
    tft.setTextColor(sdPronto ? COR_VERDE : COR_SUBTEXTO, COR_CARD);
    tft.drawString(sdPronto ? "> SD: Gravando" : "> SD: Nao Inser.", 175, 152, 1);
    tft.setTextColor(atuadores.aeracao ? COR_VERDE : COR_ALERTA, COR_CARD);
    tft.drawString(atuadores.aeracao ? "> Ar DWC: Ativo" : "> Ar DWC: Parado", 175, 174, 1);
}

void renderizarSistema() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString("SISTEMA & CALIBRACAO", 12, 8, 2);
    tft.drawFastHLine(10, 28, 300, COR_BORDA);
    desenharConteudoSistema();
    desenharNavBar();
}

//=================================================
// TELA DE ZOOM DO GRÁFICO (HISTÓRICO REAL)
//=================================================
void renderizarGraficoZoom() {
    tft.fillScreen(COR_BG);
    
    String titulo = "ZOOM: TEMPERATURA AR";
    float vMin = 10.0, vMax = 40.0;
    float* buffer = histTempAr;
    float atual = ambiente.temperaturaAr;
    String unid = " C";
    uint16_t corLinha = COR_AZUL;

    if (graficoSelecionado == 1) {
        titulo = "ZOOM: UMIDADE AR";
        vMin = 20.0; vMax = 100.0;
        buffer = histUmidAr;
        atual = ambiente.umidadeAr;
        unid = " %";
        corLinha = COR_VERDE;
    } else if (graficoSelecionado == 2) {
        titulo = "ZOOM: HISTORICO pH";
        vMin = 4.0; vMax = 9.0;
        buffer = histPH;
        atual = solucao.ph;
        unid = "";
        corLinha = COR_VERDE;
    } else if (graficoSelecionado == 3) {
        titulo = "ZOOM: HISTORICO EC";
        vMin = 0.0; vMax = 3.0;
        buffer = histEC;
        atual = solucao.ec;
        unid = " mS";
        corLinha = COR_AVISO;
    }

    tft.setTextColor(COR_AZUL, COR_BG);
    tft.drawString(titulo, 12, 8, 2);
    
    desenharBotao(235, 5, 75, 26, "VOLTAR", COR_AZUL, COR_TEXTO);
    tft.drawFastHLine(10, 35, 300, COR_BORDA);

    tft.drawRect(12, 42, 296, 156, COR_BORDA);
    tft.fillRect(14, 44, 292, 152, COR_CARD);

    tft.setTextColor(COR_TEXTO, COR_CARD);
    tft.drawString("Atual: " + String(atual, 1) + unid + " (Toque no grafico p/ trocar)", 22, 50, 1);

    // Linhas de grade horizontais
    tft.drawFastHLine(24, 75, 270, COR_BORDA);
    tft.drawFastHLine(24, 130, 270, COR_BORDA);
    tft.drawFastHLine(24, 180, 270, COR_BORDA);

    int n = totalPontosHistorico;
    if (n < 2) {
        int yMeio = 130;
        tft.drawFastHLine(25, yMeio, 260, corLinha);
    } else {
        for (int i = 0; i < n - 1; i++) {
            int x1 = 25 + (i * 10);
            int x2 = 25 + ((i + 1) * 10);
            float val1 = constrain(buffer[i], vMin, vMax);
            float val2 = constrain(buffer[i + 1], vMin, vMax);
            int y1 = 180 - (int)(((val1 - vMin) / (vMax - vMin)) * 105.0);
            int y2 = 180 - (int)(((val2 - vMin) / (vMax - vMin)) * 105.0);
            tft.drawLine(x1, y1, x2, y2, corLinha);
            tft.drawLine(x1, y1 + 1, x2, y2 + 1, corLinha);
            tft.fillCircle(x2, y2, 2, COR_TEXTO);
        }
    }
}

//=================================================
// GERENCIADOR CENTRAL DE RENDERIZAÇÃO
//=================================================
void atualizarDisplayCompleto() {
    if (telaAtual == SPLASH) {
        renderizarSplash();
        return;
    }
    if (graficoZoomAtivo) {
        renderizarGraficoZoom();
        return;
    }

    switch(telaAtual) {
        case HOME: renderizarHome(); break;
        case CLIMA: renderizarClima(); break;
        case DWC: renderizarDWC(); break;
        case CONTROLE: renderizarControle(); break;
        case SISTEMA: renderizarSistema(); break;
        default: break;
    }
}

// Atualiza apenas os cartões de dados no ciclo periódico (sem piscar a tela inteira)
void atualizarValoresDisplay() {
    if (telaAtual == SPLASH) return;
    if (graficoZoomAtivo) {
        renderizarGraficoZoom();
        return;
    }
    switch(telaAtual) {
        case HOME: desenharConteudoHome(); break;
        case CLIMA: desenharConteudoClima(); break;
        case DWC: desenharConteudoDWC(); break;
        case CONTROLE: desenharConteudoControle(); break;
        case SISTEMA: desenharConteudoSistema(); break;
        default: break;
    }
}

//=================================================
// INICIALIZAÇÃO DO DISPLAY E TOUCH (PAISAGEM 320x240)
//=================================================
void iniciarDisplay() {
    // 1. Desabilita todos os dispositivos SPI antes do boot para evitar conflito no barramento compartilhado
    pinMode(TFT_CS, OUTPUT);
    pinMode(TOUCH_CS, OUTPUT);
    pinMode(SD_CS, OUTPUT);
    digitalWrite(TFT_CS, HIGH);
    digitalWrite(TOUCH_CS, HIGH);
    digitalWrite(SD_CS, HIGH);
    delay(50);

    // 2. Inicializa o controlador gráfico (TPM408-2.8: 240x320 nativo)
    tft.init();
    tft.resetViewport();

    // 3. Limpa TODA a memória GRAM nativa (240x320 Retrato) ANTES de rotacionar
    //    Isso elimina definitivamente a faixa de 80px de ruído/lixo na borda!
    tft.setRotation(0);
    tft.fillScreen(COR_BG);

    // 4. Aplica orientação Paisagem completa (320x240): use ROTACAO_TELA = 1 (ou 3 se invertida)
    tft.setRotation(ROTACAO_TELA);
    tft.resetViewport();
    tft.fillScreen(COR_BG);

    // 5. Inicializa e alinha o Touchscreen XPT2046 na mesma orientação paisagem
    touch.begin();
    touch.setRotation(ROTACAO_TELA);

    Serial.print("IHM Touch TPM408-2.8 inicializada | Rotacao=");
    Serial.print(ROTACAO_TELA);
    Serial.print(" | Dimensoes ativas=");
    Serial.print(tft.width());
    Serial.print("x");
    Serial.print(tft.height());
    Serial.print(" | ChipID(0x04)=0x");
    Serial.println(tft.readcommand32(0x04), HEX);
}

//=================================================
// MOTOR DE LEITURA DO TOUCHSCREEN (PAISAGEM 320x240)
//=================================================
void atualizarDisplay() {
    if (touch.touched()) {
        TS_Point p = touch.getPoint();
        if (p.z < 200) return; // Ignora toques fantasmas / ruído elétrico

        // Mapeia coordenadas do XPT2046 (já rotacionado via touch.setRotation(ROTACAO_TELA)) para 320x240
        int x = TOUCH_INVERTER_X
            ? map(p.x, TOUCH_MAX_X, TOUCH_MIN_X, 0, 320)
            : map(p.x, TOUCH_MIN_X, TOUCH_MAX_X, 0, 320);
        int y = TOUCH_INVERTER_Y
            ? map(p.y, TOUCH_MAX_Y, TOUCH_MIN_Y, 0, 240)
            : map(p.y, TOUCH_MIN_Y, TOUCH_MAX_Y, 0, 240);

        x = constrain(x, 0, 319);
        y = constrain(y, 0, 239);
        
        // 1. Toque na Tela Splash / Iniciar Sistema
        if (telaAtual == SPLASH) {
            if (x > 60 && x < 260 && y > 115 && y < 170) {
                executarAnimacaoInicializacao();
                telaAtual = HOME;
                atualizarDisplayCompleto();
                enviarTelemetriaJSON();
                delay(250);
            }
            return;
        }

        // 2. Toque na Tela de Zoom do Gráfico
        if (graficoZoomAtivo) {
            if (x > 235 && x < 315 && y > 5 && y < 38) {
                graficoZoomAtivo = false;
                atualizarDisplayCompleto();
                delay(250);
            } else if (y > 42 && y < 198) {
                // Toque no meio do gráfico alterna entre Temp Ar, Umidade, pH e EC
                graficoSelecionado = (graficoSelecionado + 1) % 4;
                renderizarGraficoZoom();
                delay(250);
            }
            return;
        }

        // 3. Toque na Barra de Navegação Inferior
        if (y > 205) {
            if (x < 64) telaAtual = HOME;
            else if (x < 128) telaAtual = CLIMA;
            else if (x < 192) telaAtual = DWC;
            else if (x < 256) telaAtual = CONTROLE;
            else telaAtual = SISTEMA;
            
            graficoZoomAtivo = false;
            atualizarDisplayCompleto();
            delay(250);
            return;
        }

        // 4. Toque no Card de Cultura na Tela HOME (Alterna Alface <-> Manjericão)
        if (telaAtual == HOME) {
            if (x > 12 && x < 157 && y > 38 && y < 75) {
                alternarCultivoPadrao();
                atualizarDiagnostico();
                atualizarAutomacao();
                desenharConteudoHome();
                enviarTelemetriaJSON();
                delay(250);
                return;
            }
        }

        // 5. Zoom na Tela Clima
        if (telaAtual == CLIMA) {
            if (y > 38 && y < 198) {
                graficoZoomAtivo = true;
                graficoSelecionado = (x < 160) ? 0 : 1;
                renderizarGraficoZoom();
                delay(250);
                return;
            }
        }

        // 6. Zoom na Tela DWC (Card Nutriente)
        if (telaAtual == DWC) {
            if (x > 210 && y > 38 && y < 198) {
                graficoZoomAtivo = true;
                graficoSelecionado = (y < 120) ? 2 : 3;
                renderizarGraficoZoom();
                delay(250);
                return;
            }
        }

        // 7. Ações na Tela de Controle (Espelhamento Imediato com Gêmeo Digital)
        if (telaAtual == CONTROLE) {
            bool alterou = false;
            // Linha 1: Iluminação (y: 48..78)
            if (y >= 45 && y <= 82) {
                if (x >= 12 && x <= 104) { modoLuz = 0; alterou = true; }
                else if (x >= 112 && x <= 204) { modoLuz = 1; alterou = true; }
                else if (x >= 212 && x <= 308) { modoLuz = 2; alterou = true; }
            }
            // Linha 2: Exaustor (y: 101..131)
            else if (y >= 98 && y <= 135) {
                if (x >= 12 && x <= 104) { modoExaustor = 0; alterou = true; }
                else if (x >= 112 && x <= 204) { modoExaustor = 1; alterou = true; }
                else if (x >= 212 && x <= 308) { modoExaustor = 2; alterou = true; }
            }
            // Linha 3: Bomba Água (y: 154..184)
            else if (y >= 150 && y <= 188) {
                if (x >= 12 && x <= 104) { modoBombaAgua = 0; alterou = true; }
                else if (x >= 112 && x <= 204) { modoBombaAgua = 1; alterou = true; }
                else if (x >= 212 && x <= 308) { modoBombaAgua = 2; alterou = true; }
            }

            if (alterou) {
                atualizarAutomacao();
                desenharConteudoControle();
                enviarTelemetriaJSON();
                delay(200);
            }
        }
        
        // 8. Ações na Tela de Sistema (Calibração de pH e EC espelhada)
        else if (telaAtual == SISTEMA) {
            bool alterouCal = false;
            // Offset pH (y: 58..88)
            if (y >= 55 && y <= 92) {
                if (x >= 18 && x <= 62) { offsetPH -= 0.1; alterouCal = true; }
                else if (x >= 106 && x <= 152) { offsetPH += 0.1; alterouCal = true; }
            }
            // Ganho EC (y: 116..146)
            else if (y >= 112 && y <= 150) {
                if (x >= 18 && x <= 62) { fatorEC = max(0.1f, fatorEC - 0.05f); alterouCal = true; }
                else if (x >= 106 && x <= 152) { fatorEC = min(5.0f, fatorEC + 0.05f); alterouCal = true; }
            }

            if (alterouCal) {
                lerPH();
                lerEC();
                atualizarDiagnostico();
                desenharConteudoSistema();
                enviarTelemetriaJSON();
                delay(180);
            }
        }
    }
}

//=================================================
// TELA SPLASH INICIAL DO BOOT
//=================================================
void mostrarInicializacao() {
    telaAtual = SPLASH;
    atualizarDisplayCompleto();
}

#else

// Stubs leves quando USAR_DISPLAY_TFT == false (modo 100% Web App Wi-Fi / Serial)
inline void iniciarDisplay() {
    Serial.println("Display TFT desativado em config.h (modo headless Wi-Fi/Serial).");
}
inline void atualizarDisplay() {}
inline void atualizarDisplayCompleto() {}
inline void atualizarValoresDisplay() {}
inline void mostrarInicializacao() {}

#endif // USAR_DISPLAY_TFT

#endif