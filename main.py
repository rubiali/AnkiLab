#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnkiLab - Cognitive Flashcard Engine
=====================================

Ponto de entrada principal da aplicação.

Autor: AnkiLab Team
Versão: 3.0
"""

import tkinter as tk
from utils.validators import validar_api_key
from ui.app import AnkiLabApp


def main():
    """Inicializa e executa a aplicação AnkiLab."""
    
    # Validação da API Key antes de iniciar a UI
    api_key = validar_api_key()
    if not api_key:
        raise SystemExit(1)
    
    # Inicialização da janela principal
    root = tk.Tk()
    
    # Instancia a aplicação
    _ = AnkiLabApp(root)
    
    # Loop principal da interface
    root.mainloop()


if __name__ == "__main__":
    main()
