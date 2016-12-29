#!/usr/bin/env python

"""Sluice Flask App."""

from __future__ import absolute_import

import os

from celery import Celery
from flask import (
    Flask,
    abort,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for,
)
from flask.ext.bootstrap import Bootstrap
from flask.ext import breadcrumbs
from flask_extras import FlaskExtras
from flask_wtf.csrf import CsrfProtect

from bson.objectid import ObjectId
from pymongo import MongoClient

import forms

import filters
import prospector_api as api
import settings as fs


DB_URI = os.environ.get('SLUICE_DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('SLUICE_DB_PORT', 27017))
DB_NAME = os.environ.get('SLUICE_DB', 'sluice')
DB_COLL = os.environ.get('SLUICE_DB_COLL', 'jobs')

client = MongoClient(host=DB_URI, port=DB_PORT)
conn = client[DB_NAME]
coll = conn[DB_COLL]


currdir = os.getcwd()
app = Flask(__name__)
app.config.update(**fs.FLASK_CONFIG)
app.secret_key = fs.SECRET_KEY

app.jinja_env.filters['error_label'] = filters.error_label
app.jinja_env.filters['get_strictness_label'] = filters.get_strictness_label

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# Inject app config into celery.
celery.conf.update(app.config)

# Add nav breadcrumbs
breadcrumbs.Breadcrumbs(app=app)

# Setup CSRF protection
CsrfProtect().init_app(app)
bootstrap = Bootstrap(app)

# Setup extra filters/macros
FlaskExtras(app)


def _get_search_formdefaults():
    """Return search form pre-populated with existing GET params."""
    defaults = dict()
    for arg in ['output', 'strictness', 'name', 'path', 'github_url']:
        if all([
            request.args.get(arg) is not None,
            request.args.get(arg) != '',
        ]):
            defaults.update(**{arg: request.args.get(arg).strip()})
    return forms.SearchForm(**defaults)


@app.context_processor
def _inject_default_args():
    return dict(
        active_nav='',
        searchform=_get_search_formdefaults(),
        APP_NAME=fs.APP_NAME,
        page_title=str(request.url_rule),
        user=session.get('user', None),
    )


@app.route('/job/<tr_id>', methods=['GET'])
@breadcrumbs.register_breadcrumb(app, '.job', 'Job')
def job(tr_id):
    """Job results."""
    testrun = coll.find_one(dict(_id=ObjectId(tr_id)))
    if not testrun:
        abort(404)
    kwargs = dict(
        id=tr_id,
        testrun=testrun
    )
    return render_template('pages/job.html', **kwargs)


@app.route('/timeline/<pathname>', methods=['GET'])
@breadcrumbs.register_breadcrumb(app, '.timeline', 'Timeline')
def timeline(pathname):
    """View results."""
    kwargs = dict(
        pathname=pathname,
        runs=coll.find(dict(pathname=pathname)),
    )
    return render_template('pages/timeline.html', **kwargs)


@celery.task
def lint_code(username, **kwargs):
    """Layer of indirection around db, celery task and prospector API."""
    pathname = kwargs.pop('path')
    name = kwargs.pop('name')
    github_url = kwargs.pop('github_url')

    results = api.get_results(pathname, **kwargs)
    kwargs.update(dict(
        name=name,
        github_url=github_url,
        pathname=pathname,
        created_by=username,
        results=results,
    ))
    coll.insert_one(kwargs)


@app.route('/search', methods=['GET'])
@breadcrumbs.register_breadcrumb(app, '.search', 'Search results')
def search():
    """Search page."""
    search_kwargs = dict()
    for arg in ['output', 'strictness', 'name', 'path', 'github_url']:
        if all([
            request.args.get(arg) is not None,
            request.args.get(arg) != '',
        ]):
            search_kwargs.update(**{arg: request.args.get(arg).strip()})
    results = coll.find(search_kwargs)
    if not results:
        return abort(404)
    kwargs = dict(results=results)
    return render_template('pages/search.html', **kwargs)


@app.route('/', methods=['GET', 'POST'])
@breadcrumbs.register_breadcrumb(app, '.', 'Home')
def index():
    """Index page."""
    form = forms.ProspectorResultsForm()
    task = None
    if request.method == 'POST':
        if form.validate_on_submit():
            data = form.data
            user = session.get('user', 'Anonymous')
            task = lint_code.delay(user, **data)
            flash('Added new test entry to queue.')
            return redirect(url_for('index'))
    kwargs = dict(
        results=task,
        form=form,
        existing=coll.find(),
    )
    return render_template('pages/index.html', **kwargs)


if __name__ == "__main__":
    # TOOD: move to one-time script, like alembic.
    # models.create_schemas(db)
    app.run(**fs.FLASK_RUN_SETTINGS)
