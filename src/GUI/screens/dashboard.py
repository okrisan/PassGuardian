# src/GUI/screens/dashboard.py
import customtkinter as ctk
from GUI import theme
from GUI.screens.vault_view import VaultView
from GUI.screens.security_view import SecurityView
from GUI.screens.admin_view import AdminView
from GUI.screens.ssh_view import SshView


class Dashboard(ctk.CTkFrame):
    """Shell principale post-login: sidebar di navigazione + area contenuti dinamica."""

    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_BASE)
        self.app = app
        self.username = app.username
        self.role = app.role
        self._nav_buttons = {}
        self._current_view = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content_area()

        self.show_vault()

    # ------------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=theme.BG_SURFACE, width=230, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        # --- Logo ---
        logo_frame = ctk.CTkFrame(sidebar, fg_color=theme.TRANSPARENT)
        logo_frame.pack(fill="x", padx=20, pady=(26, 4))
        ctk.CTkLabel(
            logo_frame, text="PASS\u2589GUARD",
            font=theme.font_title(size=19), text_color=theme.PURPLE_GLOW,
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text="// vault v2.0", font=theme.font_mono(size=10),
            text_color=theme.GRAY_MUTED,
        ).pack(anchor="w")

        divider = ctk.CTkFrame(sidebar, fg_color=theme.BORDER, height=1)
        divider.pack(fill="x", padx=20, pady=(16, 18))

        # --- Badge utente ---
        user_card = ctk.CTkFrame(sidebar, fg_color=theme.BG_SURFACE_2, corner_radius=10)
        user_card.pack(fill="x", padx=16, pady=(0, 20))

        is_master = self.role == "super_user"
        ctk.CTkLabel(
            user_card, text=self.username, font=theme.font_body(size=13, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=12, pady=(10, 0))

        badge_text = "MASTER" if is_master else "USER"
        badge_color = theme.MAGENTA_NEON if is_master else theme.GRAY_TEXT
        ctk.CTkLabel(
            user_card, text=f"\u25CF {badge_text}", font=theme.font_mono(size=10),
            text_color=badge_color,
        ).pack(anchor="w", padx=12, pady=(2, 10))

        # --- Navigazione ---
        nav_items = [
            ("vault", "\U0001F5C4  Vault Credenziali", self.show_vault),
            ("ssh", "\U0001F5A5  Gestione SSH", self.show_ssh),
            ("security", "\U0001F6E1  Sicurezza Account", self.show_security),
        ]
        if is_master:
            nav_items.append(("admin", "\u2699  Amministrazione", self.show_admin))

        nav_frame = ctk.CTkFrame(sidebar, fg_color=theme.TRANSPARENT)
        nav_frame.pack(fill="x", padx=12)

        for key, label, command in nav_items:
            btn = ctk.CTkButton(
                nav_frame, text=label, command=command, height=40,
                **theme.button_ghost_kwargs(),
            )
            btn.pack(fill="x", pady=3)
            self._nav_buttons[key] = btn

        # --- Footer: switch utente / esci ---
        footer = ctk.CTkFrame(sidebar, fg_color=theme.TRANSPARENT)
        footer.pack(side="bottom", fill="x", padx=12, pady=18)

        ctk.CTkButton(
            footer, text="\u21BB  Cambia Utente", command=self._switch_user,
            height=36, **theme.button_secondary_kwargs(),
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            footer, text="\u23FB  Esci", command=self._quit_app,
            height=36, **theme.button_danger_kwargs(),
        ).pack(fill="x")

    def _set_active(self, key):
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(fg_color=theme.PURPLE_DEEP, text_color=theme.TEXT_PRIMARY)
            else:
                btn.configure(fg_color=theme.TRANSPARENT, text_color=theme.GRAY_TEXT)

    # ------------------------------------------------------------------
    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=theme.BG_BASE, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _swap_view(self, view):
        if self._current_view is not None:
            self._current_view.destroy()
        self._current_view = view
        view.grid(row=0, column=0, sticky="nsew")

    def show_vault(self):
        self._set_active("vault")
        self._swap_view(VaultView(self.content, vault=self.app.vault,
                                   username=self.username, role=self.role))

    def show_security(self):
        self._set_active("security")
        self._swap_view(SecurityView(self.content, username=self.username))

    def show_admin(self):
        self._set_active("admin")
        self._swap_view(AdminView(self.content, current_username=self.username))

    def show_ssh(self):
        self._set_active("ssh")
        self._swap_view(SshView(self.content, username=self.username, role=self.role))

    def _switch_user(self):
        self.app.logout()

    def _quit_app(self):
        self.app.destroy()
