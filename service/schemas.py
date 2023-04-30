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
        description='Session private key in encrypt own traffic',
        required=True
    )

    public_key = fields.String(
        data_key='SessionPublicKey',
        description='Session key to decrypt RPS traffic',
        required=True
    )


class AerialConnectionSessionResponseErrors(Schema):
    uss = fields.String(data_key='USS', required=True)


class AerialConnectionSessionResponseFailed(ErrorSchema):
    errors = fields.Nested(AerialConnectionSessionResponseErrors, data_key='Errors')
