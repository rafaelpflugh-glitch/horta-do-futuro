from modelo.relogio_horta import RelogioHorta

print("=" * 60)
print("TESTE DO RELÓGIO")
print("=" * 60)

relogio = RelogioHorta()

print()
print(relogio.horario())

relogio.avancar_minutos(30)

print(relogio.horario())

relogio.avancar_horas(5)

print(relogio.horario())

relogio.avancar_dias(2)

print(relogio.horario())

print()

relogio.definir_velocidade(60)

for _ in range(10):

    relogio.atualizar()

print(relogio.horario())

print()

print(relogio.snapshot())

print()

print("=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)