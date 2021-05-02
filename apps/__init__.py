#!/usr/bin/python3

import datetime

import dash_bootstrap_components as dbc
import pandas as pd
import sqlalchemy

from app import cache
import far_core.db

NAVBAR = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Main", href="/")),
        dbc.NavItem(dbc.NavLink("Input", href="/input")),
        dbc.NavItem(dbc.NavLink("Expenses", href="/expenses")),
        dbc.NavItem(dbc.NavLink("Incomes", href="/incomes")),
        dbc.DropdownMenu(
            label="Reports",
            children=[
                dbc.DropdownMenuItem("Monthly Review", href="/report/monthly"),
                dbc.DropdownMenuItem("Annual Review", href="/report/annual"),
                dbc.DropdownMenuItem("Forecast", href="/report/forecast"),
            ],
            nav=True,
            in_navbar=True,
        ),
    ],
    brand="Finance & Reporting App",
    brand_href="#",
    color="primary",
    dark=True,
)


@cache.memoize(timeout=5)
def get_all_expense_records():
    return far_core.db.ExpenseRecord.query.all()


@cache.memoize(timeout=5)
def get_filtered_expense_records(
    *_args,
    category: far_core.ExpenseCategory = None,
    end_date: datetime.date = None,
    reduced_category: far_core.ReducedCategory = None,
    start_date: datetime.date = None,
):
    if _args:
        raise NotImplementedError("get_filtered_expense_records() only takes kwargs")
    del _args
    q = far_core.db.ExpenseRecord.query
    if category:
        q = q.filter_by(category=category)
    if end_date:
        q = q.filter(far_core.db.ExpenseRecord.date < end_date)
    if reduced_category:
        q = q.filter(
            sqlalchemy.or_(
                far_core.db.ExpenseRecord.category == cat
                for cat in far_core.EXPENSE_CATEGORY_BY_REDUCED_CATEGORY[
                    reduced_category
                ]
            )
        )
    if start_date:
        q = q.filter(far_core.db.ExpenseRecord.date >= start_date)
    return q.all()


def dataframe_from_expense_records(expense_record_list: list):
    return pd.DataFrame.from_records(
        data=(exp_rec.pandas_record for exp_rec in expense_record_list),
        columns=("id", "Date", "Amount", "Category", "Account", "Note"),
    )


@cache.memoize(timeout=5)
def get_all_income_records():
    return far_core.db.IncomeRecord.query.all()


@cache.memoize(timeout=5)
def get_filtered_income_records(
    *_args,
    category: far_core.IncomeCategory = None,
    end_date: datetime.date = None,
    start_date: datetime.date = None,
):
    if _args:
        raise NotImplementedError("get_filtered_income_records() only takes kwargs")
    del _args
    q = far_core.db.IncomeRecord.query
    if category:
        q = q.filter_by(category=category)
    if end_date:
        q = q.filter(far_core.db.IncomeRecord.date < end_date)
    if start_date:
        q = q.filter(far_core.db.IncomeRecord.date >= start_date)
    return q.all()


def dataframe_from_income_records(income_record_list: list):
    return pd.DataFrame.from_records(
        data=(inc_rec.pandas_record for inc_rec in income_record_list),
        columns=("id", "Date", "Amount", "Category", "Account", "Note"),
    )
