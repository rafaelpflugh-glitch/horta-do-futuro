#ifndef SAUDE_H
#define SAUDE_H



#include "dados.h"
#include "cultivo.h"



/*
=================================================

ÍNDICE DE SAÚDE

Cálculo:

Temperatura 30%
pH           30%
EC           20%
Nível água   20%

=================================================
*/



float avaliarTemperatura()
{


if(
ambiente.temperaturaAr >= cultivoAtual.temperaturaMin
&&
ambiente.temperaturaAr <= cultivoAtual.temperaturaMax
)

{

return 100;

}

else

{

return 50;

}



}



float avaliarPH()
{


if(
ambiente.ph >= cultivoAtual.phMin
&&
ambiente.ph <= cultivoAtual.phMax
)

{

return 100;

}

else

{

return 50;

}


}



float avaliarNivel()
{


if(ambiente.nivelAgua)

return 100;


else

return 0;


}




void calcularSaude()
{


float resultado;



resultado =
(
avaliarTemperatura()*0.30
+
avaliarPH()*0.30
+
90*0.20
+
avaliarNivel()*0.20
);



indiceSaude =
(int)resultado;



}



#endif