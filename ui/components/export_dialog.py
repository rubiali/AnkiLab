# -*- coding: utf-8 -*-
"""
Diálogo de Exportação
=====================

Modal para seleção de formato e configuração de exportação.
"""

import tkinter as tk
from ui.theme import NeuroTheme


class ExportDialog(tk.Toplevel):
    """
    Diálogo modal para configuração de exportação de flashcards.
    
    Permite escolher entre formatos: .apkg, .txt (Anki), .txt (Noji).
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        num_cards: int,
        theme: NeuroTheme,
        title: str = "Exportar"
    ):
        """
        Inicializa o diálogo de exportação.
        
        Args:
            parent: Janela pai.
            num_cards: Número de cards a exportar.
            theme: Tema visual.
            title: Título da janela.
        """
        super().__init__(parent)
        
        self.theme = theme
        self.result = None
        self.deck_name = "Flashcards AnkiLab"
        
        # Configuração da janela
        self.title(title)
        self.geometry("340x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.theme.BG_MAIN)
        
        # Centralização
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 170
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
        self.geometry(f"+{x}+{y}")
        
        # Construção da interface
        self._build_ui(num_cards)
    
    def _build_ui(self, num_cards: int):
        """
        Constrói os componentes do diálogo.
        
        Args:
            num_cards: Número de cards para exibir no header.
        """
        # Header
        self._build_header(num_cards)
        
        # Conteúdo
        self._build_content()
        
        # Botões
        self._build_buttons()
    
    def _build_header(self, num_cards: int):
        """Constrói o cabeçalho do diálogo."""
        header = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        header.pack(fill="x")
        
        header_content = tk.Frame(header, bg=self.theme.BG_SECONDARY)
        header_content.pack(fill="x", padx=16, pady=10)
        
        # Ícone
        tk.Label(
            header_content, text="💾", font=("Segoe UI Emoji", 14),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))
        
        # Textos
        title_frame = tk.Frame(header_content, bg=self.theme.BG_SECONDARY)
        title_frame.pack(side="left")
        
        tk.Label(
            title_frame, text="Exportar Flashcards",
            font=self.theme.get_ui_font(10, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            title_frame, text=f"{num_cards} card(s) prontos",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w")
    
    def _build_content(self):
        """Constrói o conteúdo principal do diálogo."""
        content = tk.Frame(self, bg=self.theme.BG_MAIN)
        content.pack(fill="both", expand=True, padx=16, pady=10)
        
        # Label de formato
        tk.Label(
            content, text="Formato:",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        # Variável de seleção
        self.formato_var = tk.StringVar(value="anki_apkg")
        
        # Opções de formato
        options = [
            ("anki_apkg", "📗 Anki (.apkg)", "Pacote nativo"),
            ("anki_txt", "📄 Anki (.txt)", "Texto tabulado"),
            ("noji_txt", "🟣 Noji (.txt)", "Para Noji"),
        ]
        
        for value, label, desc in options:
            self._build_format_option(content, value, label, desc)
        
        # Campo de nome do deck
        self._build_deck_name_field(content)
    
    def _build_format_option(
        self,
        parent: tk.Frame,
        value: str,
        label: str,
        description: str
    ):
        """
        Constrói uma opção de formato.
        
        Args:
            parent: Frame pai.
            value: Valor da opção.
            label: Texto do label.
            description: Descrição da opção.
        """
        frame = tk.Frame(parent, bg=self.theme.BG_MAIN)
        frame.pack(fill="x", pady=1)
        
        tk.Radiobutton(
            frame, variable=self.formato_var, value=value,
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_MAIN,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0,
            command=self._toggle_deck_name
        ).pack(side="left")
        
        label_frame = tk.Frame(frame, bg=self.theme.BG_MAIN)
        label_frame.pack(side="left")
        
        tk.Label(
            label_frame, text=label,
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            label_frame, text=description,
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
    
    def _build_deck_name_field(self, parent: tk.Frame):
        """Constrói o campo de nome do deck."""
        self.deck_frame = tk.Frame(parent, bg=self.theme.BG_MAIN)
        self.deck_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(
            self.deck_frame, text="Nome do Deck:",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 3))
        
        self.deck_entry = tk.Entry(
            self.deck_frame,
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.theme.BORDER
        )
        self.deck_entry.insert(0, "Flashcards AnkiLab")
        self.deck_entry.pack(fill="x", ipady=3)
    
    def _build_buttons(self):
        """Constrói os botões de ação."""
        btn_frame = tk.Frame(self, bg=self.theme.BG_MAIN)
        btn_frame.pack(fill="x", padx=16, pady=10)
        
        # Botão Cancelar
        tk.Button(
            btn_frame, text="Cancelar",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            relief="flat", padx=12, pady=4,
            command=self._cancelar
        ).pack(side="right", padx=(5, 0))
        
        # Botão Exportar
        tk.Button(
            btn_frame, text="Exportar",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.ACCENT_PRIMARY, fg=self.theme.TEXT_INVERSE,
            relief="flat", padx=12, pady=4,
            command=self._exportar
        ).pack(side="right")
    
    def _toggle_deck_name(self):
        """Habilita/desabilita o campo de nome do deck conforme o formato."""
        if self.formato_var.get() == "anki_apkg":
            self.deck_entry.config(state="normal")
        else:
            self.deck_entry.config(state="disabled")
    
    def _exportar(self):
        """Confirma a exportação e fecha o diálogo."""
        self.deck_name = self.deck_entry.get().strip() or "Flashcards AnkiLab"
        self.result = self.formato_var.get()
        self.destroy()
    
    def _cancelar(self):
        """Cancela e fecha o diálogo."""
        self.result = None
        self.destroy()
