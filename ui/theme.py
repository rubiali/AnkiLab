# -*- coding: utf-8 -*-
"""
Sistema de Temas
================

Definição centralizada de cores, fontes e estilos visuais.
Tema: Neuro / Cognitive Lab
"""


class NeuroTheme:
    """
    Paleta de cores e configurações visuais do tema Neuro/Cognitive Lab.
    
    Uso:
        from ui.theme import NeuroTheme
        bg = NeuroTheme.BG_MAIN
    """
    
    # ==========================================================================
    # FUNDOS
    # ==========================================================================
    BG_MAIN = "#0f1419"
    BG_SECONDARY = "#1a1f26"
    BG_TERTIARY = "#242b35"
    BG_INPUT = "#1e252e"
    BG_HOVER = "#2a3441"
    
    # ==========================================================================
    # CORES DE DESTAQUE
    # ==========================================================================
    ACCENT_PRIMARY = "#00d4aa"
    ACCENT_SECONDARY = "#9b7dff"
    ACCENT_TERTIARY = "#00a3cc"
    
    # ==========================================================================
    # TEXTOS
    # ==========================================================================
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    TEXT_INVERSE = "#0f1419"
    
    # ==========================================================================
    # CORES SEMÂNTICAS
    # ==========================================================================
    SUCCESS = "#3fb950"
    WARNING = "#d29922"
    ERROR = "#f85149"
    INFO = "#58a6ff"
    
    # ==========================================================================
    # BORDAS E SEPARADORES
    # ==========================================================================
    BORDER = "#30363d"
    BORDER_FOCUS = "#00d4aa"
    SEPARATOR = "#21262d"
    
    # ==========================================================================
    # FLASHCARDS
    # ==========================================================================
    CARD_Q = "#58a6ff"
    CARD_A = "#3fb950"
    CARD_HEADER = "#f0883e"
    
    # ==========================================================================
    # FONTES
    # ==========================================================================
    FONT_MONO = ("Consolas", "Cascadia Code", "monospace")
    FONT_UI = ("Segoe UI", "sans-serif")
    
    @classmethod
    def get_mono_font(cls, size: int = 8, weight: str = "normal") -> tuple:
        """
        Retorna tupla de fonte monoespaçada para tkinter.
        
        Args:
            size: Tamanho da fonte.
            weight: Peso ("normal" ou "bold").
        
        Returns:
            Tupla (família, tamanho, peso).
        """
        return (cls.FONT_MONO[0], size, weight)
    
    @classmethod
    def get_ui_font(cls, size: int = 8, weight: str = "normal") -> tuple:
        """
        Retorna tupla de fonte UI para tkinter.
        
        Args:
            size: Tamanho da fonte.
            weight: Peso ("normal" ou "bold").
        
        Returns:
            Tupla (família, tamanho, peso).
        """
        return (cls.FONT_UI[0], size, weight)
