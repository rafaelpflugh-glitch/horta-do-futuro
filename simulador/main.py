import customtkinter as ctk

from interface.janela_principal import JanelaPrincipal


def main():

    ctk.set_appearance_mode(
        "dark"
    )

    ctk.set_default_color_theme(
        "green"
    )

    app = JanelaPrincipal()

    app.mainloop()


if __name__ == "__main__":

    main()