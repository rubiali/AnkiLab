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
from string import Template


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
APP_VERSION = "v2.1"
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
- Quando o conceito envolver programação, inclua código se isso aumentar a clareza.

━━━━━━━━━━
REGRAS DE RETENÇÃO (CRÍTICAS)
━━━━━━━━━━
PARA RESPOSTAS TEXTUAIS (conceitos, explicações):
- Devem ser CURTAS, OBJETIVAS e MENSURÁVEIS.
- Preferencialmente 1 frase.
- No máximo 2 frases curtas.
- Se uma resposta exigir mais de uma ideia, DIVIDA em mais de um cartão.
- O aluno deve conseguir avaliar claramente se acertou ou errou.

PARA RESPOSTAS COM CÓDIGO:
- O código pode ter quantas linhas forem necessárias para representar a ideia corretamente.
- NÃO force código em 1 linha se isso prejudicar a legibilidade.
- Priorize clareza e boas práticas no código.
- Inclua apenas o código essencial (sem boilerplate desnecessário).
- Uma breve explicação textual (1 linha) pode acompanhar o código se necessário.

━━━━━━━━━━
TIPOS DE CARTÃO (ordem de prioridade)
━━━━━━━━━━
1) Aplicação prática (incluindo código quando relevante)
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
EXEMPLO DE CARTÃO BOM — TEXTUAL (FAÇA ASSIM)
━━━━━━━━━━
Q: Por que a validação de formulário deve estar no back-end e não apenas no front-end?
A: Porque o front-end pode ser manipulado; o back-end garante segurança e integridade.

Q: Qual a consequência de escolher um hardware inferior às exigências do software?
A: Baixa performance, travamentos ou incompatibilidade.

━━━━━━━━━━
EXEMPLO DE CARTÃO BOM — COM CÓDIGO (FAÇA ASSIM)
━━━━━━━━━━
Q: Como criar uma list comprehension em Python que filtra apenas números pares de uma lista?
A:
pares = [x for x in lista if x % 2 == 0]

Q: Como fazer uma requisição GET assíncrona com fetch em JavaScript e tratar o JSON?
A:
async function getData(url) {{
  const response = await fetch(url);
  const data = await response.json();
  return data;
}}

Q: Como definir uma rota POST básica em Express.js que recebe JSON?
A:
app.use(express.json());

app.post('/api/dados', (req, res) => {{
  const dados = req.body;
  res.status(201).json({{ recebido: dados }});
}});

━━━━━━━━━━
CONTROLE DE QUALIDADE
━━━━━━━━━━
- Se dois cartões testarem a mesma ideia, mantenha apenas o MAIS DESAFIADOR.
- Evite cartões que apenas repitam frases do texto original.
- Para código: prefira exemplos práticos e realistas, não abstratos.

━━━━━━━━━━
MODO DE GERAÇÃO
━━━━━━━━━━
Modo: $MODO

- Se MANUAL:
  Gere exatamente $QTD flashcards.

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
8. Para código na resposta, coloque-o logo após "A:" (pode ter múltiplas linhas).

Formato:
Q: <pergunta>
A: <resposta curta OU código>

Q: <pergunta>
A: <resposta curta OU código>

━━━━━━━━━━
TEXTO PARA ANÁLISE
━━━━━━━━━━
$TEXTO
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
  - "Como implementar ... em código?"
  - "Como aplicar ... em uma situação concreta?"
  - "Diferencie X de Y em um caso prático"
  - "Qual o erro neste código e como corrigir?"
  - "Refatore este trecho para..."

━━━━━━━━━━
REGRAS DE RETENÇÃO
━━━━━━━━━━
PARA RESPOSTAS TEXTUAIS:
- Curtas: preferencialmente 1 frase, no máximo 2 frases curtas.
- Objetivas e mensuráveis.

PARA RESPOSTAS COM CÓDIGO:
- O código pode ter múltiplas linhas se necessário.
- Priorize legibilidade e boas práticas.
- Inclua apenas o essencial para demonstrar o conceito.
- NÃO comprima código em 1 linha só para economizar espaço.
- Uma breve explicação (1 linha) pode acompanhar o código se agregar valor.

━━━━━━━━━━
REGRAS ADICIONAIS
━━━━━━━━━━
- Evite repetir ideias: se dois cartões forem parecidos, mantenha o mais desafiador.
- Para programação, prefira perguntas que exijam escrever/corrigir/refatorar código.
- Código deve ser funcional e seguir convenções da linguagem.

━━━━━━━━━━
EXEMPLO DE CARTÃO HARD — TEXTUAL
━━━━━━━━━━
Q: Por que usar índices em colunas frequentemente filtradas pode degradar a performance de INSERTs?
A: Cada INSERT precisa atualizar todos os índices da tabela, aumentando o tempo de escrita.

Q: Qual o risco de capturar exceções genéricas (except Exception) em Python?
A: Pode mascarar erros inesperados e dificultar debugging, ocultando a causa real do problema.

━━━━━━━━━━
EXEMPLO DE CARTÃO HARD — COM CÓDIGO
━━━━━━━━━━
Q: Como implementar um decorator em Python que mede o tempo de execução de uma função?
A:
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{{func.__name__}} executou em {{time.time() - start:.4f}}s")
        return result
    return wrapper

Q: Como evitar SQL Injection ao fazer uma query com parâmetros em Python (sqlite3)?
A:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
Usar placeholders (?) e tupla de parâmetros em vez de concatenar strings.

Q: Refatore este código para usar list comprehension:
resultado = []
for i in range(10):
    if i % 2 == 0:
        resultado.append(i ** 2)
A:
resultado = [i ** 2 for i in range(10) if i % 2 == 0]

━━━━━━━━━━
MODO DE GERAÇÃO
━━━━━━━━━━
Modo: $MODO

- Se MANUAL:
  Gere exatamente $QTD flashcards.

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
8. Para código na resposta, coloque-o logo após "A:" (pode ter múltiplas linhas).

Formato:
Q: <pergunta>
A: <resposta ou código>

Q: <pergunta>
A: <resposta ou código>

━━━━━━━━━━
TEXTO PARA ANÁLISE
━━━━━━━━━━
$TEXTO
"""

REFINE_PROMPT = """
Você é um revisor extremamente rigoroso de flashcards para Anki.

Tarefa: Refinar os cartões abaixo para maximizar retenção e qualidade, respeitando o texto original.

━━━━━━━━━━
AÇÕES DE REFINAMENTO
━━━━━━━━━━
Você deve:
- Remover redundâncias (se dois cartões testarem a mesma ideia, mantenha o melhor).
- Transformar cartões definicionais em aplicação/consequência sempre que possível.
- Garantir 1 ideia por cartão.
- Evitar frases copiadas do texto (reformule).
- Manter o conteúdo fiel ao texto original.
- Melhorar clareza de código existente se necessário.

━━━━━━━━━━
REGRAS DE TAMANHO
━━━━━━━━━━
RESPOSTAS TEXTUAIS:
- Encurtar para preferencialmente 1 frase, no máximo 2 frases curtas.
- Deve ser possível avaliar objetivamente se acertou ou errou.

RESPOSTAS COM CÓDIGO:
- Código pode ter múltiplas linhas se necessário para clareza.
- NÃO comprimir código em 1 linha de forma forçada.
- Manter apenas o código essencial (remover boilerplate desnecessário).
- Garantir que o código seja funcional e legível.
- Uma breve explicação (1 linha) pode acompanhar o código se necessário.

━━━━━━━━━━
NÍVEL DE DIFICULDADE: $DIFICULDADE
━━━━━━━━━━
- Se HARD: seja agressivo em converter definição para aplicação, elimine cartões fáceis,
  prefira cartões que exijam escrever/corrigir/analisar código.
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
A: <resposta ou código>

Q: <pergunta>
A: <resposta ou código>

━━━━━━━━━━
TEXTO ORIGINAL (referência)
━━━━━━━━━━
$TEXTO

━━━━━━━━━━
CARTÕES PARA REFINAR
━━━━━━━━━━
$CARDS
"""



# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  FUNÇÕES DE PARSING E FORMATAÇÃO                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

def parse_cards(raw: str):
    """
    Parser robusto que extrai flashcards do formato Q:/A:
    Suporta respostas multilinhas (para código).
    Corrigido para não confundir Q:/A: dentro de código.
    """
    if not raw:
        return []
    
    try:
        raw = raw.replace("\r\n", "\n").strip()
        
        # Limpar markdown e lixo
        raw = re.sub(r"```[\w]*\n?", "", raw)  # Remove blocos de código markdown
        raw = raw.replace("**", "")
        raw = re.sub(r"^\d+[\.\)]\s*(Q:)", r"\1", raw, flags=re.MULTILINE)
        
        # Remover linhas de introdução/conclusão comuns
        lines_clean = []
        for ln in raw.split("\n"):
            s = ln.strip().lower()
            if s.startswith("[score:") or s.startswith("#"):
                continue
            if s.startswith("---") or s.startswith("***") or s.startswith("==="):
                continue
            if s.startswith("aqui estão") or s.startswith("aqui estao"):
                continue
            if s.startswith("seguem") or s.startswith("abaixo"):
                continue
            if s.startswith("espero que"):
                continue
            lines_clean.append(ln)
        
        raw = "\n".join(lines_clean)
        
        cards = []
        
        # CORREÇÃO: Regex mais restritiva
        # Q: DEVE estar no início absoluto da linha (sem indentação significativa)
        # Isso evita capturar Q:/A: dentro de código indentado
        q_pattern = re.compile(r"^(Q|P|Pergunta)\s*:", re.IGNORECASE | re.MULTILINE)
        
        matches = list(q_pattern.finditer(raw))
        
        if not matches:
            return []
        
        for i, match in enumerate(matches):
            start = match.start()
            
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(raw)
            
            block = raw[start:end].strip()
            
            q_lines = []
            a_lines = []
            cur = None
            in_code_block = False  # Flag para detectar blocos de código
            
            for ln in block.split("\n"):
                ln_original = ln  # Preservar original para código
                ln_stripped = ln.strip()
                
                # Detectar se estamos em um bloco de código (indentação >= 4 espaços ou tab)
                is_indented = ln.startswith("    ") or ln.startswith("\t")
                
                # CORREÇÃO CRÍTICA: 
                # Só reconhecer Q:/A: se:
                # 1. Está no início da linha (sem indentação)
                # 2. Não estamos no meio de código
                
                # Q: só no início, sem indentação
                q_match = re.match(r"^(Q|P|Pergunta)\s*:\s*(.*)$", ln_stripped, re.IGNORECASE)
                # A: só no início, sem indentação significativa
                a_match = re.match(r"^(A|R|Resposta)\s*:\s*(.*)$", ln_stripped, re.IGNORECASE)
                
                # Se a linha está indentada E já estamos em modo resposta, é código
                if cur == "A" and is_indented:
                    a_lines.append(ln_original.rstrip())
                    continue
                
                # Se a linha começa com caracteres típicos de código, é continuação
                if cur == "A" and ln_stripped and ln_stripped[0] in "{}[]();=><|&+-*/\\@#$%^":
                    a_lines.append(ln_original.rstrip())
                    continue
                
                # Verificar se Q: é válido (início do card)
                if q_match and cur is None:
                    cur = "Q"
                    content = q_match.group(2).strip()
                    if content:
                        q_lines.append(content)
                        
                # Verificar se A: é válido (não indentado, após Q:)
                elif a_match and cur == "Q" and not is_indented:
                    cur = "A"
                    content = a_match.group(2).strip()
                    if content:
                        a_lines.append(content)
                        
                # Linha de continuação
                else:
                    if cur == "Q" and ln_stripped:
                        # Pergunta geralmente não tem múltiplas linhas
                        q_lines.append(ln_stripped)
                    elif cur == "A":
                        # Resposta pode ter múltiplas linhas (código)
                        # Preservar formatação original
                        a_lines.append(ln_original.rstrip())
            
            # Limpar linhas vazias no início e final da resposta
            while a_lines and not a_lines[0].strip():
                a_lines.pop(0)
            while a_lines and not a_lines[-1].strip():
                a_lines.pop()
            
            # Montar pergunta e resposta
            q = re.sub(r"\s+", " ", " ".join(q_lines).strip())
            a = "\n".join(a_lines).strip()
            
            if q and a:
                cards.append({"q": q, "a": a})
        
        return cards
        
    except Exception as e:
        # Log para debug - em produção, usar logging
        print(f"[parse_cards] Erro: {type(e).__name__}: {e}")
        return []



def format_cards_for_export_tab(cards):
    """Formata cards para exportação em formato tabulado (Anki/Noji)."""
    lines = []
    for c in cards:
        # Substituir quebras de linha por <br> para o Anki
        q = c['q'].replace('\n', '<br>')
        a = c['a'].replace('\n', '<br>')
        lines.append(f"{q}\t{a}")
    return "\n".join(lines) + ("\n" if cards else "")


def format_cards_for_refine(cards):
    """Formata cards para envio ao prompt de refinamento."""
    lines = []
    for c in cards:
        lines.extend([f"Q: {c['q']}", f"A: {c['a']}", ""])
    return "\n".join(lines).strip()


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  CLASSE PRINCIPAL — AnkiLabApp                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class AnkiLabApp:
    """
    Aplicação AnkiLab - Gerador de Flashcards com IA.
    Interface compacta otimizada para notebooks.
    """
    
    def __init__(self, root):
        self.root = root
        self.theme = NeuroTheme
        self.cards_data = []
        
        # Configuração da janela
        self.root.title(f"{APP_NAME} • {APP_TAGLINE}")
        self.root.geometry("880x620")
        self.root.minsize(750, 450)
        self.root.configure(bg=self.theme.BG_MAIN)
        
        # Variáveis de controle
        self.qtd_var = tk.StringVar(value="AUTO")
        self.hard_var = tk.BooleanVar(value=False)
        self.refine_var = tk.BooleanVar(value=False)
        self.cards_count_var = tk.StringVar(value="0")
        
        # Construir interface
        self._build_header()
        self._build_main_content()
        self._build_options_panel()
        self._build_actions_bar()
        self._build_footer()
        
        self._update_char_counter()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  HEADER
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
    #  MAIN CONTENT
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
        
        # Header do painel
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
        self.text_input.bind("<FocusIn>", lambda e: text_border.config(bg=self.theme.BORDER_FOCUS))
        self.text_input.bind("<FocusOut>", lambda e: text_border.config(bg=self.theme.BORDER))
        
        # Barra inferior
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
        
        # Header com contador de cards
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
        
        # Badge contagem
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
        
        # Tags de formatação
        self.preview.tag_configure("header", foreground=self.theme.CARD_HEADER, font=self.theme.get_mono_font(8, "bold"))
        self.preview.tag_configure("pergunta", foreground=self.theme.CARD_Q, font=self.theme.get_mono_font(8, "bold"))
        self.preview.tag_configure("resposta", foreground=self.theme.CARD_A, font=self.theme.get_mono_font(8))
        self.preview.tag_configure("separator", foreground=self.theme.TEXT_MUTED, font=self.theme.get_mono_font(6))
        self.preview.tag_configure("processing", foreground=self.theme.ACCENT_PRIMARY, font=self.theme.get_mono_font(8), justify="center")
        self.preview.tag_configure("error", foreground=self.theme.ERROR, font=self.theme.get_mono_font(8))
        self.preview.tag_configure("card_num", foreground=self.theme.ACCENT_SECONDARY, font=self.theme.get_mono_font(7, "bold"))
        
        self._show_preview_placeholder()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  OPTIONS PANEL
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
    #  ACTIONS BAR
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
    #  FOOTER
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
   │                              │
   ╰──────────────────────────────╯
"""
        self.preview.insert("1.0", placeholder, "processing")
        self.preview.config(state="disabled")
    
    def _insert_preview_formatted(self, cards):
        """Insere os cards formatados no preview."""
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        
        if not cards:
            self.preview.insert("1.0", "Nenhum card gerado.", "error")
            self.preview.config(state="disabled")
            return
        
        self.cards_count_var.set(str(len(cards)))
        self.cards_data = cards
        
        for i, c in enumerate(cards):
            # Número do card
            self.preview.insert(tk.END, f"┌─ Card {i + 1}\n", "card_num")
            
            # Pergunta
            self.preview.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            
            # Resposta (pode ter múltiplas linhas para código)
            a_lines = c['a'].split('\n')
            for j, line in enumerate(a_lines):
                if j == 0:
                    self.preview.insert(tk.END, f"│ A: {line}\n", "resposta")
                else:
                    self.preview.insert(tk.END, f"│    {line}\n", "resposta")
            
            # Separador
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

        def chamar_api():
            try:
                qtd = self.qtd_var.get().strip().upper()
                modo = "AUTOMÁTICO" if qtd == "AUTO" else "MANUAL"

                base_prompt = PROMPT_HARD if hard else PROMPT_NORMAL
                # CORREÇÃO: Usar Template em vez de .format()
                prompt = Template(base_prompt).safe_substitute(MODO=modo, QTD=qtd, TEXTO=texto)

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
                    # CORREÇÃO: Usar Template em vez de .format()
                    refine_prompt = Template(REFINE_PROMPT).safe_substitute(
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
                    if len(cards2) >= max(1, int(len(cards1) * 0.5)):
                        cards_final = cards2

                self.root.after(0, lambda: self._finalizar_geracao(cards_final, hard, do_refine))

            except Exception as e:
                self.root.after(0, lambda m=str(e): self._erro_geracao(m))


        threading.Thread(target=chamar_api, daemon=True).start()
    
    def _finalizar_geracao(self, cards, hard, refined):
        self._insert_preview_formatted(cards)
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
                css="""
                    .card {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 18px;
                        text-align: left;
                        color: #e6edf3;
                        background: #0f1419;
                        padding: 24px;
                        line-height: 1.5;
                    }
                    pre, code {
                        font-family: 'Consolas', 'Cascadia Code', monospace;
                        background: #1a1f26;
                        padding: 12px;
                        border-radius: 6px;
                        display: block;
                        overflow-x: auto;
                        white-space: pre;
                    }
                """
            )
            deck = genanki.Deck(abs(hash(deck_name)) % (10 ** 10), deck_name)
            for c in self.cards_data:
                # Formatar resposta: detectar código e envolver em <pre>
                answer = c["a"]
                # Se parece código (contém indentação, {}, (), etc.), envolver em <pre>
                if '\n' in answer or any(char in answer for char in ['def ', 'function ', '{', '=>', 'import ', 'const ', 'let ', 'var ']):
                    answer = f"<pre><code>{answer}</code></pre>"
                
                deck.add_note(genanki.Note(
                    model=modelo,
                    fields=[c["q"], answer],
                    guid=genanki.guid_for(c["q"], c["a"])
                ))
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
        self._show_preview_placeholder()
        self._update_char_counter()
        self._update_mode_display()
        self._update_status("Campos limpos", "info")


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  DIALOG DE EXPORTAÇÃO                                                         ║
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
