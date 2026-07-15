import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from GUI import theme
from GUI.screens.vault_view import _BaseDialog, ConfirmDialog
from ENGINE.ssh_vault import SshVault

try:
    import pyperclip
    _HAS_CLIPBOARD = True
except Exception:
    _HAS_CLIPBOARD = False


class SshView(ctk.CTkFrame):
    """Vista gestione SSH: elenco macchine con IP, utente, porta, chiave privata cifrata."""

    COLS = ("nome", "ip", "ssh_username", "password", "porta", "stato")

    def __init__(self, master, username, role):
        super().__init__(master, fg_color=theme.BG_BASE)
        self.ssh_vault = SshVault()
        self.username = username
        self.role = role
        self.is_master = role == "super_user"
        self._reveal = False
        self._rows_cache = []  # lista di (owner, nome_macchina, dati)

        self._build_header()
        self._build_toolbar()
        self._build_table()

        self.after(100, self.refresh)

    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        header.pack(fill="x", padx=28, pady=(24, 10))

        ctk.CTkLabel(
            header, text="GESTIONE SSH", font=theme.font_title(size=22),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Archivia chiavi private e IP delle macchine remote (cifratura Fernet)",
            font=theme.font_body(size=12), text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(2, 0))

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        toolbar.pack(fill="x", padx=28, pady=(0, 14))

        self.search_entry = ctk.CTkEntry(
            toolbar, width=220, height=36, placeholder_text="\U0001F50D Cerca macchina o IP...",
            **theme.entry_kwargs(),
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_filter())

        if self.is_master:
            ctk.CTkLabel(toolbar, text="Proprietario:", font=theme.font_body(size=11),
                         text_color=theme.GRAY_MUTED).pack(side="left", padx=(14, 6))
            owners = ["Tutti"] + sorted(self.ssh_vault.elenca_tutte().keys())
            self.owner_combo = ctk.CTkComboBox(
                toolbar, values=owners, width=130, height=36,
                fg_color=theme.BG_INPUT, border_color=theme.BORDER,
                button_color=theme.PURPLE_DEEP, button_hover_color=theme.PURPLE_PRIMARY,
                text_color=theme.TEXT_PRIMARY, dropdown_fg_color=theme.BG_SURFACE_2,
                dropdown_text_color=theme.TEXT_PRIMARY, dropdown_hover_color=theme.PURPLE_DEEP,
                command=lambda v: self.refresh(),
            )
            self.owner_combo.set("Tutti" if self.is_master else self.username)
            self.owner_combo.pack(side="left")

        self.reveal_switch = ctk.CTkSwitch(
            toolbar, text="Mostra chiave", command=self._toggle_reveal,
            progress_color=theme.MAGENTA_NEON, button_color=theme.PURPLE_GLOW,
            button_hover_color=theme.PURPLE_BRIGHT, text_color=theme.TEXT_SECONDARY,
            font=theme.font_body(size=11),
        )
        self.reveal_switch.pack(side="left", padx=(14, 0))

        right_box = ctk.CTkFrame(toolbar, fg_color=theme.TRANSPARENT)
        right_box.pack(side="right")

        ctk.CTkButton(
            right_box, text="+ Aggiungi Macchina SSH", width=200, height=36,
            command=self._open_add_dialog, **theme.button_primary_kwargs(),
        ).pack(side="left")

    def _build_table(self):
        table_card = ctk.CTkFrame(self, **theme.frame_card_kwargs())
        table_card.pack(fill="both", expand=True, padx=28, pady=(0, 18))

        style = ttk.Style()
        theme.style_treeview(style)

        tree_frame = tk.Frame(table_card, bg=theme.BG_SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.tree = ttk.Treeview(
            tree_frame, columns=self.COLS, show="headings",
            style="Cyber.Treeview", selectmode="browse",
        )
        headers = {
            "nome": ("\U0001F4BB Nome Macchina", 180),
            "ip": ("\U0001F310 IP / Host", 160),
            "ssh_username": ("Utente SSH", 120),
            "password": ("Password", 120),  # <--- NUOVA COLONNA
            "porta": ("Porta", 60),
            "stato": ("Chiave", 100),
        }
        if self.is_master:
            self.tree["columns"] = ("owner",) + self.COLS
            headers = {"owner": ("Proprietario", 110), **headers}

        for col in self.tree["columns"]:
            text, width = headers[col]
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview,
                            style="Cyber.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_action_state())
        self.tree.bind("<Double-1>", lambda e: self._open_edit_dialog())

        # --- Barra azioni riga selezionata ---
        # --- Barra azioni riga selezionata ---
        # --- Barra azioni riga selezionata ---
        actions = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        actions.pack(fill="x", padx=28, pady=(0, 22))

        # NUOVO BOTTONE COPIA PASSWORD
        self.btn_copy_pwd = ctk.CTkButton(
            actions, text="\U0001F511 Copia Password", width=150, height=36,
            command=self._copy_password, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_copy_pwd.pack(side="left", padx=(0, 8))

        self.btn_copy_key = ctk.CTkButton(
            actions, text="\U0001F511 Copia Chiave", width=150, height=36,
            command=self._copy_key, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_copy_key.pack(side="left", padx=(0, 8))

        self.btn_copy_cmd = ctk.CTkButton(
            actions, text="\U0001F4CB Copia Comando", width=150, height=36,
            command=self._copy_command, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_copy_cmd.pack(side="left", padx=(0, 8))

        self.btn_edit = ctk.CTkButton(
            actions, text="\u270E Modifica", width=110, height=36,
            command=self._open_edit_dialog, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_edit.pack(side="left", padx=(0, 8))

        self.btn_delete = ctk.CTkButton(
            actions, text="\U0001F5D1 Elimina", width=110, height=36,
            command=self._delete_selected, state="disabled", **theme.button_danger_kwargs(),
        )
        self.btn_delete.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self, text="", font=theme.font_mono(size=11), text_color=theme.TEXT_SECONDARY,
        )
        self.status_label.pack(anchor="w", padx=28, pady=(0, 12))

    # ------------------------------------------------------------------
    def _selected_owner_filter(self):
        if not self.is_master:
            return self.username
        val = self.owner_combo.get()
        return None if val == "Tutti" else val

    def refresh(self):
        self._rows_cache = []
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtro = self._selected_owner_filter()
        tutti_dati = self.ssh_vault.elenca_tutte()

        for owner, macchine in tutti_dati.items():
            if filtro and owner != filtro:
                continue
            for nome, dati in macchine.items():
                self._rows_cache.append((owner, nome, dati))

        self._apply_filter()

    def _apply_filter(self):
        query = self.search_entry.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        count = 0
        for owner, nome, dati in self._rows_cache:
            ip = dati.get("ip", "")
            if query and query not in nome.lower() and query not in ip.lower():
                continue

            has_key = bool(dati.get("chiave_privata"))
            stato = "\U0001F512 Cifrata" if has_key else "\u2014"

            # --- GESTIONE VISUALIZZAZIONE PASSWORD ---
            if self._reveal:
                # Decifra al volo usando cerca_ssh
                voce_decifrata = self.ssh_vault.cerca_ssh(owner, nome)
                pwd_display = voce_decifrata.get("password", "") if voce_decifrata else ""
                if not pwd_display:
                    pwd_display = "\u2014"
            else:
                # Mostra pallini se esiste una password cifrata, altrimenti un trattino
                pwd_display = "\u2022" * 8 if dati.get("password") else "\u2014"

            # Inseriamo pwd_display nei values
            values = (nome, ip, dati.get("ssh_username", ""), pwd_display, dati.get("porta", 22), stato)

            if self.is_master:
                values = (owner,) + values
            iid = f"{owner}::{nome}"
            self.tree.insert("", "end", iid=iid, values=values)
            count += 1

        self.status_label.configure(text=f"{count} macchine SSH registrate.")
        self._update_action_state()

    def _toggle_reveal(self):
        self._reveal = not self._reveal
        self.refresh()

    def _update_action_state(self):
        sel = self.tree.selection()
        enabled = bool(sel)
        self.btn_copy_pwd.configure(state="normal" if enabled else "disabled") # AGGIUNTO
        self.btn_copy_key.configure(state="normal" if enabled else "disabled")
        self.btn_copy_cmd.configure(state="normal" if enabled else "disabled")
        self.btn_edit.configure(state="normal" if enabled else "disabled")
        self.btn_delete.configure(state="normal" if enabled else "disabled")

    def _selected_owner_name(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        iid = sel[0]
        owner, nome = iid.split("::", 1)
        return owner, nome

    # ------------------------------------------------------------------
    def _copy_key(self):
        owner, nome = self._selected_owner_name()
        if not owner:
            return
        voce = self.ssh_vault.cerca_ssh(owner, nome)
        if voce and voce["chiave_privata"] and voce["chiave_privata"] != "[ERRORE DECRITTAZIONE]":
            self._to_clipboard(voce["chiave_privata"])
            self.status_label.configure(text=f"\u2705 Chiave privata di '{nome}' copiata negli appunti.",
                                         text_color=theme.SUCCESS)
        else:
            self.status_label.configure(text="\u26A0 Nessuna chiave valida da copiare.",
                                         text_color=theme.WARNING)

    def _copy_password(self):
        owner, nome = self._selected_owner_name()
        if not owner:
            return
        voce = self.ssh_vault.cerca_ssh(owner, nome)
        if voce and voce.get("password"):
            self._to_clipboard(voce["password"])
            self.status_label.configure(text=f"\u2705 Password di '{nome}' copiata negli appunti.",
                                        text_color=theme.SUCCESS)
        else:
            self.status_label.configure(text="\u26A0 Nessuna password memorizzata da copiare.",
                                        text_color=theme.WARNING)
    def _copy_command(self):
        owner, nome = self._selected_owner_name()
        if not owner:
            return
        voce = self.ssh_vault.cerca_ssh(owner, nome)
        if voce:
            porta = voce.get("porta", 22)
            cmd = f"ssh -p {porta} {voce['ssh_username']}@{voce['ip']}"
            self._to_clipboard(cmd)
            self.status_label.configure(text=f"\u2705 Comando SSH copiato: {cmd}",
                                         text_color=theme.SUCCESS)

    def _to_clipboard(self, text):
        try:
            if _HAS_CLIPBOARD:
                pyperclip.copy(text)
            else:
                self.clipboard_clear()
                self.clipboard_append(text)
        except Exception:
            self.clipboard_clear()
            self.clipboard_append(text)

    # ------------------------------------------------------------------
    def _open_add_dialog(self):
        AddSshDialog(self, owner=self.username, on_saved=self.refresh)

    def _open_edit_dialog(self):
        owner, nome = self._selected_owner_name()
        if not owner:
            return
        # L'admin puo' modificare le macchine di tutti; l'utente solo le proprie
        edit_owner = owner if self.is_master else self.username
        EditSshDialog(self, ssh_vault=self.ssh_vault, owner=edit_owner,
                       nome_macchina=nome, on_saved=self.refresh)

    def _delete_selected(self):
        owner, nome = self._selected_owner_name()
        if not owner:
            return
        del_owner = owner if self.is_master else self.username
        ConfirmDialog(
            self, title="Elimina macchina SSH",
            message=f"Eliminare definitivamente la connessione '{nome}' ({owner})?\nQuesta azione non e' reversibile.",
            on_confirm=lambda: self._do_delete(del_owner, nome),
        )

    def _do_delete(self, owner, nome):
        if self.ssh_vault.elimina_ssh(owner, nome):
            self.status_label.configure(text=f"\u2705 Macchina '{nome}' eliminata.",
                                         text_color=theme.SUCCESS)
        else:
            self.status_label.configure(text="\u274C Impossibile eliminare la macchina.",
                                         text_color=theme.DANGER)
        self.refresh()


# ======================================================================
#  DIALOGS
# ======================================================================

class AddSshDialog(_BaseDialog):
    def __init__(self, master, owner, on_saved):
        super().__init__(
            master,
            title="Aggiungi Macchina SSH",
            width=520,
            height=720
        )
        self.minsize(520, 720)
        self.owner = owner
        self.on_saved = on_saved
        self.ssh_vault = SshVault()

        body = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        body.pack(fill="both", expand=True, padx=26, pady=22)

        ctk.CTkLabel(body, text="NUOVA CONNESSIONE SSH", font=theme.font_title(size=15),
                     text_color=theme.PURPLE_GLOW).pack(anchor="w", pady=(0, 16))

        self.name_entry = self._labeled_entry(
            body,
            "NOME MACCHINA (es. web-server-01)"
        )

        self.ip_entry = self._labeled_entry(
            body,
            "IP / HOSTNAME (es. 192.168.1.50)"
        )

        self.user_entry = self._labeled_entry(
            body,
            "UTENTE SSH (es. root)"
        )

        self.password_entry = self._labeled_entry(
            body,
            "PASSWORD SSH",
            show="•"
        )

        self.port_entry = self._labeled_entry(
            body,
            "PORTA (default 22)"
        )
        self.port_entry.insert(0, "22")

        self.key_entry = self._labeled_entry(
            body,
            "CHIAVE PRIVATA (OPZIONALE)",
            show="•"
        )

        self.note_entry = self._labeled_entry(
            body,
            "NOTE (opzionale)"
        )
        self.error_label = ctk.CTkLabel(body, text="", font=theme.font_body(size=11),
                                         text_color=theme.DANGER, wraplength=420)
        self.error_label.pack(anchor="w", pady=(4, 0))

        btn_row = ctk.CTkFrame(body, fg_color=theme.TRANSPARENT)
        btn_row.pack(fill="x", pady=(14, 0))
        ctk.CTkButton(btn_row, text="Annulla", command=self.destroy, width=120, height=38,
                      **theme.button_secondary_kwargs()).pack(side="left")
        ctk.CTkButton(btn_row, text="Salva Macchina", command=self._save, width=180, height=38,
                      **theme.button_primary_kwargs()).pack(side="right")

        self.name_entry.focus()

    def _labeled_entry(self, parent, label, show=None):
        ctk.CTkLabel(parent, text=label, font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        kwargs = theme.entry_kwargs()
        if show:
            kwargs["show"] = show
        entry = ctk.CTkEntry(parent, height=36, **kwargs)
        entry.pack(fill="x", pady=(4, 12))
        return entry

    def _save(self):
        nome = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        ssh_user = self.user_entry.get().strip()
        password = self.password_entry.get()
        porta = self.port_entry.get().strip() or "22"
        chiave = self.key_entry.get()
        note = self.note_entry.get().strip()

        if not nome or not ip or not ssh_user:
            self.error_label.configure(
                text="Nome, IP e utente SSH sono obbligatori."
            )
            return

        try:
            int(porta)
        except ValueError:
            self.error_label.configure(
                text="La porta deve essere un numero."
            )
            return

        self.ssh_vault.salva_ssh(
            self.owner,
            nome,
            ip,
            ssh_user,
            password,
            porta,
            chiave,
            note
        )

        self.on_saved()
        self.destroy()


class EditSshDialog(_BaseDialog):
    def __init__(self, master, ssh_vault, owner, nome_macchina, on_saved):
        super().__init__(master, title=f"Modifica \u2014 {nome_macchina}", width=480, height=560)
        self.ssh_vault = ssh_vault
        self.owner = owner
        self.nome_macchina = nome_macchina
        self.on_saved = on_saved

        voce = ssh_vault.cerca_ssh(owner, nome_macchina) or {}

        body = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        body.pack(fill="both", expand=True, padx=26, pady=22)

        ctk.CTkLabel(body, text=f"MODIFICA \u2014 {nome_macchina}", font=theme.font_title(size=14),
                     text_color=theme.PURPLE_GLOW, wraplength=420).pack(anchor="w", pady=(0, 16))

        self.ip_entry = self._labeled_entry(body, "IP / HOSTNAME")
        self.ip_entry.insert(0, voce.get("ip", ""))
        self.user_entry = self._labeled_entry(body, "UTENTE SSH")
        self.user_entry.insert(0, voce.get("ssh_username", ""))
        self.password_entry = self._labeled_entry(
            body,
            "PASSWORD SSH",
            show="•"
        )
        self.password_entry.insert(
            0,
            voce.get("password", "")
        )
        self.port_entry = self._labeled_entry(body, "PORTA")
        self.port_entry.insert(0, str(voce.get("porta", 22)))
        self.key_entry = self._labeled_entry(body, "NUOVA CHIAVE PRIVATA (vuoto = mantiene)", show="\u2022")
        self.note_entry = self._labeled_entry(body, "NOTE")
        self.note_entry.insert(0, voce.get("note", ""))

        self.error_label = ctk.CTkLabel(body, text="", font=theme.font_body(size=11),
                                         text_color=theme.DANGER, wraplength=420)
        self.error_label.pack(anchor="w", pady=(4, 0))

        btn_row = ctk.CTkFrame(body, fg_color=theme.TRANSPARENT)
        btn_row.pack(fill="x", pady=(14, 0))
        ctk.CTkButton(btn_row, text="Annulla", command=self.destroy, width=120, height=38,
                      **theme.button_secondary_kwargs()).pack(side="left")
        ctk.CTkButton(btn_row, text="Aggiorna Macchina", command=self._save, width=180, height=38,
                      **theme.button_primary_kwargs()).pack(side="right")

        self.ip_entry.focus()

    def _labeled_entry(self, parent, label, show=None):
        ctk.CTkLabel(parent, text=label, font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        kwargs = theme.entry_kwargs()
        if show:
            kwargs["show"] = show
        entry = ctk.CTkEntry(parent, height=36, **kwargs)
        entry.pack(fill="x", pady=(4, 12))
        return entry

    def _save(self):
        nome = self.nome_macchina
        ip = self.ip_entry.get().strip()
        ssh_user = self.user_entry.get().strip()
        password = self.password_entry.get()
        porta = self.port_entry.get().strip() or "22"
        chiave = self.key_entry.get()
        note = self.note_entry.get().strip()

        if not nome or not ip or not ssh_user:
            self.error_label.configure(
                text="Nome, IP e utente SSH sono obbligatori."
            )
            return

        try:
            int(porta)
        except ValueError:
            self.error_label.configure(
                text="La porta deve essere un numero."
            )
            return

        vault = SshVault()

        vault.salva_ssh(
            self.owner,
            nome,
            ip,
            ssh_user,
            password,
            porta,
            chiave,
            note
        )

        self.on_saved()
        self.destroy()