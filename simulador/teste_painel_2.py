import customtkinter as ctk

from modelo.horta import Horta
from interface.painel_configuracao import PainelConfiguracao


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


app = ctk.CTk()

app.title(
    "Teste — Horta do Futuro"
)

app.geometry(
    "500x300"
)

horta = Horta()


def abrir_painel():

    PainelConfiguracao(
        app,
        horta
    )


botao = ctk.CTkButton(
    app,
    text="🌱 ABRIR CONFIGURAÇÃO",
    command=abrir_painel
)

botao.pack(
    expand=True
)


app.mainloop()