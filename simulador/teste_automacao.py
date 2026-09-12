from modelo.horta import Horta
from modelo.automacao import Automacao


horta = Horta()

automacao = Automacao(horta)


print("=" * 60)
print("TESTE 1 — ESTADO NORMAL")
print("=" * 60)

print(automacao.executar())

print()


print("=" * 60)
print("TESTE 2 — TEMPERATURA ALTA")
print("=" * 60)

horta.alterar_temperatura_ar(30)

print(automacao.executar())

print(
    "Ventilação:",
    horta.ventilacao
)

print()


print("=" * 60)
print("TESTE 3 — TEMPERATURA NORMAL")
print("=" * 60)

horta.alterar_temperatura_ar(24)

print(automacao.executar())

print(
    "Ventilação:",
    horta.ventilacao
)

print()


print("=" * 60)
print("TESTE 4 — NÍVEL BAIXO")
print("=" * 60)

horta.alterar_nivel_agua(5)

horta.ligar_bomba()

print(
    "Bomba antes:",
    horta.bomba
)

print(automacao.executar())

print(
    "Bomba depois:",
    horta.bomba
)

print()


print("=" * 60)
print("TESTE 5 — pH FORA DA FAIXA")
print("=" * 60)

horta.alterar_nivel_agua(100)

horta.alterar_ph(4.5)

print(automacao.executar())

print()


print("=" * 60)
print("TESTE 6 — EC FORA DA FAIXA")
print("=" * 60)

horta.alterar_ec(2.5)

print(automacao.executar())

print()


print("=" * 60)
print("SNAPSHOT DA AUTOMAÇÃO")
print("=" * 60)

print(automacao.snapshot())