import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Student Performance | João Pedro",
    layout="wide",
)

st.title("Desempenho escolar — Student Performance")
st.caption("João Pedro Aguiar Morais | Análise e Visualização de Dados")
st.write(
    "Explore a relação entre faltas, tempo de estudo e desempenho escolar. "
    "Use os filtros à esquerda para definir o grupo de alunos da análise."
)

try:
    df = load_data()
except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as erro:
    st.error(f"Não foi possível carregar o dataset tratado: {erro}")
    st.stop()

VARS_QUANT = ["age", "absences", "G1", "G2", "G3"]
# Na EDA, studytime e failures são tratadas como variáveis ordinais.
VARS_ORDINAIS = ["studytime", "failures"]
ROTULOS = {
    "age": "Idade (age)",
    "absences": "Faltas (absences)",
    "G1": "Nota do 1º período (G1)",
    "G2": "Nota do 2º período (G2)",
    "G3": "Nota final (G3)",
    "studytime": "Faixa de tempo de estudo (studytime)",
    "failures": "Reprovações anteriores (failures)",
}

colunas_necessarias = VARS_QUANT + VARS_ORDINAIS
colunas_ausentes = [coluna for coluna in colunas_necessarias if coluna not in df.columns]
if colunas_ausentes:
    st.error(f"Colunas ausentes no dataset tratado: {', '.join(colunas_ausentes)}.")
    st.stop()

if df.empty:
    st.warning("O dataset tratado está vazio.")
    st.stop()

colunas_invalidas = [
    coluna
    for coluna in colunas_necessarias
    if not pd.api.types.is_numeric_dtype(df[coluna]) or df[coluna].isna().any()
]
if colunas_invalidas:
    st.error(
        "As variáveis precisam ser numéricas e não conter valores ausentes. "
        f"Confira a exportação da EDA: {', '.join(colunas_invalidas)}."
    )
    st.stop()

with st.sidebar:
    st.header("Filtros")
    variaveis = st.multiselect(
        "Variáveis para análise",
        options=colunas_necessarias,
        default=["absences", "studytime", "failures", "G1", "G2", "G3"],
        format_func=ROTULOS.__getitem__,
        help="Selecione variáveis para os futuros gráficos e ajuste seus intervalos.",
    )
    st.caption(
        "studytime é uma escala ordinal: 1 = menos de 2 h/semana; "
        "2 = de 2 a 5 h; 3 = de 5 a 10 h; 4 = mais de 10 h. "
        "As notas G1, G2 e G3 vão de 0 a 20."
    )

    intervalos = {}
    for variavel in variaveis:
        minimo = df[variavel].min().item()
        maximo = df[variavel].max().item()
        if minimo == maximo:
            st.caption(f"{ROTULOS[variavel]}: valor único {minimo}.")
            continue
        passo = 1 if pd.api.types.is_integer_dtype(df[variavel]) else 0.1
        intervalos[variavel] = st.slider(
            f"Intervalo de {ROTULOS[variavel]}",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            key=f"intervalo_{variavel}",
        )

df_filtrado = df
for variavel, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[variavel].between(inicio, fim)]

st.caption(f"{len(df_filtrado)} de {len(df)} alunos dentro dos intervalos escolhidos.")

col_alunos, col_nota, col_aprovacao = st.columns(3)
col_alunos.metric("Alunos no recorte", len(df_filtrado))
col_nota.metric(
    "Nota final média",
    "—" if df_filtrado.empty else f"{df_filtrado['G3'].mean():.2f}",
    help="Média de G3 no grupo filtrado, na escala de 0 a 20.",
)
col_aprovacao.metric(
    "Taxa de aprovação",
    "—" if df_filtrado.empty else f"{df_filtrado['G3'].ge(10).mean():.1%}",
    help="Mesmo critério dos notebooks: aprovado quando G3 é maior ou igual a 10.",
)

if df_filtrado.empty:
    st.warning("Nenhum aluno atende a todos os intervalos. Amplie os filtros.")

with st.container(border=True):
    st.subheader("Correlação (heatmap)")
    st.caption("Método previsto: Spearman, utilizado nos notebooks de EDA.")
    if len(variaveis) < 2:
        st.warning("Selecione pelo menos 2 variáveis para a correlação.")
    elif len(df_filtrado) < 2:
        st.warning("São necessários pelo menos 2 alunos no recorte para a correlação.")
    else:
        # TODO: Implementar heatmap com px.imshow da correlação de Spearman
        # de df_filtrado[variaveis], incluindo absences, studytime e G3.
        st.info(
            "Espaço reservado para o heatmap interativo com Plotly Express. "
            "Ele mostrará as associações entre as variáveis selecionadas."
        )
    st.caption(
        "studytime e failures são ordinais na EDA. "
        "Uma associação com G3 não demonstra causa e efeito."
    )

with st.container(border=True):
    st.subheader("Distribuição (histograma)")
    if not variaveis:
        st.warning("Selecione pelo menos 1 variável para a distribuição.")
    elif df_filtrado.empty:
        st.info("A distribuição será exibida quando houver alunos no recorte.")
    else:
        # TODO: Implementar histogramas com px.histogram para cada variável
        # selecionada em df_filtrado; usar categorias discretas para as ordinais.
        st.info(
            "Espaço reservado para os histogramas interativos com Plotly Express. "
            "Eles mostrarão a frequência de alunos nas variáveis selecionadas."
        )
