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

#endif
