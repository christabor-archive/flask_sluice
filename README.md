# sluice

![sluice logo](sluice_logo.png)

A dashboard and service for displaying results and executing linting reports for the Python prospector analysis module.

## Getting started.

You'll need postgresql, flask, and celery, along with all other python dependencies.

`git clone --recursive https://github.com/christabor-incubator/sluice.git`

Celery

`celery -A app.celery worker`

Postgresql

e.g. in mac:
`postgres -D /usr/local/postgresql/data/`
