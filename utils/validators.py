# -*- coding: utf-8 -*-
"""
Validadores
===========

Funções de validação para a aplicação.
"""

import os
import tkinter as tk
from tkinter import messagebox
from typing import Optional


def validar_api_key() -> Optional[str]:
    """
    Valida a existência da API Key da OpenAI.
    
    Verifica se a variável de ambiente OPENAI_API_KEY está definida.
    Exibe um erro visual caso não esteja.
    
    Returns:
        A API key se existir, None caso contrário.
    """
    key = os.getenv("OPENAI_API_KEY")
    
    if not key:
        # Cria janela temporária para exibir o erro
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "🔑 API Key Não Encontrada",
            "Defina a variável de ambiente OPENAI_API_KEY.\n\n"
            "Linux/Mac:\n"
            "  export OPENAI_API_KEY='sua-chave'\n\n"
            "Windows:\n"
            "  set OPENAI_API_KEY=sua-chave"
        )
        
        root.destroy()
        return None
    
    return key
