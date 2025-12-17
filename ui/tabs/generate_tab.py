# -*- coding: utf-8 -*-
"""
Aba de Geração de Flashcards
============================

Interface e lógica para criação de novos flashcards a partir de texto.
"""

import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable, List, Dict

from ui.theme import NeuroTheme
from ui.components.export_dialog import ExportDialog
from core.api import generate_cards, refine_cards
from utils.export import export_apkg, export_txt
from core.parser import format_cards_for_export_tab


class GenerateTab:
    """
    Gerencia a aba de geração de flashcards.
    
    Responsável pela entrada de texto, configurações e exibição dos cards gerados.
    """
    
    def __init__(
        self,
        parent: tk.Frame,
        theme: NeuroTheme,
        status_callback: Callable[[str, str], None]
    ):
        """
        Inicializa a aba de geração.
        
        Args:
            parent: Frame pai (container da aba).
            theme: Instância do tema visual.
            status_callback: Função para atualizar status na barra inferior.
        """
        self.parent = parent
        self.theme = theme
        self.update_status = status_callback
        
        # Dados
        self.cards_data: List[Dict[str, str]] = []
        
        # Variáveis de controle
        self.qtd_var = tk.StringVar(value="AUTO")
        self.hard_var = tk.BooleanVar(value=False)
        self.refine_var = tk.BooleanVar(value=False)
        self.cards_count_var = tk.StringVar(value="0")
        
        # Construção da interface
        self._build_ui()
    
    def _build_ui(self):
        """Constrói todos os componentes da aba."""
        main_container = tk.Frame(self.parent, bg=self.theme.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_container.grid_columnconfigure(0, weight=45, minsize=280)
        main_container.grid_columnconfigure(1, weight=55, minsize=320)
        main_container.grid_rowconfigure(0, weight=1)
        
        self._build_left_panel(main_container)
        self._build_right_panel(main_container)
        self._build_options_panel()
        self._build_actions_bar()
        
        self._update_char_counter()
    
    def _build_left_panel(self, parent: tk.Frame):
        """Constrói o painel esquerdo (entrada de texto)."""
        left_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Header
        self._build_panel_header(
            left_panel,
            icon="📝",
            title="ENTRADA DE TEXTO"
        )
        
        # Área de texto
        text_frame = tk.Frame(left_panel, bg=self.theme.BG_SECONDARY, padx=8, pady=6)
        text_frame.pack(fill="both", expand=True)
        
        tk.Label(
            text_frame, text="Cole ou digite o conteúdo para análise:",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        text_border = tk.Frame(text_frame, bg=self.theme.BORDER, padx=1, pady=1)
        text_border.pack(fill="both", expand=True)
        
        self.text_input = tk.Text(
            text_border, wrap="word",
            font=self.theme.get_mono_font(8),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            selectbackground=self.theme.ACCENT_PRIMARY,
            selectforeground=self.theme.BG_MAIN,
            relief="flat", padx=8, pady=6, highlightthickness=0
        )
        self.text_input.pack(fill="both", expand=True)
        self.text_input.bind("<KeyRelease>", self._update_char_counter)
        self.text_input.bind(
            "<FocusIn>",
            lambda e: text_border.config(bg=self.theme.BORDER_FOCUS)
        )
        self.text_input.bind(
            "<FocusOut>",
            lambda e: text_border.config(bg=self.theme.BORDER)
        )
        
        # Barra inferior
        self._build_bottom_bar(left_panel)
    
    def _build_bottom_bar(self, parent: tk.Frame):
        """Constrói a barra inferior com contadores e configuração de quantidade."""
        bottom_bar = tk.Frame(parent, bg=self.theme.BG_TERTIARY, height=34)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        
        bottom_content = tk.Frame(bottom_bar, bg=self.theme.BG_TERTIARY)
        bottom_content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Contadores (esquerda)
        counter_frame = tk.Frame(bottom_content, bg=self.theme.BG_TERTIARY)
        counter_frame.pack(side="left", fill="y")
        
        self.char_counter_label = tk.Label(
            counter_frame, text="0 chars",
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_SECONDARY
        )
        self.char_counter_label.pack(side="left")
        
        tk.Label(
            counter_frame, text=" • ",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_MUTED
        ).pack(side="left")
        
        self.token_counter_label = tk.Label(
            counter_frame, text="~0 tokens",
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_SECONDARY
        )
        self.token_counter_label.pack(side="left")
        
        # Quantidade (direita)
        qtd_frame = tk.Frame(bottom_content, bg=self.theme.BG_TERTIARY)
        qtd_frame.pack(side="right", fill="y")
        
        tk.Label(
            qtd_frame, text="Cards:",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 3))
        
        self.qtd_entry = tk.Entry(
            qtd_frame, textvariable=self.qtd_var,
            font=self.theme.get_mono_font(8),
            bg=self.theme.BG_INPUT, fg=self.theme.ACCENT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            relief="flat", width=6, justify="center",
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.BORDER_FOCUS
        )
        self.qtd_entry.pack(side="left", padx=(0, 3))
        
        tk.Label(
            qtd_frame, text="(n° ou AUTO)",
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_MUTED
        ).pack(side="left")
    
    def _build_right_panel(self, parent: tk.Frame):
        """Constrói o painel direito (preview dos flashcards)."""
        right_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Header com contador
        panel_header = tk.Frame(right_panel, bg=self.theme.BG_TERTIARY, height=32)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=10, pady=6)
        
        # Título
        title_frame = tk.Frame(header_content, bg=self.theme.BG_TERTIARY)
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame, text="🎴", font=("Segoe UI Emoji", 9),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 5))
        
        tk.Label(
            title_frame, text="FLASHCARDS GERADOS",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Badge de contagem
        count_badge = tk.Frame(header_content, bg=self.theme.BG_MAIN, padx=6, pady=1)
        count_badge.pack(side="right")
        
        self.cards_count_label = tk.Label(
            count_badge, textvariable=self.cards_count_var,
            font=self.theme.get_mono_font(8, "bold"),
            bg=self.theme.BG_MAIN, fg=self.theme.ACCENT_PRIMARY
        )
        self.cards_count_label.pack(side="left")
        
        tk.Label(
            count_badge, text=" cards",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # Área de preview
        preview_frame = tk.Frame(right_panel, bg=self.theme.BG_SECONDARY, padx=8, pady=6)
        preview_frame.pack(fill="both", expand=True)
        
        preview_border = tk.Frame(preview_frame, bg=self.theme.BORDER, padx=1, pady=1)
        preview_border.pack(fill="both", expand=True)
        
        preview_container = tk.Frame(preview_border, bg=self.theme.BG_INPUT)
        preview_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(
            preview_container, orient="vertical",
            bg=self.theme.BG_TERTIARY, troughcolor=self.theme.BG_INPUT,
            activebackground=self.theme.ACCENT_PRIMARY, highlightthickness=0
        )
        scrollbar.pack(side="right", fill="y")
        
        self.preview = tk.Text(
            preview_container, wrap="word",
            font=self.theme.get_mono_font(8),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_PRIMARY,
            relief="flat", padx=8, pady=6, highlightthickness=0,
            yscrollcommand=scrollbar.set, state="disabled", cursor="arrow"
        )
        self.preview.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self.preview.yview)
        
        # Configuração de tags de formatação
        self._configure_preview_tags()
        self._show_preview_placeholder()
    
    def _configure_preview_tags(self):
        """Configura as tags de formatação do preview."""
        self.preview.tag_configure(
            "header",
            foreground=self.theme.CARD_HEADER,
            font=self.theme.get_mono_font(8, "bold")
        )
        self.preview.tag_configure(
            "pergunta",
            foreground=self.theme.CARD_Q,
            font=self.theme.get_mono_font(8, "bold")
        )
        self.preview.tag_configure(
            "resposta",
            foreground=self.theme.CARD_A,
            font=self.theme.get_mono_font(8)
        )
        self.preview.tag_configure(
            "separator",
            foreground=self.theme.TEXT_MUTED,
            font=self.theme.get_mono_font(6)
        )
        self.preview.tag_configure(
            "processing",
            foreground=self.theme.ACCENT_PRIMARY,
            font=self.theme.get_mono_font(8),
            justify="center"
        )
        self.preview.tag_configure(
            "error",
            foreground=self.theme.ERROR,
            font=self.theme.get_mono_font(8)
        )
        self.preview.tag_configure(
            "card_num",
            foreground=self.theme.ACCENT_SECONDARY,
            font=self.theme.get_mono_font(7, "bold")
        )
    
    def _build_options_panel(self):
        """Constrói o painel de opções (Hard Mode, Refinamento)."""
        options_container = tk.Frame(self.parent, bg=self.theme.BG_MAIN)
        options_container.pack(fill="x", padx=10, pady=(0, 5))
        
        options_panel = tk.Frame(options_container, bg=self.theme.BG_SECONDARY)
        options_panel.pack(fill="x")
        
        options_content = tk.Frame(options_panel, bg=self.theme.BG_SECONDARY)
        options_content.pack(fill="x", padx=10, pady=8)
        
        # Título
        title_frame = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame, text="⚙️", font=("Segoe UI Emoji", 8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 4))
        
        tk.Label(
            title_frame, text="CONFIGURAÇÕES",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # Separador
        tk.Frame(
            options_content, bg=self.theme.BORDER, width=1
        ).pack(side="left", fill="y", padx=12)
        
        # Hard Mode
        self._build_option_checkbox(
            options_content,
            variable=self.hard_var,
            icon="🧠",
            title="Hard Mode",
            description="Cards focados em aplicação",
            command=self._update_mode_display
        )
        
        # Separador
        tk.Frame(
            options_content, bg=self.theme.BORDER, width=1
        ).pack(side="left", fill="y", padx=10)
        
        # Refinamento
        self._build_option_checkbox(
            options_content,
            variable=self.refine_var,
            icon="🔁",
            title="Segunda Passada",
            description="Revisão automática"
        )
        
        # Indicador de modo
        self.mode_indicator = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        self.mode_indicator.pack(side="right", fill="y")
        
        self.mode_label = tk.Label(
            self.mode_indicator, text="MODO: NORMAL",
            font=self.theme.get_mono_font(7, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.ACCENT_PRIMARY
        )
        self.mode_label.pack(side="right")
    
    def _build_option_checkbox(
        self,
        parent: tk.Frame,
        variable: tk.BooleanVar,
        icon: str,
        title: str,
        description: str,
        command: Callable = None
    ):
        """
        Constrói um checkbox de opção com ícone e descrição.
        
        Args:
            parent: Frame pai.
            variable: Variável de controle do checkbox.
            icon: Emoji do ícone.
            title: Título da opção.
            description: Descrição curta.
            command: Callback ao clicar.
        """
        frame = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        frame.pack(side="left", fill="y", padx=(0, 10))
        
        check = tk.Checkbutton(
            frame, variable=variable,
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            activeforeground=self.theme.TEXT_PRIMARY,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0, bd=0,
            command=command
        )
        check.pack(side="left")
        
        label_frame = tk.Frame(frame, bg=self.theme.BG_SECONDARY)
        label_frame.pack(side="left", fill="y")
        
        title_label = tk.Label(
            label_frame, text=f"{icon} {title}",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, cursor="hand2"
        )
        title_label.pack(anchor="w")
        title_label.bind("<Button-1>", lambda e: variable.set(not variable.get()))
        
        tk.Label(
            label_frame, text=description,
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
    
    def _build_actions_bar(self):
        """Constrói a barra de ações (botões)."""
        actions_container = tk.Frame(self.parent, bg=self.theme.BG_MAIN)
        actions_container.pack(fill="x", padx=10, pady=(0, 5))
        
        actions_panel = tk.Frame(actions_container, bg=self.theme.BG_TERTIARY)
        actions_panel.pack(fill="x")
        
        actions_content = tk.Frame(actions_panel, bg=self.theme.BG_TERTIARY)
        actions_content.pack(fill="x", padx=10, pady=8)
        
        # Botão principal
        self.btn_gerar = self._create_button(
            actions_content,
            text="  🚀  GERAR FLASHCARDS  ",
            primary=True,
            command=self.gerar_cards
        )
        self.btn_gerar.pack(side="left", padx=(0, 10))
        
        # Separador
        tk.Frame(
            actions_content, bg=self.theme.BORDER, width=1
        ).pack(side="left", fill="y", padx=10)
        
        # Botões secundários
        self.btn_exportar = self._create_button(
            actions_content,
            text="  💾 Exportar  ",
            command=self.exportar_cards
        )
        self.btn_exportar.pack(side="left", padx=(0, 5))
        
        self.btn_copiar = self._create_button(
            actions_content,
            text="  📋 Copiar  ",
            command=self.copiar_clipboard
        )
        self.btn_copiar.pack(side="left", padx=(0, 5))
        
        self.btn_limpar = self._create_button(
            actions_content,
            text="  🔄 Limpar  ",
            command=self.limpar_tudo
        )
        self.btn_limpar.pack(side="left")
        
        # Atalho
        tk.Label(
            actions_content, text="Ctrl+Enter: Gerar",
            font=self.theme.get_mono_font(6),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_MUTED
        ).pack(side="right")
    
    def _create_button(
        self,
        parent: tk.Frame,
        text: str,
        primary: bool = False,
        command: Callable = None
    ) -> tk.Button:
        """
        Cria um botão estilizado.
        
        Args:
            parent: Frame pai.
            text: Texto do botão.
            primary: Se True, usa estilo de destaque.
            command: Callback ao clicar.
        
        Returns:
            Instância do botão criado.
        """
        if primary:
            bg = self.theme.ACCENT_PRIMARY
            fg = self.theme.TEXT_INVERSE
            hover_bg = self.theme.ACCENT_TERTIARY
            font = self.theme.get_ui_font(9, "bold")
            padx, pady = 10, 5
        else:
            bg = self.theme.BG_SECONDARY
            fg = self.theme.TEXT_PRIMARY
            hover_bg = self.theme.BG_HOVER
            font = self.theme.get_ui_font(8)
            padx, pady = 8, 4
        
        btn = tk.Button(
            parent, text=text, font=font,
            bg=bg, fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief="flat", cursor="hand2",
            padx=padx, pady=pady,
            command=command
        )
        
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        
        return btn
    
    def _build_panel_header(self, parent: tk.Frame, icon: str, title: str):
        """
        Constrói um header padrão para painéis.
        
        Args:
            parent: Frame pai.
            icon: Emoji do ícone.
            title: Título do painel.
        """
        panel_header = tk.Frame(parent, bg=self.theme.BG_TERTIARY, height=32)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=10, pady=6)
        
        tk.Label(
            header_content, text=icon, font=("Segoe UI Emoji", 9),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 5))
        
        tk.Label(
            header_content, text=title,
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
    
    # ==========================================================================
    # MÉTODOS DE ATUALIZAÇÃO DA INTERFACE
    # ==========================================================================
    
    def _update_char_counter(self, event=None):
        """Atualiza os contadores de caracteres e tokens."""
        texto = self.text_input.get("1.0", tk.END).strip()
        chars = len(texto)
        self.char_counter_label.config(text=f"{chars:,} chars")
        self.token_counter_label.config(text=f"~{chars // 4:,} tokens")
    
    def _update_mode_display(self):
        """Atualiza o indicador de modo (Normal/Hard)."""
        if self.hard_var.get():
            self.mode_label.config(text="MODO: HARD", fg=self.theme.ERROR)
        else:
            self.mode_label.config(text="MODO: NORMAL", fg=self.theme.ACCENT_PRIMARY)
    
    def _show_preview_placeholder(self):
        """Exibe o placeholder inicial no preview."""
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        placeholder = """

   ╭──────────────────────────────╮
   │                              │
   │   Cole um texto no painel    │
   │   esquerdo e clique em       │
   │   "GERAR FLASHCARDS"         │
   │                              │
   │   Os cards aparecerão aqui   │
   │                              │
   ╰──────────────────────────────╯
"""
        self.preview.insert("1.0", placeholder, "processing")
        self.preview.config(state="disabled")
    
    def _insert_preview_formatted(self, cards: List[Dict[str, str]]):
        """
        Insere os cards formatados no preview.
        
        Args:
            cards: Lista de cards para exibir.
        """
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        
        if not cards:
            self.preview.insert("1.0", "Nenhum card gerado.", "error")
            self.preview.config(state="disabled")
            return
        
        self.cards_count_var.set(str(len(cards)))
        self.cards_data = cards
        
        for i, c in enumerate(cards):
            self.preview.insert(tk.END, f"┌─ Card {i + 1}\n", "card_num")
            self.preview.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            
            a_lines = c['a'].split('\n')
            for j, line in enumerate(a_lines):
                prefix = "│ A: " if j == 0 else "│    "
                self.preview.insert(tk.END, f"{prefix}{line}\n", "resposta")
            
            separator = "└─────────────────────────────\n"
            if i < len(cards) - 1:
                separator += "\n"
            self.preview.insert(tk.END, separator, "separator")
        
        self.preview.config(state="disabled")
    
    def _set_busy(self, is_busy: bool, msg: str = ""):
        """
        Define o estado ocupado da interface.
        
        Args:
            is_busy: Se True, desabilita botões.
            msg: Mensagem de status.
        """
        state = "disabled" if is_busy else "normal"
        
        self.btn_gerar.config(state=state)
        self.btn_exportar.config(state=state)
        self.btn_copiar.config(state=state)
        self.btn_limpar.config(state=state)
        
        if is_busy:
            self.update_status(msg if msg else "Processando...", "warning")
    
    # ==========================================================================
    # AÇÕES PRINCIPAIS
    # ==========================================================================
    
    def gerar_cards(self):
        """Inicia o processo de geração de flashcards."""
        texto = self.text_input.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showerror("Erro", "Insira um texto para análise.")
            return
        
        hard = bool(self.hard_var.get())
        do_refine = bool(self.refine_var.get())
        
        self._set_busy(True, "Gerando flashcards...")
        
        # Mostra indicador de processamento
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        msg = "\n\n    ⏳ Processando...\n"
        if do_refine:
            msg += "    (Refinamento ativado)\n"
        self.preview.insert(tk.END, msg, "processing")
        self.preview.config(state="disabled")
        
        self.cards_count_var.set("...")
        
        def chamar_api():
            try:
                qtd = self.qtd_var.get().strip()
                
                self.update_status("Gerando (1ª passada)...", "warning")
                cards = generate_cards(texto, qtd, hard)
                
                if do_refine and len(cards) >= 1:
                    self.update_status("Refinando (2ª passada)...", "warning")
                    cards = refine_cards(texto, cards, hard)
                
                self.parent.after(
                    0,
                    lambda: self._finalizar_geracao(cards, hard, do_refine)
                )
                
            except Exception as e:
                self.parent.after(0, lambda m=str(e): self._erro_geracao(m))
        
        threading.Thread(target=chamar_api, daemon=True).start()
    
    def _finalizar_geracao(
        self,
        cards: List[Dict[str, str]],
        hard: bool,
        refined: bool
    ):
        """
        Finaliza o processo de geração.
        
        Args:
            cards: Cards gerados.
            hard: Se modo hard estava ativo.
            refined: Se refinamento foi aplicado.
        """
        self._insert_preview_formatted(cards)
        mode_txt = "HARD" if hard else "NORMAL"
        ref_txt = " + refinado" if refined else ""
        self._set_busy(False)
        self.update_status(f"✓ {len(cards)} card(s) • {mode_txt}{ref_txt}", "success")
    
    def _erro_geracao(self, mensagem: str):
        """
        Trata erro durante a geração.
        
        Args:
            mensagem: Mensagem de erro.
        """
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, f"\n  ❌ Erro:\n\n  {mensagem}", "error")
        self.preview.config(state="disabled")
        self.cards_count_var.set("0")
        self._set_busy(False)
        self.update_status("Erro na geração", "error")
        messagebox.showerror("Erro", mensagem)
    
    def exportar_cards(self):
        """Abre o diálogo de exportação."""
        if not self.cards_data:
            messagebox.showwarning("Aviso", "Nenhum card para exportar.")
            return
        
        dialog = ExportDialog(
            self.parent.winfo_toplevel(),
            len(self.cards_data),
            self.theme
        )
        self.parent.winfo_toplevel().wait_window(dialog)
        
        if not dialog.result:
            return
        
        if dialog.result == "anki_apkg":
            path = filedialog.asksaveasfilename(
                defaultextension=".apkg",
                filetypes=[("Pacote Anki", "*.apkg")],
                title="Salvar .apkg",
                initialfile=f"{dialog.deck_name}.apkg"
            )
            if path:
                try:
                    export_apkg(path, dialog.deck_name, self.cards_data)
                    self.update_status(f"Exportado: {len(self.cards_data)} cards", "success")
                    messagebox.showinfo(
                        "Sucesso",
                        f"✓ {len(self.cards_data)} cards exportados!\n\nNo Anki: Arquivo → Importar"
                    )
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
        else:
            target = "anki" if dialog.result == "anki_txt" else "noji"
            filename = f"flashcards_{target}.txt"
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Texto", "*.txt")],
                initialfile=filename
            )
            if path:
                try:
                    export_txt(path, self.cards_data)
                    self.update_status(f"Exportado: {len(self.cards_data)} cards", "success")
                    messagebox.showinfo(
                        "Sucesso",
                        f"✓ {len(self.cards_data)} cards exportados!"
                    )
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
    
    def copiar_clipboard(self):
        """Copia os cards para a área de transferência."""
        if not self.cards_data:
            messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar.")
            return
        
        root = self.parent.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(format_cards_for_export_tab(self.cards_data))
        root.update()
        self.update_status("Copiado! (formato Tab)", "success")
    
    def limpar_tudo(self):
        """Limpa todos os campos e reseta a interface."""
        self.text_input.delete("1.0", tk.END)
        self.qtd_var.set("AUTO")
        self.hard_var.set(False)
        self.refine_var.set(False)
        self.cards_data = []
        self.cards_count_var.set("0")
        self._show_preview_placeholder()
        self._update_char_counter()
        self._update_mode_display()
        self.update_status("Campos limpos", "info")
