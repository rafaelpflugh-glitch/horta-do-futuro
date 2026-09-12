from modelo.fertilizante import Fertilizante
from modelo.receita_nutritiva import ReceitaNutritiva


hydrofert = Fertilizante(

    nome=(
        "HydroFert Orquídeas "
        "Crescimento Alto Rendimento"
    ),

    registro_mapa="SP002442-2.000011",

    tipo=(
        "Fertilizante misto, "
        "via foliar"
    ),

    solubilidade="Solúvel em água",

    rendimento_litros=200,

    n_percentual=30,
    p2o5_percentual=9,
    k2o_percentual=10,

    b_percentual=0.1,
    zn_percentual=0.3,

    observacoes=(
        "Para orquídeas: "
        "1 g/L ou 5 g/m². "
        "1 colher medida rasa = 1 g."
    )
)


print("========================================")
print("FERTILIZANTE")
print("========================================")

print(hydrofert)

print()
print("Nome:", hydrofert.nome)
print("Registro MAPA:", hydrofert.registro_mapa)
print("Composição:", hydrofert.composicao)
print("Rendimento:", hydrofert.rendimento_litros, "L")

print()
print("SNAPSHOT:")
print(hydrofert.snapshot())


receita = ReceitaNutritiva(

    nome="HydroFert Orquídeas - Aplicação",

    fertilizantes=[
        hydrofert
    ],

    objetivo="Crescimento",

    observacoes=(
        "Dados de aplicação copiados "
        "da embalagem do fabricante."
    )
)


print()
print("========================================")
print("RECEITA")
print("========================================")

print(receita)

print()
print("Aplicação para 1 litro:")

print(
    receita.calcular_aplicacao(
        concentracao=1,
        volume_litros=1,
        unidade="g/L"
    )
)

print()
print("Aplicação para 10 litros:")

print(
    receita.calcular_aplicacao(
        concentracao=1,
        volume_litros=10,
        unidade="g/L"
    )
)