#!/usr/bin/python3

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
import apps
import apps.report
import far_core


LAYOUT = html.Div([
    apps.NAVBAR,
    dbc.Row(
        dbc.Col(
            children=[
                dbc.Table(
                    children=[], id="main_page_categorical_expenses",
                    bordered=True, responsive=True, striped=True,
                ),
                dbc.Table(
                    children=[], id="main_page_categorical_incomes",
                    bordered=True, responsive=True, striped=True,
                ),
            ],
            id="main_page_col",
            width=6, align="center",
        ),
        justify="center",
    )
])


@app.callback(
    Output("main_page_categorical_expenses", "children"),
    Input("url", "pathname"),
)
def main_page_categorical_expenses(pathname):
    if pathname != "/":
        return []
    start_date = far_core.get_current_month()
    end_date = far_core.month_delta(start_date, 1)
    table_rows = [
        html.Thead([
            html.Tr([html.Th("Categorical Expense Review: Current Month", colSpan=2)]),
            html.Tr([
                html.Th("Category"),
                html.Th(start_date.strftime("%Y-%m")),
            ]),
        ]),
    ]
    category_counters = []
    exp_records = apps.get_filtered_expense_records(
        end_date=end_date, start_date=start_date
    )
    category_counters.append(
        apps.report.get_category_counter(exp_records)
    )
    category_rows = apps.report.get_categorical_review_table_expense_rows(category_counters)
    table_rows.append(html.Tbody(category_rows))
    return table_rows


@app.callback(
    Output("main_page_categorical_incomes", "children"),
    Input("url", "pathname"),
)
def main_page_categorical_incomes(pathname):
    if pathname != "/":
        return []
    start_date = far_core.get_current_month()
    end_date = far_core.month_delta(start_date, 1)
    table_rows = [
        html.Thead([
            html.Tr([html.Th("Categorical Income Review: Current Month", colSpan=2)]),
            html.Tr([
                html.Th("Category"),
                html.Th(start_date.strftime("%Y-%m")),
            ]),
        ]),
    ]
    category_counters = []
    inc_records = apps.get_filtered_income_records(
        end_date=end_date, start_date=start_date
    )
    category_counters.append(
        apps.report.get_category_counter(inc_records)
    )
    category_rows = apps.report.get_categorical_review_table_income_rows(
        category_counters
    )
    table_rows.append(html.Tbody(category_rows))
    return table_rows
