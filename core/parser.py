# -*- coding: utf-8 -*-
"""
Parsing e Formatação de Flashcards
==================================

Funções para extração, formatação e manipulação de flashcards.
"""

import re
import csv
from io import StringIO
from typing import List, Dict, Optional
import zipfile
import sqlite3
import tempfile
import os

def parse_apkg_cards_detailed(file_path: str) -> tuple[List[Dict[str, str]], Dict]:
    """
    Extrai flashcards e metadados de um arquivo .apkg.
    
    Returns:
        Tuple com (lista de cards, dicionário de metadados).
    """
    cards = []
    metadata = {
        "deck_name": "Desconhecido",
        "note_types": set(),
        "total_notes": 0,
        "tags": set()
    }
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            db_path = None
            for db_name in ['collection.anki2', 'collection.anki21']:
                potential = os.path.join(temp_dir, db_name)
                if os.path.exists(potential):
                    db_path = potential
                    break
            
            if not db_path:
                return [], metadata
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Extrai nome do deck da tabela col
                cursor.execute("SELECT decks FROM col")
                decks_json = cursor.fetchone()
                if decks_json:
                    import json
                    decks = json.loads(decks_json[0])
                    # Pega o primeiro deck que não é "Default"
                    for deck_id, deck_info in decks.items():
                        name = deck_info.get('name', '')
                        if name and name != 'Default':
                            metadata["deck_name"] = name
                            break
                
                # Extrai tipos de nota
                cursor.execute("SELECT models FROM col")
                models_json = cursor.fetchone()
                if models_json:
                    import json
                    models = json.loads(models_json[0])
                    for model_id, model_info in models.items():
                        metadata["note_types"].add(model_info.get('name', 'Unknown'))
                
                # Extrai notas com tags
                cursor.execute("SELECT flds, tags FROM notes")
                rows = cursor.fetchall()
                metadata["total_notes"] = len(rows)
                
                for flds, tags in rows:
                    fields = flds.split('\x1f')
                    
                    # Coleta tags
                    if tags:
                        for tag in tags.strip().split():
                            metadata["tags"].add(tag)
                    
                    if len(fields) >= 2:
                        q = _clean_html(fields[0].strip())
                        a = _clean_html(fields[1].strip())
                        
                        if q and a:
                            cards.append({"q": q, "a": a})
                
            finally:
                conn.close()
        
        # Converte sets para listas para serialização
        metadata["note_types"] = list(metadata["note_types"])
        metadata["tags"] = list(metadata["tags"])
        
        return cards, metadata
        
    except Exception as e:
        print(f"[parse_apkg_cards_detailed] Erro: {e}")
        return [], metadata


def parse_apkg_cards(file_path: str) -> List[Dict[str, str]]:
    """
    Extrai flashcards de um arquivo .apkg do Anki.
    
    O formato .apkg é um ZIP contendo um banco SQLite com as notas.
    Os campos estão na tabela 'notes', coluna 'flds', separados por \\x1f.
    
    Args:
        file_path: Caminho do arquivo .apkg.
    
    Returns:
        Lista de dicionários com chaves 'q' e 'a'.
    """
    cards = []
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # .apkg é um arquivo ZIP
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Localiza o banco SQLite (pode ser .anki2 ou .anki21)
            db_path = None
            for db_name in ['collection.anki2', 'collection.anki21']:
                potential = os.path.join(temp_dir, db_name)
                if os.path.exists(potential):
                    db_path = potential
                    break
            
            if not db_path:
                print("[parse_apkg_cards] Banco SQLite não encontrado no .apkg")
                return []
            
            # Conecta e extrai notas
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Extrai campos das notas
                # flds contém todos os campos separados por \x1f (unit separator)
                cursor.execute("SELECT flds FROM notes")
                rows = cursor.fetchall()
                
                for row in rows:
                    fields = row[0].split('\x1f')
                    
                    if len(fields) >= 2:
                        q = _clean_html(fields[0].strip())
                        a = _clean_html(fields[1].strip())
                        
                        if q and a:
                            cards.append({"q": q, "a": a})
                
            finally:
                conn.close()
        
        return cards
        
    except zipfile.BadZipFile:
        print("[parse_apkg_cards] Arquivo não é um ZIP válido")
        return []
    except sqlite3.Error as e:
        print(f"[parse_apkg_cards] Erro SQLite: {e}")
        return []
    except Exception as e:
        print(f"[parse_apkg_cards] Erro: {type(e).__name__}: {e}")
        return []


def _clean_html(text: str) -> str:
    """
    Remove tags HTML e limpa o texto extraído do Anki.
    
    Args:
        text: Texto com possíveis tags HTML.
    
    Returns:
        Texto limpo.
    """
    if not text:
        return ""
    
    # Remove tags HTML
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decodifica entidades HTML comuns
    html_entities = {
        '&nbsp;': ' ',
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    # Remove espaços extras mantendo quebras de linha
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    return text.strip()


def parse_flashcard_file(file_path: str) -> List[Dict[str, str]]:
    """
    Função unificada para carregar flashcards de qualquer formato suportado.
    
    Detecta automaticamente o formato pelo extensão e conteúdo.
    
    Args:
        file_path: Caminho do arquivo (.apkg, .csv, .txt).
    
    Returns:
        Lista de dicionários com chaves 'q' e 'a'.
    
    Raises:
        ValueError: Se o formato não for suportado.
        FileNotFoundError: Se o arquivo não existir.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.apkg':
        return parse_apkg_cards(file_path)
    elif ext in ['.csv', '.txt', '.tsv']:
        return parse_csv_cards(file_path=file_path)
    else:
        # Tenta detectar pelo conteúdo
        try:
            # Verifica se é um ZIP (possível .apkg renomeado)
            with zipfile.ZipFile(file_path, 'r') as zf:
                names = zf.namelist()
                if any('anki' in n.lower() for n in names):
                    return parse_apkg_cards(file_path)
        except zipfile.BadZipFile:
            pass
        
        # Tenta como texto
        return parse_csv_cards(file_path=file_path)


def parse_cards(raw: str) -> List[Dict[str, str]]:
    """
    Extrai flashcards do formato Q:/A: com suporte a respostas multilinhas.
    
    Args:
        raw: Texto bruto contendo os flashcards.
    
    Returns:
        Lista de dicionários com chaves 'q' e 'a'.
    """
    if not raw:
        return []
    
    try:
        raw = raw.replace("\r\n", "\n").strip()
        
        # Remove markdown e formatação indesejada
        raw = re.sub(r"```[\w]*\n?", "", raw)
        raw = raw.replace("**", "")
        raw = re.sub(r"^\d+[\.\)]\s*(Q:)", r"\1", raw, flags=re.MULTILINE)
        
        # Filtra linhas de introdução/conclusão
        lines_clean = []
        skip_patterns = [
            "[score:", "#", "---", "***", "===",
            "aqui estão", "aqui estao", "seguem",
            "abaixo", "espero que"
        ]
        
        for ln in raw.split("\n"):
            s = ln.strip().lower()
            if any(s.startswith(p) for p in skip_patterns):
                continue
            lines_clean.append(ln)
        
        raw = "\n".join(lines_clean)
        
        # Localiza todas as perguntas
        q_pattern = re.compile(r"^(Q|P|Pergunta)\s*:", re.IGNORECASE | re.MULTILINE)
        matches = list(q_pattern.finditer(raw))
        
        if not matches:
            return []
        
        cards = []
        
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            block = raw[start:end].strip()
            
            q_lines, a_lines = [], []
            cur = None
            
            for ln in block.split("\n"):
                ln_original = ln
                ln_stripped = ln.strip()
                
                is_indented = ln.startswith("    ") or ln.startswith("\t")
                
                # Detecta início de pergunta
                q_match = re.match(r"^(Q|P|Pergunta)\s*:\s*(.*)$", ln_stripped, re.IGNORECASE)
                a_match = re.match(r"^(A|R|Resposta)\s*:\s*(.*)$", ln_stripped, re.IGNORECASE)
                
                # Código indentado pertence à resposta
                if cur == "A" and is_indented:
                    a_lines.append(ln_original.rstrip())
                    continue
                
                # Linhas que parecem código
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
            
            # Remove linhas vazias no início e fim da resposta
            while a_lines and not a_lines[0].strip():
                a_lines.pop(0)
            while a_lines and not a_lines[-1].strip():
                a_lines.pop()
            
            # Monta o card
            q = re.sub(r"\s+", " ", " ".join(q_lines).strip())
            a = "\n".join(a_lines).strip()
            
            if q and a:
                cards.append({"q": q, "a": a})
        
        return cards
        
    except Exception as e:
        print(f"[parse_cards] Erro: {type(e).__name__}: {e}")
        return []


def parse_csv_cards(
    file_path: Optional[str] = None,
    csv_content: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Lê flashcards de arquivo CSV ou string.
    
    Suporta delimitadores: vírgula, ponto-e-vírgula e tab.
    
    Args:
        file_path: Caminho do arquivo CSV.
        csv_content: Conteúdo CSV como string.
    
    Returns:
        Lista de dicionários com chaves 'q' e 'a'.
    """
    cards = []
    
    try:
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = csv_content or ""
        
        if not content.strip():
            return []
        
        # Detecta o delimitador
        sample = "\n".join(content.splitlines()[:5]) or content
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t'])
            delimiter = dialect.delimiter
        except Exception:
            # Fallback manual: conta delimitadores fora de aspas
            counts = {',': 0, ';': 0, '\t': 0}
            in_quotes = False
            for ch in sample:
                if ch == '"':
                    in_quotes = not in_quotes
                elif not in_quotes and ch in counts:
                    counts[ch] += 1
            if counts['\t'] > 0:
                delimiter = '\t'
            else:
                delimiter = ',' if counts[','] >= counts[';'] else ';'
        
        reader = csv.reader(StringIO(content), delimiter=delimiter)
        
        # Headers comuns a ignorar
        skip_headers = {'front', 'frente', 'pergunta', 'question', 'q'}
        
        for row in reader:
            if len(row) >= 2:
                q = row[0].strip()
                a = row[1].strip()
                
                if q.lower() in skip_headers:
                    continue
                
                if q and a:
                    # Converte <br> de volta para quebras de linha
                    q = q.replace('<br>', '\n')
                    a = a.replace('<br>', '\n')
                    cards.append({"q": q, "a": a})
        
        return cards
        
    except Exception as e:
        print(f"[parse_csv_cards] Erro: {type(e).__name__}: {e}")
        return []


def format_cards_for_export_tab(cards: List[Dict[str, str]]) -> str:
    """
    Formata cards para exportação em formato tabulado (Anki/Noji).
    
    Args:
        cards: Lista de cards.
    
    Returns:
        String com cards separados por tab e quebras de linha como <br>.
    """
    lines = []
    for c in cards:
        q = c['q'].replace('\\n', '\n').replace('\n', '<br>')
        a = c['a'].replace('\\n', '\n').replace('\n', '<br>')
        lines.append(f"{q}\t{a}")
    
    return "\n".join(lines) + ("\n" if cards else "")


def format_cards_for_prompt(cards: List[Dict[str, str]]) -> str:
    """
    Formata cards para envio em prompts de revisão.
    
    Args:
        cards: Lista de cards.
    
    Returns:
        String formatada com numeração.
    """
    lines = []
    for i, c in enumerate(cards, 1):
        lines.append(f"[Card {i}]")
        lines.append(f"Q: {c['q']}")
        lines.append(f"A: {c['a']}")
        lines.append("")
    
    return "\n".join(lines).strip()


def format_cards_for_refine(cards: List[Dict[str, str]]) -> str:
    """
    Formata cards para envio ao prompt de refinamento.
    
    Args:
        cards: Lista de cards.
    
    Returns:
        String no formato Q:/A: simples.
    """
    lines = []
    for c in cards:
        lines.extend([f"Q: {c['q']}", f"A: {c['a']}", ""])
    
    return "\n".join(lines).strip()


def extract_new_cards_from_audit(response: str) -> List[Dict[str, str]]:
    """
    Extrai novos cards sugeridos da resposta de auditoria.
    
    Args:
        response: Resposta completa da IA.
    
    Returns:
        Lista de novos cards sugeridos.
    """
    markers = [
        "=== NOVOS CARDS SUGERIDOS ===",
        "NOVOS CARDS SUGERIDOS",
        "=== CARDS SUGERIDOS ==="
    ]
    
    start_idx = -1
    for marker in markers:
        if marker in response:
            start_idx = response.find(marker) + len(marker)
            break
    
    if start_idx == -1:
        start_idx = 0
    
    cards_section = response[start_idx:]
    return parse_cards(cards_section)


def extract_cards_from_review(response: str) -> List[Dict[str, str]]:
    """
    Extrai cards finais da resposta de revisão completa.
    
    Args:
        response: Resposta completa da IA.
    
    Returns:
        Lista de cards finais revisados.
    """
    markers = [
        "=== CARDS FINAIS ===",
        "CARDS FINAIS",
        "=== DECK REVISADO ==="
    ]
    
    start_idx = -1
    for marker in markers:
        if marker in response:
            start_idx = response.find(marker) + len(marker)
            break
    
    if start_idx == -1:
        return []
    
    cards_section = response[start_idx:]
    return parse_cards(cards_section)


def extract_report_from_review(response: str) -> str:
    """
    Extrai o relatório de alterações da resposta de revisão.
    
    Args:
        response: Resposta completa da IA.
    
    Returns:
        Texto do relatório de alterações.
    """
    start_markers = [
        "=== RELATÓRIO DE ALTERAÇÕES ===",
        "RELATÓRIO DE ALTERAÇÕES"
    ]
    end_markers = [
        "=== CARDS FINAIS ===",
        "CARDS FINAIS"
    ]
    
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
    
    return response[start_idx:end_idx].strip()
