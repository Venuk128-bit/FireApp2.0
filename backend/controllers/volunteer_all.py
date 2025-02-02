from flask import Blueprint
from flask_restful import Resource, fields, marshal_with, Api

from domain import session_scope
from repository.volunteer_repository import *
from services.jwk import requires_auth

'''
No Data Input
--
Define Data Output

{
    "results" : [{
        "id": String
        "firstName": String
        "lastName": String
        "email": String
        "mobileNo": String
        "prefHours": Integer
        "expYears": Integer
        "possibleRoles": [String]
        "qualifications": [String]
        "availabilities": [[DateTimeString iso8601, DateTimeString iso8601]]
    }]
}
'''

availability_field = {
    "Monday": fields.List(fields.List(fields.Integer)),
    "Tuesday": fields.List(fields.List(fields.Integer)),
    "Wednesday": fields.List(fields.List(fields.Integer)),
    "Thursday": fields.List(fields.List(fields.Integer)),
    "Friday": fields.List(fields.List(fields.Integer)),
    "Saturday": fields.List(fields.List(fields.Integer)),
    "Sunday": fields.List(fields.List(fields.Integer)),
}

volunteer_list_field = {
    'ID': fields.String,
    'firstName': fields.String,
    'lastName': fields.String,
    'email': fields.String,
    'mobileNo': fields.String,
    'prefHours': fields.Integer,
    'expYears': fields.Integer,
    'possibleRoles': fields.List(fields.String),
    'qualifications': fields.List(fields.String),
    'availabilities': fields.Nested(availability_field)
}

resource_fields = {
    'results': fields.List(fields.Nested(volunteer_list_field)),
}


# Handle the Recommendation endpoint
class VolunteerAll(Resource):

    @requires_auth
    @marshal_with(resource_fields)
    def get(self):
        with session_scope() as session:
            rtn = []
            for row in list_volunteers(session):
                # Access protected _asdict() to return the keyed tuple as a dict to enable flask_restful to marshal
                # it correctly. The alternative method is less tidy.
                rtn.append(row._asdict())
            return {"success": True, "results": rtn}


volunteer_all_bp = Blueprint('volunteer_all', __name__)
api = Api(volunteer_all_bp)
api.add_resource(VolunteerAll, '/volunteer/all')
