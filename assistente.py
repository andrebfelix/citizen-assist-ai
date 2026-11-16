# -*- coding: utf-8 -*-
"""Classe Assistente: faz o atendimento, guarda o histórico e calcula os indicadores.

Integrantes: André Felix (571691), Gabriel Silveira (568910), Isabela Camargo (569196)
"""
import csv
import json
import time
import uuid
from datetime import datetime

from base_conhecimento import BaseConhecimento

CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "nota_facilidade"]

MAX_DIGITOS = 8          # pergunta com 8 ou mais dígitos é recusada (pode ser CPF, telefone...)
MAX_ALTERNATIVAS = 2     # a melhor orientação + até 2 alternativas
TAMANHO_MAX_PERGUNTA = 200


class FimDeEntrada(Exception):
    """A entrada do teclado foi fechada (Ctrl+D / Ctrl+Z): encerra com educação, sem erro."""


class Assistente:
    """Quem conversa com o cidadão."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base                       # objeto BaseConhecimento (composição)
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = uuid.uuid4().hex[:8]     # identifica esta execução (sem dados pessoais)
        self.historico = self._carregar_historico()

    # ------------------------------------------------------------ arquivos
    def _carregar_historico(self):
        """Lê o histórico; se não existir ou estiver corrompido, começa vazio sem travar."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return [d for d in dados if isinstance(d, dict)]
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
            pass
        return []

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
            return True
        except OSError:
            print("Aviso: não consegui salvar o histórico neste momento.")
            return False

    # ------------------------------------------------------------- entrada
    @staticmethod
    def _ler(texto):
        """Lê uma linha do teclado. Se a entrada for fechada, levanta FimDeEntrada (tratada no menu)."""
        try:
            return input(texto).strip()
        except EOFError:
            print()
            raise FimDeEntrada()

    @staticmethod
    def _tem_dado_pessoal(texto):
        """Recusa texto com 8 ou mais dígitos ou com @ (CPF, telefone, e-mail...)."""
        digitos = sum(1 for caractere in texto if caractere.isdigit())
        return digitos >= MAX_DIGITOS or "@" in texto

    def _perguntar_sim_nao(self, texto):
        """Repete até receber s ou n. Respostas inválidas nunca encerram o programa."""
        while True:
            resposta = self._ler(texto).lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("Resposta inválida. Digite s para sim ou n para não.")

    def _escolher_numero(self, texto, maximo):
        """Pede um número de 0 a maximo. Letras, vazio e números fora da faixa são tratados."""
        while True:
            resposta = self._ler(texto)
            if resposta.isdigit() and 0 <= int(resposta) <= maximo:
                return int(resposta)
            print("Opção inválida. Digite um número de 0 a " + str(maximo) + ".")

    # ------------------------------------------------------------ registro
    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        """Guarda um atendimento no histórico (e no arquivo data/historico.json)."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "nota_facilidade": None,
        }
        self.historico.append(atendimento)
        self._salvar_historico()
        return atendimento

    # ----------------------------------------------------------- perguntar
    def perguntar(self):
        """Atendimento por pergunta em texto livre, com busca por pontuação."""
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível no momento. Tente novamente mais tarde.")
            return
        inicio = time.time()
        tentativas = 0
        mostrou = None            # última orientação mostrada
        ajudou = False
        ultima_pergunta = ""
        tempo = 0.0
        while True:
            pergunta = self._ler("\nDigite sua dúvida (0 para voltar): ")
            if pergunta == "0":
                break
            if not pergunta:
                print("Você não digitou nada. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if self._tem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue
            if len(pergunta) > TAMANHO_MAX_PERGUNTA:
                print("Sua dúvida ficou muito longa. Escreva em poucas palavras.")
                continue
            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)
            if not resultados or self.base.confianca(resultados[0][0]) is None:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (exemplo: \"seguro desemprego\") ou use a opção "
                      "\"Navegar por categorias\". Categorias: " + ", ".join(self.base.categorias()) + ".")
                tempo = round(time.time() - inicio, 1)
                if not self._perguntar_sim_nao("Quer tentar de novo? (s/n): "):
                    break
                continue
            pontos, melhor = resultados[0]
            # alternativas: só as que também têm confiança (3 pontos ou mais)
            alternativas = [t for t in resultados[1:1 + MAX_ALTERNATIVAS] if self.base.confianca(t[0])]
            print("\nConfiança da resposta: " + self.base.confianca(pontos) + " (" + str(pontos) + " pontos)")
            melhor.exibir()
            mostrou = melhor
            tempo = round(time.time() - inicio, 1)
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for numero, (pts, alt) in enumerate(alternativas, 1):
                    print("  " + str(numero) + ") " + alt.titulo + " (" + str(pts) + " pontos)")
            if self._perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                ajudou = True
                break
            if alternativas:
                escolha = self._escolher_numero("Digite o número de uma alternativa para ver, ou 0 para "
                                                "escrever outra pergunta: ", len(alternativas))
                if escolha > 0:
                    tentativas += 1
                    alternativa = alternativas[escolha - 1][1]
                    alternativa.exibir()
                    mostrou = alternativa
                    tempo = round(time.time() - inicio, 1)
                    if self._perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): "):
                        ajudou = True
                        break
            if not self._perguntar_sim_nao("Quer tentar de novo com outras palavras? (s/n): "):
                break
        if tentativas > 0:
            self.registrar("pergunta", ultima_pergunta, mostrou.id if mostrou else None,
                           mostrou is not None, ajudou, tentativas, tempo)

    # ------------------------------------------------------------- navegar
    def navegar(self):
        """Atendimento por categorias: escolhe a categoria e depois a orientação."""
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento não está disponível.")
            return
        while True:
            inicio = time.time()
            print("\n=== Categorias ===")
            for numero, categoria in enumerate(categorias, 1):
                print(str(numero) + ") " + categoria)
            print("0) Voltar")
            escolha = self._escolher_numero("Escolha uma categoria: ", len(categorias))
            if escolha == 0:
                return
            categoria = categorias[escolha - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print("\n=== " + categoria + " ===")
                for numero, orientacao in enumerate(orientacoes, 1):
                    print(str(numero) + ") " + orientacao.titulo)
                print("0) Voltar")
                opcao = self._escolher_numero("Escolha uma orientação: ", len(orientacoes))
                if opcao == 0:
                    break
                orientacao = orientacoes[opcao - 1]
                orientacao.exibir()
                tempo = round(time.time() - inicio, 1)
                ajudou = self._perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", "", orientacao.id, True, ajudou, 1, tempo)
                inicio = time.time()

    # --------------------------------------------------------- indicadores
    def indicadores(self, imprimir=True):
        """Calcula (e mostra) os indicadores a partir do histórico."""
        total = len(self.historico)
        if total == 0:
            resultado = {"total": 0}
            if imprimir:
                print("\nAinda não há atendimentos registrados.")
            return resultado
        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]
        tempos = [a["tempo_segundos"] for a in encontrados if isinstance(a.get("tempo_segundos"), (int, float))]
        tentativas = [a["tentativas"] for a in self.historico if isinstance(a.get("tentativas"), int)]
        notas_por_sessao = {}
        for a in self.historico:
            if isinstance(a.get("nota_facilidade"), int):
                notas_por_sessao[a.get("sessao")] = a["nota_facilidade"]
        sem_solucao = []
        for a in self.historico:
            if (not a.get("encontrou") or not a.get("ajudou")) and a.get("pergunta"):
                if a["pergunta"] not in sem_solucao:
                    sem_solucao.append(a["pergunta"])
        resultado = {
            "total": total,
            "encontrada_pct": 100.0 * len(encontrados) / total,
            "acerto_pct": 100.0 * len(ajudaram) / total,
            "tempo_medio": (sum(tempos) / len(tempos)) if tempos else None,
            "tentativas_media": (sum(tentativas) / len(tentativas)) if tentativas else None,
            "facilidade": (sum(notas_por_sessao.values()) / len(notas_por_sessao)) if notas_por_sessao else None,
            "sem_solucao": sem_solucao,
        }
        if imprimir:
            def fmt(valor, casas=1):
                return "sem dados" if valor is None else ("%." + str(casas) + "f") % valor
            print("\n=== Indicadores (" + str(total) + " atendimentos) ===")
            print("Resposta encontrada (%):        " + fmt(resultado["encontrada_pct"]))
            print("Taxa de acerto: ajudou (%):     " + fmt(resultado["acerto_pct"]))
            print("Tempo médio para encontrar (s): " + fmt(resultado["tempo_medio"]))
            print("Tentativas por atendimento:     " + fmt(resultado["tentativas_media"], 2))
            print("Facilidade de uso (1 a 5):      " + fmt(resultado["facilidade"], 2))
            print("Dúvidas sem solução:")
            if sem_solucao:
                for duvida in sem_solucao:
                    print("  - " + duvida)
            else:
                print("  - nenhuma")
        return resultado

    # ----------------------------------------------------------------- CSV
    def exportar_csv(self):
        """Exporta o histórico para data/atendimentos.csv com csv.DictWriter."""
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print("\nExportado: " + self.caminho_csv + " (" + str(len(self.historico)) + " atendimentos).")
            return True
        except OSError:
            print("\nNão consegui exportar o CSV agora. Verifique se o arquivo não está aberto em outro programa.")
            return False

    # ---------------------------------------------------------- menu e fim
    def _pedir_nota(self):
        """Ao sair, pede uma nota de facilidade de 1 a 5 (Enter pula) e grava nos atendimentos da sessão."""
        atendimentos = [a for a in self.historico if a.get("sessao") == self.sessao]
        if not atendimentos:
            return
        while True:
            resposta = self._ler("De 1 (muito difícil) a 5 (muito fácil), quão fácil foi usar o assistente? "
                                 "(Enter para pular): ")
            if resposta == "":
                return
            if resposta.isdigit() and 1 <= int(resposta) <= 5:
                for atendimento in atendimentos:
                    atendimento["nota_facilidade"] = int(resposta)
                self._salvar_historico()
                return
            print("Nota inválida. Digite um número de 1 a 5.")

    def menu(self):
        """Menu principal."""
        print("=" * 60)
        print(self.nome)
        print("Orientação para jovens no primeiro emprego (documentos, contratos e direitos).")
        print("Aviso: este assistente NÃO é um canal oficial. Não digite dados pessoais.")
        print("=" * 60)
        if not self.base.orientacoes:
            print("\nAtenção: " + self.base.erro + ". O assistente continua aberto, mas sem orientações.")
        elif self.base.ignoradas:
            print("\nAviso: " + str(self.base.ignoradas) + " registro(s) incompleto(s) da base foram ignorados.")
        try:
            while True:
                print("\n=== Menu principal ===")
                print("1) Digitar uma dúvida")
                print("2) Navegar por categorias")
                print("3) Ver indicadores")
                print("4) Exportar atendimentos para CSV")
                print("0) Sair")
                opcao = self._escolher_numero("Escolha uma opção: ", 4)
                if opcao == 1:
                    self.perguntar()
                elif opcao == 2:
                    self.navegar()
                elif opcao == 3:
                    self.indicadores()
                elif opcao == 4:
                    self.exportar_csv()
                else:
                    self._pedir_nota()
                    print("\nObrigado! Lembre-se: confirme sempre na fonte oficial. Até logo!")
                    return
        except FimDeEntrada:
            print("Entrada encerrada. Até logo!")
