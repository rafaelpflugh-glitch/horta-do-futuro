from modelo.receita_nutritiva import ReceitaNutritiva
from modelo.reservatorio_cultivo import ReservatorioCultivo
from modelo.sistema_preparacao import SistemaPreparacao


print("=" * 60)
print("TESTE DO SISTEMA DE PREPARAÇÃO")
print("=" * 60)


# ==========================================================
# RECEITA
# ==========================================================

receita = ReceitaNutritiva(
    nome="Alface - Vegetativo",
    fase="VEGETATIVO",
    ph_min=5.8,
    ph_max=6.2,
    ec_min=1.2,
    ec_max=1.8,
    observacoes=(
        "Receita inicial de teste."
    )
)


receita.adicionar_componente(
    nome="FERTILIZANTE A",
    quantidade_por_litro=2.0,
    unidade="ml"
)


receita.adicionar_componente(
    nome="FERTILIZANTE B",
    quantidade_por_litro=2.0,
    unidade="ml"
)


# ==========================================================
# RESERVATÓRIO
# ==========================================================

reservatorio = ReservatorioCultivo(
    capacidade_litros=6.0,
    volume_litros=5.0
)


# ==========================================================
# SISTEMA
# ==========================================================

sistema = SistemaPreparacao(
    receita=receita,
    reservatorio=reservatorio
)


# ==========================================================
# VOLUME
# ==========================================================

print()
print("VOLUME:")
print(
    sistema.volume_alvo(),
    "litros"
)


# ==========================================================
# QUANTIDADES
# ==========================================================

print()
print("QUANTIDADES:")

for item in sistema.calcular_quantidades():

    print(
        f"- {item['nome']}: "
        f"{item['quantidade']} "
        f"{item['unidade']}"
    )


# ==========================================================
# VALIDAÇÃO
# ==========================================================

print()
print("VALIDAÇÃO:")

print(
    sistema.validar()
)


# ==========================================================
# PLANO
# ==========================================================

print()
print("=" * 60)
print("PLANO DE PREPARO")
print("=" * 60)

plano = sistema.gerar_plano()

print()

print(
    "Receita:",
    plano["receita"]
)

print(
    "Fase:",
    plano["fase"]
)

print(
    "Volume:",
    plano["volume_litros"],
    "L"
)

print()

print("FAIXA DE PH:")

print(
    plano["ph_alvo"]
)

print()

print("FAIXA DE EC:")

print(
    plano["ec_alvo"]
)

print()

print("ETAPAS:")

for etapa in plano["etapas"]:

    print(
        f"- {etapa['insumo']}: "
        f"{etapa['quantidade']} "
        f"{etapa['unidade']}"
    )


print()
print("=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)