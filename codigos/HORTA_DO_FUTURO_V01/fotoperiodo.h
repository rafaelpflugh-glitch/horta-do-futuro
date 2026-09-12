#ifndef FOTOPERIODO_H
#define FOTOPERIODO_H



/*
=================================================

FOTOPERÍODO

Controle do ciclo da luz.

=================================================
*/



enum FaseCultivo
{

VEGETATIVO,

FLORACAO,

PERSONALIZADO

};



FaseCultivo faseAtual =
VEGETATIVO;



int horasLuz;



void configurarFotoperiodo()
{


switch(faseAtual)
{


case VEGETATIVO:


horasLuz = 16;

break;



case FLORACAO:


horasLuz = 12;

break;



case PERSONALIZADO:


horasLuz = 14;

break;



}



}



#endif