from modelo.reservatorio_cultivo import (
    ReservatorioCultivo
)


print("=" * 60)
print("TESTE DO RESERVATÓRIO DE CULTIVO")
print("=" * 60)


reservatorio = ReservatorioCultivo(
    capacidade_litros=20
)


print("\nRESERVATÓRIO:")
print(reservatorio)


print("\nSNAPSHOT:")
print(
    reservatorio.snapshot()
)


print("\nRETIRANDO 2 LITROS:")

reservatorio.retirar_solucao(
    2
)

print(
    reservatorio.snapshot()
)


print("\nADICIONANDO 1 LITRO:")

reservatorio.adicionar_agua(
    1
)

print(
    reservatorio.snapshot()
)


print("\nALTERANDO PARÂMETROS:")

reservatorio.ph = 5.9

reservatorio.ec = 1.4

reservatorio.temperatura_agua = 21.5

print(
    reservatorio.snapshot()
)


print("\n" + "=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)