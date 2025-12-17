# -*- coding: utf-8 -*-
"""
Configurações Globais
=====================

Define constantes, parâmetros e configurações da aplicação.
"""

import os
from openai import OpenAI


# ==============================================================================
# METADADOS DA APLICAÇÃO
# ==============================================================================

APP_NAME = "AnkiLab"
APP_VERSION = "v3.0"
APP_TAGLINE = "Cognitive Flashcard Engine"


# ==============================================================================
# CONFIGURAÇÃO DE MODELOS
# ==============================================================================

MODEL_NAME = "gpt-4.1-mini"          # Modelo principal para geração
MODEL_REFINEMENT = "gpt-4o-mini"     # Modelo para refinamento
MODEL_ADVANCED = "gpt-4o"            # Modelo para revisão avançada


# ==============================================================================
# PARÂMETROS DE GERAÇÃO
# ==============================================================================

GENERATION_TEMPERATURE = 0.45
REFINEMENT_TEMPERATURE = 0.3
REVIEW_TEMPERATURE = 0.3
MAX_TOKENS_GENERATION = 15000
MAX_TOKENS_REVIEW = 16000


# ==============================================================================
# CLIENTE OPENAI (Singleton)
# ==============================================================================

_openai_client = None


def get_openai_client() -> OpenAI:
    """
    Retorna uma instância singleton do cliente OpenAI.
    
    Returns:
        OpenAI: Cliente configurado com a API key do ambiente.
    
    Raises:
        ValueError: Se a API key não estiver configurada.
    """
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada.")
        _openai_client = OpenAI(api_key=api_key)
    
    return _openai_client
