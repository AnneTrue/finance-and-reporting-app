#!/usr/bin/python3

import datetime
import json

import far_core.db
from app import db


def import_expenses_from_json(json_path: str):
    """
    Adds expenses to the SQLite DB from a JSON blob.
    Assumes the blob is a list of lists, with format:
    [["date str", amount, "category", "note", "account"], ...]
    """
    with open(json_path, "rt") as f:
        expenses = json.load(f)
    for exp in expenses:
        exp_record = far_core.db.ExpenseRecord(
            date=datetime.datetime.strptime(
                exp[0], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).date(),
            amount=exp[1],
            category=exp[2],
            note=exp[3],
            account=exp[4],
        )
        db.session.add(exp_record)
    db.session.commit()


def import_incomes_from_json(json_path):
    """
    Adds incomes to the SQLite DB from a JSON blob.
    Assumes the blob is a list of lists, with format:
    [["date str", amount, "category", "note", "account"], ...]
    """
    with open(json_path, "rt") as f:
        expenses = json.load(f)
    for exp in expenses:
        exp_record = far_core.db.IncomeRecord(
            date=datetime.datetime.strptime(
                exp[0], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).date(),
            amount=exp[1],
            category=exp[2],
            note=exp[3],
            account=exp[4],
        )
        db.session.add(exp_record)
    db.session.commit()
