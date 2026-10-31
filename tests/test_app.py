import base64
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import pyarrow as pa
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.data_loader import load_data


ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(ROOT / "data" / "clean" / "dataset.csv")

    def run_app(self, app=None):
        if app is None:
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        app.run()
        self.assertFalse(app.exception, [error.message for error in app.exception])
        return app

    def assert_metrics(self, app, expected, offset=1):
        values = [str(len(expected))]
        if offset == 1:
            values = [
                "—" if expected.empty else f"{expected.G3.mean():.2f}",
                "—" if expected.empty else f"{expected.absences.median():.1f}",
                "—" if expected.empty else f"{expected.G3.ge(10).mean():.1%}",
                "—" if expected.empty else f"{expected.G3.lt(10).mean():.1%}",
            ]
            captions = [caption.value for caption in app.caption]
            approved = int(expected.G3.ge(10).sum())
            failed = int(expected.G3.lt(10).sum())
            for label, count in [("Aprovados", approved), ("Reprovados", failed)]:
                percentage = "—" if expected.empty else f"{count / len(expected):.1%}"
                self.assertIn(f"{label}: {count} alunos ({percentage})", captions)
            donuts = [
                chart for chart in app.get("vega_lite_chart")
                if json.loads(chart.proto.spec)["mark"]["type"] == "arc"
            ]
            self.assertEqual(len(donuts), 0 if expected.empty else 1)
            if donuts:
                spec = json.loads(donuts[0].proto.spec)
                self.assertEqual(spec["mark"]["type"], "arc")
                self.assertGreater(spec["mark"]["innerRadius"], 0)
                pd.testing.assert_frame_equal(self.chart_data(donuts[0]), pd.DataFrame({
                    "situacao": ["Aprovado", "Reprovado"],
                    "alunos": [approved, failed],
                    "percentual": [approved / len(expected), failed / len(expected)],
                }))
            counts = [int(expected.studytime.eq(code).sum()) for code in range(1, 5)]
            pd.testing.assert_frame_equal(app.dataframe[0].value, pd.DataFrame({
                "Horas/semana": ["Menos de 2 h", "De 2 a 5 h", "De 5 a 10 h", "Mais de 10 h"],
                "Alunos": counts,
                "Percentual": [
                    "—" if expected.empty else f"{count / len(expected):.1%}"
                    for count in counts
                ],
            }))
        self.assertEqual([metric.value for metric in app.metric][offset:offset + len(values)], values)

    def test_approval_threshold(self):
        sample = self.df.iloc[:2].copy()
        sample["G3"] = [9, 10]
        with patch("src.data_loader.load_data", return_value=sample):
            app = self.run_app()
        self.assert_metrics(app, sample)

    def chart_data(self, chart):
        return pa.ipc.open_stream(chart.proto.datasets[0].data.data).read_all().to_pandas()

    def study_charts(self, app):
        return [
            chart for chart in app.get("vega_lite_chart")
            if json.loads(chart.proto.spec)["mark"]["type"] != "arc"
        ]

    def test_donut_storytelling(self):
        cases = [
            ([10, 10, 10, 9], "número de aprovados é aproximadamente **3,00 vezes** o número de reprovados."),
            ([10, 9, 9, 9], "número de reprovados é aproximadamente **3,00 vezes** o número de aprovados."),
            ([10, 9], "**O número de aprovados é igual ao número de reprovados.**"),
            ([10, 20], "**Todos os alunos do recorte foram aprovados.** Não há reprovados."),
            ([0, 9], "**Todos os alunos do recorte foram reprovados.** Não há aprovados."),
        ]
        for grades, story in cases:
            with self.subTest(grades=grades):
                sample = self.df.iloc[:len(grades)].copy()
                sample["G3"] = grades
                with patch("src.data_loader.load_data", return_value=sample):
                    app = self.run_app()
                self.assert_metrics(app, sample)
                self.assertTrue(any(story in element.value for element in app.markdown))

    def assert_correlations(self, app, expected, variables):
        spec = json.loads(app.get("plotly_chart")[0].proto.spec)
        encoded = spec["data"][0]["z"]
        matrix = np.frombuffer(base64.b64decode(encoded["bdata"]), dtype=encoded["dtype"])
        matrix = matrix.reshape(len(variables), len(variables))
        lower = np.tril_indices(len(variables), k=-1)
        np.testing.assert_allclose(
            matrix[lower],
            expected[variables].corr(method="spearman").to_numpy()[lower],
        )
        self.assertTrue(np.isnan(matrix[np.triu_indices(len(variables))]).all())
        self.assertEqual(np.isfinite(matrix).sum(), len(variables) * (len(variables) - 1) // 2)
        self.assertFalse(spec["data"][0]["hoverongaps"])
        self.assertFalse(spec["data"][0]["connectgaps"])
        self.assertEqual(spec["layout"]["coloraxis"]["cmin"], -1)
        self.assertEqual(spec["layout"]["coloraxis"]["cmax"], 1)

    def test_correlation_triangle_follows_selected_order(self):
        app = self.run_app()
        for variables in [["G3", "G1"], ["G1", "G3"], ["studytime", "absences", "G3"]]:
            with self.subTest(variables=variables):
                app.multiselect(key="variaveis").set_value(variables)
                self.run_app(app)
                self.assert_correlations(app, self.df, variables)
                spec = json.loads(app.get("plotly_chart")[0].proto.spec)
                self.assertEqual(spec["data"][0]["x"], spec["data"][0]["y"])
                for label, variable in zip(spec["data"][0]["x"], variables):
                    self.assertIn(f"({variable})", label)

    def test_initial_charts_and_metrics(self):
        app = self.run_app()
        self.assertEqual(len(app.tabs), 2)
        self.assertEqual(len(app.get("plotly_chart")), 7)
        self.assertEqual(len(app.get("vega_lite_chart")), 4)
        self.assert_metrics(app, self.df, offset=0)
        self.assert_metrics(app, self.df)
        self.assert_correlations(app, self.df, app.multiselect(key="variaveis").value)
        self.assertEqual(self.chart_data(self.study_charts(app)[0]).alunos.sum(), len(self.df))
        self.assertEqual(len(self.chart_data(self.study_charts(app)[1])), len(self.df))
        self.assertEqual(
            [(metric.label, metric.value) for metric in app.tabs[0].get("metric")],
            [("Alunos no recorte", str(len(self.df)))],
        )

    def test_study_bars_stack_outcomes_and_select_whole_range(self):
        app = self.run_app()
        app.slider(key="intervalo_absences").set_value((0, 5))
        app.multiselect(key="escolas").set_value(["GP"])
        self.run_app(app)
        chart = self.study_charts(app)[0]
        spec = json.loads(chart.proto.spec)
        self.assertEqual(spec["mark"]["type"], "bar")
        self.assertEqual(spec["encoding"]["y"]["stack"], "zero")
        self.assertEqual(spec["encoding"]["color"]["field"], "situacao")
        self.assertEqual(spec["encoding"]["color"]["scale"]["domain"], ["Aprovado", "Reprovado"])
        self.assertEqual(spec["params"][0]["select"]["fields"], ["studytime"])
        expected = self.df[self.df.absences.between(0, 5) & self.df.school.eq("GP")]
        summary = self.chart_data(chart)
        self.assertEqual(summary.alunos.sum(), len(expected))
        for code in expected.studytime.unique():
            for outcome in ["Aprovado", "Reprovado"]:
                group = expected[
                    expected.studytime.eq(code) & expected.G3.ge(10).eq(outcome == "Aprovado")
                ]
                segment = summary[summary.studytime.eq(code) & summary.situacao.eq(outcome)]
                self.assertEqual(segment.alunos.sum(), len(group))
                if not group.empty:
                    self.assertAlmostEqual(segment.nota_media.iloc[0], group.G3.mean())
        self.assert_metrics(app, expected)

    def test_metrics_and_visualizations_are_separate(self):
        app = self.run_app()
        blocks = [
            block for block in app.tabs[1].children.values()
            if block.type == "flex_container"
        ]
        self.assertEqual([block.key for block in blocks], ["metricas_kpi", "visualizacoes_kpi"])
        metrics, visuals = blocks
        self.assertEqual(len(metrics.get("metric")), 4)
        self.assertEqual(len(metrics.get("dataframe")), 1)
        self.assertFalse(metrics.get("vega_lite_chart"))
        self.assertFalse(metrics.get("plotly_chart"))
        self.assertEqual(len(visuals.get("vega_lite_chart")), 4)
        self.assertFalse(visuals.get("metric"))
        self.assertTrue(metrics.proto.flex_container.border)
        self.assertTrue(visuals.proto.flex_container.border)
        self.assertEqual(app.sidebar.multiselect(key="escolas").value, ["GP", "MS"])
        self.assertEqual(len(app.tabs[1].get("multiselect")), 0)
        self.assertEqual(len(app.sidebar.button), 1)

    def test_combined_filters_recalculate_both_dashboards(self):
        app = self.run_app()
        app.slider(key="intervalo_absences").set_value((0, 5))
        app.slider(key="intervalo_studytime").set_value((2, 3))
        self.run_app(app)
        expected = self.df[self.df.absences.between(0, 5) & self.df.studytime.between(2, 3)]
        self.assert_metrics(app, expected, offset=0)
        self.assert_metrics(app, expected)
        self.assert_correlations(app, expected, app.multiselect(key="variaveis").value)
        hist = json.loads(app.get("plotly_chart")[1].proto.spec)["data"][0]["x"]
        values = np.frombuffer(base64.b64decode(hist["bdata"]), dtype=hist["dtype"])
        np.testing.assert_array_equal(values, expected.absences)

    def test_kpi_cards_group_each_metric(self):
        app = self.run_app()
        metrics = next(
            block for block in app.tabs[1].get("flex_container")
            if block.key == "metricas_kpi"
        )
        columns = metrics.get("column")
        self.assertEqual(len(columns), 3)
        self.assertEqual(
            [[block.key for block in column.get("flex_container") if block.key]
             for column in columns],
            [
                ["cartao_kpi_media", "cartao_kpi_faltas"],
                ["cartao_kpi_situacao"],
                ["cartao_kpi_estudo"],
            ],
        )
        cards = {
            block.key: block
            for block in app.tabs[1].get("flex_container")
            if block.key and block.key.startswith("cartao_kpi_")
        }
        self.assertEqual(set(cards), {
            "cartao_kpi_situacao", "cartao_kpi_media",
            "cartao_kpi_faltas", "cartao_kpi_estudo",
        })
        self.assertEqual(
            [metric.label for metric in cards["cartao_kpi_situacao"].get("metric")],
            ["Aprovados", "Reprovados"],
        )
        self.assertEqual(
            [metric.label for metric in cards["cartao_kpi_media"].get("metric")],
            ["Média da nota final"],
        )
        self.assertEqual(
            [metric.label for metric in cards["cartao_kpi_faltas"].get("metric")],
            ["Mediana de faltas"],
        )
        self.assertEqual(len(cards["cartao_kpi_estudo"].get("dataframe")), 1)
        for card in cards.values():
            self.assertTrue(card.proto.flex_container.border)
            self.assertFalse(card.get("vega_lite_chart"))
        self.assert_metrics(app, self.df)

    def test_zero_one_and_two_variables(self):
        app = self.run_app()
        for variables, chart_count in [([], 0), (["G3"], 1), (["G3", "absences"], 3)]:
            with self.subTest(variables=variables):
                app.multiselect(key="variaveis").set_value(variables)
                self.run_app(app)
                self.assertEqual(len(app.get("plotly_chart")), chart_count)
                self.assertEqual(len(app.get("vega_lite_chart")), 4)
                self.assert_metrics(app, self.df)
        app.slider(key="intervalo_absences").set_value((0, 0))
        self.run_app(app)
        app.multiselect(key="variaveis").set_value(["G3"])
        self.run_app(app)
        self.assert_metrics(app, self.df, offset=0)

    def test_constant_variables_excluded_only_from_heatmap(self):
        app = self.run_app()
        app.multiselect(key="variaveis").set_value(["absences", "G3"])
        self.run_app(app)
        app.slider(key="intervalo_absences").set_value((0, 0))
        self.run_app(app)
        self.assertEqual(len(app.get("plotly_chart")), 2)
        self.assertTrue(any("constantes" in message.value for message in app.warning))
        self.assert_metrics(app, self.df[self.df.absences.eq(0)])

    def test_empty_filter_result(self):
        app = self.run_app()
        app.multiselect(key="variaveis").set_value(["age", "G3"])
        self.run_app(app)
        app.slider(key="intervalo_age").set_value((22, 22))
        app.slider(key="intervalo_G3").set_value((0, 0))
        self.run_app(app)
        self.assert_metrics(app, self.df.iloc[:0], offset=0)
        self.assert_metrics(app, self.df.iloc[:0])
        self.assertTrue(app.warning)
        self.assertFalse(app.get("plotly_chart"))
        self.assertFalse(app.get("vega_lite_chart"))
        self.assertTrue(any("Sem alunos no recorte para comparar" in message.value for message in app.info))

    def test_school_filter_is_exclusive_and_empty_means_no_students(self):
        app = self.run_app()
        app.multiselect(key="escolas").set_value(["GP"])
        self.run_app(app)
        self.assert_metrics(app, self.df[self.df.school.eq("GP")])
        self.assert_metrics(app, self.df, offset=0)
        app.multiselect(key="escolas").set_value([])
        self.run_app(app)
        self.assert_metrics(app, self.df.iloc[:0])
        self.assertFalse(app.get("vega_lite_chart"))

    def test_selection_payload_filters_metrics_and_both_altair_charts(self):
        original = st.altair_chart
        for faixas in [[1], [1, 3], []]:
            with self.subTest(faixas=faixas):
                def select(chart, **kwargs):
                    result = original(chart, **kwargs)
                    if kwargs.get("on_select") == "rerun":
                        return SimpleNamespace(
                            selection={"faixa_estudo": [{"studytime": value} for value in faixas]}
                        )
                    return result

                # O payload do Vega-Lite é simulado; o clique real é validado no navegador.
                with patch("streamlit.altair_chart", side_effect=select):
                    app = self.run_app()
                expected = self.df[self.df.studytime.isin(faixas)] if faixas else self.df
                self.assert_metrics(app, expected)
                for chart in self.study_charts(app)[1:]:
                    plotted = self.chart_data(chart)
                    pd.testing.assert_frame_equal(
                        plotted[["studytime", "absences", "G3"]].reset_index(drop=True),
                        expected[["studytime", "absences", "G3"]].reset_index(drop=True),
                    )

    def test_filter_changes_and_clear_button_reset_chart_identity(self):
        app = self.run_app()
        revision = app.session_state["revisao_estudo"]
        app.button[0].click()
        self.run_app(app)
        self.assertEqual(app.session_state["revisao_estudo"], revision + 1)
        app.multiselect(key="escolas").set_value(["MS"])
        self.run_app(app)
        self.assertEqual(app.session_state["revisao_estudo"], revision + 2)
        self.assertTrue(self.study_charts(app)[0].proto.id.endswith(f"estudo_{revision + 2}"))

    def test_dataset_errors_are_explicit(self):
        for data in [
            self.df.drop(columns="G3"),
            self.df.assign(G3="invalid"),
            self.df.assign(G3=np.nan),
            self.df.assign(G3=np.inf),
            self.df.assign(studytime=9),
            self.df.assign(school=None),
        ]:
            with self.subTest(columns=data.columns.tolist()):
                with patch("src.data_loader.load_data", return_value=data):
                    app = self.run_app()
                self.assertTrue(app.error)
        with patch("src.data_loader.load_data", side_effect=FileNotFoundError("CSV ausente")):
            app = self.run_app()
        self.assertTrue(app.error)

    def test_empty_and_single_row_dataset(self):
        with patch("src.data_loader.load_data", return_value=self.df.iloc[:0]):
            app = self.run_app()
        self.assertTrue(app.warning)
        with patch("src.data_loader.load_data", return_value=self.df.iloc[:1]):
            app = self.run_app()
        self.assertFalse(app.slider)
        self.assert_metrics(app, self.df.iloc[:1])

    def test_data_loader_caches_reads_and_returns_isolated_data(self):
        load_data.clear()
        try:
            with patch("src.data_loader.pd.read_csv", return_value=self.df.copy()) as read:
                first = load_data("cache-test.csv")
                first.loc[0, "G3"] = -100
                second = load_data("cache-test.csv")
                self.assertEqual(read.call_count, 1)
                self.assertEqual(second.loc[0, "G3"], self.df.loc[0, "G3"])
        finally:
            load_data.clear()


if __name__ == "__main__":
    unittest.main()
