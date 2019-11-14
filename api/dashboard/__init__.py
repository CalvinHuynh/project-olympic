from flask import Blueprint

blueprint = Blueprint('dash-examples_blueprint',
                      __name__,
                      url_prefix='/dash',
                      template_folder='templates',
                      static_folder='static')
