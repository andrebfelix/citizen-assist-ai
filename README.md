# Citizen Assist AI: Primeiro Emprego

Assistente de terminal, feito em Python, que orienta **jovens no primeiro emprego** sobre documentos, contratos e direitos, sempre mostrando a fonte, a data de verificação e o aviso de que **não é um canal oficial**.

## Integrantes

| Integrante | RM |
|---|---|
| André Felix | 571691 |
| Gabriel Silveira | 568910 |
| Isabela Camargo | 569196 |

## Público e problema

**Público:** jovens (16 a 24 anos) que estão procurando ou começando o primeiro emprego, estágio ou contrato de aprendizagem.

**Problema:** as informações sobre CPF, identidade, carteira de trabalho, contrato de experiência, estágio, FGTS e seguro-desemprego existem, mas estão espalhadas, em linguagem técnica e misturadas com páginas que parecem oficiais e não são. O assistente responde apenas com o que está em uma base de conhecimento com fontes oficiais, em linguagem simples, e admite quando não encontrou (em vez de inventar).

## ODS relacionados

- **ODS 8:** trabalho decente e crescimento econômico (direitos do primeiro emprego, aprendizagem, estágio).
- **ODS 4:** educação de qualidade (aprendizagem profissional e estágio ligados à escola).
- **ODS 10:** redução das desigualdades (acesso a programas como o CadÚnico).
- **ODS 16:** instituições eficazes e acesso à informação (orientação com fonte e data).

## Como executar

Python 3.8 ou superior. **Não usa bibliotecas externas.**

```bash
python main.py
```

Menu: 1) digitar uma dúvida, 2) navegar por categorias, 3) ver indicadores, 4) exportar atendimentos para CSV, 0) sair (pede uma nota de facilidade de 1 a 5). Em todas as telas de escolha, **0 volta**.

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py               # cria a base e o assistente e abre o menu
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento (+ normalizar)
├── assistente.py         # classe Assistente
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    └── atendimentos.csv
```

Classes (composição: `Assistente` → `BaseConhecimento` → lista de `Orientacao`):

| Classe | Atributos | Métodos |
|---|---|---|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()` |

## Base de conhecimento

`data/base_conhecimento.json`: lista de dicionários com `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`. São **13 orientações em 3 categorias** (Documentos; Primeiro emprego; Dinheiro e proteção), cada uma com 7 a 10 palavras-chave. Todas têm fonte oficial (portais do governo, leis no Planalto, TSE, Exército) e a data em que a equipe conferiu (2026-11-11). Não há valores em reais nem prazos inventados: só o que consta nas fontes.

## Regra de pontuação usada

1. `normalizar()`: minúsculas, sem acentos e sem pontuação, com um espaço no começo e no fim (assim compara palavras inteiras).
2. `pontuar()`: **+3** por palavra-chave da orientação que aparece na pergunta; **+1** por palavra da pergunta (4 letras ou mais) que aparece no título.
3. Confiança: **6 pontos ou mais = ALTA**; **3 a 5 = MÉDIA**; **menos de 3 = "não encontrei"** (sugere outras palavras ou as categorias).
4. `buscar()` devolve uma **lista de tuplas `(pontos, orientacao)`**, da maior para a menor pontuação. O assistente mostra a melhor orientação e até 2 alternativas.

Exemplo: "Como peço o seguro-desemprego?" → "seguro desemprego" (+3) + "desemprego" (+3) + "seguro" no título (+1) + "desemprego" no título (+1) = **8 pontos, confiança ALTA**.

**Ajuste explicado (permitido pelo enunciado):** as alternativas só aparecem se também tiverem 3 pontos ou mais, para não sugerir orientações pouco relacionadas.

## Regras de atendimento

- **Entradas inválidas** (opção fora da faixa, letras, resposta vazia, s/n inválido) nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** base ausente, corrompida ou com registros incompletos não trava o programa (ele avisa e continua; registros incompletos são ignorados). Histórico ausente ou corrompido recomeça vazio.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: `data`, `sessao`, `origem` (pergunta ou categoria), `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas`, `tempo_segundos` e `nota_facilidade` (1 a 5, pedida ao sair). O tempo é medido com `time.time()` desde o início do atendimento até a orientação ser mostrada.

Indicadores (menu 3): resposta encontrada (%), taxa de acerto, isto é, ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (média das notas, uma por sessão) e lista de dúvidas sem solução. O menu 4 exporta para `data/atendimentos.csv` com `csv.DictWriter`.

## Integrações com outras disciplinas

Nenhuma. A busca por pontuação é a do enunciado, implementada do zero.

## Fontes consultadas

- Receita Federal (CPF): https://www.gov.br/receitafederal
- Governo Federal (identidade, CIN): https://www.gov.br
- Tribunal Superior Eleitoral (título): https://www.tse.jus.br
- Ministério do Trabalho e Emprego (carteira digital, seguro-desemprego): https://www.gov.br/trabalho-e-emprego
- Exército, Alistamento Online: https://alistamento.eb.mil.br
- CLT (arts. 445 e 130, experiência e férias): https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
- Lei do Aprendiz (10.097/2000): https://www.planalto.gov.br/ccivil_03/Leis/L10097.htm
- Lei do Estágio (11.788/2008): https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm
- Lei do FGTS (8.036/1990): https://www.planalto.gov.br/ccivil_03/leis/l8036consol.htm
- Meu INSS: https://meu.inss.gov.br
- Meu CadÚnico: https://meucadunico.cidadania.gov.br/meu_cadunico/
- TRT-4, jovem aprendiz: https://www.trt4.jus.br/portais/trt4/jovem-aprendiz
- Agência Brasil, prazo do alistamento militar de 2026 (30/06/2026), reproduzida por veículos de imprensa.

## Teste com usuários

O teste com usuários foi realizado pela equipe e o histórico consolidado contém **22 atendimentos em 5 sessões**, sem nomes ou dados pessoais. A quantidade exata de participantes não foi registrada no histórico; por isso, ela não é inferida a partir da quantidade de sessões.

### Indicadores registrados

| Indicador | Resultado |
|---|---:|
| Atendimentos | 22 |
| Resposta encontrada | 95,5% (21 de 22) |
| Taxa de acerto (ajudou) | 90,9% (20 de 22) |
| Tempo médio para encontrar, entre respostas encontradas | 8,4 s |
| Tentativas por atendimento | 1,00 |
| Facilidade de uso | 4,00 / 5 (média das notas por sessão) |

**Dúvidas sem solução:**
- “posso trabalhar com 16 anos?” (não encontrada na base durante o teste)
- “O primeiro emprego conta na carteira de trabalho?” (a orientação exibida não resolveu a dúvida)

**Melhoria realizada a partir do teste:** foram acrescentadas à orientação “Carteira de Trabalho Digital” as palavras-chave “conta na carteira” e “primeiro emprego na carteira”, para melhorar a identificação de perguntas sobre o registro do primeiro emprego. Essa alteração foi feita na base de conhecimento após a coleta dos 22 atendimentos; portanto, os indicadores acima representam os resultados anteriores à melhoria.


## Limitações

- Base pequena (13 orientações) e nacional: não cobre regras de cada estado ou município.
- A busca compara palavras inteiras: palavras fora das palavras-chave (por exemplo "vale-transporte") não são encontradas, e o assistente admite que não sabe.
- Leis e prazos mudam: a base precisa ser reconferida nas fontes oficiais (data em cada orientação).
- Não calcula valores (salário, seguro-desemprego, FGTS) nem substitui o atendimento oficial.
- O tempo medido inclui o tempo de leitura da pessoa.

## Vídeo técnico

Link do vídeo técnico (YouTube, não listado): pendente de envio pela equipe.
