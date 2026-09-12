#ifndef CONFIG_H
#define CONFIG_H

//=================================================
// HORTA DO FUTURO - CONFIGURAÇÃO GERAL V1.0
// ESP32 DevKit V1 (38 Pinos)
//=================================================

// SENSORES
#define PINO_DHT       4
#define PINO_DS18B20   5
#define PINO_PH        34  // Porta Analógica (ADC)
#define PINO_EC        35  // Porta Analógica (ADC) - Futuro
#define PINO_NIVEL     27  // Porta Digital (Boia)

// ATUADORES (Relés)
#define RELE_LUZ          16
#define RELE_VENTILADOR   17
#define RELE_BOMBA        26

// PARÂMETROS PADRÃO ALFACE
#define PH_MIN_PADRAO             5.5
#define PH_MAX_PADRAO             6.5
#define EC_MIN_PADRAO             1.0
#define EC_MAX_PADRAO             1.8
#define TEMPERATURA_MIN_PADRAO    18.0
#define TEMPERATURA_MAX_PADRAO    26.0
#define UMIDADE_MIN_PADRAO        50.0
#define UMIDADE_MAX_PADRAO        80.0
#define HORAS_LUZ_PADRAO          16

// CONTROLE DO SISTEMA
#define INTERVALO_CICLO           2000UL
#define HORA_INICIO_LUZ           6

// MODO DE OPERAÇÃO
#define MODO_SIMULACAO            false // Alterado para false: Sensores Reais ativados!

#endif