#include <SPI.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#include "config.h"
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"
#include "display.h"
#include "sistema.h"

unsigned long ultimoCicloMs = 0;

void setup() {
  Serial.begin(115200);
  delay(300);

  // Inicializa o display, o touch, os sensores, relés e a tela de apresentação
  iniciarDisplay();
  iniciarSistema();
  mostrarInicializacao();
  ultimoCicloMs = millis();
}

void loop() {
  // 1. Leitura imediata do touchscreen e navegação fluida
  atualizarDisplay();

  // 2. Recepção instantânea de comandos JSON vindos do Gêmeo Digital (Python)
  receberComandosJSON();

  // 3. Ciclo periódico de leitura de sensores, automação DWC, display e telemetria JSON
  unsigned long agora = millis();
  if (agora - ultimoCicloMs >= INTERVALO_CICLO) {
    ultimoCicloMs = agora;
    executarCiclo();
  }
}