#ifndef CONFIG_H
#define CONFIG_H

//=================================================
// HORTA DO FUTURO - CONFIGURAÇÃO GERAL V2.0
// ESP32 DevKit V1 (38 Pinos)
//=================================================

// 1. SENSORES GERAIS
#define PINO_DHT        4   // Temperatura e Umidade do Ar
#define PINO_DS18B20    13  // Temperatura da Água 
#define PINO_NIVEL      32  // Boia Magnética (Usa resistor Pull-up interno)
#define PINO_PH         34  // Entrada Analógica ADC1 (Somente leitura)
#define PINO_EC         35  // Entrada Analógica ADC1 (Somente leitura)

// 2. MÓDULO RTC DS3231 (I2C Padrão)
// SDA = 21, SCL = 22

// 3. TELA TFT & CARTÃO SD (SPI Padrão: SCK=18, MISO=19, MOSI=23)
#ifndef TFT_CS
#define TFT_CS          5   // Chip Select da Tela
#endif
#ifndef TFT_DC
#define TFT_DC          25  // Data/Command da Tela
#endif
#ifndef TFT_RST
#define TFT_RST         26  // Reset da Tela
#endif
#ifndef TOUCH_CS
#define TOUCH_CS        33  // Chip Select do Touch
#endif
#ifndef SD_CS
#define SD_CS           15  // Chip Select do Cartão SD
#endif
#define ROTACAO_TELA    1   // 1 = Paisagem 320x240 (use 3 se ficar de cabeça para baixo; NUNCA 0 ou 2)

// Calibração do Touchscreen XPT2046 (Modo Paisagem 320x240 - TPM408-2.8)
#define TOUCH_MIN_X      250
#define TOUCH_MAX_X      3800
#define TOUCH_MIN_Y      250
#define TOUCH_MAX_Y      3800
#define TOUCH_INVERTER_X false
#define TOUCH_INVERTER_Y false

// 4. ATUADORES (Módulo Relé Optoacoplado - Low Trigger)
#define RELE_BOMBA_AGUA 14  // Bomba Submersa (Timer de Circulação)
#define RELE_BOMBA_AR   16  // Oxigenador de Aquário (Contínuo)
#define RELE_LUZ        17  // Painel LED Grow
#define RELE_VENTILADOR 27  // Exaustor / Fan

// 5. PARÂMETROS PADRÃO (Para Inicialização)
#define PH_MIN_PADRAO           5.5
#define PH_MAX_PADRAO           6.5
#define EC_MIN_PADRAO           1.0
#define EC_MAX_PADRAO           1.8
#define TEMPERATURA_MIN_PADRAO  18.0
#define TEMPERATURA_MAX_PADRAO  26.0
#define TEMP_AGUA_MIN_PADRAO    18.0
#define TEMP_AGUA_MAX_PADRAO    26.0
#define UMIDADE_MIN_PADRAO      50.0
#define UMIDADE_MAX_PADRAO      80.0
#define HORAS_LUZ_PADRAO        16
#define BOMBA_ON_MIN_PADRAO     15
#define BOMBA_OFF_MIN_PADRAO    45

// 6. CONTROLE DO SISTEMA
#define INTERVALO_CICLO         2000UL // Roda o diagnóstico e telemetria a cada 2 segundos
#define HORA_INICIO_LUZ         6
#define TAMANHO_HISTORICO       26     // Pontos do gráfico na tela TFT

// 7. MODO DE OPERAÇÃO DOS SENSORES
#define MODO_SIMULACAO          false // false = Hardware real ativado!
#define SENSOR_PH_REAL_ATIVO    true  // true = Lê ADC pino 34 | false = valor fixo 6.0
#define SENSOR_EC_REAL_ATIVO    true  // true = Lê ADC pino 35 | false = valor fixo 1.4

// 8. DISPLAY TFT TOUCH (Defina false caso queira operar 100% via Web App Wi-Fi / Serial)
#define USAR_DISPLAY_TFT        true

// 9. REDE WI-FI & WEB APP / PWA EMBARCADO (Acesso simultâneo PC e Celular)
// Preencha com o Wi-Fi da sua casa ou deixe como está para iniciar direto no Modo AP reserva
#define WIFI_SSID               "SUA_REDE_WIFI"
#define WIFI_SENHA              "SUA_SENHA_WIFI"
#define WIFI_HOSTNAME           "horta"         // Endereço amigável: http://horta.local
#define WIFI_TIMEOUT_MS         12000UL         // Timeout (ms) tentando Wi-Fi antes de ativar AP reserva
#define AP_SSID                 "HortaDoFuturo" // Rede própria de reserva (http://192.168.4.1)
#define AP_SENHA                "horta2026"     // Senha do AP reserva (mínimo 8 caracteres)

#endif
