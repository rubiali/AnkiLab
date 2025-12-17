# -*- coding: utf-8 -*-
"""
Módulo de Configuração
======================

Contém configurações globais e prompts do sistema.
"""

from .settings import (
    APP_NAME,
    APP_VERSION,
    APP_TAGLINE,
    MODEL_NAME,
    MODEL_REFINEMENT,
    MODEL_ADVANCED,
    get_openai_client,
)

from .prompts import (
    PROMPT_NORMAL,
    PROMPT_HARD,
    REFINE_PROMPT,
    PROMPT_AUDIT,
    PROMPT_FINAL_REVIEW,
)

__all__ = [
    "APP_NAME",
    "APP_VERSION", 
    "APP_TAGLINE",
    "MODEL_NAME",
    "MODEL_REFINEMENT",
    "MODEL_ADVANCED",
    "get_openai_client",
    "PROMPT_NORMAL",
    "PROMPT_HARD",
    "REFINE_PROMPT",
    "PROMPT_AUDIT",
    "PROMPT_FINAL_REVIEW",
]