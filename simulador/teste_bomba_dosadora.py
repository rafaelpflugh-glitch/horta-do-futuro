from modelo.bomba_dosadora import (
    BombaDosadora
)


print("=" * 60)
print("TESTE DE BOMBA DOSADORA")
print("=" * 60)


# ==========================================================
# CRIAÇÃO
# ==========================================================

bomba = BombaDosadora(
    nome="BOMBA A",
    vazao_ml_min=30
)


print("\nBOMBA:")
print(bomba)


print("\nSNAPSHOT INICIAL:")
print(
    bomba.snapshot()
)


# ==========================================================
# TEMPO PARA DOSAGEM
# ==========================================================

print("\nTEMPO PARA DOSAR:")

for volume in (
    1,
    5,
    10,
    20,
):

    tempo = bomba.tempo_para_dosar(
        volume
    )

    print(
        f"{volume} ml -> "
        f"{tempo:.2f} segundos"
    )


# ==========================================================
# VOLUME POR TEMPO
# ==========================================================

print("\nVOLUME POR TEMPO:")

for segundos in (
    5,
    10,
    30,
    60,
):

    volume = bomba.volume_por_tempo(
        segundos
    )

    print(
        f"{segundos} s -> "
        f"{volume:.2f} ml"
    )


# ==========================================================
# DOSAGEM
# ==========================================================

print("\nDOSANDO 10 ML:")

tempo = bomba.dosar_ml(
    10
)

print(
    f"Tempo necessário: "
    f"{tempo:.2f} segundos"
)

print(
    f"Bomba ativa: "
    f"{bomba.ativa}"
)


# ==========================================================
# CALIBRAÇÃO
# ==========================================================

print("\nCALIBRAÇÃO REAL SIMULADA:")

print(
    "Coletamos 15 ml em 30 segundos."
)

vazao = bomba.calibrar(
    volume_medido_ml=15,
    tempo_segundos=30
)

print(
    f"Nova vazão calibrada: "
    f"{vazao:.2f} ml/min"
)


# ==========================================================
# NOVA DOSAGEM
# ==========================================================

print("\nDOSANDO NOVAMENTE 10 ML:")

tempo = bomba.dosar_ml(
    10
)

print(
    f"Tempo necessário: "
    f"{tempo:.2f} segundos"
)


# ==========================================================
# SNAPSHOT FINAL
# ==========================================================

print("\nSNAPSHOT FINAL:")

print(
    bomba.snapshot()
)


print("\n" + "=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)