# -*- coding: utf-8 -*-
"""
Módulo Core
===========

Contém a lógica de negócio principal: chamadas à API e parsing.
"""

from .api import generate_cards, refine_cards, review_deck
from .parser import (
    parse_cards,
    parse_csv_cards,
    parse_apkg_cards,
    parse_flashcard_file,
    format_cards_for_export_tab,
    format_cards_for_prompt,
    format_cards_for_refine,
    extract_new_cards_from_audit,
    extract_cards_from_review,
    extract_report_from_review,
)

__all__ = [
    "generate_cards",
    "refine_cards",
    "review_deck",
    "parse_cards",
    "parse_csv_cards",
    "parse_apkg_cards",
    "parse_flashcard_file",
    "format_cards_for_export_tab",
    "format_cards_for_prompt",
    "format_cards_for_refine",
    "extract_new_cards_from_audit",
    "extract_cards_from_review",
    "extract_report_from_review",
]
