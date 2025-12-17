# -*- coding: utf-8 -*-
"""
Funções de Exportação
=====================

Exportação de flashcards para diferentes formatos.
"""

from typing import List, Dict
import genanki

from core.parser import format_cards_for_export_tab


# ==============================================================================
# MODELO ANKI PADRÃO
# ==============================================================================

ANKI_MODEL = genanki.Model(
    1607392319,
    "AnkiLab Card",
    fields=[
        {"name": "Frente"},
        {"name": "Verso"}
    ],
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


def export_apkg(path: str, deck_name: str, cards: List[Dict[str, str]]) -> None:
    """
    Exporta flashcards para formato .apkg (Anki).
    
    Args:
        path: Caminho do arquivo de saída.
        deck_name: Nome do deck.
        cards: Lista de cards com chaves 'q' e 'a'.
    
    Raises:
        Exception: Se houver erro na exportação.
    """
    # Cria o deck com ID único baseado no nome
    deck_id = abs(hash(deck_name)) % (10 ** 10)
    deck = genanki.Deck(deck_id, deck_name)
    
    for card in cards:
        # Normaliza quebras de linha
        question = card["q"].replace('\\n', '\n')
        answer = card["a"].replace('\\n', '\n')
        
        # Detecta se a resposta contém código
        code_indicators = ['def ', 'function ', '{', '=>', 'import ', 'const ', 'let ', 'var ']
        is_code = '\n' in answer or any(ind in answer for ind in code_indicators)
        
        if is_code:
            answer = f"<pre><code>{answer}</code></pre>"
        
        # Cria a nota
        note = genanki.Note(
            model=ANKI_MODEL,
            fields=[question, answer],
            guid=genanki.guid_for(card["q"], card["a"])
        )
        deck.add_note(note)
    
    # Salva o pacote
    genanki.Package(deck).write_to_file(path)


def export_txt(path: str, cards: List[Dict[str, str]]) -> None:
    """
    Exporta flashcards para formato .txt (tabulado).
    
    Compatível com importação no Anki e Noji.
    
    Args:
        path: Caminho do arquivo de saída.
        cards: Lista de cards com chaves 'q' e 'a'.
    
    Raises:
        Exception: Se houver erro na escrita do arquivo.
    """
    content = format_cards_for_export_tab(cards)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
