#!/usr/bin/python3

import dash.dependencies
import dash_bootstrap_components as dbc


# bootstrap theme
# https://bootswatch.com/lux/
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True
)
server = app.server
