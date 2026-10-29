# Template: rascunho de layout → esqueleto do app

Preencha cada bloco e envie à ferramenta de IA.

## Contexto

<!-- Quem você é, qual a disciplina/projeto, qual o dataset e o objetivo do dashboard. -->
Meu nome é João Pedro Aguiar Morais, esse é um projeto de prática de streamlit para a disciplina de AVD, o dataset usado será o Student Performance e o objetivo do dashboard a ser construído é praticar o desenvolvimento com streamlit.

## Entrada

<!-- Anexe a imagem do rascunho e cite o caminho dela no repositório (ex.: prompts/rascunho_dashboard1.jpg). Informe também as colunas do dataset e as perguntas que o dashboard deve responder. -->
A imagem a ser usada será um rascunho para o dashboard e está no caminho entregas/rascunho_dashboard1.png

O dataset possui colunas relacionadas ao desempenho escolar, como absences (faltas), studytime (tempo de estudo), failures (reprovações passadas), G1, G2 e G3 (nota final).

O dashboard deve ajudar a responder perguntas como:

Qual a relação entre a quantidade de faltas e a nota final?

Como o tempo de estudo impacta o desempenho?

<!-- Opcional, se a ferramenta de IA não aceitar imagem ou interpretar mal o rascunho: descreva o layout em poucas linhas (ex.: sidebar à esquerda com 2 filtros; topo com 3 métricas; abaixo, 2 gráficos lado a lado). -->

## Restrições

<!-- Regras que a resposta deve respeitar: biblioteca (Streamlit, plotly), arquivos a editar (app.py), carregar dados via src/data_loader.py, o que NÃO deve ser feito. -->

Use exclusivamente Streamlit para o layout/interface e Plotly Express (px) para os gráficos, garantindo interatividade.

Concentre a estrutura no arquivo principal, app.py.

Considere que o dataset já é carregado e retornado como um DataFrame df por uma função fictícia load_data().

NÃO gere modelos de Machine Learning nem aplique limpeza de dados complexa no app.py. O foco é 100% no layout e nos componentes do Streamlit.

## Formato de saída

<!-- Como você quer a resposta: código completo do app.py, só o esqueleto com comentários # TODO, explicação breve de cada seção, etc. -->

Forneça o código completo do esqueleto para o arquivo app.py.
Construa toda a estrutura visual (usando st.sidebar, st.columns, st.metric), mas não perca tempo gerando os gráficos exatos ainda: utilize placeholders/espaços reservados com st.plotly_chart vazios ou st.info com comentários # TODO: Implementar gráfico X cruzando coluna Y e Z. Ao final, adicione uma explicação breve em tópicos sobre a estrutura de layout escolhida.
