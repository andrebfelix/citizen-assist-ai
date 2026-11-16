# Relatório de validação automatizada — Citizen Assist AI: Primeiro Emprego

## Escopo

Foi executada uma bateria automatizada de 10 interações por meio do ponto de entrada `python main.py`, utilizando entradas de terminal para verificar o fluxo de perguntas, a busca na base, o registro do histórico, a atribuição da avaliação de facilidade, a apresentação dos indicadores e a exportação do CSV.

Esta execução valida o comportamento do software. Ela não corresponde à aplicação observacional com participantes externos prevista na seção de teste com usuários do guia de entrega.

## Cenários executados

| Nº | Pergunta | Resultado do sistema |
|---:|---|---|
| 1 | Como pedir seguro desemprego? | Seguro-desemprego depois da demissão |
| 2 | Quanto tempo pode durar o estágio na mesma empresa? | Estágio: regras e direitos do estagiário |
| 3 | Meu RG antigo ainda vale? | Carteira de Identidade Nacional (novo RG) |
| 4 | O que é FGTS e quem paga? | FGTS: depósito mensal da empresa |
| 5 | Como faço a carteira de trabalho digital? | Carteira de Trabalho Digital |
| 6 | Quem pode ser jovem aprendiz? | Jovem Aprendiz: contrato de aprendizagem de 14 a 24 anos |
| 7 | Como funciona o contrato de experiência? | Contrato de experiência de até 90 dias |
| 8 | Como consultar meu CPF? | CPF: inscrição gratuita na Receita Federal |
| 9 | Como funciona o título de eleitor? | Título de eleitor e voto aos 16 e 17 anos |
| 10 | posso trabalhar com 16 anos? | Não encontrada; o sistema exibiu a mensagem de ausência de orientação |

## Indicadores registrados pelo programa

| Indicador | Resultado |
|---|---:|
| Atendimentos registrados | 10 |
| Resposta encontrada | 90,0% |
| Taxa de acerto (marcada como útil no roteiro automatizado) | 90,0% |
| Tempo médio registrado | 0,0 s |
| Tentativas por atendimento | 1,00 |
| Nota de facilidade registrada | 4,00 / 5 |
| Dúvida sem orientação | “posso trabalhar com 16 anos?” |

## Verificações técnicas

- Execução de `python main.py`: concluída com código de saída 0.
- Histórico JSON: 10 registros.
- Exportação CSV pelo menu 4: concluída com 10 registros de dados, além do cabeçalho.
- Menu de indicadores: exibiu os seis indicadores previstos e a dúvida não encontrada.
- Pergunta sem correspondência: não encerrou o programa e foi registrada como não encontrada.

## Observação sobre interpretação

As entradas foram fornecidas automaticamente ao processo do terminal. Por isso, o tempo de 0,0 s e a nota de facilidade não representam uma medição humana válida. Os resultados demonstram a execução dos fluxos e a consistência dos arquivos, mas não substituem a coleta com pelo menos três participantes externos. Para concluir essa etapa, é necessário observar pessoas reais utilizando o programa e registrar suas respostas sem identificá-las.
