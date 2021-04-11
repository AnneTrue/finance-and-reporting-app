#!/usr/bin/python3

import dash_bootstrap_components as dbc


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
