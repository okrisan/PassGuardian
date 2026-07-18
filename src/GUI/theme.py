# src/GUI/theme.py
"""
PassGuardian :: Cyber Theme Engine
-----------------------------------
Palette scura ispirata al cyberpunk: nero profondo, viola/magenta neon e
grigi metallici.
"""

import customtkinter as ctk

# ==========================================================
#  PALETTE
# ==========================================================
VOID        = "#050308"   # nero quasi assoluto
BG_BASE     = "#0b0812"   # sfondo principale app
BG_SURFACE  = "#140f1f"   # pannelli / card
BG_SURFACE_2 = "#1c1529"  # pannelli sopraelevati / hover
BG_INPUT    = "#181022"   # sfondo campi di input
BORDER      = "#33253f"   # bordi sottili
BORDER_SOFT = "#241a30"

GRAY_MUTED   = "#877e96"
GRAY_TEXT    = "#b4abc4"
GRAY_LIGHT   = "#d9d3e3"

TEXT_PRIMARY   = "#efe9fb"
TEXT_SECONDARY = "#a79fc0"
TEXT_DISABLED  = "#5c5468"

PURPLE_DEEP    = "#3a1a5c"
PURPLE_PRIMARY = "#7c2ee0"
PURPLE_BRIGHT  = "#a855f7"
PURPLE_GLOW    = "#c084fc"
MAGENTA_NEON   = "#e935d1"
MAGENTA_SOFT   = "#f472e8"

SUCCESS      = "#39e991"
SUCCESS_DIM  = "#1f6e4f"
DANGER       = "#ff4d6a"
DANGER_DIM   = "#7a2333"
WARNING      = "#ffb454"
INFO         = "#9d7bff"

TRANSPARENT = "transparent"

# ==========================================================
#  FONT[cite: 6]
# ==========================================================
FONT_FAMILY_MONO = "Consolas"
FONT_FAMILY_UI = "Segoe UI"

def font_display(size=28, weight="bold"):
    return ctk.CTkFont(family=FONT_FAMILY_MONO, size=size, weight=weight)

def font_title(size=18, weight="bold"):
    return ctk.CTkFont(family=FONT_FAMILY_MONO, size=size, weight=weight)

def font_body(size=13, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY_UI, size=size, weight=weight)

def font_mono(size=13, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY_MONO, size=size, weight=weight)

def font_button(size=13, weight="bold"):
    return ctk.CTkFont(family=FONT_FAMILY_UI, size=size, weight=weight)


# ==========================================================
#  SETUP GLOBALE (Questa è la funzione che mancava!)[cite: 6]
# ==========================================================
def apply_global_theme():
    """Da chiamare una sola volta all'avvio, prima di creare la finestra root."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")  # base, verra' sovrascritta dai widget[cite: 6]


def style_treeview(style, row_height=32):
    """Applica il tema cyberpunk a un ttk.Treeview."""
    style.theme_use("clam")

    style.configure(
        "Cyber.Treeview",
        background=BG_SURFACE,
        foreground=TEXT_PRIMARY,
        fieldbackground=BG_SURFACE,
        bordercolor=BORDER,
        borderwidth=0,
        rowheight=row_height,
        font=(FONT_FAMILY_UI, 11),
    )
    style.map(
        "Cyber.Treeview",
        background=[("selected", PURPLE_DEEP)],
        foreground=[("selected", TEXT_PRIMARY)],
    )

    style.configure(
        "Cyber.Treeview.Heading",
        background=BG_SURFACE_2,
        foreground=PURPLE_GLOW,
        borderwidth=0,
        relief="flat",
        font=(FONT_FAMILY_MONO, 11, "bold"),
    )
    style.map(
        "Cyber.Treeview.Heading",
        background=[("active", PURPLE_DEEP)],
    )

    style.configure(
        "Cyber.Vertical.TScrollbar",
        background=BG_SURFACE_2,
        troughcolor=BG_BASE,
        bordercolor=BG_BASE,
        arrowcolor=PURPLE_GLOW,
        lightcolor=BG_SURFACE_2,
        darkcolor=BG_SURFACE_2,
        relief="flat",
        borderwidth=0,
        arrowsize=14,
    )
    style.map(
        "Cyber.Vertical.TScrollbar",
        background=[("active", PURPLE_DEEP), ("pressed", PURPLE_DEEP)],
        arrowcolor=[("active", MAGENTA_NEON)],
    )


# ==========================================================
#  STILI ARGOMENTI PER BOTTONI E CARD[cite: 6]
# ==========================================================
def button_primary_kwargs():
    return dict(
        fg_color=PURPLE_PRIMARY,
        hover_color=PURPLE_BRIGHT,
        text_color=TEXT_PRIMARY,
        border_width=0,
        corner_radius=8,
        font=font_button(),
    )

def button_secondary_kwargs():
    return dict(
        fg_color=BG_SURFACE_2,
        hover_color=BORDER,
        text_color=PURPLE_GLOW,
        border_width=1,
        border_color=PURPLE_DEEP,
        corner_radius=8,
        font=font_button(),
    )

def button_danger_kwargs():
    return dict(
        fg_color=DANGER_DIM,
        hover_color=DANGER,
        text_color=TEXT_PRIMARY,
        border_width=0,
        corner_radius=8,
        font=font_button(),
    )

def button_ghost_kwargs():
    return dict(
        fg_color=TRANSPARENT,
        hover_color=BG_SURFACE_2,
        text_color=GRAY_TEXT,
        border_width=0,
        corner_radius=8,
        anchor="w",
        font=font_button(size=13),
    )

def entry_kwargs():
    return dict(
        fg_color=BG_INPUT,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_PRIMARY,
        placeholder_text_color=TEXT_DISABLED,
        corner_radius=6,
        font=font_body(),
    )

def frame_card_kwargs():
    return dict(
        fg_color=BG_SURFACE,
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
    )