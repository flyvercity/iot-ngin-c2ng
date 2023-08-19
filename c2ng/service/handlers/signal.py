# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements certificate requests.'''
import logging as lg

from c2ng.service.schemas import (
    SignalStatsReportRequest,
    SignalRequestResponse,
    SignalRequestResponseFailed
)

from c2ng.service.handlers.auth import AuthHandler


class SignalStatsHandler(AuthHandler):
    '''Signal Statistics Reporting Handler'''

    def post(self, uasid):
        '''Receives a measurement sample.

        Args:
            uasid: Logical UAS identifier

        ---
        summary: Receives a sample of signal measurements from a UA with reference time and position.

        requestBody:
            description: A measurement sample object.
            required: True
            content:
                application/json:
                    schema:
                        SignalStatsReportRequest

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID that sent the sample.

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

        self.influx.write_signal(uasid, request['Packet'])
        lg.info(f'Signal data written for {uasid}')
        self.respond()

    def get(self, uasid):
        '''Returns signal statistics for a given UAS.

        Args:
            uasid: Logical UAS identifier

        ---
        summary: Request a current address from existing connectivity session.

        parameters:
            -   in: path
                name: UasID
                schema:
                    type: string
                required: true
                description: UAS ID for which to fetch the peer's address.

        responses:
            200:
                description: Success payload containing peer's address
                content:
                    application/json:
                        schema:
                            SignalRequestResponse
            400:
                description: Payload containing error description
                content:
                    application/json:
                        schema:
                            SignalRequestResponseFailed
        '''

        try:
            response = self.statsman.get_signal_stats(uasid)

            self.respond(SignalRequestResponse, {
                'Stats': response
            })

        except Exception as exc:
            lg.error(f'Failed to read signal stats: {exc}')

            self.fail(
                SignalRequestResponseFailed,
                errors={'Database': 'unable_to_read'},
            )
