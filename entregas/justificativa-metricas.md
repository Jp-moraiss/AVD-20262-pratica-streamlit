# Justificativa das métricas — Dashboard 2

## Métrica 1: Taxa de Aprovação vs. Reprovação

- **Variável:** G3 (Nota final — transformada em categoria: >= 10 Aprovado, < 10 Reprovado).
- **O que mede:** A proporção e a quantidade absoluta de alunos que alcançaram a nota mínima exigida em comparação aos que não alcançaram.
- **Por que foi escolhida:** É o indicador de "sucesso x falha" do sistema escolar. Antes de olhar para os detalhes, a gestão precisa saber o saldo final de aprovações.
- **Público-alvo:** Diretores, coordenadores pedagógicos e gestores escolares.
- **Qual decisão pode ser apoiada por essa métrica?** Alocação de recursos financeiros e de tempo para turmas de recuperação, nivelamento escolar ou mudanças na metodologia de ensino (se o índice de reprovação está alto, o problema pode ser na metodologia).
- **O que comunica ao público-alvo:** A eficácia do ensino e do aproveitamento da turma no período letivo.

## Métrica 2: Média da Nota Final

- **Variável:** G3 (Nota final).
- **O que mede:** O valor médio aritmético das notas de todos os alunos da amostra filtrada.
- **Por que foi escolhida:** Diferente da taxa de aprovação, essa métrica mostra a média da nota. Pra ser aprovado precisa de 10, mas a média pode ter sido maior que isso (18, por exemplo).
- **Público-alvo:** Professores e equipe pedagógica.
- **Qual decisão pode ser apoiada por essa métrica?** Calibração do nível de dificuldade das provas, revisão do plano de ensino e identificação de turmas que precisam de mais aprofundamento.
- **O que comunica ao público-alvo:** O quão bem, em média, a turma entendeu os conteúdos ensinados, mostrando o nível da turma.

## Métrica 3: Mediana de Faltas

- **Variável:** absences (Número de faltas).
- **O que mede:** O ponto central de faltas da turma.
- **Por que foi escolhida:** A mediana foi preferida no lugar da média porque a distribuição de faltas tem outliers (ex.: uma turma presente, mas um único aluno que faltou 40 vezes, jogaria a média lá para cima artificialmente). A mediana mostra o comportamento de assiduidade típico da turma.
- **Público-alvo:** Orientadores educacionais, professores e assistentes sociais da escola.
- **Qual decisão pode ser apoiada por essa métrica?** Estabelecer quando o Conselho Tutelar ou os pais devem ser acionados, e desenhar campanhas de engajamento escolar.
- **O que comunica ao público-alvo:** O nível de engajamento e presença típico do corpo discente, ajudando a diferenciar se o absenteísmo é uma cultura geral da turma ou problema de indivíduos isolados.

## Métrica 4: Tempo de Estudo Semanal (Extra-classe)

- **Variável:** studytime.
- **O que mede:** A quantidade e o percentual de alunos por faixa de estudo semanal: menos de 2 h, de 2 a 5 h, de 5 a 10 h e mais de 10 h.
- **Por que foi escolhida:** Tempo de estudo mede o esforço proativo do aluno. Permite cruzar dados comportamentais com o desempenho e mostrar se os alunos estão estudando fora da escola de forma adequada.
- **Público-alvo:** Coordenadores pedagógicos, pais e responsáveis, etc.
- **Qual decisão pode ser apoiada por essa métrica?** Estímulo à organização da rotina de estudo dos alunos, permitindo um acompanhamento melhor por parte dos responsáveis/professores/equipe pedagógica.
- **O que comunica ao público-alvo:** Acompanhamento do tempo de estudo e dedicação dos alunos fora da escola (quanto tempo eles estudam em casa).

Conforme confirmado pelo aluno, a métrica 4 usa faixas em horas em vez de uma
média de horas, pois `studytime` não informa o tempo exato.
