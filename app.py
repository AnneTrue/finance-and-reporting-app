#!/usr/bin/python3
"""
Globally shared app references, namely the dash app, the flask server,
and the database.
"""

import dash.dependencies
import dash_bootstrap_components as dbc
import flask_caching
import flask_sqlalchemy


# bootstrap theme
# https://bootswatch.com/flatly/
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)
server = app.server
server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/far_app_data.db"
db = flask_sqlalchemy.SQLAlchemy(server)
cache = flask_caching.Cache()
cache.init_app(
    server,
    config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "/tmp/far_app_cache"},
)
