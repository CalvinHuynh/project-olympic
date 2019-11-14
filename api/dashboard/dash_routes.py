from . import blueprint
from flask import render_template
from .dash_app_1 import dash_app_1


@blueprint.route('/app1')
def app1_template():
    return render_template('app_1.html', dash_url=dash_app_1.url_base)
