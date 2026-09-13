/*
=====================================================
              HORTA DO FUTURO
        COMPUTADOR DE PLANTAS
        Firmware V1.0
        ESP32 DevKit V1
=====================================================
*/

#include "sistema.h"
#include "display.h"

//=====================================================
// CONTROLE DE TEMPO
//=====================================================
unsigned long ultimoCiclo = 0;

//=====================================================
// SETUP
//=====================================================
void setup() {
    Serial.begin(115200);
    delay(500);

    Serial.println();
    Serial.println("================================");
    Serial.println("        HORTA DO FUTURO");
    Serial.println("      COMPUTADOR DE PLANTAS");
    Serial.println("          Firmware V1.0");
    Serial.println("================================");

    iniciarSistema();
    iniciarDisplay();
    mostrarInicializacao();

    delay(1500);
    estadoAtual = MONITORAMENTO;
}

//=====================================================
// LOOP
//=====================================================
void loop() {
    unsigned long agora = millis();

    if (agora - ultimoCiclo >= INTERVALO_CICLO) {
        ultimoCiclo = agora;
        executarCiclo();
    }

    // O touch interativo e o render são atualizados aqui
    atualizarInterface(); 
}