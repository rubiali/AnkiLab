"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                         🧠 ANKILAB — COGNITIVE FLASHCARD ENGINE               ║
║                                                                               ║
║  Tema: NEURO / COGNITIVE LAB                                                  ║
║  Layout completamente reconstruído para transmitir:                           ║
║  • Laboratório cognitivo                                                      ║
║  • Ciência da memória                                                         ║
║  • Aprendizado profundo                                                       ║
║  • Precisão, controle e inteligência                                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

ESTRUTURA DO LAYOUT:
────────────────────
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER: Logo + Título + Indicador de Status Global                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────┐ │
│  │                         │    │                                         │ │
│  │   PAINEL ESQUERDO       │    │   PAINEL DIREITO                        │ │
│  │   ─────────────────     │    │   ──────────────                        │ │
│  │   • Área de entrada     │    │   • Métricas (cards, score médio)       │ │
│  │   • Contador tokens     │    │   • Preview dos flashcards              │ │
│  │   • Controle quantidade │    │   • Destaque visual Q/A/Score           │ │
│  │                         │    │                                         │ │
│  └─────────────────────────┘    └─────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  PAINEL DE OPÇÕES AVANÇADAS: Hard Mode | Refinamento | Configurações        │
├─────────────────────────────────────────────────────────────────────────────┤
│  BARRA DE AÇÕES: [Gerar] [Exportar] [Copiar] [Limpar]                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  FOOTER: Status detalhado | Modo ativo | Versão                             │
└─────────────────────────────────────────────────────────────────────────────┘
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
    """
    Sistema de cores centralizado para o tema Neuro/Cognitive Lab.
    Grafite escuro com acentos em ciano neural e roxo suave.
    """
    # ── Fundos ──────────────────────────────────────────────────────────────────
    BG_MAIN = "#0f1419"           # Fundo principal (azul petróleo escuro)
    BG_SECONDARY = "#1a1f26"      # Superfícies secundárias
    BG_TERTIARY = "#242b35"       # Cards e painéis elevados
    BG_INPUT = "#1e252e"          # Campos de entrada
    BG_HOVER = "#2a3441"          # Hover states
    
    # ── Acentos ─────────────────────────────────────────────────────────────────
    ACCENT_PRIMARY = "#00d4aa"    # Ciano/verde neural (ações principais)
    ACCENT_SECONDARY = "#9b7dff"  # Roxo suave (scores, destaques)
    ACCENT_TERTIARY = "#00a3cc"   # Azul ciano (links, info)
    
    # ── Textos ──────────────────────────────────────────────────────────────────
    TEXT_PRIMARY = "#e6edf3"      # Texto principal (branco suave)
    TEXT_SECONDARY = "#8b949e"    # Texto secundário (cinza médio)
    TEXT_MUTED = "#484f58"        # Texto desabilitado (cinza escuro)
    TEXT_INVERSE = "#0f1419"      # Texto sobre fundos claros
    
    # ── Semânticas ──────────────────────────────────────────────────────────────
    SUCCESS = "#3fb950"           # Verde sucesso
    WARNING = "#d29922"           # Amarelo aviso
    ERROR = "#f85149"             # Vermelho erro
    INFO = "#58a6ff"              # Azul informação
    
    # ── Bordas e Separadores ────────────────────────────────────────────────────
    BORDER = "#30363d"            # Bordas sutis
    BORDER_FOCUS = "#00d4aa"      # Borda com foco
    SEPARATOR = "#21262d"         # Linhas divisórias
    
    # ── Específicos de Flashcards ───────────────────────────────────────────────
    CARD_Q = "#58a6ff"            # Perguntas (azul claro)
    CARD_A = "#3fb950"            # Respostas (verde)
    CARD_SCORE = "#d2a8ff"        # Scores (lilás)
    CARD_HEADER = "#f0883e"       # Headers de métricas (laranja)
    
    # ── Fontes ──────────────────────────────────────────────────────────────────
    FONT_MONO = ("JetBrains Mono", "Consolas", "Cascadia Code", "Fira Code", "monospace")
    FONT_UI = ("Segoe UI", "SF Pro Display", "Helvetica Neue", "sans-serif")
    
    @classmethod
    def get_mono_font(cls, size=10, weight="normal"):
        """Retorna fonte monoespaçada disponível no sistema."""
        return (cls.FONT_MONO[1], size, weight)
    
    @classmethod
    def get_ui_font(cls, size=10, weight="normal"):
        """Retorna fonte de UI disponível no sistema."""
        return (cls.FONT_UI[0], size, weight)


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  VALIDAÇÃO INICIAL                                                            ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def validar_api_key():
    """Verifica se a API key está configurada nas variáveis de ambiente."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "🔑 API Key Não Encontrada",
            "Defina a variável de ambiente OPENAI_API_KEY.\n\n"
            "Windows (CMD):\n  set OPENAI_API_KEY=sua_chave\n\n"
            "Windows (PowerShell):\n  $env:OPENAI_API_KEY='sua_chave'\n\n"
            "Linux/Mac:\n  export OPENAI_API_KEY=sua_chave"
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
# ║  PROMPTS (mantidos da versão original)                                        ║
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
# ║  FUNÇÕES DE PARSING E SCORING (mantidas da versão original)                   ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def parse_cards(raw: str):
    """Parse da resposta da API para extrair flashcards no formato Q/A."""
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
        
        if s.startswith("[Score:"):
            continue
        if s.startswith("#"):
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
        
        q_lines = []
        a_lines = []
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
        
        q = " ".join(q_lines).strip()
        a = " ".join(a_lines).strip()
        
        q = re.sub(r"\s+", " ", q)
        a = re.sub(r"\s+", " ", a)
        
        if q and a:
            cards.append({"q": q, "a": a})
    
    return cards


def word_count(s: str) -> int:
    """Conta palavras em uma string."""
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return 0
    return len(s.split(" "))


def score_card(q: str, a: str, hard: bool) -> float:
    """Calcula score de qualidade para um flashcard."""
    q_l = q.lower().strip()
    a_l = a.lower().strip()

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
        "ao escolher", "ao rodar", "ao desenvolver", "em um sistema", "em um aplicativo",
        "em um jogo", "google maps", "startup", "servidor", "banco de dados",
        "front-end", "back-end", "hardware", "requisitos", "teste", "segurança",
        "desempenho", "incompatibilidade", "usuário", "cliente", "projeto"
    ]
    if any(m in q_l for m in practical_markers):
        score += 0.9

    if any(x in a_l for x in ["porque", "pois", "assim", "portanto", "logo", "então"]):
        score += 0.4

    if score < 0:
        score = 0.0
    if score > 10:
        score = 10.0

    return round(score, 1)


def format_cards_for_export_tab(cards):
    """Formato tabulado: Frente<TAB>Verso (funciona para Anki .txt e Noji)"""
    lines = []
    for c in cards:
        lines.append(f"{c['q']}\t{c['a']}")
    return "\n".join(lines) + ("\n" if lines else "")


def format_cards_for_refine(cards):
    """Formata cards para envio ao prompt de refinamento."""
    lines = []
    for c in cards:
        lines.append(f"Q: {c['q']}")
        lines.append(f"A: {c['a']}")
        lines.append("")
    return "\n".join(lines).strip()


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  CLASSE PRINCIPAL DA APLICAÇÃO — AnkiLabApp                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class AnkiLabApp:
    """
    Aplicação principal do AnkiLab com tema NEURO / COGNITIVE LAB.
    
    A interface é dividida em seções claras:
    - Header: identidade visual e status global
    - Painel Esquerdo: entrada de texto e configurações
    - Painel Direito: preview e métricas dos flashcards
    - Painel de Opções: controles avançados (Hard Mode, Refinamento)
    - Footer: status detalhado e informações do sistema
    """
    
    def __init__(self, root):
        self.root = root
        self.theme = NeuroTheme
        self.cards_data = []  # Armazena os cards gerados
        
        # ── Configuração da janela principal ────────────────────────────────────
        self.root.title(f"{APP_NAME} • {APP_TAGLINE}")
        self.root.geometry("1280x820")
        self.root.minsize(1024, 700)
        self.root.configure(bg=self.theme.BG_MAIN)
        
        # ── Variáveis de controle ───────────────────────────────────────────────
        self.qtd_var = tk.StringVar(value="AUTO")
        self.hard_var = tk.BooleanVar(value=False)
        self.refine_var = tk.BooleanVar(value=False)
        self.cards_count_var = tk.StringVar(value="0")
        self.avg_score_var = tk.StringVar(value="—")
        
        # ── Configurar estilos ttk ──────────────────────────────────────────────
        self._configure_styles()
        
        # ── Construir interface ─────────────────────────────────────────────────
        self._build_header()
        self._build_main_content()
        self._build_options_panel()
        self._build_actions_bar()
        self._build_footer()
        
        # ── Inicialização ───────────────────────────────────────────────────────
        self._update_char_counter()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  CONFIGURAÇÃO DE ESTILOS TTK
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _configure_styles(self):
        """Configura todos os estilos ttk para o tema Neuro."""
        style = ttk.Style()
        
        # ── Estilo dos botões principais (ação) ─────────────────────────────────
        style.configure(
            "Action.TButton",
            font=self.theme.get_ui_font(10, "bold"),
            padding=(16, 10),
            background=self.theme.ACCENT_PRIMARY,
            foreground=self.theme.TEXT_INVERSE
        )
        
        # ── Estilo dos botões secundários ───────────────────────────────────────
        style.configure(
            "Secondary.TButton",
            font=self.theme.get_ui_font(10),
            padding=(14, 8),
            background=self.theme.BG_TERTIARY
        )
        
        # ── Estilo dos checkbuttons ─────────────────────────────────────────────
        style.configure(
            "Neuro.TCheckbutton",
            font=self.theme.get_ui_font(10),
            background=self.theme.BG_SECONDARY,
            foreground=self.theme.TEXT_PRIMARY
        )
        
        # ── Estilo dos labels ───────────────────────────────────────────────────
        style.configure(
            "Neuro.TLabel",
            font=self.theme.get_ui_font(10),
            background=self.theme.BG_MAIN,
            foreground=self.theme.TEXT_PRIMARY
        )
        
        style.configure(
            "NeuroSecondary.TLabel",
            font=self.theme.get_ui_font(9),
            background=self.theme.BG_MAIN,
            foreground=self.theme.TEXT_SECONDARY
        )
        
        style.configure(
            "NeuroMuted.TLabel",
            font=self.theme.get_ui_font(9),
            background=self.theme.BG_MAIN,
            foreground=self.theme.TEXT_MUTED
        )
        
        # ── Estilo do Entry ─────────────────────────────────────────────────────
        style.configure(
            "Neuro.TEntry",
            fieldbackground=self.theme.BG_INPUT,
            foreground=self.theme.TEXT_PRIMARY,
            insertcolor=self.theme.ACCENT_PRIMARY
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  HEADER — Identidade visual e status global
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_header(self):
        """
        Constrói o cabeçalho com:
        - Logo/título do aplicativo
        - Tagline
        - Indicador de modelo ativo
        """
        header = tk.Frame(self.root, bg=self.theme.BG_SECONDARY, height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # ── Container interno com padding ───────────────────────────────────────
        header_inner = tk.Frame(header, bg=self.theme.BG_SECONDARY)
        header_inner.pack(fill="both", expand=True, padx=24, pady=12)
        
        # ── Lado esquerdo: Logo e título ────────────────────────────────────────
        left_frame = tk.Frame(header_inner, bg=self.theme.BG_SECONDARY)
        left_frame.pack(side="left", fill="y")
        
        # Ícone neural (emoji)
        logo_label = tk.Label(
            left_frame,
            text="🧠",
            font=("Segoe UI Emoji", 28),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        )
        logo_label.pack(side="left", padx=(0, 12))
        
        # Título e tagline
        title_frame = tk.Frame(left_frame, bg=self.theme.BG_SECONDARY)
        title_frame.pack(side="left", fill="y")
        
        title_label = tk.Label(
            title_frame,
            text=APP_NAME,
            font=self.theme.get_ui_font(18, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        )
        title_label.pack(anchor="w")
        
        tagline_label = tk.Label(
            title_frame,
            text=APP_TAGLINE,
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        )
        tagline_label.pack(anchor="w")
        
        # ── Lado direito: Status do modelo ──────────────────────────────────────
        right_frame = tk.Frame(header_inner, bg=self.theme.BG_SECONDARY)
        right_frame.pack(side="right", fill="y")
        
        # Badge do modelo
        model_frame = tk.Frame(
            right_frame,
            bg=self.theme.BG_TERTIARY,
            padx=12,
            pady=6
        )
        model_frame.pack(side="right")
        
        model_icon = tk.Label(
            model_frame,
            text="⚡",
            font=("Segoe UI Emoji", 11),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.ACCENT_PRIMARY
        )
        model_icon.pack(side="left", padx=(0, 6))
        
        model_label = tk.Label(
            model_frame,
            text=MODEL_NAME,
            font=self.theme.get_mono_font(10),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY
        )
        model_label.pack(side="left")
        
        # Separador visual abaixo do header
        separator = tk.Frame(self.root, bg=self.theme.BORDER, height=1)
        separator.pack(fill="x", side="top")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  MAIN CONTENT — Painéis esquerdo e direito
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_main_content(self):
        """
        Constrói a área principal dividida em dois painéis:
        - Esquerdo: entrada de texto + controles
        - Direito: preview dos flashcards + métricas
        """
        # ── Container principal ─────────────────────────────────────────────────
        main_container = tk.Frame(self.root, bg=self.theme.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Configura grid com duas colunas (proporção 45% / 55%)
        main_container.grid_columnconfigure(0, weight=45, minsize=400)
        main_container.grid_columnconfigure(1, weight=55, minsize=450)
        main_container.grid_rowconfigure(0, weight=1)
        
        # ── Painel Esquerdo ─────────────────────────────────────────────────────
        self._build_left_panel(main_container)
        
        # ── Painel Direito ──────────────────────────────────────────────────────
        self._build_right_panel(main_container)
    
    def _build_left_panel(self, parent):
        """
        Painel esquerdo: entrada de texto e controles de quantidade.
        """
        left_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # ── Header do painel ────────────────────────────────────────────────────
        panel_header = tk.Frame(left_panel, bg=self.theme.BG_TERTIARY, height=48)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=16, pady=10)
        
        # Ícone e título
        tk.Label(
            header_content,
            text="📝",
            font=("Segoe UI Emoji", 14),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))
        
        tk.Label(
            header_content,
            text="ENTRADA DE TEXTO",
            font=self.theme.get_ui_font(11, "bold"),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # ── Área de texto ───────────────────────────────────────────────────────
        text_frame = tk.Frame(left_panel, bg=self.theme.BG_SECONDARY, padx=16, pady=12)
        text_frame.pack(fill="both", expand=True)
        
        # Label de instrução
        instruction_label = tk.Label(
            text_frame,
            text="Cole ou digite o conteúdo para análise:",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY,
            anchor="w"
        )
        instruction_label.pack(fill="x", pady=(0, 8))
        
        # Frame do texto com borda
        text_border = tk.Frame(
            text_frame,
            bg=self.theme.BORDER,
            padx=1,
            pady=1
        )
        text_border.pack(fill="both", expand=True)
        
        # Widget de texto
        self.text_input = tk.Text(
            text_border,
            wrap="word",
            font=self.theme.get_mono_font(10),
            bg=self.theme.BG_INPUT,
            fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            selectbackground=self.theme.ACCENT_PRIMARY,
            selectforeground=self.theme.BG_MAIN,
            relief="flat",
            padx=12,
            pady=10,
            highlightthickness=0
        )
        self.text_input.pack(fill="both", expand=True)
        self.text_input.bind("<KeyRelease>", self._update_char_counter)
        self.text_input.bind("<FocusIn>", lambda e: text_border.config(bg=self.theme.BORDER_FOCUS))
        self.text_input.bind("<FocusOut>", lambda e: text_border.config(bg=self.theme.BORDER))
        
        # ── Barra inferior: contador e quantidade ───────────────────────────────
        bottom_bar = tk.Frame(left_panel, bg=self.theme.BG_TERTIARY, height=50)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        
        bottom_content = tk.Frame(bottom_bar, bg=self.theme.BG_TERTIARY)
        bottom_content.pack(fill="both", expand=True, padx=16, pady=8)
        
        # Contador de caracteres/tokens (esquerda)
        counter_frame = tk.Frame(bottom_content, bg=self.theme.BG_TERTIARY)
        counter_frame.pack(side="left", fill="y")
        
        self.char_counter_label = tk.Label(
            counter_frame,
            text="0 caracteres",
            font=self.theme.get_mono_font(9),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_SECONDARY
        )
        self.char_counter_label.pack(side="left")
        
        tk.Label(
            counter_frame,
            text="  •  ",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_MUTED
        ).pack(side="left")
        
        self.token_counter_label = tk.Label(
            counter_frame,
            text="~0 tokens",
            font=self.theme.get_mono_font(9),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_SECONDARY
        )
        self.token_counter_label.pack(side="left")
        
        # Controle de quantidade (direita)
        qtd_frame = tk.Frame(bottom_content, bg=self.theme.BG_TERTIARY)
        qtd_frame.pack(side="right", fill="y")
        
        tk.Label(
            qtd_frame,
            text="Cards:",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 6))
        
        self.qtd_entry = tk.Entry(
            qtd_frame,
            textvariable=self.qtd_var,
            font=self.theme.get_mono_font(10),
            bg=self.theme.BG_INPUT,
            fg=self.theme.ACCENT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            relief="flat",
            width=8,
            justify="center",
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.BORDER_FOCUS
        )
        self.qtd_entry.pack(side="left", padx=(0, 6))
        
        tk.Label(
            qtd_frame,
            text="(n° ou AUTO)",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_MUTED
        ).pack(side="left")
    
    def _build_right_panel(self, parent):
        """
        Painel direito: métricas e preview dos flashcards.
        """
        right_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        # ── Header do painel com métricas ───────────────────────────────────────
        panel_header = tk.Frame(right_panel, bg=self.theme.BG_TERTIARY, height=48)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=16, pady=10)
        
        # Ícone e título (esquerda)
        title_frame = tk.Frame(header_content, bg=self.theme.BG_TERTIARY)
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame,
            text="🎴",
            font=("Segoe UI Emoji", 14),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))
        
        tk.Label(
            title_frame,
            text="FLASHCARDS GERADOS",
            font=self.theme.get_ui_font(11, "bold"),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Métricas (direita)
        metrics_frame = tk.Frame(header_content, bg=self.theme.BG_TERTIARY)
        metrics_frame.pack(side="right", fill="y")
        
        # Badge de contagem
        count_badge = tk.Frame(
            metrics_frame,
            bg=self.theme.BG_MAIN,
            padx=10,
            pady=4
        )
        count_badge.pack(side="left", padx=(0, 12))
        
        self.cards_count_label = tk.Label(
            count_badge,
            textvariable=self.cards_count_var,
            font=self.theme.get_mono_font(11, "bold"),
            bg=self.theme.BG_MAIN,
            fg=self.theme.ACCENT_PRIMARY
        )
        self.cards_count_label.pack(side="left")
        
        tk.Label(
            count_badge,
            text=" cards",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_MAIN,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # Badge de score médio
        score_badge = tk.Frame(
            metrics_frame,
            bg=self.theme.BG_MAIN,
            padx=10,
            pady=4
        )
        score_badge.pack(side="left")
        
        tk.Label(
            score_badge,
            text="Score: ",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_MAIN,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        self.avg_score_label = tk.Label(
            score_badge,
            textvariable=self.avg_score_var,
            font=self.theme.get_mono_font(11, "bold"),
            bg=self.theme.BG_MAIN,
            fg=self.theme.ACCENT_SECONDARY
        )
        self.avg_score_label.pack(side="left")
        
        tk.Label(
            score_badge,
            text="/10",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_MAIN,
            fg=self.theme.TEXT_MUTED
        ).pack(side="left")
        
        # ── Área de preview ─────────────────────────────────────────────────────
        preview_frame = tk.Frame(right_panel, bg=self.theme.BG_SECONDARY, padx=16, pady=12)
        preview_frame.pack(fill="both", expand=True)
        
        # Frame do preview com borda
        preview_border = tk.Frame(
            preview_frame,
            bg=self.theme.BORDER,
            padx=1,
            pady=1
        )
        preview_border.pack(fill="both", expand=True)
        
        # Container para texto + scrollbar
        preview_container = tk.Frame(preview_border, bg=self.theme.BG_INPUT)
        preview_container.pack(fill="both", expand=True)
        
        # Scrollbar customizada
        scrollbar = tk.Scrollbar(
            preview_container,
            orient="vertical",
            bg=self.theme.BG_TERTIARY,
            troughcolor=self.theme.BG_INPUT,
            activebackground=self.theme.ACCENT_PRIMARY,
            highlightthickness=0
        )
        scrollbar.pack(side="right", fill="y")
        
        # Widget de texto para preview
        self.preview = tk.Text(
            preview_container,
            wrap="word",
            font=self.theme.get_mono_font(10),
            bg=self.theme.BG_INPUT,
            fg=self.theme.TEXT_PRIMARY,
            relief="flat",
            padx=14,
            pady=12,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            state="disabled",
            cursor="arrow"
        )
        self.preview.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self.preview.yview)
        
        # ── Configurar tags de formatação ───────────────────────────────────────
        self.preview.tag_configure(
            "header",
            foreground=self.theme.CARD_HEADER,
            font=self.theme.get_mono_font(10, "bold")
        )
        self.preview.tag_configure(
            "score",
            foreground=self.theme.CARD_SCORE,
            font=self.theme.get_mono_font(9, "bold")
        )
        self.preview.tag_configure(
            "pergunta",
            foreground=self.theme.CARD_Q,
            font=self.theme.get_mono_font(10, "bold")
        )
        self.preview.tag_configure(
            "resposta",
            foreground=self.theme.CARD_A,
            font=self.theme.get_mono_font(10)
        )
        self.preview.tag_configure(
            "separator",
            foreground=self.theme.TEXT_MUTED,
            font=self.theme.get_mono_font(8)
        )
        self.preview.tag_configure(
            "processing",
            foreground=self.theme.ACCENT_PRIMARY,
            font=self.theme.get_mono_font(10),
            justify="center"
        )
        self.preview.tag_configure(
            "error",
            foreground=self.theme.ERROR,
            font=self.theme.get_mono_font(10)
        )
        
        # Mensagem inicial
        self._show_preview_placeholder()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  OPTIONS PANEL — Controles avançados
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_options_panel(self):
        """
        Painel de opções avançadas: Hard Mode e Refinamento.
        """
        options_container = tk.Frame(self.root, bg=self.theme.BG_MAIN)
        options_container.pack(fill="x", padx=16, pady=(0, 8))
        
        # ── Painel interno ──────────────────────────────────────────────────────
        options_panel = tk.Frame(options_container, bg=self.theme.BG_SECONDARY)
        options_panel.pack(fill="x")
        
        options_content = tk.Frame(options_panel, bg=self.theme.BG_SECONDARY)
        options_content.pack(fill="x", padx=20, pady=14)
        
        # ── Título da seção ─────────────────────────────────────────────────────
        title_frame = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame,
            text="⚙️",
            font=("Segoe UI Emoji", 12),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side="left", padx=(0, 8))
        
        tk.Label(
            title_frame,
            text="CONFIGURAÇÕES AVANÇADAS",
            font=self.theme.get_ui_font(10, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side="left")
        
        # ── Separador vertical ──────────────────────────────────────────────────
        tk.Frame(
            options_content,
            bg=self.theme.BORDER,
            width=1
        ).pack(side="left", fill="y", padx=24)
        
        # ── Checkbox Hard Mode ──────────────────────────────────────────────────
        hard_frame = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        hard_frame.pack(side="left", fill="y", padx=(0, 20))
        
        self.hard_check = tk.Checkbutton(
            hard_frame,
            variable=self.hard_var,
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            activeforeground=self.theme.TEXT_PRIMARY,
            selectcolor=self.theme.BG_INPUT,
            highlightthickness=0,
            bd=0,
            command=self._update_mode_display
        )
        self.hard_check.pack(side="left")
        
        hard_label_frame = tk.Frame(hard_frame, bg=self.theme.BG_SECONDARY)
        hard_label_frame.pack(side="left", fill="y")
        
        hard_title = tk.Label(
            hard_label_frame,
            text="🧠 Hard Mode",
            font=self.theme.get_ui_font(10, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            cursor="hand2"
        )
        hard_title.pack(anchor="w")
        hard_title.bind("<Button-1>", lambda e: self.hard_var.set(not self.hard_var.get()) or self._update_mode_display())
        
        tk.Label(
            hard_label_frame,
            text="Cards mais desafiadores, focados em aplicação",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # ── Separador vertical ──────────────────────────────────────────────────
        tk.Frame(
            options_content,
            bg=self.theme.BORDER,
            width=1
        ).pack(side="left", fill="y", padx=20)
        
        # ── Checkbox Refinamento ────────────────────────────────────────────────
        refine_frame = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        refine_frame.pack(side="left", fill="y")
        
        self.refine_check = tk.Checkbutton(
            refine_frame,
            variable=self.refine_var,
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            activeforeground=self.theme.TEXT_PRIMARY,
            selectcolor=self.theme.BG_INPUT,
            highlightthickness=0,
            bd=0
        )
        self.refine_check.pack(side="left")
        
        refine_label_frame = tk.Frame(refine_frame, bg=self.theme.BG_SECONDARY)
        refine_label_frame.pack(side="left", fill="y")
        
        refine_title = tk.Label(
            refine_label_frame,
            text="🔁 Segunda Passada de Refinamento",
            font=self.theme.get_ui_font(10, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            cursor="hand2"
        )
        refine_title.pack(anchor="w")
        refine_title.bind("<Button-1>", lambda e: self.refine_var.set(not self.refine_var.get()))
        
        tk.Label(
            refine_label_frame,
            text="Revisão automática para eliminar redundâncias",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # ── Indicador de modo ativo (direita) ───────────────────────────────────
        self.mode_indicator = tk.Frame(options_content, bg=self.theme.BG_SECONDARY)
        self.mode_indicator.pack(side="right", fill="y")
        
        self.mode_label = tk.Label(
            self.mode_indicator,
            text="MODO: NORMAL",
            font=self.theme.get_mono_font(9, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.ACCENT_PRIMARY
        )
        self.mode_label.pack(side="right")
    
    def _update_mode_display(self):
        """Atualiza o indicador de modo (Normal/Hard)."""
        if self.hard_var.get():
            self.mode_label.config(
                text="MODO: HARD",
                fg=self.theme.ERROR
            )
        else:
            self.mode_label.config(
                text="MODO: NORMAL",
                fg=self.theme.ACCENT_PRIMARY
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  ACTIONS BAR — Botões principais
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_actions_bar(self):
        """
        Barra de ações com os botões principais.
        """
        actions_container = tk.Frame(self.root, bg=self.theme.BG_MAIN)
        actions_container.pack(fill="x", padx=16, pady=(0, 8))
        
        # ── Painel interno ──────────────────────────────────────────────────────
        actions_panel = tk.Frame(actions_container, bg=self.theme.BG_TERTIARY)
        actions_panel.pack(fill="x")
        
        actions_content = tk.Frame(actions_panel, bg=self.theme.BG_TERTIARY)
        actions_content.pack(fill="x", padx=20, pady=14)
        
        # ── Botão principal: Gerar Cards ────────────────────────────────────────
        self.btn_gerar = tk.Button(
            actions_content,
            text="  🚀  GERAR FLASHCARDS  ",
            font=self.theme.get_ui_font(11, "bold"),
            bg=self.theme.ACCENT_PRIMARY,
            fg=self.theme.TEXT_INVERSE,
            activebackground=self.theme.ACCENT_TERTIARY,
            activeforeground=self.theme.TEXT_INVERSE,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.gerar_cards
        )
        self.btn_gerar.pack(side="left", padx=(0, 16))
        
        # Efeitos hover
        self.btn_gerar.bind("<Enter>", lambda e: self.btn_gerar.config(bg=self.theme.ACCENT_TERTIARY))
        self.btn_gerar.bind("<Leave>", lambda e: self.btn_gerar.config(bg=self.theme.ACCENT_PRIMARY))
        
        # ── Separador ───────────────────────────────────────────────────────────
        tk.Frame(
            actions_content,
            bg=self.theme.BORDER,
            width=1
        ).pack(side="left", fill="y", padx=16)
        
        # ── Botões secundários ──────────────────────────────────────────────────
        self.btn_exportar = tk.Button(
            actions_content,
            text="  💾  Exportar  ",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8,
            command=self.exportar_cards
        )
        self.btn_exportar.pack(side="left", padx=(0, 8))
        self._add_button_hover(self.btn_exportar)
        
        self.btn_copiar = tk.Button(
            actions_content,
            text="  📋  Copiar  ",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8,
            command=self.copiar_clipboard
        )
        self.btn_copiar.pack(side="left", padx=(0, 8))
        self._add_button_hover(self.btn_copiar)
        
        self.btn_limpar = tk.Button(
            actions_content,
            text="  🔄  Limpar  ",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8,
            command=self.limpar_tudo
        )
        self.btn_limpar.pack(side="left")
        self._add_button_hover(self.btn_limpar)
        
        # ── Atalhos de teclado (lado direito) ───────────────────────────────────
        shortcuts_frame = tk.Frame(actions_content, bg=self.theme.BG_TERTIARY)
        shortcuts_frame.pack(side="right", fill="y")
        
        tk.Label(
            shortcuts_frame,
            text="Ctrl+Enter: Gerar",
            font=self.theme.get_mono_font(8),
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_MUTED
        ).pack(side="right")
        
        # Bind Ctrl+Enter
        self.root.bind("<Control-Return>", lambda e: self.gerar_cards())
    
    def _add_button_hover(self, button):
        """Adiciona efeitos de hover aos botões secundários."""
        button.bind("<Enter>", lambda e: button.config(bg=self.theme.BG_HOVER))
        button.bind("<Leave>", lambda e: button.config(bg=self.theme.BG_SECONDARY))
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  FOOTER — Status e informações
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_footer(self):
        """
        Rodapé com status detalhado e informações do sistema.
        """
        # Separador
        tk.Frame(self.root, bg=self.theme.BORDER, height=1).pack(fill="x", side="bottom")
        
        # Footer
        footer = tk.Frame(self.root, bg=self.theme.BG_SECONDARY, height=36)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=self.theme.BG_SECONDARY)
        footer_content.pack(fill="both", expand=True, padx=20, pady=8)
        
        # ── Status (esquerda) ───────────────────────────────────────────────────
        status_frame = tk.Frame(footer_content, bg=self.theme.BG_SECONDARY)
        status_frame.pack(side="left", fill="y")
        
        self.status_icon = tk.Label(
            status_frame,
            text="◉",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.SUCCESS
        )
        self.status_icon.pack(side="left", padx=(0, 6))
        
        self.status_label = tk.Label(
            status_frame,
            text="Pronto para gerar flashcards",
            font=self.theme.get_ui_font(9),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left")
        
        # ── Versão (direita) ────────────────────────────────────────────────────
        version_frame = tk.Frame(footer_content, bg=self.theme.BG_SECONDARY)
        version_frame.pack(side="right", fill="y")
        
        tk.Label(
            version_frame,
            text=f"{APP_NAME} {APP_VERSION}",
            font=self.theme.get_mono_font(8),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_MUTED
        ).pack(side="right")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  MÉTODOS UTILITÁRIOS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _update_char_counter(self, event=None):
        """Atualiza contadores de caracteres e tokens."""
        texto = self.text_input.get("1.0", tk.END).strip()
        chars = len(texto)
        tokens_est = chars // 4
        
        self.char_counter_label.config(text=f"{chars:,} caracteres")
        self.token_counter_label.config(text=f"~{tokens_est:,} tokens")
    
    def _show_preview_placeholder(self):
        """Mostra placeholder no preview."""
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        
        placeholder = """
    ╭──────────────────────────────────────────╮
    │                                          │
    │       Cole um texto no painel            │
    │       esquerdo e clique em               │
    │       "GERAR FLASHCARDS"                 │
    │                                          │
    │       Os cards aparecerão aqui           │
    │       com scores de qualidade            │
    │                                          │
    ╰──────────────────────────────────────────╯
"""
        self.preview.insert("1.0", placeholder, "processing")
        self.preview.config(state="disabled")
    
    def _insert_preview_formatted(self, cards, hard):
        """Insere cards formatados no preview com cores."""
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        
        if not cards:
            self.preview.insert("1.0", "Nenhum card gerado.", "error")
            self.preview.config(state="disabled")
            return
        
        # Calcular scores e média
        scores = [score_card(c["q"], c["a"], hard) for c in cards]
        avg = round(sum(scores) / len(scores), 1) if scores else 0.0
        
        # Atualizar métricas no header
        self.cards_count_var.set(str(len(cards)))
        self.avg_score_var.set(str(avg))
        
        # Armazenar dados
        self.cards_data = cards
        
        # Inserir cards
        for i, c in enumerate(cards):
            sc = scores[i]
            
            # Score badge
            self.preview.insert(tk.END, f"┌─ Score: {sc}/10 ", "score")
            
            # Indicador visual de qualidade
            if sc >= 8.0:
                self.preview.insert(tk.END, "●●●●● Excelente\n", "score")
            elif sc >= 6.5:
                self.preview.insert(tk.END, "●●●●○ Bom\n", "score")
            elif sc >= 5.0:
                self.preview.insert(tk.END, "●●●○○ Regular\n", "score")
            else:
                self.preview.insert(tk.END, "●●○○○ Revisar\n", "score")
            
            # Pergunta
            self.preview.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            
            # Resposta
            self.preview.insert(tk.END, f"│ A: {c['a']}\n", "resposta")
            
            # Separador
            if i < len(cards) - 1:
                self.preview.insert(tk.END, "└─────────────────────────────────────────\n\n", "separator")
            else:
                self.preview.insert(tk.END, "└─────────────────────────────────────────\n", "separator")
        
        self.preview.config(state="disabled")
    
    def _set_busy(self, is_busy: bool, msg: str = ""):
        """Define estado de ocupado (desabilita botões)."""
        state = "disabled" if is_busy else "normal"
        
        self.btn_gerar.config(state=state)
        self.btn_exportar.config(state=state)
        self.btn_copiar.config(state=state)
        self.btn_limpar.config(state=state)
        
        if is_busy:
            self.status_icon.config(fg=self.theme.WARNING, text="◉")
            self.status_label.config(text=msg if msg else "Processando...")
        else:
            self.status_icon.config(fg=self.theme.SUCCESS, text="◉")
    
    def _update_status(self, msg: str, status_type: str = "info"):
        """Atualiza status no footer."""
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  AÇÕES PRINCIPAIS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def gerar_cards(self):
        """Gera flashcards a partir do texto de entrada."""
        texto = self.text_input.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showerror("Erro", "Insira um texto para análise.")
            return

        hard = bool(self.hard_var.get())
        do_refine = bool(self.refine_var.get())

        self._set_busy(True, "Gerando flashcards... aguarde")
        
        # Mostrar estado de processamento no preview
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, "\n\n       ⏳ Processando sua solicitação...\n\n", "processing")
        self.preview.insert(tk.END, "       Isso pode levar alguns segundos.\n", "processing")
        if do_refine:
            self.preview.insert(tk.END, "       (Refinamento ativado: 2 passadas)\n", "processing")
        self.preview.config(state="disabled")
        
        # Resetar métricas
        self.cards_count_var.set("...")
        self.avg_score_var.set("...")

        def chamar_api():
            try:
                qtd = self.qtd_var.get().strip().upper()
                modo = "AUTOMÁTICO" if qtd == "AUTO" else "MANUAL"

                base_prompt = PROMPT_HARD if hard else PROMPT_NORMAL
                prompt = base_prompt.format(MODO=modo, QTD=qtd, TEXTO=texto)

                self._update_status("Gerando flashcards (1ª passada)...", "warning")
                
                resp1 = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4
                )
                raw1 = (resp1.choices[0].message.content or "").strip()
                cards1 = parse_cards(raw1)

                if not cards1:
                    raise RuntimeError(
                        "Não consegui extrair nenhum card da resposta.\n\n"
                        "Possíveis causas:\n"
                        "• Texto muito curto ou vago\n"
                        "• API retornou formato inesperado\n\n"
                        "Tente novamente ou reformule o texto."
                    )

                cards_final = cards1
                if do_refine and len(cards1) >= 1:
                    self._update_status("Refinando flashcards (2ª passada)...", "warning")

                    cards_text = format_cards_for_refine(cards1)
                    refine_prompt = REFINE_PROMPT.format(
                        DIFICULDADE=("HARD" if hard else "NORMAL"),
                        TEXTO=texto,
                        CARDS=cards_text
                    )
                    
                    resp2 = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": refine_prompt}],
                        temperature=0.3
                    )
                    raw2 = (resp2.choices[0].message.content or "").strip()
                    cards2 = parse_cards(raw2)
                    
                    min_cards = max(1, int(len(cards1) * 0.5))
                    if len(cards2) >= min_cards:
                        cards_final = cards2

                self.root.after(0, lambda: self._finalizar_geracao(cards_final, hard, do_refine))

            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda m=msg: self._erro_geracao(m))

        threading.Thread(target=chamar_api, daemon=True).start()
    
    def _finalizar_geracao(self, cards, hard, refined):
        """Finaliza a geração com sucesso."""
        self._insert_preview_formatted(cards, hard)
        
        hard_txt = "HARD" if hard else "NORMAL"
        ref_txt = " + refinado" if refined else ""
        
        self._set_busy(False)
        self._update_status(
            f"✓ {len(cards)} flashcard(s) gerado(s) • modo {hard_txt}{ref_txt}",
            "success"
        )
    
    def _erro_geracao(self, mensagem: str):
        """Trata erro na geração."""
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, f"\n  ❌ Erro ao gerar flashcards:\n\n  {mensagem}", "error")
        self.preview.config(state="disabled")
        
        self.cards_count_var.set("0")
        self.avg_score_var.set("—")
        
        self._set_busy(False)
        self._update_status("Erro na geração. Tente novamente.", "error")
        messagebox.showerror("Erro", mensagem)
    
    def exportar_cards(self):
        """Exporta flashcards para arquivo."""
        if not self.cards_data:
            messagebox.showwarning("Aviso", "Nenhum card válido para exportar.\nGere flashcards primeiro.")
            return

        # Abre dialog de exportação
        dialog = ExportDialog(self.root, len(self.cards_data), self.theme)
        self.root.wait_window(dialog)
        
        if not dialog.result:
            return
        
        formato = dialog.result
        deck_name = dialog.deck_name
        
        if formato == "anki_apkg":
            self._export_apkg(deck_name)
        elif formato == "anki_txt":
            self._export_txt("anki")
        elif formato == "noji_txt":
            self._export_txt("noji")
    
    def _export_apkg(self, deck_name):
        """Exporta para formato .apkg do Anki."""
        path = filedialog.asksaveasfilename(
            defaultextension=".apkg",
            filetypes=[("Pacote Anki", "*.apkg"), ("Todos os arquivos", "*.*")],
            title="Salvar pacote Anki (.apkg)",
            initialfile=f"{deck_name}.apkg"
        )
        if not path:
            return

        try:
            model_id = 1607392319
            deck_id = abs(hash(deck_name)) % (10 ** 10)

            modelo = genanki.Model(
                model_id,
                "AnkiLab Flashcard",
                fields=[
                    {"name": "Frente"},
                    {"name": "Verso"},
                ],
                templates=[
                    {
                        "name": "Card 1",
                        "qfmt": "{{Frente}}",
                        "afmt": '{{FrontSide}}<hr id="answer">{{Verso}}',
                    },
                ],
                css="""
                .card {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 20px;
                    text-align: center;
                    color: #e6edf3;
                    background-color: #0f1419;
                    padding: 24px;
                }
                hr#answer {
                    border: none;
                    border-top: 1px solid #30363d;
                    margin: 20px 0;
                }
                """
            )

            deck = genanki.Deck(deck_id, deck_name)

            for c in self.cards_data:
                nota = genanki.Note(
                    model=modelo,
                    fields=[c["q"], c["a"]],
                    guid=genanki.guid_for(c["q"], c["a"])
                )
                deck.add_note(nota)

            pacote = genanki.Package(deck)
            pacote.write_to_file(path)

            self._update_status(f"Exportado: {len(self.cards_data)} cards → {os.path.basename(path)}", "success")
            messagebox.showinfo(
                "Exportação Concluída",
                f"✓ {len(self.cards_data)} flashcard(s) exportado(s)!\n\n"
                f"Deck: {deck_name}\n"
                f"Arquivo: {path}\n\n"
                "No Anki: Arquivo → Importar → selecione o .apkg"
            )

        except Exception as e:
            messagebox.showerror("Erro ao exportar", str(e))
    
    def _export_txt(self, target):
        """Exporta para formato .txt (tabulado)."""
        title = "Salvar para Anki (.txt)" if target == "anki" else "Salvar para Noji (.txt)"
        filename = "flashcards_anki.txt" if target == "anki" else "flashcards_noji.txt"
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title=title,
            initialfile=filename
        )
        if not path:
            return

        try:
            export_text = format_cards_for_export_tab(self.cards_data)
            with open(path, "w", encoding="utf-8") as f:
                f.write(export_text)

            self._update_status(f"Exportado: {len(self.cards_data)} cards → {os.path.basename(path)}", "success")
            
            if target == "anki":
                msg = (
                    f"✓ {len(self.cards_data)} flashcard(s) exportado(s)!\n\n"
                    f"Arquivo: {path}\n\n"
                    "No Anki:\n"
                    "1. Arquivo → Importar\n"
                    "2. Separador de campo: Tab\n"
                    "3. Importar"
                )
            else:
                msg = (
                    f"✓ {len(self.cards_data)} flashcard(s) exportado(s)!\n\n"
                    f"Arquivo: {path}\n\n"
                    "No Noji:\n"
                    "1. Vá em Importar cartões\n"
                    "2. Cole o conteúdo do arquivo\n"
                    "3. Entre frente/verso: Tab\n"
                    "4. Entre cartões: Nova linha"
                )
            
            messagebox.showinfo("Exportação Concluída", msg)

        except Exception as e:
            messagebox.showerror("Erro ao exportar", str(e))
    
    def copiar_clipboard(self):
        """Copia flashcards para a área de transferência."""
        if not self.cards_data:
            messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar.")
            return

        texto_limpo = format_cards_for_export_tab(self.cards_data)

        self.root.clipboard_clear()
        self.root.clipboard_append(texto_limpo)
        self.root.update()
        
        self._update_status("Copiado! Cole no Anki ou Noji (formato Tab)", "success")
    
    def limpar_tudo(self):
        """Limpa todos os campos."""
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
        self._update_status("Campos limpos. Pronto para nova geração.", "info")


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  DIALOG DE EXPORTAÇÃO (com tema Neuro)                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class ExportDialog(tk.Toplevel):
    """Dialog modal para escolha do formato de exportação."""
    
    def __init__(self, parent, num_cards, theme):
        super().__init__(parent)
        self.theme = theme
        self.result = None
        self.deck_name = "Flashcards AnkiLab"
        
        # ── Configuração da janela ──────────────────────────────────────────────
        self.title("Exportar Flashcards")
        self.geometry("460x340")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.theme.BG_MAIN)
        
        # Centralizar na tela
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (460 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (340 // 2)
        self.geometry(f"+{x}+{y}")
        
        # ── Construir interface ─────────────────────────────────────────────────
        self._build_ui(num_cards)
    
    def _build_ui(self, num_cards):
        """Constrói a interface do dialog."""
        # Header
        header = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        header.pack(fill="x")
        
        header_content = tk.Frame(header, bg=self.theme.BG_SECONDARY)
        header_content.pack(fill="x", padx=24, pady=16)
        
        tk.Label(
            header_content,
            text="💾",
            font=("Segoe UI Emoji", 20),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 12))
        
        title_frame = tk.Frame(header_content, bg=self.theme.BG_SECONDARY)
        title_frame.pack(side="left", fill="y")
        
        tk.Label(
            title_frame,
            text="Exportar Flashcards",
            font=self.theme.get_ui_font(14, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text=f"{num_cards} card(s) prontos para exportar",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w")
        
        # Conteúdo
        content = tk.Frame(self, bg=self.theme.BG_MAIN)
        content.pack(fill="both", expand=True, padx=24, pady=20)
        
        # Label formato
        tk.Label(
            content,
            text="Escolha o formato:",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_MAIN,
            fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 12))
        
        # Opções de formato
        self.formato_var = tk.StringVar(value="anki_apkg")
        
        formatos = [
            ("anki_apkg", "📗  Anki (.apkg)", "Pacote nativo — importação direta"),
            ("anki_txt", "📄  Anki (.txt)", "Texto tabulado — flexível"),
            ("noji_txt", "🟣  Noji (.txt)", "Texto tabulado para Noji")
        ]
        
        for value, label, desc in formatos:
            frame = tk.Frame(content, bg=self.theme.BG_MAIN)
            frame.pack(fill="x", pady=4)
            
            rb = tk.Radiobutton(
                frame,
                variable=self.formato_var,
                value=value,
                bg=self.theme.BG_MAIN,
                fg=self.theme.TEXT_PRIMARY,
                activebackground=self.theme.BG_MAIN,
                activeforeground=self.theme.TEXT_PRIMARY,
                selectcolor=self.theme.BG_INPUT,
                highlightthickness=0,
                command=self._toggle_deck_name
            )
            rb.pack(side="left")
            
            label_frame = tk.Frame(frame, bg=self.theme.BG_MAIN)
            label_frame.pack(side="left", fill="y")
            
            tk.Label(
                label_frame,
                text=label,
                font=self.theme.get_ui_font(10),
                bg=self.theme.BG_MAIN,
                fg=self.theme.TEXT_PRIMARY,
                cursor="hand2"
            ).pack(anchor="w")
            
            tk.Label(
                label_frame,
                text=desc,
                font=self.theme.get_ui_font(8),
                bg=self.theme.BG_MAIN,
                fg=self.theme.TEXT_MUTED
            ).pack(anchor="w")
        
        # Nome do deck
        self.deck_frame = tk.Frame(content, bg=self.theme.BG_MAIN)
        self.deck_frame.pack(fill="x", pady=(16, 0))
        
        tk.Label(
            self.deck_frame,
            text="Nome do Deck:",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_MAIN,
            fg=self.theme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 6))
        
        self.deck_entry = tk.Entry(
            self.deck_frame,
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_INPUT,
            fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.ACCENT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.BORDER_FOCUS
        )
        self.deck_entry.insert(0, "Flashcards AnkiLab")
        self.deck_entry.pack(fill="x", ipady=6)
        
        # Botões
        btn_frame = tk.Frame(self, bg=self.theme.BG_MAIN)
        btn_frame.pack(fill="x", padx=24, pady=20)
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            font=self.theme.get_ui_font(10),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._cancelar
        ).pack(side="right", padx=(8, 0))
        
        tk.Button(
            btn_frame,
            text="Exportar",
            font=self.theme.get_ui_font(10, "bold"),
            bg=self.theme.ACCENT_PRIMARY,
            fg=self.theme.TEXT_INVERSE,
            activebackground=self.theme.ACCENT_TERTIARY,
            activeforeground=self.theme.TEXT_INVERSE,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._exportar
        ).pack(side="right")
    
    def _toggle_deck_name(self):
        """Mostra/esconde campo de nome do deck."""
        if self.formato_var.get() == "anki_apkg":
            self.deck_entry.config(state="normal")
        else:
            self.deck_entry.config(state="disabled")
    
    def _exportar(self):
        """Confirma exportação."""
        self.deck_name = self.deck_entry.get().strip() or "Flashcards AnkiLab"
        self.result = self.formato_var.get()
        self.destroy()
    
    def _cancelar(self):
        """Cancela exportação."""
        self.result = None
        self.destroy()


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  PONTO DE ENTRADA                                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    root = tk.Tk()
    app = AnkiLabApp(root)
    root.mainloop()
