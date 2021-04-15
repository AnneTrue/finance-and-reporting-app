#!/usr/bin/python3

from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app
import apps


LAYOUT = html.Div([
    apps.NAVBAR,
    dbc.Row(
        [
            dbc.Col(
                [html.Div("Loading...", id="income_table_div")],
                width=10
            )
        ],
        justify="center")
])


@app.callback(
    Output("income_table_div", "children"),
    Input("url", "pathname"),
)
def load_incomes(pathname: str):
    if pathname != "/incomes":
        return []
    df = apps.dataframe_from_expense_records(apps.get_all_income_records())
    dtable = dash_table.DataTable(
        id="income_datatable",
        columns=[
            {"name": col, "id": col} for col in df.columns
        ],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        fixed_rows={"headers": True, "data": 0},
    )
    return dtable
