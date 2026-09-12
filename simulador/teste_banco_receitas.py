from modelo.banco_receitas import BancoReceitas
from modelo.receita_nutritiva import ReceitaNutritiva


print("=" * 60)
print("TESTE DO BANCO DE RECEITAS")
print("=" * 60)


# ==========================================================
# BANCO
# ==========================================================

banco = BancoReceitas()


# ==========================================================
# RECEITA 1
# ==========================================================

alface_semente = ReceitaNutritiva(

    nome="Alface - Semente",

    fase="SEMENTE",

    ph_min=5.8,
    ph_max=6.2,

    ec_min=0.6,
    ec_max=1.0,

    observacoes=(
        "Valores de teste. "
        "Substituir pelos dados reais."
    )
)

alface_semente.adicionar_componente(
    "FERTILIZANTE A",
    1.0,
    "ml"
)

alface_semente.adicionar_componente(
    "FERTILIZANTE B",
    1.0,
    "ml"
)


# ==========================================================
# RECEITA 2
# ==========================================================

alface_vegetativo = ReceitaNutritiva(

    nome="Alface - Vegetativo",

    fase="VEGETATIVO",

    ph_min=5.8,
    ph_max=6.2,

    ec_min=1.2,
    ec_max=1.8,

    observacoes=(
        "Valores de teste. "
        "Substituir pelos dados reais."
    )
)

alface_vegetativo.adicionar_componente(
    "FERTILIZANTE A",
    2.0,
    "ml"
)

alface_vegetativo.adicionar_componente(
    "FERTILIZANTE B",
    2.0,
    "ml"
)


# ==========================================================
# CADASTRAR
# ==========================================================

print()
print("CADASTRANDO RECEITAS...")

banco.cadastrar(
    alface_semente
)

banco.cadastrar(
    alface_vegetativo
)


# ==========================================================
# REPRESENTAÇÃO
# ==========================================================

print()
print("BANCO:")

print(
    banco
)


# ==========================================================
# QUANTIDADE
# ==========================================================

print()
print("QUANTIDADE DE RECEITAS:")

print(
    banco.quantidade()
)


# ==========================================================
# NOMES
# ==========================================================

print()
print("RECEITAS CADASTRADAS:")

for nome in banco.listar_nomes():

    print(
        f"- {nome}"
    )


# ==========================================================
# OBTER
# ==========================================================

print()
print("=" * 60)
print("OBTENDO ALFACE - VEGETATIVO")
print("=" * 60)

receita = banco.obter(
    "alface - vegetativo"
)

print(
    receita
)


# ==========================================================
# CALCULAR PREPARO
# ==========================================================

print()
print("PREPARO PARA 20 LITROS:")

for item in receita.calcular_preparo(
    20
):

    print(
        f"{item['nome']}: "
        f"{item['quantidade']} "
        f"{item['unidade']}"
    )


# ==========================================================
# FILTRAR POR FASE
# ==========================================================

print()
print("=" * 60)
print("RECEITAS DA FASE VEGETATIVO")
print("=" * 60)

receitas_vegetativo = banco.por_fase(
    "vegetativo"
)

for receita in receitas_vegetativo:

    print(
        f"- {receita.nome}"
    )


# ==========================================================
# EXISTÊNCIA
# ==========================================================

print()
print("VERIFICANDO EXISTÊNCIA:")

print(
    banco.existe(
        "Alface - Vegetativo"
    )
)

print(
    banco.existe(
        "Receita Inexistente"
    )
)


# ==========================================================
# SNAPSHOT
# ==========================================================

print()
print("=" * 60)
print("SNAPSHOT DO BANCO")
print("=" * 60)

print(
    banco.snapshot()
)


# ==========================================================
# FINAL
# ==========================================================

print()
print("=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)