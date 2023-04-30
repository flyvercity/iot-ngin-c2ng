''' Incoming Request Schemas '''
from marshmallow import Schema, fields


class BaseSuccessSchema(Schema):
    success = fields.Boolean(data_key='Success', default=True)


class ErrorSchema(Schema):
    success = fields.Boolean(data_key='Success', default=False)


class ValidationErrorSchema(ErrorSchema):
    errors = fields.Dict(
        data_key='Errors',
        keys=fields.String,
        values=fields.List(fields.String)
    )


def uavid():
    return fields.String(
        data_key='UavID',
        required=True,
        description='CAA UAV ID'
    )


class Degrees(fields.Float):
    def __init__(self, key):
        super().__init__(required=True, data_key=key)


class Meters(fields.Float):
    def __init__(self, key):
        super().__init__(required=True, data_key=key)


class Waypoint(Schema):
    lat = Degrees('Latitude')
    lon = Degrees('Longitude')
    alt = Meters('Altitude')


class AerialConnectionSessionRequest(Schema):
    ref_time = fields.Integer(
        data_key='ReferenceTime',
        description='UNIX Timestamp',
        required=True
    )

    uavid = uavid()
    waypoints = fields.List(fields.Nested(Waypoint), data_key='Waypoints')
    margin = Meters('OperationalMargin')
    metadata = fields.Dict(data_key='UssMetadata', required=False)


class AerialConnectionSessionResponseErrors(Schema):
    uss = fields.String(data_key='USS', required=True)


class AerialConnectionSessionResponseFailed(ErrorSchema):
    errors = fields.Nested(AerialConnectionSessionResponseErrors, data_key='Errors')
