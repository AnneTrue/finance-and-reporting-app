#!/usr/bin/python3
"""
Globally shared app references, namely the dash app, the flask server,
and the database.
"""

import dash.dependencies
import dash_bootstrap_components as dbc
import flask_sqlalchemy


# bootstrap theme
# https://bootswatch.com/flatly/
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)
server = app.server
server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"  # TODO /data
db = flask_sqlalchemy.SQLAlchemy(server)
