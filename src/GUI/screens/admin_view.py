# src/GUI/screens/admin_view.py
import json
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from GUI import theme
import ENGINE.auth as auth
from GUI.screens.vault_view import _BaseDialog, ConfirmDialog


class AdminView(ctk.CTkFrame):
    """Pannello di amministrazione di sistema: elenco, creazione ed eliminazione utenti."""

    def __init__(self, master, current_username):
        super().__init__(master, fg_color=theme.BG_BASE)
        self.current_username = current_username

        header = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        header.pack(fill="x", padx=28, pady=(24, 10))
        ctk.CTkLabel(header, text="AMMINISTRAZIONE DI SISTEMA", font=theme.font_title(size=22),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Gestisci gli account che possono accedere a PassGuardian",
                     font=theme.font_body(size=12), text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        toolbar = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        toolbar.pack(fill="x", padx=28, pady=(0, 14))

        ctk.CTkButton(
            toolbar, text="+ Registra Nuovo Utente", width=200, height=36,
            command=self._open_add_dialog, **theme.button_primary_kwargs(),
        ).pack(side="left")

        self._build_table()
        self.refresh()

    def _build_table(self):
        table_card = ctk.CTkFrame(self, **theme.frame_card_kwargs())
        table_card.pack(fill="both", expand=True, padx=28, pady=(0, 18))

        style = ttk.Style()
        theme.style_treeview(style)

        tree_frame = tk.Frame(table_card, bg=theme.BG_SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree = ttk.Treeview(
            tree_frame, columns=("id", "username", "ruolo"), show="headings",
            style="Cyber.Treeview", selectmode="browse",
        )
        self.tree.heading("id", text="USER ID")
        self.tree.heading("username", text="USERNAME")
        self.tree.heading("ruolo", text="RUOLO")
        self.tree.column("id", width=100, anchor="w")
        self.tree.column("username", width=260, anchor="w")
        self.tree.column("ruolo", width=200, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview,
                             style="Cyber.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_action_state())

        actions = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        actions.pack(fill="x", padx=28, pady=(0, 22))

        self.btn_delete = ctk.CTkButton(
            actions, text="\U0001F5D1 Elimina Utente Selezionato", width=240, height=36,
            command=self._delete_selected, state="disabled", **theme.button_danger_kwargs(),
        )
        self.btn_delete.pack(side="left")

        self.status_label = ctk.CTkLabel(self, text="", font=theme.font_mono(size=11),
                                          text_color=theme.TEXT_SECONDARY)
        self.status_label.pack(anchor="w", padx=28, pady=(0, 12))

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            with open(auth.PATH_UTENTI, "r", encoding="utf-8") as f:
                utenti = json.load(f)
        except Exception:
            utenti = {}

        for username, info in utenti.items():
            uid = 0 if username == "admin" else info.get("id", 1)
            ruolo = "MASTER (Admin)" if info.get("role") == "super_user" else "USER (Standard)"
            self.tree.insert("", "end", iid=username, values=(uid, username, ruolo))

        self.status_label.configure(text=f"{len(utenti)} utenti registrati nel sistema.")
        self._update_action_state()

    def _update_action_state(self):
        sel = self.tree.selection()
        is_admin_row = sel and sel[0] == "admin"
        self.btn_delete.configure(state="normal" if (sel and not is_admin_row) else "disabled")

    def _open_add_dialog(self):
        AddUserDialog(self, on_saved=self.refresh)

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        username = sel[0]
        ConfirmDialog(
            self, title="Elimina utente",
            message=f"Eliminare definitivamente l'utente '{username}'?\nQuesta azione non e' reversibile.",
            on_confirm=lambda: self._do_delete(username),
        )

    def _do_delete(self, username):
        if auth.elimina_utente(username):
            self.status_label.configure(text=f"\u2705 Utente '{username}' eliminato.", text_color=theme.SUCCESS)
        else:
            self.status_label.configure(text="\u274c Impossibile eliminare l'utente.", text_color=theme.DANGER)
        self.refresh()


class AddUserDialog(_BaseDialog):
    def __init__(self, master, on_saved):
        super().__init__(master, title="Registra Nuovo Utente", height=320)
        self.on_saved = on_saved

        body = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        body.pack(fill="both", expand=True, padx=26, pady=22)

        ctk.CTkLabel(body, text="NUOVO UTENTE DI SISTEMA", font=theme.font_title(size=15),
                     text_color=theme.PURPLE_GLOW).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(body, text="USERNAME", font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        self.user_entry = ctk.CTkEntry(body, height=36, **theme.entry_kwargs())
        self.user_entry.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(body, text="PASSWORD INIZIALE", font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        self.pass_entry = ctk.CTkEntry(body, height=36, show="\u2022", **theme.entry_kwargs())
        self.pass_entry.pack(fill="x", pady=(4, 12))

        self.error_label = ctk.CTkLabel(body, text="", font=theme.font_body(size=11),
                                         text_color=theme.DANGER)
        self.error_label.pack(anchor="w")

        btn_row = ctk.CTkFrame(body, fg_color=theme.TRANSPARENT)
        btn_row.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(btn_row, text="Annulla", command=self.destroy, width=120, height=38,
                      **theme.button_secondary_kwargs()).pack(side="left")
        ctk.CTkButton(btn_row, text="Registra Utente", command=self._save, width=160, height=38,
                      **theme.button_primary_kwargs()).pack(side="right")

        self.user_entry.focus()

    def _save(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            self.error_label.configure(text="Username e password sono obbligatori.")
            return
        if len(password) < 8:
            self.error_label.configure(text="La password deve avere almeno 8 caratteri.")
            return

        if auth.aggiungi_nuovo_utente(username, password):
            self.on_saved()
            self.destroy()
        else:
            self.error_label.configure(text="L'utente esiste gia' o il database non e' raggiungibile.")
