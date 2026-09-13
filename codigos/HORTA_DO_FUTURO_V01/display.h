#ifndef DISPLAY_H
#define DISPLAY_H

#include <SPI.h>
#include <TFT_eSPI.h>
#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"

TFT_eSPI tft = TFT_eSPI();

//=================================================
// PALETA DE CORES DARK THEME (RGB565)
//=================================================
#define COR_BG          0x0821  // Grafite Escuro (#0B0E14)
#define COR_CARD        0x18C5  // Cinza Chumbo
#define COR_BORDA       0x2969  // Borda sutil
#define COR_TEXTO       0xFFFF  // Branco
#define COR_SUBTEXTO    0x9E3B  // Cinza Claro
#define COR_VERDE       0x07E0  // Verde Sucesso
#define COR_AZUL        0x2CDF  // Azul Destaque
#define COR_ALERTA      0xF800  // Vermelho
#define COR_NAV         0x0000  // Preto (Barra Inferior)

//=================================================
// ESTADOS DA INTERFACE
//=================================================
enum TelaTFT { HOME, CLIMA, DWC, CONTROLE, SISTEMA };
TelaTFT telaAtual = HOME;

float offsetPH = 0.0; // Usado na tela de calibração

//=================================================
// FUNÇÕES DE DESENHO AUXILIARES
//=================================================
void desenharBotao(int x, int y, int w, int h, String texto, uint16_t corBase, uint16_t corTexto) {
    tft.fillRoundRect(x, y, w, h, 5, corBase);
    tft.drawRoundRect(x, y, w, h, 5, COR_BORDA);
    tft.setTextColor(corTexto);
    tft.setTextDatum(MC_DATUM); // Centraliza
    tft.drawString(texto, x + (w/2), y + (h/2), 2); // Fonte 2
    tft.setTextDatum(TL_DATUM); // Retorna ao padrão Top-Left
}

//=================================================
// BARRA DE NAVEGAÇÃO INFERIOR (FIXA)
//=================================================
void desenharNavBar() {
    tft.fillRect(0, 280, 240, 40, COR_NAV);
    tft.drawFastHLine(0, 280, 240, COR_BORDA);

    // 5 Botões de 48px de largura
    uint16_t c0 = (telaAtual == HOME) ? COR_AZUL : COR_NAV;
    uint16_t c1 = (telaAtual == CLIMA) ? COR_AZUL : COR_NAV;
    uint16_t c2 = (telaAtual == DWC) ? COR_AZUL : COR_NAV;
    uint16_t c3 = (telaAtual == CONTROLE) ? COR_AZUL : COR_NAV;
    uint16_t c4 = (telaAtual == SISTEMA) ? COR_AZUL : COR_NAV;

    desenharBotao(2,   285, 44, 30, "HM", c0, COR_TEXTO);
    desenharBotao(50,  285, 44, 30, "CL", c1, COR_TEXTO);
    desenharBotao(98,  285, 44, 30, "AQ", c2, COR_TEXTO);
    desenharBotao(146, 285, 44, 30, "PW", c3, COR_TEXTO);
    desenharBotao(194, 285, 44, 30, "CF", c4, COR_TEXTO);
}

//=================================================
// 1. TELA HOME (DASHBOARD)
//=================================================
void renderizarHome() {
    tft.fillScreen(COR_BG);
    
    // Cabeçalho
    tft.setTextColor(COR_AZUL);
    tft.drawString("HORTA DO FUTURO", 10, 10, 2);
    tft.setTextColor(COR_TEXTO);
    tft.drawString(obterHora(), 180, 10, 2);

    // Cultura Atual
    tft.fillRoundRect(10, 35, 220, 35, 5, COR_CARD);
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("CULTURA:", 20, 45, 2);
    tft.setTextColor(COR_VERDE);
    tft.drawString(cultivoAtual.nome, 90, 45, 2);

    // Saúde Biológica
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("SAUDE BIOLOGICA", 10, 85, 2);
    uint16_t corSaude = (saudeCultivo > 70) ? COR_VERDE : COR_ALERTA;
    tft.drawRoundRect(10, 105, 220, 20, 4, COR_BORDA);
    tft.fillRoundRect(12, 107, map(saudeCultivo, 0, 100, 0, 216), 16, 2, corSaude);
    tft.setTextColor(corSaude);
    tft.drawString(String(saudeCultivo) + "%", 100, 130, 2);

    // Resumo Rápido
    tft.setTextColor(COR_TEXTO);
    tft.drawString("Temp Ar: " + String(ambiente.temperaturaAr, 1) + "C", 10, 170, 2);
    tft.drawString("pH Agua: " + String(solucao.ph, 2), 10, 195, 2);
    tft.drawString("Luz: " + String(atuadores.luz ? "ON" : "OFF"), 10, 220, 2);
    
    desenharNavBar();
}

//=================================================
// 2. TELA CLIMA (AR)
//=================================================
void renderizarClima() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL);
    tft.drawString("CLIMA & AR", 10, 10, 2);

    tft.fillRoundRect(10, 40, 220, 80, 5, COR_CARD);
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("TEMPERATURA", 20, 50, 2);
    tft.setTextColor(alertas.temperaturaAlta ? COR_ALERTA : COR_VERDE);
    tft.drawString(String(ambiente.temperaturaAr, 1) + " C", 20, 75, 4);

    tft.fillRoundRect(10, 130, 220, 80, 5, COR_CARD);
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("UMIDADE", 20, 140, 2);
    tft.setTextColor(alertas.umidadeAlta ? COR_ALERTA : COR_VERDE);
    tft.drawString(String(ambiente.umidadeAr, 0) + " %", 20, 165, 4);

    desenharNavBar();
}

//=================================================
// 3. TELA DWC (SOLUÇÃO)
//=================================================
void renderizarDWC() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL);
    tft.drawString("RESERVATORIO DWC", 10, 10, 2);

    // Card de Nível
    tft.fillRoundRect(10, 40, 105, 110, 5, COR_CARD);
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("NIVEL", 20, 50, 2);
    tft.setTextColor(solucao.nivelOK ? COR_VERDE : COR_ALERTA);
    tft.drawString(solucao.nivelOK ? "OK" : "BAIXO", 20, 80, 4);

    // Card Temp Água
    tft.fillRoundRect(125, 40, 105, 110, 5, COR_CARD);
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("TEMP", 135, 50, 2);
    tft.setTextColor(COR_TEXTO);
    tft.drawString(String(solucao.temperaturaAgua, 1), 135, 80, 4);

    // Card Química (pH e EC)
    tft.fillRoundRect(10, 160, 220, 100, 5, COR_CARD);
    tft.setTextColor(COR_TEXTO);
    tft.drawString("pH: " + String(solucao.ph, 2), 20, 180, 4);
    tft.drawString("EC: " + String(solucao.ec, 1), 20, 215, 4);

    desenharNavBar();
}

//=================================================
// 4. TELA CONTROLE (MANUAL & RELES)
//=================================================
void renderizarControle() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL);
    tft.drawString("CONTROLE MANUAL", 10, 10, 2);

    // Chave Seletora de Iluminação
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("ILUMINACAO (REL 1):", 10, 40, 2);
    desenharBotao(10,  65, 70, 40, "AUTO", (modoLuz==0)?COR_AZUL:COR_CARD, COR_TEXTO);
    desenharBotao(85,  65, 70, 40, "ON",   (modoLuz==1)?COR_VERDE:COR_CARD, COR_TEXTO);
    desenharBotao(160, 65, 70, 40, "OFF",  (modoLuz==2)?COR_ALERTA:COR_CARD, COR_TEXTO);

    // Toggles
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("EXAUSTOR (REL 2):", 10, 125, 2);
    desenharBotao(10, 150, 105, 40, "AUTO", COR_VERDE, COR_BG);
    desenharBotao(125, 150, 100, 40, "FORCE ON", COR_CARD, COR_TEXTO);

    tft.drawString("AERACAO (REL 3):", 10, 205, 2);
    desenharBotao(10, 230, 215, 40, atuadores.aeracao ? "LIGADO" : "DESLIGADO", atuadores.aeracao ? COR_VERDE : COR_ALERTA, COR_BG);

    desenharNavBar();
}

//=================================================
// 5. TELA SISTEMA & CALIBRAÇÃO
//=================================================
void renderizarSistema() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL);
    tft.drawString("SISTEMA & CALIBRACAO", 10, 10, 2);

    tft.fillRoundRect(10, 40, 220, 110, 5, COR_CARD);
    tft.setTextColor(COR_TEXTO);
    tft.drawString("Calibracao pH Offset", 20, 50, 2);
    
    // Botões de Ajuste (+ e -)
    desenharBotao(20, 80, 50, 50, "-", COR_BG, COR_TEXTO);
    tft.setTextDatum(MC_DATUM);
    tft.setTextColor(COR_VERDE);
    tft.drawString(String(offsetPH, 1), 120, 105, 4);
    tft.setTextDatum(TL_DATUM);
    desenharBotao(170, 80, 50, 50, "+", COR_BG, COR_TEXTO);

    // Terminal Simulado
    tft.setTextColor(COR_SUBTEXTO);
    tft.drawString("LOG DE EVENTOS:", 10, 170, 1);
    tft.setTextColor(COR_TEXTO);
    tft.drawString("> ESP32 Boot OK", 10, 190, 1);
    tft.drawString("> WiFi Desconectado", 10, 205, 1);
    tft.drawString("> Modulo SD Preparado", 10, 220, 1);

    desenharNavBar();
}

//=================================================
// GERENCIADOR CENTRAL DE RENDERIZAÇÃO
//=================================================
void atualizarDisplayCompleto() {
    switch(telaAtual) {
        case HOME: renderizarHome(); break;
        case CLIMA: renderizarClima(); break;
        case DWC: renderizarDWC(); break;
        case CONTROLE: renderizarControle(); break;
        case SISTEMA: renderizarSistema(); break;
    }
}

//=================================================
// INICIALIZAÇÃO
//=================================================
void iniciarDisplay() {
    tft.init();
    tft.setRotation(0);
    
    // Ajuste aqui a calibração real do seu touch quando montar
    uint16_t calData[5] = { 275, 3600, 305, 3400, 7 };
    tft.setTouch(calData);
    
    Serial.println("IHM Touch V1 inicializada.");
}

//=================================================
// LOOP DE LEITURA DO TOUCHSCREEN
//=================================================
void atualizarDisplay() {
    uint16_t x, y;
    bool tocado = tft.getTouch(&x, &y);
    
    if (tocado) {
        // 1. ZONA DE NAVEGAÇÃO (Y > 280)
        if (y > 280) {
            if (x < 48) telaAtual = HOME;
            else if (x < 96) telaAtual = CLIMA;
            else if (x < 144) telaAtual = DWC;
            else if (x < 192) telaAtual = CONTROLE;
            else telaAtual = SISTEMA;
            
            atualizarDisplayCompleto();
            delay(250); // Debounce
            return;
        }

        // 2. ZONAS ESPECÍFICAS DE CADA TELA
        if (telaAtual == CONTROLE) {
            if (y > 65 && y < 105) {
                if (x > 10 && x < 80) modoLuz = 0;
                else if (x > 85 && x < 155) modoLuz = 1;
                else if (x > 160 && x < 230) modoLuz = 2;
                atualizarDisplayCompleto();
                delay(200);
            }
        }
        else if (telaAtual == SISTEMA) {
            if (y > 80 && y < 130) {
                if (x > 20 && x < 70) { offsetPH -= 0.1; atualizarDisplayCompleto(); delay(150); }
                else if (x > 170 && x < 220) { offsetPH += 0.1; atualizarDisplayCompleto(); delay(150); }
            }
        }
    }
}

// Tela splash
void mostrarInicializacao() {
    tft.fillScreen(COR_BG);
    tft.setTextColor(COR_AZUL);
    tft.setTextDatum(MC_DATUM);
    tft.drawString("HORTA DO FUTURO", 120, 140, 4);
    tft.setTextColor(COR_TEXTO);
    tft.drawString("Carregando Sistema...", 120, 180, 2);
    tft.setTextDatum(TL_DATUM);
    delay(1000);
    atualizarDisplayCompleto();
}

#endif