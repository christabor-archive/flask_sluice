"""Provides basic static asset serving for HTML, JS, and CSS...."""

from flask import (
    Blueprint,
    abort,
    render_template,
    send_from_directory,
)

from jinja2 import TemplateNotFound

static_pages = Blueprint(
    'static_pages', __name__,
    template_folder='templates')

static_assets = Blueprint(
    'static_assets', __name__,
    static_url_path='/static',
    static_folder='/static')


@static_pages.route('/', defaults={'page': 'index'})
@static_pages.route('/pages/<page>')
def staticpage(page):
    """Handle static pages."""
    try:
        return render_template('pages/{0}.html'.format(page))
    except TemplateNotFound:
        abort(404)


@static_assets.route('/<path:filename>')
def _static(filename):
    return send_from_directory('static/', filename)
