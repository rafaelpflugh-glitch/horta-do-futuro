#ifndef SENSOR_EC_H
#define SENSOR_EC_H


/*
====================================================

HORTA DO FUTURO

MÓDULO EC/TDS

Mede concentração
da solução nutritiva.


====================================================
*/


#include "config.h"
#include "dados.h"



void iniciarSensorEC()
{


Serial.println(
"Sensor EC preparado."
);


}



void lerEC()
{


valorEC = 1.4;


}



#endif