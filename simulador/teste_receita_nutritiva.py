from modelo.receita_nutritiva import ReceitaNutritiva


print("=" * 60)
print("TESTE DE RECEITA NUTRITIVA")
print("=" * 60)


# ==========================================================
# CRIAR RECEITA
# ==========================================================

receita = ReceitaNutritiva(

    nome="Alface - Vegetativo",

    fase="VEGETATIVO",

    ph_min=5.8,
    ph_max=6.2,

    ec_min=1.2,
    ec_max=1.8,

    observacoes=(
        "Receita inicial para cultivo DWC. "
        "Ajustar conforme fabricante e medição real."
    )
)


# ==========================================================
# ADICIONAR COMPONENTES
# ==========================================================

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
# REPRESENTAÇÃO
# ==========================================================

print()
print("RECEITA:")
print(receita)


# ==========================================================
# SNAPSHOT
# ==========================================================

print()
print("SNAPSHOT:")

print(
    receita.snapshot()
)


# ==========================================================
# PREPARO DE 1 LITRO
# ==========================================================

print()
print("=" * 60)
print("PREPARO PARA 1 LITRO")
print("=" * 60)

for item in receita.calcular_preparo(1):

    print(
        f"{item['nome']}: "
        f"{item['quantidade']} "
        f"{item['unidade']}"
    )


# ==========================================================
# PREPARO DE 10 LITROS
# ==========================================================

print()
print("=" * 60)
print("PREPARO PARA 10 LITROS")
print("=" * 60)

for item in receita.calcular_preparo(10):

    print(
        f"{item['nome']}: "
        f"{item['quantidade']} "
        f"{item['unidade']}"
    )


# ==========================================================
# PREPARO DE 20 LITROS
# ==========================================================

print()
print("=" * 60)
print("PREPARO PARA 20 LITROS")
print("=" * 60)

for item in receita.calcular_preparo(20):

    print(
        f"{item['nome']}: "
        f"{item['quantidade']} "
        f"{item['unidade']}"
    )


# ==========================================================
# PH
# ==========================================================

print()
print("FAIXA DE PH:")

print(
    receita.faixa_ph()
)


# ==========================================================
# EC
# ==========================================================

print()
print("FAIXA DE EC:")

print(
    receita.faixa_ec()
)


print()
print("=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)