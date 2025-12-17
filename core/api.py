# -*- coding: utf-8 -*-
"""
Integração com API OpenAI
=========================

Funções para comunicação com a API de IA para geração e revisão de flashcards.
"""

from string import Template
from typing import List, Dict, Optional

from config import (
    get_openai_client,
    MODEL_NAME,
    MODEL_REFINEMENT,
    MODEL_ADVANCED,
    PROMPT_NORMAL,
    PROMPT_HARD,
    REFINE_PROMPT,
    PROMPT_AUDIT,
    PROMPT_FINAL_REVIEW,
)
from config.settings import (
    GENERATION_TEMPERATURE,
    REFINEMENT_TEMPERATURE,
    REVIEW_TEMPERATURE,
    MAX_TOKENS_GENERATION,
    MAX_TOKENS_REVIEW,
)
from .parser import parse_cards, format_cards_for_refine


def generate_cards(
    texto: str,
    quantidade: str,
    hard_mode: bool = False
) -> List[Dict[str, str]]:
    """
    Gera flashcards a partir de um texto usando IA.
    
    Args:
        texto: Conteúdo para análise.
        quantidade: Número de cards ou "AUTO".
        hard_mode: Se True, usa prompt focado em aplicação.
    
    Returns:
        Lista de dicionários com chaves 'q' (pergunta) e 'a' (resposta).
    
    Raises:
        RuntimeError: Se não conseguir extrair cards da resposta.
    """
    client = get_openai_client()
    
    # Determina o modo de geração
    modo = "AUTOMÁTICO" if quantidade.upper() == "AUTO" else "MANUAL"
    
    # Seleciona o prompt apropriado
    base_prompt = PROMPT_HARD if hard_mode else PROMPT_NORMAL
    prompt = Template(base_prompt).safe_substitute(
        MODO=modo,
        QTD=quantidade,
        TEXTO=texto
    )
    
    # Chamada à API
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=GENERATION_TEMPERATURE,
        max_tokens=MAX_TOKENS_GENERATION
    )
    
    raw_content = (response.choices[0].message.content or "").strip()
    cards = parse_cards(raw_content)
    
    if not cards:
        raise RuntimeError("Não foi possível extrair cards. Tente reformular o texto.")
    
    return cards


def refine_cards(
    texto_original: str,
    cards: List[Dict[str, str]],
    hard_mode: bool = False
) -> List[Dict[str, str]]:
    """
    Refina uma lista de flashcards existentes.
    
    Args:
        texto_original: Texto fonte original.
        cards: Lista de cards para refinar.
        hard_mode: Se True, aplica refinamento mais rigoroso.
    
    Returns:
        Lista de cards refinados.
    """
    if not cards:
        return cards
    
    client = get_openai_client()
    
    # Formata os cards para o prompt
    cards_text = format_cards_for_refine(cards)
    dificuldade = "HARD" if hard_mode else "NORMAL"
    
    prompt = Template(REFINE_PROMPT).safe_substitute(
        DIFICULDADE=dificuldade,
        TEXTO=texto_original,
        CARDS=cards_text
    )
    
    response = client.chat.completions.create(
        model=MODEL_REFINEMENT,
        messages=[{"role": "user", "content": prompt}],
        temperature=REFINEMENT_TEMPERATURE,
        max_tokens=MAX_TOKENS_GENERATION
    )
    
    raw_content = (response.choices[0].message.content or "").strip()
    refined = parse_cards(raw_content)
    
    # Retorna refinados apenas se manteve pelo menos 50% dos cards
    min_cards = max(1, int(len(cards) * 0.5))
    if len(refined) >= min_cards:
        return refined
    
    return cards


def review_deck(
    assunto: str,
    cards_text: str,
    mode: str = "audit"
) -> str:
    """
    Executa revisão de um deck existente.
    
    Args:
        assunto: Tema/assunto do deck.
        cards_text: Cards formatados como texto.
        mode: "audit" para auditoria ou "final" para revisão completa.
    
    Returns:
        Resposta completa da IA (não parseada).
    """
    client = get_openai_client()
    
    # Seleciona o prompt apropriado
    if mode == "audit":
        prompt_template = PROMPT_AUDIT
    else:
        prompt_template = PROMPT_FINAL_REVIEW
    
    prompt = Template(prompt_template).safe_substitute(
        ASSUNTO=assunto,
        CARDS=cards_text
    )
    
    response = client.chat.completions.create(
        model=MODEL_ADVANCED,
        messages=[{"role": "user", "content": prompt}],
        temperature=REVIEW_TEMPERATURE,
        max_tokens=MAX_TOKENS_REVIEW
    )
    
    return (response.choices[0].message.content or "").strip()
