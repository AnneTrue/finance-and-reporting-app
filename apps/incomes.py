#!/usr/bin/python3

from dash.dependencies import Input, Output, State
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html

from app import app
import apps
import far_core.db


LAYOUT = html.Div(
    [
        apps.NAVBAR,
        dbc.Row(
            [dbc.Col([html.Div("Loading...", id="income_table_div")], width=10)],
            justify="center",
        ),
    ]
)


@app.callback(
    Output("income_table_div", "children"),
    Input("url", "pathname"),
)
def load_incomes(pathname: str):
    if pathname != "/incomes":
        return []
    df = apps.dataframe_from_expense_records(apps.get_all_income_records())
    df.sort_values(by="Date", ascending=False)
    dtable = dash_table.DataTable(
        id="income_datatable",
        columns=[{"name": col, "id": col} for col in df.columns if col != "id"],
        data=df.to_dict("records"),
        filter_action="native",
        row_selectable="multi",
        sort_action="native",
        sort_by=[{"column_id": "Date", "direction": "desc"}],
        fixed_rows={"headers": True, "data": 0},
    )
    return [
        dbc.Alert(
            "Deleting selected rows... Please reload the page to see changes!",
            id="income_alert_auto",
            is_open=False,
            duration=10000,
        ),
        html.Button(
            "Delete", id="income_delete_button", className="btn btn-outline-primary"
        ),
        dtable,
    ]


@app.callback(
    [Output("income_alert_auto", "is_open")],
    Input("income_delete_button", "n_clicks"),
    [State("income_datatable", "selected_row_ids")],
)
def handle_delete_incomes(n_clicks, selected_row_ids):
    if not n_clicks:
        return [False]
    far_core.db.delete_income_records_by_id(selected_row_ids)
    return [True]
