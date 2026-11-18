#ifndef FOTOPERIODO_H
#define FOTOPERIODO_H

#include "dados.h"

enum FaseCultivo {
    MUDA_FASE,
    VEGETATIVO,
    FLORACAO,
    PERSONALIZADO
};

FaseCultivo faseAtual = VEGETATIVO;
int horasLuz = 16;

void configurarFotoperiodo() {
    if (cultivoAtual.fase == "MUDA" || cultivoAtual.fase == "MUDAS") {
        faseAtual = MUDA_FASE;
    } else if (cultivoAtual.fase == "FLORACAO" || cultivoAtual.fase == "FLORA") {
        faseAtual = FLORACAO;
    } else {
        faseAtual = VEGETATIVO;
    }
    horasLuz = cultivoAtual.horasLuz;
}

#endif
