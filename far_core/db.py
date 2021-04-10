#!/usr/bin/python3
"""
DB models and DB utilities of the Finance and Reporting App.
"""

import logging

from app import db
import far_core


class ExpenseRecord(db.Model):
    """
    Represents a single expense transaction:
    Account, date, monetary amount, category, notes
    """
    expense_id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    category = db.Column(db.Enum(far_core.ExpenseCategory), nullable=False)
    account = db.Column(db.Enum(far_core.Accounts), nullable=False)
    note = db.Column(db.String(length=1024), nullable=True)


class IncomeRecord(db.Model):
    """
    Represents a single income transaction:
    Account, date, monetary amount, category, notes
    """
    income_id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    category = db.Column(db.Enum(far_core.IncomeCategory), nullable=False)
    account = db.Column(db.Enum(far_core.Accounts), nullable=False)
    note = db.Column(db.String(length=1024), nullable=True)


def init_tables():
    """
    Initialises all tables if no tables already exist
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking if DB tables need to be initialised")
    if not db.engine.table_names():
        logger.warning("Creating DB tables for the first time!")
        db.create_all()
