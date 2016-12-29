# sluice

![sluice logo](sluice_logo.png)

A dashboard and service for displaying results and executing linting reports for the Python prospector analysis module.

## Getting started.

You'll need mongo, flask, and celery, along with all other python dependencies.

`git clone --recursive https://github.com/christabor-incubator/sluice.git`

```shell
virtualenv env
source env/bin/activate
pip install -r frozen.txt
cd src
python app.py
```

#### Celery+Redis

`redis-server`

`celery -A app.celery worker`

#### Mongo

e.g. in OSX:

`mongod`
