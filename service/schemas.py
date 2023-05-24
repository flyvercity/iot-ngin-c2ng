# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines Input/Output Data Object Schemas.'''
from marshmallow import Schema, fields, validate


def uasid():
    '''Generate standard UAS ID field.'''
    return fields.String(required=True, description='CAA UAS ID')


def validate_imsi(value):
    '''Validate standard 3GPP IMSI number.'''
    return validate.Regexp('[0-9]{14,15}')


class BaseSuccessSchema(Schema):
    Success = fields.Boolean(validate=validate.Equal(True), description='Success flag')


class ErrorSchema(Schema):
    Success = fields.Boolean(validate=validate.Equal(False), description='Failure flag.')
    Message = fields.String()


class ValidationErrorSchema(ErrorSchema):
    Errors = fields.Dict(
        keys=fields.String,
        values=fields.List(fields.String),
        description='Error identifier dict'
    )


class AerialConnectionSessionRequest(Schema):
    # TODO: Check reference time
    ReferenceTime = fields.Float(
        description='UNIX Timestamp',
        required=True
    )

    UasID = uasid()
    IMSI = fields.String(validate=validate_imsi, required=True, description='UE IMSI ID')
    # TODO: Transmit metadata to USS
    Metadata = fields.Dict(required=False, description='Opaque object to pass to USSP')


class AerialConnectionSessionResponseErrors(Schema):
    USS = fields.String(required=True, validate=validate.OneOf([
        'provider_unavailable',
        'flight_not_approved'
    ]))


class AerialConnectionSessionResponseFailed(ErrorSchema):
    Errors = fields.Nested(AerialConnectionSessionResponseErrors, required=True)


class AerialConnectionSessionResponse(BaseSuccessSchema):
    IP = fields.IP(required=True, description='Own IP address for aerial connection.')
    GatewayIP = fields.IP(required=True, description='Gateway IP for aerial connection.')

    EncryptedPrivateKey = fields.String(
        required=True, description='Session private key encrypted with client secret'
    )


class AdxConnectionSessionRequest(Schema):
    # TODO: Check reference time
    ReferenceTime = fields.Float(
        description='UNIX Timestamp',
        required=True
    )

    UasID = fields.String(required=True)


class AdxConnectionSessionResponseErrors(Schema):
    USS = fields.String(required=True, validate=validate.OneOf([
        'here_define_the_errors'
    ]))


class AdxConnectionSessionResponseFailed(ErrorSchema):
    Errors = fields.Nested(AdxConnectionSessionResponseErrors, required=True)


class AdxConnectionSessionResponse(BaseSuccessSchema):
    IP = fields.IP(required=True, description='Own IP address for the ADX connection.')
    GatewayIP = fields.IP(required=True, description='Gateway IP for ADX connection.')

    EncryptedPrivateKey = fields.String(
        required=True, description='Session private key encrypted with client secret'
    )


class CertificateRequestResponseErrors(Schema):
    UasID = fields.String(validate=validate.OneOf([
        'not_found',
    ]))

    Session = fields.String(validate=validate.OneOf([
        'session_not_found',
        'peer_not_connected'
    ]))


class CertificateRequestResponseFailed(ErrorSchema):
    Errors = fields.Nested(CertificateRequestResponseErrors, required=True)


class CertificateRequestResponse(BaseSuccessSchema):
    Certificate = fields.String(
        required=True, description='Certificate with a public key as a PEM string'
    )


class GeoPointWGS84(Schema):
    Latitude = fields.Float(description='Latitude in degress', required=True)
    Longitude = fields.Float(description='Longitude in degress', required=True)
    Altitude = fields.Float(description='Geodetic altitude in meters', required=True)


class SignalStatsReportRequest(Schema):
    ReferenceTime = fields.Float(
        description='UNIX Timestamp',
        required=True
    )

    UasID = fields.String(required=True)

    Radio = fields.String(
        validate=validate.OneOf([
            '4glte',
            '5gnr'
        ]),
        description='Current radio access mode',
        required=True
    )

    Waypoint = fields.Nested(GeoPointWGS84, description='Reference Position', required=True)
    Roll = fields.Integer(description='Aircraft Roll (degrees)')
    Pitch = fields.Integer(description='Aircraft Pitch (degrees)')
    Yaw = fields.Integer(description='Aircraft Yaw (degrees)')

    VNorth = fields.Float(description='Aircraft North Velocity (meters per second)')
    VEast = fields.Float(description='Aircraft Eest Velocity (meters per second)')
    VDown = fields.Float(description='Aircraft Downward Velocity (meters per second)')
    VAir = fields.Float(description='Aircraft Air Speed (meters per second)')
    Baro = fields.Float(description='Aircraft Barometric Altitude')
    Heading = fields.Float(description='Aircraft True Heading (degrees)')

    RSRP = fields.Integer(description='Reference Signal Received Power', required=True)
    RSRP = fields.Integer(description='Reference Signal Received Power', required=True)
    RSRQ = fields.Integer(description='Reference Signal Received Quality', required=True)
    RSSI = fields.Integer(description='Received Signal Strength Indicator', required=True)
    SINR = fields.Integer(description='Signal to Interference & Noise Ratio', required=True)

    HeartbeatLoss = fields.Boolean(description='Heartbeat Loss Flag', required=True)
    RTT = fields.Integer(description='Round-Trip Time (ms)')
    Cell = fields.String(description='Aircraft Serving physical cell identifier', required=True)
    FrequencyBand = fields.String(description='Aircraft Serving Frequency Band Identification')
