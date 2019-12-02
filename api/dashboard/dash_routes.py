from flask import render_template

from api.helpers.check_token_type_decorator import jwt_required_extended

from . import blueprint
from .dash_app_1 import dash_app_1


@blueprint.route('/info')
@jwt_required_extended
def app1_template():
    return render_template('app_1.html', dash_url=dash_app_1.url_base)
