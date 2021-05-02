#!/usr/bin/python3
"""
Core components of the Finance and Reporting App.
e.g. configuration data, utility functions unrelated to the web apps.
"""

import datetime
import decimal
import re

import dateutil.relativedelta
import enum


@enum.unique
class Accounts(str, enum.Enum):
    """
    An enumeration of accounts, which you should edit as an end-user
    """

    # my_name = "My Name"
    # example_joint = "Example Joint"
    anne = "Anne"
    john = "John"
    joint = "Joint"

    def __str__(self):
        return self.value

    @property
    def colour(self):
        return {
            self.anne: "red",
            self.john: "green",
            self.joint: "blue",
        }[self]


@enum.unique
class ReducedCategory(str, enum.Enum):
    asset = "Asset"
    debt = "Debt"
    fun = "Fun"
    mandatory = "Mandatory"
    misc = "Misc"

    def __str__(self):
        return self.value

    @property
    def colour(self):
        return {
            self.asset: "green",
            self.debt: "red",
            self.fun: "orange",
            self.mandatory: "gray",
            self.misc: "blue",
        }[self]


@enum.unique
class ExpenseCategory(str, enum.Enum):
    """
    An enumeration for expenses.
    You can call str() on an ExpenseCategory enum to get its display name.
    You can check the reduced_category property of an ExpenseCategory enum
    to get the associated ReducedCategory enum
    """

    business = "Business & Work"
    car_fees = "Car Fees"
    clothing = "Clothing"
    debt = "Debt"
    dependents = "Dependents"
    dining_out = "Dining Out"
    drugs = "Drugs"
    education = "Education"
    finance = "Finance"
    gift = "Gift"
    groceries = "Groceries"
    grooming = "Grooming"
    health = "Health"
    household_supplies = "Household Supplies"
    house_repairs = "House Repairs"
    insurance = "Insurance"
    investment = "Investment"
    leisure = "Leisure & Hobbies"
    mortgage = "Mortgage"
    recreation = "Recreation & Fitness"
    refueling = "Refueling"
    rent = "Rent"
    taxes = "Taxes"
    transit = "Transit & Parking"
    utility_bills = "Utility Bills"
    vacation = "Vacation & Events"
    other = "Other"

    def __str__(self):
        return self.value

    @property
    def reduced_category(self):
        try:
            return {
                self.business: ReducedCategory.mandatory,
                self.car_fees: ReducedCategory.mandatory,
                self.clothing: ReducedCategory.mandatory,
                self.debt: ReducedCategory.debt,
                self.dependents: ReducedCategory.mandatory,
                self.dining_out: ReducedCategory.fun,
                self.drugs: ReducedCategory.fun,
                self.education: ReducedCategory.mandatory,
                self.finance: ReducedCategory.debt,
                self.gift: ReducedCategory.misc,
                self.groceries: ReducedCategory.mandatory,
                self.grooming: ReducedCategory.mandatory,
                self.health: ReducedCategory.mandatory,
                self.household_supplies: ReducedCategory.mandatory,
                self.house_repairs: ReducedCategory.mandatory,
                self.insurance: ReducedCategory.mandatory,
                self.investment: ReducedCategory.asset,
                self.leisure: ReducedCategory.fun,
                self.mortgage: ReducedCategory.mandatory,
                self.recreation: ReducedCategory.fun,
                self.refueling: ReducedCategory.mandatory,
                self.rent: ReducedCategory.mandatory,
                self.taxes: ReducedCategory.mandatory,
                self.transit: ReducedCategory.mandatory,
                self.utility_bills: ReducedCategory.mandatory,
                self.vacation: ReducedCategory.fun,
                self.other: ReducedCategory.misc,
            }[self]
        except KeyError:
            raise ValueError(f"Category {self.value} does not have a reduced category")


EXPENSE_CATEGORY_BY_REDUCED_CATEGORY = {red_cat: set() for red_cat in ReducedCategory}
for red_cat in ReducedCategory:
    for cat in ExpenseCategory:
        if cat.reduced_category is red_cat:
            EXPENSE_CATEGORY_BY_REDUCED_CATEGORY[red_cat].add(cat)


@enum.unique
class IncomeCategory(str, enum.Enum):
    """
    An enumeration for incomes.
    You can call str() on an IncomeCategory to get its display name.
    """

    capital_gains = "Capital Gains"
    disability = "Disability"
    gift = "Gift"
    interest = "Interest & Dividends"
    wages = "Wages"
    other = "Other"

    def __str__(self):
        return self.value


def date_from_string(date_str: str) -> datetime.date:
    """
    Accepts either ISO with hyphens dates such as "2021-01-30" or US-style
    dates with slashes such as "1/30/2021"
    """
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            dt_obj = datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
        else:
            return dt_obj.date()
    raise ValueError(f"Unrecognised date string: '{date_str}'")


def month_from_string(month_str: str) -> datetime.date:
    """
    Accepts year-month strings with hyphens such as "%Y-%m"
    """
    return datetime.datetime.strptime(month_str, "%Y-%m").date()


def get_current_month() -> datetime.date:
    now = datetime.datetime.now()
    return datetime.date(year=now.year, month=now.month, day=1)


def month_delta(start_month: datetime.date, months: int) -> datetime.date:
    return start_month + dateutil.relativedelta.relativedelta(months=months)


def usd_str(amount: float) -> str:
    if amount < 0:
        return f"(${amount:,.2f})"
    return f"${amount:,.2f}"


def sum_all_records(records: list) -> decimal.Decimal:
    sum_records = decimal.Decimal(0)
    for record in records:
        sum_records += record.amount
    return sum_records


def get_date_from_date_str(date_str: str) -> datetime.date:
    m = re.match(r"(\d{4})-([1-9]|1[0-2]|0[1-9])", date_str)
    if not m:
        return None
    year, month = int(m.group(1)), int(m.group(2))
    return datetime.date(year, month, 1)
