# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines Input/Output Data Object Schemas.'''
from marshmallow import Schema, fields, validate

from c2ng.service.fvc_packet import FVCPacket


def uasid():
    '''Generate standard UAS ID field.

    Returns:
        A field specification for UAS Logical ID.
    '''
    return fields.String(required=True, description='CAA UAS ID')


def validate_imsi(value: str):
    '''Validate standard 3GPP IMSI number.

    Args:
        value: input value to validate.

    Returns:
        A corresponding validator function.
    '''
    return validate.Regexp('[0-9]{14,15}')


class BaseSuccessSchema(Schema):
    Success = fields.Boolean(validate=validate.Equal(True), description='Success flag')


class ErrorSchema(Schema):
    Success = fields.Boolean(validate=validate.Equal(False), description='Failure flag.')
    Message = fields.String(description='Auxillary error message')


class ValidationErrorSchema(ErrorSchema):
    Errors = fields.Dict(
        keys=fields.String,
        values=fields.Dict(keys=fields.String, values=fields.Raw),
        description='Error identifier dict'
    )


class AerialConnectionSessionRequest(Schema):
    # TODO: Check reference time
    ReferenceTime = fields.Float(
        description='UNIX Timestamp',
        required=True
    )

    UasID = uasid()

    Segment = fields.String(
        required=True,
        validate=validate.OneOf([
            'ua',
            'adx'
        ]),
        description="Segment for which to request a session: airborne ('ua') or ground ('adx')."
    )

    IMSI = fields.String(validate=validate_imsi, required=False, description='UE IMSI ID')

    # TODO: Transmit metadata to USS
    Metadata = fields.Dict(required=False, description='Opaque object to pass to USSP')


class AerialConnectionSessionResponseErrors(Schema):
    Request = fields.String(required=False, validate=validate.OneOf([
        'imsi_required'
    ]))

    USS = fields.String(required=False, validate=validate.OneOf([
        'provider_unavailable',
        'flight_not_approved'
    ]))


class AerialConnectionSessionResponseFailed(ErrorSchema):
    Errors = fields.Nested(AerialConnectionSessionResponseErrors, required=True)


class AerialConnectionSessionResponse(BaseSuccessSchema):
    IP = fields.IP(required=True, description='Own IP address for aerial connection.')
    GatewayIP = fields.IP(required=True, description='Gateway IP for aerial connection.')
    KID = fields.String(required=True, description='Key unique identifier')

    EncryptedPrivateKey = fields.String(
        required=True, description='Session private key encrypted with client secret'
    )


class CertificateRequestResponseErrors(Schema):
    UasID = fields.String(validate=validate.OneOf([
        'not_found'
    ]))

    Segment = fields.String(validate=validate.OneOf([
        'invalid'
    ]))

    Session = fields.String(validate=validate.OneOf([
        'session_not_found',
        'peer_not_connected'
    ]))


class CertificateRequestResponseFailed(ErrorSchema):
    Errors = fields.Nested(CertificateRequestResponseErrors, required=True)


class CertificateRequestResponse(BaseSuccessSchema):
    KID = fields.String(required=True, description='Key unique identifier')

    Certificate = fields.String(
        required=True, description='Certificate with a public key as a PEM string'
    )


class AddressRequestResponseErrors(Schema):
    UasID = fields.String(validate=validate.OneOf([
        'not_found'
    ]))

    Segment = fields.String(validate=validate.OneOf([
        'invalid'
    ]))

    Session = fields.String(validate=validate.OneOf([
        'session_not_found',
        'peer_not_connected'
    ]))


class AddressRequestResponseFailed(ErrorSchema):
    Errors = fields.Nested(AddressRequestResponseErrors, required=True)


class AddressRequestResponse(BaseSuccessSchema):
    Address = fields.IP(
        required=True, description='IP Address for the peer'
    )


class SignalStatsReportRequest(Schema):
    Packet = fields.Nested(FVCPacket, required=True)


class WsAuthResponseSuccess(BaseSuccessSchema):
    Ticket = fields.String(required=True, description='Websocket ticket')


class WsAuthResponseErrors(Schema):
    UasID = fields.String(validate=validate.OneOf([
        'not_found'
    ]))

    Segment = fields.String(validate=validate.OneOf([
        'not_found',
        'bad_segment'
    ]))


class WsAuthResponseFailed(ErrorSchema):
    Errors = fields.Nested(WsAuthResponseErrors, required=True)


class AsyncIncomingSchema(Schema):
    Ticket = fields.String(required=True, description='Websocket ticket')
    Action = fields.String(required=True, description='Action to perform')


class AsyncSubscribeSchema(AsyncIncomingSchema):
    pass


class AsyncUnsubscribeSchema(AsyncIncomingSchema):
    pass


class SignalRequestResponseFailed(ErrorSchema):
    Errors = fields.Nested(
        {
            'UasID': fields.String(validate=validate.OneOf([
                'not_found'
            ])),
            'Database': fields.String(validate=validate.OneOf([
                'unable_to_read'
            ]))
        },
        required=True
    )


class SignalRequestResponse(BaseSuccessSchema):
    Stats = fields.List(
        fields.Integer,
        required=True,
        description='Signal averaged statistics'
    )
