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

    def assert_metrics(self, app, expected, offset=3):
        values = [
            str(len(expected)),
            "—" if expected.empty else f"{expected.G3.mean():.2f}",
            "—" if expected.empty else f"{expected.G3.ge(10).mean():.1%}",
        ]
        if offset == 3:
            values = [
                "—" if expected.empty else f"{expected.G3.ge(10).mean():.1%}",
                "—" if expected.empty else f"{expected.G3.lt(10).mean():.1%}",
                "—" if expected.empty else f"{expected.G3.mean():.2f}",
                "—" if expected.empty else f"{expected.absences.median():.1f}",
            ]
            captions = [caption.value for caption in app.caption]
            self.assertIn(f"Aprovados: {expected.G3.ge(10).sum()} alunos", captions)
            self.assertIn(f"Reprovados: {expected.G3.lt(10).sum()} alunos", captions)
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

    def assert_correlations(self, app, expected, variables):
        spec = json.loads(app.get("plotly_chart")[0].proto.spec)
        encoded = spec["data"][0]["z"]
        matrix = np.frombuffer(base64.b64decode(encoded["bdata"]), dtype=encoded["dtype"])
        np.testing.assert_allclose(
            matrix.reshape(len(variables), len(variables)),
            expected[variables].corr(method="spearman"),
        )
        self.assertEqual(spec["layout"]["coloraxis"]["cmin"], -1)
        self.assertEqual(spec["layout"]["coloraxis"]["cmax"], 1)

    def test_initial_charts_and_metrics(self):
        app = self.run_app()
        self.assertEqual(len(app.tabs), 2)
        self.assertEqual(len(app.get("plotly_chart")), 7)
        self.assertEqual(len(app.get("vega_lite_chart")), 3)
        self.assert_metrics(app, self.df, offset=0)
        self.assert_metrics(app, self.df)
        self.assert_correlations(app, self.df, app.multiselect(key="variaveis").value)
        self.assertEqual(self.chart_data(app.get("vega_lite_chart")[0]).alunos.sum(), len(self.df))
        self.assertEqual(len(self.chart_data(app.get("vega_lite_chart")[1])), len(self.df))

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

    def test_zero_one_and_two_variables(self):
        app = self.run_app()
        for variables, chart_count in [([], 0), (["G3"], 1), (["G3", "absences"], 3)]:
            with self.subTest(variables=variables):
                app.multiselect(key="variaveis").set_value(variables)
                self.run_app(app)
                self.assertEqual(len(app.get("plotly_chart")), chart_count)
                self.assertEqual(len(app.get("vega_lite_chart")), 3)
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
                for chart in app.get("vega_lite_chart")[1:]:
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
        self.assertTrue(app.get("vega_lite_chart")[0].proto.id.endswith(f"estudo_{revision + 2}"))

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
