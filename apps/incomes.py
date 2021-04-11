#!/usr/bin/python3

from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd

from app import app, db
import apps


def get_layout():
    return html.Div([
        apps.NAVBAR,
        html.Div(id="income_table_div"),
    ])


LAYOUT = get_layout()


@app.callback(
    Output("income_table_div", "children"),
    Input("url", "pathname"),
)
def load_incomes(pathname):
    if pathname != "/incomes":
        return []
    df = pd.read_sql_query(
        "SELECT * FROM income_record", db.engine  # , parse_dates=["date"]
    )
    dtable = dash_table.DataTable(
        id="income_datatable",
        columns=[
            {"name": col, "id": col}
            for col in df.columns if col != "income_id"
        ],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native"
    )
    return dbc.Row([
        dbc.Col([dtable], width=10)
    ], justify="center")
