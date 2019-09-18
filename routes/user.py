# from flask_restplus import Namespace, Resource, fields

# api = Namespace('user', description='user related operations')

# cat = api.model('Cat', {
#     'id': fields.String(required=True, description='The cat identifier'),
#     'name': fields.String(required=True, description='The cat name'),
# })

# CATS = [
#     {'id': 'felix', 'name': 'Felix'},
# ]

# @api.route('/')
# class AccessPointsList(Resource):
#     @api.doc('get_all_access_points')
#     @api.marshal_list_with(cat)
#     def get(self):
#         """List all cats"""
#         return CATS

# @api.route('/<id>')
# @api.param('id', 'The cat identifier')
# @api.response(404, 'Cat not found')
# class SingleAccessPoint(Resource):
#     @api.doc('get_access_point')
#     @api.marshal_with(cat)
#     def get(self, id):
#         """Fetch a cat given its identifier"""
#         for cat in CATS:
#             if cat['id'] == id:
#                 return cat
#         api.abort(404)