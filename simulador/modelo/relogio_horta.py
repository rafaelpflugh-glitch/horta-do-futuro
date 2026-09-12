"""
============================================================
HORTA DO FUTURO

RELÓGIO DA HORTA

============================================================

Responsável pelo tempo da simulação.

NÃO utiliza datetime.now().

Todo o sistema deve utilizar este relógio.

Pode operar em:

- pausa
- tempo real
- acelerado

============================================================
"""

from dataclasses import dataclass


@dataclass
class RelogioHorta:

    dia: int = 1

    hora: int = 0

    minuto: int = 0

    velocidade: int = 1

    pausado: bool = False

    # =====================================================

    def avancar_minutos(self, minutos=1):

        if self.pausado:
            return

        total = self.minuto + minutos

        self.minuto = total % 60

        horas = self.hora + total // 60

        self.hora = horas % 24

        self.dia += horas // 24

    # =====================================================

    def avancar_horas(self, horas=1):

        self.avancar_minutos(horas * 60)

    # =====================================================

    def avancar_dias(self, dias=1):

        self.avancar_horas(dias * 24)

    # =====================================================

    def atualizar(self):

        self.avancar_minutos(self.velocidade)

    # =====================================================

    def pausar(self):

        self.pausado = True

    # =====================================================

    def continuar_(self):

        self.pausado = False

    # =====================================================

    def definir_velocidade(self, velocidade):

        self.velocidade = max(
            1,
            int(velocidade)
        )

    # =====================================================

    def horario(self):

        return (
            f"Dia {self.dia:03d}   "
            f"{self.hora:02d}:"
            f"{self.minuto:02d}"
        )

    # =====================================================

    def snapshot(self):

        return {

            "dia": self.dia,

            "hora": self.hora,

            "minuto": self.minuto,

            "velocidade": self.velocidade,

            "pausado": self.pausado
        }