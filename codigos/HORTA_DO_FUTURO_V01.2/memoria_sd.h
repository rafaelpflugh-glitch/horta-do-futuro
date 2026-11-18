#ifndef MEMORIA_SD_H
#define MEMORIA_SD_H

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "config.h"
#include "dados.h"
#include "rtc.h"

void iniciarMemoria() {
    if (SD.begin(SD_CS)) {
        sdPronto = true;
        Serial.println("Cartao SD inicializado com sucesso.");
        if (!SD.exists("/telemetria.csv")) {
            File arq = SD.open("/telemetria.csv", FILE_WRITE);
            if (arq) {
                arq.println("Data,Hora,Cultura,Fase,Saude,TempAr,UmidAr,TempAgua,pH,EC,NivelOK,Luz,Exaustor,BombaAgua,BombaAr");
                arq.close();
            }
        }
    } else {
        sdPronto = false;
        Serial.println("Aviso: Cartao SD nao detectado no pino CS 15.");
    }
}

void registrarDados() {
    if (!sdPronto) return;

    File arq = SD.open("/telemetria.csv", FILE_APPEND);
    if (arq) {
        arq.print(obterData()); arq.print(",");
        arq.print(obterHora()); arq.print(",");
        arq.print(cultivoAtual.nome); arq.print(",");
        arq.print(cultivoAtual.fase); arq.print(",");
        arq.print(saudeCultivo); arq.print(",");
        arq.print(ambiente.temperaturaAr, 1); arq.print(",");
        arq.print(ambiente.umidadeAr, 1); arq.print(",");
        arq.print(solucao.temperaturaAgua, 1); arq.print(",");
        arq.print(solucao.ph, 2); arq.print(",");
        arq.print(solucao.ec, 2); arq.print(",");
        arq.print(solucao.nivelOK ? 1 : 0); arq.print(",");
        arq.print(atuadores.luz ? 1 : 0); arq.print(",");
        arq.print(atuadores.ventilador ? 1 : 0); arq.print(",");
        arq.print(atuadores.bombaAgua ? 1 : 0); arq.print(",");
        arq.println(atuadores.aeracao ? 1 : 0);
        arq.close();
    }
}

#endif
