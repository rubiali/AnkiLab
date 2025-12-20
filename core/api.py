# -*- coding: utf-8 -*-
"""
Integração com API OpenAI
=========================

Funções para comunicação com a API de IA para geração e revisão de flashcards.

COMPATIBILIDADE:
- GPT-5 Family: usa Responses API (client.responses.create)
- GPT-4 Family: usa Chat Completions API (client.chat.completions.create)
"""

from string import Template
from typing import List, Dict, Optional, Any

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
    is_gpt5_model,
    # Parâmetros GPT-4
    GENERATION_TEMPERATURE,
    REFINEMENT_TEMPERATURE,
    REVIEW_TEMPERATURE,
    MAX_TOKENS_GENERATION,
    MAX_TOKENS_REVIEW,
    # Parâmetros GPT-5
    REASONING_EFFORT_GENERATION,
    REASONING_EFFORT_REFINEMENT,
    REASONING_EFFORT_REVIEW,
    VERBOSITY_GENERATION,
    VERBOSITY_REFINEMENT,
    VERBOSITY_REVIEW,
    MAX_OUTPUT_TOKENS_GENERATION,
    MAX_OUTPUT_TOKENS_REFINEMENT,
    MAX_OUTPUT_TOKENS_REVIEW,
)
from .parser import parse_cards, format_cards_for_refine


def _call_gpt5_responses_api(
    client,
    model: str,
    instructions: str,
    user_input: str,
    reasoning_effort: str = "low",
    verbosity: str = "medium",
    max_output_tokens: int = 15000,
) -> str:
    """
    Chama GPT-5 usando a Responses API.
    
    Args:
        client: Cliente OpenAI.
        model: Nome do modelo GPT-5.
        instructions: Instruções do sistema.
        user_input: Input do usuário.
        reasoning_effort: Nível de raciocínio ("none", "low", "medium", "high").
        verbosity: Nível de verbosidade ("low", "medium", "high").
        max_output_tokens: Máximo de tokens na resposta.
    
    Returns:
        Texto da resposta.
    """
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
        reasoning={"effort": reasoning_effort},
        text={"verbosity": verbosity},
        max_output_tokens=max_output_tokens,
    )
    
    return response.output_text or ""


def _call_gpt4_chat_completions_api(
    client,
    model: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 15000,
) -> str:
    """
    Chama GPT-4 usando a Chat Completions API.
    
    Args:
        client: Cliente OpenAI.
        model: Nome do modelo GPT-4.
        system_prompt: Prompt do sistema.
        user_message: Mensagem do usuário.
        temperature: Temperatura de sampling.
        max_tokens: Máximo de tokens na resposta.
    
    Returns:
        Texto da resposta.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return (response.choices[0].message.content or "").strip()


def _call_openai(
    model: str,
    system_prompt: str,
    user_message: str,
    # Parâmetros GPT-4
    temperature: float = 0.3,
    max_tokens: int = 15000,
    # Parâmetros GPT-5
    reasoning_effort: str = "low",
    verbosity: str = "medium",
    max_output_tokens: int = 15000,
) -> str:
    """
    Função unificada que roteia para a API correta baseado no modelo.
    
    Args:
        model: Nome do modelo.
        system_prompt: Prompt do sistema (instructions para GPT-5).
        user_message: Mensagem do usuário (input para GPT-5).
        temperature: Temperatura (GPT-4 only).
        max_tokens: Máximo de tokens (GPT-4 only).
        reasoning_effort: Esforço de raciocínio (GPT-5 only).
        verbosity: Verbosidade (GPT-5 only).
        max_output_tokens: Máximo de tokens de saída (GPT-5 only).
    
    Returns:
        Texto da resposta.
    """
    client = get_openai_client()
    
    if is_gpt5_model(model):
        return _call_gpt5_responses_api(
            client=client,
            model=model,
            instructions=system_prompt,
            user_input=user_message,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            max_output_tokens=max_output_tokens,
        )
    else:
        return _call_gpt4_chat_completions_api(
            client=client,
            model=model,
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )


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
    # Determina o modo de geração
    modo = "AUTOMÁTICO" if quantidade.upper() == "AUTO" else "MANUAL"
    
    # Seleciona o prompt apropriado
    base_prompt = PROMPT_HARD if hard_mode else PROMPT_NORMAL
    prompt = Template(base_prompt).safe_substitute(
        MODO=modo,
        QTD=quantidade,
        TEXTO=texto
    )
    
    # Chamada à API (roteamento automático)
    raw_content = _call_openai(
        model=MODEL_NAME,
        system_prompt=prompt,
        user_message=texto,
        # Parâmetros GPT-4
        temperature=GENERATION_TEMPERATURE,
        max_tokens=MAX_TOKENS_GENERATION,
        # Parâmetros GPT-5
        reasoning_effort=REASONING_EFFORT_GENERATION,
        verbosity=VERBOSITY_GENERATION,
        max_output_tokens=MAX_OUTPUT_TOKENS_GENERATION,
    )
    
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
    
    # Formata os cards para o prompt
    cards_text = format_cards_for_refine(cards)
    dificuldade = "HARD" if hard_mode else "NORMAL"
    
    prompt = Template(REFINE_PROMPT).safe_substitute(
        DIFICULDADE=dificuldade,
        TEXTO=texto_original,
        CARDS=cards_text
    )
    
    # Chamada à API (roteamento automático)
    raw_content = _call_openai(
        model=MODEL_REFINEMENT,
        system_prompt=prompt,
        user_message=cards_text,
        # Parâmetros GPT-4
        temperature=REFINEMENT_TEMPERATURE,
        max_tokens=MAX_TOKENS_GENERATION,
        # Parâmetros GPT-5
        reasoning_effort=REASONING_EFFORT_REFINEMENT,
        verbosity=VERBOSITY_REFINEMENT,
        max_output_tokens=MAX_OUTPUT_TOKENS_REFINEMENT,
    )
    
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
    # Seleciona o prompt apropriado
    if mode == "audit":
        prompt_template = PROMPT_AUDIT
    else:
        prompt_template = PROMPT_FINAL_REVIEW
    
    prompt = Template(prompt_template).safe_substitute(
        ASSUNTO=assunto,
        CARDS=cards_text
    )
    
    # Chamada à API (roteamento automático)
    return _call_openai(
        model=MODEL_ADVANCED,
        system_prompt=prompt,
        user_message=cards_text,
        # Parâmetros GPT-4
        temperature=REVIEW_TEMPERATURE,
        max_tokens=MAX_TOKENS_REVIEW,
        # Parâmetros GPT-5
        reasoning_effort=REASONING_EFFORT_REVIEW,
        verbosity=VERBOSITY_REVIEW,
        max_output_tokens=MAX_OUTPUT_TOKENS_REVIEW,
    )
