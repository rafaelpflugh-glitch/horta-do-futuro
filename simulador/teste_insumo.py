from modelo.insumo import (
    Insumo,
    ReservatorioInsumo,
    SistemaDosagem
)


print("=" * 50)
print("TESTE DE INSUMO")
print("=" * 50)


# ======================================================
# INSUMO
# ======================================================

fertilizante_a = Insumo(
    nome="FERTILIZANTE A",
    tipo="FERTILIZANTE",
    unidade="ml",
    descricao="Solução concentrada de nutrientes A"
)

print()
print("INSUMO:")
print(fertilizante_a)

print()
print(fertilizante_a.snapshot())


# ======================================================
# RESERVATÓRIO
# ======================================================

reservatorio = ReservatorioInsumo(
    insumo=fertilizante_a,
    capacidade_ml=1000,
    nivel_ml=800
)

print()
print("=" * 50)
print("RESERVATÓRIO")
print("=" * 50)

print(reservatorio)

print()
print("Nível:")
print(reservatorio.nivel_ml)

print()
print("Percentual:")
print(reservatorio.percentual)

print()
print("Snapshot:")
print(reservatorio.snapshot())


# ======================================================
# CONSUMO
# ======================================================

print()
print("=" * 50)
print("CONSUMINDO 50 ML")
print("=" * 50)

reservatorio.consumir(50)

print(
    f"Nível restante: "
    f"{reservatorio.nivel_ml} ml"
)


# ======================================================
# REABASTECIMENTO
# ======================================================

print()
print("=" * 50)
print("REABASTECENDO 100 ML")
print("=" * 50)

reservatorio.reabastecer(100)

print(
    f"Nível atual: "
    f"{reservatorio.nivel_ml} ml"
)


# ======================================================
# SISTEMA DE DOSAGEM
# ======================================================

print()
print("=" * 50)
print("SISTEMA DE DOSAGEM")
print("=" * 50)

sistema = SistemaDosagem()


sistema.adicionar_reservatorio(
    nome="FERTILIZANTE A",
    capacidade_ml=1000,
    nivel_ml=800,
    tipo="FERTILIZANTE",
    unidade="ml"
)


sistema.adicionar_reservatorio(
    nome="FERTILIZANTE B",
    capacidade_ml=1000,
    nivel_ml=800,
    tipo="FERTILIZANTE",
    unidade="ml"
)


sistema.adicionar_reservatorio(
    nome="PH UP",
    capacidade_ml=500,
    nivel_ml=500,
    tipo="CORRETIVO_PH",
    unidade="ml"
)


sistema.adicionar_reservatorio(
    nome="PH DOWN",
    capacidade_ml=500,
    nivel_ml=500,
    tipo="CORRETIVO_PH",
    unidade="ml"
)


print()
print("Reservatórios:")

for nome in sistema.reservatorios:

    print(
        "-",
        nome
    )


# ======================================================
# DOSAGEM
# ======================================================

print()
print("=" * 50)
print("DOSAGEM")
print("=" * 50)

dosado = sistema.dosar(
    "FERTILIZANTE A",
    20
)

print(
    f"Dosado: {dosado} ml"
)


# ======================================================
# STATUS
# ======================================================

print()
print("STATUS DO FERTILIZANTE A:")

print(
    sistema.status_reservatorio(
        "FERTILIZANTE A"
    )
)


# ======================================================
# SNAPSHOT COMPLETO
# ======================================================

print()
print("=" * 50)
print("SNAPSHOT COMPLETO")
print("=" * 50)

print(
    sistema.snapshot()
)