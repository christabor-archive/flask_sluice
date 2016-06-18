"""Settings for sluice."""

import os

ENV = os.environ.get('SERVICE_TIER') or 'DEV'
SECRET_KEY = os.urandom(10)
ADMINS = ['dxdstudio@gmail.com']
APP_NAME = 'sluice'
LOG_FILENAME = 'sluice-app'
SQL_PROTOCOL = 'mysql'
DB_URI = os.environ.get(
    'SLUICE_DB_URI',
    'postgresql+psycopg2://taborc:password@0.0.0.0:5432/sluice')
LOGFILE_NAME = './flask-app-test.log'
FLASK_RUN_SETTINGS = dict(
    host='0.0.0.0',
    port=os.environ.get('PORT') or 8000,
    debug=True,
)
FLASK_CONFIG = dict(
    SECRET_KEY=SECRET_KEY,
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=DB_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',
)
