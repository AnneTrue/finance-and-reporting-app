#!/usr/bin/python3

import collections
import decimal

from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px

from app import app
import apps
import far_core
from far_core import get_date_from_date_str


def get_layout(report_type: str):
    if report_type not in ("annual", "monthly"):
        raise NotImplementedError(f"Unknown report type: {report_type}")
    children = []
    # Date picker
    children.append(
        html.Div(
            children=[
                html.Label(
                    children=f"Choose month to end {report_type} report on:",
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

    # Executive Summary
    if report_type == "monthly":
        children.append(
            html.Div(
                id=f"executive_summary_{report_type}",
                className="card text-white bg-primary mb-3",
                children=[
                    html.Div(
                        id=f"executive_summary_header_{report_type}",
                        className="card-header",
                    ),
                    html.Div(
                        id=f"executive_summary_text_{report_type}",
                        className="card-body",
                    )
                ],
            )
        )
        children.append(html.Hr())

    # Cash-flow Review Graph
    children.append(dcc.Graph(id=f"cash_flow_review_graph_{report_type}"))
    children.append(html.Hr())

    # KPI Graph
    children.append(dcc.Graph(id=f"kpi_graph_{report_type}"))
    children.append(html.Hr())

    # Categorical Expense Breakdown
    children.append(
        dbc.Table(
            children=[], id=f"categorical_expense_table_{report_type}",
            bordered=True, responsive=True, striped=True,
        )
    )

    # Discretionary Spending Review Graph
    children.append(dcc.Graph(
        id=f"discretionary_spending_review_graph_{report_type}"
    ))
    children.append(html.Hr())

    # Expense & Income breakdown
    if report_type == "monthly":
        children.append(
            html.Div("Loading table...", id="expense_breakdown_monthly_div")
        )
        children.append(html.Hr())
        children.append(
            html.Div("Loading table...", id="income_breakdown_monthly_div")
        )
        children.append(html.Hr())
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


@app.callback(
    [
        Output("executive_summary_header_monthly", "children"),
        Output("executive_summary_text_monthly", "children"),
    ],
    Input("report_date_picker_monthly", "value"),
)
def executive_summary_monthly(date_str: str) -> tuple:
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return ["No summary..."], [f"No summary available for {date_str}"]
    start_date = far_core.month_delta(end_date, -1)
    exp_records = apps.get_filtered_expense_records(
        end_date=end_date, start_date=start_date,
    )
    inc_records = apps.get_filtered_income_records(
        end_date=end_date, start_date=start_date,
    )
    total_expenses = far_core.sum_all_records(exp_records)
    total_income = far_core.sum_all_records(inc_records)
    net_cashflow = total_income - total_expenses
    header_children = []
    if net_cashflow > 0:
        header_children.append(html.H4("Executive Summary: Net Positive!"))
    else:
        header_children.append(html.H4("Executive Summary: Negative..."))
    text_children = []
    text_children.append(html.P(
        "Summary for the month of {}".format(start_date.strftime("%Y-%m")),
        className="card-text",
    ))
    text_children.append(html.P(
        f"Net Cashflow: {far_core.usd_str(net_cashflow)}",
        className="card-text",
    ))
    text_children.append(html.P(
        f"Total Income: {far_core.usd_str(total_income)}",
        className="card-text",
    ))
    text_children.append(html.P(
        f"Total Expenses: {far_core.usd_str(total_expenses)}",
        className="card-text",
    ))
    return header_children, text_children


def get_category_counter(records: list) -> collections.Counter:
    counter = collections.Counter()
    for record in records:
        counter[record.category] += record.amount
    return counter


def get_categorical_review_table_expense_rows(category_counters: list) -> list:
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


def get_categorical_review_table_income_rows(category_counters: list) -> list:
    cat_rows = []
    for cat in far_core.IncomeCategory:
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
    table_rows = [
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
            get_category_counter(exp_records)
        )
    category_rows = get_categorical_review_table_expense_rows(category_counters)
    table_rows.append(html.Tbody(category_rows))
    return table_rows


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
                html.Th(
                    "Year ending on {}".format(
                        far_core.month_delta(end_date, -12).strftime("%Y-%m")
                    )
                ),
                html.Th(
                    "Year ending on {}".format(end_date.strftime("%Y-%m"))
                ),
            ]),
        ]),
    ]
    category_counters = []
    for month_delta in range(-25, -12, 12):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 12)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        category_counters.append(
            get_category_counter(exp_records)
        )
    category_rows = get_categorical_review_table_expense_rows(category_counters)
    header_row.append(html.Tbody(category_rows))
    return header_row


def get_reduced_category_counter(
        exp_records: list
) -> collections.Counter:
    """
    :return: a collections.Counter with keys of far_core.ReducedCategory and
        value of the sum of expenses in that reduced category from exp_records.
    """
    counter = collections.Counter()
    for record in exp_records:
        counter[record.category.reduced_category] += record.amount
    return counter


@app.callback(
    Output("cash_flow_review_graph_monthly", "figure"),
    Input("report_date_picker_monthly", "value"),
)
def cash_flow_review_graph_monthly(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return {"data": []}
    months = []
    reduced_category_counters = []
    incomes = []
    for month_delta in range(-13, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        reduced_category_counters.append(
            get_reduced_category_counter(exp_records)
        )
        inc_records = apps.get_filtered_income_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        month_income = 0.0
        for inc_record in inc_records:
            month_income += float(inc_record.amount)
        incomes.append(month_income)
    df = pd.DataFrame(index=months)
    colours = []
    for red_cat in far_core.ReducedCategory:
        df[str(red_cat)] = [
            float(cntr[red_cat]) for cntr in reduced_category_counters
        ]
        colours.append(red_cat.colour)
    df["Income"] = incomes
    colours.append("black")
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title="Monthly Cash Flow Review",
        color_discrete_sequence=colours,
        labels={
            "index": "Month",
            "value": "Spending (USD)",
            "variable": "Category"
        },
    )


@app.callback(
    Output("cash_flow_review_graph_annual", "figure"),
    Input("report_date_picker_annual", "value"),
)
def cash_flow_review_graph_annual(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return {"data": []}
    months = []
    reduced_category_counters = []
    incomes = []
    for month_delta in range((-12 * 3) - 1, 0):  # Three years
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        reduced_category_counters.append(
            get_reduced_category_counter(exp_records)
        )
        inc_records = apps.get_filtered_income_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        month_income = 0.0
        for inc_record in inc_records:
            month_income += float(inc_record.amount)
        incomes.append(month_income)
    df = pd.DataFrame(index=months)
    colours = []
    for red_cat in far_core.ReducedCategory:
        df[str(red_cat)] = [
            float(cntr[red_cat]) for cntr in reduced_category_counters
        ]
        colours.append(red_cat.colour)
    df["Income"] = incomes
    colours.append("black")
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title="Annual Cash Flow Review",
        color_discrete_sequence=colours,
        labels={
            "index": "Month",
            "value": "Spending (USD)",
            "variable": "Category"
        },
    )


@app.callback(
    Output("discretionary_spending_review_graph_monthly", "figure"),
    Input("report_date_picker_monthly", "value"),
)
def discretionary_spending_review_graph_monthly(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return {"data": []}
    months = []
    account_counters = []
    for month_delta in range(-13, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        account_counter = collections.Counter()
        for exp_record in exp_records:
            if exp_record.category.reduced_category is far_core.ReducedCategory.fun:
                account_counter[exp_record.account] += exp_record.amount
        account_counters.append(account_counter)
    df = pd.DataFrame(index=months)
    colours = []
    for account in far_core.Accounts:
        df[str(account)] = [
            float(cntr[account]) for cntr in account_counters
        ]
        colours.append(account.colour)
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title="Discretionary Spending Review",
        color_discrete_sequence=colours,
        labels={
            "index": "Month",
            "value": "Spending (USD)",
            "variable": "Account"
        },
    )


@app.callback(
    Output("discretionary_spending_review_graph_annual", "figure"),
    Input("report_date_picker_annual", "value"),
)
def discretionary_spending_review_graph_annual(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return {"data": []}
    months = []
    account_counters = []
    for month_delta in range(-(12 * 3) - 1, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        account_counter = collections.Counter()
        for exp_record in exp_records:
            if exp_record.category.reduced_category is far_core.ReducedCategory.fun:
                account_counter[exp_record.account] += exp_record.amount
        account_counters.append(account_counter)
    df = pd.DataFrame(index=months)
    colours = []
    for account in far_core.Accounts:
        df[str(account)] = [
            float(cntr[account]) for cntr in account_counters
        ]
        colours.append(account.colour)
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title="Discretionary Spending Review",
        color_discrete_sequence=colours,
        labels={
            "index": "Month",
            "value": "Spending (USD)",
            "variable": "Account"
        },
    )


def get_discretionary_rate(exp_records: list) -> decimal.Decimal:
    """
    :param List[far_core.db.ExpenseRecord] exp_records: window of expenses
    :return: the discretionary rate over the window, which is defined as
        (discretionary expenses / total non-asset & non-misc spending).
    """
    total_expense = decimal.Decimal(0)
    total_discretionary = decimal.Decimal(0)
    for exp_record in exp_records:
        if exp_record.category.reduced_category in (
            far_core.ReducedCategory.fun, far_core.ReducedCategory.mandatory,
            far_core.ReducedCategory.debt,
        ):
            total_expense += exp_record.amount
        if exp_record.category.reduced_category is far_core.ReducedCategory.fun:
            total_discretionary += exp_record.amount
    return (
        total_discretionary / total_expense if total_expense else total_expense
    )  # avoid zero division


def get_savings_rate(exp_records: list, inc_records: list) -> decimal.Decimal:
    """
    :param List[far_core.db.ExpenseRecord] exp_records: window of expenses
    :param List[far_core.db.IncomeRecord] inc_records: window of incomes
    :return: the savings rate over the window, which is defined as:
        (income - expenses) / income.
    """
    total_expense = decimal.Decimal(0)
    total_income = far_core.sum_all_records(inc_records)
    for exp_record in exp_records:
        if exp_record.category.reduced_category in (
            far_core.ReducedCategory.fun, far_core.ReducedCategory.mandatory,
            far_core.ReducedCategory.debt,
        ):
            total_expense += exp_record.amount
    return (
        (total_income - total_expense) / total_income
        if total_income else total_income  # avoid zero division error
    )


@app.callback(
    Output("kpi_graph_monthly", "figure"),
    Input("report_date_picker_monthly", "value"),
)
def kpi_graph_monthly(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return {"data": []}
    months = []
    savings_rates = []
    discretionary_rates = []
    for month_delta in range(-13, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        inc_records = apps.get_filtered_income_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        discretionary_rates.append(get_discretionary_rate(exp_records))
        savings_rates.append(
            get_savings_rate(exp_records=exp_records, inc_records=inc_records)
        )
    df = pd.DataFrame(index=months)
    df["Savings Rate"] = savings_rates
    df["Discretionary Rate"] = discretionary_rates
    colours = ["green", "red"]
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title="Key Performance Indicators",
        color_discrete_sequence=colours,
        labels={
            "index": "Month",
            "value": "",
            "variable": "KPI"
        },
    )


@app.callback(
    Output("kpi_graph_annual", "figure"),
    Input("report_date_picker_annual", "value"),
)
def kpi_graph_annual(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return {"data": []}
    months = []
    savings_rates = []
    discretionary_rates = []
    for month_delta in range(-(12 * 3) - 1, 0):
        month_slice_start = far_core.month_delta(end_date, month_delta)
        month_slice_end = far_core.month_delta(end_date, month_delta + 1)
        months.append(month_slice_start)
        inc_records = apps.get_filtered_income_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        exp_records = apps.get_filtered_expense_records(
            end_date=month_slice_end, start_date=month_slice_start
        )
        discretionary_rates.append(get_discretionary_rate(exp_records))
        savings_rates.append(
            get_savings_rate(exp_records=exp_records, inc_records=inc_records)
        )
    df = pd.DataFrame(index=months)
    df["Savings Rate"] = savings_rates
    df["Discretionary Rate"] = discretionary_rates
    colours = ["green", "red"]
    return px.line(
        df,
        x=df.index,
        y=df.columns,
        title="Key Performance Indicators",
        color_discrete_sequence=colours,
        labels={
            "index": "Month",
            "value": "",
            "variable": "KPI"
        },
    )


@app.callback(
    Output("expense_breakdown_monthly_div", "children"),
    Input("report_date_picker_monthly", "value"),
)
def load_expenses(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return ["Loading table..."]
    start_date = far_core.month_delta(end_date, -1)
    df = apps.dataframe_from_expense_records(
        apps.get_filtered_expense_records(
            end_date=end_date, start_date=start_date,
        )
    )
    dtable = dash_table.DataTable(
        id="expense_breakdown_table",
        columns=[
            {"name": col, "id": col} for col in df.columns if col != 'id'
        ],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        sort_by=[{"column_id": "Date", "direction": "asc"}],
        fixed_rows={"headers": True, "data": 0},
    )
    return dtable


@app.callback(
    Output("income_breakdown_monthly_div", "children"),
    Input("report_date_picker_monthly", "value"),
)
def load_incomes(date_str: str):
    end_date = get_date_from_date_str(date_str)
    if not end_date:
        return ["Loading table..."]
    start_date = far_core.month_delta(end_date, -1)
    df = apps.dataframe_from_income_records(
        apps.get_filtered_income_records(
            end_date=end_date, start_date=start_date,
        )
    )
    dtable = dash_table.DataTable(
        id="income_breakdown_table",
        columns=[
            {"name": col, "id": col} for col in df.columns if col != 'id'
        ],
        data=df.to_dict("records"),
        filter_action="native",
        sort_action="native",
        sort_by=[{"column_id": "Date", "direction": "asc"}],
        fixed_rows={"headers": True, "data": 0},
    )
    return dtable
