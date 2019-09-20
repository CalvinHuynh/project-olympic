from flask_restplus import Namespace, Resource, fields
from services import AccessPointService
from peewee import PeeweeException
from dto import CreateAccessPointDto

api = Namespace('access-points', description="Access point related operations")

user = api.inherit(
    'User',
    {
        'id':
        fields.Integer(description="Id of user"),
        # 'username':
        # fields.String(description="Username", example="admin1234"),
        # 'email':
        # fields.String(description="Email of user", example="test@test.test"),
        # 'join_date': fields.String,
        # 'last_login_date': fields.String
    })

create_access_point_dto = api.model(
    'CreateAccessPoint', {
        'description':
        fields.String(description="Description of access point",
                      example="Near the entrance"),
        'user':
        fields.Nested(user)
    })

# TODO: Add DI
access_point_service = AccessPointService


@api.route('/')
class GetAllAccessPoints(Resource):
    @api.doc('get_all_access_points')
    # @api.marshal_list_with(access_point) # marshal is able to format the responses
    def get(self):
        """Retrieves all access points"""
        return access_point_service.get_all_access_points(self)

    @api.doc('create_access_point')
    @api.expect(create_access_point_dto)
    def post(self):
        return create_access_point_dto


@api.route('/<id>')
@api.param('id', 'The identifier of the access point')
@api.response(404, 'Access point not found')
class GetAccessPoint(Resource):
    @api.doc('get_access_point')
    # @api.marshal_with(access_point)
    def get(self, id):
        """Fetch a single access point"""
        return access_point_service.get_one_access_point(self, id)