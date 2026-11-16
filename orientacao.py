# -*- coding: utf-8 -*-
"""Classe Orientacao: uma informação da base de conhecimento (um registro do JSON).

Integrantes: André Felix (571691), Gabriel Silveira (568910), Isabela Camargo (569196)
"""

CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em")

AVISO = "este assistente NÃO é um canal oficial."


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @staticmethod
    def registro_valido(registro):
        """Confere se um dicionário do JSON tem todos os campos e tipos esperados."""
        if not isinstance(registro, dict):
            return False
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in registro:
                return False
        if not isinstance(registro["id"], int):
            return False
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(registro[campo], str) or not registro[campo].strip():
                return False
        if not isinstance(registro["palavras_chave"], list) or len(registro["palavras_chave"]) < 3:
            return False
        if not isinstance(registro["documentos"], list):
            return False
        return True

    @classmethod
    def de_dicionario(cls, registro):
        """Cria uma Orientacao a partir de um dicionário já validado."""
        return cls(registro["id"], registro["categoria"], registro["titulo"],
                   registro["palavras_chave"], registro["resposta"],
                   registro["documentos"], registro["onde"], registro["fonte"],
                   registro["verificado_em"])

    def exibir(self):
        """Mostra a orientação na tela, sempre com fonte, data e aviso."""
        print()
        print(">> " + self.titulo + "  [" + self.categoria + "]")
        print(self.resposta)
        print("Documentos necessários:")
        if self.documentos:
            for doc in self.documentos:
                print("  - " + doc)
        else:
            print("  - Nenhum documento específico")
        print("Onde: " + self.onde)
        print("Fonte: " + self.fonte + " (verificado em " + self.verificado_em + ")")
        print("Aviso: " + AVISO)
