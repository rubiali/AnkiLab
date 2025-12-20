# -*- coding: utf-8 -*-
"""
Configurações Globais
=====================

Define constantes, parâmetros e configurações da aplicação.

MODELOS DISPONÍVEIS (Dezembro 2025):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPT-5 Family (usam Responses API):
  • gpt-5.2          → Flagship, melhor em tudo
  • gpt-5.1          → Excelente equilíbrio inteligência/velocidade
  • gpt-5            → Modelo base da família GPT-5
  • gpt-5-mini       → Custo/velocidade equilibrados
  • gpt-5-nano       → Mais barato/leve para tarefas simples

GPT-4 Family (usam Chat Completions API):
  • gpt-4.1          → Última versão estável do GPT-4
  • gpt-4.1-mini     → Versão leve do GPT-4.1
  • gpt-4o           → GPT-4 Omni
  • gpt-4o-mini      → GPT-4 Omni Mini

REASONING EFFORT (GPT-5):
  • "minimal" → Mínimo raciocínio (mais rápido, tarefas simples)
  • "low"     → Baixo raciocínio
  • "medium"  → Médio raciocínio
  • "high"    → Alto raciocínio
  • "xhigh"   → Extra alto (apenas gpt-5.2)
"""

import os
from openai import OpenAI


# ==============================================================================
# METADADOS DA APLICAÇÃO
# ==============================================================================

APP_NAME = "AnkiLab"
APP_VERSION = "v3.1"
APP_TAGLINE = "Cognitive Flashcard Engine"


# ==============================================================================
# CONFIGURAÇÃO DE MODELOS
# ==============================================================================

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ CONFIGURAÇÃO ATIVA - GPT-5 Family                                           │
# └─────────────────────────────────────────────────────────────────────────────┘

#MODEL_NAME = "gpt-5-mini"            # Geração principal (bom custo-benefício)
#MODEL_REFINEMENT = "gpt-5-nano"      # Refinamento (rápido e barato)
#MODEL_ADVANCED = "gpt-5.1"           # Revisão avançada (alta qualidade)

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ ALTERNATIVAS GPT-5 (descomente conforme necessidade)                        │
# └─────────────────────────────────────────────────────────────────────────────┘

# Configuração PREMIUM (máxima qualidade, maior custo):
# MODEL_NAME = "gpt-5.1"
# MODEL_REFINEMENT = "gpt-5-mini"
# MODEL_ADVANCED = "gpt-5.2"

# Configuração ECONÔMICA (menor custo):
# MODEL_NAME = "gpt-5-nano"
# MODEL_REFINEMENT = "gpt-5-nano"
# MODEL_ADVANCED = "gpt-5-mini"

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ CONFIGURAÇÃO LEGACY - GPT-4 Family (descomente para usar)                   │
# └─────────────────────────────────────────────────────────────────────────────┘

MODEL_NAME = "gpt-4.1-mini"
MODEL_REFINEMENT = "gpt-4o-mini"
MODEL_ADVANCED = "gpt-4o"


# ==============================================================================
# PARÂMETROS DE GERAÇÃO - GPT-4 (Chat Completions API)
# ==============================================================================

GENERATION_TEMPERATURE = 0.45
REFINEMENT_TEMPERATURE = 0.3
REVIEW_TEMPERATURE = 0.3
MAX_TOKENS_GENERATION = 15000
MAX_TOKENS_REVIEW = 16000


# ==============================================================================
# PARÂMETROS DE GERAÇÃO - GPT-5 (Responses API)
# ==============================================================================
# reasoning_effort: "minimal" | "low" | "medium" | "high" | "xhigh" (5.2 only)
# verbosity: "low" | "medium" | "high"

# Geração principal
REASONING_EFFORT_GENERATION = "medium"
VERBOSITY_GENERATION = "medium"
MAX_OUTPUT_TOKENS_GENERATION = 15000

# Refinamento (tarefas mais simples, usa minimal)
REASONING_EFFORT_REFINEMENT = "minimal"
VERBOSITY_REFINEMENT = "low"
MAX_OUTPUT_TOKENS_REFINEMENT = 15000

# Revisão avançada (tarefas complexas, usa medium)
REASONING_EFFORT_REVIEW = "medium"
VERBOSITY_REVIEW = "medium"
MAX_OUTPUT_TOKENS_REVIEW = 16000


# ==============================================================================
# MAPEAMENTO DE CAPACIDADES DOS MODELOS
# ==============================================================================

MODEL_CONFIG = {
    # GPT-5 Family - usam Responses API
    "gpt-5.2": {
        "is_gpt5": True,
        "reasoning_effort": ["minimal", "low", "medium", "high", "xhigh"],
        "max_context": 400000,
        "max_output": 128000,
    },
    "gpt-5.1": {
        "is_gpt5": True,
        "reasoning_effort": ["minimal", "low", "medium", "high"],
        "max_context": 200000,
        "max_output": 100000,
    },
    "gpt-5": {
        "is_gpt5": True,
        "reasoning_effort": ["minimal", "low", "medium", "high"],
        "max_context": 200000,
        "max_output": 100000,
    },
    "gpt-5-mini": {
        "is_gpt5": True,
        "reasoning_effort": ["minimal", "low", "medium", "high"],
        "max_context": 200000,
        "max_output": 100000,
    },
    "gpt-5-nano": {
        "is_gpt5": True,
        "reasoning_effort": ["minimal", "low", "medium", "high"],
        "max_context": 128000,
        "max_output": 16000,
    },
    # GPT-4 Family - usam Chat Completions API
    "gpt-4.1": {
        "is_gpt5": False,
        "reasoning_effort": None,
        "max_context": 128000,
        "max_output": 16000,
    },
    "gpt-4.1-mini": {
        "is_gpt5": False,
        "reasoning_effort": None,
        "max_context": 128000,
        "max_output": 16000,
    },
    "gpt-4o": {
        "is_gpt5": False,
        "reasoning_effort": None,
        "max_context": 128000,
        "max_output": 16000,
    },
    "gpt-4o-mini": {
        "is_gpt5": False,
        "reasoning_effort": None,
        "max_context": 128000,
        "max_output": 16000,
    },
}


def is_gpt5_model(model_name: str) -> bool:
    """
    Verifica se um modelo é da família GPT-5 (usa Responses API).
    
    Args:
        model_name: Nome do modelo.
    
    Returns:
        True se for GPT-5, False caso contrário.
    """
    # Verifica no config primeiro
    if model_name in MODEL_CONFIG:
        return MODEL_CONFIG[model_name]["is_gpt5"]
    
    # Fallback: detecta pelo nome
    return model_name.startswith("gpt-5")


def get_model_config(model_name: str) -> dict:
    """
    Retorna a configuração de um modelo.
    
    Args:
        model_name: Nome do modelo.
    
    Returns:
        Dicionário com configuração ou defaults.
    """
    # Tenta match exato primeiro
    if model_name in MODEL_CONFIG:
        return MODEL_CONFIG[model_name]
    
    # Tenta match parcial (ex: "gpt-5.2-2025-12-11" → "gpt-5.2")
    for key in MODEL_CONFIG:
        if model_name.startswith(key):
            return MODEL_CONFIG[key]
    
    # Default: assume GPT-4 style
    return {
        "is_gpt5": False,
        "reasoning_effort": None,
        "max_context": 128000,
        "max_output": 16000,
    }


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
