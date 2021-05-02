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
    __tablename__ = "expense_record"

    expense_id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    category = db.Column(db.Enum(far_core.ExpenseCategory), nullable=False)
    account = db.Column(db.Enum(far_core.Accounts), nullable=False)
    note = db.Column(db.String(length=1024), nullable=True)

    def __str__(self):
        return (
            f"<ExpenseRecord {self.account} {self.date}"
            f" {self.amount} {self.category}>"
        )

    @property
    def pandas_record(self):
        return (
            self.expense_id, self.date, self.amount, self.category,
            self.account, self.note,
        )


def delete_expense_records_by_id(expense_ids: list):
    try:
        for expense_id in expense_ids:
            ExpenseRecord.query.filter(
                ExpenseRecord.expense_id == expense_id
            ).delete()
    except Exception:
        db.session.rollback()
        raise
    db.session.commit()


class IncomeRecord(db.Model):
    """
    Represents a single income transaction:
    Account, date, monetary amount, category, notes
    """
    __tablename__ = "income_record"

    income_id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    category = db.Column(db.Enum(far_core.IncomeCategory), nullable=False)
    account = db.Column(db.Enum(far_core.Accounts), nullable=False)
    note = db.Column(db.String(length=1024), nullable=True)

    def __str__(self):
        return (
            f"<IncomeRecord {self.account} {self.date}"
            f" {self.amount} {self.category}>"
        )

    @property
    def pandas_record(self):
        return (
            self.income_id, self.date, self.amount, self.category,
            self.account, self.note,
        )


def delete_income_records_by_id(income_ids: list):
    try:
        for income_id in income_ids:
            IncomeRecord.query.filter(
                IncomeRecord.income_id == income_id
            ).delete()
    except Exception:
        db.session.rollback()
        raise
    db.session.commit()


def init_tables():
    """
    Initialises all tables if no tables already exist
    """
    logger = logging.getLogger(__name__)
    logger.info("Checking if DB tables need to be initialised")
    if not db.engine.table_names():
        logger.warning("Creating DB tables for the first time!")
        db.create_all()
