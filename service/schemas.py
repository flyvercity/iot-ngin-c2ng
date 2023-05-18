#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

'''Input/Output Data Object Schemas'''

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
    ReferenceTime = fields.Integer(
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
    ReferenceTime = fields.Integer(
        description='UNIX Timestamp',
        required=True
    )

    UasID = fields.String()


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
