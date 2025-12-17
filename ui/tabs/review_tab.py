# -*- coding: utf-8 -*-
"""
Aba de Revisão de Deck
======================

Interface e lógica para auditoria e revisão de decks existentes.
"""

import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable, List, Dict
import os

from config import MODEL_ADVANCED
from ui.theme import NeuroTheme
from ui.components.export_dialog import ExportDialog
from core.api import review_deck
from core.parser import (
    parse_apkg_cards,
    parse_flashcard_file,
    parse_csv_cards,
    format_cards_for_prompt,
    format_cards_for_export_tab,
    extract_new_cards_from_audit,
    extract_cards_from_review,
    extract_report_from_review,
)
from utils.export import export_apkg, export_txt


class ReviewTab:
    """
    Gerencia a aba de revisão de decks.
    
    Permite carregar CSVs existentes e executar auditoria ou revisão completa.
    """
    
    def __init__(
        self,
        parent: tk.Frame,
        theme: NeuroTheme,
        status_callback: Callable[[str, str], None]
    ):
        """
        Inicializa a aba de revisão.
        
        Args:
            parent: Frame pai (container da aba).
            theme: Instância do tema visual.
            status_callback: Função para atualizar status.
        """
        self.parent = parent
        self.theme = theme
        self.update_status = status_callback
        
        # Dados
        self.loaded_csv_cards: List[Dict[str, str]] = []
        self.review_cards_data: List[Dict[str, str]] = []
        
        # Variáveis de controle
        self.assunto_var = tk.StringVar(value="")
        self.review_mode_var = tk.StringVar(value="audit")
        self.loaded_count_var = tk.StringVar(value="0 cards carregados")
        self.review_count_var = tk.StringVar(value="0")
        
        # Construção da interface
        self._build_ui()
    
    def _build_ui(self):
        """Constrói todos os componentes da aba."""
        main_container = tk.Frame(self.parent, bg=self.theme.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_container.grid_columnconfigure(0, weight=40, minsize=300)
        main_container.grid_columnconfigure(1, weight=60, minsize=400)
        main_container.grid_rowconfigure(0, weight=1)
        
        self._build_left_panel(main_container)
        self._build_right_panel(main_container)
        self._build_actions_bar()
    
    def _build_left_panel(self, parent: tk.Frame):
        """Constrói o painel esquerdo (configurações)."""
        left_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Header
        self._build_panel_header(
            left_panel,
            icon="📂",
            title="CONFIGURAÇÃO DA REVISÃO"
        )
        
        # Conteúdo
        content_frame = tk.Frame(left_panel, bg=self.theme.BG_SECONDARY, padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)
        
        # Campo de assunto
        self._build_subject_field(content_frame)
        
        # Botão carregar CSV
        self._build_csv_loader(content_frame)
        
        # Separador
        tk.Frame(content_frame, bg=self.theme.BORDER, height=1).pack(fill="x", pady=15)
        
        # Modo de revisão
        self._build_review_mode_selector(content_frame)
        
        # Separador
        tk.Frame(content_frame, bg=self.theme.BORDER, height=1).pack(fill="x", pady=15)
        
        # Preview do deck carregado
        self._build_loaded_preview(content_frame)
    
    def _build_subject_field(self, parent: tk.Frame):
        """Constrói o campo de tema/assunto."""
        tk.Label(
            parent, text="Tema/Assunto do Deck:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        assunto_border = tk.Frame(parent, bg=self.theme.BORDER, padx=1, pady=1)
        assunto_border.pack(fill="x", pady=(0, 10))
        
        self.assunto_entry = tk.Entry(
            assunto_border,
            textvariable=self.assunto_var,
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            relief="flat", highlightthickness=0
        )
        self.assunto_entry.pack(fill="x", ipady=6, padx=2, pady=2)
        self.assunto_entry.insert(0, "Ex: Pensamento Computacional")
        
        def on_focus_in(e):
            if self.assunto_entry.get().startswith("Ex:"):
                self.assunto_entry.delete(0, tk.END)
            assunto_border.config(bg=self.theme.BORDER_FOCUS)
        
        self.assunto_entry.bind("<FocusIn>", on_focus_in)
        self.assunto_entry.bind(
            "<FocusOut>",
            lambda e: assunto_border.config(bg=self.theme.BORDER)
        )
    
    def _build_csv_loader(self, parent: tk.Frame):
        """Constrói o botão e indicador de carregamento de arquivo."""
        tk.Label(
            parent, text="Arquivo:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(5, 4))
        
        load_frame = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        load_frame.pack(fill="x", pady=(0, 5))
        
        # RENOMEADO: texto mais genérico
        self.btn_load_csv = tk.Button(
            load_frame, text="  📁 Carregar Arquivo  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.ACCENT_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.ACCENT_TERTIARY,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self._load_file
        )
        self.btn_load_csv.pack(side="left")
        
        self.loaded_label = tk.Label(
            load_frame, textvariable=self.loaded_count_var,
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        )
        self.loaded_label.pack(side="left", padx=(10, 0))

    def _load_file(self):
        """Carrega um arquivo de flashcards (CSV, TXT ou APKG)."""
        path = filedialog.askopenfilename(
            filetypes=[
                ("Todos Suportados", "*.apkg *.csv *.txt *.tsv"),
                ("Pacote Anki", "*.apkg"),
                ("CSV", "*.csv"),
                ("Texto", "*.txt *.tsv"),
                ("Todos", "*.*")
            ],
            title="Carregar arquivo de flashcards"
        )
        if not path:
            return
        
        try:
            # Usa a função unificada que detecta o formato
            cards = parse_flashcard_file(path)
            
            if not cards:
                ext = os.path.splitext(path)[1].lower()
                if ext == '.apkg':
                    msg = (
                        "Não foi possível extrair cards do arquivo .apkg.\n\n"
                        "Possíveis causas:\n"
                        "• O deck pode estar vazio\n"
                        "• Formato de nota incompatível (precisa ter 2+ campos)\n"
                        "• Arquivo corrompido"
                    )
                else:
                    msg = (
                        "Não foi possível extrair cards do arquivo.\n"
                        "Verifique o formato (2 colunas: pergunta, resposta)."
                    )
                messagebox.showerror("Erro", msg)
                return
            
            self.loaded_csv_cards = cards
            
            # Detecta o tipo de arquivo para exibir
            ext = os.path.splitext(path)[1].lower()
            file_type = "APKG" if ext == ".apkg" else "CSV/TXT"
            self.loaded_count_var.set(f"{len(cards)} cards ({file_type})")
            
            # Atualiza preview
            self.loaded_preview.config(state="normal")
            self.loaded_preview.delete("1.0", tk.END)
            
            preview_text = f"Fonte: {os.path.basename(path)}\n"
            preview_text += f"Total: {len(cards)} cards\n\n"
            
            for i, c in enumerate(cards[:5]):
                q_short = c['q'][:60] + "..." if len(c['q']) > 60 else c['q']
                # Remove quebras de linha para preview compacto
                q_short = q_short.replace('\n', ' ')
                preview_text += f"{i+1}. {q_short}\n"
            
            if len(cards) > 5:
                preview_text += f"\n... e mais {len(cards) - 5} cards"
            
            self.loaded_preview.insert("1.0", preview_text)
            self.loaded_preview.config(state="disabled")
            
            self.update_status(f"Arquivo carregado: {len(cards)} cards", "success")
            
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")

    def _build_review_mode_selector(self, parent: tk.Frame):
        """Constrói o seletor de modo de revisão."""
        tk.Label(
            parent, text="Modo de Revisão:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        # Opção: Auditoria
        self._build_radio_option(
            parent,
            variable=self.review_mode_var,
            value="audit",
            icon="🔎",
            title="Auditoria de Cobertura",
            description="Analisa lacunas e sugere novos cards"
        )
        
        # Opção: Revisão Final
        self._build_radio_option(
            parent,
            variable=self.review_mode_var,
            value="final",
            icon="✨",
            title="Revisão Final Completa",
            description="Melhora, remove, modifica e adiciona cards"
        )
    
    def _build_radio_option(
        self,
        parent: tk.Frame,
        variable: tk.StringVar,
        value: str,
        icon: str,
        title: str,
        description: str
    ):
        """
        Constrói uma opção de radio button.
        
        Args:
            parent: Frame pai.
            variable: Variável de controle.
            value: Valor da opção.
            icon: Emoji do ícone.
            title: Título da opção.
            description: Descrição.
        """
        frame = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        frame.pack(fill="x", pady=2)
        
        tk.Radiobutton(
            frame, variable=variable, value=value,
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0
        ).pack(side="left")
        
        label_frame = tk.Frame(frame, bg=self.theme.BG_SECONDARY)
        label_frame.pack(side="left", fill="y")
        
        tk.Label(
            label_frame, text=f"{icon} {title}",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            label_frame, text=description,
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
    
    def _build_loaded_preview(self, parent: tk.Frame):
        """Constrói o preview do deck carregado."""
        tk.Label(
            parent, text="Preview do Deck Carregado:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        preview_border = tk.Frame(parent, bg=self.theme.BORDER, padx=1, pady=1)
        preview_border.pack(fill="both", expand=True)
        
        self.loaded_preview = tk.Text(
            preview_border, wrap="word",
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_SECONDARY,
            relief="flat", padx=6, pady=4, highlightthickness=0,
            state="disabled", height=8
        )
        self.loaded_preview.pack(fill="both", expand=True)
    
    def _build_right_panel(self, parent: tk.Frame):
        """Constrói o painel direito (resultado da revisão)."""
        right_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Header
        panel_header = tk.Frame(right_panel, bg=self.theme.BG_TERTIARY, height=32)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=10, pady=6)
        
        tk.Label(
            header_content, text="📊", font=("Segoe UI Emoji", 9),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 5))
        
        tk.Label(
            header_content, text="RESULTADO DA REVISÃO",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Badge de contagem
        count_badge = tk.Frame(header_content, bg=self.theme.BG_MAIN, padx=6, pady=1)
        count_badge.pack(side="right")
        
        self.review_count_label = tk.Label(
            count_badge, textvariable=self.review_count_var,
            font=self.theme.get_mono_font(8, "bold"),
            bg=self.theme.BG_MAIN, fg=self.theme.ACCENT_PRIMARY
        )
        self.review_count_label.pack(side="left")
        
        tk.Label(
            count_badge, text=" cards",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # Área de resultado
        result_frame = tk.Frame(right_panel, bg=self.theme.BG_SECONDARY, padx=8, pady=6)
        result_frame.pack(fill="both", expand=True)
        
        result_border = tk.Frame(result_frame, bg=self.theme.BORDER, padx=1, pady=1)
        result_border.pack(fill="both", expand=True)
        
        result_container = tk.Frame(result_border, bg=self.theme.BG_INPUT)
        result_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(
            result_container, orient="vertical",
            bg=self.theme.BG_TERTIARY, troughcolor=self.theme.BG_INPUT,
            activebackground=self.theme.ACCENT_PRIMARY, highlightthickness=0
        )
        scrollbar.pack(side="right", fill="y")
        
        self.review_result = tk.Text(
            result_container, wrap="word",
            font=self.theme.get_mono_font(8),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_PRIMARY,
            relief="flat", padx=8, pady=6, highlightthickness=0,
            yscrollcommand=scrollbar.set, state="disabled", cursor="arrow"
        )
        self.review_result.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self.review_result.yview)
        
        # Configuração de tags
        self._configure_result_tags()
        self._show_review_placeholder()
    
    def _configure_result_tags(self):
        """Configura as tags de formatação do resultado."""
        tags = {
            "header": {"foreground": self.theme.CARD_HEADER, "font": self.theme.get_mono_font(9, "bold")},
            "subheader": {"foreground": self.theme.ACCENT_SECONDARY, "font": self.theme.get_mono_font(8, "bold")},
            "pergunta": {"foreground": self.theme.CARD_Q, "font": self.theme.get_mono_font(8, "bold")},
            "resposta": {"foreground": self.theme.CARD_A, "font": self.theme.get_mono_font(8)},
            "info": {"foreground": self.theme.INFO, "font": self.theme.get_mono_font(8)},
            "warning": {"foreground": self.theme.WARNING, "font": self.theme.get_mono_font(8)},
            "success": {"foreground": self.theme.SUCCESS, "font": self.theme.get_mono_font(8)},
            "error": {"foreground": self.theme.ERROR, "font": self.theme.get_mono_font(8)},
            "muted": {"foreground": self.theme.TEXT_MUTED, "font": self.theme.get_mono_font(7)},
            "processing": {"foreground": self.theme.ACCENT_PRIMARY, "font": self.theme.get_mono_font(8), "justify": "center"},
        }
        
        for tag_name, config in tags.items():
            self.review_result.tag_configure(tag_name, **config)
    
    def _build_actions_bar(self):
        """Constrói a barra de ações."""
        actions_container = tk.Frame(self.parent, bg=self.theme.BG_MAIN)
        actions_container.pack(fill="x", padx=10, pady=(0, 5))
        
        actions_panel = tk.Frame(actions_container, bg=self.theme.BG_TERTIARY)
        actions_panel.pack(fill="x")
        
        actions_content = tk.Frame(actions_panel, bg=self.theme.BG_TERTIARY)
        actions_content.pack(fill="x", padx=10, pady=8)
        
        # Botão principal
        self.btn_revisar = self._create_button(
            actions_content,
            text="  🔍  EXECUTAR REVISÃO  ",
            primary=True,
            command=self._executar_revisao
        )
        self.btn_revisar.pack(side="left", padx=(0, 10))
        
        # Separador
        tk.Frame(
            actions_content, bg=self.theme.BORDER, width=1
        ).pack(side="left", fill="y", padx=10)
        
        # Botões secundários
        self.btn_export_review = self._create_button(
            actions_content,
            text="  💾 Exportar Resultado  ",
            command=self._exportar_review
        )
        self.btn_export_review.pack(side="left", padx=(0, 5))
        
        self.btn_copy_review = self._create_button(
            actions_content,
            text="  📋 Copiar Cards  ",
            command=self._copiar_review
        )
        self.btn_copy_review.pack(side="left", padx=(0, 5))
        
        self.btn_clear_review = self._create_button(
            actions_content,
            text="  🔄 Limpar  ",
            command=self._limpar_review
        )
        self.btn_clear_review.pack(side="left")
        
        # Indicador de modelo
        tk.Label(
            actions_content, text=f"Usando: {MODEL_ADVANCED}",
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
        """Cria um botão estilizado."""
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
        """Constrói um header padrão para painéis."""
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
    
    def _show_review_placeholder(self):
        """Exibe o placeholder inicial no resultado."""
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        placeholder = """

   ╭──────────────────────────────────╮
   │                                  │
   │   1. Informe o tema/assunto      │
   │   2. Carregue um arquivo         │
   │   3. Escolha o modo de revisão   │
   │   4. Clique em EXECUTAR REVISÃO  │
   │                                  │
   │   O resultado aparecerá aqui     │
   │                                  │
   ╰──────────────────────────────────╯
"""
        self.review_result.insert("1.0", placeholder, "processing")
        self.review_result.config(state="disabled")
    
    def _set_busy(self, is_busy: bool, msg: str = ""):
        """Define o estado ocupado da interface."""
        state = "disabled" if is_busy else "normal"
        
        self.btn_revisar.config(state=state)
        self.btn_export_review.config(state=state)
        self.btn_copy_review.config(state=state)
        self.btn_clear_review.config(state=state)
        self.btn_load_csv.config(state=state)
        
        if is_busy:
            self.update_status(msg if msg else "Processando...", "warning")
    
    # ==========================================================================
    # AÇÕES PRINCIPAIS
    # ==========================================================================
    
    def _load_csv(self):
        """Carrega um arquivo de flashcards."""
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("Texto", "*.txt"), ("Todos", "*.*")],
            title="Carregar arquivo de flashcards"
        )
        if not path:
            return
        
        try:
            cards = parse_csv_cards(file_path=path)
            
            if not cards:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível extrair cards do arquivo.\n"
                    "Verifique o formato (2 colunas: pergunta, resposta)."
                )
                return
            
            self.loaded_csv_cards = cards
            self.loaded_count_var.set(f"{len(cards)} cards carregados")
            
            # Atualiza preview
            self.loaded_preview.config(state="normal")
            self.loaded_preview.delete("1.0", tk.END)
            
            preview_text = f"Total: {len(cards)} cards\n\n"
            for i, c in enumerate(cards[:5]):
                q_short = c['q'][:60] + "..." if len(c['q']) > 60 else c['q']
                preview_text += f"{i+1}. {q_short}\n"
            
            if len(cards) > 5:
                preview_text += f"\n... e mais {len(cards) - 5} cards"
            
            self.loaded_preview.insert("1.0", preview_text)
            self.loaded_preview.config(state="disabled")
            
            self.update_status(f"CSV carregado: {len(cards)} cards", "success")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
    
    def _executar_revisao(self):
        """Inicia o processo de revisão do deck."""
        assunto = self.assunto_var.get().strip()
        if not assunto or assunto.startswith("Ex:"):
            messagebox.showerror("Erro", "Informe o tema/assunto do deck.")
            return
        
        if not self.loaded_csv_cards:
            messagebox.showerror("Erro", "Carregue um arquivo primeiro.")
            return
        
        mode = self.review_mode_var.get()
        
        self._set_busy(True, "Executando revisão...")
        
        # Mostra indicador de processamento
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        
        if mode == "audit":
            msg = "\n\n    ⏳ Executando Auditoria de Cobertura...\n\n"
            msg += "    Analisando lacunas e sugerindo novos cards...\n"
        else:
            msg = "\n\n    ⏳ Executando Revisão Final Completa...\n\n"
            msg += "    Melhorando, removendo e adicionando cards...\n"
        
        self.review_result.insert(tk.END, msg, "processing")
        self.review_result.config(state="disabled")
        
        self.review_count_var.set("...")
        
        def chamar_api():
            try:
                cards_text = format_cards_for_prompt(self.loaded_csv_cards)
                
                self.update_status(f"Processando com {MODEL_ADVANCED}...", "warning")
                
                response = review_deck(assunto, cards_text, mode)
                
                self.parent.after(
                    0,
                    lambda: self._finalizar_revisao(response, mode)
                )
                
            except Exception as e:
                self.parent.after(0, lambda m=str(e): self._erro_revisao(m))
        
        threading.Thread(target=chamar_api, daemon=True).start()
    
    def _finalizar_revisao(self, response: str, mode: str):
        """
        Finaliza o processo de revisão.
        
        Args:
            response: Resposta completa da IA.
            mode: Modo de revisão ("audit" ou "final").
        """
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        
        if mode == "audit":
            # Extrai novos cards sugeridos
            new_cards = extract_new_cards_from_audit(response)
            self.review_cards_data = new_cards
            self.review_count_var.set(str(len(new_cards)))
            
            # Mostra resposta formatada
            self._format_audit_response(response)
        else:
            # Extrai cards finais e relatório
            final_cards = extract_cards_from_review(response)
            report = extract_report_from_review(response)
            
            self.review_cards_data = final_cards
            self.review_count_var.set(str(len(final_cards)))
            
            # Mostra relatório e cards
            self._format_review_response(report, final_cards)
        
        self.review_result.config(state="disabled")
        self._set_busy(False)
        
        mode_txt = "Auditoria" if mode == "audit" else "Revisão Final"
        self.update_status(
            f"✓ {mode_txt} concluída • {len(self.review_cards_data)} cards",
            "success"
        )
    
    def _format_audit_response(self, response: str):
        """
        Formata a resposta de auditoria para exibição.
        
        Args:
            response: Resposta completa da IA.
        """
        lines = response.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped.startswith("==="):
                self.review_result.insert(tk.END, line + "\n", "header")
            elif line_stripped.startswith("Q:"):
                self.review_result.insert(tk.END, line + "\n", "pergunta")
            elif line_stripped.startswith("A:"):
                self.review_result.insert(tk.END, line + "\n", "resposta")
            elif "ALTA" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "error")
            elif "MÉDIA" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "warning")
            elif "BAIXA" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "info")
            elif line_stripped.startswith("•") or line_stripped.startswith("-"):
                self.review_result.insert(tk.END, line + "\n", "info")
            elif any(line_stripped.startswith(str(i) + ".") for i in range(1, 100)):
                self.review_result.insert(tk.END, line + "\n", "info")
            else:
                self.review_result.insert(tk.END, line + "\n")
    
    def _format_review_response(self, report: str, cards: List[Dict[str, str]]):
        """
        Formata a resposta de revisão final para exibição.
        
        Args:
            report: Relatório de alterações.
            cards: Cards finais.
        """
        # Header do relatório
        self.review_result.insert(tk.END, "═" * 50 + "\n", "muted")
        self.review_result.insert(tk.END, "  RELATÓRIO DE ALTERAÇÕES\n", "header")
        self.review_result.insert(tk.END, "═" * 50 + "\n\n", "muted")
        
        # Conteúdo do relatório
        lines = report.split('\n')
        for line in lines:
            line_stripped = line.strip()
            
            if "REMOVIDOS" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "error")
            elif "MODIFICADOS" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "warning")
            elif "DIVIDIDOS" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "info")
            elif "ADICIONADOS" in line_stripped:
                self.review_result.insert(tk.END, line + "\n", "success")
            elif "ESTATÍSTICAS" in line_stripped or line_stripped.startswith("==="):
                self.review_result.insert(tk.END, line + "\n", "subheader")
            elif line_stripped.startswith("•") or line_stripped.startswith("-"):
                self.review_result.insert(tk.END, line + "\n", "muted")
            else:
                self.review_result.insert(tk.END, line + "\n")
        
        # Header dos cards finais
        self.review_result.insert(tk.END, "\n" + "═" * 50 + "\n", "muted")
        self.review_result.insert(tk.END, f"  CARDS FINAIS ({len(cards)} cards)\n", "header")
        self.review_result.insert(tk.END, "═" * 50 + "\n\n", "muted")
        
        # Lista de cards
        for i, c in enumerate(cards):
            self.review_result.insert(tk.END, f"┌─ Card {i + 1}\n", "subheader")
            self.review_result.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            
            a_lines = c['a'].split('\n')
            for j, aline in enumerate(a_lines):
                prefix = "│ A: " if j == 0 else "│    "
                self.review_result.insert(tk.END, f"{prefix}{aline}\n", "resposta")
            
            self.review_result.insert(tk.END, "└" + "─" * 40 + "\n\n", "muted")
    
    def _erro_revisao(self, mensagem: str):
        """
        Trata erro durante a revisão.
        
        Args:
            mensagem: Mensagem de erro.
        """
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        self.review_result.insert(tk.END, f"\n  ❌ Erro:\n\n  {mensagem}", "error")
        self.review_result.config(state="disabled")
        self.review_count_var.set("0")
        self._set_busy(False)
        self.update_status("Erro na revisão", "error")
        messagebox.showerror("Erro", mensagem)
    
    def _exportar_review(self):
        """Exporta o resultado da revisão."""
        if not self.review_cards_data:
            messagebox.showwarning("Aviso", "Nenhum card para exportar.")
            return
        
        # Pergunta se quer incluir cards originais (modo auditoria)
        cards_to_export = self.review_cards_data
        export_label = "novos"
        
        if self.review_mode_var.get() == "audit" and self.loaded_csv_cards:
            escolha = messagebox.askyesnocancel(
                "Exportar Cards",
                f"Novos cards sugeridos: {len(self.review_cards_data)}\n"
                f"Cards originais do deck: {len(self.loaded_csv_cards)}\n\n"
                f"Deseja incluir os cards ORIGINAIS junto com os novos?\n\n"
                f"• SIM = Originais + Novos ({len(self.loaded_csv_cards) + len(self.review_cards_data)} cards)\n"
                f"• NÃO = Apenas Novos ({len(self.review_cards_data)} cards)\n"
                f"• CANCELAR = Voltar"
            )
            
            if escolha is None:
                return
            elif escolha:
                cards_to_export = self.loaded_csv_cards + self.review_cards_data
                export_label = "originais + novos"
        
        # Abre diálogo de exportação
        dialog = ExportDialog(
            self.parent.winfo_toplevel(),
            len(cards_to_export),
            self.theme,
            title="Exportar Resultado da Revisão"
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
                    export_apkg(path, dialog.deck_name, cards_to_export)
                    self.update_status(
                        f"Exportado: {len(cards_to_export)} cards ({export_label})",
                        "success"
                    )
                    messagebox.showinfo(
                        "Sucesso",
                        f"✓ {len(cards_to_export)} cards exportados!\n\nNo Anki: Arquivo → Importar"
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
                    export_txt(path, cards_to_export)
                    self.update_status(
                        f"Exportado: {len(cards_to_export)} cards ({export_label})",
                        "success"
                    )
                    messagebox.showinfo(
                        "Sucesso",
                        f"✓ {len(cards_to_export)} cards exportados!"
                    )
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
    
    def _copiar_review(self):
        """Copia os cards da revisão para a área de transferência."""
        if not self.review_cards_data:
            messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar.")
            return
        
        root = self.parent.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(format_cards_for_export_tab(self.review_cards_data))
        root.update()
        self.update_status("Copiado! (formato Tab)", "success")
    
    def _limpar_review(self):
        """Limpa todos os campos da aba de revisão."""
        self.assunto_var.set("")
        self.loaded_csv_cards = []
        self.review_cards_data = []
        self.loaded_count_var.set("0 cards carregados")
        self.review_count_var.set("0")
        self.review_mode_var.set("audit")
        
        self.loaded_preview.config(state="normal")
        self.loaded_preview.delete("1.0", tk.END)
        self.loaded_preview.config(state="disabled")
        
        self._show_review_placeholder()
        self.update_status("Campos limpos", "info")
