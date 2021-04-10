#!/usr/bin/python3
"""
Dash app for the accounting input page, which handles adding expenses/incomes
to the database.
"""

import datetime
import logging

from dash.dependencies import Input, Output, State
import dash.exceptions
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import enum

from app import app, db
import apps
import far_core
import far_core.db


# How many lines of input to accept at a time
NUMBER_OF_INPUT_ROWS = 2


class InputType(enum.Enum):
    expense = "Expense"
    income = "Income"

    def __str__(self):
        return self.value


def get_layout():
    return html.Div([
        apps.NAVBAR,
        dbc.Alert(
            "Input validation error! Please check your inputs for mistakes",
            id="input_alert_auto",
            is_open=False,
            duration=4000,
        ),
        dbc.Row(
            [
                dbc.Col(get_account_dropdown(), width=3),
                dbc.Col(
                    [get_input_submit_button(), get_input_clear_button()],
                    width=1,
                ),
            ],
            align="center",
            justify="center",
        ),
        html.Hr(),
        dbc.Row([
            dbc.Col(html.Div(get_input_form(InputType.expense))),
            dbc.Col(html.Div(get_input_form(InputType.income))),
        ]),
    ])


def get_account_dropdown():
    """
    :return: A dropdown element with options for account names
    """
    return dcc.Dropdown(
        options=[
            {"label": str(account), "value": str(account)}
            for account in far_core.Accounts
        ],
        placeholder="Select an account",
        id="account_dropdown"
    )


def get_input_submit_button():
    return html.Button(
        "Submit", id="submit_input_button", className="btn btn-outline-primary"
    )


def get_input_clear_button():
    return html.Button(
        "Clear", id="clear_input_button", className="btn btn-outline-secondary"
    )


def get_input_form(input_type):
    """
    :param InputType input_type: enum of expense or income
    :return: styling elements
    """
    header_row = [
        html.Thead(html.Tr([
            html.Th("Date:"),
            html.Th("Amount:"),
            html.Th(f"{input_type} Category:"),
            html.Th("Notes:"),
        ])),
    ]
    input_rows = [
        get_input_row(input_type, identifier=i)
        for i in range(NUMBER_OF_INPUT_ROWS)
    ]
    table = dbc.Table(
        header_row + [html.Tbody(input_rows)],
        bordered=True,
        responsive=True,
        striped=True,
    )
    return table


def get_input_row(input_type, identifier):
    """
    :param InputType input_type:
    :param int identifier: index of the row, used to identify the forms
        The full row identifier looks like "input-Expense-1-<input name>"
    :return:
    """
    type_and_identifier = f"input_{input_type}_{identifier}"
    if input_type is InputType.expense:
        categories = (cat_enum for cat_enum in far_core.ExpenseCategory)
    elif input_type is InputType.income:
        categories = (cat_enum for cat_enum in far_core.IncomeCategory)
    else:
        raise NotImplementedError("Only income and expenses inputs are allowed")
    return html.Tr([
        html.Td([
            dcc.Input(id=f"{type_and_identifier}_date", type="text")
        ]),
        html.Td([
            dcc.Input(id=f"{type_and_identifier}_amount", type="number")
        ]),
        html.Td([
            dcc.Dropdown(
                id=f"{type_and_identifier}_category",
                options=[
                    {'label': str(cat), "value": str(cat)} for cat in categories
                ],
                placeholder="Category",
            )
        ]),
        html.Td([
            dcc.Input(
                id=f"{type_and_identifier}_note", type="text",
                placeholder="Notes",
            )
        ])
    ])


LAYOUT = get_layout()


def validate_expense_input(
        account: str, amount: float, category: str, date: str, note: str
) -> dict:
    # All non-account inputs are null, therefore empty row to skip:
    if not amount and not category and not date and not note:
        return {}
    if not account or not amount or not category or not date:
        raise ValueError("Missing required field in input")
    account_obj = far_core.Accounts(account)
    if amount <= 0.0:
        raise ValueError("Amount cannot be negative")
    cat_obj = far_core.ExpenseCategory(category)
    date_obj = far_core.date_from_string(date_str=date)
    if date_obj > (datetime.datetime.now().date() + datetime.timedelta(days=1)):
        raise ValueError("Dates cannot be set in the future!")
    return {
        "account": account_obj,
        "amount": amount,
        "category": cat_obj,
        "date": date_obj,
        "note": note,
    }


def validate_income_input(
        account: str, amount: float, category: str, date: str, note: str
) -> dict:
    # All non-account inputs are null, therefore empty row to skip:
    if not amount and not category and not date and not note:
        return {}
    if not account or not amount or not category or not date:
        raise ValueError("Missing required field in input")
    account_obj = far_core.Accounts(account)
    if amount <= 0.0:
        raise ValueError("Amount cannot be negative")
    cat_obj = far_core.IncomeCategory(category)
    date_obj = far_core.date_from_string(date_str=date)
    if date_obj > (datetime.datetime.now().date() + datetime.timedelta(days=1)):
        raise ValueError("Dates cannot be set in the future!")
    return {
        "account": account_obj,
        "amount": amount,
        "category": cat_obj,
        "date": date_obj,
        "note": note,
    }


def generate_all_input_ids():
    input_ids = []
    for input_type in InputType:
        for i in range(NUMBER_OF_INPUT_ROWS):
            for specific_input in ("date", "amount", "category", "note"):
                input_ids.append(
                    f"input_{input_type}_{i}_{specific_input}"
                )
    return input_ids


def handle_submit(ctx, account_name: str, in_states: tuple):
    """
    Handles the submit button, validating input rows and inserting them into
    the database if all are valid inputs.

    :param dash.callback_context ctx: context of the callback
    :param str account_name:
    :param tuple[str] in_states: tuple of states from handle_inputs
    :return: List of outputs for handle_inputs
    """
    logger = logging.getLogger(__name__).getChild("handle_submit")
    for i in range(NUMBER_OF_INPUT_ROWS):
        exp_id = f"input_{InputType.expense}_{i}"
        inc_id = f"input_{InputType.income}_{i}"
        exp_date = ctx.states[f"{exp_id}_date.value"]
        exp_amount = ctx.states[f"{exp_id}_amount.value"]
        exp_category = ctx.states[f"{exp_id}_category.value"]
        exp_note = ctx.states[f"{exp_id}_note.value"]
        try:
            exp_kwargs = validate_expense_input(
                date=exp_date, amount=exp_amount, category=exp_category,
                note=exp_note, account=account_name,
            )
            if exp_kwargs:
                exp_record = far_core.db.ExpenseRecord(**exp_kwargs)
        except ValueError as e:
            logger.info("Handle expense input validation error: %s", e)
            # Validation error, display the alert bar
            db.session.rollback()
            return (True, account_name) + in_states
        if exp_kwargs:
            db.session.add(exp_record)
        inc_date = ctx.states[f"{inc_id}_date.value"]
        inc_amount = ctx.states[f"{inc_id}_amount.value"]
        inc_category = ctx.states[f"{inc_id}_category.value"]
        inc_note = ctx.states[f"{inc_id}_note.value"]
        try:
            inc_kwargs = validate_income_input(
                date=inc_date, amount=inc_amount, category=inc_category,
                note=inc_note, account=account_name,
            )
            if inc_kwargs:
                inc_record = far_core.db.IncomeRecord(**inc_kwargs)
        except ValueError as e:
            logger.info("Handle income input validation error: %s", e)
            # Validation error, display the alert bar
            db.session.rollback()
            return (True, account_name) + in_states
        if inc_kwargs:
            db.session.add(inc_record)
    db.session.commit()
    return [False, account_name] + [""] * len(in_states)


@app.callback(
    [
        Output("input_alert_auto", "is_open"),
        Output("account_dropdown", "value"),
    ] + [
        Output(input_id, "value")
        for input_id in generate_all_input_ids()
    ],
    Input("clear_input_button", "n_clicks"),
    Input("submit_input_button", "n_clicks"),
    [State("account_dropdown", "value")] + [
        State(input_id, "value")
        for input_id in generate_all_input_ids()
    ],
)
def handle_inputs(clear_clicks, submit_clicks, account_name, *in_states):
    """
    Handler for the input sheet, determines whether clearing or submitting.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate()
    triggered_ids = tuple(t["prop_id"] for t in ctx.triggered)
    if "submit_input_button.n_clicks" in triggered_ids and submit_clicks:
        return handle_submit(
            ctx, account_name=account_name, in_states=in_states
        )
    elif "clear_input_button.n_clicks" in triggered_ids and clear_clicks:
        return [False, ""] + [""] * len(in_states)
    return (False, account_name) + in_states
