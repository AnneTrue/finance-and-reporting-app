#!/usr/bin/python3

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import apps


LAYOUT = html.Div([
    apps.NAVBAR,
    html.H3('INCOMES PAGE'),
])
