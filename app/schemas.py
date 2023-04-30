''' Incoming Request Schemas '''
from marshmallow import Schema, fields, post_load


class BaseSuccessSchema:
    success = fields.Boolean(data_key='Success', default=True)


class ErrorSchema:
    success = fields.Boolean(data_key='Success', default=False)
    errors = fields.Dict(data_key='Errors', required=True)


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
