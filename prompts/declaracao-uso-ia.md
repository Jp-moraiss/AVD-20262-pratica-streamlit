# Declaração de Uso de IA

**Nome:** João Pedro Aguiar Morais

**Data:** 28 e 29/10/2026

## Ferramenta

Assistente de IA usando Copilot SDK no VS Code.

## Aula 21 — esqueleto do dashboard

### Prompt usado

> Crie um app.py de acordo com o prompt e com base nos notebooks anexados

O prompt detalhado fornecido está em [prompt.md](prompt.md). Foram usados como
contexto o rascunho do Dashboard 1, os notebooks
`eda-joao-pedro.ipynb` e `eda-joao-pedro-downloads.ipynb`, o app anterior e os CSVs
indicados pelo aluno.

### O que foi implementado pela IA

- Substituição do exemplo Heart Disease por um esqueleto Student Performance.
- Sidebar com seleção de variáveis e intervalos, métricas do recorte e espaços
  reservados para os gráficos, conforme o prompt detalhado.
- Leitura do CSV tratado pela função existente, sem nova limpeza complexa ou ML.
- Testes automatizados com Streamlit AppTest e verificação de sintaxe.

## Aula 22 — gráficos, KPIs e seleção vinculada

### Prompt usado

> siga o roteiro e faça a parte 2 do streamlit, e atualize a declaração de uso de ia

Arquivos indicados: [ROTEIRO.md](../ROTEIRO.md) e
[ALTAIR-CROSSFILTER.md](../ALTAIR-CROSSFILTER.md).

### Proposta da IA confirmada pelo aluno antes de codificar o Dashboard 2

Manter Plotly no Dashboard 1 e usar Altair no Dashboard 2. Usar quatro métricas:
alunos no recorte, média de G3, aprovação com G3 >= 10 e mediana de faltas;
filtrar por escola e por clique nas faixas de estudo, além dos intervalos
compartilhados da sidebar. Gerar um rascunho digital antes da implementação.

Respostas do aluno no formulário:

- **Métricas e filtros:** “Usar a proposta acima”.
- **Publicação:** “Deixar alterações locais para eu revisar”.

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito pelo aluno:** proposta de métricas, filtros, bibliotecas e rascunho digital.
- **Modificação de escopo solicitada:** os placeholders da Aula 21 foram substituídos
  por gráficos; a Aula 22 usa Altair no Dashboard 2 conforme o roteiro, em vez de
  restringir toda a aplicação a Plotly como no prompt inicial.
- **Não autorizado:** commit e push; as alterações ficam locais para revisão.
- **Rejeição de outras sugestões:** não registrada nesta conversa.

### Registro de execução da Aula 22

- Definidas as variáveis, métricas e interações em
  [justificativa-metricas.md](../entregas/justificativa-metricas.md).
- Gerado o [rascunho digital do Dashboard 2](../entregas/rascunho-dashboard2.png)
  com código de desenho, antes de implementar a segunda aba. Não é um desenho
  manual do aluno.
- Implementados heatmap de Spearman e histogramas com Plotly Express, duas abas,
  cache no carregamento e tema roxo/rosa com modos claro e escuro.
- Implementado o Dashboard 2 com Altair: clique simples/múltiplo nas faixas de
  estudo filtra KPIs, distribuição das notas e dispersão faltas × G3.
- Adicionados avisos para recortes vazios, variáveis constantes e problemas de
  dados; alterações de filtros limpam a seleção do gráfico.
- Atualizados o README e o checklist das entregas.

### Validações realizadas pela IA

- **11 testes automatizados** em [tests/test_app.py](../tests/test_app.py),
  executados com `python -m unittest discover -s tests -v`: passaram.
  Cobrem métricas e valores dos gráficos, correlação recalculada, filtros
  combinados, zero/uma/várias variáveis, constantes, recortes vazios, escolas,
  payloads de seleção, cache, CSV ausente/inválido e dataset com uma linha.
- O primeiro teste exploratório procurou o nome antigo do elemento Altair no
  AppTest; foi ajustado ao nome retornado pela versão instalada.
- A primeira execução da suíte usava a posição do multisseletor, que passou a
  apontar para escolas após adicionar a segunda aba. Os testes passaram a
  identificar os widgets por chaves explícitas.
- O Pylance apontou incompatibilidade de tipo em `text_auto=".2f"`; foi usada
  a opção booleana e o formato foi aplicado via `texttemplate`, preservando
  duas casas decimais sem suprimir o diagnóstico.
- **Navegador real:** recorte completo = 649 alunos, média 11,91 e aprovação 84,6%.
  Clique em faixa 1 = 212 alunos, média 10,84, aprovação 76,4% e mediana de faltas 4.
  Shift + clique incluindo faixa 3 = 309 alunos, média 11,59, aprovação 81,6%
  e mediana de faltas 2; a dispersão exibiu 309 pontos.
- O botão de limpeza restaurou os 649 alunos. Após selecionar uma faixa e
  remover a escola MS, a seleção foi limpa e o recorte GP apresentou
  423 alunos, média 12,58 e aprovação 92,4%, com 423 pontos na dispersão.
- Verificados também os histogramas renderizados: as quatro categorias de
  `studytime` contaram 212, 305, 97 e 35 alunos, totalizando os 649 registros.
- A análise final do Pylance não retornou diagnósticos nos arquivos Python alterados.
- Nenhum commit, push ou deploy foi realizado nesta etapa, conforme a escolha
  do aluno. Revisão final e publicação continuam pendentes.

As decisões explicitamente confirmadas acima não equivalem à revisão final de
todo o código pelo aluno. Código, documentação e rascunho digital produzidos
pela IA devem ser revisados pelo autor antes da entrega.

## 29/10/2026 — Alteração das métricas

### Prompt usado

Trechos da solicitação original:

> Faça a mudança das métricas.
>
> As métricas devem ser essas:

O aluno forneceu as quatro métricas, acompanhadas de variável, definição,
justificativa, público-alvo, decisões apoiadas e significado para o público.
O conteúdo está registrado em
[justificativa-metricas.md](../entregas/justificativa-metricas.md), com o ajuste
da métrica 4 descrito abaixo.

> com base nisso, atualize a declaração de uso de ia e a justificativa de métricas, evite escrever algo que não está escrito nesse prompt e faça o mínimo de alterações possíveis

### Escolha das novas métricas pelo aluno

**As novas métricas foram escolhidas por mim, João Pedro Aguiar Morais, e não
propostas pela IA nesta etapa.** Também forneci os textos de justificativa e
os públicos-alvo. A IA foi utilizada para implementar essas escolhas no
Dashboard 2 e atualizar a documentação correspondente.

As métricas que defini foram:

1. **Taxa de Aprovação vs. Reprovação:** proporção e quantidade absoluta de
   alunos aprovados (`G3 >= 10`) e reprovados (`G3 < 10`), para diretores,
   coordenadores pedagógicos e gestores escolares.
2. **Média da Nota Final:** média aritmética de `G3` na amostra filtrada, para
   professores e equipe pedagógica.
3. **Mediana de Faltas:** ponto central de `absences`, escolhido em vez da média
   por causa dos outliers, para orientadores educacionais, professores e
   assistentes sociais da escola.
4. **Tempo Médio de Estudo Semanal (Extra-classe):** proposta inicial baseada
   em `studytime`, para acompanhar o estudo fora da escola, direcionada a
   coordenadores pedagógicos, pais e responsáveis.

Essa escolha substituiu o conjunto inicialmente sugerido pela IA na etapa
anterior. A quantidade de alunos deixou de ser uma métrica independente do
Dashboard 2, permanecendo como informação do recorte.

### Ajuste técnico proposto pela IA e confirmado pelo aluno

A IA informou que `studytime` contém códigos de faixas de estudo, não horas
exatas, e que calcular uma média em horas exigiria uma conversão não fornecida
pelo dataset. Minha resposta foi:

> Mostre como horas para facilitar leitura e interpretação

Em seguida, a IA propôs apresentar quantidade e percentual de alunos por faixa:
menos de 2 h, de 2 a 5 h, de 5 a 10 h e mais de 10 h. Confirmei essa alternativa
no formulário, aceitando usar as faixas em horas no lugar de uma média de horas.
Por isso, a quarta métrica passou a se chamar **Tempo de Estudo Semanal
(Extra-classe)**, sem indicar uma média que os dados não permitem calcular.

### O que foi aceito, modificado ou rejeitado e por quê

- **Definido pelo aluno:** escolha das quatro métricas e fornecimento de suas
  justificativas, públicos-alvo e decisões apoiadas.
- **Aceito pelo aluno:** apresentação de `studytime` por faixas em horas, com
  quantidades e percentuais, para facilitar a interpretação sem inventar horas.
- **Modificado:** a métrica 4 deixou de ser uma média de horas e passou a
  representar a distribuição por faixas, após minha confirmação.
- **Preservado:** filtros, gráficos e Dashboard 1, conforme o pedido de fazer
  o mínimo de alterações.
- **Rejeição de outras sugestões:** não registrada nesta etapa.

### O que foi implementado pela IA

- Ajuste dos KPIs do Dashboard 2 às métricas escolhidas pelo aluno: aprovação
  e reprovação com quantidade e percentual, média da nota final, mediana de
  faltas e tabela de estudo semanal por faixas em horas.
- Manutenção do recálculo das métricas conforme os filtros e a seleção no
  gráfico, incluindo o tratamento de recortes vazios.
- Atualização da justificativa com o texto fornecido pelo aluno, ajustando a
  métrica 4 conforme a confirmação acima.
- Atualização desta declaração, da descrição dos KPIs no README e dos testes
  relacionados às métricas.

### Validações realizadas pela IA

- **12 testes automatizados** em [tests/test_app.py](../tests/test_app.py)
  passaram, verificando também as quantidades e percentuais de aprovação,
  reprovação e faixas de estudo.
- Adicionado teste para o limite de aprovação: nota 9 corresponde a reprovação
  e nota 10 corresponde a aprovação.
- Verificada a preservação dos filtros, gráficos, seleção vinculada, cache e
  tratamento de recortes vazios.
- Corrigida uma incompatibilidade de tipo apontada pelo Pylance no uso de
  `reindex`; a análise final não retornou diagnósticos no app e nos testes.
- Nenhum commit, push ou deploy foi realizado nesta alteração.

## 29/10/2026 — Donut e storytelling da aprovação

### Prompt usado

> Faça uma modificação na visualização da taxa de aprovação com um gráfico de donut, com um storytelling de algo parecido como "número de aprovados x vezes maior que número de aprovados"

### Decisão do aluno e esclarecimento

A escolha do donut e da comparação textual foi feita pelo aluno. Como o pedido
repetia “aprovados” nos dois lados, a IA perguntou se a comparação deveria ser
entre aprovados e reprovados. O aluno confirmou.

### O que foi implementado pela IA

- Substituição dos indicadores percentuais de aprovação e reprovação por um
  donut Altair, mantendo quantidades e percentuais visíveis e nos tooltips.
- Frase dinâmica com a razão entre os grupos: “O número de aprovados é
  aproximadamente X vezes o número de reprovados”. Quando há mais reprovados,
  a comparação se inverte. Empate, ausência de uma categoria e recorte vazio
  recebem mensagens específicas, sem divisão por zero.
- Preservação dos filtros, da seleção vinculada e das demais métricas.
- Atualização da justificativa e dos testes relacionados.

### Validações realizadas pela IA

- **13 testes automatizados passaram**, incluindo valores do donut após filtros
  e seleção, limites de aprovação, comparação em ambos os sentidos, empate,
  todos aprovados, todos reprovados e recorte vazio.
- No navegador, o donut apresentou 549 aprovados e 100 reprovados, com a razão
  de 5,49 vezes. Após selecionar a faixa de estudo 1, passou a 162 aprovados
  e 50 reprovados, com a frase atualizada para 3,24 vezes.
- Pylance sem diagnósticos no app e nos testes. Nenhum commit ou push realizado.

## 29/10/2026 — Separação de métricas e visualizações

### Prompt usado

> deixe separado no dashboard as métricas e as visualizações, use de base o rascunho manual do dashboard 2

### Referência fornecida pelo aluno

O aluno forneceu o [rascunho manual do Dashboard 2](../entregas/rascunho-manual-dashboard2.png),
com sidebar à esquerda, métricas no topo e visualizações abaixo. A organização
do layout foi definida pelo aluno; a IA adaptou o código a essa referência.

### O que foi implementado pela IA

- Dois blocos com bordas e títulos: **Métricas** e **Visualizações**.
- No topo, aprovação e reprovação com valores numéricos, média da nota final,
  mediana de faltas e resumo das faixas de estudo em horas.
- No bloco inferior, donut com storytelling e barras de estudo lado a lado;
  abaixo, distribuição das notas e dispersão faltas × nota final.
- Filtro de escolas e botão de limpeza da seleção transferidos para a sidebar,
  mantendo seu efeito exclusivo no Dashboard 2.
- Preservação das métricas escolhidas pelo aluno, das regras de cálculo e da
  atualização pela seleção nas barras. Dashboard 1 mantido.

### Validações realizadas pela IA

- **14 testes automatizados passaram**, incluindo um novo teste que verifica
  a ordem dos blocos, ausência de gráficos na área de métricas, presença dos
  quatro gráficos no bloco de visualizações e filtros na sidebar.
- No navegador, confirmada a área de métricas acima da área de visualizações,
  com zero gráficos no primeiro bloco e quatro no segundo.
- Pylance sem diagnósticos no app e nos testes. Nenhum commit ou push realizado.

## 29/10/2026 — Barras empilhadas e métricas do Dashboard 1

### Prompt usado

> no gráfico alunos por faixa de estudo, modifique a visualização para um gráfico de barras empilhadas. além disso, remova as métricas do dashboard 1, com exceção de "alunos no recorte".

### Escolha confirmada pelo aluno

A IA perguntou qual categoria deveria dividir as barras. O aluno escolheu
**aprovados e reprovados**, mantendo a seleção da faixa inteira ao clicar em
qualquer segmento.

### O que foi implementado pela IA

- Barras empilhadas de contagem de alunos por faixa de estudo, divididas pela
  situação (`G3 >= 10`: aprovado; `G3 < 10`: reprovado), com as mesmas cores do donut.
- Tooltip com faixa, situação, quantidade de alunos e nota final média do grupo.
- Preservação dos filtros e da seleção vinculada por faixa de estudo.
- Remoção da média da nota final e da taxa de aprovação do Dashboard 1,
  mantendo somente **Alunos no recorte** nessa aba. Os KPIs do Dashboard 2
  e os gráficos do Dashboard 1 foram preservados.
- Atualização dos testes e da descrição do funcionamento no README.

### Validações realizadas pela IA

- **15 testes automatizados passaram**, verificando também o empilhamento,
  as contagens e médias por situação após filtros, a seleção por faixa inteira
  e a presença de uma única métrica no Dashboard 1.
- Pylance sem diagnósticos no app. Nenhum commit ou push realizado.

## 29/10/2026 — Mapa de correlação triangular

### Prompt usado

> no dashboard 1, no mapa de correlação, mantenha só a diagonal principal (formando um triângulo), além disso, retire a diagonal também

### O que foi implementado pela IA

- O pedido foi interpretado como mostrar apenas o triângulo inferior da matriz,
  excluindo a diagonal principal e a metade superior, que repete as correlações.
- Aplicada uma máscara visual, preservando os valores de Spearman entre variáveis
  diferentes, a ordem selecionada e a escala de cores de -1 a 1.
- Desativados os tooltips nas células ocultas e mantidos os filtros existentes.
- Atualizados o README e os testes do heatmap.

### Validações realizadas pela IA

- **16 testes automatizados passaram**, verificando valores abaixo da diagonal,
  ausência de valores na diagonal e acima dela, ordem das variáveis e recálculo
  após filtros. Com duas variáveis, resta somente uma correlação visível.
- Pylance sem diagnósticos no app. Nenhum commit ou push realizado.
