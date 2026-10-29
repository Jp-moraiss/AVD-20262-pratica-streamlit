import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_data


def limpar_selecao_estudo() -> None:
    st.session_state["revisao_estudo"] += 1


def exibir_metricas(dados: pd.DataFrame, dashboard_kpis: bool = False) -> None:
    if dashboard_kpis:
        col_situacao, col_media, col_faltas, col_estudo = st.columns(4)
        with col_situacao:
            st.markdown("**Taxa de aprovação vs. reprovação**")
            for situacao, quantidade in [
                ("Aprovados", int(dados["G3"].ge(10).sum())),
                ("Reprovados", int(dados["G3"].lt(10).sum())),
            ]:
                st.metric(
                    situacao,
                    "—" if dados.empty else f"{quantidade / len(dados):.1%}",
                )
                st.caption(f"{situacao}: {quantidade} alunos")
        col_media.metric(
            "Média da nota final",
            "—" if dados.empty else f"{dados['G3'].mean():.2f}",
        )
        col_faltas.metric(
            "Mediana de faltas",
            "—" if dados.empty else f"{dados['absences'].median():.1f}",
        )
        with col_estudo:
            st.markdown("**Tempo de estudo semanal (extra-classe)**")
            quantidades = dados["studytime"].value_counts().reindex(list(FAIXAS_ESTUDO), fill_value=0)
            st.dataframe(
                pd.DataFrame({
                    "Horas/semana": [rotulo.split(" · ", 1)[1] for rotulo in FAIXAS_ESTUDO.values()],
                    "Alunos": quantidades.to_list(),
                    "Percentual": [
                        "—" if dados.empty else f"{quantidade / len(dados):.1%}"
                        for quantidade in quantidades
                    ],
                }),
                hide_index=True,
                width="stretch",
            )
        return

    colunas = st.columns(3)
    colunas[0].metric("Alunos no recorte", len(dados))
    colunas[1].metric(
        "Nota final média",
        "—" if dados.empty else f"{dados['G3'].mean():.2f}",
        help="Média de G3 no grupo filtrado, na escala de 0 a 20.",
    )
    colunas[2].metric(
        "Taxa de aprovação",
        "—" if dados.empty else f"{dados['G3'].ge(10).mean():.1%}",
        help="Alunos com G3 >= 10 divididos pelo total de alunos do recorte.",
    )


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
FAIXAS_ESTUDO = {
    1: "1 · Menos de 2 h",
    2: "2 · De 2 a 5 h",
    3: "3 · De 5 a 10 h",
    4: "4 · Mais de 10 h",
}
COR_DESTAQUE = "#7541a0"
CORES_SITUACAO = alt.Scale(
    domain=["Aprovado", "Reprovado"],
    range=["#d98db3", COR_DESTAQUE],
)

colunas_necessarias = VARS_QUANT + VARS_ORDINAIS
colunas_ausentes = [
    coluna for coluna in colunas_necessarias + ["school"] if coluna not in df.columns
]
if colunas_ausentes:
    st.error(f"Colunas ausentes no dataset tratado: {', '.join(colunas_ausentes)}.")
    st.stop()

if df.empty:
    st.warning("O dataset tratado está vazio.")
    st.stop()

colunas_invalidas = [
    coluna
    for coluna in colunas_necessarias
    if (
        not pd.api.types.is_numeric_dtype(df[coluna])
        or df[coluna].isna().any()
        or df[coluna].isin([float("inf"), float("-inf")]).any()
    )
]
if colunas_invalidas:
    st.error(
        "As variáveis precisam ser numéricas, finitas e não conter valores ausentes. "
        f"Confira a exportação da EDA: {', '.join(colunas_invalidas)}."
    )
    st.stop()

if df["school"].isna().any() or not df["studytime"].isin(FAIXAS_ESTUDO).all():
    st.error("Confira a EDA: school não pode ser ausente e studytime deve estar entre 1 e 4.")
    st.stop()

st.session_state.setdefault("revisao_estudo", 0)

with st.sidebar:
    st.header("Filtros")
    st.caption("Os intervalos abaixo filtram as duas abas.")
    variaveis = st.multiselect(
        "Variáveis para análise",
        options=colunas_necessarias,
        default=["absences", "studytime", "failures", "G1", "G2", "G3"],
        key="variaveis",
        format_func=ROTULOS.__getitem__,
        help="Escolha as variáveis do Dashboard 1 e os intervalos usados nas duas abas.",
        on_change=limpar_selecao_estudo,
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
            on_change=limpar_selecao_estudo,
        )

df_filtrado = df
for variavel, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[variavel].between(inicio, fim)]

st.caption(f"{len(df_filtrado)} de {len(df)} alunos dentro dos intervalos escolhidos.")

if df_filtrado.empty:
    st.warning("Nenhum aluno atende a todos os intervalos. Amplie os filtros.")

aba_exploracao, aba_kpis = st.tabs(["Dashboard 1 — Exploração", "Dashboard 2 — KPIs"])

with aba_exploracao:
    exibir_metricas(df_filtrado)
    with st.container(border=True):
        st.subheader("Correlação (heatmap)")
        st.caption("Correlação de Spearman, como nos notebooks de EDA.")
        if len(variaveis) < 2:
            st.warning("Selecione pelo menos 2 variáveis para a correlação.")
        elif len(df_filtrado) < 2:
            st.warning("São necessários pelo menos 2 alunos no recorte para a correlação.")
        else:
            constantes = [var for var in variaveis if df_filtrado[var].nunique() < 2]
            validas = [var for var in variaveis if var not in constantes]
            if constantes:
                st.warning(
                    "Sem correlação definida para variáveis constantes no recorte: "
                    + ", ".join(ROTULOS[var] for var in constantes)
                    + ". Elas foram excluídas apenas do heatmap."
                )
            if len(validas) < 2:
                st.info("Amplie os intervalos para ter pelo menos 2 variáveis não constantes.")
            else:
                correlacao = df_filtrado[validas].corr(method="spearman")
                heatmap = px.imshow(
                    correlacao.rename(index=ROTULOS, columns=ROTULOS),
                    text_auto=True,
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    aspect="auto",
                    labels={"color": "Spearman"},
                )
                heatmap.update_traces(texttemplate="%{z:.2f}")
                heatmap.update_layout(height=430, margin=dict(t=20, b=20))
                st.plotly_chart(heatmap, width="stretch", key="correlacao")
        st.caption(
            "studytime e failures são ordinais na EDA. "
            "Uma associação com G3 não demonstra causa e efeito."
        )

    with st.container(border=True):
        st.subheader("Distribuição (histogramas)")
        if not variaveis:
            st.warning("Selecione pelo menos 1 variável para a distribuição.")
        elif df_filtrado.empty:
            st.info("A distribuição será exibida quando houver alunos no recorte.")
        else:
            for inicio in range(0, len(variaveis), 2):
                for coluna, variavel in zip(st.columns(2), variaveis[inicio : inicio + 2]):
                    histograma = px.histogram(
                        df_filtrado,
                        x=variavel,
                        labels=ROTULOS,
                        title=ROTULOS[variavel],
                        color_discrete_sequence=[COR_DESTAQUE],
                    )
                    if variavel in VARS_ORDINAIS:
                        histograma.update_xaxes(
                            type="category",
                            categoryorder="array",
                            categoryarray=sorted(df_filtrado[variavel].unique().tolist()),
                        )
                        if variavel == "studytime":
                            histograma.update_xaxes(
                                tickvals=list(FAIXAS_ESTUDO),
                                ticktext=list(FAIXAS_ESTUDO.values()),
                            )
                    else:
                        histograma.update_traces(xbins=dict(size=1))
                    histograma.update_layout(
                        height=300, yaxis_title="Alunos", bargap=0.1,
                    )
                    with coluna:
                        st.plotly_chart(histograma, width="stretch", key=f"hist_{variavel}")

with aba_kpis:
    st.subheader("Acompanhamento do desempenho escolar")
    st.caption(
        "Filtros da sidebar + escola + seleção nas barras de estudo. "
        "Filtrar G3 altera diretamente a média e a aprovação."
    )
    escolas = st.multiselect(
        "Escolas",
        options=sorted(df["school"].unique().tolist()),
        default=sorted(df["school"].unique().tolist()),
        key="escolas",
        on_change=limpar_selecao_estudo,
        help="Este filtro afeta apenas o Dashboard 2. Sem escolas, o recorte fica vazio.",
    )
    st.button("Limpar seleção do gráfico", on_click=limpar_selecao_estudo)
    dados_escolas = df_filtrado[df_filtrado["school"].isin(escolas)]
    # O espaço mantém os KPIs acima do gráfico que fornece a seleção no mesmo rerun.
    espaco_metricas = st.container()
    dados_selecionados = dados_escolas

    if dados_escolas.empty:
        st.warning("Nenhum aluno nas escolas e intervalos selecionados.")
    else:
        st.markdown("#### Alunos por faixa de estudo")
        st.caption(
            "Clique em uma barra para filtrar os KPIs e os gráficos abaixo. "
            "Use Shift + clique para várias faixas; dê duplo clique ou use o botão para limpar. "
            "As barras sempre mostram o recorte anterior à seleção."
        )
        resumo_estudo = (
            dados_escolas.groupby("studytime", as_index=False)
            .agg(alunos=("G3", "size"), nota_media=("G3", "mean"))
            .assign(faixa_estudo=lambda dados: dados["studytime"].map(FAIXAS_ESTUDO))
        )
        clique = alt.selection_point(
            name="faixa_estudo", fields=["studytime"], clear="dblclick",
        )
        barras = (
            alt.Chart(resumo_estudo)
            .mark_bar(color=COR_DESTAQUE)
            .encode(
                x=alt.X(
                    "faixa_estudo:N", title="Estudo semanal",
                    sort=list(FAIXAS_ESTUDO.values()), axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y("alunos:Q", title="Alunos", axis=alt.Axis(tickMinStep=1)),
                opacity=alt.condition(clique, alt.value(1), alt.value(0.3)),
                tooltip=[
                    alt.Tooltip("studytime:O", title="Código"),
                    alt.Tooltip("faixa_estudo:N", title="Estudo semanal"),
                    alt.Tooltip("alunos:Q", title="Alunos"),
                    alt.Tooltip("nota_media:Q", title="Nota final média", format=".2f"),
                ],
            )
            .add_params(clique)
            .properties(height=250)
        )
        evento = st.altair_chart(
            barras,
            key=f"estudo_{st.session_state['revisao_estudo']}",
            on_select="rerun",
            selection_mode=["faixa_estudo"],
            width="stretch",
        )
        faixas = [item["studytime"] for item in evento.selection.get("faixa_estudo", [])]
        if faixas:
            dados_selecionados = dados_escolas[dados_escolas["studytime"].isin(faixas)]
            st.caption("Faixas selecionadas: " + ", ".join(FAIXAS_ESTUDO[faixa] for faixa in faixas))
        else:
            st.caption("Sem seleção nas barras: todas as faixas do recorte estão incluídas.")

    with espaco_metricas:
        exibir_metricas(dados_selecionados, dashboard_kpis=True)
        st.caption(
            f"{len(dados_selecionados)} de {len(dados_escolas)} alunos do recorte "
            "de escolas após a seleção de estudo."
        )

    if dados_selecionados.empty:
        st.info("Não há dados para os gráficos de desempenho. Ajuste os filtros ou limpe a seleção.")
    else:
        dados_graficos = dados_selecionados.assign(
            situacao=dados_selecionados["G3"].ge(10).map({True: "Aprovado", False: "Reprovado"}),
        )
        col_notas, col_faltas = st.columns(2)
        with col_notas:
            st.markdown("#### Distribuição das notas finais")
            notas = (
                alt.Chart(dados_graficos)
                .mark_bar()
                .encode(
                    x=alt.X("G3:Q", bin=alt.Bin(step=1), title="Nota final (G3)"),
                    y=alt.Y("count():Q", title="Alunos", axis=alt.Axis(tickMinStep=1)),
                    color=alt.Color("situacao:N", title="Situação", scale=CORES_SITUACAO),
                    tooltip=[
                        alt.Tooltip("G3:Q", bin=alt.Bin(step=1), title="Nota final"),
                        alt.Tooltip("situacao:N", title="Situação"),
                        alt.Tooltip("count():Q", title="Alunos"),
                    ],
                )
                .properties(height=300)
            )
            st.altair_chart(notas, key="notas_kpi", width="stretch")
        with col_faltas:
            st.markdown("#### Faltas × nota final")
            dispersao = (
                alt.Chart(dados_graficos)
                .mark_circle(size=70, opacity=0.6)
                .encode(
                    x=alt.X("absences:Q", title="Faltas"),
                    y=alt.Y("G3:Q", title="Nota final (G3)", scale=alt.Scale(domain=[0, 20])),
                    color=alt.Color("situacao:N", title="Situação", scale=CORES_SITUACAO),
                    tooltip=[
                        alt.Tooltip("school:N", title="Escola"),
                        alt.Tooltip("absences:Q", title="Faltas"),
                        alt.Tooltip("G3:Q", title="Nota final"),
                        alt.Tooltip("studytime:O", title="Faixa de estudo (1–4)"),
                        alt.Tooltip("situacao:N", title="Situação"),
                    ],
                )
                .properties(height=300)
                .interactive()
            )
            st.altair_chart(dispersao, key="faltas_kpi", width="stretch")
        st.caption(
            "Um ponto representa um aluno; pontos iguais podem se sobrepor. "
            "A amostra e seus recortes não demonstram relações de causa e efeito."
        )
