#!/usr/bin/python3
"""
Entrypoint for the FaR app docker container, which runs a server on 8080
"""

import dash.dependencies
import dash_core_components as dcc
import dash_html_components as html

from app import app
import apps.main


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
    else:
        return [html.Div([html.H3("The page you're looking for does not exist")])]


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8080)
