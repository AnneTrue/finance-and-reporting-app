#!/usr/bin/python3

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import statsmodels.tsa.api

from app import app
import apps
import far_core


LAYOUT = html.Div(
    [
        apps.NAVBAR,
        dbc.Row(
            dbc.Col(
                children=[
                    html.Div(
                        children=[
                            html.Label(
                                children="Choose month to end forecast on:",
                                className="col-form-label",
                                htmlFor="report_date_picker_forecast",
                            ),
                            dcc.Input(
                                id="report_date_picker_forecast",
                                className="form-control",
                                debounce=True,
                                type="text",
                                value=far_core.get_current_month().strftime("%Y-%m"),
                                placeholder='Month to end forecast on, e.g. "2000-01"',
                                pattern=r"\d{4}-([1-9]|1[0-2]|0[1-9])",
                            ),
                            html.Label(
                                children="Category for forecast:",
                                className="col-form-label",
                                htmlFor="report_category_picker_forecast",
                            ),
                            dcc.Dropdown(
                                id="report_category_picker_forecast",
                                options=[
                                    {"label": str(cat), "value": str(cat)}
                                    for cat in far_core.ExpenseCategory
                                ],
                                placeholder="Category",
                            ),
                            html.Label(
                                children="Seasonality",
                                className="col-form-label",
                                htmlFor="report_seasonality_forecast",
                            ),
                            dcc.Input(
                                id="report_seasonality_forecast",
                                value=2,
                                type="number",
                                className="form-control",
                            ),
                        ],
                        className="form-group",
                    ),
                    html.Hr(),
                    dcc.Graph(id="categorical_forecast_graph"),
                    html.Hr(),
                ],
                width=8,
                align="center",
            ),
            justify="center",
        ),
    ]
)


@app.callback(
    Output("categorical_forecast_graph", "figure"),
    [
        Input("report_date_picker_forecast", "value"),
        Input("report_category_picker_forecast", "value"),
        Input("report_seasonality_forecast", "value"),
    ],
)
def categorical_forecast_graph(date_str: str, category_str: str, seasonality):
    end_date = far_core.get_date_from_date_str(date_str)
    if not end_date or seasonality > 12 or seasonality < 2:
        return {"data": []}
    try:
        category = far_core.ExpenseCategory(category_str)
    except ValueError:
        return {"data": []}
    data = []
    months = []
    for month_delta in range(-(12 * 2) - 1, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        data.append(
            float(
                far_core.sum_all_records(
                    apps.get_filtered_expense_records(
                        category=category,
                        end_date=month_slice_end,
                        start_date=month_slice_start,
                    )
                )
            )
        )
    series = pd.Series(data, index=months)
    fit = statsmodels.tsa.api.ExponentialSmoothing(
        series,
        seasonal_periods=seasonality,
        trend="add",
        seasonal="add",
        initialization_method="estimated",
    ).fit()
    fitted_vals = fit.fittedvalues
    forecast = fit.forecast(3)
    df = pd.concat([series, fitted_vals, forecast], axis=1)
    df.columns = ["Actual", "Fitted", "Forecast"]
    df["Fitted"] = df["Fitted"].clip(lower=0.0)
    df["Forecast"] = df["Forecast"].clip(lower=0.0)
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title=f"Forecast for {str(category)}",
        labels={
            "index": "Month",
            "value": "Spending (USD)",
            "variable": "",
        },
    )
