#!/usr/bin/env python

"""Sluice Flask App."""

from __future__ import absolute_import

import os

from celery import Celery
from flask import (
    abort,
    Flask,
    flash,
    render_template,
    session,
    redirect,
    request,
    g,
    url_for,
)
from flask.ext.bootstrap import Bootstrap
from flask.ext import breadcrumbs
from flask_extras.filters import config as filter_conf
from flask_wtf.csrf import CsrfProtect

import jinja2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import forms
import filters
import models
import prospector_api as api
import settings as fs

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
filter_conf.config_flask_filters(app)

folders = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('{0}/flask_extras/macros/'.format(currdir)),
])
app.jinja_loader = folders

db = create_engine(fs.DB_URI)
SluiceSession = sessionmaker(bind=db)
dbsession = SluiceSession()


@app.context_processor
def _inject_default_args():
    return {
        'active_nav': '',
        'APP_NAME': fs.APP_NAME,
        'page_title': str(request.url_rule),
        'user': session.get('user', None)
    }


@app.route('/job/<tr_id>', methods=['GET'])
@breadcrumbs.register_breadcrumb(app, '.job', 'Job')
def job(tr_id):
    """Job results."""
    testrun = dbsession.query(models.TestRun).filter_by(id=tr_id).first()
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
        runs=dbsession.query(
            models.TestRun).filter_by(pathname=pathname).all()
    )
    return render_template('pages/timeline.html', **kwargs)


@celery.task
def _check_code(pathname, username, **kwargs):
    """Layer of indirection around db, celery task and prospector API."""
    results = api.get_results(pathname, **kwargs)
    kwargs.update(dict(
        pathname=pathname,
        created_by=username,
        results=results,
    ))
    dbsession.add(models.TestRun(**kwargs))
    dbsession.commit()


@app.route('/search', methods=['GET'])
@breadcrumbs.register_breadcrumb(app, '.search', 'Search results')
def search():
    """Search page."""
    if request.args.get('q', None) is None:
        flash('No argument specified.')
        return redirect(url_for('index'))
    pathname = request.args.get('q').strip()
    results = (dbsession
               .query(models.TestRun)
               .filter_by(pathname=pathname)
               .all())
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
            pathname = form['path'].data
            data = dict(
                strictness=form['strictness'].data,
                output=form['output'].data,)
            user = session.get('user', 'Anonymous')
            task = _check_code.delay(pathname, user, **data)
            flash('Added new test entry to queue.')
            redirect(url_for('index'))
    kwargs = dict(
        results=task,
        form=form,
        existing=dbsession.query(models.TestRun).all()
    )
    return render_template('pages/index.html', **kwargs)


if __name__ == "__main__":
    # TOOD: move to one-time script, like alembic.
    models.create_schemas(db)
    app.run(**fs.FLASK_RUN_SETTINGS)
