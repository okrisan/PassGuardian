# src/GUI/screens/splash_screen.py
import customtkinter as ctk
from GUI import theme


class SplashScreen(ctk.CTkFrame):
    """Schermata di avvio animata: logo che compare con un fade + barra di boot."""

    DURATION_MS = 2200
    STEPS = 40

    def __init__(self, master, on_done):
        super().__init__(master, fg_color=theme.VOID)
        self.on_done = on_done
        self._step = 0
        self._after_id = None

        center = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Glow "card" attorno al logo
        card = ctk.CTkFrame(
            center,
            fg_color=theme.BG_SURFACE,
            border_width=2,
            border_color=theme.PURPLE_PRIMARY,
            corner_radius=18,
        )
        card.pack(padx=10, pady=10)

        inner = ctk.CTkFrame(card, fg_color=theme.TRANSPARENT)
        inner.pack(padx=60, pady=48)

        self.title_label = ctk.CTkLabel(
            inner,
            text="PASS\u2589GUARDIAN",
            font=theme.font_display(size=40),
            text_color=theme.PURPLE_GLOW,
        )
        self.title_label.pack(pady=(0, 4))

        self.subtitle_label = ctk.CTkLabel(
            inner,
            text="// SECURE CREDENTIAL VAULT // v2.0",
            font=theme.font_mono(size=12),
            text_color=theme.GRAY_MUTED,
        )
        self.subtitle_label.pack(pady=(0, 28))

        self.progress = ctk.CTkProgressBar(
            inner,
            width=340,
            height=10,
            corner_radius=6,
            fg_color=theme.BG_INPUT,
            progress_color=theme.MAGENTA_NEON,
        )
        self.progress.set(0)
        self.progress.pack(pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            inner,
            text="Inizializzazione moduli di sicurezza...",
            font=theme.font_mono(size=11),
            text_color=theme.TEXT_SECONDARY,
        )
        self.status_label.pack()

        self._messages = [
            "Inizializzazione moduli di sicurezza...",
            "Caricamento motore di cifratura Fernet...",
            "Verifica integrita' database utenti...",
            "Avvio rilevatore anti-phishing...",
            "Pronto.",
        ]

        self.after(150, self._animate)

    def _animate(self):
        self._step += 1
        progress = self._step / self.STEPS
        self.progress.set(min(progress, 1.0))

        msg_index = min(len(self._messages) - 1, int(progress * len(self._messages)))
        self.status_label.configure(text=self._messages[msg_index])

        if self._step < self.STEPS:
            self._after_id = self.after(self.DURATION_MS // self.STEPS, self._animate)
        else:
            self.after(300, self._finish)

    def _finish(self):
        if self.winfo_exists():
            self.on_done()

    def destroy(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()
