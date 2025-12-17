# -*- coding: utf-8 -*-
"""
Classe Principal da Aplicação
=============================

Gerencia a janela principal, notebook de abas e coordenação geral.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from config import APP_NAME, APP_VERSION, APP_TAGLINE, MODEL_NAME, MODEL_ADVANCED, MODEL_REFINEMENT
from .theme import NeuroTheme
from .tabs.generate_tab import GenerateTab
from .tabs.review_tab import ReviewTab


class AnkiLabApp:
    """
    Aplicação principal AnkiLab.
    
    Gerencia a janela, header, footer e coordena as abas de funcionalidades.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa a aplicação.
        
        Args:
            root: Janela principal do tkinter.
        """
        self.root = root
        self.theme = NeuroTheme
        
        # Configuração da janela
        self._configure_window()
        
        # Construção da interface
        self._build_header()
        self._build_notebook()
        self._build_footer()
    
    def _configure_window(self):
        """Configura propriedades da janela principal."""
        self.root.title(f"{APP_NAME} • {APP_TAGLINE}")
        self.root.geometry("950x700")
        self.root.minsize(850, 550)
        self.root.configure(bg=self.theme.BG_MAIN)
    
    def _build_header(self):
        """Constrói o cabeçalho da aplicação."""
        header = tk.Frame(self.root, bg=self.theme.BG_SECONDARY, height=55)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg=self.theme.BG_SECONDARY)
        header_inner.pack(fill="both", expand=True, padx=12, pady=6)
        
        # Logo e título (esquerda)
        self._build_header_left(header_inner)
        
        # Badge do modelo (direita)
        self._build_header_right(header_inner)
        
        # Separador
        tk.Frame(self.root, bg=self.theme.BORDER, height=1).pack(fill="x", side="top")
    
    def _build_header_left(self, parent: tk.Frame):
        """Constrói a parte esquerda do header (logo e título)."""
        left_frame = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        left_frame.pack(side="left", fill="y")
        
        # Ícone
        tk.Label(
            left_frame, text="🧠", font=("Segoe UI Emoji", 16),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        
        # Textos
        title_frame = tk.Frame(left_frame, bg=self.theme.BG_SECONDARY)
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame, text=APP_NAME,
            font=self.theme.get_ui_font(12, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            title_frame, text=APP_TAGLINE,
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w")
    
    def _build_header_right(self, parent: tk.Frame):
        """Constrói a parte direita do header (badge do modelo)."""
        right_frame = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        right_frame.pack(side="right", fill="y")
        
        model_frame = tk.Frame(right_frame, bg=self.theme.BG_TERTIARY, padx=6, pady=3)
        model_frame.pack(side="right")
        
        tk.Label(
            model_frame, text="⚡", font=("Segoe UI Emoji", 8),
            bg=self.theme.BG_TERTIARY, fg=self.theme.ACCENT_PRIMARY
        ).pack(side="left", padx=(0, 3))
        
        tk.Label(
            model_frame, text=f"{MODEL_NAME} / {MODEL_ADVANCED} / {MODEL_REFINEMENT}",
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
    
    def _build_notebook(self):
        """Constrói o notebook com as abas."""
        # Estilo customizado
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure(
            'Custom.TNotebook',
            background=self.theme.BG_MAIN,
            borderwidth=0
        )
        style.configure(
            'Custom.TNotebook.Tab',
            background=self.theme.BG_TERTIARY,
            foreground=self.theme.TEXT_SECONDARY,
            padding=[15, 8],
            font=self.theme.get_ui_font(9)
        )
        style.map(
            'Custom.TNotebook.Tab',
            background=[('selected', self.theme.BG_SECONDARY)],
            foreground=[('selected', self.theme.ACCENT_PRIMARY)]
        )
        
        # Notebook
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Aba de Geração
        tab_generate = tk.Frame(self.notebook, bg=self.theme.BG_MAIN)
        self.notebook.add(tab_generate, text="  📝 Gerar Cards  ")
        self.generate_tab = GenerateTab(tab_generate, self.theme, self._update_status)
        
        # Aba de Revisão
        tab_review = tk.Frame(self.notebook, bg=self.theme.BG_MAIN)
        self.notebook.add(tab_review, text="  🔍 Revisar Deck  ")
        self.review_tab = ReviewTab(tab_review, self.theme, self._update_status)
        
        # Atalho global
        self.root.bind("<Control-Return>", lambda e: self.generate_tab.gerar_cards())
    
    def _build_footer(self):
        """Constrói o rodapé com status."""
        tk.Frame(self.root, bg=self.theme.BORDER, height=1).pack(fill="x", side="bottom")
        
        footer = tk.Frame(self.root, bg=self.theme.BG_SECONDARY, height=26)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=self.theme.BG_SECONDARY)
        footer_content.pack(fill="both", expand=True, padx=10, pady=4)
        
        # Status (esquerda)
        status_frame = tk.Frame(footer_content, bg=self.theme.BG_SECONDARY)
        status_frame.pack(side="left", fill="y")
        
        self.status_icon = tk.Label(
            status_frame, text="◉", font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.SUCCESS
        )
        self.status_icon.pack(side="left", padx=(0, 3))
        
        self.status_label = tk.Label(
            status_frame, text="Pronto",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left")
        
        # Versão (direita)
        tk.Label(
            footer_content, text=f"{APP_NAME} {APP_VERSION}",
            font=self.theme.get_mono_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(side="right")
    
    def _update_status(self, msg: str, status_type: str = "info"):
        """
        Atualiza o status no rodapé.
        
        Args:
            msg: Mensagem de status.
            status_type: Tipo (info, success, warning, error).
        """
        color_map = {
            "info": self.theme.INFO,
            "success": self.theme.SUCCESS,
            "warning": self.theme.WARNING,
            "error": self.theme.ERROR
        }
        
        self.root.after(0, lambda: (
            self.status_icon.config(fg=color_map.get(status_type, self.theme.INFO)),
            self.status_label.config(text=msg)
        ))
