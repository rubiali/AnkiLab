"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         🧠 ANKILAB — COGNITIVE FLASHCARD ENGINE               ║
║                              Tema: NEURO / COGNITIVE LAB                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from openai import OpenAI
import genanki


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  PALETA DE CORES — NEURO / COGNITIVE LAB                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class NeuroTheme:
    """Sistema de cores centralizado para o tema Neuro/Cognitive Lab."""
    
    # ── Fundos ──────────────────────────────────────────────────────────────────
    BG_MAIN = "#0f1419"
    BG_SECONDARY = "#1a1f26"
    BG_TERTIARY = "#242b35"
    BG_INPUT = "#1e252e"
    BG_HOVER = "#2a3441"
    
    # ── Acentos ─────────────────────────────────────────────────────────────────
    ACCENT_PRIMARY = "#00d4aa"
    ACCENT_SECONDARY = "#9b7dff"
    ACCENT_TERTIARY = "#00a3cc"
    
    # ── Textos ──────────────────────────────────────────────────────────────────
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    TEXT_INVERSE = "#0f1419"
    
    # ── Semânticas ──────────────────────────────────────────────────────────────
    SUCCESS = "#3fb950"
    WARNING = "#d29922"
    ERROR = "#f85149"
    INFO = "#58a6ff"
    
    # ── Bordas ──────────────────────────────────────────────────────────────────
    BORDER = "#30363d"
    BORDER_FOCUS = "#00d4aa"
    SEPARATOR = "#21262d"
    
    # ── Flashcards ──────────────────────────────────────────────────────────────
    CARD_Q = "#58a6ff"
    CARD_A = "#3fb950"
    CARD_SCORE = "#d2a8ff"
    CARD_HEADER = "#f0883e"
    
    # ── Fontes (escala compacta) ────────────────────────────────────────────────
    FONT_MONO = ("Consolas", "Cascadia Code", "monospace")
    FONT_UI = ("Segoe UI", "sans-serif")
    
    @classmethod
    def get_mono_font(cls, size=8, weight="normal"):
        return (cls.FONT_MONO[0], size, weight)
    
    @classmethod
    def get_ui_font(cls, size=8, weight="normal"):
        return (cls.FONT_UI[0], size, weight)


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  VALIDAÇÃO INICIAL                                                            ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def validar_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "🔑 API Key Não Encontrada",
            "Defina a variável de ambiente OPENAI_API_KEY."
        )
        return None
    return key


api_key = validar_api_key()
if not api_key:
    raise SystemExit(1)


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURAÇÕES GLOBAIS                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

client = OpenAI(api_key=api_key)
MODEL_NAME = "gpt-4.1-mini"
APP_VERSION = "v2.0"
APP_NAME = "AnkiLab"
APP_TAGLINE = "Cognitive Flashcard Engine"


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  PROMPTS                                                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

PROMPT_NORMAL = """
Você é um especialista em aprendizagem, ciência cognitiva e sistemas de repetição espaçada (Anki).

Sua tarefa é analisar o texto fornecido e gerar flashcards de ALTA QUALIDADE, focados em:
- compreensão profunda
- retenção de longo prazo
- aplicação real dos conceitos

━━━━━━━━━━
REGRAS FUNDAMENTAIS
━━━━━━━━━━
- NÃO crie cartões genéricos, óbvios ou puramente descritivos.
- NÃO crie cartões respondíveis apenas por senso comum.
- Cada cartão deve testar APENAS UMA ideia central.
- Evite repetir a mesma ideia em cartões diferentes.
- Sempre que um conceito puder ser cobrado como DEFINIÇÃO ou APLICAÇÃO,
  a APLICAÇÃO é OBRIGATÓRIA.
- Para cada conceito central, gere NO MÁXIMO:
  • 1 cartão definicional
- Use definições SOMENTE quando indispensáveis.

━━━━━━━━━━
REGRAS DE RETENÇÃO (CRÍTICAS)
━━━━━━━━━━
- A resposta deve ser CURTA, OBJETIVA e MENSURÁVEL.
- Preferencialmente 1 frase.
- No máximo 2 frases curtas.
- Se uma resposta exigir mais de uma ideia, DIVIDA em mais de um cartão.
- O aluno deve conseguir avaliar claramente se acertou ou errou.

━━━━━━━━━━
TIPOS DE CARTÃO (ordem obrigatória)
━━━━━━━━━━
1) Aplicação prática
2) Distinção / comparação
3) Causa e consequência
4) Definição essencial (última opção)

━━━━━━━━━━
EXEMPLO DE CARTÃO RUIM (NÃO FAÇA ASSIM)
━━━━━━━━━━
Q: O que é back-end?
A: É a parte do software que processa dados.
→ Problema: Definição rasa, não testa compreensão real.

Q: Qual o papel da computação em nossas vidas?
A: A computação está presente em várias atividades do cotidiano.
→ Problema: Genérico, respondível por senso comum.

━━━━━━━━━━
EXEMPLO DE CARTÃO BOM (FAÇA ASSIM)
━━━━━━━━━━
Q: Por que a validação de formulário deve estar no back-end e não apenas no front-end?
A: Porque o front-end pode ser manipulado; o back-end garante segurança e integridade.

Q: Qual a consequência de escolher um hardware inferior às exigências do software?
A: Baixa performance, travamentos ou incompatibilidade.

━━━━━━━━━━
CONTROLE DE QUALIDADE
━━━━━━━━━━
- Se dois cartões testarem a mesma ideia, mantenha apenas o MAIS DESAFIADOR.
- Evite cartões que apenas repitam frases do texto original.

━━━━━━━━━━
MODO DE GERAÇÃO
━━━━━━━━━━
Modo: {MODO}

- Se MANUAL:
  Gere exatamente {QTD} flashcards.

- Se AUTOMÁTICO:
  Decida a quantidade ideal de flashcards, priorizando:
  - máximo valor educacional
  - máxima retenção
  - mínima redundância
  - evitar fragmentação excessiva

━━━━━━━━━━
FORMATO DE SAÍDA (OBRIGATÓRIO - SIGA EXATAMENTE)
━━━━━━━━━━
REGRAS ESTRITAS:
1. Use EXATAMENTE o formato abaixo.
2. NÃO escreva NENHUM texto antes ou depois dos cartões.
3. NÃO adicione introduções, explicações, conclusões ou comentários.
4. NÃO use markdown (sem **, ##, ```, -, •, etc.).
5. NÃO numere os cartões.
6. Cada cartão deve começar com "Q:" e ter "A:" na linha seguinte.
7. Separe cada cartão com UMA linha em branco.

Formato:
Q: <pergunta>
A: <resposta curta e objetiva>

Q: <pergunta>
A: <resposta curta e objetiva>

━━━━━━━━━━
TEXTO PARA ANÁLISE
━━━━━━━━━━
{TEXTO}
"""

PROMPT_HARD = """
Você é um especialista em aprendizagem, ciência cognitiva e Anki. Gere flashcards DIFÍCEIS e de alta retenção.

Objetivo: criar cartões que NÃO possam ser respondidos por reconhecimento, apenas por compreensão real.

━━━━━━━━━━
REGRAS HARD (OBRIGATÓRIAS)
━━━━━━━━━━
- Priorize aplicação, consequência e distinção. DEFINIÇÃO só se for inevitável (máximo 10%).
- Cada cartão testa UMA ideia.
- Evite qualquer pergunta "O que é X?" (quase sempre é ruim).
- Sempre que possível, faça perguntas do tipo:
  - "O que acontece se...?"
  - "Qual a consequência de...?"
  - "Por que ... (com justificativa causal)?"
  - "Como aplicar ... em uma situação concreta?"
  - "Diferencie X de Y em um caso prático"
- Respostas curtas: preferencialmente 1 frase, no máximo 2 frases curtas.
- Evite repetir ideias: se dois cartões forem parecidos, mantenha o mais desafiador.

━━━━━━━━━━
MODO DE GERAÇÃO
━━━━━━━━━━
Modo: {MODO}

- Se MANUAL:
  Gere exatamente {QTD} flashcards.

- Se AUTOMÁTICO:
  Decida a quantidade ideal (NEM pouco, NEM redundante), priorizando valor educacional.

━━━━━━━━━━
FORMATO DE SAÍDA (OBRIGATÓRIO - SIGA EXATAMENTE)
━━━━━━━━━━
REGRAS ESTRITAS:
1. Use EXATAMENTE o formato abaixo.
2. NÃO escreva NENHUM texto antes ou depois dos cartões.
3. NÃO adicione introduções, explicações, conclusões ou comentários.
4. NÃO use markdown (sem **, ##, ```, -, •, etc.).
5. NÃO numere os cartões.
6. Cada cartão deve começar com "Q:" e ter "A:" na linha seguinte.
7. Separe cada cartão com UMA linha em branco.

Formato:
Q: <pergunta>
A: <resposta>

Q: <pergunta>
A: <resposta>

━━━━━━━━━━
TEXTO PARA ANÁLISE
━━━━━━━━━━
{TEXTO}
"""

REFINE_PROMPT = """
Você é um revisor extremamente rigoroso de flashcards para Anki.

Tarefa: Refinar os cartões abaixo para maximizar retenção e qualidade, respeitando o texto original.

Você deve:
- Remover redundâncias (se dois cartões testarem a mesma ideia, mantenha o melhor).
- Transformar cartões definicionais em aplicação/consequência sempre que possível.
- Encurtar respostas: preferencialmente 1 frase, no máximo 2 frases curtas.
- Garantir 1 ideia por cartão.
- Evitar frases copiadas do texto (reformule).
- Manter o conteúdo fiel ao texto.

Nível de dificuldade: {DIFICULDADE}
- Se HARD: seja agressivo em converter definição para aplicação, e elimine cartões fáceis.
- Se NORMAL: mantenha equilíbrio entre clareza e desafio.

━━━━━━━━━━
FORMATO DE SAÍDA (OBRIGATÓRIO - SIGA EXATAMENTE)
━━━━━━━━━━
REGRAS ESTRITAS:
1. Use EXATAMENTE o formato abaixo.
2. NÃO escreva NENHUM texto antes ou depois dos cartões.
3. NÃO adicione introduções, explicações, conclusões ou comentários.
4. NÃO use markdown (sem **, ##, ```, -, •, etc.).
5. NÃO numere os cartões.
6. Cada cartão deve começar com "Q:" e ter "A:" na linha seguinte.
7. Separe cada cartão com UMA linha em branco.
8. Devolva APENAS os cartões refinados.

Formato:
Q: <pergunta>
A: <resposta>

Q: <pergunta>
A: <resposta>

━━━━━━━━━━
TEXTO ORIGINAL (referência)
━━━━━━━━━━
{TEXTO}

━━━━━━━━━━
CARTÕES PARA REFINAR
━━━━━━━━━━
{CARDS}
"""


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  FUNÇÕES DE PARSING E SCORING                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def parse_cards(raw: str):
    if not raw:
        return []
    
    raw = raw.replace("\r\n", "\n").strip()
    lines_clean = []
    in_code_block = False
    
    for ln in raw.split("\n"):
        s = ln.strip()
        if s.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if s.startswith("[Score:") or s.startswith("#"):
            continue
        if s.startswith("---") or s.startswith("***") or s.startswith("==="):
            continue
        if s.startswith("**") and s.endswith("**") and len(s) > 4:
            continue
        if s.lower().startswith("flashcard") and ":" not in s[10:]:
            continue
        if s.lower().startswith("cartão") or s.lower().startswith("cartao"):
            if ":" not in s[7:]:
                continue
        if s.lower().startswith("aqui estão") or s.lower().startswith("aqui estao"):
            continue
        if s.lower().startswith("seguem") or s.lower().startswith("abaixo"):
            continue
        if s.lower().startswith("espero que"):
            continue
        lines_clean.append(ln)
    
    raw = "\n".join(lines_clean).strip()
    raw = re.sub(r"\*\*\s*(Q:)", r"\1", raw)
    raw = re.sub(r"\*\*\s*(A:)", r"\1", raw)
    raw = re.sub(r"(Q:)\s*\*\*", r"\1 ", raw)
    raw = re.sub(r"(A:)\s*\*\*", r"\1 ", raw)
    raw = raw.replace("**", "")
    raw = re.sub(r"^\d+[\.\)]\s*(Q:)", r"\1", raw, flags=re.MULTILINE)
    
    blocks = re.split(r"\n\s*\n+", raw)
    cards = []
    
    for blk in blocks:
        blk = blk.strip()
        if not blk:
            continue
        
        q_lines, a_lines = [], []
        cur = None
        
        for ln in blk.split("\n"):
            s = ln.strip()
            if not s:
                continue
            
            q_match = re.match(r"^(Q|P|Pergunta)\s*:\s*(.*)$", s, re.IGNORECASE)
            a_match = re.match(r"^(A|R|Resposta)\s*:\s*(.*)$", s, re.IGNORECASE)
            
            if q_match:
                cur = "Q"
                content = q_match.group(2).strip()
                if content:
                    q_lines.append(content)
            elif a_match:
                cur = "A"
                content = a_match.group(2).strip()
                if content:
                    a_lines.append(content)
            else:
                if cur == "Q":
                    q_lines.append(s)
                elif cur == "A":
                    a_lines.append(s)
        
        q = re.sub(r"\s+", " ", " ".join(q_lines).strip())
        a = re.sub(r"\s+", " ", " ".join(a_lines).strip())
        
        if q and a:
            cards.append({"q": q, "a": a})
    
    return cards


def word_count(s: str) -> int:
    s = re.sub(r"\s+", " ", s).strip()
    return len(s.split(" ")) if s else 0


def score_card(q: str, a: str, hard: bool) -> float:
    q_l, a_l = q.lower().strip(), a.lower().strip()
    score = 5.0

    aw = word_count(a)
    if aw <= 12:
        score += 2.0
    elif aw <= 20:
        score += 1.0
    elif aw <= 28:
        score += 0.2
    else:
        score -= 1.5

    good_starts = [
        "por que", "como", "qual a consequência", "qual a consequencia",
        "o que acontece", "em que aspecto", "diferencie", "compare",
        "qual a diferença", "qual a diferenca", "qual seria a consequência",
        "o que pode ocorrer", "como aplicar", "por que é", "por que e",
        "quando devemos", "em que situação", "qual o impacto", "qual o efeito"
    ]
    if any(q_l.startswith(gs) for gs in good_starts):
        score += 1.8

    if q_l.startswith("o que é") or q_l.startswith("o que e"):
        score -= 2.5 if hard else 1.8

    generic_markers = [
        "em nossas vidas", "no dia a dia", "no cotidiano", "de forma geral",
        "qual o papel", "explique", "descreva", "fale sobre", "cite"
    ]
    if any(m in q_l for m in generic_markers):
        score -= 1.0 if hard else 0.6

    practical_markers = [
        "ao escolher", "ao rodar", "ao desenvolver", "em um sistema",
        "em um aplicativo", "em um jogo", "servidor", "banco de dados",
        "front-end", "back-end", "hardware", "requisitos", "teste",
        "segurança", "desempenho", "incompatibilidade", "usuário", "projeto"
    ]
    if any(m in q_l for m in practical_markers):
        score += 0.9

    if any(x in a_l for x in ["porque", "pois", "assim", "portanto", "logo", "então"]):
        score += 0.4

    return round(max(0, min(10, score)), 1)


def format_cards_for_export_tab(cards):
    return "\n".join(f"{c['q']}\t{c['a']}" for c in cards) + ("\n" if cards else "")


def format_cards_for_refine(cards):
    lines = []
    for c in cards:
        lines.extend([f"Q: {c['q']}", f"A: {c['a']}", ""])
    return "\n".join(lines).strip()


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  CLASSE PRINCIPAL — AnkiLabApp (ESCALA COMPACTA PARA NOTEBOOKS)               ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class AnkiLabApp:
    """
    Aplicação AnkiLab com escala compacta para notebooks.
    Proporções reduzidas em ~25% mantendo o layout idêntico.
    """
    
    def __init__(self, root):
        self.root = root
        self.theme = NeuroTheme
        self.cards_data = []
        
        # ══════════════════════════════════════════════════════════════════════
        # ESCALA COMPACTA: 880x540
        # ══════════════════════════════════════════════════════════════════════
        self.root.title(f"{APP_NAME} • {APP_TAGLINE}")
        self.root.geometry("880x650")
        self.root.minsize(750, 450)
        self.root.configure(bg=self.theme.BG_MAIN)
        
        # Variáveis de controle
        self.qtd_var = tk.StringVar(value="AUTO")
        self.hard_var = tk.BooleanVar(value=False)
        self.refine_var = tk.BooleanVar(value=False)
        self.cards_count_var = tk.StringVar(value="0")
        self.avg_score_var = tk.StringVar(value="—")
        
        # Construir interface
        self._build_header()
        self._build_main_content()
        self._build_options_panel()
        self._build_actions_bar()
        self._build_footer()
        
        self._update_char_counter()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  HEADER (altura: 40px)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_header(self):
        header = tk.Frame(self.root, bg=self.theme.BG_SECONDARY, height=55)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg=self.theme.BG_SECONDARY)
        header_inner.pack(fill="both", expand=True, padx=12, pady=6)
        
        # Logo e título
        left_frame = tk.Frame(header_inner, bg=self.theme.BG_SECONDARY)
        left_frame.pack(side="left", fill="y")
        
        tk.Label(
            left_frame, text="🧠", font=("Segoe UI Emoji", 16),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        
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
        
        # Badge do modelo
        right_frame = tk.Frame(header_inner, bg=self.theme.BG_SECONDARY)
        right_frame.pack(side="right", fill="y")
        
        model_frame = tk.Frame(right_frame, bg=self.theme.BG_TERTIARY, padx=6, pady=3)
        model_frame.pack(side="right")
        
        tk.Label(
            model_frame, text="⚡", font=("Segoe UI Emoji", 8),
            bg=self.theme.BG_TERTIARY, fg=self.theme.ACCENT_PRIMARY
        ).pack(side="left", padx=(0, 3))
        
        tk.Label(
            model_frame, text=MODEL_NAME,
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Separador
        tk.Frame(self.root, bg=self.theme.BORDER, height=1).pack(fill="x", side="top")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  MAIN CONTENT (padding: 10px)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_main_content(self):
        main_container = tk.Frame(self.root, bg=self.theme.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_container.grid_columnconfigure(0, weight=45, minsize=280)
        main_container.grid_columnconfigure(1, weight=55, minsize=320)
        main_container.grid_rowconfigure(0, weight=1)
        
        self._build_left_panel(main_container)
        self._build_right_panel(main_container)
    
    def _build_left_panel(self, parent):
        """Painel esquerdo: entrada de texto."""
        left_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Header do painel (altura: 32px)
        panel_header = tk.Frame(left_panel, bg=self.theme.BG_TERTIARY, height=32)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=10, pady=6)
        
        tk.Label(
            header_content, text="📝", font=("Segoe UI Emoji", 9),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 5))
        
        tk.Label(
            header_content, text="ENTRADA DE TEXTO",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Área de texto (padding: 8px)
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
        self.text_input.bind("<FocusIn>", lambda e: text_border.config(bg=self.theme.BORDER_FOCUS))
        self.text_input.bind("<FocusOut>", lambda e: text_border.config(bg=self.theme.BORDER))
        
        # Barra inferior (altura: 34px)
        bottom_bar = tk.Frame(left_panel, bg=self.theme.BG_TERTIARY, height=34)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        
        bottom_content = tk.Frame(bottom_bar, bg=self.theme.BG_TERTIARY)
        bottom_content.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Contador
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
        
        # Quantidade
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
    
    def _build_right_panel(self, parent):
        """Painel direito: preview dos flashcards."""
        right_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Header com métricas (altura: 32px)
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
        
        # Métricas
        metrics_frame = tk.Frame(header_content, bg=self.theme.BG_TERTIARY)
        metrics_frame.pack(side="right", fill="y")
        
        # Badge contagem
        count_badge = tk.Frame(metrics_frame, bg=self.theme.BG_MAIN, padx=6, pady=1)
        count_badge.pack(side="left", padx=(0, 6))
        
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
        
        # Badge score
        score_badge = tk.Frame(metrics_frame, bg=self.theme.BG_MAIN, padx=6, pady=1)
        score_badge.pack(side="left")
        
        tk.Label(
            score_badge, text="Score: ",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        self.avg_score_label = tk.Label(
            score_badge, textvariable=self.avg_score_var,
            font=self.theme.get_mono_font(8, "bold"),
            bg=self.theme.BG_MAIN, fg=self.theme.ACCENT_SECONDARY
        )
        self.avg_score_label.pack(side="left")
        
        tk.Label(
            score_badge, text="/10",
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_MUTED
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
        
        # Tags de formatação
        self.preview.tag_configure("header", foreground=self.theme.CARD_HEADER, font=self.theme.get_mono_font(8, "bold"))
        self.preview.tag_configure("score", foreground=self.theme.CARD_SCORE, font=self.theme.get_mono_font(7, "bold"))
        self.preview.tag_configure("pergunta", foreground=self.theme.CARD_Q, font=self.theme.get_mono_font(8, "bold"))
        self.preview.tag_configure("resposta", foreground=self.theme.CARD_A, font=self.theme.get_mono_font(8))
        self.preview.tag_configure("separator", foreground=self.theme.TEXT_MUTED, font=self.theme.get_mono_font(6))
        self.preview.tag_configure("processing", foreground=self.theme.ACCENT_PRIMARY, font=self.theme.get_mono_font(8), justify="center")
        self.preview.tag_configure("error", foreground=self.theme.ERROR, font=self.theme.get_mono_font(8))
        
        self._show_preview_placeholder()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  OPTIONS PANEL (padding: 10px)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_options_panel(self):
        options_container = tk.Frame(self.root, bg=self.theme.BG_MAIN)
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
        tk.Frame(options_content, bg=self.theme.BORDER, width=1).pack(side="left", fill="y", padx=12)
        
        # Hard Mode
        hard_frame = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        hard_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.hard_check = tk.Checkbutton(
            hard_frame, variable=self.hard_var,
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            activeforeground=self.theme.TEXT_PRIMARY,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0, bd=0,
            command=self._update_mode_display
        )
        self.hard_check.pack(side="left")
        
        hard_label_frame = tk.Frame(hard_frame, bg=self.theme.BG_SECONDARY)
        hard_label_frame.pack(side="left", fill="y")
        
        hard_title = tk.Label(
            hard_label_frame, text="🧠 Hard Mode",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, cursor="hand2"
        )
        hard_title.pack(anchor="w")
        hard_title.bind("<Button-1>", lambda e: self.hard_var.set(not self.hard_var.get()) or self._update_mode_display())
        
        tk.Label(
            hard_label_frame, text="Cards focados em aplicação",
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # Separador
        tk.Frame(options_content, bg=self.theme.BORDER, width=1).pack(side="left", fill="y", padx=10)
        
        # Refinamento
        refine_frame = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        refine_frame.pack(side="left", fill="y")
        
        self.refine_check = tk.Checkbutton(
            refine_frame, variable=self.refine_var,
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            activeforeground=self.theme.TEXT_PRIMARY,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0, bd=0
        )
        self.refine_check.pack(side="left")
        
        refine_label_frame = tk.Frame(refine_frame, bg=self.theme.BG_SECONDARY)
        refine_label_frame.pack(side="left", fill="y")
        
        refine_title = tk.Label(
            refine_label_frame, text="🔁 Segunda Passada",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, cursor="hand2"
        )
        refine_title.pack(anchor="w")
        refine_title.bind("<Button-1>", lambda e: self.refine_var.set(not self.refine_var.get()))
        
        tk.Label(
            refine_label_frame, text="Revisão automática",
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # Indicador de modo
        self.mode_indicator = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        self.mode_indicator.pack(side="right", fill="y")
        
        self.mode_label = tk.Label(
            self.mode_indicator, text="MODO: NORMAL",
            font=self.theme.get_mono_font(7, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.ACCENT_PRIMARY
        )
        self.mode_label.pack(side="right")
    
    def _update_mode_display(self):
        if self.hard_var.get():
            self.mode_label.config(text="MODO: HARD", fg=self.theme.ERROR)
        else:
            self.mode_label.config(text="MODO: NORMAL", fg=self.theme.ACCENT_PRIMARY)
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  ACTIONS BAR (padding: 10px, botões compactos)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_actions_bar(self):
        actions_container = tk.Frame(self.root, bg=self.theme.BG_MAIN)
        actions_container.pack(fill="x", padx=10, pady=(0, 5))
        
        actions_panel = tk.Frame(actions_container, bg=self.theme.BG_TERTIARY)
        actions_panel.pack(fill="x")
        
        actions_content = tk.Frame(actions_panel, bg=self.theme.BG_TERTIARY)
        actions_content.pack(fill="x", padx=10, pady=8)
        
        # Botão principal
        self.btn_gerar = tk.Button(
            actions_content, text="  🚀  GERAR FLASHCARDS  ",
            font=self.theme.get_ui_font(9, "bold"),
            bg=self.theme.ACCENT_PRIMARY, fg=self.theme.TEXT_INVERSE,
            activebackground=self.theme.ACCENT_TERTIARY,
            activeforeground=self.theme.TEXT_INVERSE,
            relief="flat", cursor="hand2", padx=10, pady=5,
            command=self.gerar_cards
        )
        self.btn_gerar.pack(side="left", padx=(0, 10))
        self.btn_gerar.bind("<Enter>", lambda e: self.btn_gerar.config(bg=self.theme.ACCENT_TERTIARY))
        self.btn_gerar.bind("<Leave>", lambda e: self.btn_gerar.config(bg=self.theme.ACCENT_PRIMARY))
        
        # Separador
        tk.Frame(actions_content, bg=self.theme.BORDER, width=1).pack(side="left", fill="y", padx=10)
        
        # Botões secundários
        self.btn_exportar = tk.Button(
            actions_content, text="  💾 Exportar  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self.exportar_cards
        )
        self.btn_exportar.pack(side="left", padx=(0, 5))
        self.btn_exportar.bind("<Enter>", lambda e: self.btn_exportar.config(bg=self.theme.BG_HOVER))
        self.btn_exportar.bind("<Leave>", lambda e: self.btn_exportar.config(bg=self.theme.BG_SECONDARY))
        
        self.btn_copiar = tk.Button(
            actions_content, text="  📋 Copiar  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self.copiar_clipboard
        )
        self.btn_copiar.pack(side="left", padx=(0, 5))
        self.btn_copiar.bind("<Enter>", lambda e: self.btn_copiar.config(bg=self.theme.BG_HOVER))
        self.btn_copiar.bind("<Leave>", lambda e: self.btn_copiar.config(bg=self.theme.BG_SECONDARY))
        
        self.btn_limpar = tk.Button(
            actions_content, text="  🔄 Limpar  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self.limpar_tudo
        )
        self.btn_limpar.pack(side="left")
        self.btn_limpar.bind("<Enter>", lambda e: self.btn_limpar.config(bg=self.theme.BG_HOVER))
        self.btn_limpar.bind("<Leave>", lambda e: self.btn_limpar.config(bg=self.theme.BG_SECONDARY))
        
        # Atalho
        tk.Label(
            actions_content, text="Ctrl+Enter: Gerar",
            font=self.theme.get_mono_font(6),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_MUTED
        ).pack(side="right")
        
        self.root.bind("<Control-Return>", lambda e: self.gerar_cards())
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  FOOTER (altura: 26px)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_footer(self):
        tk.Frame(self.root, bg=self.theme.BORDER, height=1).pack(fill="x", side="bottom")
        
        footer = tk.Frame(self.root, bg=self.theme.BG_SECONDARY, height=26)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=self.theme.BG_SECONDARY)
        footer_content.pack(fill="both", expand=True, padx=10, pady=4)
        
        # Status
        status_frame = tk.Frame(footer_content, bg=self.theme.BG_SECONDARY)
        status_frame.pack(side="left", fill="y")
        
        self.status_icon = tk.Label(
            status_frame, text="◉", font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.SUCCESS
        )
        self.status_icon.pack(side="left", padx=(0, 3))
        
        self.status_label = tk.Label(
            status_frame, text="Pronto para gerar flashcards",
            font=self.theme.get_ui_font(7),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left")
        
        # Versão
        tk.Label(
            footer_content, text=f"{APP_NAME} {APP_VERSION}",
            font=self.theme.get_mono_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(side="right")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  MÉTODOS UTILITÁRIOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _update_char_counter(self, event=None):
        texto = self.text_input.get("1.0", tk.END).strip()
        chars = len(texto)
        self.char_counter_label.config(text=f"{chars:,} chars")
        self.token_counter_label.config(text=f"~{chars // 4:,} tokens")
    
    def _show_preview_placeholder(self):
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
   │   com scores de qualidade    │
   │                              │
   ╰──────────────────────────────╯
"""
        self.preview.insert("1.0", placeholder, "processing")
        self.preview.config(state="disabled")
    
    def _insert_preview_formatted(self, cards, hard):
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        
        if not cards:
            self.preview.insert("1.0", "Nenhum card gerado.", "error")
            self.preview.config(state="disabled")
            return
        
        scores = [score_card(c["q"], c["a"], hard) for c in cards]
        avg = round(sum(scores) / len(scores), 1) if scores else 0.0
        
        self.cards_count_var.set(str(len(cards)))
        self.avg_score_var.set(str(avg))
        self.cards_data = cards
        
        for i, c in enumerate(cards):
            sc = scores[i]
            
            # Score badge
            quality = "●●●●● Excelente" if sc >= 8.0 else "●●●●○ Bom" if sc >= 6.5 else "●●●○○ Regular" if sc >= 5.0 else "●●○○○ Revisar"
            self.preview.insert(tk.END, f"┌─ Score: {sc}/10 {quality}\n", "score")
            self.preview.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            self.preview.insert(tk.END, f"│ A: {c['a']}\n", "resposta")
            
            if i < len(cards) - 1:
                self.preview.insert(tk.END, "└─────────────────────────────\n\n", "separator")
            else:
                self.preview.insert(tk.END, "└─────────────────────────────\n", "separator")
        
        self.preview.config(state="disabled")
    
    def _set_busy(self, is_busy: bool, msg: str = ""):
        state = "disabled" if is_busy else "normal"
        self.btn_gerar.config(state=state)
        self.btn_exportar.config(state=state)
        self.btn_copiar.config(state=state)
        self.btn_limpar.config(state=state)
        
        if is_busy:
            self.status_icon.config(fg=self.theme.WARNING)
            self.status_label.config(text=msg if msg else "Processando...")
        else:
            self.status_icon.config(fg=self.theme.SUCCESS)
    
    def _update_status(self, msg: str, status_type: str = "info"):
        color_map = {"info": self.theme.INFO, "success": self.theme.SUCCESS, "warning": self.theme.WARNING, "error": self.theme.ERROR}
        self.root.after(0, lambda: (
            self.status_icon.config(fg=color_map.get(status_type, self.theme.INFO)),
            self.status_label.config(text=msg)
        ))
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  AÇÕES PRINCIPAIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def gerar_cards(self):
        texto = self.text_input.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showerror("Erro", "Insira um texto para análise.")
            return

        hard = bool(self.hard_var.get())
        do_refine = bool(self.refine_var.get())

        self._set_busy(True, "Gerando flashcards...")
        
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        msg = "\n\n    ⏳ Processando...\n"
        if do_refine:
            msg += "    (Refinamento ativado)\n"
        self.preview.insert(tk.END, msg, "processing")
        self.preview.config(state="disabled")
        
        self.cards_count_var.set("...")
        self.avg_score_var.set("...")

        def chamar_api():
            try:
                qtd = self.qtd_var.get().strip().upper()
                modo = "AUTOMÁTICO" if qtd == "AUTO" else "MANUAL"

                base_prompt = PROMPT_HARD if hard else PROMPT_NORMAL
                prompt = base_prompt.format(MODO=modo, QTD=qtd, TEXTO=texto)

                self._update_status("Gerando (1ª passada)...", "warning")
                
                resp1 = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4
                )
                raw1 = (resp1.choices[0].message.content or "").strip()
                cards1 = parse_cards(raw1)

                if not cards1:
                    raise RuntimeError("Não consegui extrair cards. Tente reformular o texto.")

                cards_final = cards1
                if do_refine and len(cards1) >= 1:
                    self._update_status("Refinando (2ª passada)...", "warning")
                    cards_text = format_cards_for_refine(cards1)
                    refine_prompt = REFINE_PROMPT.format(
                        DIFICULDADE=("HARD" if hard else "NORMAL"),
                        TEXTO=texto, CARDS=cards_text
                    )
                    resp2 = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": refine_prompt}],
                        temperature=0.3
                    )
                    raw2 = (resp2.choices[0].message.content or "").strip()
                    cards2 = parse_cards(raw2)
                    if len(cards2) >= max(1, int(len(cards1) * 0.5)):
                        cards_final = cards2

                self.root.after(0, lambda: self._finalizar_geracao(cards_final, hard, do_refine))

            except Exception as e:
                self.root.after(0, lambda m=str(e): self._erro_geracao(m))

        threading.Thread(target=chamar_api, daemon=True).start()
    
    def _finalizar_geracao(self, cards, hard, refined):
        self._insert_preview_formatted(cards, hard)
        mode_txt = "HARD" if hard else "NORMAL"
        ref_txt = " + refinado" if refined else ""
        self._set_busy(False)
        self._update_status(f"✓ {len(cards)} card(s) • {mode_txt}{ref_txt}", "success")
    
    def _erro_geracao(self, mensagem: str):
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, f"\n  ❌ Erro:\n\n  {mensagem}", "error")
        self.preview.config(state="disabled")
        self.cards_count_var.set("0")
        self.avg_score_var.set("—")
        self._set_busy(False)
        self._update_status("Erro na geração", "error")
        messagebox.showerror("Erro", mensagem)
    
    def exportar_cards(self):
        if not self.cards_data:
            messagebox.showwarning("Aviso", "Nenhum card para exportar.")
            return

        dialog = ExportDialog(self.root, len(self.cards_data), self.theme)
        self.root.wait_window(dialog)
        
        if not dialog.result:
            return
        
        if dialog.result == "anki_apkg":
            self._export_apkg(dialog.deck_name)
        else:
            self._export_txt("anki" if dialog.result == "anki_txt" else "noji")
    
    def _export_apkg(self, deck_name):
        path = filedialog.asksaveasfilename(
            defaultextension=".apkg",
            filetypes=[("Pacote Anki", "*.apkg")],
            title="Salvar .apkg",
            initialfile=f"{deck_name}.apkg"
        )
        if not path:
            return

        try:
            modelo = genanki.Model(
                1607392319, "AnkiLab Card",
                fields=[{"name": "Frente"}, {"name": "Verso"}],
                templates=[{
                    "name": "Card 1",
                    "qfmt": "{{Frente}}",
                    "afmt": '{{FrontSide}}<hr id="answer">{{Verso}}',
                }],
                css=".card { font-family: 'Segoe UI', Arial; font-size: 20px; text-align: center; color: #e6edf3; background: #0f1419; padding: 24px; }"
            )
            deck = genanki.Deck(abs(hash(deck_name)) % (10 ** 10), deck_name)
            for c in self.cards_data:
                deck.add_note(genanki.Note(model=modelo, fields=[c["q"], c["a"]], guid=genanki.guid_for(c["q"], c["a"])))
            genanki.Package(deck).write_to_file(path)

            self._update_status(f"Exportado: {len(self.cards_data)} cards", "success")
            messagebox.showinfo("Sucesso", f"✓ {len(self.cards_data)} cards exportados!\n\nNo Anki: Arquivo → Importar")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def _export_txt(self, target):
        filename = "flashcards_anki.txt" if target == "anki" else "flashcards_noji.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile=filename
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(format_cards_for_export_tab(self.cards_data))
            self._update_status(f"Exportado: {len(self.cards_data)} cards", "success")
            messagebox.showinfo("Sucesso", f"✓ {len(self.cards_data)} cards exportados!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def copiar_clipboard(self):
        if not self.cards_data:
            messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(format_cards_for_export_tab(self.cards_data))
        self.root.update()
        self._update_status("Copiado! (formato Tab)", "success")
    
    def limpar_tudo(self):
        self.text_input.delete("1.0", tk.END)
        self.qtd_var.set("AUTO")
        self.hard_var.set(False)
        self.refine_var.set(False)
        self.cards_data = []
        self.cards_count_var.set("0")
        self.avg_score_var.set("—")
        self._show_preview_placeholder()
        self._update_char_counter()
        self._update_mode_display()
        self._update_status("Campos limpos", "info")


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  DIALOG DE EXPORTAÇÃO (escala compacta)                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class ExportDialog(tk.Toplevel):
    def __init__(self, parent, num_cards, theme):
        super().__init__(parent)
        self.theme = theme
        self.result = None
        self.deck_name = "Flashcards AnkiLab"
        
        self.title("Exportar")
        self.geometry("340x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.theme.BG_MAIN)
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 170
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 125
        self.geometry(f"+{x}+{y}")
        
        self._build_ui(num_cards)
    
    def _build_ui(self, num_cards):
        # Header
        header = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        header.pack(fill="x")
        
        header_content = tk.Frame(header, bg=self.theme.BG_SECONDARY)
        header_content.pack(fill="x", padx=16, pady=10)
        
        tk.Label(
            header_content, text="💾", font=("Segoe UI Emoji", 14),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))
        
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
        
        # Conteúdo
        content = tk.Frame(self, bg=self.theme.BG_MAIN)
        content.pack(fill="both", expand=True, padx=16, pady=10)
        
        tk.Label(
            content, text="Formato:",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.formato_var = tk.StringVar(value="anki_apkg")
        
        for value, label, desc in [
            ("anki_apkg", "📗 Anki (.apkg)", "Pacote nativo"),
            ("anki_txt", "📄 Anki (.txt)", "Texto tabulado"),
            ("noji_txt", "🟣 Noji (.txt)", "Para Noji")
        ]:
            frame = tk.Frame(content, bg=self.theme.BG_MAIN)
            frame.pack(fill="x", pady=1)
            
            tk.Radiobutton(
                frame, variable=self.formato_var, value=value,
                bg=self.theme.BG_MAIN, fg=self.theme.TEXT_PRIMARY,
                activebackground=self.theme.BG_MAIN,
                selectcolor=self.theme.BG_INPUT, highlightthickness=0,
                command=self._toggle_deck_name
            ).pack(side="left")
            
            lf = tk.Frame(frame, bg=self.theme.BG_MAIN)
            lf.pack(side="left")
            tk.Label(lf, text=label, font=self.theme.get_ui_font(8), bg=self.theme.BG_MAIN, fg=self.theme.TEXT_PRIMARY).pack(anchor="w")
            tk.Label(lf, text=desc, font=self.theme.get_ui_font(6), bg=self.theme.BG_MAIN, fg=self.theme.TEXT_MUTED).pack(anchor="w")
        
        # Nome do deck
        self.deck_frame = tk.Frame(content, bg=self.theme.BG_MAIN)
        self.deck_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(
            self.deck_frame, text="Nome do Deck:",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_MAIN, fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 3))
        
        self.deck_entry = tk.Entry(
            self.deck_frame, font=self.theme.get_ui_font(8),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY, relief="flat",
            highlightthickness=1, highlightbackground=self.theme.BORDER
        )
        self.deck_entry.insert(0, "Flashcards AnkiLab")
        self.deck_entry.pack(fill="x", ipady=3)
        
        # Botões
        btn_frame = tk.Frame(self, bg=self.theme.BG_MAIN)
        btn_frame.pack(fill="x", padx=16, pady=10)
        
        tk.Button(
            btn_frame, text="Cancelar", font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            relief="flat", padx=12, pady=4, command=self._cancelar
        ).pack(side="right", padx=(5, 0))
        
        tk.Button(
            btn_frame, text="Exportar", font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.ACCENT_PRIMARY, fg=self.theme.TEXT_INVERSE,
            relief="flat", padx=12, pady=4, command=self._exportar
        ).pack(side="right")
    
    def _toggle_deck_name(self):
        self.deck_entry.config(state="normal" if self.formato_var.get() == "anki_apkg" else "disabled")
    
    def _exportar(self):
        self.deck_name = self.deck_entry.get().strip() or "Flashcards AnkiLab"
        self.result = self.formato_var.get()
        self.destroy()
    
    def _cancelar(self):
        self.result = None
        self.destroy()


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  PONTO DE ENTRADA                                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    root = tk.Tk()
    app = AnkiLabApp(root)
    root.mainloop()
