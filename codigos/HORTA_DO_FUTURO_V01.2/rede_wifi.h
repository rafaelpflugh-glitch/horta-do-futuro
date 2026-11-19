#ifndef REDE_WIFI_H
#define REDE_WIFI_H

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <SD.h>
#include <ArduinoJson.h>
#include "config.h"
#include "dados.h"
#include "sistema.h"
#include "web_ui.h"

WebServer servidorWeb(80);
Preferences prefsWifi;

unsigned long ultimoCheckWifiMs = 0;

void adicionarHeadersCORS() {
    servidorWeb.sendHeader("Access-Control-Allow-Origin", "*");
    servidorWeb.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    servidorWeb.sendHeader("Access-Control-Allow-Headers", "Content-Type");
}

void iniciarModoAPReserva() {
    WiFi.disconnect(true);
    delay(100);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_SENHA);

    wifiConectado = false;
    wifiModoAP = true;
    ipLocal = WiFi.softAPIP().toString();

    Serial.println("=================================================");
    Serial.println("WI-FI EM MODO ACCESS POINT RESERVA (INDEPENDENTE)");
    Serial.print("Rede Wi-Fi : "); Serial.println(AP_SSID);
    Serial.print("Senha      : "); Serial.println(AP_SENHA);
    Serial.print("Acesse em  : http://"); Serial.println(ipLocal);
    Serial.println("=================================================");
}

void configurarRotasWeb() {
    // 1. Página principal (Web App / PWA Responsivo PC + Celular)
    servidorWeb.on("/", HTTP_GET, []() {
        servidorWeb.send_P(200, "text/html; charset=utf-8", INDEX_HTML);
    });

    // 2. Recursos PWA (Manifest e Ícone SVG offline)
    servidorWeb.on("/manifest.json", HTTP_GET, []() {
        servidorWeb.send_P(200, "application/manifest+json; charset=utf-8", MANIFEST_JSON);
    });

    servidorWeb.on("/icon.svg", HTTP_GET, []() {
        servidorWeb.send_P(200, "image/svg+xml", ICON_SVG);
    });

    // 3. API Telemetria ao Vivo (mesmas chaves JSON da Serial)
    servidorWeb.on("/api/status", HTTP_GET, []() {
        adicionarHeadersCORS();
        servidorWeb.sendHeader("Cache-Control", "no-store");
        servidorWeb.send(200, "application/json; charset=utf-8", gerarTelemetriaJSON());
    });

    // 4. API Histórico Circular (para preencher os gráficos instantaneamente)
    servidorWeb.on("/api/history", HTTP_GET, []() {
        adicionarHeadersCORS();
        servidorWeb.sendHeader("Cache-Control", "no-store");
        servidorWeb.send(200, "application/json; charset=utf-8", gerarHistoricoJSON());
    });

    // 5. API Comandos Bidirecionais (mesmo protocolo JSON do Gêmeo Digital)
    servidorWeb.on("/api/cmd", HTTP_OPTIONS, []() {
        adicionarHeadersCORS();
        servidorWeb.send(204);
    });

    servidorWeb.on("/api/cmd", HTTP_POST, []() {
        adicionarHeadersCORS();
        if (!servidorWeb.hasArg("plain")) {
            servidorWeb.send(400, "application/json", "{\"ok\":false,\"erro\":\"Corpo JSON ausente\"}");
            return;
        }
        String corpo = servidorWeb.arg("plain");
        bool ok = processarComandoJSON(corpo, false);
        if (ok) {
            servidorWeb.send(200, "application/json; charset=utf-8", gerarTelemetriaJSON());
        } else {
            servidorWeb.send(400, "application/json", "{\"ok\":false,\"erro\":\"Comando JSON invalido\"}");
        }
    });

    // 6. API Salvar Credenciais Wi-Fi na memória NVS do ESP32
    servidorWeb.on("/api/wifi", HTTP_OPTIONS, []() {
        adicionarHeadersCORS();
        servidorWeb.send(204);
    });

    servidorWeb.on("/api/wifi", HTTP_POST, []() {
        adicionarHeadersCORS();
        if (!servidorWeb.hasArg("plain")) {
            servidorWeb.send(400, "application/json", "{\"ok\":false}");
            return;
        }
#if ARDUINOJSON_VERSION_MAJOR >= 7
        JsonDocument doc;
#else
        StaticJsonDocument<512> doc;
#endif
        if (deserializeJson(doc, servidorWeb.arg("plain"))) {
            servidorWeb.send(400, "application/json", "{\"ok\":false}");
            return;
        }

        prefsWifi.begin("horta_wifi", false);
        if (doc["reset"] | false) {
            prefsWifi.clear();
            prefsWifi.end();
            servidorWeb.send(200, "application/json", "{\"ok\":true,\"reset\":true}");
            return;
        }

        String novoSsid = doc["ssid"] | "";
        String novaSenha = doc["senha"] | "";
        novoSsid.trim();

        if (novoSsid.length() == 0) {
            prefsWifi.end();
            servidorWeb.send(400, "application/json", "{\"ok\":false,\"erro\":\"SSID vazio\"}");
            return;
        }

        prefsWifi.putString("ssid", novoSsid);
        prefsWifi.putString("senha", novaSenha);
        prefsWifi.end();

        servidorWeb.send(200, "application/json", "{\"ok\":true}");
    });

    // 7. API Reiniciar ESP32
    servidorWeb.on("/api/reboot", HTTP_POST, []() {
        adicionarHeadersCORS();
        servidorWeb.send(200, "application/json", "{\"ok\":true}");
        delay(350);
        ESP.restart();
    });

    // 8. API Download direto do arquivo CSV do Cartão SD
    servidorWeb.on("/api/csv", HTTP_GET, []() {
        if (!sdPronto || !SD.exists("/telemetria.csv")) {
            servidorWeb.send(404, "text/plain", "Cartao SD nao detectado ou arquivo telemetria.csv ausente.");
            return;
        }
        File arq = SD.open("/telemetria.csv", FILE_READ);
        if (!arq) {
            servidorWeb.send(500, "text/plain", "Falha ao abrir /telemetria.csv");
            return;
        }
        servidorWeb.sendHeader("Content-Disposition", "attachment; filename=\"horta_telemetria_sd.csv\"");
        servidorWeb.streamFile(arq, "text/csv");
        arq.close();
    });

    // Fallback para rotas desconhecidas / preflight CORS
    servidorWeb.onNotFound([]() {
        if (servidorWeb.method() == HTTP_OPTIONS) {
            adicionarHeadersCORS();
            servidorWeb.send(204);
            return;
        }
        servidorWeb.sendHeader("Location", "/");
        servidorWeb.send(302, "text/plain", "");
    });
}

void iniciarRedeWiFi() {
    // 1. Verifica se existem credenciais salvas na memória NVS (via Web App)
    prefsWifi.begin("horta_wifi", true);
    String ssidAlvo = prefsWifi.getString("ssid", "");
    String senhaAlvo = prefsWifi.getString("senha", "");
    prefsWifi.end();

    // 2. Se não houver na NVS, usa o config.h (desde que o usuário tenha preenchido)
    if (ssidAlvo.length() == 0) {
        String ssidCfg = String(WIFI_SSID);
        if (ssidCfg.length() > 0 && ssidCfg != "SUA_REDE_WIFI") {
            ssidAlvo = ssidCfg;
            senhaAlvo = String(WIFI_SENHA);
        }
    }

    if (ssidAlvo.length() > 0) {
        Serial.print("Conectando ao Wi-Fi: ");
        Serial.println(ssidAlvo);

        WiFi.mode(WIFI_STA);
        WiFi.setHostname(WIFI_HOSTNAME);
        WiFi.setAutoReconnect(true);
        WiFi.begin(ssidAlvo.c_str(), senhaAlvo.c_str());

        unsigned long inicio = millis();
        while (WiFi.status() != WL_CONNECTED && (millis() - inicio) < WIFI_TIMEOUT_MS) {
            delay(250);
            Serial.print(".");
        }
        Serial.println();

        if (WiFi.status() == WL_CONNECTED) {
            wifiConectado = true;
            wifiModoAP = false;
            ipLocal = WiFi.localIP().toString();

            Serial.println("=================================================");
            Serial.println("WI-FI CONECTADO COM SUCESSO!");
            Serial.print("Acesse no PC/Celular : http://"); Serial.println(ipLocal);
            if (MDNS.begin(WIFI_HOSTNAME)) {
                MDNS.addService("http", "tcp", 80);
                Serial.print("Endereco amigavel    : http://");
                Serial.print(WIFI_HOSTNAME);
                Serial.println(".local");
            }
            Serial.println("=================================================");
        } else {
            Serial.println("Timeout no Wi-Fi domestico. Ativando Modo AP reserva...");
            iniciarModoAPReserva();
        }
    } else {
        Serial.println("Wi-Fi domestico nao configurado. Iniciando Modo AP reserva...");
        iniciarModoAPReserva();
    }

    configurarRotasWeb();
    servidorWeb.begin();
    Serial.println("Servidor Web/PWA da Horta do Futuro ativo na porta 80.");
    ultimoCheckWifiMs = millis();
}

void atualizarRedeWiFi() {
    servidorWeb.handleClient();

    unsigned long agora = millis();
    if (!wifiModoAP && (agora - ultimoCheckWifiMs >= 15000UL)) {
        ultimoCheckWifiMs = agora;
        bool conectadoAgora = (WiFi.status() == WL_CONNECTED);
        wifiConectado = conectadoAgora;
        if (conectadoAgora) {
            ipLocal = WiFi.localIP().toString();
        }
    }
}

#endif
