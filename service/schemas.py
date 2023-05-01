#   SPDX-License-Identifier: MIT
#   Copyright 2023 Flyvercity

''' Input/Output Data Object Schemas '''

from marshmallow import Schema, fields, validate


class BaseSuccessSchema(Schema):
    Success = fields.Boolean(validate=validate.Equal(True))


class ErrorSchema(Schema):
    Success = fields.Boolean(validate=validate.Equal(False))
    Message = fields.String()


class ValidationErrorSchema(ErrorSchema):
    Errors = fields.Dict(
        keys=fields.String,
        values=fields.List(fields.String)
    )


def uasid():
    return fields.String(
        required=True,
        description='CAA UAS ID'
    )


class AerialConnectionSessionRequest(Schema):
    ref_time = fields.Integer(
        data_key='ReferenceTime',
        description='UNIX Timestamp',
        required=True
    )

    UasID = uasid()
    # TODO: Transmit metadata to USS
    metadata = fields.Dict(data_key='UssMetadata', required=False)


class AerialConnectionSessionResponse(Schema):
    own_ip = fields.IP(
        data_key='IP',
        description='Own IP (v4 or v6) for the reliable connection',
        required=True
    )

    gateway_id = fields.IP(
        data_key='GatewayIP',
        description='IP (v4 or v6) for the reliable connection gateway',
        required=True
    )

    private_key = fields.String(
        data_key='SessionPrivateKey', 
        description='Session private key in encrypt own traffic (hex)',
        required=True
    )

    public_key = fields.String(
        data_key='SessionPublicKey',
        description='Session key to decrypt RPS traffic (hex)',
        required=True
    )


class AerialConnectionSessionResponseErrors(Schema):
    USS = fields.String(required=True, validate=validate.OneOf([
        'provider_unavailable',
        'flight_not_approved'
    ]))


class AerialConnectionSessionResponseFailed(ErrorSchema):
    Errors = fields.Nested(AerialConnectionSessionResponseErrors, required=True)
