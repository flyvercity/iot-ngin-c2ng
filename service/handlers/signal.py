# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements certificate requests.'''
import logging as lg

from schemas import (
    SignalStatsReportRequest
)

from handlers.auth import AuthHandler


class SignalStatsHandler(AuthHandler):
    '''Signal Statistics Reporting Handler'''

    def post(self):
        '''Receives a measurement sample.
        ---
        summary: Receives a sample of signal measurements from a UA with reference time and position.

        requestBody:
            description: A measurement sample object.
            required: True
            content:
                application/json:
                    schema:
                        SignalStatsReportRequest

        responses:
            200:
                description: Sample is successfully received.
                content:
                    application/json:
                        schema:
                            BaseSuccessSchema
            400:
                description: Payload containing error description.
                content:
                    application/json:
                        schema:
                            ValidationErrorSchema
        '''

        if not (request := self.get_request(SignalStatsReportRequest)):
            return

        lg.warn(f'Request {request}')

        self.respond()
