#!/usr/bin/python3
"""
Entrypoint for the FaR app docker container, which runs a server on 8080
"""

import logging

import dash.dependencies
import dash_core_components as dcc
import dash_html_components as html

from app import app
import apps.expenses
import apps.incomes
import apps.input
import apps.main
import apps.report
import far_core.db


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/":
        return apps.main.LAYOUT
    elif pathname == "/expenses":
        return apps.expenses.LAYOUT
    elif pathname == "/incomes":
        return apps.incomes.LAYOUT
    elif pathname == "/input":
        return apps.input.LAYOUT
    elif pathname == "/report/annual":
        return apps.report.ANNUAL_LAYOUT
    elif pathname == "/report/monthly":
        return apps.report.MONTHLY_LAYOUT
    else:
        return [
            html.Div(
                [
                    html.H3("The page you're looking for does not exist"),
                    dcc.Link('Back to the main page', href='/')
                ]
            ),
        ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    far_core.db.init_tables()
    app.run_server(host='0.0.0.0', port=8080)
