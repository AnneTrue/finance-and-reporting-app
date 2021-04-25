# FaR App: Finance and Reporting Application
A python app for personal finances and cashflow reporting

Heavily opinionated, and *not* a balance sheet or asset tracker.

Built using plotly's Dash and features bookkeeping input, an SQLite database of records, and cash flow reports.

Get started with `mkdir data; sudo chown 1000:1000 ./data/` then `docker-compose build` and `docker-compose up`.


requirements.txt generated via `pipenv lock --keep-outdated --requirements > requirements.txt`
