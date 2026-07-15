# src/GUI/screens/vault_view.py
import threading
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from GUI import theme
from ENGINE.security import PhishingDetector, decifra_password

try:
    import pyperclip
    _HAS_CLIPBOARD = True
except Exception:
    _HAS_CLIPBOARD = False

try:
    import socket
except Exception:
    socket = None


def _verifica_stato_sito(dominio, timeout=0.6):
    """Controlla se un dominio risponde sulla porta 80. Eseguito in background."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((dominio.strip(), 80))
        s.close()
        return True
    except Exception:
        return False


class VaultView(ctk.CTkFrame):
    """Vista principale: elenco credenziali con ricerca, reveal, add/edit/delete."""

    COLS = ("dominio", "username", "password", "stato")

    def __init__(self, master, vault, username, role):
        super().__init__(master, fg_color=theme.BG_BASE)
        self.vault = vault
        self.username = username
        self.role = role
        self.is_master = role == "super_user"
        self._reveal = False
        self._rows_cache = []  # lista di (owner, dominio, username, password_plain_or_None)

        self._build_header()
        self._build_toolbar()
        self._build_table()

        self.after(100, self.refresh)

    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        header.pack(fill="x", padx=28, pady=(24, 10))

        ctk.CTkLabel(
            header, text="VAULT CREDENZIALI", font=theme.font_title(size=22),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Gestisci in sicurezza le credenziali dei tuoi servizi web",
            font=theme.font_body(size=12), text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(2, 0))

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        toolbar.pack(fill="x", padx=28, pady=(0, 14))

        self.search_entry = ctk.CTkEntry(
            toolbar, width=220, height=36, placeholder_text="\U0001F50D Cerca dominio...",
            **theme.entry_kwargs(),
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_filter())

        if self.is_master:
            ctk.CTkLabel(toolbar, text="Proprietario:", font=theme.font_body(size=11),
                         text_color=theme.GRAY_MUTED).pack(side="left", padx=(14, 6))
            owners = ["Tutti"] + sorted(self.vault.elenca_tutte().keys())
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
            toolbar, text="Mostra in chiaro", command=self._toggle_reveal,
            progress_color=theme.MAGENTA_NEON, button_color=theme.PURPLE_GLOW,
            button_hover_color=theme.PURPLE_BRIGHT, text_color=theme.TEXT_SECONDARY,
            font=theme.font_body(size=11),
        )
        self.reveal_switch.pack(side="left", padx=(14, 0))

        right_box = ctk.CTkFrame(toolbar, fg_color=theme.TRANSPARENT)
        right_box.pack(side="right")

        ctk.CTkButton(
            right_box, text="\u21BB Verifica stato", width=120, height=36,
            command=self.refresh_status_async, **theme.button_secondary_kwargs(),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            right_box, text="+ Aggiungi Credenziale", width=170, height=36,
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
            "dominio": ("\U0001F310 Dominio / Servizio", 240),
            "username": ("Username / Email", 200),
            "password": ("Password", 160),
            "stato": ("Stato", 110),
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
        actions = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        actions.pack(fill="x", padx=28, pady=(0, 22))

        self.btn_copy_pwd = ctk.CTkButton(
            actions, text="\U0001F4CB Copia Password", width=170, height=36,
            command=self._copy_password, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_copy_pwd.pack(side="left", padx=(0, 8))

        self.btn_copy_user = ctk.CTkButton(
            actions, text="\U0001F464 Copia Username", width=170, height=36,
            command=self._copy_username, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_copy_user.pack(side="left", padx=(0, 8))

        self.btn_edit = ctk.CTkButton(
            actions, text="\u270E Modifica Password", width=170, height=36,
            command=self._open_edit_dialog, state="disabled", **theme.button_secondary_kwargs(),
        )
        self.btn_edit.pack(side="left", padx=(0, 8))

        self.btn_delete = ctk.CTkButton(
            actions, text="\U0001F5D1 Elimina", width=120, height=36,
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
        """Ricarica i dati dal vault e ripopola la tabella."""
        self._rows_cache = []
        all_data = self.vault.elenca_tutte()
        owner_filter = self._selected_owner_filter()

        owners = [owner_filter] if owner_filter else sorted(all_data.keys())
        for owner in owners:
            servizi = all_data.get(owner, {})
            for dominio, info in servizi.items():
                self._rows_cache.append({
                    "owner": owner,
                    "dominio": dominio,
                    "username": info.get("username", ""),
                    "password_enc": info.get("password", ""),
                    "online": None,
                })
        self._apply_filter()
        self.refresh_status_async()

    def _apply_filter(self):
        query = self.search_entry.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in self._rows_cache:
            if query and query not in row["dominio"].lower():
                continue
            self._insert_row(row)

        self.status_label.configure(
            text=f"{len(self.tree.get_children())} credenziali visualizzate."
        )
        self._update_action_state()

    def _password_display(self, row):
        if self._reveal:
            try:
                return decifra_password(row["password_enc"])
            except Exception:
                return "[ERRORE]"
        return "\u2022" * 10

    def _stato_display(self, row):
        if row["online"] is None:
            return "\u25CF verifica..."
        return "\U0001F535 ONLINE" if row["online"] else "\U0001F534 OFFLINE"

    def _insert_row(self, row):
        values = []
        if self.is_master:
            values.append(row["owner"])
        values += [row["dominio"], row["username"], self._password_display(row), self._stato_display(row)]
        iid = f"{row['owner']}::{row['dominio']}"
        if self.tree.exists(iid):
            self.tree.item(iid, values=values)
        else:
            self.tree.insert("", "end", iid=iid, values=values)

    def _toggle_reveal(self):
        self._reveal = self.reveal_switch.get() == 1
        self._apply_filter()

    def refresh_status_async(self):
        """Verifica in background (thread) lo stato online/offline di ogni dominio."""
        if socket is None:
            return
        rows_snapshot = list(self._rows_cache)

        def worker():
            for row in rows_snapshot:
                online = _verifica_stato_sito(row["dominio"])
                row["online"] = online
                self.after(0, self._refresh_single_row_status, row)

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_single_row_status(self, row):
        iid = f"{row['owner']}::{row['dominio']}"
        if self.tree.exists(iid):
            values = list(self.tree.item(iid, "values"))
            values[-1] = self._stato_display(row)
            self.tree.item(iid, values=values)

    def _selected_row(self):
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        owner, dominio = iid.split("::", 1)
        for row in self._rows_cache:
            if row["owner"] == owner and row["dominio"] == dominio:
                return row
        return None

    def _update_action_state(self):
        row = self._selected_row()
        state = "normal" if row else "disabled"
        # Un utente standard non puo' modificare/eliminare credenziali altrui (viste solo da super_user su "Tutti")
        can_edit = row is not None and (self.is_master or row["owner"] == self.username)
        edit_state = "normal" if can_edit else "disabled"
        self.btn_copy_pwd.configure(state=state)
        self.btn_copy_user.configure(state=state)
        self.btn_edit.configure(state=edit_state)
        self.btn_delete.configure(state=edit_state)

    # ------------------------------------------------------------------
    def _copy_password(self):
        row = self._selected_row()
        if not row:
            return
        try:
            plain = decifra_password(row["password_enc"])
        except Exception:
            plain = ""
        self._to_clipboard(plain, "Password copiata negli appunti.")

    def _copy_username(self):
        row = self._selected_row()
        if not row:
            return
        self._to_clipboard(row["username"], "Username copiato negli appunti.")

    def _to_clipboard(self, text, ok_message):
        if _HAS_CLIPBOARD:
            try:
                pyperclip.copy(text)
                self.status_label.configure(text=f"\u2705 {ok_message}", text_color=theme.SUCCESS)
                return
            except Exception:
                pass
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_label.configure(text=f"\u2705 {ok_message}", text_color=theme.SUCCESS)
        except Exception:
            self.status_label.configure(text="\u26A0 Impossibile accedere agli appunti.", text_color=theme.WARNING)

    # ------------------------------------------------------------------
    def _open_add_dialog(self):
        AddCredentialDialog(self, vault=self.vault, owner=self.username, on_saved=self.refresh)

    def _open_edit_dialog(self):
        row = self._selected_row()
        if not row:
            return
        if not (self.is_master or row["owner"] == self.username):
            return
        EditCredentialDialog(self, vault=self.vault, owner=row["owner"],
                              dominio=row["dominio"], on_saved=self.refresh)

    def _delete_selected(self):
        row = self._selected_row()
        if not row:
            return
        if not (self.is_master or row["owner"] == self.username):
            return
        ConfirmDialog(
            self,
            title="Elimina credenziale",
            message=f"Eliminare definitivamente la credenziale per\n'{row['dominio']}' ({row['owner']})?",
            on_confirm=lambda: self._do_delete(row),
        )

    def _do_delete(self, row):
        self.vault.elimina_credenziale(row["owner"], row["dominio"])
        self.refresh()


# ==========================================================
#  DIALOGHI MODALI
# ==========================================================

class _BaseDialog(ctk.CTkToplevel):
    def __init__(self, master, title, width=440, height=360):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=theme.BG_BASE)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.after(50, self._center)

    def _center(self):
        self.update_idletasks()
        master = self.master
        mx = master.winfo_rootx() + master.winfo_width() // 2
        my = master.winfo_rooty() + master.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{mx - w // 2}+{my - h // 2}")


class AddCredentialDialog(_BaseDialog):
    def __init__(self, master, vault, owner, on_saved):
        super().__init__(master, title="Aggiungi Credenziale", height=440)
        self.vault = vault
        self.owner = owner
        self.on_saved = on_saved
        self.detector = PhishingDetector()

        body = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        body.pack(fill="both", expand=True, padx=26, pady=22)

        ctk.CTkLabel(body, text="NUOVA CREDENZIALE WEB", font=theme.font_title(size=15),
                     text_color=theme.PURPLE_GLOW).pack(anchor="w", pady=(0, 16))

        self.domain_entry = self._labeled_entry(body, "DOMINIO (es. google.com)")
        self.domain_entry.bind("<KeyRelease>", lambda e: self._check_phishing())
        self.user_entry = self._labeled_entry(body, "USERNAME / EMAIL")
        self.pass_entry = self._labeled_entry(body, "PASSWORD", show="\u2022")

        self.phishing_label = ctk.CTkLabel(
            body, text="", font=theme.font_body(size=11), wraplength=380, justify="left",
        )
        self.phishing_label.pack(anchor="w", pady=(4, 4), fill="x")

        self.error_label = ctk.CTkLabel(body, text="", font=theme.font_body(size=11),
                                         text_color=theme.DANGER)
        self.error_label.pack(anchor="w")

        btn_row = ctk.CTkFrame(body, fg_color=theme.TRANSPARENT)
        btn_row.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(btn_row, text="Annulla", command=self.destroy, width=120, height=38,
                      **theme.button_secondary_kwargs()).pack(side="left")
        ctk.CTkButton(btn_row, text="Salva Credenziale", command=self._save, width=180, height=38,
                      **theme.button_primary_kwargs()).pack(side="right")

        self.domain_entry.focus()

    def _labeled_entry(self, parent, label, show=None):
        ctk.CTkLabel(parent, text=label, font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        kwargs = theme.entry_kwargs()
        if show:
            kwargs["show"] = show
        entry = ctk.CTkEntry(parent, height=36, **kwargs)
        entry.pack(fill="x", pady=(4, 12))
        return entry

    def _check_phishing(self):
        raw = self.domain_entry.get().strip()
        if not raw:
            self.phishing_label.configure(text="")
            return
        clean = self.detector.estrai_dominio(raw)
        safe, msg = self.detector.verifica_dominio(raw)
        color = theme.SUCCESS if safe else theme.DANGER
        self.phishing_label.configure(text=f"{msg}", text_color=color)

    def _save(self):
        raw_domain = self.domain_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not raw_domain or not username or not password:
            self.error_label.configure(text="Tutti i campi sono obbligatori.")
            return

        clean_domain = self.detector.estrai_dominio(raw_domain)
        self.vault.salva_credenziale(self.owner, clean_domain, username, password)
        self.on_saved()
        self.destroy()


class EditCredentialDialog(_BaseDialog):
    def __init__(self, master, vault, owner, dominio, on_saved):
        super().__init__(master, title=f"Modifica \u2014 {dominio}", height=300)
        self.vault = vault
        self.owner = owner
        self.dominio = dominio
        self.on_saved = on_saved

        body = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        body.pack(fill="both", expand=True, padx=26, pady=22)

        ctk.CTkLabel(body, text=f"MODIFICA PASSWORD \u2014 {dominio}", font=theme.font_title(size=14),
                     text_color=theme.PURPLE_GLOW, wraplength=380).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(body, text="NUOVA PASSWORD", font=theme.font_mono(size=10),
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
        ctk.CTkButton(btn_row, text="Aggiorna Password", command=self._save, width=180, height=38,
                      **theme.button_primary_kwargs()).pack(side="right")

        self.pass_entry.focus()

    def _save(self):
        new_pass = self.pass_entry.get()
        if not new_pass:
            self.error_label.configure(text="Inserisci una nuova password.")
            return
        self.vault.modifica_password(self.owner, self.dominio, new_pass)
        self.on_saved()
        self.destroy()


class ConfirmDialog(_BaseDialog):
    def __init__(self, master, title, message, on_confirm):
        super().__init__(master, title=title, width=380, height=200)
        self.on_confirm = on_confirm

        body = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        body.pack(fill="both", expand=True, padx=24, pady=22)

        ctk.CTkLabel(body, text="\u26A0 " + title, font=theme.font_title(size=15),
                     text_color=theme.DANGER).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(body, text=message, font=theme.font_body(size=12),
                     text_color=theme.TEXT_SECONDARY, justify="left").pack(anchor="w")

        btn_row = ctk.CTkFrame(body, fg_color=theme.TRANSPARENT)
        btn_row.pack(fill="x", pady=(24, 0))
        ctk.CTkButton(btn_row, text="Annulla", command=self.destroy, width=110, height=36,
                      **theme.button_secondary_kwargs()).pack(side="left")
        ctk.CTkButton(btn_row, text="Elimina", command=self._confirm, width=110, height=36,
                      **theme.button_danger_kwargs()).pack(side="right")

    def _confirm(self):
        self.on_confirm()
        self.destroy()
