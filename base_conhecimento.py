# -*- coding: utf-8 -*-
"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação.

Integrantes: André Felix (571691), Gabriel Silveira (568910), Isabela Camargo (569196)
"""
import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a", "é": "e", "è": "e", "ê": "e",
           "í": "i", "ì": "i", "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ú": "u", "ù": "u",
           "ü": "u", "ç": "c"}

SINAIS = "?!.,;:()-/\"'\u201c\u201d\u2019\u00ba\u00aa\u00b0"

# Regra de pontuação (ver README)
PONTOS_PALAVRA_CHAVE = 3      # palavra-chave da orientação que aparece na pergunta
PONTOS_PALAVRA_TITULO = 1     # palavra da pergunta (4+ letras) que aparece no título
LIMITE_ALTA = 6               # 6 pontos ou mais: confiança ALTA
LIMITE_MEDIA = 3              # de 3 a 5 pontos: confiança MÉDIA
TAMANHO_MIN_PALAVRA = 4


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação; devolve com um espaço no começo e no fim."""
    texto = str(texto).lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """O conjunto de todas as orientações."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []      # lista de objetos Orientacao
        self.erro = ""             # explica por que a base não carregou (se for o caso)
        self.ignoradas = 0         # registros do JSON que estavam incompletos

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava: devolve False se falhar."""
        self.orientacoes = []
        self.ignoradas = 0
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = "arquivo da base de conhecimento não encontrado"
            return False
        except json.JSONDecodeError:
            self.erro = "arquivo da base de conhecimento está corrompido"
            return False
        except (OSError, UnicodeDecodeError):
            self.erro = "não foi possível ler o arquivo da base de conhecimento"
            return False
        if not isinstance(dados, list):
            self.erro = "o formato da base de conhecimento é inválido"
            return False
        for registro in dados:
            if Orientacao.registro_valido(registro):
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            else:
                self.ignoradas += 1
        if not self.orientacoes:
            self.erro = "a base de conhecimento não tem nenhuma orientação válida"
            return False
        self.erro = ""
        return True

    def categorias(self):
        """Lista as categorias, na ordem em que aparecem na base, sem repetir."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Pontos de uma orientação para uma pergunta: +3 por palavra-chave, +1 por palavra do título."""
        pergunta_norm = normalizar(pergunta)
        pontos = 0
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE
        titulo_norm = normalizar(orientacao.titulo)
        for palavra in set(pergunta_norm.split()):
            if len(palavra) >= TAMANHO_MIN_PALAVRA and (" " + palavra + " ") in titulo_norm:
                pontos += PONTOS_PALAVRA_TITULO
        return pontos

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor pontuação (só quem pontuou)."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados

    @staticmethod
    def confianca(pontos):
        """ALTA (6+), MÉDIA (3 a 5) ou None (menos de 3: não encontrei)."""
        if pontos >= LIMITE_ALTA:
            return "ALTA"
        if pontos >= LIMITE_MEDIA:
            return "MÉDIA"
        return None
