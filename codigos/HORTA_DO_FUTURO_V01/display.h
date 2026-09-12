#ifndef DISPLAY_H
#define DISPLAY_H

#include <SPI.h>
#include <TFT_eSPI.h>
#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"

// Inicializa o objeto da tela TFT
TFT_eSPI tft = TFT_eSPI();

// Controle de Telas (Total de 5 telas do sistema)
int telaAtual = 0;
const int TOTAL_TELAS = 5;

// Paleta de Cores Minimalista (RGB565)
#define COR_FUNDO       0x0000 // Preto
#define COR_TEXTO       0xFFFF // Branco
#define COR_DESTAQUE    0x07E0 // Verde Claro (Sucesso/OK)
#define COR_ALERTA      0xF800 // Vermelho (Erros/Baixo)
#define COR_TITULO      0x001F // Azul Claro (Cabeçalhos)
#define COR_CINZA       0x7BEF // Cinza para divisórias e textos secundários

//=================================================
// INICIALIZAÇÃO
//=================================================
void iniciarDisplay() {
    tft.init();
    tft.setRotation(0); // Modo Retrato
    tft.fillScreen(COR_FUNDO);
    
    Serial.println("Display TFT Touch (Minimalista) inicializado.");
}

//=================================================
// TELA DE INICIALIZAÇÃO (SPLASH)
//=================================================
void mostrarInicializacao() {
    tft.fillScreen(COR_FUNDO);
    
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.setTextSize(3);
    tft.setCursor(25, 80);
    tft.println("HORTA");
    
    tft.setCursor(25, 115);
    tft.setTextColor(COR_DESTAQUE, COR_FUNDO);
    tft.println("DO FUTURO");
    
    tft.setTextSize(1);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setCursor(25, 180);
    tft.println("Computador de Plantas V1.0");
}

//=================================================
// 1. TELA PRINCIPAL (DASHBOARD)
//=================================================
void telaPrincipal() {
    tft.fillScreen(COR_FUNDO);

    // Cabeçalho Minimalista
    tft.setTextColor(COR_TITULO, COR_FUNDO);
    tft.setTextSize(2);
    tft.setCursor(10, 10);
    tft.println("DASHBOARD");
    
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setTextSize(1);
    tft.setCursor(175, 15);
    tft.println(obterHora());

    tft.drawFastHLine(0, 35, 240, COR_CINZA);

    // Cultivo Ativo
    tft.setCursor(10, 48);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.print("PLANTA: ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.println(cultivoAtual.nome);

    // Saúde do Cultivo (Índice Central)
    tft.setCursor(10, 80);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.println("SAUDE DO SISTEMA");
    
    tft.setTextSize(3);
    tft.setCursor(10, 100);
    if(saudeCultivo > 70) {
        tft.setTextColor(COR_DESTAQUE, COR_FUNDO);
    } else {
        tft.setTextColor(COR_ALERTA, COR_FUNDO);
    }
    tft.print(saudeCultivo);
    tft.println("%");

    // Status Atuadores (Rodapé da tela)
    tft.setTextSize(1);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.drawFastHLine(0, 160, 240, COR_CINZA);
    
    tft.setCursor(10, 175);
    tft.print("Luz (Rele 1): ");
    tft.setTextColor(atuadores.luz ? COR_DESTAQUE : COR_ALERTA, COR_FUNDO);
    tft.println(atuadores.luz ? "ON " : "OFF");

    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setCursor(10, 200);
    tft.print("Bomba Ar (Rele 3): ");
    tft.setTextColor(atuadores.aeracao ? COR_DESTAQUE : COR_ALERTA, COR_FUNDO);
    tft.println(atuadores.aeracao ? "ON " : "OFF");
}

//=================================================
// 2. TELA AMBIENTE (AR)
//=================================================
void telaAmbiente() {
    tft.fillScreen(COR_FUNDO);

    tft.setTextColor(COR_TITULO, COR_FUNDO);
    tft.setTextSize(2);
    tft.setCursor(10, 10);
    tft.println("CLIMA DO AR");
    tft.drawFastHLine(0, 35, 240, COR_CINZA);

    tft.setTextSize(1);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setCursor(10, 60);
    tft.println("TEMPERATURA DO AR");
    
    tft.setTextSize(2);
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.setCursor(10, 80);
    tft.print(ambiente.temperaturaAr, 1);
    tft.println(" C");

    tft.setTextSize(1);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setCursor(10, 130);
    tft.println("UMIDADE RELATIVA");
    
    tft.setTextSize(2);
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.setCursor(10, 150);
    tft.print(ambiente.umidadeAr, 1);
    tft.println(" %");
}

//=================================================
// 3. TELA SOLUÇÃO DWC
//=================================================
void telaSolucao() {
    tft.fillScreen(COR_FUNDO);

    tft.setTextColor(COR_TITULO, COR_FUNDO);
    tft.setTextSize(2);
    tft.setCursor(10, 10);
    tft.println("SOLUCAO DWC");
    tft.drawFastHLine(0, 35, 240, COR_CINZA);

    tft.setTextSize(1);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setCursor(10, 50);
    tft.print("Temp Agua: ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.print(solucao.temperaturaAgua, 1);
    tft.println(" C");

    tft.setCursor(10, 85);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.print("pH Atual:  ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.print(solucao.ph, 2);
    tft.println("");

    tft.setCursor(10, 120);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.print("EC Atual:  ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.print(solucao.ec, 2);
    tft.println(" mS/cm");

    tft.setCursor(10, 155);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.print("Nivel Agua: ");
    tft.setTextColor(solucao.nivelOK ? COR_DESTAQUE : COR_ALERTA, COR_FUNDO);
    tft.println(solucao.nivelOK ? "OK" : "BAIXO");
}

//=================================================
// 4. TELA DE ALERTAS
//=================================================
void telaAlertas() {
    tft.fillScreen(COR_FUNDO);

    tft.setTextColor(COR_ALERTA, COR_FUNDO);
    tft.setTextSize(2);
    tft.setCursor(10, 10);
    tft.println("DIAGNOSTICO");
    tft.drawFastHLine(0, 35, 240, COR_CINZA);

    tft.setTextSize(1);
    int linha = 55;

    if(alertas.phBaixo) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- pH ABAIXO DO IDEAL"); linha += 20; }
    if(alertas.phAlto) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- pH ACIMA DO IDEAL"); linha += 20; }
    if(alertas.ecBaixo) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- EC ABAIXO DO IDEAL"); linha += 20; }
    if(alertas.ecAlto) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- EC ACIMA DO IDEAL"); linha += 20; }
    if(alertas.temperaturaAlta) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- TEMPERATURA ALTA"); linha += 20; }
    if(alertas.umidadeAlta) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- UMIDADE ALTA"); linha += 20; }
    if(alertas.nivelBaixo) { tft.setTextColor(COR_ALERTA, COR_FUNDO); tft.setCursor(10, linha); tft.println("- NIVEL DE AGUA BAIXO!"); linha += 20; }

    if(!alertas.phBaixo && !alertas.phAlto && !alertas.ecBaixo && !alertas.ecAlto && 
       !alertas.temperaturaAlta && !alertas.umidadeAlta && !alertas.nivelBaixo) {
        tft.setTextColor(COR_DESTAQUE, COR_FUNDO);
        tft.setCursor(10, 80);
        tft.println("Tudo operando normalmente.");
    }
}

//=================================================
// 5. TELA DE SISTEMA
//=================================================
void telaSistema() {
    tft.fillScreen(COR_FUNDO);

    tft.setTextColor(COR_TITULO, COR_FUNDO);
    tft.setTextSize(2);
    tft.setCursor(10, 10);
    tft.println("INFO SISTEMA");
    tft.drawFastHLine(0, 35, 240, COR_CINZA);

    tft.setTextSize(1);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.setCursor(10, 60);
    tft.print("Arquitetura: ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.println("ESP32 V1");

    tft.setCursor(10, 95);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.print("Fotoperiodo: ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.print(cultivoAtual.horasLuz);
    tft.println("h diarios");

    tft.setCursor(10, 130);
    tft.setTextColor(COR_CINZA, COR_FUNDO);
    tft.print("Modo Log: ");
    tft.setTextColor(COR_TEXTO, COR_FUNDO);
    tft.println("Cartão SD / CSV");
}

//=================================================
// ATUALIZAÇÃO DA TELA ATIVA
//=================================================
void atualizarDisplay() {
    switch(telaAtual) {
        case 0: telaPrincipal(); break;
        case 1: telaAmbiente(); break;
        case 2: telaSolucao(); break;
        case 3: telaAlertas(); break;
        case 4: telaSistema(); break;
    }
}

//=================================================
// CONTROLE DE NAVEGAÇÃO TOUCH / BOTÃO
//=================================================
void proximaTela() {
    telaAtual++;
    if(telaAtual >= TOTAL_TELAS) {
        telaAtual = 0;
    }
}

void telaAnterior() {
    telaAtual--;
    if(telaAtual < 0) {
        telaAtual = TOTAL_TELAS - 1;
    }
}

#endif