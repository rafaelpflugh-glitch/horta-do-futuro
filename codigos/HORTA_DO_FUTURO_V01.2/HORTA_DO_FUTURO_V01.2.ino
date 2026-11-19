#include <SPI.h>
#include "config.h"
#if USAR_DISPLAY_TFT
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#endif
#include "dados.h"
#include "cultivo.h"
#include "rtc.h"
#include "display.h"
#include "sistema.h"
#include "web_ui.h"
#include "rede_wifi.h"

unsigned long ultimoCicloMs = 0;

void setup() {
  Serial.begin(115200);
  delay(300);

  // 1. Inicializa o display TFT (se USAR_DISPLAY_TFT == true) e exibe tela inicial
  iniciarDisplay();
  mostrarInicializacao();

  // 2. Inicializa cultivo, RTC, sensores, diagnóstico, automação DWC e SD (fail-safe)
  iniciarSistema();

  // 3. Conecta ao Wi-Fi de casa (horta.local) ou abre Modo AP reserva (HortaDoFuturo)
  iniciarRedeWiFi();

  ultimoCicloMs = millis();
}

void loop() {
  // 1. Atendimento instantâneo do Web App / PWA via Wi-Fi (PC e Celular)
  atualizarRedeWiFi();

  // 2. Leitura imediata do touchscreen e navegação fluida no TFT
  atualizarDisplay();

  // 3. Recepção instantânea de comandos JSON vindos do Gêmeo Digital (USB Serial)
  receberComandosJSON();

  // 4. Ciclo periódico de leitura de sensores, automação DWC, display e telemetria JSON
  unsigned long agora = millis();
  if (agora - ultimoCicloMs >= INTERVALO_CICLO) {
    ultimoCicloMs = agora;
    executarCiclo();
  }
}
