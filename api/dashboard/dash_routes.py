from flask import render_template

from api.helpers.check_token_type_decorator import jwt_required_extended

from . import blueprint
from .dash_overview import occupancy_overview
from .dash_forecast import occupancy_forecast


@blueprint.route('/overview')
@jwt_required_extended
def overview_dashboard():
    return render_template(
        'iframe_layout.html',
        dash_url=occupancy_overview.url_base
    )


@blueprint.route('/forecast')
def forecast_dashboard():
    return render_template(
        'iframe_layout.html',
        dash_url=occupancy_forecast.url_base
    )
