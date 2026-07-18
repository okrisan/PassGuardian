# src/GUI/screens/splash_screen.py
import customtkinter as ctk
from GUI import theme


class SplashScreen(ctk.CTkFrame):
    """Schermata di avvio con barra di caricamento cyberpunk."""

    def __init__(self, parent, on_done):
        super().__init__(parent, fg_color=theme.BG_BASE)
        self.on_done = on_done
        self.progress = 0.0

        # Layout centrale
        self.grid_rowconfigure((0, 4), weight=1)
        self.grid_columnconfigure((0, 2), weight=1)

        # Titolo ad alto impatto
        self.title_label = ctk.CTkLabel(
            self,
            text="PASSGUARDIAN",
            font=theme.font_display(size=42),
            text_color=theme.MAGENTA_NEON,
        )
        self.title_label.grid(row=1, column=1, pady=(0, 10))

        # Sottotitolo
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="SYSTEM INITIALIZATION // SECURE POLYMORPHIC VAULT",
            font=theme.font_mono(size=12),
            text_color=theme.PURPLE_GLOW,
        )
        self.subtitle_label.grid(row=2, column=1, pady=(0, 40))

        # Barra di progresso
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=4,
            fg_color=theme.BG_SURFACE_2,
            progress_color=theme.PURPLE_PRIMARY,
        )
        self.progress_bar.grid(row=3, column=1, pady=10)
        self.progress_bar.set(0)

        # Avvia il finto caricamento
        self._update_progress()

    def _update_progress(self):
        if self.progress < 1.0:
            self.progress += 0.05
            self.progress_bar.set(self.progress)
            # Rallenta o accelera leggermente l'effetto
            self.after(80, self._update_progress)
        else:
            # Una volta completato, passa al login tramite callback
            self.on_done()