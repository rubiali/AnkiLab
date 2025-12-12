import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from openai import OpenAI
import genanki

# =========================
# VALIDAÇÃO INICIAL
# =========================
def validar_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "API Key não encontrada",
            "Defina a variável de ambiente OPENAI_API_KEY antes de executar o aplicativo.\n\n"
            "Windows (CMD): set OPENAI_API_KEY=sua_chave\n"
            "Windows (PowerShell): $env:OPENAI_API_KEY='sua_chave'\n"
            "Linux/Mac: export OPENAI_API_KEY=sua_chave"
        )
        return None
    return key


api_key = validar_api_key()
if not api_key:
    raise SystemExit(1)

# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(api_key=api_key)

MODEL_NAME = "gpt-4.1-mini"
APP_VERSION = "v1.4"

# =========================
# PROMPTS
# =========================
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

# =========================
# PARSING / SCORING
# =========================
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
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return 0
    return len(s.split(" "))


def score_card(q: str, a: str, hard: bool) -> float:
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


def format_cards_for_preview(cards, hard: bool):
    if not cards:
        return ""

    scores = [score_card(c["q"], c["a"], hard) for c in cards]
    avg = round(sum(scores) / len(scores), 1) if scores else 0.0

    out_lines = []
    out_lines.append(f"📊 Média de qualidade: {avg}/10  •  Cards: {len(cards)}")
    out_lines.append("")

    for i, c in enumerate(cards):
        sc = scores[i]
        out_lines.append(f"[Score: {sc}/10]")
        out_lines.append(f"Q: {c['q']}")
        out_lines.append(f"A: {c['a']}")
        out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n"


def format_cards_for_export_tab(cards):
    """Formato tabulado: Frente<TAB>Verso (funciona para Anki .txt e Noji)"""
    lines = []
    for c in cards:
        lines.append(f"{c['q']}\t{c['a']}")
    return "\n".join(lines) + ("\n" if lines else "")


def format_cards_for_refine(cards):
    lines = []
    for c in cards:
        lines.append(f"Q: {c['q']}")
        lines.append(f"A: {c['a']}")
        lines.append("")
    return "\n".join(lines).strip()


# =========================
# DIALOG DE EXPORTAÇÃO
# =========================
class ExportDialog(tk.Toplevel):
    def __init__(self, parent, num_cards):
        super().__init__(parent)
        self.title("Exportar Flashcards")
        self.geometry("420x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.deck_name = "Flashcards Gerados"
        
        # Centraliza
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (420 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (280 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Info
        ttk.Label(
            frame, 
            text=f"📦 {num_cards} flashcard(s) prontos para exportar",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(0, 15))
        
        # Escolha do formato
        ttk.Label(frame, text="Escolha o formato de exportação:").pack(anchor="w")
        
        self.formato_var = tk.StringVar(value="anki_apkg")
        
        formatos_frame = ttk.Frame(frame)
        formatos_frame.pack(fill="x", pady=10)
        
        ttk.Radiobutton(
            formatos_frame, 
            text="📗 Anki (.apkg) - Pacote nativo", 
            variable=self.formato_var, 
            value="anki_apkg",
            command=self.toggle_deck_name
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            formatos_frame, 
            text="📄 Anki (.txt) - Texto tabulado", 
            variable=self.formato_var, 
            value="anki_txt",
            command=self.toggle_deck_name
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            formatos_frame, 
            text="🟣 Noji (.txt) - Texto tabulado", 
            variable=self.formato_var, 
            value="noji_txt",
            command=self.toggle_deck_name
        ).pack(anchor="w", pady=2)
        
        # Nome do deck (só para .apkg)
        self.deck_frame = ttk.Frame(frame)
        self.deck_frame.pack(fill="x", pady=(10, 5))
        
        ttk.Label(self.deck_frame, text="Nome do Deck:").pack(anchor="w")
        self.deck_entry = ttk.Entry(self.deck_frame, width=45)
        self.deck_entry.insert(0, "Flashcards Gerados")
        self.deck_entry.pack(fill="x", pady=(2, 0))
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(15, 0))
        
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar, width=12).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Exportar", command=self.exportar, width=12).pack(side="right")
    
    def toggle_deck_name(self):
        """Mostra/esconde campo de nome do deck conforme formato"""
        if self.formato_var.get() == "anki_apkg":
            self.deck_entry.config(state="normal")
        else:
            self.deck_entry.config(state="disabled")
    
    def exportar(self):
        self.deck_name = self.deck_entry.get().strip() or "Flashcards Gerados"
        self.result = self.formato_var.get()
        self.destroy()
    
    def cancelar(self):
        self.result = None
        self.destroy()


# =========================
# FUNÇÕES UI
# =========================
def atualizar_contador(event=None):
    texto = text_input.get("1.0", tk.END).strip()
    chars = len(texto)
    tokens_est = chars // 4
    contador_label.config(text=f"{chars:,} caracteres  •  ~{tokens_est:,} tokens")


def inserir_preview_formatado(texto: str):
    preview.config(state="normal")
    preview.delete("1.0", tk.END)

    for linha in texto.split("\n"):
        s = linha.strip()
        if s.startswith("📊"):
            preview.insert(tk.END, linha + "\n", "header")
        elif s.startswith("[Score:"):
            preview.insert(tk.END, linha + "\n", "score")
        elif s.startswith("Q:"):
            preview.insert(tk.END, linha + "\n", "pergunta")
        elif s.startswith("A:"):
            preview.insert(tk.END, linha + "\n", "resposta")
        else:
            preview.insert(tk.END, linha + "\n")

    preview.config(state="disabled")


def set_busy(is_busy: bool, msg: str = ""):
    if is_busy:
        btn_gerar.config(state="disabled")
        btn_exportar.config(state="disabled")
        btn_copiar.config(state="disabled")
        btn_limpar.config(state="disabled")
        if msg:
            status_label.config(text=msg)
    else:
        btn_gerar.config(state="normal")
        btn_exportar.config(state="normal")
        btn_copiar.config(state="normal")
        btn_limpar.config(state="normal")


def atualizar_status(msg: str):
    root.after(0, lambda: status_label.config(text=msg))


def gerar_cards():
    texto = text_input.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showerror("Erro", "Insira um texto para análise.")
        return

    hard = bool(hard_var.get())
    do_refine = bool(refine_var.get())

    set_busy(True, "⏳ Gerando flashcards... aguarde.")
    preview.config(state="normal")
    preview.delete("1.0", tk.END)
    preview.insert(tk.END, "⏳ Processando sua solicitação...\n\nIsso pode levar alguns segundos.")
    preview.config(state="disabled")

    def chamar_api():
        try:
            qtd = qtd_var.get().strip().upper()
            modo = "AUTOMÁTICO" if qtd == "AUTO" else "MANUAL"

            base_prompt = PROMPT_HARD if hard else PROMPT_NORMAL
            prompt = base_prompt.format(MODO=modo, QTD=qtd, TEXTO=texto)

            atualizar_status("⏳ Gerando flashcards (1ª passada)...")
            
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
                    "- Texto muito curto ou vago\n"
                    "- API retornou formato inesperado\n\n"
                    "Tente novamente ou reduza/reformule o texto."
                )

            cards_final = cards1
            if do_refine and len(cards1) >= 1:
                atualizar_status("🧼 Refinando flashcards (2ª passada)...")

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

            preview_text = format_cards_for_preview(cards_final, hard=hard)
            root.after(0, lambda: finalizar_geracao(preview_text, len(cards_final), hard, do_refine))

        except Exception as e:
            msg = str(e)
            root.after(0, lambda m=msg: erro_geracao(m))

    threading.Thread(target=chamar_api, daemon=True).start()


def finalizar_geracao(preview_text: str, count: int, hard: bool, refined: bool):
    inserir_preview_formatado(preview_text)
    hard_txt = "HARD" if hard else "NORMAL"
    ref_txt = " • refinado" if refined else ""
    status_label.config(text=f"✅ {count} flashcard(s) gerado(s)! • modo {hard_txt}{ref_txt}")
    set_busy(False)


def erro_geracao(mensagem: str):
    preview.config(state="normal")
    preview.delete("1.0", tk.END)
    preview.insert(tk.END, f"❌ Erro ao gerar flashcards:\n\n{mensagem}")
    preview.config(state="disabled")
    status_label.config(text="❌ Erro na geração. Tente novamente.")
    set_busy(False)
    messagebox.showerror("Erro", mensagem)


def exportar_cards():
    """Função principal de exportação com dialog de escolha"""
    conteudo = preview.get("1.0", tk.END).strip()
    if not conteudo or conteudo.startswith("⏳") or conteudo.startswith("❌"):
        messagebox.showwarning("Aviso", "Nenhum card válido para exportar.")
        return

    cards = parse_cards(conteudo)
    if not cards:
        messagebox.showwarning("Aviso", "Não encontrei cards no formato Q/A para exportar.")
        return

    # Abre dialog de exportação
    dialog = ExportDialog(root, len(cards))
    root.wait_window(dialog)
    
    if not dialog.result:
        return  # Cancelou
    
    formato = dialog.result
    deck_name = dialog.deck_name
    
    # === ANKI .APKG ===
    if formato == "anki_apkg":
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
            deck_id = abs(hash(deck_name)) % (10 ** 10)  # ID baseado no nome

            modelo = genanki.Model(
                model_id,
                "Flashcard Gerado",
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
                    font-family: Arial, sans-serif;
                    font-size: 20px;
                    text-align: center;
                    color: #333;
                    background-color: #fff;
                    padding: 20px;
                }
                """
            )

            deck = genanki.Deck(deck_id, deck_name)

            for c in cards:
                nota = genanki.Note(
                    model=modelo,
                    fields=[c["q"], c["a"]],
                    guid=genanki.guid_for(c["q"], c["a"])
                )
                deck.add_note(nota)

            pacote = genanki.Package(deck)
            pacote.write_to_file(path)

            status_label.config(text=f"📁 Exportado: {len(cards)} cards → {os.path.basename(path)}")
            messagebox.showinfo(
                "Sucesso",
                f"✅ {len(cards)} flashcard(s) exportado(s)!\n\n"
                f"📦 Deck: {deck_name}\n"
                f"📁 Arquivo: {path}\n\n"
                "No Anki: Arquivo → Importar → selecione o .apkg"
            )

        except Exception as e:
            messagebox.showerror("Erro ao exportar .apkg", str(e))
    
    # === ANKI .TXT ===
    elif formato == "anki_txt":
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Salvar para Anki (.txt)",
            initialfile="flashcards_anki.txt"
        )
        if not path:
            return

        try:
            export_text = format_cards_for_export_tab(cards)
            with open(path, "w", encoding="utf-8") as f:
                f.write(export_text)

            status_label.config(text=f"📁 Exportado: {len(cards)} cards → {os.path.basename(path)}")
            messagebox.showinfo(
                "Sucesso",
                f"✅ {len(cards)} flashcard(s) exportado(s)!\n\n"
                f"📁 Arquivo: {path}\n\n"
                "No Anki:\n"
                "1. Arquivo → Importar\n"
                "2. Separador de campo: Tab\n"
                "3. Importar"
            )

        except Exception as e:
            messagebox.showerror("Erro ao exportar", str(e))
    
    # === NOJI .TXT ===
    elif formato == "noji_txt":
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Salvar para Noji (.txt)",
            initialfile="flashcards_noji.txt"
        )
        if not path:
            return

        try:
            export_text = format_cards_for_export_tab(cards)
            with open(path, "w", encoding="utf-8") as f:
                f.write(export_text)

            status_label.config(text=f"📁 Exportado: {len(cards)} cards → {os.path.basename(path)}")
            messagebox.showinfo(
                "Sucesso",
                f"✅ {len(cards)} flashcard(s) exportado(s)!\n\n"
                f"📁 Arquivo: {path}\n\n"
                "No Noji:\n"
                "1. Vá em Importar cartões\n"
                "2. Cole o conteúdo do arquivo OU\n"
                "   abra o arquivo e copie tudo (Ctrl+A, Ctrl+C)\n"
                "3. Entre frente/verso: Tab\n"
                "4. Entre cartões: Nova linha"
            )

        except Exception as e:
            messagebox.showerror("Erro ao exportar", str(e))


def copiar_clipboard():
    conteudo = preview.get("1.0", tk.END).strip()
    if not conteudo or conteudo.startswith("⏳"):
        messagebox.showwarning("Aviso", "Nenhum conteúdo para copiar.")
        return

    cards = parse_cards(conteudo)
    if cards:
        # Formato tabulado (compatível com Noji direto)
        texto_limpo = format_cards_for_export_tab(cards)
    else:
        texto_limpo = conteudo

    root.clipboard_clear()
    root.clipboard_append(texto_limpo)
    root.update()
    status_label.config(text="📋 Copiado! Cole no Anki ou Noji (formato Tab já pronto)")


def limpar_tudo():
    text_input.delete("1.0", tk.END)
    preview.config(state="normal")
    preview.delete("1.0", tk.END)
    preview.config(state="disabled")
    qtd_var.set("AUTO")
    hard_var.set(False)
    refine_var.set(False)
    status_label.config(text="🔄 Campos limpos. Pronto para nova geração.")
    atualizar_contador()


# =========================
# INTERFACE (UI)
# =========================
root = tk.Tk()
root.title(f"Gerador de Flashcards • Anki & Noji • {APP_VERSION}")
root.geometry("1040x760")
root.minsize(840, 640)

style = ttk.Style()
style.configure("TButton", padding=6)

# =========================
# FRAME SUPERIOR - INPUT
# =========================
frame_input = ttk.LabelFrame(root, text="📝 Texto para Análise", padding=10)
frame_input.pack(fill="x", padx=10, pady=(10, 5))

text_input = tk.Text(
    frame_input,
    height=10,
    wrap="word",
    font=("Consolas", 10),
    relief="flat",
    borderwidth=1,
    highlightthickness=1,
    highlightbackground="#ccc",
    highlightcolor="#0078d4"
)
text_input.pack(fill="x", pady=(0, 5))
text_input.bind("<KeyRelease>", atualizar_contador)

contador_label = ttk.Label(frame_input, text="0 caracteres  •  ~0 tokens", foreground="#666")
contador_label.pack(anchor="e")

# =========================
# FRAME DE CONTROLES
# =========================
frame_controles = ttk.Frame(root, padding=5)
frame_controles.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_controles, text="Quantidade:").grid(row=0, column=0, padx=(0, 5))

qtd_var = tk.StringVar(value="AUTO")
entry_qtd = ttk.Entry(frame_controles, textvariable=qtd_var, width=10, justify="center")
entry_qtd.grid(row=0, column=1, padx=(0, 6))

ttk.Label(frame_controles, text="(número ou AUTO)", foreground="#666").grid(row=0, column=2, padx=(0, 14))

hard_var = tk.BooleanVar(value=False)
chk_hard = ttk.Checkbutton(frame_controles, text="🔥 Modo HARD", variable=hard_var)
chk_hard.grid(row=0, column=3, padx=(0, 10))

refine_var = tk.BooleanVar(value=False)
chk_refine = ttk.Checkbutton(frame_controles, text="🧼 Refinar (2ª passada)", variable=refine_var)
chk_refine.grid(row=0, column=4, padx=(0, 10))

btn_gerar = ttk.Button(frame_controles, text="🚀 Gerar Cards", command=gerar_cards, width=15)
btn_gerar.grid(row=0, column=5, padx=5)

btn_exportar = ttk.Button(frame_controles, text="💾 Exportar", command=exportar_cards, width=12)
btn_exportar.grid(row=0, column=6, padx=5)

btn_copiar = ttk.Button(frame_controles, text="📋 Copiar", command=copiar_clipboard, width=12)
btn_copiar.grid(row=0, column=7, padx=5)

btn_limpar = ttk.Button(frame_controles, text="🔄 Limpar", command=limpar_tudo, width=12)
btn_limpar.grid(row=0, column=8, padx=5)

# =========================
# FRAME INFERIOR - PREVIEW
# =========================
frame_preview = ttk.LabelFrame(root, text="🎴 Flashcards Gerados (com Score)", padding=10)
frame_preview.pack(fill="both", expand=True, padx=10, pady=(5, 10))

frame_texto = ttk.Frame(frame_preview)
frame_texto.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_texto)
scrollbar.pack(side="right", fill="y")

preview = tk.Text(
    frame_texto,
    height=20,
    wrap="word",
    font=("Consolas", 10),
    relief="flat",
    borderwidth=1,
    highlightthickness=1,
    highlightbackground="#ccc",
    highlightcolor="#0078d4",
    yscrollcommand=scrollbar.set,
    state="disabled"
)
preview.pack(fill="both", expand=True, side="left")
scrollbar.config(command=preview.yview)

preview.tag_configure("header", foreground="#444", font=("Consolas", 10, "bold"))
preview.tag_configure("score", foreground="#8a2be2", font=("Consolas", 10, "bold"))
preview.tag_configure("pergunta", foreground="#0066cc", font=("Consolas", 10, "bold"))
preview.tag_configure("resposta", foreground="#228b22", font=("Consolas", 10))

# =========================
# BARRA DE STATUS
# =========================
frame_status = ttk.Frame(root)
frame_status.pack(fill="x", padx=10, pady=(0, 10))

status_label = ttk.Label(
    frame_status,
    text="✨ Pronto. Cole um texto e clique em 'Gerar Cards'.",
    foreground="#666"
)
status_label.pack(side="left")

versao_label = ttk.Label(frame_status, text=f"{APP_VERSION} • {MODEL_NAME}", foreground="#999")
versao_label.pack(side="right")

# =========================
# INICIAR
# =========================
root.mainloop()
