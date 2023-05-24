# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines a base class for all API handlers.'''
import logging as lg
import json

import tornado.web as web
from marshmallow.exceptions import ValidationError

from uss import UssInterface  # noqa
from mongo import Mongo  # noqa
from nsacf import NSACF  # noqa
from secman import SecMan  # noqa

from schemas import (
    BaseSuccessSchema,
    ValidationErrorSchema
)


class HandlerBase(web.RequestHandler):
    '''Helper methods for request and errors handling.'''

    def prepare(self):
        '''Creates shortcuts to subservices.'''
        self.uss = self.settings['uss']  # type: UssInterface
        self.mongo = self.settings['mongo']  # type: Mongo
        self.nsacf = self.settings['nsacf']  # type: NSACF
        self.secman = self.settings['secman']  # type: SecMan

    def _return(self, ResponseSchema: type, response: dict):
        '''Validate and return a response.

        Args:
            ResponseSchema: a schema of the response, subclass of `Schema`.
            response: a dict with formattable data.

        Raises:
            RuntimeError: on a attempt to return a malformed response.
        '''

        self.set_header('Content-Type', 'application/json')
        schema = ResponseSchema()

        try:
            ve = schema.validate(response)

            if ve:
                raise ValidationError(ve)

            self.finish(json.dumps(response) + '\n')

        except ValidationError as ve:
            lg.error(f'Invalid response {response}: {ve}')
            raise RuntimeError('Invalid response')

    def respond(self, ResponseSchema: type = BaseSuccessSchema, data: dict = {}):
        '''Successful response with optional data

        Args:
            ResponseSchema: a schema of the successful response, subclass of `BaseSuccessSchema`.
            data: JSON-formattable response.
        '''

        self.set_status(200)
        data['Success'] = True
        self._return(ResponseSchema, data)

    def fail(self, ResponseSchema: type, errors: dict, message: str = None):
        '''Produces a graceful failure response.

        Args:
            ResponseSchema: a schema of the erroneous response, subclass of `ErrorSchema`.
            errors: a dict with structured error.
            message: an optional human readable message.
        '''

        self.set_status(400)
        response = {'Success': False, 'Errors': errors}

        if message:
            response.update({'Message': message})

        self._return(ResponseSchema, response)

    def write_error(self, status_code, **kwargs):
        '''Produces an exception response.

        Args:
            status_code: HTTP status code.
            kwargs: unused here.
        '''
        self.set_header('Content-Type', 'application/json')

        if status_code == 403:
            self.finish(json.dumps({
                'Success': False,
                'Code': status_code,
                'Errors': 'Access denied'
            }))
        else:
            self.finish(json.dumps({
                'Success': False,
                'Code': status_code,
                'Errors': 'Internal Server Error'
            }))

    def get_request(self, RequestSchema):
        '''Unmarshal and validate a JSON request.

        Args:
            RequestSchema: a type of the request to validate against.

        Returns:
            A validated request JSON object.
        '''

        try:
            payload = json.loads(self.request.body)
            schema = RequestSchema()

            if ve := schema.validate(payload):
                raise ValidationError(ve)

            request = schema.load(payload)
            return request

        except ValidationError as ve:
            self.fail(ValidationErrorSchema, ve.messages_dict)
            return None
