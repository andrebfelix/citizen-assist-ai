# -*- coding: utf-8 -*-
"""Citizen Assist AI: Primeiro Emprego. Assistente de terminal para jovens no primeiro emprego.

Integrantes: André Felix (571691), Gabriel Silveira (568910), Isabela Camargo (569196)

Como executar:  python main.py
"""
import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    base.carregar()          # se falhar, o assistente avisa e continua aberto
    assistente = Assistente("Citizen Assist AI: Primeiro Emprego", base,
                            CAMINHO_HISTORICO, CAMINHO_CSV)
    try:
        assistente.menu()
    except KeyboardInterrupt:
        print("\n\nEncerrado. Até logo!")


if __name__ == "__main__":
    main()
