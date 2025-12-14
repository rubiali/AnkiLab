"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         🧠 ANKILAB — COGNITIVE FLASHCARD ENGINE               ║
║                              Tema: NEURO / COGNITIVE LAB                      ║
║                                    v3.0                                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import csv
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from openai import OpenAI
import genanki
from string import Template
from io import StringIO


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
MODEL_REFINEMENT = "gpt-4o-mini"  # Modelo intermediário para refinamento
MODEL_ADVANCED = "gpt-4o"  # Modelo avançado para revisão
APP_VERSION = "v3.0"
APP_NAME = "AnkiLab"
APP_TAGLINE = "Cognitive Flashcard Engine"


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  PROMPTS DE GERAÇÃO                                                           ║
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
4. NÃO use markdown (sem **, ##, 
, -, •, etc.).
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
4. NÃO use markdown (sem **, ##,
, -, •, etc.).
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
4. NÃO use markdown (sem **, ##, 
, -, •, etc.).
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
# ║  PROMPTS DE REVISÃO DE DECK                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

PROMPT_AUDIT = """
Você é um especialista em educação, ciência cognitiva e design instrucional para sistemas de repetição espaçada (Anki).

━━━━━━━━━━
TAREFA: AUDITORIA DE COBERTURA
━━━━━━━━━━
Analise o deck de flashcards fornecido e identifique LACUNAS DE CONTEÚDO com base no tema informado.

TEMA/ASSUNTO DO DECK:
$ASSUNTO

━━━━━━━━━━
O QUE VOCÊ DEVE FAZER
━━━━━━━━━━

1) CONCEITOS COBERTOS:
   Liste os principais conceitos que JÁ ESTÃO no deck (seja conciso).

2) LACUNAS IDENTIFICADAS:
   Liste conceitos ESSENCIAIS do tema que estão FALTANDO ou foram abordados superficialmente.
   Para cada lacuna, indique:
   - O conceito que falta
   - Por que é importante para o tema
   - Prioridade: ALTA / MÉDIA / BAIXA

3) CARDS SUGERIDOS (NOVOS):
   Gere flashcards NOVOS para cobrir as lacunas de prioridade ALTA e MÉDIA e BAIXA.
   Use o formato Q:/A: padrão.
   Gere o máximo de cards necessários para cobrir todas as lacunas.
   
4) PROBLEMAS NO DECK ATUAL:
   Identifique cards problemáticos:
   - Redundantes (testam a mesma ideia)
   - Muito vagos ou genéricos
   - Respostas muito longas
   - Perguntas que podem ser respondidas por senso comum

━━━━━━━━━━
REGRAS CRÍTICAS
━━━━━━━━━━
- Base sua análise no conhecimento consolidado sobre o tema informado.
- Não invente conceitos que não existem no campo.
- Os novos cards devem seguir as melhores práticas de Anki:
  • 1 ideia por card
  • Respostas curtas e objetivas
  • Preferir aplicação/consequência sobre definição
  • Código quando relevante (legível, funcional)

É PROIBIDO:
- Gerar variações do mesmo comando trocando apenas parâmetros
- Criar séries do tipo:
  (stash x branch, stash x commit, stash x tag, etc.)
- Gerar mais de UM card por comando quando a diferença for apenas o alvo

━━━━━━━━━━
FORMATO DE SAÍDA (OBRIGATÓRIO)
━━━━━━━━━━

=== CONCEITOS COBERTOS ===
• [conceito 1]
• [conceito 2]
...

=== LACUNAS IDENTIFICADAS ===
1. [Conceito] — [Por que é importante] — Prioridade: [ALTA/MÉDIA/BAIXA]
2. ...

=== PROBLEMAS NO DECK ATUAL ===
• Card "[início da pergunta...]": [problema identificado]
• ...

=== NOVOS CARDS SUGERIDOS ===

Q: [pergunta]
A: [resposta]

Q: [pergunta]
A: [resposta]

...

━━━━━━━━━━
DECK ATUAL PARA ANÁLISE
━━━━━━━━━━
$CARDS
"""


PROMPT_FINAL_REVIEW = """
Você é um revisor profissional de decks Anki com expertise em ciência cognitiva e retenção de longo prazo.

━━━━━━━━━━
TAREFA: REVISÃO FINAL COMPLETA
━━━━━━━━━━
Revise o deck fornecido aplicando TODAS as melhorias necessárias para maximizar a retenção.

TEMA/ASSUNTO DO DECK:
$ASSUNTO

━━━━━━━━━━
AÇÕES OBRIGATÓRIAS
━━━━━━━━━━

1) REMOVER cards que:
   - São redundantes (mesma ideia que outro card)
   - São respondíveis por senso comum
   - São muito vagos ou genéricos
   - Têm perguntas que "entregam" a resposta

2) MODIFICAR cards para:
   - Transformar definições em aplicação/consequência
   - Encurtar respostas longas (máx 2 frases)
   - Melhorar clareza das perguntas
   - Corrigir erros factuais (baseado no tema)
   - Melhorar código (se houver)

3) DIVIDIR cards que:
   - Testam mais de uma ideia
   - Têm respostas com múltiplos pontos

4) ADICIONAR cards para:
   - Cobrir lacunas críticas do tema
   - Criar cards de aplicação onde só há definição

━━━━━━━━━━
REGRAS DE QUALIDADE
━━━━━━━━━━
- 1 ideia por card
- Respostas: preferencialmente 1 frase, máximo 2
- Preferir: aplicação > consequência > distinção > definição
- Código: legível, funcional, sem boilerplate
- Perguntas diretas, sem floreios

━━━━━━━━━━
REGRAS CRÍTICAS DE SAÍDA
━━━━━━━━━━
⚠️ ATENÇÃO MÁXIMA:
- NÃO DUPLIQUE cards! Cada card deve aparecer UMA ÚNICA VEZ.
- A contagem de "Total final" nas estatísticas DEVE bater com o número real de cards listados.
- Confira ANTES de responder: conte os cards e valide o número.
- Se um card foi modificado, liste apenas a versão NOVA (não a antiga).
- Se um card foi dividido, liste apenas os cards RESULTANTES.

━━━━━━━━━━
FORMATO DE SAÍDA (OBRIGATÓRIO)
━━━━━━━━━━

Primeiro, forneça o RELATÓRIO DE ALTERAÇÕES, depois os CARDS FINAIS.

=== RELATÓRIO DE ALTERAÇÕES ===

REMOVIDOS (X cards):
• "[início da pergunta...]" — Motivo: [razão]

MODIFICADOS (X cards):
• "[pergunta original...]" → "[nova pergunta...]" — Alteração: [o que mudou]

DIVIDIDOS (X cards):
• "[pergunta original...]" → Dividido em N cards

ADICIONADOS (X cards):
• "[nova pergunta...]" — Motivo: [lacuna coberta]

ESTATÍSTICAS:
- Cards originais: [número]
- Cards removidos: [número]
- Cards modificados: [número]
- Cards divididos: [número] (geraram [número] cards)
- Cards adicionados: [número]
- Total final: [DEVE SER = originais - removidos + novos_de_divisao + adicionados]

=== CARDS FINAIS ===

⚠️ LISTA ÚNICA - NÃO REPETIR NENHUM CARD

Q: [pergunta]
A: [resposta]

Q: [pergunta]
A: [resposta]

[... todos os cards UMA vez cada ...]

━━━━━━━━━━
DECK PARA REVISÃO
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
    """
    if not raw:
        return []
    
    try:
        raw = raw.replace("\r\n", "\n").strip()
        
        # Limpar markdown e lixo
        raw = re.sub(r"```[\w]*\n?", "", raw)
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
            
            for ln in block.split("\n"):
                ln_original = ln
                ln_stripped = ln.strip()
                
                is_indented = ln.startswith("    ") or ln.startswith("\t")
                
                q_match = re.match(r"^(Q|P|Pergunta)\s*:\s*(.*)$", ln_stripped, re.IGNORECASE)
                a_match = re.match(r"^(A|R|Resposta)\s*:\s*(.*)$", ln_stripped, re.IGNORECASE)
                
                if cur == "A" and is_indented:
                    a_lines.append(ln_original.rstrip())
                    continue
                
                if cur == "A" and ln_stripped and ln_stripped[0] in "{}[]();=><|&+-*/\\@#$%^":
                    a_lines.append(ln_original.rstrip())
                    continue
                
                if q_match and cur is None:
                    cur = "Q"
                    content = q_match.group(2).strip()
                    if content:
                        q_lines.append(content)
                        
                elif a_match and cur == "Q" and not is_indented:
                    cur = "A"
                    content = a_match.group(2).strip()
                    if content:
                        a_lines.append(content)
                        
                else:
                    if cur == "Q" and ln_stripped:
                        q_lines.append(ln_stripped)
                    elif cur == "A":
                        a_lines.append(ln_original.rstrip())
            
            while a_lines and not a_lines[0].strip():
                a_lines.pop(0)
            while a_lines and not a_lines[-1].strip():
                a_lines.pop()
            
            q = re.sub(r"\s+", " ", " ".join(q_lines).strip())
            a = "\n".join(a_lines).strip()
            
            if q and a:
                cards.append({"q": q, "a": a})
        
        return cards
        
    except Exception as e:
        print(f"[parse_cards] Erro: {type(e).__name__}: {e}")
        return []


def parse_csv_cards(file_path: str = None, csv_content: str = None):
    """
    Lê flashcards de um arquivo CSV ou string CSV.
    Suporta vírgula, ponto-e-vírgula e tab como delimitadores.
    Retorna lista de dicts com 'q' e 'a'.
    """
    cards = []
    
    try:
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = csv_content
        
        if not content.strip():
            return []
        
        # Detectar delimitador
        first_line = content.split('\n')[0]
        if '\t' in first_line:
            delimiter = '\t'
        elif ';' in first_line:
            delimiter = ';'
        else:
            delimiter = ','
        
        reader = csv.reader(StringIO(content), delimiter=delimiter)
        
        for row in reader:
            if len(row) >= 2:
                q = row[0].strip()
                a = row[1].strip()
                
                # Pular headers comuns
                if q.lower() in ['front', 'frente', 'pergunta', 'question', 'q']:
                    continue
                
                if q and a:
                    # Converter <br> de volta para quebras de linha
                    q = q.replace('<br>', '\n')
                    a = a.replace('<br>', '\n')
                    cards.append({"q": q, "a": a})
        
        return cards
        
    except Exception as e:
        print(f"[parse_csv_cards] Erro: {type(e).__name__}: {e}")
        return []


def format_cards_for_export_tab(cards):
    """Formata cards para exportação em formato tabulado (Anki/Noji)."""
    lines = []
    for c in cards:
        # Normalizar: primeiro converte \n literal para quebra real, depois para <br>
        q = c['q'].replace('\\n', '\n').replace('\n', '<br>')
        a = c['a'].replace('\\n', '\n').replace('\n', '<br>')
        lines.append(f"{q}\t{a}")
    return "\n".join(lines) + ("\n" if cards else "")



def format_cards_for_prompt(cards):
    """Formata cards para envio ao prompt."""
    lines = []
    for i, c in enumerate(cards, 1):
        lines.append(f"[Card {i}]")
        lines.append(f"Q: {c['q']}")
        lines.append(f"A: {c['a']}")
        lines.append("")
    return "\n".join(lines).strip()


def format_cards_for_refine(cards):
    """Formata cards para envio ao prompt de refinamento."""
    lines = []
    for c in cards:
        lines.extend([f"Q: {c['q']}", f"A: {c['a']}", ""])
    return "\n".join(lines).strip()


def extract_new_cards_from_audit(response: str):
    """Extrai novos cards sugeridos da resposta de auditoria."""
    cards = []
    
    # Procurar seção de novos cards
    markers = ["=== NOVOS CARDS SUGERIDOS ===", "NOVOS CARDS SUGERIDOS", "=== CARDS SUGERIDOS ==="]
    
    start_idx = -1
    for marker in markers:
        if marker in response:
            start_idx = response.find(marker) + len(marker)
            break
    
    if start_idx == -1:
        # Tentar extrair cards do final da resposta
        start_idx = 0
    
    # Extrair a parte com os cards
    cards_section = response[start_idx:]
    
    # Parse normal
    parsed = parse_cards(cards_section)
    
    return parsed


def extract_cards_from_review(response: str):
    """Extrai cards finais da resposta de revisão."""
    # Procurar seção de cards finais
    markers = ["=== CARDS FINAIS ===", "CARDS FINAIS", "=== DECK REVISADO ==="]
    
    start_idx = -1
    for marker in markers:
        if marker in response:
            start_idx = response.find(marker) + len(marker)
            break
    
    if start_idx == -1:
        return []
    
    cards_section = response[start_idx:]
    
    return parse_cards(cards_section)


def extract_report_from_review(response: str):
    """Extrai relatório de alterações da resposta de revisão."""
    # Procurar seção de relatório
    start_markers = ["=== RELATÓRIO DE ALTERAÇÕES ===", "RELATÓRIO DE ALTERAÇÕES"]
    end_markers = ["=== CARDS FINAIS ===", "CARDS FINAIS"]
    
    start_idx = -1
    for marker in start_markers:
        if marker in response:
            start_idx = response.find(marker)
            break
    
    if start_idx == -1:
        return "Relatório não encontrado na resposta."
    
    end_idx = len(response)
    for marker in end_markers:
        if marker in response:
            end_idx = response.find(marker)
            break
    
    report = response[start_idx:end_idx].strip()
    
    return report


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  CLASSE PRINCIPAL — AnkiLabApp                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class AnkiLabApp:
    """
    Aplicação AnkiLab - Gerador de Flashcards com IA.
    Interface com abas para geração e revisão de decks.
    """
    
    def __init__(self, root):
        self.root = root
        self.theme = NeuroTheme
        self.cards_data = []
        self.review_cards_data = []
        self.loaded_csv_cards = []
        
        # Configuração da janela
        self.root.title(f"{APP_NAME} • {APP_TAGLINE}")
        self.root.geometry("950x700")
        self.root.minsize(850, 550)
        self.root.configure(bg=self.theme.BG_MAIN)
        
        # Variáveis de controle - Geração
        self.qtd_var = tk.StringVar(value="AUTO")
        self.hard_var = tk.BooleanVar(value=False)
        self.refine_var = tk.BooleanVar(value=False)
        self.cards_count_var = tk.StringVar(value="0")
        
        # Variáveis de controle - Revisão
        self.assunto_var = tk.StringVar(value="")
        self.review_mode_var = tk.StringVar(value="audit")
        self.loaded_count_var = tk.StringVar(value="0 cards carregados")
        self.review_count_var = tk.StringVar(value="0")
        
        # Construir interface
        self._build_header()
        self._build_notebook()
        self._build_footer()
    
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
            model_frame, text=f"{MODEL_NAME} / {MODEL_ADVANCED}",
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Separador
        tk.Frame(self.root, bg=self.theme.BORDER, height=1).pack(fill="x", side="top")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  NOTEBOOK (ABAS)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_notebook(self):
        # Estilo customizado para o notebook
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure('Custom.TNotebook', 
                       background=self.theme.BG_MAIN,
                       borderwidth=0)
        style.configure('Custom.TNotebook.Tab',
                       background=self.theme.BG_TERTIARY,
                       foreground=self.theme.TEXT_SECONDARY,
                       padding=[15, 8],
                       font=self.theme.get_ui_font(9))
        style.map('Custom.TNotebook.Tab',
                 background=[('selected', self.theme.BG_SECONDARY)],
                 foreground=[('selected', self.theme.ACCENT_PRIMARY)])
        
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Aba 1: Geração de Cards
        self.tab_generate = tk.Frame(self.notebook, bg=self.theme.BG_MAIN)
        self.notebook.add(self.tab_generate, text="  📝 Gerar Cards  ")
        self._build_generate_tab()
        
        # Aba 2: Revisão de Deck
        self.tab_review = tk.Frame(self.notebook, bg=self.theme.BG_MAIN)
        self.notebook.add(self.tab_review, text="  🔍 Revisar Deck  ")
        self._build_review_tab()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  ABA DE GERAÇÃO (original)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_generate_tab(self):
        main_container = tk.Frame(self.tab_generate, bg=self.theme.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_container.grid_columnconfigure(0, weight=45, minsize=280)
        main_container.grid_columnconfigure(1, weight=55, minsize=320)
        main_container.grid_rowconfigure(0, weight=1)
        
        self._build_gen_left_panel(main_container)
        self._build_gen_right_panel(main_container)
        self._build_gen_options_panel()
        self._build_gen_actions_bar()
        
        self._update_char_counter()
    
    def _build_gen_left_panel(self, parent):
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
    
    def _build_gen_right_panel(self, parent):
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
    
    def _build_gen_options_panel(self):
        options_container = tk.Frame(self.tab_generate, bg=self.theme.BG_MAIN)
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
    
    def _build_gen_actions_bar(self):
        actions_container = tk.Frame(self.tab_generate, bg=self.theme.BG_MAIN)
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
    #  ABA DE REVISÃO DE DECK
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_review_tab(self):
        main_container = tk.Frame(self.tab_review, bg=self.theme.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_container.grid_columnconfigure(0, weight=40, minsize=300)
        main_container.grid_columnconfigure(1, weight=60, minsize=400)
        main_container.grid_rowconfigure(0, weight=1)
        
        self._build_review_left_panel(main_container)
        self._build_review_right_panel(main_container)
        self._build_review_actions_bar()
    
    def _build_review_left_panel(self, parent):
        """Painel esquerdo: configurações e CSV carregado."""
        left_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Header
        panel_header = tk.Frame(left_panel, bg=self.theme.BG_TERTIARY, height=32)
        panel_header.pack(fill="x", side="top")
        panel_header.pack_propagate(False)
        
        header_content = tk.Frame(panel_header, bg=self.theme.BG_TERTIARY)
        header_content.pack(fill="both", expand=True, padx=10, pady=6)
        
        tk.Label(
            header_content, text="📂", font=("Segoe UI Emoji", 9),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left", padx=(0, 5))
        
        tk.Label(
            header_content, text="CONFIGURAÇÃO DA REVISÃO",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Conteúdo
        content_frame = tk.Frame(left_panel, bg=self.theme.BG_SECONDARY, padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)
        
        # Campo de assunto
        tk.Label(
            content_frame, text="Tema/Assunto do Deck:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        assunto_border = tk.Frame(content_frame, bg=self.theme.BORDER, padx=1, pady=1)
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
        self.assunto_entry.bind("<FocusIn>", lambda e: (
            self.assunto_entry.delete(0, tk.END) if self.assunto_entry.get().startswith("Ex:") else None,
            assunto_border.config(bg=self.theme.BORDER_FOCUS)
        ))
        self.assunto_entry.bind("<FocusOut>", lambda e: assunto_border.config(bg=self.theme.BORDER))
        
        # Botão carregar CSV
        tk.Label(
            content_frame, text="Arquivo CSV:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(5, 4))
        
        load_frame = tk.Frame(content_frame, bg=self.theme.BG_SECONDARY)
        load_frame.pack(fill="x", pady=(0, 5))
        
        self.btn_load_csv = tk.Button(
            load_frame, text="  📁 Carregar CSV  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.ACCENT_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.ACCENT_TERTIARY,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self._load_csv
        )
        self.btn_load_csv.pack(side="left")
        
        self.loaded_label = tk.Label(
            load_frame, textvariable=self.loaded_count_var,
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_SECONDARY
        )
        self.loaded_label.pack(side="left", padx=(10, 0))
        
        # Separador
        tk.Frame(content_frame, bg=self.theme.BORDER, height=1).pack(fill="x", pady=15)
        
        # Modo de revisão
        tk.Label(
            content_frame, text="Modo de Revisão:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        # Opção 1: Auditoria
        audit_frame = tk.Frame(content_frame, bg=self.theme.BG_SECONDARY)
        audit_frame.pack(fill="x", pady=2)
        
        tk.Radiobutton(
            audit_frame, variable=self.review_mode_var, value="audit",
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0
        ).pack(side="left")
        
        audit_label_frame = tk.Frame(audit_frame, bg=self.theme.BG_SECONDARY)
        audit_label_frame.pack(side="left", fill="y")
        
        tk.Label(
            audit_label_frame, text="🔎 Auditoria de Cobertura",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            audit_label_frame, text="Analisa lacunas e sugere novos cards",
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # Opção 2: Revisão Final
        review_frame = tk.Frame(content_frame, bg=self.theme.BG_SECONDARY)
        review_frame.pack(fill="x", pady=2)
        
        tk.Radiobutton(
            review_frame, variable=self.review_mode_var, value="final",
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_SECONDARY,
            selectcolor=self.theme.BG_INPUT, highlightthickness=0
        ).pack(side="left")
        
        review_label_frame = tk.Frame(review_frame, bg=self.theme.BG_SECONDARY)
        review_label_frame.pack(side="left", fill="y")
        
        tk.Label(
            review_label_frame, text="✨ Revisão Final Completa",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            review_label_frame, text="Melhora, remove, modifica e adiciona cards",
            font=self.theme.get_ui_font(6),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # Preview dos cards carregados
        tk.Frame(content_frame, bg=self.theme.BORDER, height=1).pack(fill="x", pady=15)
        
        tk.Label(
            content_frame, text="Preview do Deck Carregado:",
            font=self.theme.get_ui_font(8, "bold"),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        preview_border = tk.Frame(content_frame, bg=self.theme.BORDER, padx=1, pady=1)
        preview_border.pack(fill="both", expand=True)
        
        self.loaded_preview = tk.Text(
            preview_border, wrap="word",
            font=self.theme.get_mono_font(7),
            bg=self.theme.BG_INPUT, fg=self.theme.TEXT_SECONDARY,
            relief="flat", padx=6, pady=4, highlightthickness=0,
            state="disabled", height=8
        )
        self.loaded_preview.pack(fill="both", expand=True)
    
    def _build_review_right_panel(self, parent):
        """Painel direito: resultado da revisão."""
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
        
        # Badge contagem
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
        
        # Tags de formatação
        self.review_result.tag_configure("header", foreground=self.theme.CARD_HEADER, font=self.theme.get_mono_font(9, "bold"))
        self.review_result.tag_configure("subheader", foreground=self.theme.ACCENT_SECONDARY, font=self.theme.get_mono_font(8, "bold"))
        self.review_result.tag_configure("pergunta", foreground=self.theme.CARD_Q, font=self.theme.get_mono_font(8, "bold"))
        self.review_result.tag_configure("resposta", foreground=self.theme.CARD_A, font=self.theme.get_mono_font(8))
        self.review_result.tag_configure("info", foreground=self.theme.INFO, font=self.theme.get_mono_font(8))
        self.review_result.tag_configure("warning", foreground=self.theme.WARNING, font=self.theme.get_mono_font(8))
        self.review_result.tag_configure("success", foreground=self.theme.SUCCESS, font=self.theme.get_mono_font(8))
        self.review_result.tag_configure("error", foreground=self.theme.ERROR, font=self.theme.get_mono_font(8))
        self.review_result.tag_configure("muted", foreground=self.theme.TEXT_MUTED, font=self.theme.get_mono_font(7))
        self.review_result.tag_configure("processing", foreground=self.theme.ACCENT_PRIMARY, font=self.theme.get_mono_font(8), justify="center")
        
        self._show_review_placeholder()
    
    def _build_review_actions_bar(self):
        actions_container = tk.Frame(self.tab_review, bg=self.theme.BG_MAIN)
        actions_container.pack(fill="x", padx=10, pady=(0, 5))
        
        actions_panel = tk.Frame(actions_container, bg=self.theme.BG_TERTIARY)
        actions_panel.pack(fill="x")
        
        actions_content = tk.Frame(actions_panel, bg=self.theme.BG_TERTIARY)
        actions_content.pack(fill="x", padx=10, pady=8)
        
        # Botão principal
        self.btn_revisar = tk.Button(
            actions_content, text="  🔍  EXECUTAR REVISÃO  ",
            font=self.theme.get_ui_font(9, "bold"),
            bg=self.theme.ACCENT_PRIMARY, fg=self.theme.TEXT_INVERSE,
            activebackground=self.theme.ACCENT_TERTIARY,
            relief="flat", cursor="hand2", padx=10, pady=5,
            command=self._executar_revisao
        )
        self.btn_revisar.pack(side="left", padx=(0, 10))
        self.btn_revisar.bind("<Enter>", lambda e: self.btn_revisar.config(bg=self.theme.ACCENT_TERTIARY))
        self.btn_revisar.bind("<Leave>", lambda e: self.btn_revisar.config(bg=self.theme.ACCENT_PRIMARY))
        
        # Separador
        tk.Frame(actions_content, bg=self.theme.BORDER, width=1).pack(side="left", fill="y", padx=10)
        
        # Botões secundários
        self.btn_export_review = tk.Button(
            actions_content, text="  💾 Exportar Resultado  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self._exportar_review
        )
        self.btn_export_review.pack(side="left", padx=(0, 5))
        self.btn_export_review.bind("<Enter>", lambda e: self.btn_export_review.config(bg=self.theme.BG_HOVER))
        self.btn_export_review.bind("<Leave>", lambda e: self.btn_export_review.config(bg=self.theme.BG_SECONDARY))
        
        self.btn_copy_review = tk.Button(
            actions_content, text="  📋 Copiar Cards  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self._copiar_review
        )
        self.btn_copy_review.pack(side="left", padx=(0, 5))
        self.btn_copy_review.bind("<Enter>", lambda e: self.btn_copy_review.config(bg=self.theme.BG_HOVER))
        self.btn_copy_review.bind("<Leave>", lambda e: self.btn_copy_review.config(bg=self.theme.BG_SECONDARY))
        
        self.btn_clear_review = tk.Button(
            actions_content, text="  🔄 Limpar  ",
            font=self.theme.get_ui_font(8),
            bg=self.theme.BG_SECONDARY, fg=self.theme.TEXT_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            relief="flat", cursor="hand2", padx=8, pady=4,
            command=self._limpar_review
        )
        self.btn_clear_review.pack(side="left")
        self.btn_clear_review.bind("<Enter>", lambda e: self.btn_clear_review.config(bg=self.theme.BG_HOVER))
        self.btn_clear_review.bind("<Leave>", lambda e: self.btn_clear_review.config(bg=self.theme.BG_SECONDARY))
        
        # Indicador de modelo
        tk.Label(
            actions_content, text=f"Usando: {MODEL_ADVANCED}",
            font=self.theme.get_mono_font(6),
            bg=self.theme.BG_TERTIARY, fg=self.theme.TEXT_MUTED
        ).pack(side="right")
    
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
            status_frame, text="Pronto",
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
    
    def _update_mode_display(self):
        if self.hard_var.get():
            self.mode_label.config(text="MODO: HARD", fg=self.theme.ERROR)
        else:
            self.mode_label.config(text="MODO: NORMAL", fg=self.theme.ACCENT_PRIMARY)
    
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
    
    def _show_review_placeholder(self):
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        placeholder = """

   ╭──────────────────────────────────╮
   │                                  │
   │   1. Informe o tema/assunto      │
   │   2. Carregue um arquivo CSV     │
   │   3. Escolha o modo de revisão   │
   │   4. Clique em EXECUTAR REVISÃO  │
   │                                  │
   │   O resultado aparecerá aqui     │
   │                                  │
   ╰──────────────────────────────────╯
"""
        self.review_result.insert("1.0", placeholder, "processing")
        self.review_result.config(state="disabled")
    
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
            self.preview.insert(tk.END, f"┌─ Card {i + 1}\n", "card_num")
            self.preview.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            
            a_lines = c['a'].split('\n')
            for j, line in enumerate(a_lines):
                if j == 0:
                    self.preview.insert(tk.END, f"│ A: {line}\n", "resposta")
                else:
                    self.preview.insert(tk.END, f"│    {line}\n", "resposta")
            
            if i < len(cards) - 1:
                self.preview.insert(tk.END, "└─────────────────────────────\n\n", "separator")
            else:
                self.preview.insert(tk.END, "└─────────────────────────────\n", "separator")
        
        self.preview.config(state="disabled")
    
    def _set_busy(self, is_busy: bool, msg: str = ""):
        state = "disabled" if is_busy else "normal"
        
        # Botões da aba de geração
        self.btn_gerar.config(state=state)
        self.btn_exportar.config(state=state)
        self.btn_copiar.config(state=state)
        self.btn_limpar.config(state=state)
        
        # Botões da aba de revisão
        self.btn_revisar.config(state=state)
        self.btn_export_review.config(state=state)
        self.btn_copy_review.config(state=state)
        self.btn_clear_review.config(state=state)
        self.btn_load_csv.config(state=state)
        
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
    #  AÇÕES DA ABA DE GERAÇÃO
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
                prompt = Template(base_prompt).safe_substitute(MODO=modo, QTD=qtd, TEXTO=texto)

                self._update_status("Gerando (1ª passada)...", "warning")
                
                resp1 = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.45,
                    max_tokens=15000
                )
                raw1 = (resp1.choices[0].message.content or "").strip()
                cards1 = parse_cards(raw1)

                if not cards1:
                    raise RuntimeError("Não consegui extrair cards. Tente reformular o texto.")

                cards_final = cards1
                if do_refine and len(cards1) >= 1:
                    self._update_status("Refinando (2ª passada)...", "warning")
                    cards_text = format_cards_for_refine(cards1)
                    refine_prompt = Template(REFINE_PROMPT).safe_substitute(
                        DIFICULDADE=("HARD" if hard else "NORMAL"),
                        TEXTO=texto, 
                        CARDS=cards_text
                    )
                    resp2 = client.chat.completions.create(
                        model=MODEL_REFINEMENT,
                        messages=[{"role": "user", "content": refine_prompt}],
                        temperature=0.3,
                        max_tokens=15000
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
            self._export_apkg(dialog.deck_name, self.cards_data)
        else:
            self._export_txt("anki" if dialog.result == "anki_txt" else "noji", self.cards_data)
    
    def _export_apkg(self, deck_name, cards):
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
            for c in cards:
                answer = c["a"].replace('\\n', '\n')
                if '\n' in answer or any(char in answer for char in ['def ', 'function ', '{', '=>', 'import ', 'const ', 'let ', 'var ']):
                    answer = f"<pre><code>{answer}</code></pre>"
                
                deck.add_note(genanki.Note(
                    model=modelo,
                    fields=[c["q"].replace('\\n', '\n'), answer],  # Também normalizar pergunta
                    guid=genanki.guid_for(c["q"], c["a"])
                ))
            genanki.Package(deck).write_to_file(path)

            self._update_status(f"Exportado: {len(cards)} cards", "success")
            messagebox.showinfo("Sucesso", f"✓ {len(cards)} cards exportados!\n\nNo Anki: Arquivo → Importar")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def _export_txt(self, target, cards):
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
                f.write(format_cards_for_export_tab(cards))
            self._update_status(f"Exportado: {len(cards)} cards", "success")
            messagebox.showinfo("Sucesso", f"✓ {len(cards)} cards exportados!")
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    #  AÇÕES DA ABA DE REVISÃO
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _load_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("Texto", "*.txt"), ("Todos", "*.*")],
            title="Carregar arquivo de flashcards"
        )
        if not path:
            return
        
        try:
            cards = parse_csv_cards(file_path=path)
            
            if not cards:
                messagebox.showerror("Erro", "Não foi possível extrair cards do arquivo.\nVerifique o formato (2 colunas: pergunta, resposta).")
                return
            
            self.loaded_csv_cards = cards
            self.loaded_count_var.set(f"{len(cards)} cards carregados")
            
            # Mostrar preview
            self.loaded_preview.config(state="normal")
            self.loaded_preview.delete("1.0", tk.END)
            
            preview_text = f"Total: {len(cards)} cards\n\n"
            for i, c in enumerate(cards[:5]):  # Mostrar apenas os 5 primeiros
                q_short = c['q'][:60] + "..." if len(c['q']) > 60 else c['q']
                preview_text += f"{i+1}. {q_short}\n"
            
            if len(cards) > 5:
                preview_text += f"\n... e mais {len(cards) - 5} cards"
            
            self.loaded_preview.insert("1.0", preview_text)
            self.loaded_preview.config(state="disabled")
            
            self._update_status(f"CSV carregado: {len(cards)} cards", "success")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
    
    def _executar_revisao(self):
        assunto = self.assunto_var.get().strip()
        if not assunto or assunto.startswith("Ex:"):
            messagebox.showerror("Erro", "Informe o tema/assunto do deck.")
            return
        
        if not self.loaded_csv_cards:
            messagebox.showerror("Erro", "Carregue um arquivo CSV primeiro.")
            return
        
        mode = self.review_mode_var.get()
        
        self._set_busy(True, "Executando revisão...")
        
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        
        if mode == "audit":
            msg = "\n\n    ⏳ Executando Auditoria de Cobertura...\n\n    Analisando lacunas e sugerindo novos cards...\n"
        else:
            msg = "\n\n    ⏳ Executando Revisão Final Completa...\n\n    Melhorando, removendo e adicionando cards...\n"
        
        self.review_result.insert(tk.END, msg, "processing")
        self.review_result.config(state="disabled")
        
        self.review_count_var.set("...")

        def chamar_api():
            try:
                cards_text = format_cards_for_prompt(self.loaded_csv_cards)
                
                if mode == "audit":
                    prompt = Template(PROMPT_AUDIT).safe_substitute(
                        ASSUNTO=assunto,
                        CARDS=cards_text
                    )
                else:
                    prompt = Template(PROMPT_FINAL_REVIEW).safe_substitute(
                        ASSUNTO=assunto,
                        CARDS=cards_text
                    )
                
                self._update_status(f"Processando com {MODEL_ADVANCED}...", "warning")
                
                resp = client.chat.completions.create(
                    model=MODEL_ADVANCED,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=16000  
                )
                
                response_text = (resp.choices[0].message.content or "").strip()
                
                self.root.after(0, lambda: self._finalizar_revisao(response_text, mode))

            except Exception as e:
                self.root.after(0, lambda m=str(e): self._erro_revisao(m))

        threading.Thread(target=chamar_api, daemon=True).start()
    
    def _finalizar_revisao(self, response: str, mode: str):
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        
        if mode == "audit":
            # Extrair novos cards sugeridos
            new_cards = extract_new_cards_from_audit(response)
            self.review_cards_data = new_cards
            self.review_count_var.set(str(len(new_cards)))
            
            # Mostrar resposta completa formatada
            self._format_audit_response(response)
            
        else:
            # Extrair cards finais e relatório
            final_cards = extract_cards_from_review(response)
            report = extract_report_from_review(response)
            
            self.review_cards_data = final_cards
            self.review_count_var.set(str(len(final_cards)))
            
            # Mostrar relatório e cards
            self._format_review_response(report, final_cards)
        
        self.review_result.config(state="disabled")
        self._set_busy(False)
        
        mode_txt = "Auditoria" if mode == "audit" else "Revisão Final"
        self._update_status(f"✓ {mode_txt} concluída • {len(self.review_cards_data)} cards", "success")
    
    def _format_audit_response(self, response: str):
        """Formata a resposta de auditoria para exibição."""
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
    
    def _format_review_response(self, report: str, cards: list):
        """Formata a resposta de revisão final para exibição."""
        # Mostrar relatório
        self.review_result.insert(tk.END, "═" * 50 + "\n", "muted")
        self.review_result.insert(tk.END, "  RELATÓRIO DE ALTERAÇÕES\n", "header")
        self.review_result.insert(tk.END, "═" * 50 + "\n\n", "muted")
        
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
        
        # Mostrar cards finais
        self.review_result.insert(tk.END, "\n" + "═" * 50 + "\n", "muted")
        self.review_result.insert(tk.END, f"  CARDS FINAIS ({len(cards)} cards)\n", "header")
        self.review_result.insert(tk.END, "═" * 50 + "\n\n", "muted")
        
        for i, c in enumerate(cards):
            self.review_result.insert(tk.END, f"┌─ Card {i + 1}\n", "subheader")
            self.review_result.insert(tk.END, f"│ Q: {c['q']}\n", "pergunta")
            
            a_lines = c['a'].split('\n')
            for j, aline in enumerate(a_lines):
                if j == 0:
                    self.review_result.insert(tk.END, f"│ A: {aline}\n", "resposta")
                else:
                    self.review_result.insert(tk.END, f"│    {aline}\n", "resposta")
            
            self.review_result.insert(tk.END, "└" + "─" * 40 + "\n\n", "muted")
    
    def _erro_revisao(self, mensagem: str):
        self.review_result.config(state="normal")
        self.review_result.delete("1.0", tk.END)
        self.review_result.insert(tk.END, f"\n  ❌ Erro:\n\n  {mensagem}", "error")
        self.review_result.config(state="disabled")
        self.review_count_var.set("0")
        self._set_busy(False)
        self._update_status("Erro na revisão", "error")
        messagebox.showerror("Erro", mensagem)
    
    def _exportar_review(self):
        if not self.review_cards_data:
            messagebox.showwarning("Aviso", "Nenhum card para exportar.")
            return

        dialog = ExportDialog(self.root, len(self.review_cards_data), self.theme, title="Exportar Resultado da Revisão")
        self.root.wait_window(dialog)
        
        if not dialog.result:
            return
        
        if dialog.result == "anki_apkg":
            self._export_apkg(dialog.deck_name, self.review_cards_data)
        else:
            self._export_txt("anki" if dialog.result == "anki_txt" else "noji", self.review_cards_data)
    
    def _copiar_review(self):
        if not self.review_cards_data:
            messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(format_cards_for_export_tab(self.review_cards_data))
        self.root.update()
        self._update_status("Copiado! (formato Tab)", "success")
    
    def _limpar_review(self):
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
        self._update_status("Campos limpos", "info")


# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║  DIALOG DE EXPORTAÇÃO                                                         ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

class ExportDialog(tk.Toplevel):
    def __init__(self, parent, num_cards, theme, title="Exportar"):
        super().__init__(parent)
        self.theme = theme
        self.result = None
        self.deck_name = "Flashcards AnkiLab"
        
        self.title(title)
        self.geometry("340x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=self.theme.BG_MAIN)
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 170
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
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
