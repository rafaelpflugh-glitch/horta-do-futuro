from modelo.receita_nutritiva import ReceitaNutritiva
from modelo.reservatorio_cultivo import ReservatorioCultivo
from modelo.sistema_preparacao import SistemaPreparacao


print("=" * 60)
print("INTEGRAÇÃO — RECEITA + RESERVATÓRIO + PREPARAÇÃO")
print("=" * 60)


# ==========================================================
# RECEITA NORMAL
# ==========================================================

receita = ReceitaNutritiva(
    nome="Alface - Vegetativo",
    fase="VEGETATIVO",
    ph_min=5.8,
    ph_max=6.2,
    ec_min=1.2,
    ec_max=1.8,
    observacoes="Receita de teste para DWC."
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
# RESERVATÓRIO NORMAL
# ==========================================================

reservatorio = ReservatorioCultivo(
    capacidade_litros=20.0,
    volume_litros=20.0
)


# ==========================================================
# SISTEMA NORMAL
# ==========================================================

sistema = SistemaPreparacao(
    receita=receita,
    reservatorio=reservatorio
)


# ==========================================================
# CAPACIDADE
# ==========================================================

print()
print("CAPACIDADE:")

print(sistema.verificar_capacidade())


# ==========================================================
# QUANTIDADES
# ==========================================================

print()
print("QUANTIDADES NECESSÁRIAS:")

for item in sistema.calcular_quantidades():
    print(
        f"- {item['nome']}: "
        f"{item['quantidade']:.2f} "
        f"{item['unidade']}"
    )


# ==========================================================
# ÁGUA
# ==========================================================

print()
print("ÁGUA INICIAL:")

print(
    f"{sistema.volume_agua_inicial_litros():.3f} L"
)


# ==========================================================
# VALIDAÇÃO NORMAL
# ==========================================================

print()
print("VALIDAÇÃO:")

validacao_normal = sistema.validar()

print(validacao_normal)

assert validacao_normal["valido"] is True

print()
print("PREPARAÇÃO NORMAL VALIDADA")


# ==========================================================
# PLANO
# ==========================================================

print()
print("=" * 60)
print("PLANO DE PREPARO")
print("=" * 60)

plano = sistema.gerar_plano()

print()
print("Receita:", plano["receita"])
print("Fase:", plano["fase"])
print("Volume final:", plano["volume_final_litros"], "L")
print("Água inicial:", plano["agua_inicial_litros"], "L")
print("Insumos:", plano["volume_insumos_ml"], "ml")

print()
print("ETAPAS:")

for etapa in plano["etapas"]:
    print(
        f"{etapa['ordem']}. "
        f"{etapa['tipo']}: "
        f"{etapa.get('descricao', '')}"
    )

    if etapa["tipo"] == "AGUA":
        print(
            f"   Volume: "
            f"{etapa['volume_litros']:.3f} L"
        )

    elif etapa["tipo"] == "DOSAGEM":
        print(
            f"   Insumo: "
            f"{etapa['insumo']}"
        )

        print(
            f"   Quantidade: "
            f"{etapa['quantidade']:.2f} "
            f"{etapa['unidade']}"
        )


# ==========================================================
# TESTE DE SEGURANÇA
# VOLUME ALVO ACIMA DA CAPACIDADE
# ==========================================================

print()
print("=" * 60)
print("TESTE DE SEGURANÇA — VOLUME ACIMA DA CAPACIDADE")
print("=" * 60)


reservatorio_excesso = ReservatorioCultivo(
    capacidade_litros=10.0,
    volume_litros=15.0
)


sistema_excesso = SistemaPreparacao(
    receita=receita,
    reservatorio=reservatorio_excesso
)


# ==========================================================
# CAPACIDADE DO TESTE
# ==========================================================

print()
print("CAPACIDADE DO RESERVATÓRIO:")

capacidade_excesso = (
    sistema_excesso.verificar_capacidade()
)

print(capacidade_excesso)


# ==========================================================
# QUANTIDADES DO TESTE
# ==========================================================

print()
print("QUANTIDADES DO TESTE:")

for item in sistema_excesso.calcular_quantidades():
    print(
        f"- {item['nome']}: "
        f"{item['quantidade']:.2f} "
        f"{item['unidade']}"
    )


# ==========================================================
# ÁGUA DO TESTE
# ==========================================================

print()
print("ÁGUA NECESSÁRIA:")

print(
    f"{sistema_excesso.volume_agua_inicial_litros():.3f} L"
)


# ==========================================================
# VALIDAÇÃO DO TESTE
# ==========================================================

print()
print("VALIDAÇÃO:")

validacao_excesso = (
    sistema_excesso.validar()
)

print(validacao_excesso)


# ==========================================================
# DEVE SER REPROVADO
# ==========================================================

assert validacao_excesso["valido"] is False


print()
print(
    "SEGURANÇA VALIDADA: "
    "o sistema recusou uma preparação "
    "acima da capacidade do reservatório."
)


# ==========================================================
# PROBLEMAS
# ==========================================================

print()
print("PROBLEMAS DETECTADOS:")

for problema in validacao_excesso["problemas"]:
    print(
        f"- {problema}"
    )


# ==========================================================
# FINAL
# ==========================================================

print()
print("=" * 60)
print("TESTE FINALIZADO COM SUCESSO")
print("=" * 60)