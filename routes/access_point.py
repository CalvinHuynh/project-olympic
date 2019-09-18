from flask_restplus import Namespace, Resource, fields
from services import AccessPointService

api = Namespace('access-points', description='Access point related operations')

# access_point = api.model('AccessPoint', {
#     'description':
#     fields.String(description='Description of the access point.'),
# })

# TODO: Create a constructor so that the route becomes testable without hitting the database
access_point_service = AccessPointService


@api.route('/')
class GetAllAccessPoints(Resource):
    @api.doc('get_all_access_points')
    # @api.marshal_list_with(access_point)
    def get(self):
        """Retrieves all access points"""
        return access_point_service.get_all_access_points(self)


@api.route('/<id>')
@api.param('id', 'The identifier of the access point')
@api.response(404, 'Access point not found')
class GetAccessPoint(Resource):
    @api.doc('get_access_point')
    # @api.marshal_with(access_point)
    def get(self, id):
        """Fetch a single access point"""
        access_point = access_point_service.get_one_access_point(self, id)
        if access_point:
            return access_point
        api.abort(404)