#!/usr/bin/python3

import collections
import datetime
import re

from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from app import app
import apps
import far_core


def get_layout(report_type: str):
    if report_type not in ("annual", "monthly"):
        raise NotImplementedError(f"Unknown report type: {report_type}")
    children = []
    # Date picker
    children.append(
        html.Div(
            children=[
                html.Label(
                    children="Choose month to end report on:",
                    className="col-form-label",
                    htmlFor=f"report_date_picker_{report_type}",
                ),
                dcc.Input(
                    id=f"report_date_picker_{report_type}",
                    className="form-control",
                    debounce=True,
                    type="text",
                    value=far_core.get_current_month().strftime("%Y-%m"),
                    placeholder="Month to end report on, e.g. \"2000-01\"",
                    pattern=r"\d{4}-([1-9]|1[0-2]|0[1-9])",
                ),
            ],
            className="form-group",
        )
    )
    children.append(html.Hr())

    # Categorical Expense Breakdown
    children.append(
        dbc.Table(
            children=[], id=f"categorical_expense_table_{report_type}",
            bordered=True, responsive=True, striped=True,
        )
    )
    return html.Div(
        [
            apps.NAVBAR,
            dbc.Row(
                dbc.Col(
                    children=children, id=f"main_report_col_{report_type}",
                    width=8, align="center",
                ),
                justify="center",
            )
        ]
    )


ANNUAL_LAYOUT = get_layout("annual")
MONTHLY_LAYOUT = get_layout("monthly")


def get_date_from_date_str(date_str: str) -> datetime.date:
    m = re.match(r"(\d{4})-([1-9]|1[0-2]|0[1-9])", date_str)
    if not m:
        return None
    year, month = int(m.group(1)), int(m.group(2))
    return datetime.date(year, month, 1)


def get_categorical_review_table_counter(exp_records: list) -> collections.Counter:
    counter = collections.Counter()
    for record in exp_records:
        counter[record.category] += record.amount
    return counter


def get_categorical_review_table_rows(category_counters: list) -> list:
    cat_rows = []
    for cat in far_core.ExpenseCategory:
        if all(not cat_counter[cat] for cat_counter in category_counters):
            # Skip zero-filled categories
            continue
        cat_rows.append(
            html.Tr(
                [html.Td(str(cat))] + [
                    html.Td(far_core.usd_str(cat_counter[cat]))
                    for cat_counter in category_counters
                ]
            )
        )
    return cat_rows


@app.callback(
    Output("categorical_expense_table_monthly", "children"),
    Input("report_date_picker_monthly", "value"),
)
def categorical_review_table_monthly(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return []
    header_row = [
        html.Thead([
            html.Tr([html.Th("Categorical Expense Review: Monthly", colSpan=4)]),
            html.Tr([
                html.Th("Category"),
                html.Th(far_core.month_delta(end_date, -3).strftime("%Y-%m")),
                html.Th(far_core.month_delta(end_date, -2).strftime("%Y-%m")),
                html.Th(far_core.month_delta(end_date, -1).strftime("%Y-%m")),
            ]),
        ]),
    ]
    category_counters = []
    for month_delta in range(-3, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        category_counters.append(
            get_categorical_review_table_counter(exp_records)
        )
    category_rows = get_categorical_review_table_rows(category_counters)
    header_row.append(html.Tbody(category_rows))
    return header_row


@app.callback(
    Output("categorical_expense_table_annual", "children"),
    Input("report_date_picker_annual", "value"),
)
def categorical_review_table_annual(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return []
    header_row = [
        html.Thead([
            html.Tr([html.Th("Categorical Expense Review: Annual", colSpan=4)]),
            html.Tr([
                html.Th("Category"),
                html.Th(far_core.month_delta(end_date, -13).strftime("%Y-%m")),
                html.Th(far_core.month_delta(end_date, -1).strftime("%Y-%m")),
            ]),
        ]),
    ]
    category_counters = []
    for month_delta in range(-13, 0, 12):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 12)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        category_counters.append(
            get_categorical_review_table_counter(exp_records)
        )
    category_rows = get_categorical_review_table_rows(category_counters)
    header_row.append(html.Tbody(category_rows))
    return header_row
