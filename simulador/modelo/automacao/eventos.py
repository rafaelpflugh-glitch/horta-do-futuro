"""
============================================================
HORTA DO FUTURO
AUTOMAÇÃO — EVENTOS
============================================================

Registro estruturado dos acontecimentos da automação.

O sistema não deve apenas agir.
Ele deve conseguir explicar o que fez e por quê.

Cada evento representa uma decisão ou acontecimento
importante do cérebro de automação.
============================================================
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EventoAutomacao:

    tipo: str

    mensagem: str

    dados: dict[str, Any] = field(
        default_factory=dict
    )

    nivel: str = "INFO"

    timestamp: str = field(
        default_factory=lambda:
            datetime.now().isoformat(
                timespec="seconds"
            )
    )

    def snapshot(self):

        return {
            "timestamp": self.timestamp,
            "nivel": self.nivel,
            "tipo": self.tipo,
            "mensagem": self.mensagem,
            "dados": dict(self.dados),
        }


class RegistroEventos:

    def __init__(self, limite=500):

        self.limite = int(limite)

        self.eventos = []

    # ======================================================
    # REGISTRAR
    # ======================================================

    def registrar(
        self,
        tipo,
        mensagem,
        dados=None,
        nivel="INFO"
    ):

        evento = EventoAutomacao(

            tipo=str(tipo),

            mensagem=str(mensagem),

            dados=(
                dict(dados)
                if dados
                else {}
            ),

            nivel=str(nivel).upper()
        )

        self.eventos.append(evento)

        if len(self.eventos) > self.limite:

            self.eventos.pop(0)

        return evento

    # ======================================================
    # ATALHOS
    # ======================================================

    def info(
        self,
        tipo,
        mensagem,
        dados=None
    ):

        return self.registrar(
            tipo,
            mensagem,
            dados,
            "INFO"
        )

    def aviso(
        self,
        tipo,
        mensagem,
        dados=None
    ):

        return self.registrar(
            tipo,
            mensagem,
            dados,
            "AVISO"
        )

    def erro(
        self,
        tipo,
        mensagem,
        dados=None
    ):

        return self.registrar(
            tipo,
            mensagem,
            dados,
            "ERRO"
        )

    def bloqueio(
        self,
        tipo,
        mensagem,
        dados=None
    ):

        return self.registrar(
            tipo,
            mensagem,
            dados,
            "BLOQUEIO"
        )

    # ======================================================
    # CONSULTA
    # ======================================================

    def listar(self):

        return [
            evento.snapshot()
            for evento in self.eventos
        ]

    def ultimo(self):

        if not self.eventos:

            return None

        return self.eventos[-1].snapshot()

    def limpar(self):

        self.eventos.clear()