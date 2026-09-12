import customtkinter as ctk

from modelo.horta import Horta
from interface.painel_configuracao import PainelConfiguracao


# ============================================================
# CALLBACK
# ============================================================

def cultura_atualizada(configuracao):

    print()
    print("=" * 60)
    print("CULTURA APLICADA")
    print("=" * 60)

    print(configuracao.snapshot())

    print("=" * 60)


# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


# ============================================================
# HORTA
# ============================================================

horta = Horta()


# ============================================================
# JANELA
# ============================================================

app = ctk.CTk()

app.title(
    "Horta do Futuro — Configuração de Cultivo"
)

app.geometry(
    "1100x760"
)

app.minsize(
    900,
    650
)


# ============================================================
# PAINEL
# ============================================================

painel = PainelConfiguracao(
    app,
    horta=horta,
    callback_atualizacao=cultura_atualizada
)

painel.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)


# ============================================================
# LOOP
# ============================================================

app.mainloop()